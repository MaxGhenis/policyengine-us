"""Validate a preserved YAML failure without accepting import/setup errors."""

import argparse
import json
from pathlib import Path

import pytest
from policyengine_core.tools.test_runner import OpenFiscaPlugin
from policyengine_us.system import system

from mutate import FailureEvidence

parser = argparse.ArgumentParser()
parser.add_argument("file")
parser.add_argument("--results", required=True, type=Path)
args = parser.parse_args()
evidence = FailureEvidence()
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
            args.file,
        ],
        plugins=[OpenFiscaPlugin(system, {}), evidence],
    )
)
valid = (
    code == 1
    and bool(evidence.failures)
    and all(
        failure["when"] == "call" and failure["assertion"]
        for failure in evidence.failures
    )
)
args.results.write_text(
    json.dumps(
        {
            "actual_exit_code": code,
            "expected_assertion_failure": valid,
            "failures": evidence.failures,
        },
        indent=2,
    )
)
raise SystemExit(0 if valid else 1)
