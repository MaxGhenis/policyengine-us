from policyengine_us.model_api import *


class ny_itemized_deductions_max(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY itemized deductions before reduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/615",
        "https://www.tax.ny.gov/pit/file/itemized-deductions.htm",
        # 2025 Form IT-196 instructions, line 34
        "https://www.tax.ny.gov/pdf/2025/inc/it196i_2025.pdf#page=17",
    )
    defined_for = StateCode.NY
    documentation = """
    NY Tax Law § 615 requires itemized deductions to be computed using
    federal rules as they existed immediately prior to the enactment of
    Public Law 115-97 (TCJA). This means:
    - No SALT cap ($10,000 limit does not apply)
    - State/local income taxes are NOT deductible (only sales + property)
    - Miscellaneous deductions still allowed with 2% AGI floor
    - Casualty losses not limited to federally declared disasters
    - NY-specific college tuition deduction addition per § 615(d)
    """
    adds = [
        # Federal deductions that don't differ from pre-TCJA
        "charitable_deduction",
        "interest_deduction",
        "medical_expense_deduction",
        # NY-specific pre-TCJA versions
        "ny_salt_deduction",
        "ny_misc_deduction",
        "ny_casualty_loss_deduction",
        # Form IT-196 line 34: a repayment over $3,000 that federal law
        # deducts under 26 U.S.C. 1341(a)(4), outside the 2% floor
        "claim_of_right_deduction",
        # NY-specific addition per Tax Law § 615(d)
        "ny_college_tuition_deduction",
    ]
