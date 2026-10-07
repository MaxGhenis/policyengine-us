#!/usr/bin/env python3
"""Summarize downloaded #9676 CI artifacts using only the standard library.

Usage:
  python3 .resume/summarize_ci.py .resume/ci-output \
      --json .resume/ci-summary.json --markdown .resume/ci-summary.md

Input may contain the artifact-name directory created by gh run download.
No pickle files are opened and no model/dependency modules are imported.
Missing evidence stays explicit. --strict rejects incomplete/unexpected results.
"""

import argparse
import json
import math
import re
from pathlib import Path


ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
COUNTS = re.compile(
    r"(\d+)\s+(passed|failed|errors?|skipped|xfailed|xpassed|deselected|warnings?)\b"
)
SUMMARY = re.compile(
    r"^\s*=*\s*((?:\d+\s+(?:passed|failed|errors?|skipped|xfailed|xpassed|"
    r"deselected|warnings?)[,\s]*)+)\s+in\s+([\d.]+)s\b"
)
EXPECTED_TASKS = ("suites", "mutations", "main", "old_head")
EXPECTED_SCENARIOS = ("unmodified", "marked", "marked_no_assets")
TARGETS = {
    "npcr_never": "test_non_parent_caretaker_identification_matches_independent_rule",
    "drop_has_dependent_child_py": "test_parent_flag_needs_a_dependent_child_in_the_persons_tax_unit",
    "drop_has_dependent_child_yaml": "Explicit parent flag requires a dependent child",
}


def read_text(path):
    return ANSI.sub("", path.read_text(errors="replace"))


def parse_counts(text):
    """Keep each pytest session separate, including repeated mutation runs."""
    sessions = []
    mutation = None
    for line in text.splitlines():
        marker = re.match(r"=== MUTATION (\S+) START", line)
        if marker:
            mutation = marker.group(1)
        match = SUMMARY.match(line)
        if not match:
            continue
        counts = {}
        for amount, status in COUNTS.findall(match.group(1)):
            status = {"error": "errors", "warning": "warnings"}.get(status, status)
            counts[status] = int(amount)
        sessions.append(
            {
                "mutation": mutation,
                "counts": counts,
                "reported_seconds": float(match.group(2)),
                "summary_line": line.strip(),
            }
        )
    totals = {}
    for session in sessions:
        for name, amount in session["counts"].items():
            totals[name] = totals.get(name, 0) + amount
    files = re.findall(r"^Total test files:\s*(\d+)\s*$", text, re.M)
    batch_outcomes = re.findall(
        r"^\s*Batch \d+:.*\|\s*(passed|failed|timeout|interrupted)\s*$", text, re.M
    )
    return {
        "sessions": sessions,
        "totals_across_reported_sessions": totals or None,
        "test_files": int(files[-1]) if files else None,
        "batch_outcomes": batch_outcomes,
        "has_traceback": "Traceback (most recent call last)" in text,
    }


def clock_seconds(value):
    parts = value.split(":")
    return sum(float(part) * 60**i for i, part in enumerate(reversed(parts)))


def parse_time(text):
    result = {}
    for line in text.splitlines():
        elapsed = re.match(r"\s*Elapsed.*\):\s*(\S+)\s*$", line)
        if elapsed:
            result["wall_seconds"] = clock_seconds(elapsed.group(1))
            continue
        for label, key, cast in (
            ("User time (seconds)", "user_seconds", float),
            ("System time (seconds)", "system_seconds", float),
            ("Maximum resident set size (kbytes)", "max_rss_kbytes", int),
            ("Exit status", "exit_status", int),
        ):
            prefix = label + ":"
            if line.strip().startswith(prefix):
                result[key] = cast(line.strip()[len(prefix) :].strip())
    if "user_seconds" in result and "system_seconds" in result:
        result["cpu_seconds"] = result["user_seconds"] + result["system_seconds"]
    return result


