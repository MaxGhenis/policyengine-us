#!/usr/bin/env python3
"""Record partner assertions without modifying fixtures or accepting new values.

`run` accepts exactly one YAML file. Coordinated runs over multiple files must
hold the machine-wide heavy lock; wrapping them in one Python file is no
exception. `list-files` and `merge` never construct a country model.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import importlib
from importlib.metadata import version
import json
import math
import os
from pathlib import Path
import sys
import traceback
from types import MethodType


REPO = Path(__file__).resolve().parents[1]
PARTNERS = REPO / "policyengine_us/tests/policy/baseline/partners"
DEFAULT_OUTPUT = REPO / ".resume-evidence/partner-inventory"


def evidence_path(path):
    path = path.resolve()
    if not path.is_relative_to(REPO / ".resume-evidence"):
        raise ValueError(
            "Inventory output must remain under this workspace's .resume-evidence/"
        )
    return path


def load_yaml(path):
    # This is the loader selected by the core YAML test runner itself.
    from policyengine_core.tools.test_runner import Loader, yaml

    with path.open() as stream:
        value = yaml.load(stream, Loader=Loader)
    return value if isinstance(value, list) else [value]


def in_year(value, year):
    if value is None:
        return False
    from policyengine_core.periods import period

    try:
        return period(value).start.year == year
    except (TypeError, ValueError, AttributeError):
        return False


def has_requested_output(test, year):
    if in_year(test.get("period"), year):
        return True

    def contains_period(value):
        return isinstance(value, dict) and any(
            in_year(key, year) or contains_period(child) for key, child in value.items()
        )

    return contains_period(test.get("output", {}))


def matching_files(year):
    result = []
    for path in sorted(PARTNERS.rglob("*")):
        if path.suffix not in {".yaml", ".yml"} or not path.is_file():
            continue
        tests = load_yaml(path)
        if any(
            isinstance(test, dict) and has_requested_output(test, year)
            for test in tests
        ):
            result.append(path)
    return result


def json_value(value, scalar=False):
    import numpy as np
    from policyengine_core.enums import EnumArray

    if isinstance(value, EnumArray):
        value = value.decode_to_str()
    if isinstance(value, np.ndarray):
        if scalar and value.size == 1:
            value = value.reshape(-1)[0]
        else:
            return json_value(value.tolist())
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, dict):
        return {str(key): json_value(child) for key, child in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_value(child) for child in value]
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def readable(value):
    # Financial displays use cents; JSON retains the full calculated value.
    if isinstance(value, float):
        return round(value, 2)
    if isinstance(value, list):
        return [readable(child) for child in value]
    return value


def dispatch_labels(item):
    """Supply labels in core callback order, checking each callback identity.

    The original core callback still dispatches and calculates all assertions.
    This iterator tracks paths only, including mixed root/entity outputs.
    """
    default_period = item.test.get("period")

    def leaves(variable_name, expected, requested_period, entity_index, label):
        if isinstance(expected, dict):
            for requested, value in expected.items():
                yield from leaves(variable_name, value, requested, entity_index, label)
        else:
            yield variable_name, str(requested_period), entity_index, label

    for key, expected in item.test["output"].items():
        if item.tax_benefit_system.get_variable(key):
            yield from leaves(key, expected, default_period, None, key)
        elif item.simulation.populations.get(key):
            for variable_name, value in expected.items():
                yield from leaves(
                    variable_name, value, default_period, None, f"{key}.{variable_name}"
                )
        else:
            population = item.simulation.get_population(plural=key)
            if population is None:
                return  # Core's original dispatcher raises the fixture error.
            for instance_id, values in expected.items():
                for variable_name, value in values.items():
                    index = population.get_index(instance_id)
                    yield from leaves(
                        variable_name,
                        value,
                        default_period,
                        index,
                        f"{key}.{instance_id}.{variable_name}",
                    )


def tolerance(test):
    absolute = test.get("absolute_error_margin")
    relative = test.get("relative_error_margin")
    return {
        "absolute": 0.001 if absolute is None and relative is None else absolute,
        "relative": relative,
        "semantics": "both supplied limits must pass; core assert_near determines result",
    }


@contextmanager
def recording_assertions(item, file, case_index, year, rows, errors):
    """Keep core construction/dispatch/comparison, recording every assertion.

    Core check_variable calls module-level assert_near. Intercept that function
    while retaining the original comparator, then suppress its AssertionError
    to continue collecting later outputs. Calculation errors are recorded by
    the check_variable wrapper and likewise allow subsequent outputs to run.
    """
    from policyengine_core.tools import test_runner

    original_assert = test_runner.assert_near
    original_check = item.check_variable
    context = {}
    labels = dispatch_labels(item)

    def base_row(variable_name, expected, period, entity_index, label):
        return {
            "file": str(file.relative_to(REPO)),
            "case": item.test.get("name", ""),
            "case_index": case_index,
            "output": label,
            "variable": variable_name,
            "period": str(period),
            "entity_index": entity_index,
            "old": json_value(expected),
            "tolerance": tolerance(item.test),
        }

    def record_assert(value, target_value, *args, **kwargs):
        row = dict(context)
        row["new"] = json_value(
            value, scalar=not isinstance(target_value, (list, tuple))
        )
        if isinstance(target_value, str):
            import numpy as np

            from policyengine_core.enums import EnumArray
            from policyengine_core.tools import eval_expression

            if not isinstance(value, EnumArray) and not np.issubdtype(
                np.asarray(value).dtype, np.datetime64
            ):
                try:
                    evaluated = eval_expression(target_value)
                except Exception:
                    pass  # Leave invalid/string values to the core comparator.
                else:
                    row["old_fixture"] = row["old"]
                    row["old"] = json_value(evaluated)
        try:
            original_assert(value, target_value, *args, **kwargs)
        except AssertionError as error:
            row["within_tolerance"] = False
            row["assertion_message"] = str(error)
        except Exception:
            row["within_tolerance"] = None
            row["error"] = traceback.format_exc()
            errors.append(dict(row))
        else:
            row["within_tolerance"] = True
        row["display_changed"] = readable(row["old"]) != readable(row["new"])
        rows.append(row)

    def record_variable(self, variable_name, expected_value, period, entity_index=None):
        if isinstance(expected_value, dict):
            # The original recursion calls self.check_variable for each period.
            return original_check(variable_name, expected_value, period, entity_index)
        label_variable, label_period, label_index, label = next(labels)
        if (label_variable, label_period, label_index) != (
            variable_name,
            str(period),
            entity_index,
        ):
            raise RuntimeError("Core output dispatch differs from the inventory labels")
        if not in_year(period, year) or self.should_ignore_variable(variable_name):
            return
        context.clear()
        context.update(
            base_row(variable_name, expected_value, period, entity_index, label)
        )
        try:
            return original_check(variable_name, expected_value, period, entity_index)
        except Exception:
            row = dict(context)
            row.update(new=None, within_tolerance=None, error=traceback.format_exc())
            errors.append(row)
            rows.append(row)

    item.check_variable = MethodType(record_variable, item)
    test_runner.assert_near = record_assert
    try:
        yield
    finally:
        test_runner.assert_near = original_assert
        item.check_variable = original_check


def markdown(payload):
    rows = payload["assertions"]
    failed = [row for row in rows if row.get("within_tolerance") is False]
    moved = [
        row
        for row in rows
        if row.get("within_tolerance") is True and row.get("display_changed")
    ]
    lines = [
        "# IRS/state indexing partner output inventory",
        "",
        "Partner fixtures were read without edits. Calculated values are proposed output changes, not approved contract changes.",
        "",
        f"Model: {payload.get('model_label', 'see per-file metadata')}. Year: {payload['year']}.",
        f"Assertions: {len(rows)}; outside tolerance: {len(failed)}; changed within tolerance: {len(moved)}; errors: {len(payload['errors'])}.",
        "",
        "Each case index is one-based within its YAML file. Tables round financial values to cents; JSON retains full precision and every assertion, including unchanged outputs.",
    ]
    if payload.get("missing_files"):
        lines += ["", "INCOMPLETE: files still requiring a model run:", ""]
        lines.extend(f"- `{file}`" for file in payload["missing_files"])
    for title, section in [
        ("Expected outputs outside fixture tolerance", failed),
        ("Changed outputs within fixture tolerance", moved),
    ]:
        lines += [
            "",
            f"## {title}",
            "",
            "| File | Case | Output | Old | New | Tolerance | Within tolerance |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
        for row in section:
            fields = [
                row["file"],
                f"{row['case_index']}: {row['case']}",
                f"{row['output']}@{row['period']}",
                json.dumps(readable(row["old"])),
                json.dumps(readable(row["new"])),
                json.dumps(
                    {
                        key: value
                        for key, value in row["tolerance"].items()
                        if key != "semantics"
                    }
                ),
                str(row["within_tolerance"]).lower(),
            ]
            lines.append(
                "| "
                + " | ".join(
                    field.replace("|", "\\|").replace("\n", " ") for field in fields
                )
                + " |"
            )
    if payload["errors"]:
        lines += ["", "## Calculation or fixture errors", ""]
        for error in payload["errors"]:
            lines += [
                f"- `{error.get('file')}` — {error.get('case', 'collection/build')} — `{error.get('output', '')}`",
                "",
                "```text",
                error["error"],
                "```",
                "",
            ]
    return "\n".join(lines) + "\n"


def write_payload(stem, payload):
    stem.parent.mkdir(parents=True, exist_ok=True)
    for suffix, text in [
        (".json", json.dumps(payload, indent=2, allow_nan=False) + "\n"),
        (".md", markdown(payload)),
    ]:
        path = stem.with_suffix(suffix)
        temporary = path.with_name(path.name + ".tmp")
        temporary.write_text(text)
        temporary.replace(path)


def run_file(args):
    file = (REPO / args.file).resolve()
    if (
        not file.is_file()
        or file.suffix not in {".yaml", ".yml"}
        or not file.is_relative_to(PARTNERS)
    ):
        raise ValueError(
            "--file must identify exactly one existing YAML file under partners/"
        )
    output_dir = evidence_path(args.output_dir)
    stem = output_dir / str(file.relative_to(PARTNERS)).replace("/", "__").replace(
        file.suffix, ""
    )
    if stem.with_suffix(".json").exists() and not args.overwrite:
        raise ValueError(
            f"Existing evidence: {stem.with_suffix('.json')}; use --overwrite only to intentionally replace it"
        )
    payload = {
        "format_version": 1,
        "file": str(file.relative_to(REPO)),
        "year": args.year,
        "model_label": args.model_label,
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "fixture_sha256": hashlib.sha256(file.read_bytes()).hexdigest(),
        "completed": False,
        "cases_executed": 0,
        "assertions": [],
        "errors": [],
    }
    write_payload(stem, payload)
    sys.path.insert(0, str(REPO))
    try:
        os.environ.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
        import pytest
        from policyengine_core.scripts import build_tax_benefit_system
        from policyengine_core.tools.test_runner import YamlFile, YamlItem

        payload["core_version"] = version("policyengine-core")
        package = importlib.import_module("policyengine_us")
        package_file = Path(package.__file__).resolve()
        if not package_file.is_relative_to(REPO):
            raise RuntimeError(f"Wrong model checkout imported: {package_file}")
        payload["model_package"] = str(package_file)
        baseline = build_tax_benefit_system("policyengine_us", [], [])
        config = pytest.Config.fromdictargs(
            {}, ["--noconftest", "-p", "no:cacheprovider"]
        )
        session = pytest.Session.from_config(config)
        collector = YamlFile.from_parent(
            session, path=file, tax_benefit_system=baseline, options={}
        )
        try:
            for case_index, item in enumerate(collector.collect(), 1):
                if not isinstance(item, YamlItem):
                    raise TypeError(
                        "Core YAML collector returned an unexpected item type"
                    )
                if not has_requested_output(item.test, args.year):
                    continue
                try:
                    with recording_assertions(
                        item,
                        file,
                        case_index,
                        args.year,
                        payload["assertions"],
                        payload["errors"],
                    ):
                        item.runtest()
                except Exception:
                    payload["errors"].append(
                        {
                            "file": payload["file"],
                            "case": item.test.get("name", ""),
                            "case_index": case_index,
                            "error": traceback.format_exc(),
                        }
                    )
                finally:
                    item.simulation = None
                    payload["cases_executed"] += 1
                    write_payload(stem, payload)
                print(f"{payload['file']}: case {case_index} recorded", flush=True)
        finally:
            config._ensure_unconfigure()
        payload["completed"] = True
    except Exception:
        payload["errors"].append(
            {"file": payload["file"], "error": traceback.format_exc()}
        )
    finally:
        payload["finished_utc"] = datetime.now(timezone.utc).isoformat()
        write_payload(stem, payload)
    print(
        f"Evidence: {stem.with_suffix('.json')} and {stem.with_suffix('.md')}",
        flush=True,
    )
    return 2 if payload["errors"] or not payload["completed"] else 0


def merge_files(args):
    expected = {str(path.relative_to(REPO)) for path in matching_files(args.year)}
    payload = {
        "format_version": 1,
        "year": args.year,
        "model_label": args.model_label,
        "assertions": [],
        "errors": [],
        "files": [],
        "missing_files": [],
    }
    seen = set()
    for path in sorted(evidence_path(args.input_dir).glob("*.json")):
        result = json.loads(path.read_text())
        if result.get("year") != args.year or "file" not in result:
            continue
        fixture = (REPO / result["file"]).resolve()
        if not fixture.is_relative_to(PARTNERS) or result["file"] not in expected:
            continue
        if result["file"] in seen:
            raise ValueError(
                f"Multiple inventory results for the same fixture: {fixture}"
            )
        seen.add(result["file"])
        if result.get("model_label") != args.model_label:
            raise ValueError(
                f"Different model label in {path}; keep one output directory per build"
            )
        if hashlib.sha256(fixture.read_bytes()).hexdigest() != result.get(
            "fixture_sha256"
        ):
            raise ValueError(f"Fixture changed after inventory run: {fixture}")
        payload["files"].append(
            {
                key: result.get(key)
                for key in [
                    "file",
                    "model_label",
                    "core_version",
                    "fixture_sha256",
                    "completed",
                    "cases_executed",
                    "started_utc",
                    "finished_utc",
                ]
            }
        )
        payload["assertions"].extend(result["assertions"])
        payload["errors"].extend(result["errors"])
    completed = {file["file"] for file in payload["files"] if file["completed"]}
    payload["missing_files"] = sorted(expected - completed)
    payload["completed"] = not payload["missing_files"] and not payload["errors"]
    write_payload(evidence_path(args.output_stem), payload)
    return 0 if payload["completed"] else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    listing = subparsers.add_parser(
        "list-files",
        help="List partner files with requested-year outputs; no model run",
    )
    listing.add_argument("--year", type=int, default=2026)
    running = subparsers.add_parser(
        "run",
        help="Record exactly one partner YAML using the core loader and simulation builder",
    )
    running.add_argument("--file", required=True)
    running.add_argument("--year", type=int, default=2026)
    running.add_argument("--model-label", required=True)
    running.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    running.add_argument("--overwrite", action="store_true")
    merging = subparsers.add_parser(
        "merge", help="Combine per-file evidence and flag missing files; no model run"
    )
    merging.add_argument("--year", type=int, default=2026)
    merging.add_argument("--model-label", required=True)
    merging.add_argument("--input-dir", type=Path, default=DEFAULT_OUTPUT)
    merging.add_argument(
        "--output-stem",
        type=Path,
        default=REPO / ".resume-evidence/9621-partner-inventory",
    )
    args = parser.parse_args()
    if args.command == "list-files":
        for path in matching_files(args.year):
            print(path.relative_to(REPO))
        return 0
    if args.command == "run":
        return run_file(args)
    return merge_files(args)


if __name__ == "__main__":
    raise SystemExit(main())
