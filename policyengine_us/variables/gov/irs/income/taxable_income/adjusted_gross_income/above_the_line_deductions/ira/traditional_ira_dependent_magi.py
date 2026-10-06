from policyengine_us.model_api import *


class traditional_ira_dependent_magi(Variable):
    value_type = float
    entity = Person
    label = "Traditional IRA deduction MAGI on a dependent's own return"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/219#g_3_A"
    documentation = (
        "A dependent's IRA deduction is determined on their own return. This "
        "approximates that return's modified AGI with the dependent's own "
        "positive gross income other than Social Security, without their own "
        "adjustments or taxable Social Security benefits."
    )
    defined_for = "is_tax_unit_dependent"

    def formula(person, period, parameters):
        return person("traditional_ira_deduction_gross_income", period)
