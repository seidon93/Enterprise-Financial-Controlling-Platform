"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : inventory_adjustment.py
Object Type     : Inventory Adjustment Scenario
Layer           : Accounting Scenario
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Generates accounting entries for inventory adjustments.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from accounting.models import (
    JournalEntry,
    JournalLine,
)

from accounting.document_generator import DocumentGenerator
from accounting.enums import DocumentType


@dataclass(slots=True)
class InventoryAdjustmentRequest:

    company_code: str

    inventory_code: str

    material_code: str

    material_name: str

    event_date: date

    quantity: Decimal

    unit_cost: Decimal

    currency_code: str

    cost_center_code: str

    department_code: str

    description: str


class InventoryAdjustmentScenario:
    """
    Inventory adjustment accounting scenario.
    """

    def __init__(
        self,
        document_generator: DocumentGenerator,
    ) -> None:

        self.document_generator = document_generator

    def create(
        self,
        request: InventoryAdjustmentRequest,
    ) -> JournalEntry:

        amount = request.quantity * request.unit_cost

        document = self.document_generator.create(
            document_type=DocumentType.IA,
            posting_date=request.event_date,
            document_date=request.event_date,
            due_date=request.event_date,
        )

        lines = [

            JournalLine(

                line_number=1,

                account_number="549",

                company_code=request.company_code,

                cost_center_code=request.cost_center_code,

                department_code=request.department_code,

                currency_code=request.currency_code,

                debit_amount=amount,

                credit_amount=Decimal("0.00"),

                amount_local=amount,

                description=request.description,

                customer_code=None,

                supplier_code=None,

                asset_code=None,

                product_code=request.material_code,

                inventory_item_code=request.inventory_code,
            ),

            JournalLine(

                line_number=2,

                account_number="112",

                company_code=request.company_code,

                cost_center_code=request.cost_center_code,

                department_code=request.department_code,

                currency_code=request.currency_code,

                debit_amount=Decimal("0.00"),

                credit_amount=amount,

                amount_local=amount,

                description=request.description,

                customer_code=None,

                supplier_code=None,

                asset_code=None,

                product_code=request.material_code,

                inventory_item_code=request.inventory_code,
            ),

        ]

        return JournalEntry(
            document=document,
            lines=lines,
        )