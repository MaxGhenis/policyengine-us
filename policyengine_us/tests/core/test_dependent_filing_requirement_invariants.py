"""Invariants for the federal filing requirement with dependents in the unit.

The filing requirement of IRC 6012 depends on the filer's own gross income. A
tax unit dependent's income is on the dependent's own return, as in
`irs_gross_income`, and the dependent's own filing requirement is separate.
The unearned income test of 6012(a)(1)(C) and (f)(2)(D) applies only to an
individual another taxpayer can claim as a dependent (IRC 63(c)(5)): Chart B
of the Form 1040 instructions, not Chart A. `tax_unit_is_required_to_file`
applied that test to every tax unit, against $500 rather than the indexed
63(c)(5)(A) amount, and subtracted every member's earned income from the
filers' gross income, so a dependent's wages could turn the filer's
requirement, and with it the EITC, off.

Hypothesis draws batches of tax units (single, single and claimed as a
dependent elsewhere, head of household with dependents, joint with and
without dependents, under and over 65), and a seeded population of 200 such
units adds breadth. Dependents' wages and self-employment income are of
either sign and sometimes large. Some units have both optional filing
switches off, so the filing requirement decides the EITC. Each batch runs as
one vectorized simulation three times: as drawn; with the dependents' earned
income set to zero; and with $40,000 more of the head's wages. For every tax
unit:

1. The dependents' earned income, of any size or sign, never changes the
   filer's filing requirement, AGI or EITC.
2. Differential, in 2025: the requirement equals Chart A of the 2025 Form 1040
   instructions for filers no one can claim (gross income over the threshold
   for the filing status and age; IRC 6012(f) says "does not exceed", so
   income equal to the threshold need not file), and Chart B for a single
   filer who can be claimed as a dependent.
3. Monotonicity: more of the head's wages never turns the requirement off.
4. With both optional filing switches off, a unit that is not required to
   file gets no EITC.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01  # dollars
WAGE_SHIFT = 40_000.0
FILER_OUTPUTS = ["tax_unit_is_required_to_file", "adjusted_gross_income", "eitc"]
DEPENDENT_INPUTS = ["employment_income", "self_employment_income"]
# 2025 Form 1040 instructions, Chart A, by filing status and number of filers
# 65 or older.
CHART_A_2025 = {
    "single": [15_750, 17_750],
    "hoh": [23_625, 25_625],
    "joint": [31_500, 33_100, 34_700],
}
# Chart B, single dependents: the unearned income and gross income floor, the
# earned income addition, the cap on earned income in the gross income test,
# and the regular standard deduction; each but the cap rises by $2,000 for a
# dependent 65 or older.
CHART_B_2025 = dict(floor=1_350, addition=450, earned_cap=15_300, regular=15_750)
CHART_B_AGED_2025 = 2_000

earned = st.one_of(
    st.just(0.0),
    st.integers(-20_000, 40_000).map(float),
    st.integers(-4_000_000, 4_000_000).map(lambda x: 16.0 * x),
)


@st.composite
def tax_units(draw):
    kind = draw(
        st.sampled_from(["single", "claimed", "hoh", "joint", "joint_dependents"])
    )
    n_dependents = draw(st.integers(1, 2)) if kind in ("hoh", "joint_dependents") else 0
    high = 20_000 if kind == "claimed" else 60_000

    def filer():
        return {
            "age": draw(st.sampled_from([35, 66])),
            "employment_income": float(draw(st.integers(0, high))),
            "taxable_interest_income": float(draw(st.integers(0, 6_000))),
            "taxable_pension_income": float(
                draw(st.one_of(st.just(0), st.integers(0, 10_000)))
            ),
        }

    return {
        "kind": kind,
        "files_anyway": draw(st.booleans()),
        "head": filer(),
        "spouse": filer() if kind.startswith("joint") else None,
        "dependents": [
            {
                "age": draw(st.integers(1, 17)),
                **{name: draw(earned) for name in DEPENDENT_INPUTS},
            }
            for _ in range(n_dependents)
        ],
    }


SEED = 20261009


def _seeded_units(n=200):
    rng = np.random.default_rng(SEED)

    def some(low, high, p=0.5):
        return float(round(rng.uniform(low, high))) if rng.random() < p else 0.0

    def dependent_amount():
        if rng.random() < 0.1:
            return 16.0 * int(rng.integers(-4_000_000, 4_000_000))
        return some(-20_000, 40_000, 0.6)

    units = []
    for _ in range(n):
        kind = str(
            rng.choice(["single", "claimed", "hoh", "joint", "joint_dependents"])
        )
        n_dependents = (
            int(rng.integers(1, 3)) if kind in ("hoh", "joint_dependents") else 0
        )
        high = 20_000 if kind == "claimed" else 60_000

        def filer():
            return {
                "age": int(rng.choice([35, 66])),
                "employment_income": some(0, high, 0.8),
                "taxable_interest_income": some(0, 6_000),
                "taxable_pension_income": some(0, 10_000, 0.3),
            }

        units.append(
            {
                "kind": kind,
                "files_anyway": bool(rng.random() < 0.5),
                "head": filer(),
                "spouse": filer() if kind.startswith("joint") else None,
                "dependents": [
                    {
                        "age": int(rng.integers(1, 18)),
                        **{name: dependent_amount() for name in DEPENDENT_INPUTS},
                    }
                    for _ in range(n_dependents)
                ],
            }
        )
    return units


def _situation(units, year, *, zero_dependents=False, wage_shift=0.0):
    people, groups = {}, {"tax_units": {}, "households": {}, "marital_units": {}}
    for i, u in enumerate(units):
        head = f"head_{i}"
        people[head] = {
            "is_tax_unit_head": True,
            "is_tax_unit_dependent": False,
            "claimed_as_dependent_on_another_return": u["kind"] == "claimed",
            **u["head"],
            "employment_income": u["head"]["employment_income"] + wage_shift,
        }
        members, couple = [head], [head]
        if u["spouse"] is not None:
            spouse = f"spouse_{i}"
            people[spouse] = {
                "is_tax_unit_spouse": True,
                "is_tax_unit_dependent": False,
                **u["spouse"],
            }
            members.append(spouse)
            couple.append(spouse)
        groups["marital_units"][f"couple_{i}"] = {"members": couple}
        for j, d in enumerate(u["dependents"]):
            child = f"dependent_{i}_{j}"
            people[child] = {
                "age": d["age"],
                "is_tax_unit_dependent": True,
                **{
                    name: 0.0 if zero_dependents else d[name]
                    for name in DEPENDENT_INPUTS
                },
            }
            members.append(child)
            groups["marital_units"][f"single_{i}_{j}"] = {"members": [child]}
        groups["tax_units"][f"tax_unit_{i}"] = {
            "members": members,
            # With both switches off, only the filing requirement makes the
            # unit file, so the EITC turns on it.
            "would_file_taxes_voluntarily": {year: u["files_anyway"]},
            "would_file_if_eligible_for_refundable_credit": {year: u["files_anyway"]},
        }
        groups["households"][f"household_{i}"] = {
            "members": members,
            "state_code": {year: "TX"},
        }
    people = {
        name: {k: {year: v} for k, v in values.items()}
        for name, values in people.items()
    }
    return {"people": people, **groups}


def _run(units, year, **kwargs):
    sim = Simulation(situation=_situation(units, year, **kwargs))
    return {
        name: np.asarray(sim.calculate(name, year), dtype=float)
        for name in FILER_OUTPUTS
    }


def _filers(u):
    return [u["head"]] + ([u["spouse"]] if u["spouse"] is not None else [])


def _chart_requirement_2025(u):
    """Charts A and B of the 2025 Form 1040 instructions, from the inputs."""
    filers = _filers(u)
    wages = sum(p["employment_income"] for p in filers)
    unearned = sum(
        p["taxable_interest_income"] + p["taxable_pension_income"] for p in filers
    )
    gross = wages + unearned
    aged = sum(p["age"] >= 65 for p in filers)
    if u["kind"] == "claimed":
        b = CHART_B_2025
        extra = CHART_B_AGED_2025 * aged
        return (
            unearned > b["floor"] + extra
            or wages > b["regular"] + extra
            or gross
            > max(
                b["floor"] + extra,
                min(wages, b["earned_cap"]) + b["addition"] + extra,
            )
        )
    status = (
        "joint"
        if u["kind"].startswith("joint")
        else ("hoh" if u["dependents"] else "single")
    )
    return gross > CHART_A_2025[status][aged]


def _check(units, year):
    run = _run(units, year)
    zeroed = _run(units, year, zero_dependents=True)
    shifted = _run(units, year, wage_shift=WAGE_SHIFT)
    required = run["tax_unit_is_required_to_file"].astype(bool)

    # 1. The dependents' earned income never reaches the filer's requirement.
    for name in FILER_OUTPUTS:
        np.testing.assert_allclose(
            run[name], zeroed[name], atol=TOLERANCE, err_msg=name
        )

    # 2. Differential: Charts A and B of the 2025 instructions.
    if year == 2025:
        expected = np.array([_chart_requirement_2025(u) for u in units])
        mismatches = [
            (units[i], required[i]) for i in np.flatnonzero(required != expected)
        ]
        assert not mismatches, mismatches[:3]

    # 3. More of the head's wages never turns the requirement off.
    assert (shifted["tax_unit_is_required_to_file"].astype(bool) >= required).all()

    # 4. A unit that neither must nor would file claims no EITC.
    files_anyway = np.array([u["files_anyway"] for u in units])
    assert not (run["eitc"][~files_anyway & ~required] > 0).any()
    return required


# A batch's cost is mostly per-variable overhead, so each example is a large
# batch and there are few examples.
SETTINGS = dict(
    max_examples=5,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@settings(**SETTINGS)
@given(st.lists(tax_units(), min_size=10, max_size=40))
def test_dependents_earnings_stay_off_the_filers_requirement(units):
    _check(units, 2025)


@pytest.mark.parametrize("year", [2025, 2026])
def test_seeded_population(year):
    required = _check(_seeded_units(), year)
    # The population exercises both outcomes.
    assert required.sum() > 30
    assert (~required).sum() > 30
