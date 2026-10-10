from policyengine_us.model_api import *


class ca_investment_interest_deduction_addition(Variable):
    value_type = float
    entity = TaxUnit
    label = "California investment interest deduction addition"
    documentation = (
        "Form FTB 3526, line 10 when line 8 is more than line 9: the "
        "addition entered on Schedule CA (540) Part II line 9, column C."
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "https://www.ftb.ca.gov/forms/2025/2025-3526.pdf#page=2"

    def formula(tax_unit, period, parameters):
        california = tax_unit("ca_investment_interest_expense_deduction", period)
        federal = tax_unit("ca_federal_investment_interest_deduction", period)
        return max_(0, california - federal)
