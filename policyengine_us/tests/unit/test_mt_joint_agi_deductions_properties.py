"""Properties of Montana's AGI-based deductions on a joint (single-column) return.

From 2021 to 2023 the Form 2 Itemized Deductions Schedule (line 1b) and the
Standard Deduction Worksheet (line 1) both take Montana AGI from Form 2 page 1,
line 14. Single, head of household and joint returns report that line in one
column, so a joint return pools both spouses' income before Montana AGI is
floored at zero. A tax unit dependent's income and adjustments are on the
dependent's own return. From 2024 Form 2 line 2 takes federal itemized
deductions (Worksheet A), so the medical floor applies to federal AGI.

The YAML files for the two variables hold the worked examples. This file checks
properties over a grid instead, which YAML cannot express: each test evaluates
every grid point in one vectorized simulation.

- 2021-2023: the medical deduction is max(0, expenses - 7.5% of the return's
  Montana AGI), and the standard deduction is 20% of that AGI held between the
  filing status minimum and maximum.
- Moving wages from one spouse to the other leaves both deductions unchanged.
  They depend only on the return's pooled Montana AGI, even where the sum of
  each spouse's Montana AGI floored at zero changes.
- A dependent child's interest income and its Montana subtraction leave the
  parents' Montana AGI unchanged.
- Each deduction is held once, by the head.
- The medical deduction lies between zero and the medical expenses.
- For a single filer the joint and separate variants agree.
- From 2024 the medical deduction is the federal medical expense deduction,
  including where PE's Montana AGI differs from federal AGI.
"""

import itertools

import numpy as np
import pytest

from policyengine_us import Simulation

MEDICAL_FLOOR = 0.075  # Itemized Deductions Schedule line 1c
STANDARD_RATE = 0.2  # Standard Deduction Worksheet line 2

COUPLE_WAGES = [0, 30_000, 60_000, 100_000]
# Wages moved from the head to the spouse; the couple's total is unchanged.
SPOUSE_WAGE_SHARES = [0, 20_000]
# The spouse's Schedule C income. PE puts a loss into a shared above-the-line
# deduction, so it pushes a spouse with little income below zero.
SPOUSE_SELF_EMPLOYMENT = [-50_000, -20_000, 0, 40_000]
MEDICAL = [0, 10_000, 30_000]
# No child; a dependent child with medical expenses; or a dependent child with
# U.S. government interest, which Montana subtracts on the child's own return.
CHILDREN = [None, "medical", "interest"]
CHILD_MEDICAL = 1_500
CHILD_INTEREST = 10_000
COUPLE_GRID = list(
    itertools.product(
        COUPLE_WAGES, SPOUSE_WAGE_SHARES, SPOUSE_SELF_EMPLOYMENT, MEDICAL, CHILDREN
    )
)
SINGLE_GRID = list(
    itertools.product([0, 20_000, 100_000], [-10_000, 0], MEDICAL, [40, 70])
)
STATE_YEARS = [2021, 2022, 2023]
FEDERAL_YEARS = [2024, 2025]
YEARS = STATE_YEARS + FEDERAL_YEARS


def every_year(value):
    return {year: value for year in YEARS}


@pytest.fixture(scope="module")
def grid():
    """One simulation holding every couple and single-filer grid point."""
    people, tax_units, households = {}, {}, {}
    unit_of_person, role = [], []
    for i, (wages, share, se, medical, child) in enumerate(COUPLE_GRID):
        spouse_wages = min(share, wages)
        head, spouse = f"c{i}_head", f"c{i}_spouse"
        people[head] = {
            "age": every_year(40),
            "employment_income": every_year(wages - spouse_wages),
            "other_medical_expenses": every_year(medical),
        }
        people[spouse] = {
            "age": every_year(40),
            "employment_income": every_year(spouse_wages),
            "self_employment_income": every_year(se),
        }
        members = [head, spouse]
        if child is not None:
            name = f"c{i}_child"
            people[name] = {"age": every_year(10)}
            if child == "medical":
                people[name]["other_medical_expenses"] = every_year(CHILD_MEDICAL)
            else:
                people[name]["taxable_interest_income"] = every_year(CHILD_INTEREST)
                people[name]["us_govt_interest_person"] = every_year(CHILD_INTEREST)
            members.append(name)
        unit_of_person += [i] * len(members)
        role += ["head", "spouse", "dependent"][: len(members)]
        tax_units[f"c{i}"] = {"members": members}
        households[f"c{i}"] = {"members": members, "state_code": every_year("MT")}
    for j, (wages, se, medical, age) in enumerate(SINGLE_GRID):
        name = f"s{j}"
        people[name] = {
            "age": every_year(age),
            "employment_income": every_year(wages),
            "self_employment_income": every_year(se),
            "other_medical_expenses": every_year(medical),
        }
        unit_of_person.append(len(COUPLE_GRID) + j)
        role.append("head")
        tax_units[name] = {"members": [name]}
        households[name] = {"members": [name], "state_code": every_year("MT")}
    sim = Simulation(
        situation={"people": people, "tax_units": tax_units, "households": households}
    )
    return sim, np.array(unit_of_person), np.array(role)


N_COUPLES = len(COUPLE_GRID)
COUPLES = slice(0, N_COUPLES)
SINGLES = slice(N_COUPLES, None)


def per_unit(sim, variable, year, unit):
    """Sum a person-level variable to its tax unit, in grid order."""
    return np.bincount(unit, weights=sim.calculate(variable, year))


def montana_agi_reference(sim, year):
    # Before 2024 the grid's only Montana adjustment is the dependent child's
    # U.S. government interest subtraction, which belongs on the child's own
    # return. So page 1 line 14 is the return's federal AGI, floored at zero
    # like PE's.
    return np.maximum(sim.calculate("adjusted_gross_income", year), 0)


