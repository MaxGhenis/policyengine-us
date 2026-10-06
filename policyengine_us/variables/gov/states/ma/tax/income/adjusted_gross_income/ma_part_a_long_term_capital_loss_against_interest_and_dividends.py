from policyengine_us.model_api import *


class ma_part_a_long_term_capital_loss_against_interest_and_dividends(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA Part A long-term capital loss applied against interest and dividends"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIX/Chapter62/Section2",  # (c)(2)(b), (c)(4)
        "https://www.mass.gov/technical-information-release/tir-02-21-capital-gains-and-losses-massachusetts-tax-law-changes",  # II.C.4-5
    )
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        # Match ma_part_a_gross_income: interest is currently modeled in Part B.
        interest_and_dividends = max_(0, add(tax_unit, period, ["dividend_income"]))
        short_term_capital_gains = add(tax_unit, period, ["short_term_capital_gains"])
        long_term_capital_gains = add(tax_unit, period, ["long_term_capital_gains"])
        # Section 2(c)(2)(b): the net long-term loss offsets Part A short-term
        # gains first; only the excess can reach interest and dividends.
        remaining_long_term_capital_loss = max_(
            0, -long_term_capital_gains - max_(0, short_term_capital_gains)
        )
        short_term_loss_applied = tax_unit(
            "ma_part_a_short_term_capital_loss_against_interest_and_dividends",
            period,
        )
        p = parameters(period).gov.states.ma.tax.income.capital_gains
        # Section 2(c)(4): short-term and long-term losses share one cap.
        remaining_cap = (
            p.deductible_against_interest_dividends - short_term_loss_applied
        )
        remaining_interest_and_dividends = (
            interest_and_dividends - short_term_loss_applied
        )
        return max_(
            0,
            min_(
                remaining_long_term_capital_loss,
                min_(remaining_cap, remaining_interest_and_dividends),
            ),
        )
