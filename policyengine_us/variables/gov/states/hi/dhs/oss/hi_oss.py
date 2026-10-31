from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi._ssi_state_supplement import (
    ssi_deemed_state_supplement,
)


class hi_oss(Variable):
    value_type = float
    entity = Person
    label = "Hawaii Optional State Supplementation"
    unit = USD
    definition_period = MONTH
    defined_for = "hi_oss_eligible"
    reference = (
        "https://secure.ssa.gov/apps10/poms.nsf/lnx/0501415200SF",
        "https://secure.ssa.gov/POMS.NSF/lnx/0501415057",
    )

    def formula(person, period, parameters):
        # Per POMS SI 02005.001: when federal SSI is payable, the
        # full state supplement applies. When countable income
        # exceeds the FBR, the excess reduces the supplement
        # dollar-for-dollar ("state supplement only" case).
        payment_standard = person("hi_oss_payment_amount", period)
        uncapped_ssi = person("uncapped_ssi", period)
        income_excess = max_(0, -uncapped_ssi)
        payment = max_(0, payment_standard - income_excess)
        # POMS SI 01320.430 D: with an ineligible spouse's income deemed,
        # the supplement is the lesser of separate individual and couple
        # state computations, not the individual rate less the federal
        # shortfall.
        deeming = person("is_ssi_spousal_deeming_applies", period.this_year)
        la = person("hi_oss_living_arrangement", period)
        p = parameters(period).gov.states.hi.dhs.oss.payment
        deemed_payment = ssi_deemed_state_supplement(
            person,
            period,
            parameters,
            p.individual.amount[la],
            p.couple.amount[la],
        )
        return where(deeming, deemed_payment, payment)
