from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi._ssi_state_supplement import (
    ssi_deemed_state_supplement,
)


class dc_ossp(Variable):
    value_type = float
    entity = Person
    label = "DC Optional State Supplemental Payment"
    unit = USD
    definition_period = MONTH
    defined_for = "dc_ossp_eligible"
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.49",
        "https://www.ssa.gov/pubs/EN-05-11162.pdf#page=2",
    )

    def formula(person, period, parameters):
        # Per POMS SI 02005.001: when federal SSI is payable, the
        # full state supplement applies. When countable income
        # exceeds the FBR, the excess reduces the supplement
        # dollar-for-dollar ("state supplement only" case).
        payment_standard = person("dc_ossp_payment_amount", period)
        uncapped_ssi = person("uncapped_ssi", period)
        income_excess = max_(0, -uncapped_ssi)
        payment = max_(0, payment_standard - income_excess)
        # POMS SI 01320.430 D: with an ineligible spouse's income deemed,
        # the supplement is the lesser of separate individual and couple
        # state computations, not the individual rate less the federal
        # shortfall.
        deeming = person("is_ssi_spousal_deeming_applies", period.this_year)
        living_arrangement = person("dc_ossp_living_arrangement", period)
        p = parameters(period).gov.states.dc.dhcf.ossp.payment
        deemed_payment = ssi_deemed_state_supplement(
            person,
            period,
            parameters,
            p.individual[living_arrangement],
            p.couple[living_arrangement],
        )
        return where(deeming, deemed_payment, payment)
