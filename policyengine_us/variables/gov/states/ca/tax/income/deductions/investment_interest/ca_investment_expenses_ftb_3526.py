from policyengine_us.model_api import *


class ca_investment_expenses_ftb_3526(Variable):
    value_type = float
    entity = TaxUnit
    label = "California investment expenses for the investment interest limit"
    documentation = "Form FTB 3526, line 5."
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = (
        "https://www.ftb.ca.gov/forms/2025/2025-3526.pdf#page=2",
        "https://www.ftb.ca.gov/forms/2025/2025-540-ca.pdf#page=6",
    )

    def formula(tax_unit, period, parameters):
        # Investment expenses are miscellaneous itemized deductions on
        # Schedule CA (540) Part II line 21. Line 5 takes the smaller of
        # the investment expenses on line 21 or the line 25 total left after
        # the 2% federal AGI floor.
        investment_expenses = add(tax_unit, period, ["investment_expenses"])
        # Schedule CA (540) Part II lines 19 to 22.
        misc_expenses = investment_expenses + add(
            tax_unit,
            period,
            ["unreimbursed_business_employee_expenses", "tax_preparation_fees"],
        )
        # Lines 23 and 24: 2% of federal AGI, not less than zero.
        p = parameters(period).gov.states.ca.tax.income.deductions.itemized.misc
        floor = p.floor * tax_unit("positive_agi", period)
        # Line 25.
        misc_after_floor = max_(0, misc_expenses - floor)
        return min_(investment_expenses, misc_after_floor)
