from policyengine_us.model_api import *


class traditional_ira_deductible_contributions(Variable):
    value_type = float
    entity = Person
    label = "Deductible traditional IRA contributions on the contributor's own return"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/219"
    documentation = (
        "Traditional IRA contributions up to the section 219 deductible limit, "
        "including a dependent's contributions deductible on the dependent's own "
        "return. traditional_ira_deduction keeps only the amounts on this tax "
        "unit's federal return. States that fold dependents' income into the "
        "head's state return use this amount instead."
    )

    def formula(person, period, parameters):
        contribution = person("traditional_ira_contributions", period)
        limit = person("traditional_ira_deductible_limit", period)
        return min_(contribution, limit)
