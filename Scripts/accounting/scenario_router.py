"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : scenario_router.py
Object Type     : Scenario Router
Layer           : Accounting
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Routes business events to accounting scenarios.
===============================================================================
"""


from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


from domain.business_event import BusinessEvent
from domain.business_event_type import BusinessEventType

from decimal import Decimal

from scenarios.sales_invoice import (
    SalesInvoiceRequest,
    SalesInvoiceScenario,
)

from scenarios.purchase_invoice import (
    PurchaseInvoiceRequest,
    PurchaseInvoiceScenario,
)

from scenarios.customer_payment import (
    CustomerPaymentRequest,
    CustomerPaymentScenario,
)

from scenarios.supplier_payment import (
    SupplierPaymentRequest,
    SupplierPaymentScenario,
)

from scenarios.assets.asset_acquisition import (
    AssetAcquisitionRequest,
    AssetAcquisitionScenario,
)

from scenarios.assets.asset_capitalization import (
    AssetCapitalizationRequest,
    AssetCapitalizationScenario,
)

from scenarios.assets.asset_depreciation import (
    AssetDepreciationRequest,
    AssetDepreciationScenario,
)

from scenarios.assets.asset_impairment import (
    AssetImpairmentRequest,
    AssetImpairmentScenario,
)

from scenarios.assets.asset_disposal import (
    AssetDisposalRequest,
    AssetDisposalScenario,
)

from scenarios.assets.asset_sale import (
    AssetSaleRequest,
    AssetSaleScenario,
)

from scenarios.assets.asset_transfer import (
    AssetTransferRequest,
    AssetTransferScenario,
)

from scenarios.inventory.inventory_receipt import (
    InventoryReceiptRequest,
    InventoryReceiptScenario,
)

from scenarios.inventory.inventory_issue import (
    InventoryIssueRequest,
    InventoryIssueScenario,
)

from scenarios.inventory.inventory_transfer import (
    InventoryTransferRequest,
    InventoryTransferScenario,
)

from scenarios.inventory.inventory_adjustment import (
    InventoryAdjustmentRequest,
    InventoryAdjustmentScenario,
)

class ScenarioRouter:
    """
    Converts BusinessEvents into JournalEntries.
    """

    def __init__(
        self,
        sales_scenario: SalesInvoiceScenario,
        purchase_scenario: PurchaseInvoiceScenario,
        customer_payment_scenario: CustomerPaymentScenario,
        supplier_payment_scenario: SupplierPaymentScenario,
        asset_acquisition_scenario: AssetAcquisitionScenario,
        asset_capitalization_scenario: AssetCapitalizationScenario,
        asset_depreciation_scenario: AssetDepreciationScenario,
        asset_impairment_scenario: AssetImpairmentScenario,
        asset_disposal_scenario: AssetDisposalScenario,
        asset_sale_scenario: AssetSaleScenario,
        asset_transfer_scenario: AssetTransferScenario,
        inventory_receipt_scenario: InventoryReceiptScenario,
        inventory_issue_scenario: InventoryIssueScenario,
        inventory_transfer_scenario: InventoryTransferScenario,
        inventory_adjustment_scenario: InventoryAdjustmentScenario,
    ) -> None:

        self.sales_scenario = sales_scenario
        self.purchase_scenario = purchase_scenario
        self.customer_payment_scenario = customer_payment_scenario
        self.supplier_payment_scenario = supplier_payment_scenario
        self.asset_acquisition_scenario = asset_acquisition_scenario
        self.asset_capitalization_scenario = asset_capitalization_scenario
        self.asset_depreciation_scenario = asset_depreciation_scenario
        self.asset_impairment_scenario = asset_impairment_scenario
        self.asset_disposal_scenario = asset_disposal_scenario
        self.asset_sale_scenario = asset_sale_scenario
        self.asset_transfer_scenario = asset_transfer_scenario
        self.inventory_receipt_scenario = inventory_receipt_scenario
        self.inventory_issue_scenario = inventory_issue_scenario
        self.inventory_transfer_scenario = inventory_transfer_scenario
        self.inventory_adjustment_scenario = inventory_adjustment_scenario


    def process(
        self,
        event: BusinessEvent,
    ):

        match event.event_type:

            case BusinessEventType.SALES_INVOICE:

                request = SalesInvoiceRequest(
                    company_code=event.company_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                    currency_code=event.currency_code,
                    invoice_date=event.event_date,
                    due_date=event.due_date,
                    net_amount=event.amount,
                    vat_rate=event.vat_rate,
                    description=event.description,
                    customer_code=event.customer_code,
                )

                return self.sales_scenario.create(request)

            case BusinessEventType.PURCHASE_INVOICE:
                request = PurchaseInvoiceRequest(
                    company_code=event.company_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                    currency_code=event.currency_code,
                    invoice_date=event.event_date,
                    due_date=event.due_date,
                    net_amount=event.amount,
                    vat_rate=event.vat_rate,
                    description=event.description,
                    supplier_code=event.supplier_code,
                )
                return self.purchase_scenario.create(request)

            case BusinessEventType.CUSTOMER_PAYMENT:

                request = CustomerPaymentRequest(
                    company_code=event.company_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                    currency_code=event.currency_code,
                    payment_date=event.event_date,
                    payment_amount=event.amount,
                    description=event.description,
                    customer_code=event.customer_code,
                )

                return self.customer_payment_scenario.create(request)

            case BusinessEventType.SUPPLIER_PAYMENT:
                request = SupplierPaymentRequest(
                    company_code=event.company_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                    currency_code=event.currency_code,
                    supplier_code=event.supplier_code,
                    payment_date=event.event_date,
                    payment_amount=event.amount,
                    description=event.description,
                )

                return self.supplier_payment_scenario.create(request)

            case BusinessEventType.ASSET_ACQUISITION:

                request = AssetAcquisitionRequest(
                    company_code=event.company_code,
                    asset_code=event.asset_code,
                    asset_name=event.asset_name,
                    asset_class=event.asset_class,
                    asset_group=event.asset_group,
                    supplier_code=event.supplier_code,
                    acquisition_date=event.event_date,
                    acquisition_cost=event.acquisition_cost,
                    vat_rate=event.vat_rate,
                    useful_life_months=event.useful_life_months,
                    depreciation_method=event.depreciation_method,
                    residual_value=event.residual_value,
                    currency_code=event.currency_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                )

                return self.asset_acquisition_scenario.create(request)

            case BusinessEventType.ASSET_CAPITALIZATION:

                request = AssetCapitalizationRequest(
                    company_code=event.company_code,
                    asset_code=event.asset_code,
                    asset_name=event.asset_name,
                    asset_class=event.asset_class,
                    asset_group=event.asset_group,
                    supplier_code=event.supplier_code,
                    acquisition_date=event.event_date,
                    acquisition_cost=event.acquisition_cost,
                    vat_rate=event.vat_rate,
                    useful_life_months=event.useful_life_months,
                    depreciation_method=event.depreciation_method,
                    residual_value=event.residual_value,
                    currency_code=event.currency_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                )

                return self.asset_capitalization_scenario.create(request)

            case BusinessEventType.ASSET_DEPRECIATION:

                request = AssetDepreciationRequest(
                    company_code=event.company_code,
                    asset_code=event.asset_code,
                    asset_name=event.asset_name,
                    asset_class=event.asset_class,
                    asset_group=event.asset_group,
                    supplier_code=event.supplier_code,
                    acquisition_date=event.event_date,
                    acquisition_cost=event.acquisition_cost,
                    vat_rate=event.vat_rate,
                    useful_life_months=event.useful_life_months,
                    depreciation_method=event.depreciation_method,
                    residual_value=event.residual_value,
                    currency_code=event.currency_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                    depreciation_date=event.event_date,
                    depreciation_amount=event.amount,
                )

                return self.asset_depreciation_scenario.create(request)

            case BusinessEventType.ASSET_IMPAIRMENT:

                request = AssetImpairmentRequest(
                    company_code=event.company_code,
                    asset_code=event.asset_code,
                    asset_name=event.asset_name,
                    asset_class=event.asset_class,
                    asset_group=event.asset_group,
                    supplier_code=event.supplier_code,
                    acquisition_date=event.event_date,
                    acquisition_cost=event.acquisition_cost,
                    vat_rate=event.vat_rate,
                    useful_life_months=event.useful_life_months,
                    depreciation_method=event.depreciation_method,
                    residual_value=event.residual_value,
                    currency_code=event.currency_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                    impairment_date=event.event_date,
                    impairment_amount=event.amount,
                )

                return self.asset_impairment_scenario.create(request)

            case BusinessEventType.ASSET_DISPOSAL:

                request = AssetDisposalRequest(
                    company_code=event.company_code,
                    asset_code=event.asset_code,
                    asset_name=event.asset_name,
                    asset_class=event.asset_class,
                    asset_group=event.asset_group,
                    supplier_code=event.supplier_code,
                    acquisition_date=event.event_date,
                    acquisition_cost=event.acquisition_cost,
                    vat_rate=event.vat_rate,
                    useful_life_months=event.useful_life_months,
                    depreciation_method=event.depreciation_method,
                    residual_value=event.residual_value,
                    currency_code=event.currency_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                    disposal_date=event.event_date,
                    net_book_value=event.amount,
                )

                return self.asset_disposal_scenario.create(request)

            case BusinessEventType.ASSET_SALE:

                request = AssetSaleRequest(
                    company_code=event.company_code,
                    asset_code=event.asset_code,
                    asset_name=event.asset_name,
                    asset_class=event.asset_class,
                    asset_group=event.asset_group,
                    supplier_code=event.supplier_code,
                    acquisition_date=event.event_date,
                    acquisition_cost=event.acquisition_cost,
                    vat_rate=event.vat_rate,
                    useful_life_months=event.useful_life_months,
                    depreciation_method=event.depreciation_method,
                    residual_value=event.residual_value,
                    currency_code=event.currency_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                    sale_date=event.event_date,
                    sale_amount=event.amount,
                    customer_code=event.customer_code,
                )

                return self.asset_sale_scenario.create(request)

            case BusinessEventType.ASSET_TRANSFER:

                request = AssetTransferRequest(
                    company_code=event.company_code,
                    asset_code=event.asset_code,
                    asset_name=event.asset_name,
                    asset_class=event.asset_class,
                    asset_group=event.asset_group,
                    supplier_code=event.supplier_code,
                    acquisition_date=event.event_date,
                    acquisition_cost=event.acquisition_cost,
                    vat_rate=event.vat_rate,
                    useful_life_months=event.useful_life_months,
                    depreciation_method=event.depreciation_method,
                    residual_value=event.residual_value,
                    currency_code=event.currency_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                    transfer_date=event.event_date,
                    asset_value=event.amount,
                    from_cost_center_code=event.cost_center_code,
                    from_department_code=event.department_code,
                    to_cost_center_code=event.cost_center_code,
                    to_department_code=event.department_code,
                )

                return self.asset_transfer_scenario.create(request)

            
            case BusinessEventType.INVENTORY_RECEIPT:

                request = InventoryReceiptRequest(
                company_code=event.company_code,
                cost_center_code=event.cost_center_code,
                department_code=event.department_code,
                currency_code=event.currency_code,

                material_code=event.material_code,
                material_name=event.material_name,

                warehouse_code=event.warehouse_code,
                storage_location=event.storage_location,

                receipt_date=event.event_date,

                quantity=event.quantity,
                unit_price=event.unit_price,
                total_amount=event.amount,

                supplier_code=event.supplier_code,
                description=event.description,
            )

                return self.inventory_receipt_scenario.create(request)


            case BusinessEventType.INVENTORY_ISSUE:

                request = InventoryIssueRequest(
                    company_code=event.company_code,
                    inventory_code=event.inventory_code,
                    material_code=event.material_code,
                    material_name=event.material_name,
                    event_date=event.event_date,
                    quantity=event.quantity,
                    unit_cost=event.unit_cost,
                    currency_code=event.currency_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                    description=event.description,
                )

                return self.inventory_issue_scenario.create(request)

            case BusinessEventType.INVENTORY_TRANSFER:

                request = InventoryTransferRequest(
                    company_code=event.company_code,
                    inventory_code=event.inventory_code,
                    material_code=event.material_code,
                    material_name=event.material_name,
                    event_date=event.event_date,
                    quantity=event.quantity,
                    unit_cost=event.unit_cost,
                    currency_code=event.currency_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                    from_cost_center_code=event.from_cost_center_code,
                    from_department_code=event.from_department_code,
                    to_cost_center_code=event.to_cost_center_code,
                    to_department_code=event.to_department_code,
                    description=event.description,
                )

                return self.inventory_transfer_scenario.create(request)

            case BusinessEventType.INVENTORY_ADJUSTMENT:

                request = InventoryAdjustmentRequest(
                    company_code=event.company_code,
                    inventory_code=event.inventory_code,
                    material_code=event.material_code,
                    material_name=event.material_name,
                    event_date=event.event_date,
                    quantity=event.quantity,
                    unit_cost=event.unit_cost,
                    currency_code=event.currency_code,
                    cost_center_code=event.cost_center_code,
                    department_code=event.department_code,
                    description=event.description,
                )

                return self.inventory_adjustment_scenario.create(request)


            case _:

                raise NotImplementedError(
                    f"Unsupported event: {event.event_type}"
                )
    