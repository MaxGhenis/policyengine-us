from policyengine_us.model_api import *


class combined_sales_tax_rate(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    unit = "/1"
    label = "Combined state and local general sales tax rate"
    documentation = (
        "The combined state and local general sales tax rate where the household "
        "lives. Defaults to a population-weighted state average derived from Tax "
        "Foundation data, a PolicyEngine default rather than an IRS value; input "
        "the locality's rate to override it."
    )
    reference = (
        # Worksheet line 3 instructions: rates that changed during the year.
        "https://www.irs.gov/pub/irs-prior/i1040sca--2022.pdf#page=6",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2023.pdf#page=6",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2024.pdf#page=5",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2025.pdf#page=5",
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
        return (
            january.average_combined_rate[state_code]
            + july.average_combined_rate[state_code]
        ) / 2
