"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : asset_depreciation.py
Object Type     : Asset Depreciation Scenario
Layer           : Accounting
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Generates monthly depreciation journal entries.
===============================================================================
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from dataclasses import dataclass
from decimal import Decimal
from datetime import date

from accounting.enums import DocumentType
from accounting.models import JournalEntry, JournalLine
from scenarios.base import AccountingScenario


@dataclass(slots=True, frozen=True)
class AssetDepreciationRequest:
    """
    Input data for monthly depreciation.
    """

    company_code: str

    cost_center_code: str
    department_code: str

    currency_code: str

    depreciation_date: date

    asset_code: str

    depreciation_amount: Decimal

    description: str = "Monthly Depreciation"


class AssetDepreciationScenario(AccountingScenario):
    """
    Generates accounting entries for monthly depreciation.
    """

    def create(
        self,
        request: AssetDepreciationRequest,
    ) -> JournalEntry:

        document = self.document_generator.create(
            document_type=DocumentType.AD,
            posting_date=request.depreciation_date,
            document_date=request.depreciation_date,
            due_date=request.depreciation_date,
        )

        entry = JournalEntry(
            document=document
        )

        # ------------------------------------------------------------------
        # Debit
        # Depreciation Expense
        # ------------------------------------------------------------------

        entry.add_line(

            JournalLine(

                line_number=1,

                account_number="551",

                company_code=request.company_code,

                cost_center_code=request.cost_center_code,

                department_code=request.department_code,

                currency_code=request.currency_code,

                debit_amount=request.depreciation_amount,

                credit_amount=Decimal("0.00"),

                amount_local=request.depreciation_amount,

                description=request.description,
            )
        )

        # ------------------------------------------------------------------
        # Credit
        # Accumulated Depreciation
        # ------------------------------------------------------------------

        entry.add_line(

            JournalLine(

                line_number=2,

                account_number="082",

                company_code=request.company_code,

                cost_center_code=request.cost_center_code,

                department_code=request.department_code,

                currency_code=request.currency_code,

                debit_amount=Decimal("0.00"),

                credit_amount=request.depreciation_amount,

                amount_local=request.depreciation_amount,

                description=request.description,
            )
        )

        return self.validate(entry)