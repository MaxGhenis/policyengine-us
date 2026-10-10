"""Properties of New York's claim of right rules.

Tax Law 662: when 26 U.S.C. 1341(a)(5) applies to repaid claim of right
income for federal tax, New York State tax is reduced by the decrease in the
earlier year's New York tax from excluding that income, with any excess
refunded. Tax Law 1312(a) applies the same adjustment to the New York City
tax. Tax Law 615 keeps the federal itemized deductions as they stood before
Public Law 115-97: a repayment over $3,000 that federal law deducts is Form
IT-196 line 34, and one of $3,000 or less joins the line 24 expenses subject
to the 2% floor. From 2021, Tax Law 612(c)(45) subtracts the repayment from
New York adjusted gross income, with no threshold, unless the repayment is
included in the itemized deduction or is the basis for a section 662 credit.

So a filer chooses between subtracting and the relief the subtraction rules
out, and the model takes whichever gives less New York State, New York City
and Yonkers income tax. YAML cases check single households from the forms'
instructions. These tests check properties at every point of a grid, inside
and outside New York City, and compare the model's branch computations with
independent simulations that fix both method flags as inputs:

- the lesser-of rule: New York income tax equals the smaller of the tax with
  the subtraction fixed on and the tax with it fixed off, ties going to not
  subtracting, and the flag matches;
- the branches agree with those independent simulations;
- the subtraction is the whole repayment or nothing, each credit is the whole
  prior-year decrease or nothing, and a filer never gets both;
- a filer who subtracts a repayment that the itemized deduction would
  include takes the standard deduction;
- the rules never raise tax, and tax never rises with the prior-year New
  York decrease;
- a credit above the year's tax is refunded;
- before 2021 nobody subtracts, and the credit follows the federal method.
"""

import itertools

import numpy as np
import pytest

from policyengine_us import Simulation

REPAYMENTS = [0, 1_500, 3_000, 3_001, 20_000]
FEDERAL_DECREASES = [0, 60_000]
NY_DECREASES = [0, 150, 900, 5_000]
WAGES = [0, 50_000, 120_000, 400_000]
CHARITY = [0, 25_000]
AXES = [REPAYMENTS, FEDERAL_DECREASES, NY_DECREASES, WAGES, CHARITY]
GRID = list(itertools.product(*AXES))
SHAPE = tuple(len(axis) for axis in AXES)
NY_DECREASE_AXIS = AXES.index(NY_DECREASES)
# An illustrative New York City share of the prior-year decrease.
NYC_SHARE = 0.5
TOLERANCE = 0.01
METHODS = ["claim_of_right_credit_applies", "ny_claim_of_right_subtraction_applies"]
TAXES = ["ny_income_tax", "nyc_income_tax", "ny_yonkers_income_tax"]
VARIABLES = [
    *METHODS,
    *TAXES,
    "adjusted_gross_income",
    "ny_agi",
    "ny_claim_of_right_subtraction",
    "ny_claim_of_right_subtraction_bars_itemizing",
    "ny_claim_of_right_credit",
    "nyc_claim_of_right_credit",
    "ny_deductions",
    "ny_standard_deduction",
]
BRANCHES = [
    "ny_income_tax_if_subtracting_claim_of_right_repayment",
    "ny_income_tax_if_not_subtracting_claim_of_right_repayment",
]


def axis_values(places):
    """Each grid axis, repeated once for each place."""
    return (
        np.tile(np.array([point[i] for point in GRID], dtype=float), len(places))
        for i in range(len(AXES))
    )


def simulation(year, places, repay=True, methods=None):
    """One single-person New York tax unit per grid point and place.

    `places` lists whether each copy of the grid lives in New York City.
    """
    repayment, federal_decrease, ny_decrease, wage, charitable = axis_values(places)
    in_nyc = np.repeat(places, len(GRID))
    situation = {"people": {}, "tax_units": {}, "households": {}}
    for i in range(len(repayment)):
        person = f"p{i}"
        situation["people"][person] = {
            "age": {year: 40},
            "employment_income": {year: wage[i]},
            "charitable_cash_donations": {year: charitable[i]},
        }
        if repay:
            situation["people"][person] |= {
                "claim_of_right_repayment": {year: repayment[i]},
                "claim_of_right_prior_year_tax_decrease": {year: federal_decrease[i]},
                "ny_claim_of_right_prior_year_tax_decrease": {year: ny_decrease[i]},
                "nyc_claim_of_right_prior_year_tax_decrease": {
                    year: NYC_SHARE * ny_decrease[i]
                },
            }
        situation["tax_units"][f"t{i}"] = {
            "members": [person],
            **{
                name: {year: bool(values[i])}
                for name, values in (methods or {}).items()
            },
        }
        situation["households"][f"h{i}"] = {
            "members": [person],
            "state_code": {year: "NY"},
            "in_nyc": {year: bool(in_nyc[i])},
        }
    return Simulation(situation=situation)


def calculate(simulation, year, variables):
    return {v: np.asarray(simulation.calculate(v, year)) for v in variables}


def total_tax(values):
    return sum(values[tax] for tax in TAXES)