def mutation_summary(data, filename):
    actual = data.get("actual", {})
    expected = data.get("expected", {})
    result = {}
    for mutation in sorted(set(actual) | set(expected)):
        failures = data.get("failures", {}).get(mutation, [])
        assertions = bool(failures) and all(
            row.get("when") == "call" and row.get("assertion") is True
            for row in failures
        )
        target = None
        if expected.get(mutation) == 1:
            if mutation == "drop_has_dependent_child":
                suffix = "py" if "property" in filename else "yaml"
                target = TARGETS[mutation + "_" + suffix]
            elif mutation == "npcr_never":
                target = TARGETS[mutation]
        detected = (
            any(
                target.casefold() in row.get("test_name", "").casefold()
                or target.casefold() in row.get("nodeid", "").casefold()
                for row in failures
            )
            if target
            else None
        )
        valid = actual.get(mutation) == expected.get(mutation)
        if expected.get(mutation) == 1:
            valid = valid and assertions and (detected if target else True)
        result[mutation] = {
            "actual_exit": actual.get(mutation),
            "expected_exit": expected.get(mutation),
            "matches_contract": bool(valid),
            "failure_count": len(failures),
            "all_failures_are_test_call_assertions": assertions if failures else None,
            "intended_detecting_case": target,
            "intended_case_failed": detected,
            "failures": failures,
        }
    return result


def compact_impact(data):
    result = {}
    for scenario, raw in data.items():
        if "missing" in raw:
            result[scenario] = {"missing": raw["missing"]}
            continue
        months = raw.get("monthly", {})
        payments = {
            month: value.get("entitlement", {}).get("change")
            for month, value in months.items()
        }
        known = [
            value for value in payments.values() if isinstance(value, (int, float))
        ]
        annual = raw.get("annual_entitlement", {})
        result[scenario] = {
            "metadata": raw.get("metadata"),
            "annual_entitlement": annual,
            "annual_mo_entitlement_with_takeup": raw.get(
                "annual_mo_entitlement_with_takeup"
            ),
            "annual_actual_tanf": raw.get("annual_actual_tanf"),
            "annual_actual_tanf_all_states_change": raw.get(
                "annual_actual_tanf_all_states_change"
            ),
            "months_reported": len(months),
            "monthly_entitlement_changes": payments,
            "monthly_change_min": min(known) if known else None,
            "monthly_change_max": max(known) if known else None,
            "monthly_sum_matches_annual": (
                math.isclose(sum(known), annual["change"], rel_tol=1e-9, abs_tol=0.01)
                if len(known) == 12 and "change" in annual
                else None
            ),
            "monthly": months,
            "two_largest_records_share_of_absolute_annual_change": raw.get(
                "two_largest_records_share_of_absolute_annual_change"
            ),
            "drivers": raw.get("membership_changed_or_payment_changed_records", []),
        }
    return result


