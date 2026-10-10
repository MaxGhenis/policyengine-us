from policyengine_us.model_api import *


class ca_investment_interest_expense_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "California investment interest expense deduction"
    documentation = "Form FTB 3526, line 8."
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "https://www.ftb.ca.gov/forms/2025/2025-3526.pdf"

    def formula(tax_unit, period, parameters):
        # Line 1: investment interest expense paid or accrued.
        current = add(tax_unit, period, ["investment_interest_expense"])
        # Line 2: disallowed investment interest expense from the prior
        # year's line 7; if zero or less, zero.
        prior = max_(
            0,
            tax_unit("ca_disallowed_investment_interest_expense_prior_year", period),
        )
        # Line 3: add lines 1 and 2.
        total = current + prior
        # Line 6: subtract line 5 from line 4f. A negative result allows no
        # deduction under IRC 163(d)(1), which California follows.
        net_investment_income = max_(
            0,
            tax_unit("ca_investment_income_ftb_3526", period)
            - tax_unit("ca_investment_expenses_ftb_3526", period),
        )
        # Line 8: the smaller of line 3 or line 6.
        return min_(total, net_investment_income)
