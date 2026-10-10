from policyengine_us.model_api import *


class ny_misc_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY miscellaneous deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/615",
        "https://www.tax.ny.gov/pit/file/itemized-deductions.htm",
        # 2025 Form IT-196 instructions, line 24
        "https://www.tax.ny.gov/pdf/2025/inc/it196i_2025.pdf#page=16",
    )
    defined_for = StateCode.NY
    documentation = """
    NY Tax Law § 615 requires itemized deductions to be computed using
    pre-TCJA federal rules. Unlike federal rules post-2017, NY still
    allows miscellaneous itemized deductions subject to the 2% AGI floor.
    These include unreimbursed employee expenses and tax preparation fees.
    """

    def formula(tax_unit, period, parameters):
        # NY uses pre-TCJA rules: misc deductions are still allowed
        # with the 2% AGI floor (not suspended like federal post-2017)
        p = parameters(period).gov.irs.deductions.itemized.misc
        # Form IT-196 line 24 includes a claim of right repayment of $3,000
        # or less; a larger one is deducted on line 34, outside the floor.
        repayment = tax_unit("tax_unit_claim_of_right_repayment", period)
        over_threshold = tax_unit("claim_of_right_section_1341_eligible", period)
        small_repayment = where(over_threshold, 0, repayment)
        expenses = tax_unit("total_misc_deductions", period) + small_repayment
        misc_floor = p.floor * tax_unit("positive_agi", period)
        return max_(0, expenses - misc_floor)
