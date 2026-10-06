from policyengine_us.model_api import *


class ca_investment_income_ftb_3526(Variable):
    value_type = float
    entity = TaxUnit
    label = "California investment income for the investment interest limit"
    documentation = "Form FTB 3526, line 4f."
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "https://www.ftb.ca.gov/forms/2025/2025-3526.pdf"

    def formula(tax_unit, period, parameters):
        # Line 4a: gross income from property held for investment, excluding
        # net gain from dispositions. The instructions list interest,
        # dividends, annuities and royalties. FTB 3526 has no qualified
        # dividend line (federal Form 4952 line 4b), so all ordinary
        # dividends count. PolicyEngine has no separate investment annuity
        # or royalty income input.
        gross_income = add(
            tax_unit,
            period,
            ["taxable_interest_income", "ordinary_dividend_income"],
        )
        # Capital gain distributions are long-term gains (line 4b and line
        # 4c instructions), whether reported on Schedule D or not.
        long_term = add(
            tax_unit, period, ["long_term_capital_gains", "non_sch_d_capital_gains"]
        )
        short_term = add(tax_unit, period, ["short_term_capital_gains"])
        # Line 4b: net gain from the disposition of property held for
        # investment (total gains over total losses).
        net_gain = max_(0, long_term + short_term)
        # Line 4c: net capital gain from those dispositions (net long-term
        # capital gain over net short-term capital loss).
        net_capital_gain = max_(0, long_term - max_(0, -short_term))
        # Line 4d: subtract line 4c from line 4b; if zero or less, zero.
        net_gain_less_net_capital_gain = max_(0, net_gain - net_capital_gain)
        # Line 4e: the part of line 4c elected into investment income, no
        # more than line 4b. California allows a separate election or the
        # federal one; PolicyEngine applies the federal Form 4952 election.
        federal_election = add(
            tax_unit, period, ["investment_income_elected_form_4952"]
        )
        elected = min_(max_(0, federal_election), min_(net_capital_gain, net_gain))
        # Line 4f: add lines 4a, 4d and 4e.
        return gross_income + net_gain_less_net_capital_gain + elected
