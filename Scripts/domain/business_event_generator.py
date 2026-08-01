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

    # -------------------------------------------------------------------------
    # Inventory Events
    # -------------------------------------------------------------------------

    def _inventory_event(
        self,
        event_type: BusinessEventType,
        inventory,
        description: str,
    ) -> BusinessEvent:
        """
        Helper: build BusinessEvent from Inventory object.
        """

        unit_cost = getattr(inventory, "unit_cost", None)

        if unit_cost is None:
            unit_cost = getattr(inventory, "unit_price", Decimal("0"))

        total_amount = getattr(
            inventory,
            "total_amount",
            inventory.quantity * unit_cost,
        )

        return BusinessEvent(
            event_type=event_type,
            company_code=inventory.company_code,
            event_date=inventory.movement_date,
            amount=total_amount,
            currency_code=inventory.currency_code,
            description=description,
            cost_center_code=inventory.cost_center_code,
            department_code=inventory.department_code,
            vat_rate=Decimal("0"),
            due_date=inventory.movement_date,

            inventory_code=getattr(inventory, "inventory_code", None),

            material_code=inventory.material_code,
            material_name=inventory.material_name,

            warehouse_code=inventory.warehouse_code,
            storage_location=inventory.storage_location,

            quantity=inventory.quantity,
            unit_cost=unit_cost,

            supplier_code=inventory.supplier_code,
            customer_code=inventory.customer_code,

            source_warehouse=inventory.source_warehouse,
            target_warehouse=inventory.target_warehouse,

            country_code=inventory.country_code,
            city=inventory.city,
            location=inventory.location,
        )

# -------------------------------------------------------------------------
# Inventory Events
# -------------------------------------------------------------------------

    def inventory_receipt_event(self) -> BusinessEvent:
        """
        Generate one inventory receipt business event.
        """

        transaction = self.provider.create_inventory_receipt_transaction()

        return self._inventory_event(
            BusinessEventType.INVENTORY_RECEIPT,
            transaction,
            "Inventory Receipt",
        )


    def inventory_issue_event(self) -> BusinessEvent:
        """
        Generate one inventory issue business event.
        """

        transaction = self.provider.create_inventory_issue_transaction()

        return self._inventory_event(
            BusinessEventType.INVENTORY_ISSUE,
            transaction,
            "Inventory Issue",
        )


    def inventory_transfer_event(self) -> BusinessEvent:
        """
        Generate one inventory transfer business event.
        """

        transaction = self.provider.create_inventory_transfer_transaction()

        return self._inventory_event(
            BusinessEventType.INVENTORY_TRANSFER,
            transaction,
            "Inventory Transfer",
        )


    def inventory_adjustment_event(self) -> BusinessEvent:
        """
        Generate one inventory adjustment business event.
        """

        transaction = self.provider.create_inventory_adjustment_transaction()

        return self._inventory_event(
            BusinessEventType.INVENTORY_ADJUSTMENT,
            transaction,
            "Inventory Adjustment",
        )

    def _build_payroll_event(
        self,
        event_type: BusinessEventType,
        payroll,
        description: str,
    ) -> BusinessEvent:
        """
        Helper: build BusinessEvent from Payroll object.
        """

        return BusinessEvent(
            event_type=event_type,

            company_code=payroll.company_code,

            event_date=payroll.payroll_date,

            amount=payroll.gross_salary,

            currency_code=payroll.currency_code,

            description=description,

            cost_center_code=payroll.cost_center_code,

            department_code=payroll.department_code,

            vat_rate=Decimal("0"),

            due_date=payroll.payroll_date,

            employee_code=payroll.employee_code,

            gross_salary=payroll.gross_salary,

            employer_contribution=payroll.employer_contribution,

            employee_tax=payroll.employee_tax,

            bonus_amount=payroll.bonus_amount,

            overtime_amount=payroll.overtime_amount,

            vacation_accrual=payroll.vacation_accrual,

            payroll_date=payroll.payroll_date,

            payment_amount=payroll.gross_salary - payroll.employee_tax,
        )

    def payroll_expense_event(self) -> BusinessEvent:

        payroll = self.provider.create_payroll_transaction()

        return self._build_payroll_event(
            BusinessEventType.PAYROLL_EXPENSE,
            payroll,
            "Payroll Expense",
        )

    def employer_contribution_event(self) -> BusinessEvent:

        payroll = self.provider.create_payroll_transaction()

        return self._build_payroll_event(
            BusinessEventType.EMPLOYER_CONTRIBUTION,
            payroll,
            "Employer Contribution",
        )

    def payroll_payment_event(self) -> BusinessEvent:

        payroll = self.provider.create_payroll_transaction()

        return self._build_payroll_event(
            BusinessEventType.PAYROLL_PAYMENT,
            payroll,
            "Payroll Payment",
        )

    def payroll_tax_event(self) -> BusinessEvent:

        payroll = self.provider.create_payroll_transaction()

        return self._build_payroll_event(
            BusinessEventType.PAYROLL_TAX,
            payroll,
            "Payroll Tax",
        )

    def payroll_bonus_event(self) -> BusinessEvent:

        payroll = self.provider.create_payroll_transaction()

        return self._build_payroll_event(
            BusinessEventType.PAYROLL_BONUS,
            payroll,
            "Payroll Bonus",
        )

    def vacation_accrual_event(self) -> BusinessEvent:

        payroll = self.provider.create_payroll_transaction()

        return self._build_payroll_event(
            BusinessEventType.VACATION_ACCRUAL,
            payroll,
            "Vacation Accrual",
            )

    def overtime_event(self) -> BusinessEvent:

        payroll = self.provider.create_payroll_transaction()

        return self._build_payroll_event(
            BusinessEventType.OVERTIME,
            payroll,
            "Overtime",
            )

    def payroll_reversal_event(self) -> BusinessEvent:

        payroll = self.provider.create_payroll_transaction()

        return self._build_payroll_event(
            BusinessEventType.PAYROLL_REVERSAL,
            payroll,
            "Payroll Reversal",
            )