def summarize(root, years=(2026, 2025)):
    result = {
        "artifact_root": str(root.resolve()),
        "phases": {},
        "test_tasks": {},
        "microsim_runs": {},
        "impacts": {},
        "households": {},
        "household_comparisons": {},
        "warnings": [],
    }
    files = sorted(root.rglob("*")) if root.exists() else []
    for path in files:
        if not path.is_file():
            continue
        relative = str(path.relative_to(root))
        try:
            if path.name in (
                "tests_status.txt",
                "impact_status.txt",
                "compare_status.txt",
            ):
                result["phases"][path.stem] = int(read_text(path).strip())
            elif path.name == "summary.txt" and path.parent.name in EXPECTED_TASKS:
                task = result["test_tasks"].setdefault(path.parent.name, {})
                runs = []
                text = read_text(path)
                for line in text.splitlines():
                    match = re.fullmatch(r"(\S+) actual=(-?\d+) expected=(-?\d+)", line)
                    if not match:
                        continue
                    name, actual, expected = match.groups()
                    record = {
                        "name": name,
                        "actual_exit": int(actual),
                        "expected_exit": int(expected),
                        "matches_contract": actual == expected,
                    }
                    log = path.with_name(name + ".log")
                    timing = path.with_name(name + ".time")
                    record["log_counts"] = (
                        parse_counts(read_text(log)) if log.exists() else None
                    )
                    record["cost"] = (
                        parse_time(read_text(timing)) if timing.exists() else None
                    )
                    runs.append(record)
                flag = re.search(r"Unexpected result flag:\s*(\d+)", text)
                task.update(
                    summary_file=relative,
                    unexpected_result_flag=int(flag.group(1)) if flag else None,
                    runs=runs,
                )
            elif path.name == "summary.txt" and path.parent.name == "out":
                for line in read_text(path).splitlines():
                    match = re.fullmatch(r"(\S+) exit=(-?\d+)", line)
                    if match:
                        result["microsim_runs"].setdefault(match.group(1), {})[
                            "exit_status"
                        ] = int(match.group(2))
            elif path.suffix == ".json":
                data = json.loads(read_text(path))
                if path.name.startswith("compare_"):
                    result["impacts"][path.stem.removeprefix("compare_")] = (
                        compact_impact(data)
                    )
                elif path.name.startswith("household_") and "cases" in data:
                    result["households"][data.get("label", path.stem)] = data
                elif path.name.endswith("_meta.json"):
                    tag = path.stem.removesuffix("_meta")
                    result["microsim_runs"].setdefault(tag, {})["metadata"] = data
                elif path.parent.name in EXPECTED_TASKS:
                    task = result["test_tasks"].setdefault(path.parent.name, {})
                    if "actual" in data and "expected" in data:
                        task.setdefault("mutations", {})[path.stem] = mutation_summary(
                            data, path.name
                        )
                    elif "expected_assertion_failure" in data:
                        task.setdefault("preserved_assertion_failures", {})[
                            path.stem
                        ] = data
                    elif path.name == "runtime.json":
                        task["runtime"] = data
            elif path.name.endswith("_time.txt"):
                tag = path.stem.removesuffix("_time")
                result["microsim_runs"].setdefault(tag, {})["cost"] = parse_time(
                    read_text(path)
                )
        except (ValueError, TypeError, KeyError) as error:
            result["warnings"].append(f"Cannot parse {relative}: {error}")

    main = result["households"].get("main", {}).get("cases", {})
    for label, data in result["households"].items():
        if label == "main":
            continue
        paired = {}
        for name in sorted(set(main) & set(data.get("cases", {}))):
            before, after = main[name], data["cases"][name]
            paired[name] = {
                "main": before,
                label: after,
                "payment_change": after["mo_tanf"] - before["mo_tanf"],
            }
        result["household_comparisons"][f"{label}_minus_main"] = paired

    for phase in ("tests_status", "impact_status", "compare_status"):
        if phase not in result["phases"]:
            result["warnings"].append(f"Missing phase status: {phase}")
        elif result["phases"][phase] != 0:
            result["warnings"].append(
                f"Nonzero phase status: {phase}={result['phases'][phase]}"
            )
    for name in EXPECTED_TASKS:
        task = result["test_tasks"].get(name, {})
        if not task.get("runs") or task.get("unexpected_result_flag") is None:
            result["warnings"].append(f"Missing or incomplete task summary: {name}")
        if task.get("unexpected_result_flag"):
            result["warnings"].append(f"Unexpected test result in task: {name}")
        for run in task.get("runs", []):
            if not run["matches_contract"]:
                result["warnings"].append(f"Exit mismatch: {name}/{run['name']}")
        for filename, mutations in task.get("mutations", {}).items():
            for mutation, row in mutations.items():
                if not row["matches_contract"]:
                    result["warnings"].append(
                        f"Mutation mismatch: {filename}/{mutation}"
                    )
    for year in years:
        if str(year) not in result["impacts"]:
            result["warnings"].append(f"Missing requested paired comparison: {year}")
    for year, scenarios in result["impacts"].items():
        for scenario in EXPECTED_SCENARIOS:
            impact = scenarios.get(scenario, {})
            if not impact or "missing" in impact or impact.get("months_reported") != 12:
                result["warnings"].append(
                    f"Incomplete monthly impact: {year}/{scenario}"
                )
            if (impact.get("annual_actual_tanf") or {}).get("incomplete"):
                result["warnings"].append(
                    f"Incomplete actual annual tanf: {year}/{scenario}"
                )
            if impact.get("monthly_sum_matches_annual") is False:
                result["warnings"].append(
                    f"Monthly/annual aggregate mismatch: {year}/{scenario}"
                )
    if not result["impacts"]:
        result["warnings"].append("No paired compare_*.json reports found")
    return result


def number(value, decimals=6):
    return (
        "missing" if value is None else f"{value:,.{decimals}f}".rstrip("0").rstrip(".")
    )


