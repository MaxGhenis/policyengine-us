from policyengine_us.model_api import *


class traditional_ira_contributions(Variable):
    value_type = float
    entity = Person
    label = "Traditional IRA contributions"
    unit = USD
    documentation = (
        "Traditional IRA contributions after applying the combined "
        "traditional and Roth IRA contribution limit. If desired IRA "
        "contributions exceed the limit, PolicyEngine preserves desired "
        "allocation shares by scaling traditional and Roth IRA contributions "
        "proportionally. Before 2020, no traditional contribution is allowed "
        "once the individual attains age 70½."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/219#b",
        # Former sections 219(d)(1) and 408(o)(2)(B), before 2020.
        "https://www.govinfo.gov/content/pkg/USCODE-2018-title26/html/USCODE-2018-title26-subtitleA-chap1-subchapB-partVII-sec219.htm",
        "https://www.govinfo.gov/content/pkg/USCODE-2018-title26/html/USCODE-2018-title26-subtitleA-chap1-subchapD-partI-subpartA-sec408.htm",
    )

    def formula(person, period, parameters):
        desired = person("traditional_ira_contributions_desired", period)
        scale = person("ira_contribution_scale", period)
        barred = person("traditional_ira_age_barred", period)
        return desired * scale * ~barred
