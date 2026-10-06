from policyengine_us.model_api import *


class in_other_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana other deductions"
    unit = USD
    definition_period = YEAR
    documentation = "Other deductions available in Indiana including those for civil service annuities, disability retirement, government or civic group capital contributions, human services for Medicaid recipients,  infrastructure fund gifts, indiana lottery winings annuity, Indiana partnership long-term care policy premiums, military survivor's benefits (military retirement pay itself is deducted through in_military_retirement_deduction), National Guard and reserve component members, Olympic/Paralymic medal winners, qualified patents income eemption, railroad unemployment and sickness benefits, repayment of previously taxed income deductions, COVID-related employee retention credit dissalowed expenses, and Indiana-only tax-exempt bonds."
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-2"
    defined_for = StateCode.IN
