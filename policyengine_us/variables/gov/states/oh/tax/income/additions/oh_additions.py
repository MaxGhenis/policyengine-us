from policyengine_us.model_api import *


class oh_additions(Variable):
    value_type = float
    entity = Person
    label = "Ohio additions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/communications/publications/individual_income_tax_ohio.pdf#page=2",
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-bundle.pdf#page=3",
        "https://cms7files1.revize.com/starkcountyoh/Document_center/Offices/Auditor/Services/Homestead%20Exemption/Ohio_Adj_Gross_Income.pdf#page=1",
        "https://codes.ohio.gov/ohio-revised-code/section-5747.01",
    )
    defined_for = StateCode.OH

    def formula(person, period, parameters):
        p = parameters(period).gov.states.oh.tax.income
        # Each person's Ohio AGI is summed into the filer's (oh_agi). Ohio
        # adjusts "federal adjusted gross income" (R.C. 5747.01(A)), and a
        # tax unit dependent's own income and add-backs are on their own
        # federal return, so they stay off the filer's, as their deductions
        # do (oh_deductions).
        return person_non_dep_add(person, period, p.additions)
