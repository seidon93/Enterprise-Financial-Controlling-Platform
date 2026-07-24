"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : asset_capitalization.py
Object Type     : Asset Capitalization Scenario
Layer           : ETL
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Generates accounting entries for capitalization of fixed assets.
===============================================================================
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from accounting.asset_accounts import AssetAccounts
from accounting.enums import DocumentType
from accounting.models import JournalEntry, JournalLine
from scenarios.base import AccountingScenario

@dataclass(slots=True, frozen=True)
class AssetCapitalizationRequest:
    """
    Input data for asset capitalization.
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


class AssetCapitalizationScenario(AccountingScenario):
    """
    Generates accounting entries for capitalization of fixed assets.
    """

    def create(
        self,
        request: AssetCapitalizationRequest,
    ) -> JournalEntry:

        document = self.document_generator.create(
            document_type=DocumentType.FA,
            posting_date=request.acquisition_date,
            document_date=request.acquisition_date,
            due_date=request.acquisition_date,
        )

        entry = JournalEntry(document=document)

        # Fixed Asset (022)
        entry.add_line(
            JournalLine(
                line_number=1,
                account_number=AssetAccounts.FIXED_ASSETS,
                company_code=request.company_code,
                cost_center_code=request.cost_center_code,
                department_code=request.department_code,
                currency_code=request.currency_code,
                asset_code=request.asset_code,
                debit_amount=request.acquisition_cost,
                credit_amount=Decimal("0.00"),
                amount_local=request.acquisition_cost,
                description="Asset Capitalization",
            )
        )

        # Asset in Progress (042)
        entry.add_line(
            JournalLine(
                line_number=2,
                account_number=AssetAccounts.ASSET_IN_PROGRESS,
                company_code=request.company_code,
                cost_center_code=request.cost_center_code,
                department_code=request.department_code,
                currency_code=request.currency_code,
                asset_code=request.asset_code,
                debit_amount=Decimal("0.00"),
                credit_amount=request.acquisition_cost,
                amount_local=request.acquisition_cost,
                description="Transfer from Asset in Progress",
            )
        )

        return self.validate(entry)