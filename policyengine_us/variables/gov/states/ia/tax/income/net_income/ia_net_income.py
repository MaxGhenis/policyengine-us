from policyengine_us.model_api import *


class ia_net_income(Variable):
    value_type = float
    entity = Person
    label = "Iowa net income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf",
        "https://revenue.iowa.gov/media/2650/download?inline",
        "https://revenue.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf",
        "https://revenue.iowa.gov/media/2721/download?inline",
        # Iowa Code 422.13(1)(a): a dependent with net income of $5,000 or
        # more files their own return.
        "https://www.legis.iowa.gov/docs/code/2022/422.13.pdf#page=1",
        "https://revenue.iowa.gov/media/2650/download?inline#page=4",
        "https://revenue.iowa.gov/media/2721/download?inline#page=4",
    )
    defined_for = StateCode.IA

    def formula(person, period, parameters):
        gross_income = person("ia_gross_income", period)
        income_adjustments = person("ia_income_adjustments", period)
        # The IA 1040 has columns only for the taxpayer (A) and spouse (B).
        # A tax unit dependent's income is on the dependent's own return,
        # as it is for federal AGI, so it is not on this return.
        is_dependent = person("is_tax_unit_dependent", period)
        return ~is_dependent * (gross_income - income_adjustments)
