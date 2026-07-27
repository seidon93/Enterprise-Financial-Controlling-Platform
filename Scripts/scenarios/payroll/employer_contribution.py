"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : employer_contribution.py
Object Type     : Employer Contribution Scenario
Layer           : ETL
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Generates accounting entries for employer social and health contributions.
===============================================================================
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from accounting.enums import DocumentType
from accounting.models import JournalEntry, JournalLine
from accounting.payroll_accounts import PayrollAccounts
from scenarios.base import AccountingScenario


@dataclass(slots=True, frozen=True)
class EmployerContributionRequest:
    """
    Input data for employer contributions.
    """

    company_code: str

    employee_code: str

    payroll_date: date

    contribution_amount: Decimal

    currency_code: str

    cost_center_code: str

    department_code: str


class EmployerContributionScenario(AccountingScenario):
    """
    Generates employer contribution journal entries.
    """

    def create(
        self,
        request: EmployerContributionRequest,
    ) -> JournalEntry:

        document = self.document_generator.create(
            document_type=DocumentType.PAYROLL,
            posting_date=request.payroll_date,
            document_date=request.payroll_date,
            due_date=request.payroll_date,
        )

        entry = JournalEntry(document=document)

        # MD 524
        entry.add_line(
            JournalLine(
                line_number=1,
                account_number=PayrollAccounts.EMPLOYER_CONTRIBUTIONS,
                company_code=request.company_code,
                cost_center_code=request.cost_center_code,
                department_code=request.department_code,
                currency_code=request.currency_code,
                employee_code=request.employee_code,
                debit_amount=request.contribution_amount,
                credit_amount=Decimal("0.00"),
                amount_local=request.contribution_amount,
                description="Employer Contributions",
            )
        )

        # DAL 336
        entry.add_line(
            JournalLine(
                line_number=2,
                account_number=PayrollAccounts.SOCIAL_INSURANCE,
                company_code=request.company_code,
                cost_center_code=request.cost_center_code,
                department_code=request.department_code,
                currency_code=request.currency_code,
                employee_code=request.employee_code,
                debit_amount=Decimal("0.00"),
                credit_amount=request.contribution_amount,
                amount_local=request.contribution_amount,
                description="Social and Health Insurance Liability",
            )
        )

        return self.validate(entry)