from policyengine_us.model_api import *


class dc_income_tax_before_credits_indiv(Variable):
    value_type = float
    entity = TaxUnit
    label = "DC income tax before credits when married couples file separately"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=36",
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=34",
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2025_D-2440_Form_012626.pdf#page=2",
    )
    defined_for = StateCode.DC

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        taxable_income = person("dc_taxable_income_indiv", period)
        # A married couple can claim the Form D-2440 disability exclusion
        # only on a joint return ("Who may file"), not when filing
        # separately on the same return.
        filing_status = person.tax_unit("filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT
        disability_exclusion = person("dc_disability_exclusion", period)
        taxinc = max_(0, taxable_income + joint * disability_exclusion)
        p = parameters(period).gov.states
        return tax_unit.sum(p.dc.tax.income.rates.calc(taxinc))
