from policyengine_us.model_api import *


class ira_contribution_scale(Variable):
    value_type = float
    entity = Person
    label = "IRA contribution scale"
    unit = "/1"
    documentation = (
        "Scale factor applied to desired traditional and Roth IRA "
        "contributions when they exceed the combined IRA contribution limit. "
        "This preserves desired allocation shares rather than prioritizing "
        "either IRA type. Traditional requests are disregarded while the "
        "former age 70½ bar applies."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/219#b",
        "https://www.law.cornell.edu/uscode/text/26/408A#c_2",
    )

    def formula(person, period, parameters):
        # Before 2020, no traditional contribution is allowed after age 70½,
        # so only Roth requests share the limit.
        traditional_desired = person(
            "traditional_ira_contributions_desired", period
        ) * ~person("traditional_ira_age_barred", period)
        total_desired = traditional_desired + person(
            "roth_ira_contributions_desired", period
        )
        return min_(
            person("ira_contribution_limit", period)
            / where(total_desired > 0, total_desired, 1),
            1,
        )
