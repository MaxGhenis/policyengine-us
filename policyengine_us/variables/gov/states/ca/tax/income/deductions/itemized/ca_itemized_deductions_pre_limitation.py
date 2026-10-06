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
        "https://www.ftb.ca.gov/forms/2025/2025-540-ca.pdf#page=5",
        "https://www.ftb.ca.gov/forms/2025/2025-540-ca-instructions.html",
    )
    defined_for = StateCode.CA

    # California lists its own sources rather than inheriting the federal
    # itemized deduction list, whose charitable, non-itemizer charitable
    # and miscellaneous items follow federal rules California does not adopt.
    adds = "gov.states.ca.tax.income.deductions.itemized.sources"
    # interest_deduction includes federal investment interest, which
    # ca_investment_interest_expense_deduction replaces.
    subtracts = ["investment_interest_expense"]
