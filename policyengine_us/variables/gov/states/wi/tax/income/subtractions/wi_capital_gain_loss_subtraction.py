from policyengine_us.model_api import *


class wi_capital_gain_loss_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin capital gain/loss subtraction from federal AGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/05/6/b/9",
        "https://www.revenue.wi.gov/TaxForms2021/2021-ScheduleWDf.pdf#page=2",
        "https://www.revenue.wi.gov/TaxForms2022/2022-ScheduleWDf.pdf#page=2",
        "https://www.revenue.wi.gov/TaxForms2025/2025-ScheduleWDf.pdf#page=1",
        "https://www.revenue.wi.gov/TaxForms2025/2025-ScheduleSB-Inst.pdf#page=2",
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        # calculate Schedule WD, Line 8
        stcg_net = add(tax_unit, period, ["short_term_capital_gains"])
        # calculate Schedule WD, Line 17, which includes capital gain
        # distributions (2025 Schedule WD, Line 14). Distributions are gain
        # on assets held more than one year (26 U.S.C. 852(b)(3)(B)), so
        # Wis. Stat. 71.05(6)(b)9 covers them. Those reported on federal
        # Schedule D are already in long_term_capital_gains; those reported
        # directly on Form 1040 without Schedule D are added here, which
        # yields the Schedule SB, Line 5 exception (30% of the distribution)
        # when they are the only capital gain.
        ltcg_net = add(
            tax_unit,
            period,
            ["long_term_capital_gains", "non_sch_d_capital_gains"],
        )
        # calculate Schedule WD, Line 18
        totcg = max_(0, stcg_net + ltcg_net)
        # calculate Schedule WD, Line 20, the capital gain reduction
        p = parameters(period).gov.states.wi.tax.income.subtractions
        fraction = p.capital_gain.fraction
        cg_reduction = min_(totcg, max_(0, ltcg_net)) * fraction
        # calculate Schedule WD, Line 27, the WI reduced capital gain
        wi_cg = totcg - cg_reduction
        # calculate Schedule WD, Line 29a
        us_cg = totcg
        # return Schedule SB capital gain subtraction (WD Line 29d)
        return max_(0, us_cg - wi_cg)
