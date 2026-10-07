"""Rerun the membership grid with explicit canonical tax-unit source roles.

Temporary composition evidence for #9617: share one grid simulation and
reuse the independent membership/NPCR rules in the existing property suite.
No model or checked-in test file is altered.
"""

import importlib.util
from pathlib import Path

import numpy as np
from policyengine_us import Simulation

path = (
    Path.cwd()
    / "policyengine_us/tests/core/test_mo_tanf_dependent_parent_properties.py"
)
spec = importlib.util.spec_from_file_location("mo_membership_source_role_grid", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
situation = module._situation(module.HOUSEHOLDS)
expected_heads = []
expected_spouses = []
for i, role in module.PEOPLE:
    person = situation["people"][f"h{i}_{role}"]
    head = role == "head"
    spouse = role == "spouse"
    person["is_tax_unit_head"] = {module.YEAR: head}
    person["is_tax_unit_spouse"] = {module.YEAR: spouse}
    expected_heads.append(head)
    expected_spouses.append(spouse)
sim = Simulation(situation=situation)
np.testing.assert_array_equal(
    sim.calculate("is_tax_unit_head", module.YEAR), expected_heads
)
np.testing.assert_array_equal(
    sim.calculate("is_tax_unit_spouse", module.YEAR), expected_spouses
)
for name in (
    "test_membership_matches_the_restated_rule",
    "test_non_parent_caretaker_identification_matches_independent_rule",
    "test_a_dependent_parent_member_excludes_the_non_parent_caretaker",
    "test_unit_income_is_members_income",
):
    getattr(module, name)(sim)
    print(f"PASS {name} with explicit canonical source roles", flush=True)
print(
    f"Explicit-role grid: {len(module.HOUSEHOLDS)} households, {len(module.PEOPLE)} people",
    flush=True,
)
