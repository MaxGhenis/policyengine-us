from policyengine_us.model_api import *


class ira_active_participant(Variable):
    value_type = bool
    entity = Person
    label = "Active participant in a retirement plan for the IRA deduction"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/219#g_5"
    documentation = (
        "Coverage by a workplace retirement plan for section 219(g). The default "
        "infers participation from actual 401(k) or 403(b) contributions with "
        "earnings, or self-employed pension contributions. Set this input for "
        "employer-only contributions, defined-benefit coverage, or other coverage "
        "not represented by the modeled contributions."
    )

    def formula(person, period, parameters):
        elective_contributions = add(
            person,
            period,
            [
                "traditional_401k_contributions",
                "roth_401k_contributions",
                "traditional_403b_contributions",
                "roth_403b_contributions",
            ],
        )
        has_earnings = (person("employment_income", period) > 0) | (
            person("total_self_employment_income", period) > 0
        )
        self_employed_contributions = person(
            "self_employed_pension_contributions", period
        )
        return ((elective_contributions > 0) & has_earnings) | (
            self_employed_contributions > 0
        )
