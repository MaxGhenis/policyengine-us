from policyengine_us.model_api import *


class sc_net_capital_gain_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina net capital gain deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.SC
    reference = (
        "https://dor.sc.gov/forms-site/Forms/IITPacket_2021.pdf#page=15",
        "https://dor.sc.gov/sites/dor/files/forms/SC1040Instr_2025.pdf#page=8",
        "https://www.scstatehouse.gov/code/t12c006.php",
        # South Carolina Code of Laws Section 12-6-1150 (A)
    )

    def formula(tax_unit, period, parameters):
        # S.C. Code 12-6-1150(B)(2) defines net capital gain by IRC 1222 and
        # related sections, and 26 U.S.C. 852(b)(3)(B) treats capital gain
        # distributions as gain on assets held more than one year; the
        # SC1040 instructions for line i say capital gain distributions
        # qualify when that holding period is met. Include those reported
        # on Form 1040 without Schedule D.
        ltcg = add(
            tax_unit,
            period,
            ["long_term_capital_gains", "non_sch_d_capital_gains"],
        )
        stcg = add(tax_unit, period, ["short_term_capital_gains"])
        capped_stcg = min_(0, stcg)
        base = max_(0, ltcg + capped_stcg)
        p = parameters(period).gov.states.sc.tax.income.deductions.net_capital_gain
        return base * p.rate