# -------------------------------------------------------------------------
# Bank Events
# -------------------------------------------------------------------------

    def _build_bank_event(
        self,
        event_type: BusinessEventType,
        transaction,
        description: str,
    ) -> BusinessEvent:
        """
        Helper: build BusinessEvent from BankTransaction.
        """

        return BusinessEvent(
            event_type=event_type,

            company_code=transaction.company_code,

            event_date=transaction.transaction_date,

            amount=transaction.amount,

            currency_code=transaction.currency_code,

            description=description,

            cost_center_code=transaction.cost_center_code,

            department_code=transaction.department_code,

            vat_rate=Decimal("0"),

            due_date=transaction.transaction_date,

            customer_code=transaction.customer_code,

            supplier_code=transaction.supplier_code,

            bank_account=transaction.bank_account,

            transaction_type=transaction.transaction_type,

            loan_term=transaction.loan_term,

            reference_number=transaction.reference_number,
        )


    def bank_fee_event(self) -> BusinessEvent:

        transaction = self.provider.create_bank_transaction()

        return self._build_bank_event(
            BusinessEventType.BANK_FEE,
            transaction,
            "Bank Fee",
        )


    def interest_income_event(self) -> BusinessEvent:

        transaction = self.provider.create_bank_transaction()

        return self._build_bank_event(
            BusinessEventType.INTEREST_INCOME,
            transaction,
            "Interest Income",
        )


    def interest_expense_event(self) -> BusinessEvent:

        transaction = self.provider.create_bank_transaction()

        return self._build_bank_event(
            BusinessEventType.INTEREST_EXPENSE,
            transaction,
            "Interest Expense",
        )


    def fx_gain_event(self) -> BusinessEvent:

        transaction = self.provider.create_bank_transaction()

        return self._build_bank_event(
            BusinessEventType.FX_GAIN,
            transaction,
            "Foreign Exchange Gain",
        )


    def fx_loss_event(self) -> BusinessEvent:

        transaction = self.provider.create_bank_transaction()

        return self._build_bank_event(
            BusinessEventType.FX_LOSS,
            transaction,
            "Foreign Exchange Loss",
        )


    def loan_drawdown_event(self) -> BusinessEvent:

        transaction = self.provider.create_bank_transaction()

        return self._build_bank_event(
            BusinessEventType.LOAN_DRAWDOWN,
            transaction,
            "Loan Drawdown",
        )


    def loan_repayment_event(self) -> BusinessEvent:

        transaction = self.provider.create_bank_transaction()

        return self._build_bank_event(
            BusinessEventType.LOAN_REPAYMENT,
            transaction,
            "Loan Repayment",
        )


    def cash_deposit_event(self) -> BusinessEvent:

        transaction = self.provider.create_bank_transaction()

        return self._build_bank_event(
            BusinessEventType.CASH_DEPOSIT,
            transaction,
            "Cash Deposit",
        )


    def cash_withdrawal_event(self) -> BusinessEvent:

        transaction = self.provider.create_bank_transaction()

        return self._build_bank_event(
            BusinessEventType.CASH_WITHDRAWAL,
            transaction,
            "Cash Withdrawal",
        )


    def internal_transfer_event(self) -> BusinessEvent:

        transaction = self.provider.create_bank_transaction()

        return self._build_bank_event(
            BusinessEventType.INTERNAL_TRANSFER,
            transaction,
            "Internal Transfer",
        )

    # -------------------------------------------------------------------------
