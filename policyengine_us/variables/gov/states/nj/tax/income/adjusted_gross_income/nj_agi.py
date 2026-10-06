from policyengine_us.model_api import *


class nj_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/new-jersey/2022/title-54/section-54-8a-36/",
        # N.J.S. 54A:8-3.1(a), (c), (f): a joint return covers husband and
        # wife only; a minor's own return is filed for the minor.
        "https://law.justia.com/codes/new-jersey/title-54a/section-54a-8-3-1/",
        # NJ-1040 Worksheet L counts dependents' own NJ-1040 line 27 income
        # separately from the filer's line 27.
        "https://www.nj.gov/treasury/taxation/pdf/other_forms/tgi-ee/2024/1040i.pdf#page=41",
    )
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        # A tax unit dependent's income belongs on the dependent's own
        # return, as irs_gross_income leaves it off the federal return.
        total_income = tax_unit_non_dep_add(tax_unit, period, ["nj_total_income"])
        p = parameters(period).gov.states.nj.tax.income
        exclusions = add(tax_unit, period, p.all_exclusions)
        return max_(0, total_income - exclusions)
