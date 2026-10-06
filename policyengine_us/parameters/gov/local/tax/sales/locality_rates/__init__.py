"""County- and place-level combined state and local general sales tax rates.

`rates.csv` holds, for each covered county and each place with its own rate,
the combined state and local general sales tax rate as a step function of
the date: a row applies from `effective_from` until the key's next row, and
a key's last row applies indefinitely. Every key's first row is dated
2022-01-01 and also applies to earlier years. `place_fips` is empty for a
county's balance: its residents outside every place with its own row.

`populations.csv` holds the 2020 Census population of every key, so a
county's average rate weights its places and balance by population.

`locality_sales_tax_rates(year)` returns each key's rate for a tax year,
averaged over the days of the year as the worksheet's line 3 instructions
direct when a rate changes during the year: "Multiply each tax rate for the
period it was in effect by a fraction. The numerator of the fraction is the
number of days the rate was in effect ... and the denominator is the total
number of days in the year."
"""

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import pandas as pd

FOLDER = Path(__file__).parent

# Every key's history starts on this date.
FIRST_DATE = pd.Timestamp("2022-01-01")


def _read(name: str) -> pd.DataFrame:
    return pd.read_csv(
        FOLDER / name,
        dtype={"county_fips": str, "place_fips": str},
        keep_default_na=False,
    )


def _load_rates() -> pd.DataFrame:
    df = _read("rates.csv")
    df["effective_from"] = pd.to_datetime(df["effective_from"])
    return df.sort_values(["county_fips", "place_fips", "effective_from"]).reset_index(
        drop=True
    )


locality_rate_schedule = _load_rates()
locality_populations = _read("populations.csv")


@dataclass(frozen=True)
class LocalitySalesTaxRates:
    """Annual combined sales tax rates for the covered localities.

    - `place`: rate of each place part, indexed by county FIPS + place code
      (10 characters).
    - `balance`: rate of each county's balance, indexed by county FIPS.
    - `county_average`: population-weighted average rate of each county's
      places and balance, indexed by county FIPS.
    - `state_code`: the state of each covered county, indexed by county FIPS.
    """

    place: pd.Series
    balance: pd.Series
    county_average: pd.Series
    state_code: pd.Series


def annual_rates(schedule: pd.DataFrame, year: int) -> pd.Series:
    """Day-weighted average rate over calendar `year` for each key of
    `schedule`, indexed by (county_fips, place_fips)."""
    start_of_year = pd.Timestamp(year=year, month=1, day=1)
    end_of_year = pd.Timestamp(year=year, month=12, day=31)
    days_in_year = (end_of_year - start_of_year).days + 1
    keys = ["county_fips", "place_fips"]
    next_start = schedule.groupby(keys)["effective_from"].shift(-1)
    is_first = ~schedule.duplicated(keys)
    # A key's first rate also covers the years before its history starts.
    start = schedule["effective_from"].where(~is_first, pd.Timestamp.min)
    start = start.clip(lower=start_of_year)
    end = (next_start - pd.Timedelta(days=1)).fillna(end_of_year)
    end = end.clip(upper=end_of_year)
    days = ((end - start).dt.days + 1).clip(lower=0)
    weighted = schedule["rate"] * days / days_in_year
    return weighted.groupby([schedule[k] for k in keys]).sum()


@lru_cache(maxsize=None)
def locality_sales_tax_rates(year: int) -> LocalitySalesTaxRates:
    """Annual county, balance and place rates for a tax year."""
    rates = annual_rates(locality_rate_schedule, year).rename("rate").reset_index()
    rates = rates.merge(
        locality_populations,
        on=["county_fips", "place_fips"],
        how="left",
        validate="one_to_one",
    )
    is_balance = rates["place_fips"] == ""
    places = rates[~is_balance]
    balances = rates[is_balance].set_index("county_fips")
    weighted = (rates["rate"] * rates["population"]).groupby(rates["county_fips"])
    county_average = weighted.sum() / rates.groupby("county_fips")["population"].sum()
    state_code = (
        locality_rate_schedule.drop_duplicates("county_fips")
        .set_index("county_fips")["state_code"]
    )
    return LocalitySalesTaxRates(
        place=pd.Series(
            places["rate"].to_numpy(),
            index=places["county_fips"] + places["place_fips"],
        ),
        balance=balances["rate"],
        county_average=county_average,
        state_code=state_code,
    )
