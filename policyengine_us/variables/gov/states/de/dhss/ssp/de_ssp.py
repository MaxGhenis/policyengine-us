from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi._ssi_state_supplement import (
    ssi_deemed_state_supplement,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_both_spouses,
    _ssi_couple_total,
)


class de_ssp(Variable):
    value_type = float
    entity = Person
    label = "Delaware State Supplementary Payment"
    unit = USD
    definition_period = MONTH
    defined_for = "de_ssp_eligible"
    reference = (
        "https://secure.ssa.gov/apps10/poms.nsf/lnx/0501415058",
        "https://secure.ssa.gov/poms.nsf/lnx/0501415008PHI",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.de.dhss.ssp.amount
        year = period.this_year
        joint_claim = person("ssi_claim_is_joint", year)
        eligible = person("de_ssp_eligible", period)
        is_couple = joint_claim & _ssi_both_spouses(person, year, eligible)
        per_person_amount = where(is_couple, p.couple / 2, p.individual)
        uncapped_ssi = person("uncapped_ssi", period)
        reduction = max_(0, -uncapped_ssi)
        supplement = max_(0, per_person_amount - reduction)
        # POMS SI 01320.430 D: with an ineligible spouse's income deemed,
        # the supplement is the lesser of separate individual and couple
        # state computations, not the individual rate less the federal
        # shortfall.
        deeming = person("is_ssi_spousal_deeming_applies", year)
        supplement = where(
            deeming,
            ssi_deemed_state_supplement(
                person, period, parameters, p.individual, p.couple
            ),
            supplement,
        )
        return where(
            is_couple,
            _ssi_couple_total(person, year, supplement) / 2,
            supplement,
        )
