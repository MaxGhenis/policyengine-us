"""Run one missing #9676 YAML comparison from an external temporary fixture."""

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
from pathlib import Path

import pytest
import policyengine_us
from policyengine_core.tools.test_runner import OpenFiscaPlugin
from policyengine_us.system import system

from mutate import FailureEvidence

FIXTURE_HASH = "0a01250de835a9e5067ac7f5e212fd8cb141b7a403262d6cc0e7cf9f97db2d96"
MAIN = "5b1d5bdf47044607341d76f3c932ba2e7b74a060"
OLD = "a6c44418afccac0270dcb9ea155338dac0c9a05d"


class ComparisonEvidence(FailureEvidence):
    def __init__(self):
        super().__init__()
        self.collected = 0
        self.passed = 0

    def pytest_collection_finish(self, session):
        self.collected = len(session.items)

    def pytest_runtest_logreport(self, report):
        if report.when == "call" and report.passed:
            self.passed += 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("code", choices=("main", "old_head"))
    parser.add_argument("fixture", type=Path)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--failure-output", type=Path)
    args = parser.parse_args()
    root = Path.cwd().resolve()
    fixture = args.fixture.resolve()
    assert not fixture.is_relative_to(root)
    assert hashlib.sha256(fixture.read_bytes()).hexdigest() == FIXTURE_HASH
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    assert sha == (MAIN if args.code == "main" else OLD)
    assert Path(policyengine_us.__file__).resolve().is_relative_to(root)
    core = importlib.metadata.version("policyengine-core")
    assert core == "3.32.15"
    assert platform.python_version() == "3.14.7"
    formula = (
        root
        / "policyengine_us/variables/gov/states/mo/dss/tanf/assistance_unit/mo_tanf_is_assistance_unit_member.py"
    )
    runtime = {
        "code_sha": sha,
        "policyengine_core": core,
        "policyengine_us_version": importlib.metadata.version("policyengine-us"),
        "policyengine_us_file": str(Path(policyengine_us.__file__).resolve()),
        "python": platform.python_version(),
        "membership_formula_sha256": hashlib.sha256(formula.read_bytes()).hexdigest(),
    }
    evidence = ComparisonEvidence()
    code = int(
        pytest.main(
            [
                "--capture",
                "no",
                "--maxfail",
                "0",
                "--tb",
                "short",
                "--confcutdir",
                str(fixture.parent),
                "-p",
                "no:cacheprovider",
                str(fixture),
            ],
            plugins=[OpenFiscaPlugin(system, {}), evidence],
        )
    )
    assertions = bool(evidence.failures) and all(
        row.get("when") == "call"
        and row.get("exception") == "AssertionError"
        and row.get("assertion") is True
        for row in evidence.failures
    )
    valid = evidence.collected == 16 and (
        code == 1 and assertions and evidence.passed + len(evidence.failures) == 16
        if args.code == "main"
        else code == 0 and evidence.passed == 16 and not evidence.failures
    )
    if args.failure_output:
        args.failure_output.write_text(
            json.dumps(
                {
                    "actual_exit_code": code,
                    "expected_assertion_failure": code == 1 and assertions,
                    "failures": evidence.failures,
                },
                indent=2,
            )
        )
    args.receipt.write_text(
        json.dumps(
            {
                "controller_run_id": os.environ["GITHUB_RUN_ID"],
                "controller_sha": os.environ["GITHUB_SHA"],
                "code": args.code,
                "runtime": runtime,
                "fixture": str(fixture),
                "fixture_sha256": FIXTURE_HASH,
                "collected": evidence.collected,
                "passed": evidence.passed,
                "underlying_exit": code,
                "wrapper_exit": 0 if valid else 1,
                "all_failures_are_call_assertions": assertions,
                "failures": evidence.failures,
            },
            indent=2,
        )
    )
    raise SystemExit(0 if valid else 1)
