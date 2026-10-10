from policyengine_us.model_api import *


class ca_itemized_deductions_pre_limitation(Variable):
    value_type = float
    entity = TaxUnit
    label = "California pre-limitation itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ftb.ca.gov/forms/2021/2021-540-ca-instructions.html",
        "https://www.ftb.ca.gov/forms/2022/2022-540-ca-instructions.html",
        # 2024 Schedule CA (540) instructions, line 15
        "https://www.ftb.ca.gov/forms/2024/2024-540-booklet.pdf#page=66",
    )
    defined_for = StateCode.CA

    # Schedule CA line 15 replaces the federal casualty loss, which is limited
    # to declared disasters from 2018, with California's own.
    adds = [
        "itemized_deductions_less_salt",
        "ca_casualty_loss_deduction",
        "ca_investment_interest_expense_deduction",
        "real_estate_taxes",
    ]
    subtracts = ["casualty_loss_deduction", "investment_interest_expense"]
