from policyengine_us.model_api import *


class ny_claim_of_right_subtraction_bars_itemizing(Variable):
    value_type = bool
    entity = TaxUnit
    label = (
        "Subtracting a claim of right repayment rules out New York itemized deductions"
    )
    documentation = (
        "Whether the filer subtracts a claim of right repayment that the New "
        "York itemized deduction would include. No subtraction is allowed "
        "when the repayment is included in the itemized deduction (Tax Law "
        "612(c)(45)(B)), so this filer takes the standard deduction. When "
        "federal tax is computed under 26 U.S.C. 1341(a)(5) the repayment "
        "is not deducted, so itemizing other deductions stays open."
    )
    definition_period = YEAR
    reference = (
        "https://legislation.nysenate.gov/pdf/laws/TAX612#page=23",
        # 2025 Form IT-257 instructions: filers who itemize use Form IT-196;
        # filers who do not itemize may subtract
        "https://www.tax.ny.gov/pdf/2025/inc/it257i_2025.pdf",
    )
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        subtracts = tax_unit("ny_claim_of_right_subtraction", period) > 0
        credit_applies = tax_unit("claim_of_right_credit_applies", period)
        return subtracts & ~credit_applies
