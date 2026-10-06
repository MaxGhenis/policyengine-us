"""Invariants for dependents' Social Security in the filer's taxability base.

Social Security benefits are taxable, if at all, to the person with the legal
right to receive them (IRS Pub. 915, "Who is taxed"). A tax unit dependent's
benefits are figured on the dependent's own return
(`dependent_taxable_social_security`), so the IRC 86 base on the filer's
return, `tax_unit_social_security_for_taxability`, is the head's and spouse's
benefits only. It was the tax unit total less the dependents' benefits, and in
float32 a dependent's benefits of about $16.8 million or more rounded that
total, moving the filer's base by a dollar or more.

Hypothesis draws batches of tax units (single, head of household with
dependents, joint with and without dependents), and a seeded population of 200
such units adds breadth. Dependents' benefits are of either sign and sometimes
$16 million or more. Some units have both optional filing switches off, so the
filing requirement decides the EITC. Each batch runs as one vectorized
simulation three times: as drawn; with the dependents' benefits set to zero;
and with $1,000 more of the head's benefits. For every tax unit:

1. The dependents' benefits, of any size or sign, never change the filer's
   taxability base, taxable Social Security, AGI, filing requirement or EITC.
2. Differential: the base equals an independent float64 sum of the head's and
   spouse's benefits, floored at zero.
3. Bounds: 0 <= taxable Social Security <= 85% of the base (IRC 86(a)(2)).
   $1,000 more of the head's benefits raises the base by exactly $1,000 when
   the filers' benefits are not negative.
4. For tax units without dependents, the base equals the previous formula,
   the tax unit total floored at zero.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01  # dollars
SHIFT = 1_000.0
# The filer's amounts, which a dependent's benefits must not change.
FILER_OUTPUTS = [
    "tax_unit_social_security_for_taxability",
    "tax_unit_taxable_social_security",
    "adjusted_gross_income",
    "tax_unit_is_required_to_file",
    "eitc",
]
OUTPUTS = FILER_OUTPUTS + ["tax_unit_social_security"]

benefits = st.one_of(st.just(0.0), st.integers(1, 40_000).map(float))
# Up to $64 million either way, in multiples of 16 so float32 holds them
# exactly; a tax unit total above about $16.8 million rounds in float32.
dependent_benefits = st.one_of(
    st.just(0.0),
    st.integers(-12_000, 12_000).map(float),
    st.integers(-4_000_000, 4_000_000).map(lambda x: 16.0 * x),
)


@st.composite
def tax_units(draw):
    kind = draw(st.sampled_from(["single", "hoh", "joint", "joint_dependents"]))
    n_dependents = draw(st.integers(1, 2)) if kind in ("hoh", "joint_dependents") else 0

    def filer():
        return {
            "employment_income": float(draw(st.integers(0, 40_000))),
            "taxable_interest_income": float(draw(st.integers(0, 2_000))),
            "social_security": draw(benefits),
        }

    return {
        "files_anyway": draw(st.booleans()),
        "head": filer(),
        "spouse": filer() if kind.startswith("joint") else None,
        "dependents": [
            {
                "age": draw(st.integers(1, 17)),
                "social_security": draw(dependent_benefits),
            }
            for _ in range(n_dependents)
        ],
    }


SEED = 20261007


def _seeded_units(n=200):
    rng = np.random.default_rng(SEED)

    def some(high, p=0.5):
        return float(round(rng.uniform(1, high))) if rng.random() < p else 0.0

    def filer():
        return {
            "employment_income": some(40_000, 0.7),
            "taxable_interest_income": some(2_000),
            "social_security": some(40_000, 0.6),
        }

    def dependent_amount():
        if rng.random() < 0.2:
            return 16.0 * int(rng.integers(1_000_000, 4_000_000))
        return float(round(rng.uniform(-12_000, 12_000))) if rng.random() < 0.6 else 0.0

    units = []
    for _ in range(n):
        kind = rng.choice(["single", "hoh", "joint", "joint_dependents"])
        n_dependents = (
            int(rng.integers(1, 3)) if kind in ("hoh", "joint_dependents") else 0
        )
        units.append(
            {
                "files_anyway": bool(rng.random() < 0.5),
                "head": filer(),
                "spouse": filer() if kind.startswith("joint") else None,
                "dependents": [
                    {
                        "age": int(rng.integers(1, 18)),
                        "social_security": dependent_amount(),
                    }
                    for _ in range(n_dependents)
                ],
            }
        )
    return units


def _situation(units, year, *, zero_dependents=False, head_shift=0.0):
    people, groups = {}, {"tax_units": {}, "households": {}, "marital_units": {}}
    for i, u in enumerate(units):
        head = f"head_{i}"
        people[head] = {
            "age": 35,
            "is_tax_unit_head": True,
            "is_tax_unit_dependent": False,
            **u["head"],
            "social_security": u["head"]["social_security"] + head_shift,
        }
        members, couple = [head], [head]
        if u["spouse"] is not None:
            spouse = f"spouse_{i}"
            people[spouse] = {
                "age": 33,
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
                "social_security": 0.0 if zero_dependents else d["social_security"],
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
    out = {name: np.asarray(sim.calculate(name, year), dtype=float) for name in OUTPUTS}
    out["unit"] = sim.populations["tax_unit"].members_entity_id
    return out


def _filer_benefits(units):
    """Float64 sum of the head's and spouse's benefits, by tax unit."""
    return np.array(
        [
            u["head"]["social_security"]
            + (u["spouse"]["social_security"] if u["spouse"] is not None else 0.0)
            for u in units
        ]
    )


def _check(units, year):
    run = _run(units, year)
    zeroed = _run(units, year, zero_dependents=True)
    shifted = _run(units, year, head_shift=SHIFT)
    has_dependent = np.array([len(u["dependents"]) > 0 for u in units])

    # 1. The dependents' benefits never reach the filer's return.
    for name in FILER_OUTPUTS:
        np.testing.assert_allclose(
            run[name], zeroed[name], atol=TOLERANCE, err_msg=name
        )

    # 2. Differential: the head's and spouse's benefits, floored at zero.
    base = run["tax_unit_social_security_for_taxability"]
    filer_benefits = _filer_benefits(units)
    np.testing.assert_allclose(base, np.maximum(0, filer_benefits), atol=TOLERANCE)

    # 3. Bounds, and an exact shift in the head's benefits.
    taxable = run["tax_unit_taxable_social_security"]
    assert (taxable >= -TOLERANCE).all()
    assert (taxable <= 0.85 * base + TOLERANCE).all()
    nonnegative = filer_benefits >= 0
    np.testing.assert_allclose(
        (shifted["tax_unit_social_security_for_taxability"] - base)[nonnegative],
        SHIFT,
        atol=TOLERANCE,
    )

    # 4. Without dependents: the previous formula, unchanged.
    np.testing.assert_allclose(
        base[~has_dependent],
        np.maximum(0, run["tax_unit_social_security"][~has_dependent]),
        atol=TOLERANCE,
    )
    return has_dependent


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
def test_dependent_benefits_stay_off_the_filers_taxability_base(units):
    _check(units, 2025)


def test_seeded_population():
    has_dependent = _check(_seeded_units(), 2025)
    # The population exercises both branches of property 4.
    assert has_dependent.sum() > 50
    assert (~has_dependent).sum() > 50
