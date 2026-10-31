from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_couple_total,
    _ssi_spouse_index,
)


class msp_asset_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Medicare Savings Program asset eligible"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396d#p",
        "https://www.law.cornell.edu/uscode/text/42/1382b",
        "https://www.medicare.gov/basics/costs/help/medicare-savings-programs",
        "https://www.medicareinteractive.org/understanding-medicare/"
        "cost-saving-programs/medicare-savings-programs-qmb-slmb-qi/"
        "medicare-savings-program-income-and-asset-limits",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicare.savings_programs.eligibility
        state_code = person.household("state_code_str", period)
        # Check if asset test applies (some states have eliminated it)
        asset_test_applies = p.asset.applies[state_code]
        # If asset test doesn't apply, everyone is asset-eligible
        # The resources of an individual, or of a married couple living
        # together (42 U.S.C. 1396d(p)(1)(C) applies SSI's resource rules).
        personal_resources = person("ssi_countable_resources", period.this_year)
        married = _ssi_spouse_index(person, period.this_year) >= 0
        countable_resources = _ssi_couple_total(
            person, period.this_year, personal_resources
        )
        asset_limit = where(married, p.asset.couple, p.asset.individual)
        meets_asset_test = countable_resources <= asset_limit
        return where(asset_test_applies, meets_asset_test, True)
