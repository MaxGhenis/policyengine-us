from policyengine_us.model_api import *


class federal_eitc_without_age_minimum(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal EITC without age minimum"
    unit = USD
    documentation = "The federal EITC with the minimum age condition ignored."
    definition_period = YEAR
    reference = (
        "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-704&enactments=false",  # (c)(3)(i)
        "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title26-section32&num=0&edition=prelim",  # (c)(1)(A)(ii)(II)
        "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/resident-booklet.pdf#page=22",
    )
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        # Md. Code Tax-Gen. § 10-704(c)(3)(i)1 computes the § 32 credit of an
        # individual without a qualifying child "without regard to the
        # minimum age requirement under § 32(c)(1)(A)(ii)(II)". Only the
        # minimum is disregarded: the individual (or, on a joint return,
        # either spouse) must still not have attained age 65 before the
        # close of the taxable year. The federal maximum-age parameter
        # carries the § 32(n)(2) suspension for 2021. The investment income
        # and identification gates below are unchanged here; how the
        # § 10-704(c)(3)(i)2 disregard of § 32(m) reaches ITIN filers is a
        # separate question.
        person = tax_unit.members
        age = person("age", period)
        max_age = parameters(period).gov.irs.credits.eitc.eligibility.age.max
        is_filer_or_spouse = ~person("is_tax_unit_dependent", period)
        has_child = tax_unit("eitc_child_count", period) > 0
        meets_maximum_age = tax_unit.any((age <= max_age) & is_filer_or_spouse)
        demographic_eligible = has_child | meets_maximum_age
        phased_in = tax_unit("eitc_phased_in", period)
        maximum = tax_unit("eitc_maximum", period)
        reduction = tax_unit("eitc_reduction", period)
        investment_eligible = tax_unit("eitc_investment_income_eligible", period)
        filer_has_ssn = tax_unit("filer_meets_eitc_identification_requirements", period)
        return (
            min_(phased_in, max_(0, maximum - reduction))
            * demographic_eligible
            * investment_eligible
            * filer_has_ssn
        )
