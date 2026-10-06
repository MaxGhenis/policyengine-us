from policyengine_us.model_api import *


class md_pension_subtraction_amount(Variable):
    value_type = float
    entity = Person
    label = "MD pension subtraction from AGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://interactive.marylandtaxes.gov/Individuals/iFile_ChooseForm/PriorYearForms/Resident_Booklet_2021.pdf#page=13",
        # Md. Code Tax-Gen. § 10-209(d)(1).
        "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-209",
    )
    defined_for = StateCode.MD

    def formula(person, period, parameters):
        p = parameters(period).gov.states.md.tax.income.agi.subtractions
        # determine pension subtraction eligiblity for each person
        dependent = person("is_tax_unit_dependent", period)
        min_age = p.pension.min_age
        elderly = person("age", period) >= min_age
        disabled = person("is_disabled", period)
        partner_is_disabled = person("has_disabled_spouse", period)
        eligible = ~dependent & (elderly | disabled | partner_is_disabled)
        # calculate pension subtraction amount for each person
        peninc = add(person, period, p.pension.sources)
        # § 10-209(d)(1): military retirement income included in the
        # § 10-207(q) subtraction may not be taken into account here. That
        # subtraction is capped per person and also covers survivor benefits;
        # the capped amount is applied to the person's own military retirement
        # pay first, since only that pay is inside the pension sources.
        p_mil = p.military_retirement
        military_cap = where(
            person("age", period) >= p_mil.age_threshold,
            p_mil.max_amount.at_or_above_age_threshold,
            p_mil.max_amount.under_age_threshold,
        )
        military_pay = person("military_retirement_pay", period)
        military_income = military_pay + person(
            "military_retirement_pay_survivors", period
        )
        military_subtracted = min_(military_income, military_cap)
        peninc = max_(0, peninc - min_(military_pay, military_subtracted))
        socsec = person("social_security", period)
        amount = min_(peninc, max_(0, p.pension.max_amount - socsec))
        # return pension subtraction amount for each eligible person
        return eligible * amount
