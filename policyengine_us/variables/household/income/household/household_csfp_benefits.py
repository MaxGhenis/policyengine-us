from policyengine_us.model_api import *


class household_csfp_benefits(Variable):
    value_type = float
    entity = Household
    label = "Household CSFP benefits"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Annual Commodity Supplemental Food Program value included in "
        "household_benefits only when "
        "gov.simulation.include_csfp_benefits_in_net_income is enabled. The "
        "program is valued at per-slot cost and has no take-up input, so "
        "every computed-eligible person is valued at full cost against a "
        "caseload-assigned program."
    )

    def formula(household, period, parameters):
        p = parameters(period)
        if p.gov.simulation.include_csfp_benefits_in_net_income:
            return add(household, period, p.gov.household.household_csfp_benefits)
        else:
            return 0
