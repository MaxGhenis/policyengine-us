from policyengine_us.model_api import *


class snap_state_using_standard_utility_allowance(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Qualifies for the state's SNAP heat-and-eat utility allowance"
    reference = (
        "https://www.law.cornell.edu/uscode/text/7/2014#e_6_C_iv_I",
        "https://www.congress.gov/119/plaws/publ21/PLAW-119publ21.pdf#page=12",
    )

    def formula(spm_unit, period, parameters):
        state = spm_unit.household("state_code", period)
        p = parameters(period).gov.usda.snap.income.deductions.utility

        heat_and_eat = p.always_standard[state].astype(bool)
        if p.heat_and_eat.requires_elderly_disabled:
            return heat_and_eat & spm_unit("has_snap_elderly_disabled_member", period)
        return heat_and_eat
