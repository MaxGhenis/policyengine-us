from policyengine_us.model_api import *


class ca_investment_interest_deduction_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "California investment interest deduction subtraction"
    documentation = (
        "Form FTB 3526, line 10 when line 9 is more than line 8: the "
        "subtraction entered on Schedule CA (540) Part II line 9, column B."
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "https://www.ftb.ca.gov/forms/2025/2025-3526.pdf#page=2"

    def formula(tax_unit, period, parameters):
        california = tax_unit("ca_investment_interest_expense_deduction", period)
        federal = tax_unit("ca_federal_investment_interest_deduction", period)
        return max_(0, federal - california)