def markdown(result):
    lines = [
        "# #9676 downloaded CI evidence",
        "",
        f"Artifact root: `{result['artifact_root']}`.",
        "",
    ]
    phase_text = ", ".join(
        f"{key}={value}" for key, value in sorted(result["phases"].items())
    )
    lines += ["Phase statuses: " + (phase_text or "missing") + ".", ""]
    lines += [
        "| Task/run | Actual / expected exit | Reported test counts | Wall / CPU seconds |",
        "|---|---:|---|---:|",
    ]
    for name, task in sorted(result["test_tasks"].items()):
        for run in task.get("runs", []):
            parsed = run.get("log_counts") or {}
            counts = parsed.get("totals_across_reported_sessions")
            count_text = (
                ", ".join(
                    f"{amount} {status}" for status, amount in sorted(counts.items())
                )
                if counts
                else "not reported"
            )
            if any(row["mutation"] for row in parsed.get("sessions", [])):
                count_text += " across separate mutation sessions"
            cost = run.get("cost") or {}
            lines.append(
                f"| {name}/{run['name']} | {run['actual_exit']} / {run['expected_exit']} | {count_text} | {number(cost.get('wall_seconds'), 2)} / {number(cost.get('cpu_seconds'), 2)} |"
            )
    lines.append("")
    for name, task in sorted(result["test_tasks"].items()):
        if "runtime" in task:
            lines += [
                f"Runtime ({name}): `{json.dumps(task['runtime'], sort_keys=True)}`.",
                "",
            ]
        for filename, mutations in sorted(task.get("mutations", {}).items()):
            for mutation, row in mutations.items():
                lines += [
                    f"Mutation `{filename}/{mutation}`: exit {row['actual_exit']} / expected {row['expected_exit']}; contract matched={row['matches_contract']}; intended detecting case={row['intended_detecting_case']}; case failed={row['intended_case_failed']}.",
                    "",
                ]
    for label, cases in sorted(result["household_comparisons"].items()):
        lines += [
            f"## Household checks: {label}",
            "",
            "| Case | Main grant | Compared grant | Change |",
            "|---|---:|---:|---:|",
        ]
        for name, row in cases.items():
            other = next(key for key in row if key not in ("main", "payment_change"))
            lines.append(
                f"| {name} | {number(row['main']['mo_tanf'])} | {number(row[other]['mo_tanf'])} | {number(row['payment_change'])} |"
            )
        lines.append("")
    if result["microsim_runs"]:
        lines += [
            "## Microsimulation measured cost",
            "",
            "| Run | Exit | Checkpoint | Wall / CPU seconds | Peak RSS kbytes |",
            "|---|---:|---|---:|---:|",
        ]
        for tag, row in sorted(result["microsim_runs"].items()):
            cost = row.get("cost") or {}
            checkpoint = row.get("metadata", {}).get("status", "missing")
            lines.append(
                f"| {tag} | {row.get('exit_status', 'missing')} | {checkpoint} | {number(cost.get('wall_seconds'), 2)} / {number(cost.get('cpu_seconds'), 2)} | {number(cost.get('max_rss_kbytes'), 2)} |"
            )
        lines.append("")
    for year, scenarios in sorted(result["impacts"].items(), reverse=True):
        lines += [
            f"## Paired impact: {year}",
            "",
            "| Scenario | Annual entitlement change | Annual actual MO TANF change | January entitlement change | Two-record share |",
            "|---|---:|---:|---:|---:|",
        ]
        for scenario, row in scenarios.items():
            if "missing" in row:
                lines.append(f"| {scenario} | missing | missing | missing | missing |")
                continue
            annual = row.get("annual_entitlement") or {}
            actual = row.get("annual_actual_tanf") or {}
            january = row.get("monthly", {}).get("01", {}).get("entitlement", {})
            share = row.get("two_largest_records_share_of_absolute_annual_change")
            lines.append(
                f"| {scenario} | {number(annual.get('change'))} | {number(actual.get('change'))} | {number(january.get('change'))} | {number(100 * share, 4) + '%' if share is not None else 'undefined'} |"
            )
        lines.append("")
        for scenario, row in scenarios.items():
            if "missing" in row:
                lines += [f"{scenario}: {row['missing']}", ""]
                continue
            lines += [
                f"{scenario}: {row['months_reported']} months reported; monthly entitlement change range {number(row['monthly_change_min'])} to {number(row['monthly_change_max'])}; monthly sum matches annual={row['monthly_sum_matches_annual']}.",
                "",
            ]
            january = row.get("monthly", {}).get("01", {})
            lines += [
                f"January membership/failure evidence: `{json.dumps({key: value for key, value in january.items() if key != 'entitlement'}, sort_keys=True)}`.",
                "",
            ]
            for driver in row.get("drivers", []):
                lines += [f"Driver: `{json.dumps(driver, sort_keys=True)}`.", ""]
    if result["warnings"]:
        lines += ["## Missing or unexpected evidence", ""]
        lines += [f"- {warning}" for warning in result["warnings"]]
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "artifact_dir", nargs="?", type=Path, default=Path(".resume/ci-output")
    )
    parser.add_argument("--json", type=Path)
    parser.add_argument("--markdown", type=Path)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--years", nargs="+", type=int, default=[2026, 2025])
    args = parser.parse_args()
    result = summarize(args.artifact_dir, args.years)
    report = markdown(result)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(result, indent=2) + "\n")
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(report)
    print(report)
    return 1 if args.strict and result["warnings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
