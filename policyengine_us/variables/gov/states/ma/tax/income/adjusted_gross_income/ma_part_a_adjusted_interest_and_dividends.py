from policyengine_us.model_api import *


class ma_part_a_adjusted_interest_and_dividends(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA Part A interest and dividends after capital losses"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIX/Chapter62/Section2",  # (c)(2), (4)
    )
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        # Match ma_part_a_gross_income: interest is currently modeled in Part B.
        interest_and_dividends = add(tax_unit, period, ["dividend_income"])
        loss_deduction = add(
            tax_unit,
            period,
            [
                "ma_part_a_short_term_capital_loss_against_interest_and_dividends",
                "ma_part_a_long_term_capital_loss_against_interest_and_dividends",
            ],
        )
        return max_(0, interest_and_dividends - loss_deduction)
