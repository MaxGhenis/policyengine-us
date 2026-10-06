from policyengine_us.model_api import *


class ma_part_a_short_term_capital_loss_against_interest_and_dividends(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA Part A short-term capital loss applied against interest and dividends"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIX/Chapter62/Section2",  # (c)(2)(a), (c)(4)
        "https://www.mass.gov/technical-information-release/tir-02-21-capital-gains-and-losses-massachusetts-tax-law-changes",  # II.C.3
    )
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        # Match ma_part_a_gross_income: interest is currently modeled in Part B.
        interest_and_dividends = max_(0, add(tax_unit, period, ["dividend_income"]))
        short_term_capital_gains = add(tax_unit, period, ["short_term_capital_gains"])
        short_term_capital_loss = max_(0, -short_term_capital_gains)
        p = parameters(period).gov.states.ma.tax.income.capital_gains
        # Section 2(c)(2)(a): the net short-term loss is applied against
        # Part A interest and dividends first, up to the section 2(c)(4) cap.
        # Only the remaining excess offsets Part C gains (see ma_part_c_agi).
        return min_(
            short_term_capital_loss,
            min_(p.deductible_against_interest_dividends, interest_and_dividends),
        )
