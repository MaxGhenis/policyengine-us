from policyengine_us.model_api import *


class wi_retirement_income_exclusion_claimed(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Wisconsin retirement income exclusion claimed"
    documentation = (
        "Whether the return claims the Schedule SB line 16 subtraction: the "
        "taxpayer elects it, the subtraction is in effect, and the head or "
        "spouse is at least 67 and has qualifying retirement income. A return "
        "that claims it may not claim any credit listed under Wis. Stat. 71.07."
    )
    definition_period = YEAR
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/05/6/b/54m",
        "https://www.revenue.wi.gov/TaxForms2025/2025-ScheduleSB-Inst.pdf#page=7",
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.wi.tax.income.subtractions.retirement_income.exclusion
        if not p.in_effect:
            return False

        elected = tax_unit("wi_retirement_income_exclusion_elected", period)
        # Wis. Stat. 71.05(6)(b)54m.b-d: only an individual aged 67 or older
        # can claim the subtraction, and only a claimant forfeits credits. An
        # election with no line 16 amount therefore claims nothing.
        exclusion = tax_unit("wi_retirement_income_exclusion_amount", period)
        return elected & (exclusion > 0)
