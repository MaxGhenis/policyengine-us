from policyengine_us.model_api import *


class ira_contribution_limit(Variable):
    value_type = float
    entity = Person
    label = "IRA contribution limit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/219#b",
        "https://www.law.cornell.edu/uscode/text/26/219#c",
        "https://www.law.cornell.edu/uscode/text/26/408A#c_2",
    )

    def formula(person, period, parameters):
        annual_limit = person("ira_annual_limit", period)
        compensation = person("ira_compensation", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        joint = person.tax_unit("tax_unit_is_joint", period)

        # The higher earner's contributions only use their own compensation.
        # Compute that cap from requests to avoid a cycle through contributions.
        traditional_desired = person(
            "traditional_ira_contributions_desired", period
        ) * ~person("traditional_ira_age_barred", period)
        desired = traditional_desired + person("roth_ira_contributions_desired", period)
        own_contributions = min_(max_(0, desired), min_(annual_limit, compensation))
        spouse_compensation = (
            person.tax_unit.sum(compensation * head_or_spouse)
            - compensation * head_or_spouse
        )
        spouse_contributions = (
            person.tax_unit.sum(own_contributions * head_or_spouse)
            - own_contributions * head_or_spouse
        )
        # Section 219(c) applies only to the spouse with less compensation.
        spousal_eligible = joint & head_or_spouse & (compensation < spouse_compensation)
        available_compensation = compensation + where(
            spousal_eligible,
            max_(0, spouse_compensation - spouse_contributions),
            0,
        )
        return min_(annual_limit, available_compensation)
