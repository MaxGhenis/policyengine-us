from policyengine_us.model_api import *


class ma_part_c_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA Part C AGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIX/Chapter62/Section2",  # (c)(2)(a), (e)
        "https://www.mass.gov/technical-information-release/tir-02-21-capital-gains-and-losses-massachusetts-tax-law-changes",  # II.B.1-2
    )
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        # Net long-term capital gains (long-term losses already netted).
        long_term_capital_gains = add(tax_unit, period, ["long_term_capital_gains"])
        short_term_capital_gains = add(tax_unit, period, ["short_term_capital_gains"])
        short_term_capital_loss = max_(0, -short_term_capital_gains)
        # Section 2(c)(2)(a): the short-term loss goes against Part A interest
        # and dividends first; only the remaining excess reduces Part C gains.
        # ma_part_c_gross_income nets the full short-term loss to match the
        # net capital gains that ma_part_b_gross_income backs out of
        # ma_gross_income, so Part C AGI starts from long-term gains instead.
        short_term_loss_against_interest_and_dividends = tax_unit(
            "ma_part_a_short_term_capital_loss_against_interest_and_dividends",
            period,
        )
        remaining_short_term_capital_loss = (
            short_term_capital_loss - short_term_loss_against_interest_and_dividends
        )
        return max_(0, long_term_capital_gains - remaining_short_term_capital_loss)
