from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_couple_total,
    _ssi_spouse_index,
)


class ms_wd_resource_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Mississippi Working Disabled resource eligible"
    definition_period = MONTH
    documentation = (
        "Uses modeled SSI countable resources with Mississippi's higher WD "
        "individual and couple limits. Mississippi-specific second-vehicle, "
        "personal-property, life-insurance, and income-producing property "
        "exemptions are not separately modeled."
    )
    reference = (
        "https://medicaid.ms.gov/wp-content/uploads/2025/07/Chapter-400-ABD-and-MAGI-Eligibility-Criteria-and-Budgeting.-Revised-July-2025v2.pdf#page=31",
        "https://medicaid.ms.gov/medicaid-coverage/who-qualifies-for-coverage/working-disabled/",
    )
    defined_for = StateCode.MS

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ms.dom.wd.eligibility.resources.limit
        year = period.this_year
        countable_resources = _ssi_couple_total(
            person, year, person("ssi_countable_resources", year)
        )
        resource_limit = where(
            _ssi_spouse_index(person, year) >= 0,
            p.couple,
            p.individual,
        )
        return countable_resources <= resource_limit
