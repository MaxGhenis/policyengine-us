"""Run #9676 tests against in-process mutations (adapted from the 2026-09-29 review's mutate.py).

Nothing in the worktree is edited: the formulas are replaced on the
singleton tax-benefit system that policyengine_us.Simulation uses, and the
YAML tests are run through policyengine_core's run_tests with that same
system object.

Usage (from the worktree, with its venv):
  uv run python /path/mutate.py <mutation> [--yaml DIR_OR_FILE ...] [--py FILE ...]
"""

import argparse
import gc
import json
import sys
from pathlib import Path

import numpy as np
import pytest
from policyengine_core.tools import test_runner
from policyengine_us.model_api import *  # noqa: F401,F403 (where, etc.)
from policyengine_us.system import system


def member_formula(drop=frozenset()):
    def formula(person, period, parameters):
        is_ssi_recipient = (person("ssi", period) > 0) | person("receives_ssi", period)
        dependent_child = person("mo_tanf_dependent_child", period)
        eligible_child = dependent_child & ~is_ssi_recipient
        head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        is_dependent = person("is_tax_unit_dependent", period.this_year)
        has_dependent_child = person.tax_unit.any(dependent_child)
        caretaker = (
            head_or_spouse & ~is_dependent & ~is_ssi_recipient & has_dependent_child
        )
        non_parent = person("mo_tanf_is_non_parent_caretaker", period.this_year)
        parent_caretaker = caretaker & ~non_parent
        other_parent = person("mo_tanf_is_parent_of_dependent_child", period.this_year)
        if "non_parent" not in drop:
            other_parent = other_parent & ~non_parent
        if "dependent_child" not in drop:
            other_parent = other_parent & ~dependent_child
        if "ssi" not in drop:
            other_parent = other_parent & ~is_ssi_recipient
        if "has_dependent_child" not in drop:
            other_parent = other_parent & has_dependent_child
        npcr = person("mo_tanf_non_parent_caretaker", period)
        npcr_included = person.spm_unit("mo_tanf_non_parent_caretaker_included", period)
        return eligible_child | parent_caretaker | other_parent | (npcr & npcr_included)

    return formula


def npcr_never(person, period, parameters):
    # Mutation: never identify a non-parent caretaker (the caretaker rules
    # see a parent in the home in every household).
    return np.zeros(person.count, dtype=bool)


ORIGINAL = {}


def patch(name, fn):
    variable = system.variables[name]
    ORIGINAL.setdefault(name, dict(variable.formulas))
    for key in list(variable.formulas.keys()):
        variable.formulas[key] = fn


def restore():
    for name, formulas in ORIGINAL.items():
        system.variables[name].formulas.clear()
        system.variables[name].formulas.update(formulas)
    ORIGINAL.clear()


MUTATIONS = {
    "none": lambda: None,
    "drop_has_dependent_child": lambda: patch(
        "mo_tanf_is_assistance_unit_member",
        member_formula(frozenset({"has_dependent_child"})),
    ),
    "drop_dependent_child_guard": lambda: patch(
        "mo_tanf_is_assistance_unit_member",
        member_formula(frozenset({"dependent_child"})),
    ),
    "drop_ssi": lambda: patch(
        "mo_tanf_is_assistance_unit_member", member_formula(frozenset({"ssi"}))
    ),
    "npcr_never": lambda: patch("mo_tanf_non_parent_caretaker", npcr_never),
}


class FailureEvidence:
    """Distinguish rule assertion failures from unrelated pytest errors."""

    def __init__(self):
        self.failures = []

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        result = yield
        report = result.get_result()
        if report.failed:
            self.failures.append(
                {
                    "nodeid": report.nodeid,
                    "test_name": getattr(item, "test", {}).get("name", item.name),
                    "when": report.when,
                    "exception": call.excinfo.type.__name__ if call.excinfo else None,
                    "assertion": bool(
                        call.excinfo and call.excinfo.errisinstance(AssertionError)
                    ),
                }
            )

    def pytest_collectreport(self, report):
        if report.failed:
            self.failures.append(
                {"nodeid": report.nodeid, "when": "collection", "assertion": False}
            )


def main():
    # One process, one test file, several mutations in sequence (formulas are
    # restored between them), so the model is imported once.
    parser = argparse.ArgumentParser()
    parser.add_argument("mutations", nargs="+", choices=sorted(MUTATIONS))
    parser.add_argument("--yaml", default=None)
    parser.add_argument("--py", default=None)
    parser.add_argument(
        "--expect", required=True, help="JSON mutation-to-exit-code mapping"
    )
    parser.add_argument("--results", required=True)
    args = parser.parse_args()
    assert bool(args.yaml) != bool(args.py), "give exactly one test file"
    codes = {}
    failures = {}
    expected = json.loads(args.expect)
    assert set(expected) == set(args.mutations), (expected, args.mutations)
    for mutation in args.mutations:
        # Core caches cloned YAML systems. Retire the preceding clone before
        # patching, or later mutations execute the earlier unmutated clone.
        test_runner._tax_benefit_system_cache.pop(system, None)
        gc.collect()
        MUTATIONS[mutation]()
        evidence = FailureEvidence()
        print(f"=== MUTATION {mutation} START", flush=True)
        if args.py:
            code = int(
                pytest.main(
                    ["-q", "-rf", "-p", "no:cacheprovider", args.py], plugins=[evidence]
                )
            )
        else:
            code = int(
                pytest.main(
                    [
                        "--capture",
                        "no",
                        "--maxfail",
                        "0",
                        "--tb",
                        "short",
                        "-p",
                        "no:cacheprovider",
                        args.yaml,
                    ],
                    plugins=[test_runner.OpenFiscaPlugin(system, {}), evidence],
                )
            )
        codes[mutation] = code
        failures[mutation] = evidence.failures
        print(f"=== MUTATION {mutation} EXIT CODE {code}", flush=True)
        restore()
        test_runner._tax_benefit_system_cache.pop(system, None)
        gc.collect()
    print(f"ALL EXIT CODES {codes}", flush=True)
    Path(args.results).write_text(
        json.dumps(
            {"actual": codes, "expected": expected, "failures": failures}, indent=2
        )
    )
    # Pytest exit 1 also includes setup/runtime failures. Require actual
    # assertion failures in the test call, with the intended regression case.
    mismatches = {
        name: (expected[name], code)
        for name, code in codes.items()
        if code != expected[name]
    }
    for name, expected_code in expected.items():
        if expected_code != 1:
            continue
        records = failures[name]
        if not records or not all(
            record["when"] == "call" and record["assertion"] for record in records
        ):
            mismatches[name] = "expected test-call assertions; saw unrelated failure"
        target = None
        if name == "npcr_never" and args.py:
            target = "test_non_parent_caretaker_identification_matches_independent_rule"
        elif name == "drop_has_dependent_child" and args.py:
            target = "test_parent_flag_needs_a_dependent_child_in_the_persons_tax_unit"
        elif name == "drop_has_dependent_child" and args.yaml:
            target = "Explicit parent flag requires a dependent child"
        if target and not any(
            target.casefold() in record.get("test_name", "").casefold()
            for record in records
        ):
            mismatches[name] = f"intended detecting case missing: {target}"
    if mismatches:
        print(f"UNEXPECTED MUTATION RESULTS {mismatches}", flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
