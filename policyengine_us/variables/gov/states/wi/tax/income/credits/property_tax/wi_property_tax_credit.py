from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class wi_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin property tax credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdf#page=2"
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1-Inst.pdf#page=17"
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdf#page=2"
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1-Inst.pdf#page=17"
        "https://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2023/0002_individual_income_tax_informational_paper_2.pdf#page=19"
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.wi.tax.income.credits.non_refundable
        applied = applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "wi_income_tax_before_credits",
            "wi_property_tax_credit",
            "wi_property_tax_credit_potential",
        )
        # Wis. Stat. 71.05(6)(b)54m.d bars s. 71.07 credits on a return that
        # claims the Schedule SB line 16 retirement income subtraction.
        claimed = tax_unit("wi_retirement_income_exclusion_claimed", period)
        return where(claimed, 0, applied)
