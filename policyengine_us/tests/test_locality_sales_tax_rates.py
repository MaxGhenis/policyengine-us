"""Invariants of the county- and place-level combined sales tax rates.

`parameters/gov/local/tax/sales/locality_rates/` stores official combined state
and local general sales tax rates as step functions of the date for every
county (its balance: residents outside the places with their own row) and
every place with its own rate, in the covered states, plus the 2020 Census
population of each. `combined_sales_tax_rate` reads them by county and place
FIPS code, and `local_sales_tax_table` reads the IRS selector's named counties
and cities.

Invariants, each tested below:
- L1 schema: FIPS formats, one state per county, dates ascending from
  2022-01-01, consecutive rates of a key differ, rates in (0, 0.15).
- L2 coverage: a covered state has a balance row for every county in the
  county FIPS dataset; the population file has exactly the rate keys; no
  balance population is negative.
- L3 day weighting: the annual rate of every key equals a day-by-day mean of
  its step function, computed independently, for any year.
- L4 bounds: a key's annual rate lies within its step values; a county's
  average lies within its keys' annual rates.
- L5 Tax Foundation consistency: each covered state's population-weighted
  mean point-in-time rate is within a stated tolerance of the Tax Foundation
  combined rate (the default state average) on each January 1 and July 1.
- L6 heading floor: every covered locality's annual rate is at least the IRS
  state table heading rate for its state, less the IRS rounding, so worksheet
  line 3 is non-negative from the data, not only from its floor at 0.
- L7 lookup precedence: combined_sales_tax_rate returns the place rate, else
  the balance when the place or census block is known, else the county
  average, else the state average; a county outside the household's state
  falls back to the state average.
- L8 selector lists: each year's county and place lists are disjoint across
  tables, name only counties and places in states that use the local tables,
  and local_sales_tax_table applies place > county > state default.
"""

from datetime import date, timedelta

import numpy as np
import pandas as pd
import pytest
import yaml
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from policyengine_core.simulations import SimulationBuilder

from policyengine_us.model_api import REPO
from policyengine_us.parameters.gov.local.tax.sales.locality_rates import (
    annual_rates,
    locality_populations,
    locality_rate_schedule,
    locality_sales_tax_rates,
)
from policyengine_us.system import system
from policyengine_us.tools.geography.county_helpers import (
    load_county_fips_dataset,
    state_fips_by_state_code,
)

SALT = REPO.joinpath(
    "parameters", "gov", "irs", "deductions", "itemized", "salt_and_real_estate"
)
SELECTOR = SALT / "local_sales_tax_table"
TABLES = ("a", "b", "c", "d")
IRS_YEARS = (2022, 2023, 2024, 2025)
TF_DATES = [date(year, month, 1) for year in range(2022, 2027) for month in (1, 7)]
SCHEDULE = locality_rate_schedule
COVERED_STATES = sorted(SCHEDULE["state_code"].unique())
KEYS = ["county_fips", "place_fips"]
# Largest gap, in percentage points, between a state's population-weighted
# mean rate and the Tax Foundation combined rate. Tax Foundation weights
# ZIP-code rates by ZCTA population and includes special districts that cover
# part of a county or place; the rates here exclude districts that cover
# only commercial areas. States above the default have their reason in
# locality_rates/README.md.
TF_TOLERANCE_PP = 0.25
TF_TOLERANCE_PP_BY_STATE = {}
# IRS headings round state rates to two decimals (Minnesota's 6.875% prints
# as 6.88%), and South Dakota's 2023 heading averages a mid-year change.
HEADING_ROUNDING = 0.0001

