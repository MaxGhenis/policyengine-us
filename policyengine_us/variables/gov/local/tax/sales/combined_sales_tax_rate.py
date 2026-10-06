from policyengine_us.model_api import *
from policyengine_us.parameters.gov.local.tax.sales.locality_rates import (
    locality_sales_tax_rates,
)


class combined_sales_tax_rate(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    unit = "/1"
    label = "Combined state and local general sales tax rate"
    documentation = (
        "The combined state and local general sales tax rate where the household "
        "lives. In the states with locality rates, it is the official rate of the "
        "household's place, or of its county: the rate outside the county's places "
        "with their own rate when the household's place or census block is known, "
        "otherwise the county's population-weighted average. Elsewhere, or without "
        "a county FIPS code, it is a population-weighted state average derived from "
        "Tax Foundation data, a PolicyEngine default rather than an IRS value. "
        "Input the locality's rate to override it."
    )

    def formula(household, period, parameters):
        state_code = household("state_code", period)
        january = parameters(period.start).gov.local.tax.sales
        july = parameters(period.start.offset(6, "month")).gov.local.tax.sales
        # When the rate changed during the year, the line 3 instructions weight
        # each rate by the days it was in effect. The mean of the January 1 and
        # July 1 rates approximates that. The IRS headings average mid-year
        # changes the same way: the 2023 South Dakota heading, 4.35%, footnoted
        # "The rate decreased during 2023 so the given rate is an average for
        # the year", is the mean of the 4.5% and 4.2% state rates.
        state_average = (
            january.average_combined_rate[state_code]
            + july.average_combined_rate[state_code]
        ) / 2
        # Locality rates are keyed on FIPS codes, never on the county enum,
        # which falls back to the state's alphabetically first county.
        rates = locality_sales_tax_rates(period.start.year)
        county_fips = pd.Series(household("county_fips", period)).astype(str)
        county_fips = county_fips.where(county_fips == "", county_fips.str.zfill(5))
        place_fips = pd.Series(household("place_fips", period)).astype(str)
        place_fips = place_fips.where(place_fips == "", place_fips.str.zfill(5))
        block_geoid = pd.Series(household("block_geoid", period)).astype(str)
        # Use a county's rates only when it is in the household's state.
        in_state = (
            county_fips.map(rates.state_code).to_numpy()
            == household("state_code_str", period)
        )
        place_rate = (county_fips + place_fips).map(rates.place).to_numpy()
        # A known place without its own rate, or a known census block outside
        # every place (an empty place code), puts the household in the county's
        # balance. With only the county known, use the county's average.
        location_known = ((place_fips != "") | (block_geoid != "")).to_numpy()
        county_rate = where(
            location_known,
            county_fips.map(rates.balance).to_numpy(),
            county_fips.map(rates.county_average).to_numpy(),
        )
        has_place_rate = in_state & ~np.isnan(place_rate)
        has_county_rate = in_state & ~np.isnan(county_rate)
        return select(
            [has_place_rate, has_county_rate],
            [place_rate, county_rate],
            default=state_average,
        )
