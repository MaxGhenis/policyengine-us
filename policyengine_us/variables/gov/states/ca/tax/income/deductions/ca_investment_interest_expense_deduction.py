from policyengine_us.model_api import *


class ca_investment_interest_expense_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "California investment interest expense deduction"
    unit = USD
    reference = (
        "https://www.ftb.ca.gov/forms/2025/2025-3526.pdf",
        "https://www.ftb.ca.gov/forms/2025/2025-3526.pdf#page=2",
        "https://www.ftb.ca.gov/forms/2021/2021-3526.pdf#page=2",
    )
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        # FTB 3526 line 1.
        investment_interest_expense = add(
            tax_unit, period, ["investment_interest_expense"]
        )
        # FTB 3526 line 5. The instructions include the smaller of the
        # investment expenses on Schedule CA (540), Part II, line 21 or the
        # line 25 total, because the 2% floor on line 24 may reduce them.
        investment_expenses = add(tax_unit, period, ["investment_expenses"])
        allowed_investment_expenses = min_(
            investment_expenses, tax_unit("ca_misc_deduction", period)
        )
        # Simplified FTB 3526 line 6. Carryforwards and investment income
        # elections are not separately modeled here.
        net_investment_income = max_(
            0, investment_interest_expense - allowed_investment_expenses
        )
        # FTB 3526 line 8.
        return min_(investment_interest_expense, net_investment_income)