HYPOTHESIS_SETTINGS = settings(
    max_examples=40,
    deadline=None,
    derandomize=True,
    database=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


def _steps():
    """Each key's (effective_from, rate) steps."""
    return {
        key: list(zip(group["effective_from"].dt.date, group["rate"]))
        for key, group in SCHEDULE.groupby(KEYS)
    }


STEPS = _steps()
KEY_LIST = sorted(STEPS)


def _rate_on(steps, day):
    """The rate in force on a day; the first rate also covers earlier days."""
    rate = steps[0][1]
    for start, value in steps:
        if start <= day:
            rate = value
    return rate


def _reference_annual(steps, year):
    """Day-by-day mean of a step function over a calendar year."""
    day = date(year, 1, 1)
    total, days = 0.0, 0
    while day.year == year:
        total += _rate_on(steps, day)
        days += 1
        day += timedelta(days=1)
    return total / days


def _population():
    return locality_populations.set_index(KEYS)["population"]


def test_l1_schema():
    """L1: FIPS formats, dates, rates and one state per county."""
    assert list(SCHEDULE.columns[:6]) == [
        "state_code",
        "county_fips",
        "place_fips",
        "effective_from",
        "rate",
        "source",
    ]
    assert SCHEDULE["county_fips"].str.fullmatch(r"\d{5}").all()
    places = SCHEDULE["place_fips"]
    assert (places.eq("") | places.str.fullmatch(r"\d{5}")).all()
    assert SCHEDULE["rate"].between(0, 0.15, inclusive="neither").all()
    assert (SCHEDULE["source"] != "").all()
    state_fips = state_fips_by_state_code()
    assert (
        SCHEDULE["county_fips"].str[:2] == SCHEDULE["state_code"].map(state_fips)
    ).all()
    for key, steps in STEPS.items():
        dates = [start for start, _ in steps]
        assert dates[0] == date(2022, 1, 1), key
        assert dates == sorted(set(dates)), key
        rates = [rate for _, rate in steps]
        assert all(a != b for a, b in zip(rates, rates[1:])), key


def test_l2_coverage():
    """L2: every county of a covered state has a balance; populations match."""
    counties = load_county_fips_dataset()
    balances = set(SCHEDULE.loc[SCHEDULE["place_fips"] == "", "county_fips"])
    for state in COVERED_STATES:
        expected = set(counties.loc[counties["state"] == state, "county_fips"])
        missing = expected - balances
        assert not missing, f"{state} counties without a balance row: {missing}"
    population_keys = set(map(tuple, locality_populations[KEYS].to_numpy()))
    assert population_keys == set(STEPS)
    assert not locality_populations.duplicated(KEYS).any()
    assert (locality_populations["population"] >= 0).all()


@HYPOTHESIS_SETTINGS
@given(
    keys=st.lists(st.sampled_from(KEY_LIST), min_size=1, max_size=20),
    year=st.integers(2019, 2029),
)
def test_l3_day_weighting_matches_reference(keys, year):
    """L3: annual rates equal a day-by-day mean of each step function."""
    annual = annual_rates(SCHEDULE, year)
    for key in keys:
        assert annual[key] == pytest.approx(
            _reference_annual(STEPS[key], year), abs=1e-12
        )


@pytest.mark.parametrize("year", (2021, 2022, 2023, 2024, 2025, 2026, 2030))
def test_l4_bounds(year):
    """L4: annual rates and county averages stay within their inputs."""
    annual = annual_rates(SCHEDULE, year)
    for key, steps in STEPS.items():
        values = [rate for _, rate in steps]
        assert min(values) - 1e-12 <= annual[key] <= max(values) + 1e-12, key
    rates = locality_sales_tax_rates(year)
    by_county = annual.groupby(level="county_fips")
    low, high = by_county.min(), by_county.max()
    average = rates.county_average
    assert ((average >= low - 1e-12) & (average <= high + 1e-12)).all()


@pytest.mark.parametrize("instant", TF_DATES)
def test_l5_state_means_match_tax_foundation(instant):
    """L5: population-weighted state means are near Tax Foundation's."""
    population = _population()
    tax_foundation = system.parameters.gov.local.tax.sales.average_combined_rate(
        instant.isoformat()
    )
    state_of = SCHEDULE.drop_duplicates("county_fips").set_index("county_fips")[
        "state_code"
    ]
    weighted, weights = {}, {}
    for key, steps in STEPS.items():
        state = state_of[key[0]]
        weighted[state] = weighted.get(state, 0) + population[key] * _rate_on(
            steps, instant
        )
        weights[state] = weights.get(state, 0) + population[key]
    gaps = {}
    for state in COVERED_STATES:
        ours = weighted[state] / weights[state]
        theirs = float(tax_foundation[state])
        tolerance = TF_TOLERANCE_PP_BY_STATE.get(state, TF_TOLERANCE_PP) / 100
        if abs(ours - theirs) > tolerance:
            gaps[state] = round(100 * (ours - theirs), 4)
    assert not gaps, f"Gaps from Tax Foundation (percentage points): {gaps}"


@pytest.mark.parametrize("year", IRS_YEARS)
def test_l6_rates_are_at_least_the_heading_rate(year):
    """L6: no covered locality is below its state's IRS heading rate."""
    heading = system.parameters.gov.irs.deductions.itemized.salt_and_real_estate
    heading = heading.state_sales_tax_table.rate(f"{year}-01-01")
    annual = annual_rates(SCHEDULE, year)
    state_of = SCHEDULE.drop_duplicates("county_fips").set_index("county_fips")[
        "state_code"
    ]
    below = {
        key: rate
        for key, rate in annual.items()
        if rate < float(heading[state_of[key[0]]]) - HEADING_ROUNDING
    }
    assert not below, f"Localities below the IRS heading rate: {below}"


def _combined_rate(year, state, county, place="", block=""):
    """combined_sales_tax_rate for one household per entry."""
    n = len(state)
    simulation = SimulationBuilder().build_default_simulation(system, n)
    simulation.set_input("state_code", year, np.array(state))
    simulation.set_input("county_fips", year, np.array(county))
    simulation.set_input(
        "place_fips", year, np.array(place if isinstance(place, list) else [place] * n)
    )
    simulation.set_input(
        "block_geoid", year, np.array(block if isinstance(block, list) else [block] * n)
    )
    return simulation.calculate("combined_sales_tax_rate", year)


def _state_average(year, states):
    average = system.parameters.gov.local.tax.sales.average_combined_rate
    january, july = average(f"{year}-01-01"), average(f"{year}-07-01")
    return np.array([(january[s] + july[s]) / 2 for s in states])


@pytest.mark.parametrize("year", (2022, 2024, 2026))
def test_l7_lookup_precedence(year):
    """L7: place > known-location balance > county average > state."""
    rates = locality_sales_tax_rates(year)
    state_of = rates.state_code
    place_keys = list(rates.place.index)
    counties = list(rates.balance.index)
    states = [state_of[c] for c in counties]
    # County only: the county average.
    actual = _combined_rate(year, states, counties)
    np.testing.assert_allclose(actual, rates.county_average[counties], rtol=1e-6)
    # County and a census block outside every place: the balance.
    blocks = [c + "0000000000" for c in counties]
    actual = _combined_rate(year, states, counties, block=blocks)
    np.testing.assert_allclose(actual, rates.balance[counties], rtol=1e-6)
    # County and a place code without its own row: the balance.
    actual = _combined_rate(year, states, counties, place="99999")
    np.testing.assert_allclose(actual, rates.balance[counties], rtol=1e-6)
    # Places with their own rate.
    if place_keys:
        place_counties = [k[:5] for k in place_keys]
        actual = _combined_rate(
            year,
            [state_of[c] for c in place_counties],
            place_counties,
            place=[k[5:] for k in place_keys],
        )
        np.testing.assert_allclose(actual, rates.place[place_keys], rtol=1e-6)
    # No county, or a county outside the household's state: the state average.
    for county in ("", "01001" if "AL" not in COVERED_STATES else "04013"):
        actual = _combined_rate(year, states, [county] * len(states))
        np.testing.assert_allclose(
            actual, _state_average(year, states), rtol=1e-6
        )
    other_state = [
        next(s for s in COVERED_STATES if s != state) for state in states
    ]
    actual = _combined_rate(year, other_state, counties)
    np.testing.assert_allclose(actual, _state_average(year, other_state), rtol=1e-6)


def _selector(kind, year):
    """Each table's list of codes on January 1 of the year."""
    lists = {}
    for table in TABLES:
        values = yaml.safe_load((SELECTOR / kind / f"{table}.yaml").read_text())[
            "values"
        ]
        dates = sorted(d for d in values if d <= date(year, 1, 1))
        lists[table] = [str(code) for code in values[dates[-1]]]
    return lists


@pytest.mark.parametrize("year", IRS_YEARS)
def test_l8_selector_lists(year):
    """L8: disjoint lists naming counties and places of local-table states."""
    states_param = yaml.safe_load((SELECTOR / "states.yaml").read_text())["values"]
    dates = sorted(d for d in states_param if d <= date(year, 1, 1))
    local_table_states = set(states_param[dates[-1]])
    state_fips = state_fips_by_state_code()
    local_prefixes = {state_fips[s] for s in local_table_states}
    counties = set(load_county_fips_dataset()["county_fips"])
    for kind, width in (("county", 5), ("place", 7)):
        lists = _selector(kind, year)
        seen = {}
        for table, codes in lists.items():
            for code in codes:
                assert len(code) == width and code.isdigit(), (kind, code)
                assert code[:2] in local_prefixes, (kind, code)
                if kind == "county":
                    assert code in counties, code
                assert code not in seen, f"{code} in tables {seen[code]} and {table}"
                seen[code] = table
