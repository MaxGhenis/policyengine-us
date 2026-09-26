"""Property tests for eitc_relevant_investment_income.

IRC 32(i)(2) and Publication 596 Worksheet 1 build disqualified income from
the filer's own return in three baskets: portfolio income (lines 1-4), capital
gain net income floored at zero (lines 5-7), and net passive income floored at
zero (lines 11-13), leaving out passive income or loss that is also earned
income. Hypothesis draws batches of tax units (single or joint filers, with up
to two dependents) and runs each batch, with the variants each property
compares, through one vectorized simulation. For every input:

1. Each floored basket is nonnegative, so the total is at least the filers'
   portfolio income.
2. The total is nondecreasing in every income input of a head or spouse:
   interest, tax-exempt interest, dividends, long-term, short-term and
   non-Schedule D capital gains, rental income, farm rental income, and
   passive partnership and S corporation income.
3. A dependent's amounts, of any sign, never change the result.
4. Swapping the head's and spouse's inputs never changes the result, since a
   joint return pools both spouses on each worksheet line.
5. Partnership self-employment earnings only classify passive income as
   earned. The total is nonincreasing in them. This is intended: they are not
   investment income, and more of the passive share counted as earned leaves
   less of it on lines 11 and 12. Earnings that match or exceed a same-sign
   passive share remove the whole share, and earnings of the opposite sign
   remove none of it.
6. Differential check: the vectorized formula equals scalar Worksheet 1
   line 14 arithmetic, with the model's inputs placed on the worksheet lines
   the formula's comments name.

Amounts are whole dollars below 2**24 in every sum, so float32 holds them
exactly and the checks are to the cent.
"""

import math

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEAR = 2025
TOLERANCE = 0.01
MAX_AMOUNT = 250_000
AGES = {"head": 40, "spouse": 38, "dependent": 10}

PORTFOLIO_INPUTS = [
    "taxable_interest_income",
    "tax_exempt_interest_income",
    "dividend_income",
]
CAPITAL_GAIN_INPUTS = [
    "long_term_capital_gains",
    "short_term_capital_gains",
    "non_sch_d_capital_gains",
]
PASSIVE_INPUTS = [
    "rental_income",
    "farm_rent_income",
    "passive_partnership_s_corp_income",
]
INCOME_INPUTS = PORTFOLIO_INPUTS + CAPITAL_GAIN_INPUTS + PASSIVE_INPUTS
SE_EARNINGS = "partnership_self_employment_net_earnings"
PASSIVE = "passive_partnership_s_corp_income"

