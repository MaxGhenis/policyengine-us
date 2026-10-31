from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_spouse_index,
    _ssi_spouse_value,
)


class KYSSPClaimType(Enum):
    INDIVIDUAL = "Individual"
    COUPLE_BOTH_ELIGIBLE = "Couple, both eligible"
    COUPLE_ONE_ELIGIBLE = "Couple, one eligible with ineligible spouse"


class ky_ssp_claim_type(Variable):
    value_type = Enum
    entity = Person
    label = "Kentucky SSP claim type"
    definition_period = MONTH
    defined_for = StateCode.KY
    possible_values = KYSSPClaimType
    default_value = KYSSPClaimType.INDIVIDUAL
    reference = (
        "https://apps.legislature.ky.gov/law/kar/titles/921/002/015/",
        "https://www.chfs.ky.gov/agencies/dcbs/dfs/Documents/OMVOLV.pdf#page=41",
    )

    def formula(person, period, parameters):
        # §9(1)(c) couple rates apply to an "eligible couple" — both spouses
        # must qualify for SSP itself, not merely for SSI. The §4(1) SSP
        # categorical tests (SSI-eligible + age ≥ 18 + qualifying living
        # arrangement) are applied here. The §4(1)(b) income test is
        # intentionally excluded to avoid a cycle through
        # ky_ssp_payment_standard → ky_ssp_claim_type.
        is_ssi_eligible = person("is_ssi_eligible", period)
        is_adult = person("is_adult", period)
        category = person("ky_ssp_category", period)
        in_qualifying_category = category != category.possible_values.NONE
        ssp_categorically_eligible = is_ssi_eligible & is_adult & in_qualifying_category
        year = period.this_year
        has_spouse = _ssi_spouse_index(person, year) >= 0
        spouse_eligible = _ssi_spouse_value(
            person, year, ssp_categorically_eligible, False
        )
        both_eligible = ssp_categorically_eligible & spouse_eligible
        one_eligible_couple = ssp_categorically_eligible & has_spouse & ~spouse_eligible
        return select(
            [both_eligible, one_eligible_couple],
            [
                KYSSPClaimType.COUPLE_BOTH_ELIGIBLE,
                KYSSPClaimType.COUPLE_ONE_ELIGIBLE,
            ],
            default=KYSSPClaimType.INDIVIDUAL,
        )
