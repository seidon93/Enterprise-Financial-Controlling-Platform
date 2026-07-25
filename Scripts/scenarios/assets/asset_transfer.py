"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : asset_transfer.py
Object Type     : Asset Transfer Scenario
Layer           : Accounting
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Transfers a fixed asset between organizational units.
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
class AssetTransferRequest:
    """
    Input data for asset transfer.
    """

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

    transfer_date: date

    asset_value: Decimal

    from_cost_center_code: str | None = None
    from_department_code: str | None = None
    to_cost_center_code: str | None = None
    to_department_code: str | None = None

    description: str = "Asset Transfer"


class AssetTransferScenario(AccountingScenario):
    """
    Generates accounting document for asset transfer.
    """

    def create(
        self,
        request: AssetTransferRequest,
    ) -> JournalEntry:

        document = self.document_generator.create(
            document_type=DocumentType.AT,
            posting_date=request.transfer_date,
            document_date=request.transfer_date,
            due_date=request.transfer_date,
        )

        entry = JournalEntry(
            document=document
        )

        # Source Cost Center

        entry.add_line(

            JournalLine(

                line_number=1,

                account_number="022",

                company_code=request.company_code,

                cost_center_code=request.from_cost_center_code,

                department_code=request.from_department_code,

                currency_code=request.currency_code,

                debit_amount=Decimal("0.00"),

                credit_amount=request.asset_value,

                amount_local=request.asset_value,

                description=f"Transfer OUT - {request.asset_code}",
            )
        )

        # Target Cost Center

        entry.add_line(

            JournalLine(

                line_number=2,

                account_number="022",

                company_code=request.company_code,

                cost_center_code=request.to_cost_center_code,

                department_code=request.to_department_code,

                currency_code=request.currency_code,

                debit_amount=request.asset_value,

                credit_amount=Decimal("0.00"),

                amount_local=request.asset_value,

                description=f"Transfer IN - {request.asset_code}",
            )
        )

        return self.validate(entry)