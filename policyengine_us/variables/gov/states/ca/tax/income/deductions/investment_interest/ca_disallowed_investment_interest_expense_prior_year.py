from policyengine_us.model_api import *


class ca_disallowed_investment_interest_expense_prior_year(Variable):
    value_type = float
    entity = TaxUnit
    label = "California disallowed investment interest expense from the prior year"
    documentation = (
        "Disallowed investment interest expense carried forward from the "
        "prior year's form FTB 3526, line 7 (FTB 3526 line 2). Enter zero "
        "or more."
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "https://www.ftb.ca.gov/forms/2025/2025-3526.pdf#page=1"
