from policyengine_us.model_api import *


class dc_disability_exclusion(Variable):
    value_type = float
    entity = Person
    label = "DC disability exclusion"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DC
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/47-1803.02#(a)(2)(M)",
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2025_D-2440_Form_012626.pdf#page=1",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.income.disability_income_exclusion
        tax_unit = person.tax_unit
        # D.C. Code 47-1803.02(a)(2)(M) excludes the payments that IRC
        # 105(d) excluded before 1984. Form D-2440 ("Who may file") and
        # 105(d)(1) and (4) require all of:
        # - retired on disability, and permanently and totally disabled
        #   when retired;
        # - under 65 on December 31;
        # - if married, filing a joint return.
        # Not modeled: not having reached the employer's mandatory
        # retirement age on January 1, the election to treat the payments
        # as a pension, and the $100 a week limit for partial weeks.
        # Form D-2440 is one per return, with a column for you and one for
        # your spouse. A dependent's disability payments are on their own
        # return.
        filer = ~person("is_tax_unit_dependent", period)
        retired_on_disability = person("retired_on_total_disability", period)
        under_age_limit = person("age", period) < p.age_limit
        filing_status = tax_unit("filing_status", period)
        not_separate = filing_status != filing_status.possible_values.SEPARATE
        eligible = filer & retired_on_disability & under_age_limit & not_separate
        disability_payments = person("total_disability_payments", period)
        # Lines 1 to 3: up to $5,200 per disabled person.
        capped_disability_payments = eligible * min_(disability_payments, p.cap)
        # Line 4.
        total_capped_payments = tax_unit.sum(capped_disability_payments)
        # Lines 5 to 9. Federal AGI includes the payments, as they are
        # gross income (total_disability_payments is in
        # gov.irs.gross_income.sources).
        federal_agi = tax_unit("adjusted_gross_income", period)
        social_security_income = tax_unit("tax_unit_taxable_social_security", period)
        reduced_income = federal_agi - social_security_income - p.amount
        capped_reduced_income = max_(reduced_income, 0)
        # Line 10.
        exclusion = max_(total_capped_payments - capped_reduced_income, 0)
        # dc_taxable_income_joint sums every person, so each filer gets a
        # share of the return's exclusion in proportion to their payments.
        share = np.zeros_like(total_capped_payments)
        mask = total_capped_payments > 0
        share[mask] = capped_disability_payments[mask] / total_capped_payments[mask]
        return exclusion * share
