from policyengine_us.model_api import *


class ar_taxable_capital_gains_joint(Variable):
    value_type = float
    entity = Person
    label = "Arkansas taxable capital gains when married filing jointly"
    unit = USD
    reference = (
        "https://codes.findlaw.com/ar/title-26-taxation/ar-code-sect-26-51-815.html",
        "https://www.taxformfinder.org/forms/2023/2023-arkansas-form-ar1000d.pdf#page=1",
        "https://www.dfa.arkansas.gov/wp-content/uploads/2025_AR1000D_CapitalGains.pdf#page=1",
    )
    definition_period = YEAR
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        # Line 1-3 - long term capital gain or loss. Line 1 takes federal
        # Schedule D line 15, or Form 1040 line 7 when Schedule D is not
        # required, so capital gain distributions reported without
        # Schedule D count as long-term gain (26 U.S.C. 852(b)(3)(B)).
        lt_capital_gains = add(
            person,
            period,
            ["long_term_capital_gains", "non_sch_d_capital_gains"],
        )
        # Line 4-6 - short term capital loss
        st_capital_gains = person("short_term_capital_gains", period)
        st_capital_loss = max_(-st_capital_gains, 0)
        # Line 7a - Net capital gain or loss
        net_capital_gain = lt_capital_gains - st_capital_loss
        # Line 7b - capped net capital gain
        p = parameters(period).gov.states.ar.tax.income.gross_income.capital_gains
        capped_net_cap_gain = min_(net_capital_gain, p.exempt.cap)
        # Line 8 - Tax rate applied to capital gain
        # 50% exempt if a gain, otherwise entire loss.
        exempt_fraction = where(capped_net_cap_gain > 0, p.exempt.rate, 0)
        taxable_amount = capped_net_cap_gain * (1 - exempt_fraction)
        # Lines 9-11: Arkansas short term capital gain if any.
        stcg_if_any = max_(st_capital_gains, 0)
        # Line 12: Total taxable gain or loss. Loss is capped.
        total_taxable_cap_gain_or_loss = taxable_amount + stcg_if_any
        filing_status = person.tax_unit("filing_status", period)
        loss_cap = p.loss_cap[filing_status]
        return max_(-loss_cap, total_taxable_cap_gain_or_loss)
