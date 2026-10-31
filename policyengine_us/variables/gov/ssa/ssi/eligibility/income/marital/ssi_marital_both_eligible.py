from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_both_spouses,
)


class ssi_marital_both_eligible(Variable):
    value_type = bool
    entity = Person
    label = (
        "Both spouses of a married couple living together are aged, blind or disabled"
    )
    definition_period = YEAR

    def formula(person, period, parameters):
        eligible = person("is_ssi_aged_blind_disabled", period)

        return _ssi_both_spouses(person, period, eligible)
