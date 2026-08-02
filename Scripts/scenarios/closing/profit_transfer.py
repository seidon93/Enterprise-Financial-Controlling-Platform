"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : profit_transfer.py
Object Type     : Profit Transfer Scenario
Layer           : ETL
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Transfers yearly profit or loss to retained earnings.
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

from scenarios.base import AccountingScenario


@dataclass(slots=True, frozen=True)
class ProfitTransferRequest:

    company_code: str

    closing_date: date

    amount: Decimal

    currency_code: str

    cost_center_code: str

    department_code: str

    profit_account: str

    retained_earnings_account: str


class ProfitTransferScenario(AccountingScenario):

    def create(
        self,
        request: ProfitTransferRequest,
    ) -> JournalEntry:

        document = self.document_generator.create(

            document_type=DocumentType.CLOSING,

            posting_date=request.closing_date,

            document_date=request.closing_date,

            due_date=request.closing_date,
        )

        entry = JournalEntry(document=document)

        # MD Profit / Loss

        entry.add_line(

            JournalLine(

                line_number=1,

                account_number=request.profit_account,

                company_code=request.company_code,

                cost_center_code=request.cost_center_code,

                department_code=request.department_code,

                currency_code=request.currency_code,

                debit_amount=request.amount,

                credit_amount=Decimal("0.00"),

                amount_local=request.amount,

                description="Year End Profit Transfer",
            )
        )

        # DAL Retained Earnings

        entry.add_line(

            JournalLine(

                line_number=2,

                account_number=request.retained_earnings_account,

                company_code=request.company_code,

                cost_center_code=request.cost_center_code,

                department_code=request.department_code,

                currency_code=request.currency_code,

                debit_amount=Decimal("0.00"),

                credit_amount=request.amount,

                amount_local=request.amount,

                description="Retained Earnings",
            )
        )

        return self.validate(entry)