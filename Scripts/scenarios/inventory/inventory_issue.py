"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : inventory_issue.py
Object Type     : Inventory Issue Scenario
Layer           : Accounting Scenario
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Generates accounting entries for inventory issue.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from datetime import date
from accounting.models import (
    JournalEntry,
    JournalLine,
)

from accounting.document_generator import DocumentGenerator
from accounting.enums import DocumentType


@dataclass(slots=True)
class InventoryIssueRequest:

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


class InventoryIssueScenario:
    """
    Inventory issue accounting scenario.
    """

    def __init__(
        self,
        document_generator: DocumentGenerator,
    ) -> None:

        self.document_generator = document_generator

    def create(
        self,
        request: InventoryIssueRequest,
    ) -> JournalEntry:

        amount = (
            request.quantity
            * request.unit_cost
        )

        document = self.document_generator.create(
            document_type=DocumentType.GI,
            posting_date=request.event_date,
            document_date=request.event_date,
            due_date=request.event_date,
            
        )

        lines = [

            JournalLine(

                line_number=1,

                company_code=request.company_code,

                account_number="501",

                debit_amount=amount,

                credit_amount=Decimal("0.00"),

                amount_local=amount,

                currency_code=request.currency_code,

                cost_center_code=request.cost_center_code,

                department_code=request.department_code,

                customer_code=None,

                supplier_code=None,

                asset_code=None,

                description=request.description,

            ),

            JournalLine(

                line_number=2,

                company_code=request.company_code,

                account_number="112",

                debit_amount=Decimal("0.00"),

                credit_amount=amount,

                amount_local=amount,

                currency_code=request.currency_code,

                cost_center_code=request.cost_center_code,

                department_code=request.department_code,

                customer_code=None,

                supplier_code=None,

                asset_code=None,

                description=request.description,

            ),

        ]

        return JournalEntry(
            document=document,
            lines=lines,
        )