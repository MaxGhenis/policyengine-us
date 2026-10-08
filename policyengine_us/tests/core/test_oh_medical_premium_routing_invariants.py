"""Invariants for where Ohio's medical care deduction puts insurance premiums.

R.C. 5747.01(A)(10)(a) deducts medical care insurance premiums in full, but
not for a taxpayer "eligible to participate in any subsidized health plan
maintained by any employer of the taxpayer or of the taxpayer's spouse" or
entitled to Medicare Part A. Division (b) deducts medical care, premiums
included (division (c), IRC 213(d)(1)(D)), above 7.5% of federal AGI. Both
count only amounts "not otherwise deducted or excluded" in computing federal
AGI. The 2025 IT 1040 instructions (p. 41) split the premiums between
worksheet line 1 (no Medicare or employer-paid plan) and line 3 (eligible for
either), and reduce line 1 by the federal self-employed health insurance
deduction.

Hypothesis draws batches of tax units (single, joint, head of household or
joint with dependents). Each person has an age on either side of Medicare
eligibility, employer coverage, an offer of it, an employer contribution
category or employer-paid premiums, premiums entered directly or as reported
non-Medicare premiums, pre-tax payroll premiums, self-employment income,
other medical care and long-term care premiums. A seeded population of 150
units adds breadth. Each batch runs as one vectorized simulation, and again
with every employer-plan signal removed. For every person and tax unit:

1. Exclusion: the premiums Ohio counts equal the premiums paid less pre-tax
   payroll premiums and the federal self-employed health insurance deduction,
   floored at zero. This is a consistency check: it reads the same engine
   variables the formula reads, so it catches a dropped term or floor, not an
   error upstream.
2. Routing: a separate rule written here from the raw inputs puts a person's
   premiums on line 1 exactly when the person is not Medicare eligible and
   neither the head nor the spouse has an employer-paid plan, and on line 3
   otherwise. It restates the model's reading of the law (which signals show
   an employer-paid plan), so it cross-checks the code rather than reading
   the law independently.
3. Conservation: each person's line 1 and line 3 premiums sum to the
   premiums Ohio counts, so no premium is dropped or counted twice.
4. Bounds: 0 <= the tax unit deduction <= the premiums Ohio counts plus
   long-term care premiums plus other medical care.
5. Dominance: removing every employer-plan signal moves premiums from line 3
   to line 1, where no 7.5% floor applies, so it never lowers the deduction
   and leaves federal AGI unchanged.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01  # dollars

# Medicare Part A entitlement begins at 65 (42 U.S.C. 426(a)); no one here
# receives Social Security disability benefits.
MEDICARE_AGE = 65
YEAR = 2025
CATEGORIES = ["NONE", "SOME", "ALL", "NA"]
EMPLOYER_PAID = {"SOME", "ALL"}

amounts = st.one_of(
    st.just(0.0),
    st.integers(1, 3_000).map(float),
    st.integers(3_000, 20_000).map(float),
)


@st.composite
def people(draw):
    return {
        "age": draw(st.sampled_from([30, 50, 64, 65, 72])),
        "employment_income": draw(
            st.one_of(st.just(0.0), st.integers(1, 150_000).map(float))
        ),
        "self_employment_income": draw(
            st.one_of(st.just(0.0), st.integers(-20_000, 40_000).map(float))
        ),
        "has_esi": draw(st.booleans()),
        "offered_aca_disqualifying_esi": draw(st.booleans()),
        "category": draw(st.sampled_from(CATEGORIES)),
        "employer_sponsored_insurance_premiums": draw(
            st.sampled_from([0.0, 0.0, 6_000.0])
        ),
        "direct": draw(st.booleans()),
        "premiums": draw(amounts),
        "pre_tax_health_insurance_premiums": draw(amounts),
        "other_medical_expenses": draw(amounts),
        "long_term_health_insurance_premiums": draw(amounts),
    }


@st.composite
def tax_units(draw):
    kind = draw(st.sampled_from(["single", "joint", "hoh", "joint_dependents"]))
    n_dependents = draw(st.integers(1, 2)) if kind in ("hoh", "joint_dependents") else 0
    return {
        "head": draw(people()),
        "spouse": draw(people()) if kind.startswith("joint") else None,
        "dependents": [draw(people()) for _ in range(n_dependents)],
    }


SEED = 20261008


def _seeded_units(n=150):
    rng = np.random.default_rng(SEED)

    def amount():
        return float(
            [0, rng.integers(1, 3_001), rng.integers(3_000, 20_001)][rng.choice(3)]
        )

    def person():
        return {
            "age": int(rng.choice([30, 50, 64, 65, 72])),
            "employment_income": float(rng.integers(0, 150_001)),
            "self_employment_income": float(rng.integers(-20_000, 40_001))
            if rng.random() < 0.3
            else 0.0,
            "has_esi": bool(rng.random() < 0.4),
            "offered_aca_disqualifying_esi": bool(rng.random() < 0.2),
            "category": str(rng.choice(CATEGORIES)),
            "employer_sponsored_insurance_premiums": 6_000.0
            if rng.random() < 0.2
            else 0.0,
            "direct": bool(rng.random() < 0.5),
            "premiums": amount(),
            "pre_tax_health_insurance_premiums": amount()
            if rng.random() < 0.3
            else 0.0,
            "other_medical_expenses": amount(),
            "long_term_health_insurance_premiums": amount(),
        }

    units = []
    for _ in range(n):
        kind = rng.choice(["single", "joint", "hoh", "joint_dependents"])
        n_dependents = (
            int(rng.integers(1, 3)) if kind in ("hoh", "joint_dependents") else 0
        )
        units.append(
            {
                "head": person(),
                "spouse": person() if kind.startswith("joint") else None,
                "dependents": [person() for _ in range(n_dependents)],
            }
        )
    return units


def _without_employer_plans(units):
    def strip(person):
        return {
            **person,
            "has_esi": False,
            "offered_aca_disqualifying_esi": False,
            "category": "NA",
            "employer_sponsored_insurance_premiums": 0.0,
        }

    return [
        {
            "head": strip(unit["head"]),
            "spouse": None if unit["spouse"] is None else strip(unit["spouse"]),
            "dependents": [strip(d) for d in unit["dependents"]],
        }
        for unit in units
    ]


def _members(unit):
    yield "head", unit["head"]
    if unit["spouse"] is not None:
        yield "spouse", unit["spouse"]
    for dependent in unit["dependents"]:
        yield "dependent", dependent


def _situation(units):
    people, groups = {}, {"tax_units": {}, "households": {}, "marital_units": {}}
    for i, unit in enumerate(units):
        members, couple = [], []
        for j, (role, values) in enumerate(_members(unit)):
            name = f"{role}_{i}_{j}"
            premium_input = (
                "health_insurance_premiums"
                if values["direct"]
                else "health_insurance_premiums_without_medicare_part_b"
            )
            people[name] = {
                "age": values["age"],
                "is_tax_unit_head": role == "head",
                "is_tax_unit_spouse": role == "spouse",
                "is_tax_unit_dependent": role == "dependent",
                "employment_income": values["employment_income"],
                "self_employment_income": values["self_employment_income"],
                "is_self_employed": values["self_employment_income"] != 0,
                "has_esi": values["has_esi"],
                "offered_aca_disqualifying_esi": values[
                    "offered_aca_disqualifying_esi"
                ],
                "employer_contribution_to_health_insurance_premiums_category": values[
                    "category"
                ],
                "employer_sponsored_insurance_premiums": values[
                    "employer_sponsored_insurance_premiums"
                ],
                premium_input: values["premiums"],
                "pre_tax_health_insurance_premiums": values[
                    "pre_tax_health_insurance_premiums"
                ],
                "other_medical_expenses": values["other_medical_expenses"],
                "long_term_health_insurance_premiums": values[
                    "long_term_health_insurance_premiums"
                ],
            }
            members.append(name)
            if role == "dependent":
                groups["marital_units"][f"single_{name}"] = {"members": [name]}
            else:
                couple.append(name)
        groups["marital_units"][f"couple_{i}"] = {"members": couple}
        groups["tax_units"][f"tax_unit_{i}"] = {"members": members}
        groups["households"][f"household_{i}"] = {
            "members": members,
            "state_code": {YEAR: "OH"},
        }
    people = {
        name: {key: {YEAR: value} for key, value in values.items()}
        for name, values in people.items()
    }
    return {"people": people, **groups}


PERSON = [
    "medical_expense_health_insurance_premiums",
    "pre_tax_health_insurance_premiums",
    "self_employed_health_insurance_ald_person",
    "oh_unreimbursed_health_insurance_premiums",
    "oh_uninsured_unreimbursed_medical_care_expenses",
    "oh_insured_unreimbursed_medical_care_expense_amount",
    "other_medical_expenses",
    "long_term_health_insurance_premiums",
]
TAX_UNIT = [
    "adjusted_gross_income",
    "oh_unreimbursed_medical_care_expense_deduction",
]


def _run(units):
    sim = Simulation(situation=_situation(units))
    out = {
        name: np.asarray(sim.calculate(name, YEAR), dtype=float)
        for name in PERSON + TAX_UNIT
    }
    out["unit"] = sim.populations["tax_unit"].members_entity_id
    return out


def _employer_paid_plan(filer):
    employer_pays = (
        filer["category"] in EMPLOYER_PAID
        or filer["employer_sponsored_insurance_premiums"] > 0
    )
    # An explicit NONE category says the employer pays nothing (COBRA paid in
    # full, for example), so that coverage is not a subsidized plan.
    pays_nothing = filer["category"] == "NONE" and not employer_pays
    covered_or_offered = filer["has_esi"] or filer["offered_aca_disqualifying_esi"]
    return employer_pays or (covered_or_offered and not pays_nothing)


def _expected_line_3(units):
    """Whether each person's premiums go on line 3, from the raw inputs."""
    flags = []
    for unit in units:
        filers = [unit["head"]] + ([unit["spouse"]] if unit["spouse"] else [])
        employer_plan = any(map(_employer_paid_plan, filers))
        for _, person in _members(unit):
            flags.append(employer_plan or person["age"] >= MEDICARE_AGE)
    return np.array(flags)


