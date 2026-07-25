"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : asset_disposal.py
Object Type     : Asset Disposal Scenario
Layer           : Accounting
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Generates accounting entries for disposal of fixed assets.
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
class AssetDisposalRequest:

    company_code: str

    asset_code: str
    asset_name: str
    asset_class: str
    asset_group: str

    supplier_code: str | None

    acquisition_date: date

    acquisition_cost: Decimal

    vat_rate: Decimal

    useful_life_months: int

    depreciation_method: str

    residual_value: Decimal

    currency_code: str

    cost_center_code: str

    department_code: str

    disposal_date: date

    net_book_value: Decimal

    description: str = "Asset Disposal"


class AssetDisposalScenario(AccountingScenario):

    def create(
        self,
        request: AssetDisposalRequest,
    ) -> JournalEntry:

        document = self.document_generator.create(
            document_type=DocumentType.AX,
            posting_date=request.disposal_date,
            document_date=request.disposal_date,
            due_date=request.disposal_date,
        )

        entry = JournalEntry(document=document)

        # Disposal Expense

        entry.add_line(
            JournalLine(
                line_number=1,
                account_number="541",
                company_code=request.company_code,
                cost_center_code=request.cost_center_code,
                department_code=request.department_code,
                currency_code=request.currency_code,
                debit_amount=request.net_book_value,
                credit_amount=Decimal("0.00"),
                amount_local=request.net_book_value,
                description=request.description,
            )
        )

        # Fixed Asset

        entry.add_line(
            JournalLine(
                line_number=2,
                account_number="022",
                company_code=request.company_code,
                cost_center_code=request.cost_center_code,
                department_code=request.department_code,
                currency_code=request.currency_code,
                debit_amount=Decimal("0.00"),
                credit_amount=request.net_book_value,
                amount_local=request.net_book_value,
                description=request.description,
            )
        )

        return self.validate(entry)