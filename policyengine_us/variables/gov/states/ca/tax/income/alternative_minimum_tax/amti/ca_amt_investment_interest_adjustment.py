from policyengine_us.model_api import *


class ca_amt_investment_interest_adjustment(Variable):
    value_type = float
    entity = TaxUnit
    label = "California AMT investment interest expense adjustment"
    documentation = (
        "Schedule P (540) line 7: the regular tax form FTB 3526 line 8 less "
        "the AMT form FTB 3526 line 8. Negative when the AMT deduction is "
        "larger."
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "https://www.ftb.ca.gov/forms/2025/2025-540-p-instructions.html"

    def formula(tax_unit, period, parameters):
        regular = tax_unit("ca_investment_interest_expense_deduction", period)
        amt = tax_unit("ca_amt_investment_interest_expense_deduction", period)
        # No adjustment for a filer who did not itemize deductions.
        itemizes = tax_unit("ca_itemized_deductions", period) > tax_unit(
            "ca_standard_deduction", period
        )
        return where(itemizes, regular - amt, 0)
