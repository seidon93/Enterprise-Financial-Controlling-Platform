"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : asset_impairment.py
Object Type     : Asset Impairment Scenario
Layer           : Accounting
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Generates accounting entries for fixed asset impairment.
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
class AssetImpairmentRequest:
    """
    Input data for asset impairment.
    """

    company_code: str

    asset_code: str

    cost_center_code: str
    department_code: str

    currency_code: str

    impairment_date: date

    impairment_amount: Decimal

    description: str = "Asset Impairment"


class AssetImpairmentScenario(AccountingScenario):
    """
    Generates accounting entries for asset impairment.
    """

    def create(
        self,
        request: AssetImpairmentRequest,
    ) -> JournalEntry:

        document = self.document_generator.create(
            document_type=DocumentType.AI,
            posting_date=request.impairment_date,
            document_date=request.impairment_date,
            due_date=request.impairment_date,
        )

        entry = JournalEntry(document=document)

        # ---------------------------------------------------------------------
        # Impairment Expense
        # MD 551
        # ---------------------------------------------------------------------

        entry.add_line(
            JournalLine(
                line_number=1,
                account_number="551",
                company_code=request.company_code,
                cost_center_code=request.cost_center_code,
                department_code=request.department_code,
                currency_code=request.currency_code,
                debit_amount=request.impairment_amount,
                credit_amount=Decimal("0.00"),
                amount_local=request.impairment_amount,
                description=request.description,
            )
        )

        # ---------------------------------------------------------------------
        # Accumulated Impairment
        # DAL 09x
        # (zatím používáme 092, později zmapujeme podle asset_class)
        # ---------------------------------------------------------------------

        entry.add_line(
            JournalLine(
                line_number=2,
                account_number="092",
                company_code=request.company_code,
                cost_center_code=request.cost_center_code,
                department_code=request.department_code,
                currency_code=request.currency_code,
                debit_amount=Decimal("0.00"),
                credit_amount=request.impairment_amount,
                amount_local=request.impairment_amount,
                description=request.description,
            )
        )

        return self.validate(entry)