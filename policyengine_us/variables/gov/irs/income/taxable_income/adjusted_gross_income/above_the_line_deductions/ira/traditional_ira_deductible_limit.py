from policyengine_us.model_api import *


class traditional_ira_deductible_limit(Variable):
    value_type = float
    entity = Person
    label = "Traditional IRA deductible dollar limit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/219#g",
        # Section 219(d)(1) before its repeal for years after 2019.
        "https://www.govinfo.gov/content/pkg/USCODE-2018-title26/html/USCODE-2018-title26-subtitleA-chap1-subchapB-partVII-sec219.htm",
    )
    documentation = (
        "The section 219(b) dollar limit after the section 219(g) workplace plan "
        "phase-out, and zero for years before 2020 once the individual attains "
        "age 70½ under former section 219(d)(1). Age is compared with 70.5 "
        "directly, so an integer age of 70 is treated as not yet 70½. A "
        "dependent's limit uses single-filer thresholds and their own gross "
        "income, approximating the dependent's own return."
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.ald.ira
        phase_out = p.active_participant_phase_out
        annual_limit = person("ira_annual_limit", period)
        covered = person("ira_active_participant", period)
        filing_status = person.tax_unit("filing_status", period)
        statuses = filing_status.possible_values
        joint = filing_status == statuses.JOINT
        separate = filing_status == statuses.SEPARATE
        # For separate filers, cohabitation means living with the spouse at
        # any time during the tax year; section 219(g)(4) requires all-year separation.
        cohabitating = person.tax_unit("cohabitating_spouses", period)
        separate_living_apart = separate & ~cohabitating

        # Joint filers' coverage must exclude their dependents. Marital units
        # also identify a covered spouse who files a separate return.
        filer = person("is_tax_unit_head_or_spouse", period)
        joint_spouse_covered = (
            person.tax_unit.sum(covered & filer) - (covered & filer)
        ) > 0
        separate_spouse_covered = (person.marital_unit.sum(covered) - covered) > 0
        spouse_covered = filer & (
            (joint & joint_spouse_covered)
            | (separate & cohabitating & separate_spouse_covered)
        )

        # Dependents file their own returns, so they use the single range
        # and their own income rather than the parents' return.
        dependent = person("is_tax_unit_dependent", period)
        use_single = separate_living_apart | dependent
        start = where(
            use_single, phase_out.start.SINGLE, phase_out.start[filing_status]
        )
        width = where(
            use_single, phase_out.width.SINGLE, phase_out.width[filing_status]
        )
        spouse_only = ~covered & spouse_covered & joint
        start = where(spouse_only, phase_out.spouse_covered_start, start)
        width = where(spouse_only, phase_out.spouse_covered_width, width)

        magi = where(
            dependent,
            person("traditional_ira_dependent_magi", period),
            person.tax_unit("traditional_ira_deduction_magi", period),
        )
        reduction_fraction = clip((magi - start) / width, 0, 1)
        # Section 219(g)(2)(C) rounds the reduction down to a multiple of $10.
        reduction = (
            np.floor(annual_limit * reduction_fraction / phase_out.rounding)
            * phase_out.rounding
        )
        reduced_limit = where(
            magi >= start + width,
            0,
            max_(phase_out.floor, annual_limit - reduction),
        )
        limit = where(covered | spouse_covered, reduced_limit, annual_limit)
        # Former section 219(d)(1) barred the deduction from the year the
        # individual attained age 70½. Roth limits disregard it (408A(c)(2)).
        age_barred = person("traditional_ira_age_barred", period)
        return where(age_barred, 0, limit)
