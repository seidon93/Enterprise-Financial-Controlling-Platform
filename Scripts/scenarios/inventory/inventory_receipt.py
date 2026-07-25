"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : inventory_receipt.py
Object Type     : Inventory Receipt Scenario
Layer           : ETL
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Generates accounting entries for inventory receipt from supplier.
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


class InventoryAccounts:
    """
    Inventory chart of accounts.
    """

    INVENTORY = "112"
    GR_IR = "111"


@dataclass(slots=True, frozen=True)
class InventoryReceiptRequest:
    """
    Input data for inventory receipt.
    """

    company_code: str
    cost_center_code: str
    department_code: str
    currency_code: str

    material_code: str
    material_name: str

    warehouse_code: str
    storage_location: str

    receipt_date: date

    quantity: Decimal
    unit_price: Decimal
    total_amount: Decimal

    supplier_code: str | None = None

    description: str = ""


class InventoryReceiptScenario(AccountingScenario):
    """
    Generates accounting entries for inventory receipt.
    """

    def create(
        self,
        request: InventoryReceiptRequest,
    ) -> JournalEntry:

        document = self.document_generator.create(
            document_type=DocumentType.GR,
            posting_date=request.receipt_date,
            document_date=request.receipt_date,
            due_date=request.receipt_date,
        )

        entry = JournalEntry(document=document)

        # Dr 112000 - Inventory
        entry.add_line(
            JournalLine(
                line_number=1,
                account_number=InventoryAccounts.INVENTORY,
                company_code=request.company_code,
                cost_center_code=request.cost_center_code,
                department_code=request.department_code,
                currency_code=request.currency_code,
                supplier_code=request.supplier_code,
                inventory_item_code=request.material_code,
                debit_amount=request.total_amount,
                credit_amount=Decimal("0.00"),
                amount_local=request.total_amount,
                description=(
                    f"Inventory receipt - {request.material_name}"
                ),
            )
        )

        # Cr 111000 - GR/IR clearing
        entry.add_line(
            JournalLine(
                line_number=2,
                account_number=InventoryAccounts.GR_IR,
                company_code=request.company_code,
                cost_center_code=request.cost_center_code,
                department_code=request.department_code,
                currency_code=request.currency_code,
                supplier_code=request.supplier_code,
                inventory_item_code=request.material_code,
                debit_amount=Decimal("0.00"),
                credit_amount=request.total_amount,
                amount_local=request.total_amount,
                description="GR/IR clearing",
            )
        )

        return self.validate(entry)