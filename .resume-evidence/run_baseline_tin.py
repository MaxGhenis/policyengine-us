"""Run the canonical regression against current main's exact formula."""

import importlib
import subprocess
import sys

import policyengine_core
import pytest

module = importlib.import_module(
    "policyengine_us.variables.household.demographic.person.has_tin"
)
source = subprocess.check_output(
    [
        "git",
        "show",
        "dd9cb3f6839d290c8490c561b54b7afeedc3c888:"
        "policyengine_us/variables/household/demographic/person/has_tin.py",
    ],
    text=True,
)
namespace = {}
exec(compile(source, "current-main/has_tin.py", "exec"), namespace)
print("Updated formula: full TIN test file", flush=True)
green = pytest.main(["policyengine_us/tests/core/test_has_tin_branch_inputs.py", "-q"])
print("Updated formula pytest exit:", green, flush=True)
module.has_tin.formula = namespace["has_tin"].formula
print(
    "Formula source: current main dd9cb3f6839d290c8490c561b54b7afeedc3c888", flush=True
)
print("Core source:", policyengine_core.__file__, flush=True)
sys.exit(
    pytest.main(
        [
            "policyengine_us/tests/core/test_has_tin_branch_inputs.py",
            "-k",
            "test_formula_reads_branch_or_ancestor_canonical_has_tin",
            "-q",
        ]
    )
)
