from policyengine_us.model_api import *


class traditional_ira_age_barred(Variable):
    value_type = bool
    entity = Person
    label = "Barred from traditional IRA contributions by the former age 70½ limit"
    definition_period = YEAR
    reference = (
        # Section 219(d)(1) before its repeal for years after 2019.
        "https://www.govinfo.gov/content/pkg/USCODE-2018-title26/html/USCODE-2018-title26-subtitleA-chap1-subchapB-partVII-sec219.htm",
        # Section 408(o)(2)(B)(i): the nondeductible limit is the section 219
        # amount without 219(g) less the amount with 219(g).
        "https://www.govinfo.gov/content/pkg/USCODE-2018-title26/html/USCODE-2018-title26-subtitleA-chap1-subchapD-partI-subpartA-sec408.htm",
    )
    documentation = (
        "For taxable years before 2020, former section 219(d)(1) denied the "
        "deduction for an individual who attained age 70½ before the close of "
        "the taxable year. That bar also sets the section 408(o) nondeductible "
        "limit to zero, so no traditional IRA contribution was allowed. Roth "
        "IRA contributions disregard it under section 408A(c)(4). Age is "
        "compared with 70.5 directly, so an integer age of 70 is treated as "
        "not yet 70½."
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.ald.ira.age_limit
        return p.in_effect & (person("age", period) >= p.age)
