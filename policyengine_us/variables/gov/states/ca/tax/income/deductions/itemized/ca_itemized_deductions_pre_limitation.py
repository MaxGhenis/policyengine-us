from policyengine_us.model_api import *


class ca_itemized_deductions_pre_limitation(Variable):
    value_type = float
    entity = TaxUnit
    label = "California pre-limitation itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ftb.ca.gov/forms/2021/2021-540-ca-instructions.html"
        "https://www.ftb.ca.gov/forms/2022/2022-540-ca-instructions.html"
    )
    defined_for = StateCode.CA

    # Schedule CA (540) Part II line 9: federal investment interest
    # (column A, in itemized_deductions_less_salt) plus the form FTB 3526
    # line 10 addition (column C) less its subtraction (column B).
    adds = [
        "itemized_deductions_less_salt",
        "ca_investment_interest_deduction_addition",
        "real_estate_taxes",
    ]
    subtracts = ["ca_investment_interest_deduction_subtraction"]
