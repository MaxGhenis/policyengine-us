from policyengine_us.model_api import *


class mo_capital_gains_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Missouri capital gains subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revisor.mo.gov/main/OneSection.aspx?section=143.121&bid=57543",
        "https://dor.mo.gov/faq/taxation/individual/capital-gains-subtraction.html",  # MO form MO-A
        "https://dor.mo.gov/forms/MO-1040%20Instructions_2025.pdf#page=16",  # MO-A line 18
    )
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        # Form MO-A line 18 subtracts the capital gain reported on federal
        # Form 1040 line 7a, which includes capital gain distributions
        # reported without Schedule D.
        federally_reported_capital_gains = max_(
            0,
            tax_unit("net_capital_gains", period)
            + add(tax_unit, period, ["non_sch_d_capital_gains"]),
        )
        p = parameters(period).gov.states.mo.tax.income.subtractions.net_capital_gain
        return federally_reported_capital_gains * p.rate
