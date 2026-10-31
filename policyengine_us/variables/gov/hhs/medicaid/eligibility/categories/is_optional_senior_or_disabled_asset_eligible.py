from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_couple_total,
    _ssi_spouse_index,
)


class is_optional_senior_or_disabled_asset_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Asset-eligibility for State’s optional Medicaid pathway for seniors or people with disabilities"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1396a#m"

    def formula(person, period, parameters):
        #  Assets
        # SSI financial responsibility rules (42 CFR 435.602): the unit is
        # the individual or the married couple living together, not the tax
        # filing unit or a marital unit holding other adults.
        personal_assets = person("ssi_countable_resources", period)  # $
        assets = _ssi_couple_total(person, period, personal_assets)
        is_couple = _ssi_spouse_index(person, period) >= 0
        state = person.household("state_code_str", period)

        #  Parameters
        p = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.senior_or_disabled

        #  Asset limit
        asset_limit = where(
            is_couple,
            p.assets.limit.couple[state],
            p.assets.limit.individual[state],
        )

        return assets < asset_limit
