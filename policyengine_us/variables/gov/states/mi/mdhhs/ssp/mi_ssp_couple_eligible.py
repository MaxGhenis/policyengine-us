from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_both_spouses,
)
from policyengine_us.variables.gov.states.mi.mdhhs.ssp.mi_ssp_living_arrangement import (
    MISSPLivingArrangement,
)


class mi_ssp_couple_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Michigan SSP couple rate applies"
    definition_period = MONTH
    defined_for = "mi_ssp_eligible"
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/EX/BP/Public/BEM/660.pdf#page=1",
        "https://mdhhs-pres-prod.michigan.gov/olmweb/EX/BP/Public/BEM/660.pdf#page=4",
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/RF/Public/RFT/248.pdf#page=2",
    )

    def formula(person, period, parameters):
        year = period.this_year
        joint_claim = person("ssi_claim_is_joint", year)
        eligible = person("mi_ssp_eligible", period)
        # Reading the spouse's value of the variable used in defined_for is
        # safe here; a variable masked by a different defined_for would read
        # as zero for a spouse outside it.
        both_eligible = _ssi_both_spouses(person, year, eligible)
        category = person("mi_ssp_payment_category", period)
        qualifying_arrangements = [
            value
            for value in MISSPLivingArrangement
            if value != MISSPLivingArrangement.NONE
        ]
        both_same_arrangement = (
            sum(
                _ssi_both_spouses(person, year, category == value)
                for value in qualifying_arrangements
            )
            > 0
        )
        return joint_claim & both_eligible & both_same_arrangement
