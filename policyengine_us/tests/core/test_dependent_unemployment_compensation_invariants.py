"""Invariants for dependents' unemployment compensation on the filer's return.

A tax unit dependent's unemployment compensation is on the dependent's own
return, as in `irs_gross_income`. The 2020 exclusion (IRC 85(c)) is figured on
each return's own compensation and modified AGI: up to $10,200 paid to the
taxpayer, or on a joint return to each spouse, when modified AGI, which leaves
out the compensation, is under $150,000 (2020 Form 1040 instructions,
Unemployment Compensation Exclusion Worksheet). Before this change the
exclusion pooled the dependents' compensation with the filers', capped the
pool at one $10,200, and subtracted the compensation from modified AGI a
second time; a dependent's negative compensation could also zero out the
filers' share.

Hypothesis draws batches of tax units (single, head of household with
dependents, joint with and without dependents), and a seeded population of 200
such units adds breadth. Filers have wages and interest only, so their
modified AGI is known exactly; wages reach past the $150,000 cutoff.
Dependents' compensation is of either sign and sometimes large. Some units
have both optional filing switches off, so the filing requirement decides the
EITC. Each batch runs as one vectorized simulation in 2020 and in 2025, twice:
as drawn and with the dependents' compensation set to zero. For every tax unit:

1. The dependents' compensation, of any size or sign, never changes the
   filer's taxable compensation (the tax unit's, the head's or the spouse's),
   AGI, filing requirement or EITC.
2. Differential: the tax unit's taxable compensation equals an independent
   numpy computation of the worksheet over the head and spouse, and each
   person's equals their own compensation less their own exclusion (a
   dependent's with their own modified AGI, here zero).
3. Accounting: when the filers' compensation is positive in total, the head's
   and spouse's taxable compensation sums to the tax unit's.
4. Bounds: the tax unit's taxable compensation is at most the filers'
   compensation and at least that less $10,200 per filer; after 2020 it
   equals the filers' compensation, and for tax units without dependents the
   all-member total, as before.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01  # dollars
EXCLUSION = {2020: 10_200.0, 2025: 0.0}
CUTOFF = 150_000.0
# The filer's amounts, which a dependent's compensation must not change.
FILER_OUTPUTS = [
    "tax_unit_taxable_unemployment_compensation",
    "adjusted_gross_income",
    "tax_unit_is_required_to_file",
    "eitc",
]
OUTPUTS = FILER_OUTPUTS + ["tax_unit_unemployment_compensation"]

compensation = st.one_of(st.just(0.0), st.integers(1, 30_000).map(float))
dependent_compensation = st.one_of(
    st.just(0.0),
    st.integers(-25_000, 25_000).map(float),
    st.integers(-4_000_000, 4_000_000).map(lambda x: 16.0 * x),
)


@st.composite
def tax_units(draw):
    kind = draw(st.sampled_from(["single", "hoh", "joint", "joint_dependents"]))
    n_dependents = draw(st.integers(1, 2)) if kind in ("hoh", "joint_dependents") else 0

    def filer():
        return {
            "employment_income": float(
                draw(st.one_of(st.integers(0, 40_000), st.integers(120_000, 180_000)))
            ),
            "taxable_interest_income": float(draw(st.integers(0, 2_000))),
            "unemployment_compensation": draw(compensation),
        }

    return {
        "files_anyway": draw(st.booleans()),
        "head": filer(),
        "spouse": filer() if kind.startswith("joint") else None,
        "dependents": [
            {
                "age": draw(st.integers(1, 17)),
                "unemployment_compensation": draw(dependent_compensation),
            }
            for _ in range(n_dependents)
        ],
    }


SEED = 20261008


def _seeded_units(n=200):
    rng = np.random.default_rng(SEED)

    def some(low, high, p=0.5):
        return float(round(rng.uniform(low, high))) if rng.random() < p else 0.0

    def filer():
        wages = (
            some(0, 40_000, 0.7) if rng.random() < 0.7 else some(120_000, 180_000, 1)
        )
        return {
            "employment_income": wages,
            "taxable_interest_income": some(1, 2_000),
            "unemployment_compensation": some(1, 30_000),
        }

    def dependent_amount():
        if rng.random() < 0.1:
            return 16.0 * int(rng.integers(1_000_000, 4_000_000))
        return some(-25_000, 25_000, 0.7)

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
                        "unemployment_compensation": dependent_amount(),
                    }
                    for _ in range(n_dependents)
                ],
            }
        )
    return units


def _situation(units, year, *, zero_dependents=False):
    people, groups = {}, {"tax_units": {}, "households": {}, "marital_units": {}}
    for i, u in enumerate(units):
        head = f"head_{i}"
        people[head] = {
            "age": 35,
            "is_tax_unit_head": True,
            "is_tax_unit_dependent": False,
            **u["head"],
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
                "unemployment_compensation": (
                    0.0 if zero_dependents else d["unemployment_compensation"]
                ),
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
    out["person_taxable"] = np.asarray(
        sim.calculate("taxable_unemployment_compensation", year), dtype=float
    )
    out["unit"] = sim.populations["tax_unit"].members_entity_id
    return out


def _people(units):
    """Each person's (tax unit, is filer, inputs), in member order."""
    rows = []
    for i, u in enumerate(units):
        rows.append((i, True, u["head"]))
        if u["spouse"] is not None:
            rows.append((i, True, u["spouse"]))
        rows += [(i, False, d) for d in u["dependents"]]
    return rows


