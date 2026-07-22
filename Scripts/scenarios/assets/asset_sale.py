"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : asset_sale.py
Object Type     : Asset Sale Scenario
Layer           : Accounting
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Generates accounting entries for sale of fixed assets.
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
class AssetSaleRequest:
    """
    Input data for asset sale.
    """

    company_code: str

    asset_code: str

    customer_code: str | None

    cost_center_code: str
    department_code: str

    currency_code: str

    sale_date: date

    sale_amount: Decimal

    description: str = "Asset Sale"


class AssetSaleScenario(AccountingScenario):
    """
    Generates accounting entries for fixed asset sale.
    """

    def create(
        self,
        request: AssetSaleRequest,
    ) -> JournalEntry:

        document = self.document_generator.create(
            document_type=DocumentType.AS,
            posting_date=request.sale_date,
            document_date=request.sale_date,
            due_date=request.sale_date,
        )

        entry = JournalEntry(document=document)

        # --------------------------------------------------------------
        # Trade Receivable
        # MD 311
        # --------------------------------------------------------------

        entry.add_line(
            JournalLine(
                line_number=1,
                account_number="311",
                company_code=request.company_code,
                cost_center_code=request.cost_center_code,
                department_code=request.department_code,
                currency_code=request.currency_code,
                debit_amount=request.sale_amount,
                credit_amount=Decimal("0.00"),
                amount_local=request.sale_amount,
                description=request.description,
                customer_code=request.customer_code,
            )
        )

        # --------------------------------------------------------------
        # Revenue from Sale of Fixed Assets
        # DAL 641
        # --------------------------------------------------------------

        entry.add_line(
            JournalLine(
                line_number=2,
                account_number="641",
                company_code=request.company_code,
                cost_center_code=request.cost_center_code,
                department_code=request.department_code,
                currency_code=request.currency_code,
                debit_amount=Decimal("0.00"),
                credit_amount=request.sale_amount,
                amount_local=request.sale_amount,
                description=request.description,
            )
        )

        return self.validate(entry)