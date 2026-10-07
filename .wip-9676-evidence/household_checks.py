"""Household checks for #9676, run once per code (PYTHONPATH picks main or branch).

usage: household_checks.py LABEL OUT_JSON

Prints and saves, for 2026-01, membership, parent flag, NPCR identification,
unit size, countable resources and mo_tanf for:
  - the two zero-income regressions the PR body must disclose;
  - the resource counterexample kept for the follow-up (fixture A) and the
    included-NPCR spouse sketch (fixture B);
  - the income-loss case and its zero-income pair added to the YAML.
"""

import json
import sys

import numpy as np

import policyengine_us
from policyengine_us import Simulation

YEAR = 2026
JAN = "2026-01"

CASES = {
    "regression_unmarked_grandparent": {
        "grandparent": dict(age=55),
        "mother": dict(age=20, is_tax_unit_dependent=True, own_children_in_household=1),
        "child": dict(age=3, is_tax_unit_dependent=True),
    },
    "regression_dependent_45_adult_child": {
        "head": dict(age=40, own_children_in_household=1),
        "child": dict(age=10, is_tax_unit_dependent=True),
        "dependent_45": dict(
            age=45, is_tax_unit_dependent=True, own_children_in_household=1
        ),
        "her_adult_child": dict(age=20, is_tax_unit_dependent=True),
    },
    "resource_fixture_a_excluded_grandparent_assets": {
        "grandparent": dict(
            age=55, mo_tanf_is_non_parent_caretaker=True, bank_account_assets=5_000
        ),
        "mother": dict(age=20, is_tax_unit_dependent=True, own_children_in_household=1),
        "child": dict(age=3, is_tax_unit_dependent=True),
    },
    "resource_fixture_b_included_npcr_spouse_assets": {
        "grandfather": dict(age=62, mo_tanf_is_non_parent_caretaker=True),
        "grandmother": dict(
            age=60, mo_tanf_is_non_parent_caretaker=True, bank_account_assets=5_000
        ),
        "grandchild": dict(age=8, is_tax_unit_dependent=True),
    },
    "income_loss_disability_14400": {
        "grandparent": dict(age=55, mo_tanf_is_non_parent_caretaker=True),
        "mother": dict(
            age=31,
            is_tax_unit_dependent=True,
            own_children_in_household=3,
            disability_benefits=14_400,
        ),
        "child1": dict(age=10, is_tax_unit_dependent=True),
        "child2": dict(age=8, is_tax_unit_dependent=True),
        "child3": dict(age=6, is_tax_unit_dependent=True),
    },
    "income_loss_zero_income_pair": {
        "grandparent": dict(age=55, mo_tanf_is_non_parent_caretaker=True),
        "mother": dict(age=31, is_tax_unit_dependent=True, own_children_in_household=3),
        "child1": dict(age=10, is_tax_unit_dependent=True),
        "child2": dict(age=8, is_tax_unit_dependent=True),
        "child3": dict(age=6, is_tax_unit_dependent=True),
    },
}


def situation(name, people):
    persons = {
        f"{name}_{p}": {k: {YEAR: v} for k, v in inputs.items()}
        for p, inputs in people.items()
    }
    members = list(persons)
    return {
        "people": persons,
        "tax_units": {"t": {"members": members}},
        "spm_units": {"s": {"members": members}},
        "households": {"h": {"members": members, "state_code": {YEAR: "MO"}}},
    }


def run(name, people):
    # One simulation per household: an explicit input in one household would
    # otherwise reset unspecified people's values in the others.
    sim = Simulation(situation=situation(name, people))

    def person(v, period=JAN):
        return [
            bool(x) if isinstance(x, (bool, np.bool_)) else float(x)
            for x in sim.calculate(v, period)
        ]

    def unit(v, period=JAN):
        return float(sim.calculate(v, period)[0])

    return {
        "people": list(people),
        "member": person("mo_tanf_is_assistance_unit_member"),
        "parent_flag": person("mo_tanf_is_parent_of_dependent_child", YEAR),
        "npcr": person("mo_tanf_non_parent_caretaker"),
        "npcr_included": unit("mo_tanf_non_parent_caretaker_included"),
        "size": unit("mo_tanf_assistance_unit_size"),
        "gross_unearned": unit("mo_tanf_gross_unearned_income"),
        "countable_income": unit("mo_tanf_countable_income"),
        "standard_of_need": unit("mo_tanf_standard_of_need"),
        "countable_resources": unit("mo_tanf_countable_resources"),
        "resources_eligible": unit("mo_tanf_resources_eligible"),
        "ssi": person("ssi"),
        "mo_tanf": unit("mo_tanf"),
    }


if __name__ == "__main__":
    label, out_json = sys.argv[1:]
    out = {"label": label, "module": policyengine_us.__file__, "cases": {}}
    for name, people in CASES.items():
        out["cases"][name] = run(name, people)
        print(name, json.dumps(out["cases"][name]), flush=True)
    json.dump(out, open(out_json, "w"), indent=1)
