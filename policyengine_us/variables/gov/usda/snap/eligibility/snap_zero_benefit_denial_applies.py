from policyengine_us.model_api import *


class snap_zero_benefit_denial_applies(Variable):
    value_type = bool
    entity = SPMUnit
    label = "SNAP zero-benefit denial applies"
    documentation = (
        "Whether the state denies SNAP to units of three or more whose "
        "benefit computes to zero, and this SPM unit is one"
    )
    definition_period = MONTH
    reference = (
        # 7 CFR 273.10(e)(2)(iii).
        "https://www.ecfr.gov/current/title-7/section-273.10#p-273.10(e)(2)(iii)",
        "https://www.cdss.ca.gov/lettersnotices/entres/getinfo/acl/2014/14-63.pdf#page=2",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.usda.snap.eligibility.zero_benefit_denial
        state = spm_unit.household("state_code_str", period)
        in_effect = p.in_effect[state].astype(bool)
        size = spm_unit("snap_unit_size", period)
        # The allotment snap_normal_allotment would compute. That variable is
        # defined for is_snap_eligible, which reads this one, so it is built
        # here from the same components. Any minimum allotment counts: a unit
        # that receives one is not entitled to no benefits.
        max_allotment = spm_unit("snap_max_allotment", period)
        expected_contribution = spm_unit("snap_expected_contribution", period)
        min_allotment = spm_unit("snap_min_allotment", period)
        allotment = max_(min_allotment, max_allotment - expected_contribution)
        # The rule excepts a zero due to proration or to the rule against
        # issuing less than $10 in an initial month; neither is modeled.
        return in_effect & (size >= p.minimum_household_size) & (allotment <= 0)