SETTINGS = settings(
    max_examples=25,
    deadline=None,
    derandomize=True,
    database=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


def _amounts(nonnegative):
    low = 0 if nonnegative else -MAX_AMOUNT
    # Zeros are drawn often so that baskets land exactly on the floor.
    return st.one_of(st.just(0), st.integers(low, MAX_AMOUNT))


@st.composite
def _person_inputs(draw):
    inputs = {
        name: draw(_amounts(nonnegative=name in PORTFOLIO_INPUTS))
        for name in INCOME_INPUTS
    }
    passive = inputs[PASSIVE]
    # Partnership self-employment earnings matching, exceeding, falling
    # short of, or opposing the passive share.
    relation = draw(
        st.sampled_from(["none", "equal", "double", "opposite", "independent"])
    )
    if relation == "independent":
        se_earnings = draw(_amounts(nonnegative=False))
    else:
        factor = {"none": 0, "equal": 1, "double": 2, "opposite": -1}[relation]
        se_earnings = factor * passive
    inputs[SE_EARNINGS] = se_earnings
    return inputs


@st.composite
def _tax_unit(draw):
    members = [("head", draw(_person_inputs()))]
    if draw(st.booleans()):
        members.append(("spouse", draw(_person_inputs())))
    for _ in range(draw(st.integers(0, 2))):
        members.append(("dependent", draw(_person_inputs())))
    return members


TAX_UNITS = st.lists(_tax_unit(), min_size=1, max_size=8)


def _compute(tax_units):
    """eitc_relevant_investment_income for each tax unit, in one simulation."""
    people, units, households = {}, {}, {}
    for i, members in enumerate(tax_units):
        names = []
        for j, (role, inputs) in enumerate(members):
            name = f"unit_{i}_person_{j}"
            names.append(name)
            people[name] = {
                "age": {YEAR: AGES[role]},
                "is_tax_unit_head": {YEAR: role == "head"},
                "is_tax_unit_spouse": {YEAR: role == "spouse"},
                **{var: {YEAR: value} for var, value in inputs.items()},
            }
        units[f"unit_{i}"] = {"members": names}
        households[f"unit_{i}"] = {"members": names}
    simulation = Simulation(
        situation={
            "people": people,
            "tax_units": units,
            "households": households,
        }
    )
    return simulation.calculate("eitc_relevant_investment_income", YEAR)


def _filers(members):
    return [inputs for role, inputs in members if role != "dependent"]


def _portfolio_income(members):
    return sum(p[name] for p in _filers(members) for name in PORTFOLIO_INPUTS)


def _passive_not_earned(inputs):
    # Written independently of the formula: the same-sign overlap with
    # self-employment earnings is earned income, up to the smaller magnitude.
    passive = inputs[PASSIVE]
    se_earnings = inputs[SE_EARNINGS]
    if passive * se_earnings > 0:
        return math.copysign(max(0, abs(passive) - abs(se_earnings)), passive)
    return passive


def _worksheet_1_line_14(members):
    filers = _filers(members)
    line_1 = sum(p["taxable_interest_income"] for p in filers)
    line_2 = sum(p["tax_exempt_interest_income"] for p in filers)
    line_3 = sum(p["dividend_income"] for p in filers)
    line_4 = 0  # Form 8814 elections are not modeled.
    line_5 = max(0, sum(p[name] for p in filers for name in CAPITAL_GAIN_INPUTS))
    line_6 = 0  # No Form 4797 section 1231 input.
    line_7 = max(0, line_5 - line_6)
    line_10 = 0  # Royalties and personal property rents are in rental_income.
    passive_items = [
        amount
        for p in filers
        for amount in (
            p["rental_income"],
            p["farm_rent_income"],
            _passive_not_earned(p),
        )
    ]
    line_11 = sum(amount for amount in passive_items if amount > 0)
    line_12 = sum(amount for amount in passive_items if amount < 0)
    line_13 = max(0, line_11 + line_12)
    return line_1 + line_2 + line_3 + line_4 + line_7 + line_10 + line_13


def _replace(members, role, **changes):
    return [
        (r, {**inputs, **changes}) if r == role else (r, inputs)
        for r, inputs in members
    ]


@SETTINGS
@given(TAX_UNITS)
def test_matches_worksheet_1_arithmetic(tax_units):
    result = _compute(tax_units)
    expected = [_worksheet_1_line_14(members) for members in tax_units]
    np.testing.assert_allclose(result, expected, rtol=0, atol=TOLERANCE)


@SETTINGS
@given(TAX_UNITS)
def test_floored_baskets_are_nonnegative(tax_units):
    result = _compute(tax_units)
    portfolio = np.array([_portfolio_income(members) for members in tax_units])
    assert np.all(result >= portfolio - TOLERANCE)
    assert np.all(result >= 0)


@SETTINGS
@given(TAX_UNITS, st.data())
def test_nondecreasing_in_each_income_input(tax_units, data):
    bumped = []
    for members in tax_units:
        role = data.draw(st.sampled_from([r for r, _ in members if r != "dependent"]))
        name = data.draw(st.sampled_from(INCOME_INPUTS))
        increase = data.draw(st.integers(0, MAX_AMOUNT))
        inputs = dict(members)[role]
        bumped.append(_replace(members, role, **{name: inputs[name] + increase}))
    result = _compute(tax_units + bumped)
    base, after = result[: len(tax_units)], result[len(tax_units) :]
    assert np.all(after >= base - TOLERANCE)


@SETTINGS
@given(TAX_UNITS, st.data())
def test_dependents_never_change_the_filers_result(tax_units, data):
    replaced = []
    zeroed = []
    for members in tax_units:
        replaced.append(
            [
                (role, data.draw(_person_inputs()) if role == "dependent" else inputs)
                for role, inputs in members
            ]
        )
        zeroed.append(
            [
                (role, {k: 0 for k in inputs} if role == "dependent" else inputs)
                for role, inputs in members
            ]
        )
    n = len(tax_units)
    result = _compute(tax_units + replaced + zeroed)
    np.testing.assert_allclose(result[n : 2 * n], result[:n], rtol=0, atol=TOLERANCE)
    np.testing.assert_allclose(result[2 * n :], result[:n], rtol=0, atol=TOLERANCE)


@SETTINGS
@given(TAX_UNITS)
def test_head_and_spouse_are_interchangeable(tax_units):
    swapped = []
    for members in tax_units:
        inputs = dict((r, i) for r, i in members if r != "dependent")
        if "spouse" in inputs:
            members = _replace(members, "head", **inputs["spouse"])
            members = _replace(members, "spouse", **inputs["head"])
        swapped.append(members)
    n = len(tax_units)
    result = _compute(tax_units + swapped)
    np.testing.assert_allclose(result[n:], result[:n], rtol=0, atol=TOLERANCE)


def _set_for_filers(members, change):
    return [
        (role, {**inputs, **change(inputs)}) if role != "dependent" else (role, inputs)
        for role, inputs in members
    ]


@SETTINGS
@given(TAX_UNITS, st.data())
def test_self_employment_earnings_only_classify_passive_income(tax_units, data):
    raised, matched, opposed, without_earnings, without_passive = [], [], [], [], []
    for members in tax_units:
        role = data.draw(st.sampled_from([r for r, _ in members if r != "dependent"]))
        increase = data.draw(st.integers(0, MAX_AMOUNT))
        se_earnings = dict(members)[role][SE_EARNINGS]
        raised.append(_replace(members, role, **{SE_EARNINGS: se_earnings + increase}))
        scale = data.draw(st.integers(1, 3))
        matched.append(
            _set_for_filers(members, lambda i: {SE_EARNINGS: scale * i[PASSIVE]})
        )
        opposed.append(
            _set_for_filers(members, lambda i: {SE_EARNINGS: -scale * i[PASSIVE]})
        )
        without_earnings.append(_set_for_filers(members, lambda i: {SE_EARNINGS: 0}))
        without_passive.append(
            _set_for_filers(members, lambda i: {PASSIVE: 0, SE_EARNINGS: 0})
        )
    n = len(tax_units)
    result = _compute(
        tax_units + raised + matched + opposed + without_earnings + without_passive
    )
    base, after_raise, after_match, after_oppose, no_earnings, no_passive = (
        result[k * n : (k + 1) * n] for k in range(6)
    )
    # Intended: more self-employment earnings never raise investment income.
    assert np.all(after_raise <= base + TOLERANCE)
    # Same-sign earnings at least as large as each filer's passive share
    # remove all of it; opposite-sign earnings remove none of it.
    np.testing.assert_allclose(after_match, no_passive, rtol=0, atol=TOLERANCE)
    np.testing.assert_allclose(after_oppose, no_earnings, rtol=0, atol=TOLERANCE)
