from policyengine_us.model_api import *


class ny_claim_of_right_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York claim of right repayment subtraction"
    unit = USD
    documentation = (
        "From 2021, New York subtracts from federal adjusted gross income "
        "the amount of an item that was included in New York adjusted gross "
        "income for an earlier year under a claim of right and repaid this "
        "year (Form IT-225 modification S-141). It has no $3,000 threshold. "
        "It is not allowed when the repayment is included in the New York "
        "itemized deduction or is the basis for a section 662 credit."
    )
    definition_period = YEAR
    reference = (
        "https://legislation.nysenate.gov/pdf/laws/TAX612#page=23",
        # 2025 Form IT-225 instructions, S-141
        "https://www.tax.ny.gov/pdf/2025/inc/it225i_2025.pdf#page=19",
        # 2021 Form IT-225 instructions, S-141
        "https://www.tax.ny.gov/pdf/2021/inc/it225i_2021.pdf#page=14",
    )
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ny.tax.income.agi.subtractions
        applies = tax_unit("ny_claim_of_right_subtraction_applies", period)
        repayment = tax_unit("ny_claim_of_right_repayment", period)
        return where(applies, repayment, 0) * p.claim_of_right.in_effect
