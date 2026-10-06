from policyengine_us.model_api import *


class filer_adjusted_earnings(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Filer earned income adjusted for excluded wages and self-employment tax"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/32#c_2"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        excluded_wages = max_(
            0,
            person("employment_income", period)
            - person("irs_employment_income", period),
        )
        # Subtract payroll exclusions for each filer before summing. The
        # existing self-employment adjustment and per-person floor remain.
        earnings = max_(0, person("adjusted_earnings", period) - excluded_wages)
        is_filer = not_(person("is_tax_unit_dependent", period))
        return tax_unit.sum(earnings * is_filer)