def _check(units, year):
    run = _run(units, year)
    zeroed = _run(units, year, zero_dependents=True)
    rows = _people(units)
    unit = np.array([i for i, _, _ in rows])
    filer = np.array([is_filer for _, is_filer, _ in rows])
    uc = np.array([p["unemployment_compensation"] for _, _, p in rows])
    n_units = len(units)

    def unit_sum(values):
        return np.bincount(unit, weights=values, minlength=n_units)

    has_dependent = unit_sum((~filer).astype(float)) > 0

    # 1. The dependents' compensation never reaches the filer's return.
    for name in FILER_OUTPUTS:
        np.testing.assert_allclose(
            run[name], zeroed[name], atol=TOLERANCE, err_msg=name
        )
    np.testing.assert_allclose(
        run["person_taxable"][filer], zeroed["person_taxable"][filer], atol=TOLERANCE
    )

    # 2. Differential: the worksheet over the head and spouse, whose modified
    # AGI is their wages and interest.
    wages_and_interest = np.array(
        [
            p.get("employment_income", 0) + p.get("taxable_interest_income", 0)
            for _, _, p in rows
        ]
    )
    modified_agi = unit_sum(filer * wages_and_interest)
    eligible = modified_agi < CUTOFF
    excludable = np.minimum(np.maximum(0, uc), EXCLUSION[year])
    filer_uc = unit_sum(filer * uc)
    expected = filer_uc - eligible * unit_sum(filer * excludable)
    taxable = run["tax_unit_taxable_unemployment_compensation"]
    np.testing.assert_allclose(taxable, expected, atol=TOLERANCE)
    # A dependent here has no other income, so their modified AGI is zero.
    positive = filer_uc > 0
    expected_person = np.where(
        filer,
        np.where(positive[unit], uc - eligible[unit] * excludable, 0),
        uc - excludable,
    )
    np.testing.assert_allclose(run["person_taxable"], expected_person, atol=TOLERANCE)

    # 3. Accounting: the head's and spouse's shares sum to the tax unit's.
    np.testing.assert_allclose(
        unit_sum(filer * run["person_taxable"])[positive],
        taxable[positive],
        atol=TOLERANCE,
    )

    # 4. Bounds, and no change after 2020 for tax units without dependents.
    n_filers = unit_sum(filer.astype(float))
    assert (taxable <= filer_uc + TOLERANCE).all()
    assert (taxable >= filer_uc - EXCLUSION[year] * n_filers - TOLERANCE).all()
    if EXCLUSION[year] == 0:
        np.testing.assert_allclose(taxable, filer_uc, atol=TOLERANCE)
        np.testing.assert_allclose(
            taxable[~has_dependent],
            run["tax_unit_unemployment_compensation"][~has_dependent],
            atol=TOLERANCE,
        )
    return has_dependent, eligible


# A batch's cost is mostly per-variable overhead, so each example is a large
# batch and there are few examples.
SETTINGS = dict(
    max_examples=4,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@settings(**SETTINGS)
@given(st.lists(tax_units(), min_size=10, max_size=40))
def test_dependent_compensation_stays_off_the_filers_return(units):
    for year in EXCLUSION:
        _check(units, year)


@pytest.mark.parametrize("year", list(EXCLUSION))
def test_seeded_population(year):
    has_dependent, eligible = _check(_seeded_units(), year)
    # The population exercises both sides of the dependent and cutoff tests.
    assert has_dependent.sum() > 50
    assert (~has_dependent).sum() > 50
    assert eligible.sum() > 50
    assert (~eligible).sum() > 20
