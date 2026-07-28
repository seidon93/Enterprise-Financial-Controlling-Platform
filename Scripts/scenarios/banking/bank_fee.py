"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : bank_fee.py
Object Type     : Bank Fee Scenario
Layer           : ETL
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Generates accounting entries for bank fees.
===============================================================================
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from domain.bank_accounts import BankAccounts
from accounting.enums import DocumentType
from accounting.models import JournalEntry, JournalLine
from scenarios.base import AccountingScenario


@dataclass(slots=True, frozen=True)
class BankFeeRequest:
    """
    Input data for bank fee.
    """

    company_code: str

    bank_account: str

    transaction_date: date

    amount: Decimal

    currency_code: str

    cost_center_code: str

    department_code: str


class BankFeeScenario(AccountingScenario):
    """
    Generates accounting entries for bank fee.
    """

    def create(
        self,
        request: BankFeeRequest,
    ) -> JournalEntry:

        document = self.document_generator.create(
            document_type=DocumentType.BANK,
            posting_date=request.transaction_date,
            document_date=request.transaction_date,
            due_date=request.transaction_date,
        )

        entry = JournalEntry(document=document)

        # MD 568
        entry.add_line(
            JournalLine(
                line_number=1,
                account_number=BankAccounts.BANK_FEES,
                company_code=request.company_code,
                cost_center_code=request.cost_center_code,
                department_code=request.department_code,
                currency_code=request.currency_code,
                debit_amount=request.amount,
                credit_amount=Decimal("0.00"),
                amount_local=request.amount,
                description="Bank Fee",
            )
        )

        # DAL 221
        entry.add_line(
            JournalLine(
                line_number=2,
                account_number=BankAccounts.BANK_ACCOUNT,
                company_code=request.company_code,
                cost_center_code=request.cost_center_code,
                department_code=request.department_code,
                currency_code=request.currency_code,
                debit_amount=Decimal("0.00"),
                credit_amount=request.amount,
                amount_local=request.amount,
                description="Bank Account",
            )
        )

        return self.validate(entry)