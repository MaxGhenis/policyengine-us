from policyengine_us.model_api import *


class ca_federal_investment_interest_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal investment interest deduction for California form FTB 3526"
    documentation = (
        "Form FTB 3526, line 9: the federal Form 4952, line 8 deduction, "
        "which federal Schedule A line 9 and Schedule CA (540) Part II "
        "line 9 column A carry."
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "https://www.ftb.ca.gov/forms/2025/2025-3526.pdf"

    def formula(tax_unit, period, parameters):
        # PolicyEngine does not compute federal Form 4952. Its federal
        # interest_deduction includes investment_interest_expense in full
        # (through non_mortgage_interest and deductible_interest_expense),
        # so that is the federal amount in Schedule CA column A. Reading the
        # same amount here makes column A less column B plus column C equal
        # FTB 3526 line 8.
        return add(tax_unit, period, ["investment_interest_expense"])
