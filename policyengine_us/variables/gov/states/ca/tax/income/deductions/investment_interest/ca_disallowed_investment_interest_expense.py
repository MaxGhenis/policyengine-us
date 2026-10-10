from policyengine_us.model_api import *


class ca_disallowed_investment_interest_expense(Variable):
    value_type = float
    entity = TaxUnit
    label = "California disallowed investment interest expense"
    documentation = (
        "Form FTB 3526, line 7: investment interest expense carried forward "
        "to the next year."
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "https://www.ftb.ca.gov/forms/2025/2025-3526.pdf"

    def formula(tax_unit, period, parameters):
        # Line 3 minus line 6, if zero or less, zero. Line 8 is the smaller
        # of the two, so line 7 is line 3 minus line 8.
        total = add(tax_unit, period, ["investment_interest_expense"]) + max_(
            0,
            tax_unit("ca_disallowed_investment_interest_expense_prior_year", period),
        )
        deduction = tax_unit("ca_investment_interest_expense_deduction", period)
        return max_(0, total - deduction)