def twin_pairs():
    """Couples that differ only in how the couple's wages are split."""
    index = {point: i for i, point in enumerate(COUPLE_GRID)}
    pairs = [
        (index[(w, 0, se, m, c)], index[(w, share, se, m, c)])
        for w, share, se, m, c in COUPLE_GRID
        if share > 0 and w >= share
    ]
    return np.array(pairs).T


def summed_individual_agi(sim, year, unit):
    """The old base: each member's Montana AGI floored at zero, then added."""
    return per_unit(sim, "mt_agi_indiv", year, unit)


@pytest.mark.parametrize("year", STATE_YEARS)
def test_premises(grid, year):
    sim, unit, _ = grid
    filing_status = sim.calculate("filing_status", year).decode_to_str()
    assert set(filing_status[COUPLES]) == {"JOINT"}
    assert set(filing_status[SINGLES]) == {"SINGLE"}
    # PE's joint Montana AGI is the return's federal AGI here, including where
    # a dependent child has interest and its subtraction.
    np.testing.assert_allclose(
        sim.calculate("mt_agi_joint", year), montana_agi_reference(sim, year)
    )
    # Splitting the wages differently does not change the return's AGI...
    first, second = twin_pairs()
    agi = sim.calculate("adjusted_gross_income", year)
    np.testing.assert_allclose(agi[first], agi[second])
    # ...but it does change the sum of each spouse's Montana AGI floored at
    # zero, so the grid reaches the cases where pooling matters.
    summed = summed_individual_agi(sim, year, unit)
    assert np.any(np.abs(summed[first] - summed[second]) > 1)


@pytest.mark.parametrize("year", STATE_YEARS)
def test_medical_floor_uses_the_return_montana_agi(grid, year):
    sim, unit, role = grid
    expenses = sim.calculate("itemized_medical_expenses", year)
    expected = np.maximum(
        expenses - MEDICAL_FLOOR * montana_agi_reference(sim, year), 0
    )
    deduction = per_unit(sim, "mt_medical_expense_deduction_joint", year, unit)
    np.testing.assert_allclose(deduction, expected, atol=0.01)
    held = sim.calculate("mt_medical_expense_deduction_joint", year)
    assert np.all(held[role != "head"] == 0)
    assert np.all(deduction >= 0)
    assert np.all(deduction <= expenses + 0.01)
    first, second = twin_pairs()
    np.testing.assert_allclose(deduction[first], deduction[second])
    assert deduction.max() > 0
    # The old base would have split the twins' deductions somewhere.
    summed = summed_individual_agi(sim, year, unit)
    unpooled = np.maximum(expenses - MEDICAL_FLOOR * summed, 0)
    assert np.any(np.abs(unpooled[first] - unpooled[second]) > 1)


@pytest.mark.parametrize("year", STATE_YEARS)
def test_standard_deduction_uses_the_return_montana_agi(grid, year):
    sim, unit, role = grid
    p = sim.tax_benefit_system.parameters(
        f"{year}-01-01"
    ).gov.states.mt.tax.income.deductions.standard
    filing_status = sim.calculate("filing_status", year).decode_to_str()
    minimum = p.floor[filing_status]
    maximum = p.cap[filing_status]
    expected = np.clip(
        STANDARD_RATE * montana_agi_reference(sim, year), minimum, maximum
    )
    deduction = per_unit(sim, "mt_standard_deduction_joint", year, unit)
    np.testing.assert_allclose(deduction, expected, atol=0.01)
    held = sim.calculate("mt_standard_deduction_joint", year)
    assert np.all(held[role != "head"] == 0)
    first, second = twin_pairs()
    np.testing.assert_allclose(deduction[first], deduction[second])
    # Some returns fall between the minimum and maximum.
    assert np.any((deduction > minimum + 1) & (deduction < maximum - 1))
    # The old base would have split the twins' deductions somewhere.
    summed = summed_individual_agi(sim, year, unit)
    unpooled = np.clip(STANDARD_RATE * summed, minimum, maximum)
    assert np.any(np.abs(unpooled[first] - unpooled[second]) > 1)


@pytest.mark.parametrize("year", STATE_YEARS)
def test_single_filer_joint_and_separate_variants_agree(grid, year):
    sim, unit, _ = grid
    for joint, separate in [
        ("mt_medical_expense_deduction_joint", "mt_medical_expense_deduction_indiv"),
        ("mt_standard_deduction_joint", "mt_standard_deduction_indiv"),
    ]:
        np.testing.assert_allclose(
            per_unit(sim, joint, year, unit)[SINGLES],
            per_unit(sim, separate, year, unit)[SINGLES],
            atol=0.01,
        )


@pytest.mark.parametrize("year", FEDERAL_YEARS)
def test_from_2024_the_federal_medical_deduction_carries_through(grid, year):
    sim, unit, role = grid
    federal = sim.calculate("medical_expense_deduction", year)
    deduction = per_unit(sim, "mt_medical_expense_deduction_joint", year, unit)
    np.testing.assert_allclose(deduction, federal, atol=0.01)
    held = sim.calculate("mt_medical_expense_deduction_joint", year)
    assert np.all(held[role != "head"] == 0)
    # The grid includes returns whose PE Montana AGI differs from federal AGI
    # (the subtraction for taxpayers 65 and older) and that deduct expenses.
    montana_agi = sim.calculate("mt_agi_joint", year)
    federal_agi = np.maximum(sim.calculate("adjusted_gross_income", year), 0)
    assert np.any((montana_agi < federal_agi - 1) & (deduction > 0))
