from policyengine_us.model_api import *


class military_retirement_pay(Variable):
    value_type = float
    entity = Person
    label = "Military retirement pay"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Taxable retired pay received for the person's own service in the "
        "United States uniformed services, as reported on Form 1099-R by the "
        "Defense Finance and Accounting Service. This amount is part of "
        "taxable_pension_income, so it reaches federal adjusted gross income "
        "and pension_income once; do not enter it again as public or private "
        "pension income. Survivor Benefit Plan annuities paid to a surviving "
        "spouse are entered as military_retirement_pay_survivors."
    )
    reference = (
        "https://militarypay.defense.gov/Pay/Retirement/",
        "https://www.law.cornell.edu/uscode/text/26/61#a_11",
    )
    uprating = "calibration.gov.irs.soi.taxable_pension_income"
