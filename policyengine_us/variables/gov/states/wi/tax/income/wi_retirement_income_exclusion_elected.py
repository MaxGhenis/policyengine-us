from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    ordered_capped_state_non_refundable_credits,
)


class wi_retirement_income_exclusion_elected(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Wisconsin retirement income exclusion elected"
    documentation = (
        "Whether the taxpayer elects the Schedule SB line 16 subtraction. "
        "Unless supplied as an input, elect only when it reduces net Wisconsin "
        "income tax after forfeiting all credits; keep credits on a tie. "
        "wi_retirement_income_exclusion_claimed determines whether the "
        "election takes effect."
    )
    definition_period = YEAR
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/05/6/b/54m",
        "https://www.revenue.wi.gov/TaxForms2025/2025-ScheduleSB-Inst.pdf#page=7",
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.wi.tax.income
        if not p.subtractions.retirement_income.exclusion.in_effect:
            return False

        exclusion = tax_unit("wi_retirement_income_exclusion_amount", period)
        exclusion_tax = tax_unit("wi_retirement_income_exclusion_tax", period)
        # Net tax on the return without line 16, which keeps every credit.
        # The credit variables are zero once line 16 is claimed, so read
        # their potential amounts; the claimed amounts would be circular.
        before_credits = tax_unit("wi_income_tax_before_credits", period)
        non_refundable = ordered_capped_state_non_refundable_credits(
            tax_unit,
            period,
            [f"{credit}_potential" for credit in list(p.credits.non_refundable)],
            "wi_income_tax_before_credits",
        )
        refundable = add(
            tax_unit,
            period,
            [f"{credit}_potential" for credit in list(p.credits.refundable)],
        )
        standard_tax = max_(0, before_credits - non_refundable) - refundable
        return (exclusion > 0) & (exclusion_tax < standard_tax)
