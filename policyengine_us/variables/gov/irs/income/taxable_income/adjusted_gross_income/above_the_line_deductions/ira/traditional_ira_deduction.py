from policyengine_us.model_api import *


class traditional_ira_deduction(Variable):
    value_type = float
    entity = Person
    label = "Traditional IRA deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/219"
    documentation = (
        "The deductible traditional IRA contribution on this tax unit's return. "
        "A dependent's contribution is retained as saving but is not deductible "
        "by the taxpayer claiming the dependent."
    )

    def formula(person, period, parameters):
        filer = person("is_tax_unit_head", period) | (
            person("is_tax_unit_spouse", period)
            & person.tax_unit("tax_unit_is_joint", period)
        )
        return filer * person("traditional_ira_deductible_contributions", period)
