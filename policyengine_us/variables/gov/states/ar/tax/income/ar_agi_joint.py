from policyengine_us.model_api import *


class ar_agi_joint(Variable):
    value_type = float
    entity = Person
    label = "Arkansas adjusted gross income for each individual"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dfa.arkansas.gov/wp-content/uploads/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=14",
        # Income: "Write the primary's income in column A and the spouse's
        # income in column B. For all other filing statuses, write all income
        # in column A only."
        "https://www.dfa.arkansas.gov/wp-content/uploads/2025_AR1000F_and_AR1000NR_Instructions.pdf#page=12",
        # 26 CAR § 100-143(a)(1), implementing Ark. Code § 26-51-801(a):
        # "Every person receiving gross income from Arkansas sources shall
        # file an Arkansas individual income tax return".
        "https://codeofarrules.arkansas.gov/Rules/Rule?chapterID=33&levelType=section&partID=941&sectionID=40250&subChapterID=261&subPartID=6195&titleID=26",
    )
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        gross_income = person("ar_gross_income_joint", period)
        income_exemptions = person("ar_exemptions", period)
        net_income = max_(gross_income - income_exemptions, 0)
        # Only the head's and spouse's income goes on their return (Form
        # AR1000F columns A and B); a dependent with income files their own
        # return under Ark. Code § 26-51-801(a).
        is_dependent = person("is_tax_unit_dependent", period)
        return ~is_dependent * net_income
