from policyengine_us.model_api import *


class mt_capital_gain_credit(Variable):
    value_type = float
    entity = Person
    label = "Montana capital gain credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://rules.mt.gov/gateway/RuleNo.asp?RN=42%2E4%2E502",
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2022_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=43",  # Nonrefundable credits, line 1
    )
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.credits.capital_gain

        # The credit is 2% of the net capital gain on Form 2 line 7, which
        # takes the capital gain reported on the federal return, including
        # capital gain distributions reported on Form 1040 line 7 without
        # Schedule D.
        net_capital_gain = add(
            person, period, ["capital_gains", "non_sch_d_capital_gains"]
        )
        # The net capital gain variable is capped at 0
        return p.percentage * net_capital_gain
