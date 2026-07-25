"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : business_event_generator.py
Object Type     : Business Event Generator
Layer           : Domain
Version         : 1.0.0
Status          : Development
===============================================================================
"""

from __future__ import annotations
from decimal import Decimal

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from domain.business_event import BusinessEvent
from domain.business_event_type import BusinessEventType
from domain.business_data_provider import BusinessDataProvider


class BusinessEventGenerator:
    """
    Generates business events from business transactions.
    """

    def __init__(
        self,
        provider: BusinessDataProvider,
    ) -> None:

        self.provider = provider

    def sales_event(self) -> BusinessEvent:
        """
        Generate one sales business event.
        """

        transaction = self.provider.create_sales_transaction()

        return BusinessEvent(
            event_type=BusinessEventType.SALES_INVOICE,
            company_code=transaction.company_code,
            event_date=transaction.invoice_date,
            amount=transaction.amount,
            currency_code=transaction.currency_code,
            description=transaction.description,
            cost_center_code=transaction.cost_center_code,
            department_code=transaction.department_code,
            vat_rate=transaction.vat_rate,
            due_date=transaction.due_date,
            customer_code=transaction.customer_code,
        )

    def purchase_event(self) -> BusinessEvent:
        """
        Generate one purchase business event.
        """

        transaction = self.provider.create_purchase_transaction()

        return BusinessEvent(
            event_type=BusinessEventType.PURCHASE_INVOICE,
            company_code=transaction.company_code,
            event_date=transaction.invoice_date,
            amount=transaction.amount,
            currency_code=transaction.currency_code,
            description=transaction.description,
            cost_center_code=transaction.cost_center_code,
            department_code=transaction.department_code,
            vat_rate=transaction.vat_rate,
            due_date=transaction.due_date,
            customer_code=None,
            supplier_code=transaction.supplier_code,
        )

    def customer_payment_event(self) -> BusinessEvent:
        """
        Generate one customer payment business event.
        """

        transaction = self.provider.create_customer_payment_transaction()

        return BusinessEvent(
            event_type=BusinessEventType.CUSTOMER_PAYMENT,
            company_code=transaction.company_code,
            event_date=transaction.invoice_date,
            amount=transaction.amount,
            currency_code=transaction.currency_code,
            description=transaction.description,
            cost_center_code=transaction.cost_center_code,
            department_code=transaction.department_code,
            vat_rate=transaction.vat_rate,
            due_date=transaction.due_date,
            customer_code=transaction.customer_code,
        )

  

    def supplier_payment_event(self) -> BusinessEvent:
        """
        Generate one supplier payment business event.
        """

        transaction = self.provider.create_supplier_payment_transaction()

        return BusinessEvent(
            event_type=BusinessEventType.SUPPLIER_PAYMENT,
            company_code=transaction.company_code,
            event_date=transaction.invoice_date,
            amount=transaction.amount,
            currency_code=transaction.currency_code,
            description=transaction.description,
            cost_center_code=transaction.cost_center_code,
            department_code=transaction.department_code,
            vat_rate=transaction.vat_rate,
            due_date=transaction.due_date,
            customer_code=None,
            supplier_code=transaction.supplier_code,
            
        )

    # -------------------------------------------------------------------------
    # Asset Events
    # -------------------------------------------------------------------------

    def _asset_event(
        self,
        event_type: BusinessEventType,
        asset,
        description: str,
        amount: Decimal | None = None,
    ) -> BusinessEvent:
        """
        Helper: build a BusinessEvent from an Asset object.
        """

        return BusinessEvent(
            event_type=event_type,
            company_code=asset.company_code,
            event_date=asset.acquisition_date,
            amount=amount if amount is not None else asset.acquisition_cost,
            currency_code=asset.currency_code,
            description=description,
            cost_center_code=asset.cost_center_code,
            department_code=asset.department_code,
            vat_rate=asset.vat_rate,
            due_date=asset.acquisition_date,
            asset_code=asset.asset_code,
            asset_name=asset.asset_name,
            asset_class=asset.asset_class,
            asset_group=asset.asset_group,
            acquisition_cost=asset.acquisition_cost,
            capitalization_date=asset.capitalization_date,
            depreciation_start_date=asset.depreciation_start_date,
            useful_life_months=asset.useful_life_months,
            depreciation_method=asset.depreciation_method,
            residual_value=asset.residual_value,
            country_code=asset.country_code,
            city=asset.city,
            location=asset.location,
            supplier_code=asset.supplier_code,
        )

    def asset_acquisition_event(self) -> BusinessEvent:
        """
        Generate one asset acquisition business event.
        """

        asset = self.provider.create_asset_acquisition_transaction()

        return self._asset_event(
            event_type=BusinessEventType.ASSET_ACQUISITION,
            asset=asset,
            description="Asset Acquisition",
        )

    def asset_capitalization_event(self) -> BusinessEvent:
        """
        Generate one asset capitalization business event.
        """

        asset = self.provider.create_asset_capitalization_transaction()

        return self._asset_event(
            event_type=BusinessEventType.ASSET_CAPITALIZATION,
            asset=asset,
            description="Asset Capitalization",
        )

    def asset_depreciation_event(self) -> BusinessEvent:
        """
        Generate one asset depreciation business event.
        """

        asset = self.provider.create_asset_depreciation_transaction()

        monthly_depreciation = (
            (asset.acquisition_cost - asset.residual_value)
            / asset.useful_life_months
        ).quantize(Decimal("0.01"))

        return self._asset_event(
            event_type=BusinessEventType.ASSET_DEPRECIATION,
            asset=asset,
            description="Asset Depreciation",
            amount=monthly_depreciation,
        )

    def asset_impairment_event(self) -> BusinessEvent:
        """
        Generate one asset impairment business event.
        """

        asset = self.provider.create_asset_impairment_transaction()

        impairment_amount = (
            asset.acquisition_cost * Decimal("0.15")
        ).quantize(Decimal("0.01"))

        return self._asset_event(
            event_type=BusinessEventType.ASSET_IMPAIRMENT,
            asset=asset,
            description="Asset Impairment",
            amount=impairment_amount,
        )

    def asset_disposal_event(self) -> BusinessEvent:
        """
        Generate one asset disposal business event.
        """

        asset = self.provider.create_asset_disposal_transaction()

        return self._asset_event(
            event_type=BusinessEventType.ASSET_DISPOSAL,
            asset=asset,
            description="Asset Disposal",
        )

    def asset_sale_event(self) -> BusinessEvent:
        """
        Generate one asset sale business event.
        """

        asset, customer = self.provider.create_asset_sale_transaction()

        sale_amount = (
            asset.acquisition_cost * Decimal("0.40")
        ).quantize(Decimal("0.01"))

        event = self._asset_event(
            event_type=BusinessEventType.ASSET_SALE,
            asset=asset,
            description="Asset Sale",
            amount=sale_amount,
        )

        # Override customer_code from the returned customer object
        from dataclasses import replace
        return replace(event, customer_code=customer.customer_code)

    def asset_transfer_event(self) -> BusinessEvent:
        """
        Generate one asset transfer business event.
        """

        asset = self.provider.create_asset_transfer_transaction()

        return self._asset_event(
            event_type=BusinessEventType.ASSET_TRANSFER,
            asset=asset,
            description="Asset Transfer",
        )