from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_both_spouses,
)
from policyengine_us.variables.gov.states.hi.dhs.oss.hi_oss_living_arrangement import (
    HIOSSLivingArrangement,
)


class hi_oss_couple_rate_applies(Variable):
    value_type = bool
    entity = Person
    label = "Whether the Hawaii OSS couple rate applies"
    definition_period = MONTH
    defined_for = StateCode.HI
    reference = (
        "https://secure.ssa.gov/apps10/poms.nsf/lnx/0501415200SF",
        "https://secure.ssa.gov/POMS.NSF/lnx/0501415057",
    )

    def formula(person, period, parameters):
        year = period.this_year
        joint_claim = person("ssi_claim_is_joint", year)
        is_eligible = person("is_ssi_eligible", period)
        both_ssi_eligible = _ssi_both_spouses(person, year, is_eligible)
        la = person("hi_oss_living_arrangement", period)
        LA = HIOSSLivingArrangement
        both_same_facility = (
            _ssi_both_spouses(person, year, la == LA.COMMUNITY_CARE)
            | _ssi_both_spouses(person, year, la == LA.DOMICILIARY_CARE_I)
            | _ssi_both_spouses(person, year, la == LA.DOMICILIARY_CARE_II)
            | _ssi_both_spouses(person, year, la == LA.MEDICAID_INSTITUTION)
        )
        return joint_claim & both_ssi_eligible & both_same_facility
