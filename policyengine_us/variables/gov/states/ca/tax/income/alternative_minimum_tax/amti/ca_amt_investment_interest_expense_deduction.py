from policyengine_us.model_api import *


class ca_amt_investment_interest_expense_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "California AMT investment interest expense deduction"
    documentation = (
        "Line 8 of the second form FTB 3526 that Schedule P (540) line 7 "
        "requires, figured with alternative minimum tax amounts."
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = (
        "https://www.ftb.ca.gov/forms/2025/2025-540-p-instructions.html",
        "https://www.ftb.ca.gov/forms/2025/2025-3526.pdf",
    )

    def formula(tax_unit, period, parameters):
        # Line 1 would add Schedule P line 4 home mortgage interest on debt
        # used for investment; PolicyEngine's deductible mortgage interest
        # is all acquisition interest, so there is none.
        current = add(tax_unit, period, ["investment_interest_expense"])
        # Line 2: the prior year's AMT disallowed investment interest.
        prior = max_(
            0,
            tax_unit(
                "ca_amt_disallowed_investment_interest_expense_prior_year", period
            ),
        )
        # Line 3.
        total = current + prior
        # Lines 4a to 4f are refigured with AMT adjustments and preferences.
        # PolicyEngine models none that change investment income.
        investment_income = tax_unit("ca_investment_income_ftb_3526", period)
        # Line 5: investment expenses on Schedule CA line 21 are
        # miscellaneous itemized deductions, which Schedule P line 5 adds
        # back, so none are allowed for AMT.
        # Line 6.
        net_investment_income = max_(0, investment_income)
        # Line 8.
        return min_(total, net_investment_income)
