from policyengine_us.model_api import *


class de_pre_exclusions_agi(Variable):
    value_type = float
    entity = Person
    label = "Delaware individual adjusted gross income before exclusions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE
    reference = "https://delcode.delaware.gov/title30/c011/sc02/index.html"

    def formula(person, period, parameters):
        agi = person("adjusted_gross_income_person", period)
        # Each person's net income is summed into the filer's (de_agi_joint,
        # de_agi_indiv). Delaware modifies the individual's "federal adjusted
        # gross income" (30 Del. C. 1106(a)), and a tax unit dependent's own
        # income and additions are on their own federal return, so they stay
        # off the filer's, as their subtractions do (de_subtractions).
        additions = person_non_dep_add(person, period, ["de_additions"])
        subtractions = person("de_subtractions", period)
        return agi + additions - subtractions
