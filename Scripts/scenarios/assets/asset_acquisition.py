"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : asset_acquisition.py
Object Type     : Asset Acquisition Scenario
Layer           : ETL
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Generates accounting entries for acquisition of fixed assets.
===============================================================================
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from accounting.asset_accounts import AssetAccounts
from accounting.enums import DocumentType
from accounting.models import JournalEntry, JournalLine
from scenarios.base import AccountingScenario


@dataclass(slots=True, frozen=True)
class AssetAcquisitionRequest:
    """
    Input data for fixed asset acquisition.
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


class AssetAcquisitionScenario(AccountingScenario):
    """
    Generates accounting entries for fixed asset acquisition.
    """

    def create(
        self,
        request: AssetAcquisitionRequest,
    ) -> JournalEntry:

        vat_amount = (
            request.acquisition_cost * request.vat_rate
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        total_amount = request.acquisition_cost + vat_amount

        document = self.document_generator.create(
            document_type=DocumentType.FA,
            posting_date=request.acquisition_date,
            document_date=request.acquisition_date,
            due_date=request.acquisition_date,
        )

        entry = JournalEntry(document=document)

        # Asset in Progress (042)
        entry.add_line(
            JournalLine(
                line_number=1,
                account_number=AssetAccounts.ASSET_IN_PROGRESS,
                company_code=request.company_code,
                cost_center_code=request.cost_center_code,
                department_code=request.department_code,
                currency_code=request.currency_code,
                supplier_code=request.supplier_code,
                debit_amount=request.acquisition_cost,
                credit_amount=Decimal("0.00"),
                amount_local=request.acquisition_cost,
                description="Fixed Asset Acquisition",
                asset_code=request.asset_code
            )
        )

        # Input VAT (343)
        entry.add_line(
            JournalLine(
                line_number=2,
                account_number=AssetAccounts.INPUT_VAT,
                company_code=request.company_code,
                cost_center_code=request.cost_center_code,
                department_code=request.department_code,
                currency_code=request.currency_code,
                supplier_code=request.supplier_code,
                debit_amount=vat_amount,
                credit_amount=Decimal("0.00"),
                amount_local=vat_amount,
                description="Input VAT",
                asset_code=request.asset_code
            )
        )

        # Trade Payables (321)
        entry.add_line(
            JournalLine(
                line_number=3,
                account_number=AssetAccounts.TRADE_PAYABLES,
                company_code=request.company_code,
                cost_center_code=request.cost_center_code,
                department_code=request.department_code,
                currency_code=request.currency_code,
                supplier_code=request.supplier_code,
                debit_amount=Decimal("0.00"),
                credit_amount=total_amount,
                amount_local=total_amount,
                description="Supplier Liability",
                asset_code=request.asset_code
            )
        )

        return self.validate(entry)