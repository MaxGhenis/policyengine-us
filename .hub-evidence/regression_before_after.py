"""Run the same externally specified cases with prior formulas or current ones.

The prior mode overlays source read from commit79b96595f5 into the current
system. New carryover inputs remain available so ignored line2 is observable.
This is a synthetic-household regression, not a dataset microsimulation.
"""

import os
import subprocess
import numpy as np
import pytest
from policyengine_us import Simulation
from policyengine_us.system import system
from policyengine_us.model_api import Reform, Variable

OVERLAYS = [
    "policyengine_us/variables/gov/irs/income/taxable_income/deductions/itemizing/total_misc_deductions.py",
    "policyengine_us/variables/gov/irs/income/taxable_income/deductions/itemizing/interest_deduction.py",
    "policyengine_us/variables/gov/irs/income/taxable_income/deductions/itemizing/investment_interest/form_4952_total_investment_interest_expense.py",
    "policyengine_us/variables/gov/irs/income/taxable_income/deductions/itemizing/investment_interest/form_4952_net_investment_gain.py",
    "policyengine_us/variables/gov/irs/income/taxable_income/deductions/itemizing/investment_interest/form_4952_net_capital_gain.py",
    "policyengine_us/variables/gov/irs/income/taxable_income/deductions/itemizing/investment_interest/form_4952_elected_investment_income.py",
    "policyengine_us/variables/gov/irs/income/taxable_income/deductions/itemizing/investment_interest/form_4952_investment_expenses.py",
    "policyengine_us/variables/gov/states/mt/tax/income/deductions/itemized/general/mt_itemized_deductions_indiv.py",
    "policyengine_us/variables/gov/states/mt/tax/income/deductions/itemized/federal_itemization/mt_itemized_deductions_for_federal_itemization_indiv.py",
]


class PriorForm4952(Reform):
    def apply(self):
        for path in OVERLAYS:
            source = subprocess.check_output(
                ["git", "--git-dir=.git-local", "show", f"79b96595f5:{path}"], text=True
            )
            scope = {}
            exec(compile(source, path, "exec"), scope)
            cls = scope[path.rsplit("/", 1)[-1][:-3]]
            self.replace_variable(cls)


class MainUncappedInterest(Reform):
    def apply(self):
        path = "policyengine_us/variables/gov/irs/income/taxable_income/deductions/itemizing/interest_deduction.py"
        source = subprocess.check_output(
            ["git", "--git-dir=.git-local", "show", f"b79705b4bd:{path}"], text=True
        )
        scope = {}
        exec(compile(source, path, "exec"), scope)
        self.replace_variable(scope["interest_deduction"])


prior_system = PriorForm4952(system)
main_system = MainUncappedInterest(system)


def sim(people, year=2025, unit=None, state="TX", tax_benefit_system=None):
    period = str(year)
    members = list(people)
    return Simulation(
        situation={
            "people": {
                k: {v: {period: x} for v, x in person.items()}
                for k, person in people.items()
            },
            "tax_units": {
                "unit": {
                    "members": members,
                    **{v: {period: x} for v, x in (unit or {}).items()},
                }
            },
            "households": {
                "household": {"members": members, "state_code": {period: state}}
            },
        },
        tax_benefit_system=tax_benefit_system if tax_benefit_system is not None else (prior_system if os.environ.get("FORM4952_BEFORE") == "1" else system),
    )


def test_carryover_preserves_mortgage():
    s = sim(
        {
            "head": {
                "deductible_mortgage_interest": 10000,
                "investment_interest_expense": 2000,
                "taxable_interest_income": 3000,
            }
        },
        unit={"form_4952_disallowed_investment_interest_expense_prior_year": 4000},
    )
    assert s.calculate("interest_deduction", "2025")[0] == 13000


def test_carryover_alone():
    s = sim(
        {"head": {"taxable_interest_income": 5000}},
        year=2026,
        unit={"form_4952_disallowed_investment_interest_expense_prior_year": 4000},
    )
    assert s.calculate("investment_interest_expense_deduction", "2026")[0] == 4000


def test_dependent_investments():
    s = sim(
        {
            "head": {
                "is_tax_unit_head": True,
                "taxable_interest_income": 1000,
                "investment_interest_expense": 5000,
            },
            "child": {
                "age": 12,
                "is_tax_unit_dependent": True,
                "investment_interest_expense": 5000,
                "long_term_capital_gains": 10000,
                "short_term_capital_gains": 9000,
                "investment_income_elected_form_4952": 20000,
                "qualified_dividend_income": 10000,
            },
        }
    )
    assert s.calculate("investment_interest_expense_deduction", "2025")[0] == 1000


def test_dependent_fees_2017():
    s = sim(
        {
            "head": {"is_tax_unit_head": True, "investment_expenses": 3000},
            "child": {
                "age": 12,
                "is_tax_unit_dependent": True,
                "investment_expenses": 3000,
            },
        },
        year=2017,
        unit={"adjusted_gross_income": 100000},
    )
    assert s.calculate("form_4952_investment_expenses", "2017")[0] == 1000


def test_montana_spouses():
    zeros = {
        v: 0
        for v in [
            "mortgage_interest",
            "mt_misc_deductions",
            "mt_medical_expense_deduction_indiv",
            "mt_salt_deduction",
            "mt_federal_income_tax_deduction_indiv",
        ]
    }
    s = sim(
        {
            "head": {
                **zeros,
                "is_tax_unit_head": True,
                "is_tax_unit_head_or_spouse": True,
                "investment_interest_expense": 300,
                "taxable_interest_income": 600,
            },
            "spouse": {
                **zeros,
                "is_tax_unit_spouse": True,
                "is_tax_unit_head_or_spouse": True,
                "investment_interest_expense": 900,
            },
        },
        year=2023,
        state="MT",
        unit={"filing_status": "JOINT", "charitable_deduction": 0},
    )
    np.testing.assert_allclose(
        s.calculate("mt_itemized_deductions_indiv", "2023"), [300, 0]
    )



def test_main_federal_cap():
    s = sim({'head': {'is_tax_unit_head': True, 'age': 40, 'employment_income': 140000, 'taxable_interest_income': 10000, 'investment_interest_expense': 15000, 'deductible_mortgage_interest': 20000}}, unit={'state_income_tax': 0, 'state_sales_tax': 0}, tax_benefit_system=main_system if os.environ.get('FORM4952_BEFORE') == '1' else system)
    assert s.calculate('income_tax', '2025')[0] == 21647



def test_dependent_fees_stay_off_schedule_a():
    s = sim({'head': {'is_tax_unit_head': True, 'investment_expenses': 3000}, 'child': {'age': 12, 'is_tax_unit_dependent': True, 'investment_expenses': 50000}}, year=2017, unit={'adjusted_gross_income': 100000})
    assert s.calculate('total_misc_deductions', '2017')[0] == 3000
    assert s.calculate('misc_deduction', '2017')[0] == 1000