# Closing Events
# -------------------------------------------------------------------------

    def _build_closing_event(
        self,
        event_type: BusinessEventType,
        closing,
        description: str,
    ) -> BusinessEvent:
        """
        Helper: build BusinessEvent from ClosingTransaction.
        """

        return BusinessEvent(
            event_type=event_type,

            company_code=closing.company_code,

            event_date=closing.closing_date,

            amount=closing.amount,

            currency_code=closing.currency_code,

            description=description,

            cost_center_code=closing.cost_center_code,

            department_code=closing.department_code,

            vat_rate=Decimal("0"),

            due_date=closing.closing_date,

            closing_type=closing.closing_type,
        )

    def accrual_event(self) -> BusinessEvent:

        closing = self.provider.create_closing_transaction()

        return self._build_closing_event(
            BusinessEventType.ACCRUAL,
            closing,
            "Accrual",
        )


    def deferral_event(self) -> BusinessEvent:

        closing = self.provider.create_closing_transaction()

        return self._build_closing_event(
            BusinessEventType.DEFERRAL,
            closing,
            "Deferral",
        )


    def provision_event(self) -> BusinessEvent:

        closing = self.provider.create_closing_transaction()

        return self._build_closing_event(
            BusinessEventType.PROVISION,
            closing,
            "Provision",
        )


    def fx_revaluation_event(self) -> BusinessEvent:

        closing = self.provider.create_closing_transaction()

        return self._build_closing_event(
            BusinessEventType.FX_REVALUATION,
            closing,
            "FX Revaluation",
        )


    def year_end_event(self) -> BusinessEvent:

        closing = self.provider.create_closing_transaction()

        return self._build_closing_event(
            BusinessEventType.YEAR_END,
            closing,
            "Year End Closing",
        )


    def period_close_event(self) -> BusinessEvent:

        closing = self.provider.create_closing_transaction()

        return self._build_closing_event(
            BusinessEventType.PERIOD_CLOSE,
            closing,
            "Period Close",
        )

# -------------------------------------------------------------------------
# Closing Events
# -------------------------------------------------------------------------

    def _build_closing_event(
        self,
        event_type: BusinessEventType,
        transaction,
        description: str,
    ) -> BusinessEvent:
        """
        Helper: build BusinessEvent from ClosingTransaction.
        """

        return BusinessEvent(

            event_type=event_type,

            company_code=transaction.company_code,

            event_date=transaction.closing_date,

            amount=transaction.amount,

            currency_code=transaction.currency_code,

            description=description,

            cost_center_code=transaction.cost_center_code,

            department_code=transaction.department_code,

            vat_rate=Decimal(0),

            due_date=transaction.closing_date,

            expense_account=transaction.expense_account,

            revenue_account=transaction.revenue_account,

            balance_account=transaction.balance_account,

            provision_account=transaction.provision_account,

            inventory_account=transaction.inventory_account,

            allowance_account=transaction.allowance_account,
        )


    def accrued_expense_event(self) -> BusinessEvent:

        transaction = self.provider.create_closing_transaction()

        return self._build_closing_event(
            BusinessEventType.ACCRUED_EXPENSE,
            transaction,
            "Accrued Expense",
        )
    def accrued_revenue_event(self) -> BusinessEvent:

        transaction = self.provider.create_closing_transaction()

        return self._build_closing_event(
            BusinessEventType.ACCRUED_REVENUE,
            transaction,
            "Accrued Revenue",
        )

    def prepaid_expense_event(self) -> BusinessEvent:

        transaction = self.provider.create_closing_transaction()

        return self._build_closing_event(
            BusinessEventType.PREPAID_EXPENSE,
            transaction,
            "Prepaid Expense",
        )

    def deferred_revenue_event(self) -> BusinessEvent:

        transaction = self.provider.create_closing_transaction()

        return self._build_closing_event(
            BusinessEventType.DEFERRED_REVENUE,
            transaction,
            "Deferred Revenue",
        )

    def provision_event(
        self,
    ) -> BusinessEvent:

        transaction = self.provider.create_provision_transaction()

        return self._build_closing_event(
            BusinessEventType.PROVISION,
            transaction,
            "Provision",
        )

    def inventory_writeoff_event(
        self,
    ) -> BusinessEvent:

        transaction = self.provider.create_inventory_writeoff_transaction()

        return self._build_closing_event(
            BusinessEventType.INVENTORY_WRITEOFF,
            transaction,
            "Inventory Write-off",
        )

    def inventory_revaluation_event(
        self,
    ) -> BusinessEvent:

        transaction = (
            self.provider.create_inventory_revaluation_transaction()
        )

        return self._build_closing_event(

            BusinessEventType.INVENTORY_REVALUATION,

            transaction,

            "Inventory Revaluation",
        )

    def bad_debt_allowance_event(
        self,
    ) -> BusinessEvent:

        transaction = (
            self.provider.create_bad_debt_allowance_transaction()
        )

        return self._build_closing_event(

            BusinessEventType.BAD_DEBT_ALLOWANCE,

            transaction,

            "Bad Debt Allowance",
        )