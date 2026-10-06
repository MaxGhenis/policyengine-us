from policyengine_us.model_api import *


class ut_claims_retirement_credit(Variable):
    value_type = bool
    entity = TaxUnit
    label = "claims the Utah retirement credit"
    unit = USD
    documentation = (
        "Utah filers who claim the retirement credit (code 18) cannot claim the "
        "Social Security benefits credit (code AH) or the military retirement "
        "credit (code AJ); the latter two can be claimed together. We assume "
        "filers claim the retirement credit only when it is positive and at "
        "least as large as the other two combined."
    )
    reference = (
        "https://incometax.utah.gov/credits/retirement-credit",
        # 2025 TC-40 instructions, codes 18 and AJ.
        "https://tax.utah.gov/forms/current/tc-40inst.pdf#page=23",
    )
    definition_period = YEAR
    defined_for = StateCode.UT

    def formula(tax_unit, period, parameters):
        max_retirement_credit = tax_unit("ut_retirement_credit_max", period)
        max_ss_benefits_credit = tax_unit("ut_ss_benefits_credit_max", period)
        p = parameters(period).gov.states.ut.tax.income.credits.military_retirement
        max_military_credit = (
            add(tax_unit, period, ["military_retirement_pay"]) * p.rate
        )
        alternative = max_ss_benefits_credit + max_military_credit
        return (max_retirement_credit > 0) & (max_retirement_credit >= alternative)