def _unit_sum(run, values):
    return np.bincount(
        run["unit"],
        weights=values,
        minlength=len(run["oh_unreimbursed_medical_care_expense_deduction"]),
    )


def _check(units):
    base = _run(units)
    counted = base["oh_unreimbursed_health_insurance_premiums"]
    line_1 = base["oh_uninsured_unreimbursed_medical_care_expenses"]
    line_3 = (
        base["oh_insured_unreimbursed_medical_care_expense_amount"]
        - base["other_medical_expenses"]
    )

    # 1. Exclusion of premiums excluded or deducted federally.
    np.testing.assert_allclose(
        counted,
        np.maximum(
            base["medical_expense_health_insurance_premiums"]
            - base["pre_tax_health_insurance_premiums"]
            - base["self_employed_health_insurance_ald_person"],
            0,
        ),
        atol=TOLERANCE,
    )

    # 2. Routing against the independent rule.
    on_line_3 = _expected_line_3(units)
    np.testing.assert_allclose(line_1, np.where(on_line_3, 0, counted), atol=TOLERANCE)
    np.testing.assert_allclose(line_3, np.where(on_line_3, counted, 0), atol=TOLERANCE)

    # 3. Conservation.
    np.testing.assert_allclose(line_1 + line_3, counted, atol=TOLERANCE)

    # 4. Bounds.
    deduction = base["oh_unreimbursed_medical_care_expense_deduction"]
    ceiling = _unit_sum(
        base,
        counted
        + base["long_term_health_insurance_premiums"]
        + base["other_medical_expenses"],
    )
    assert (deduction >= 0).all()
    assert (deduction <= ceiling + TOLERANCE).all()

    # 5. Dominance: line 1 has no floor, so losing the employer plan never
    # lowers the deduction.
    without = _run(_without_employer_plans(units))
    np.testing.assert_allclose(
        without["adjusted_gross_income"],
        base["adjusted_gross_income"],
        atol=TOLERANCE,
    )
    assert (
        without["oh_unreimbursed_medical_care_expense_deduction"]
        >= deduction - TOLERANCE
    ).all()


@settings(
    max_examples=3,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(st.lists(tax_units(), min_size=5, max_size=30))
def test_oh_medical_premium_routing_invariants(units):
    _check(units)


def test_oh_medical_premium_routing_seeded_population():
    _check(_seeded_units())
