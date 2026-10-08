from policyengine_us.model_api import *


class EmployerPremiumContribution(Enum):
    NONE = "NONE"  # Employer paid none of premiums.
    SOME = "SOME"
    ALL = "ALL"
    NA = "N/A"


class employer_contribution_to_health_insurance_premiums_category(Variable):
    value_type = Enum
    entity = Person
    label = "Extent to which employer paid health insurance premiums"
    documentation = (
        "How much of the person's employer health plan premiums the employer "
        "pays. NONE records that the employer pays nothing, for example COBRA "
        "coverage the person pays for in full. N/A, the default, records no "
        "information."
    )
    definition_period = YEAR
    possible_values = EmployerPremiumContribution
    default_value = EmployerPremiumContribution.NA