@pytest.fixture(scope="module")
def results():
    year = 2025
    places = [False, True]
    repayment, _, ny_decrease, _, _ = axis_values(places)
    r = calculate(simulation(year, places), year, VARIABLES + BRANCHES)
    r["repayment"] = repayment
    r["ny_decrease"] = ny_decrease
    r["in_nyc"] = np.repeat(places, len(GRID))
    r["tax"] = total_tax(r)
    # Independent references: no repayment at all, and both methods fixed as
    # inputs rather than chosen in branches. The federal method is the
    # model's own, so only the New York choice differs between the two.
    none = simulation(year, places, repay=False)
    r["tax_without_repayment"] = total_tax(calculate(none, year, TAXES))
    credit_applies = r["claim_of_right_credit_applies"]
    for name, subtracts in (("subtracting", True), ("not_subtracting", False)):
        fixed = simulation(
            year,
            places,
            methods={
                "claim_of_right_credit_applies": credit_applies,
                "ny_claim_of_right_subtraction_applies": np.full(
                    len(repayment), subtracts
                ),
            },
        )
        r[f"tax_if_{name}"] = total_tax(calculate(fixed, year, TAXES))
    return r


def test_tax_is_the_lesser_of_subtracting_and_not_subtracting(results):
    r = results
    has_repayment = r["repayment"] > 0
    subtracts = has_repayment & (
        r["tax_if_subtracting"] < r["tax_if_not_subtracting"] - TOLERANCE
    )
    assert subtracts.any() and (has_repayment & ~subtracts).any(), "both occur"
    np.testing.assert_array_equal(r["ny_claim_of_right_subtraction_applies"], subtracts)
    expected = np.where(subtracts, r["tax_if_subtracting"], r["tax_if_not_subtracting"])
    np.testing.assert_allclose(r["tax"], expected, atol=TOLERANCE)


def test_branches_match_independent_simulations(results):
    r = results
    for name in ("subtracting", "not_subtracting"):
        np.testing.assert_allclose(
            r[f"ny_income_tax_if_{name}_claim_of_right_repayment"],
            r[f"tax_if_{name}"],
            atol=TOLERANCE,
        )


def test_subtraction_and_credits_are_all_or_nothing_and_exclusive(results):
    r = results
    subtracts = r["ny_claim_of_right_subtraction_applies"]
    credit_method = r["claim_of_right_credit_applies"]
    subtraction = r["ny_claim_of_right_subtraction"]
    # The subtraction has no $3,000 threshold; the credit needs section 1341.
    assert (subtracts & (r["repayment"] <= 3_000)).any()
    assert not credit_method[r["repayment"] <= 3_000].any()
    np.testing.assert_allclose(subtraction, np.where(subtracts, r["repayment"], 0))
    np.testing.assert_allclose(
        r["ny_agi"], r["adjusted_gross_income"] - subtraction, atol=TOLERANCE
    )
    claims_credit = credit_method & ~subtracts
    assert claims_credit.any() and (credit_method & subtracts).any()
    np.testing.assert_allclose(
        r["ny_claim_of_right_credit"], np.where(claims_credit, r["ny_decrease"], 0)
    )
    np.testing.assert_allclose(
        r["nyc_claim_of_right_credit"],
        np.where(claims_credit & r["in_nyc"], NYC_SHARE * r["ny_decrease"], 0),
    )
    credits = r["ny_claim_of_right_credit"] + r["nyc_claim_of_right_credit"]
    assert not np.any((subtraction > 0) & (credits > 0))


def test_subtracting_an_itemizable_repayment_takes_the_standard_deduction(results):
    r = results
    subtracts = r["ny_claim_of_right_subtraction_applies"]
    bars_itemizing = r["ny_claim_of_right_subtraction_bars_itemizing"]
    # Under section 1341(a)(5) the repayment is not deducted, so subtracting
    # it leaves the itemized deduction open.
    np.testing.assert_array_equal(
        bars_itemizing, subtracts & ~r["claim_of_right_credit_applies"]
    )
    assert bars_itemizing.any()
    np.testing.assert_allclose(
        r["ny_deductions"][bars_itemizing], r["ny_standard_deduction"][bars_itemizing]
    )


def test_tax_never_rises(results):
    r = results
    assert np.all(r["tax"] <= r["tax_without_repayment"] + TOLERANCE)
    table = r["tax"].reshape((2, *SHAPE))
    assert np.all(np.diff(table, axis=1 + NY_DECREASE_AXIS) <= TOLERANCE)


def test_a_credit_above_the_tax_is_refunded(results):
    r = results
    credit = r["ny_claim_of_right_credit"]
    refunded = credit > r["tax_without_repayment"]
    assert refunded.any(), "the grid should include refunds"
    assert np.all(r["ny_income_tax"][refunded] < 0)


def test_before_2021_nobody_subtracts():
    year = 2020
    places = [False, True]
    r = calculate(simulation(year, places), year, VARIABLES)
    _, _, ny_decrease, _, _ = axis_values(places)
    credit_method = r["claim_of_right_credit_applies"]
    assert credit_method.any()
    assert not r["ny_claim_of_right_subtraction_applies"].any()
    assert np.all(r["ny_claim_of_right_subtraction"] == 0)
    np.testing.assert_allclose(r["ny_agi"], r["adjusted_gross_income"])
    np.testing.assert_allclose(
        r["ny_claim_of_right_credit"], np.where(credit_method, ny_decrease, 0)
    )
