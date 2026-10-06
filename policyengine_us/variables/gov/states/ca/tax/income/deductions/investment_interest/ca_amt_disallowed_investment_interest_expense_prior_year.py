from policyengine_us.model_api import *


class ca_amt_disallowed_investment_interest_expense_prior_year(Variable):
    value_type = float
    entity = TaxUnit
    label = "California AMT disallowed investment interest expense from the prior year"
    documentation = (
        "Prior-year disallowed investment interest expense figured for the "
        "alternative minimum tax, entered on line 2 of the second form "
        "FTB 3526 that Schedule P (540) line 7 requires."
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "https://www.ftb.ca.gov/forms/2025/2025-540-p-instructions.html"
