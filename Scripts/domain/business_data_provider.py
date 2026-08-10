"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : business_data_provider.py
Object Type     : Business Data Provider
Layer           : Domain
Version         : 1.0.0
Status          : Development
===============================================================================
"""


from __future__ import annotations
from domain import customer_provider

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from domain.company_profile import CompanyProfile
from datetime import date, timedelta
from decimal import Decimal
import random

from domain.business_transaction import BusinessTransaction
from domain.business_calendar import BusinessCalendar

from domain.customer_provider import CustomerProvider
from domain.supplier_provider import SupplierProvider
from scenarios.assets.asset_provider import AssetProvider

from scenarios.inventory.inventory import Inventory
from domain.payroll import Payroll

from domain.bank_transaction import BankTransaction
from domain.closing_transaction import ClosingTransaction

class BusinessDataProvider:
    """
    Provides realistic enterprise business data.
    """

    def __init__(self, seed: int = 42):

        self.random = random.Random(seed)
        self.calendar = BusinessCalendar(
            start_date=date(2021, 1, 1),
            end_date=date(2026, 8, 10),
            seed=seed,
        )
        self.supplier_provider = SupplierProvider(seed)
        self.customer_provider = CustomerProvider(seed)
        self.asset_provider = AssetProvider(seed)


        self.company_profiles = [

            CompanyProfile(
                company_code="CZ001",
                currency_code="CZK",
                growth_factor=1.10,
                sales_weight=0.45,
                active_from=2021,
                active_to=2035,
            ),

            CompanyProfile(
                company_code="SK001",
                currency_code="EUR",
                growth_factor=1.07,
                sales_weight=0.20,
                active_from=2021,
                active_to=2035,
            ),

            CompanyProfile(
                company_code="DE001",
                currency_code="EUR",
                growth_factor=1.18,
                sales_weight=0.15,
                active_from=2022,
                active_to=2035,
            ),

            CompanyProfile(
                company_code="AT001",
                currency_code="EUR",
                growth_factor=1.05,
                sales_weight=0.10,
                active_from=2023,
                active_to=2035,
            ),

            CompanyProfile(
                company_code="PL001",
                currency_code="PLN",
                growth_factor=1.12,
                sales_weight=0.10,
                active_from=2024,
                active_to=2035,
            ),
        ]

        self.material_codes = [
            "MAT-1001",
            "MAT-1002",
            "MAT-1003",
            "MAT-1004",
            "MAT-1005",
        ]

        self.material_names = [
            "Steel Plate",
            "Electric Motor",
            "Bearing",
            "Copper Cable",
            "Hydraulic Pump",
        ]

        self.warehouses = [
            "WH01",
            "WH02",
            "WH03",
        ]

        self.storage_locations = [
            "A-01",
            "A-02",
            "B-01",
            "B-02",
            "C-01",
        ]

    def random_company(self) -> CompanyProfile:
        """
        Returns one company according to business weights.
        """

        return self.random.choices(
            self.company_profiles,
            weights=[c.sales_weight for c in self.company_profiles],
            k=1,
        )[0]

    def random_due_date(self, invoice_date: date) -> date:
        """
            Generate invoice due date.
        """

        payment_terms = self.random.choice([14, 30, 45, 60])

        return invoice_date + timedelta(days=payment_terms)

    def random_vat_rate(self) -> Decimal:
        """
        Returns VAT rate.
        """

        return Decimal("0.21")

    def create_sales_transaction(self) -> BusinessTransaction:
        """
        Create business transaction for Sales Invoice.

        Sales transactions contain product-level commercial drivers so that
        downstream controller analytics can calculate Price / Volume / Mix
        effects from transactional data.
        """

        company = self.random_company()

        invoice_date = self.random_invoice_date()
        customer = self.customer_provider.random_customer()

        material_code = self.random.choice(
            self.material_codes
        )

        quantity = Decimal(
            str(self.random.randint(1, 100))
        )

        unit_price = Decimal(
            str(
                round(
                    self.random.uniform(10, 500),
                    2,
                )
            )
        )

        amount = (
            quantity * unit_price
        ).quantize(
            Decimal("0.01")
        )

        return BusinessTransaction(
            company_code=company.company_code,
            cost_center_code=self.random_cost_center(),
            department_code=self.random_department(),
            currency_code=company.currency_code,
            invoice_date=invoice_date,
            due_date=self.random_due_date(invoice_date),
            amount=amount,
            vat_rate=self.random_vat_rate(),
            description="Sales Invoice",
            material_code=material_code,
            quantity=quantity,
            unit_price=unit_price,
            customer_code=customer.customer_code,
        )


    def create_purchase_transaction(self) -> BusinessTransaction:
        """
        Create business transaction for Purchase Invoice.
        """

        company = self.random_company()

        invoice_date = self.random_invoice_date()

        supplier = self.supplier_provider.random_supplier()

        return BusinessTransaction(
            company_code=company.company_code,
            cost_center_code=self.random_cost_center(),
            department_code=self.random_department(),
            currency_code=company.currency_code,
            invoice_date=invoice_date,
            due_date=self.random_due_date(invoice_date),
            amount=self.random_invoice_amount(company),
            vat_rate=self.random_vat_rate(),
            description="Purchase Invoice",
            supplier_code=supplier.supplier_code,
        )


    def create_customer_payment_transaction(self) -> BusinessTransaction:
        """
        Create business transaction for Customer Payment.
        """

        company = self.random_company()

        payment_date = self.random_invoice_date()

        customer = self.customer_provider.random_customer()

        return BusinessTransaction(
            company_code=company.company_code,
            cost_center_code=self.random_cost_center(),
            department_code=self.random_department(),
            currency_code=company.currency_code,
            invoice_date=payment_date,
            due_date=payment_date,
            amount=self.random_invoice_amount(company),
            vat_rate=Decimal("0.00"),
            description="Customer Payment",
            customer_code=customer.customer_code,
        )

    def create_supplier_payment_transaction(self) -> BusinessTransaction:
        """
        Create business transaction for Supplier Payment.
        """

        company = self.random_company()

        payment_date = self.random_invoice_date()

        supplier = self.supplier_provider.random_supplier()

        return BusinessTransaction(
            company_code=company.company_code,
            cost_center_code=self.random_cost_center(),
            department_code=self.random_department(),
            currency_code=company.currency_code,
            invoice_date=payment_date,
            due_date=payment_date,
            amount=self.random_invoice_amount(company),
            vat_rate=Decimal("0.00"),
            description="Supplier Payment",
            supplier_code=supplier.supplier_code,
        )

    def random_invoice_date(self) -> date:
        """
        Returns a random business invoice date.
        """
        return self.calendar.random_business_date()

    def random_cost_center(self) -> str:
        """
        Returns random cost center.
        """

        return self.random.choice(
            [
                "1000",
                "1100",
                "1200",
                "2000",
                "2100",
                "2200",
                "3000",
                "3100",
                "3200",
                "3300",
                "4000",
                "4100",
                "4200",
                "5000",
            ]
        )

    def random_department(self) -> str:
        """
        Returns random department.
        """

        return self.random.choice(
            [
                "FIN",
                "ACC",
                "CTR",
                "SAL",
                "MKT",
                "PRD",
                "LOG",
                "PUR",
                "IT",
                "HR",
                "EXE",
            ]
        )

    def random_invoice_amount(
        self,
        company: CompanyProfile,
    ) -> Decimal:
        """
        Returns realistic invoice amount.
        """

        base = Decimal("50000")

        amount = float(base) * self.random.uniform(0.5, 1.5)

        amount *= company.growth_factor

        return Decimal(str(round(amount, 2)))

    def create_asset_acquisition_transaction(
        self,
    ):
        """
        Create business transaction for asset acquisition.
        """

        asset = self.asset_provider.random_asset()

        return asset

    def create_asset_capitalization_transaction(
        self,
    ):
        """
        Create business transaction for asset capitalization.
        """

        asset = self.asset_provider.random_asset()

        return asset

    def create_asset_depreciation_transaction(
        self,
    ):
        """
        Create business transaction for monthly depreciation.
        """

        asset = self.asset_provider.random_asset()

        return asset

    def create_asset_transfer_transaction(
        self,
    ):
        """
        Create business transaction for asset transfer.
        """

        asset = self.asset_provider.random_asset()

        return asset

    def create_asset_impairment_transaction(
        self,
    ):
        """
        Create business transaction for asset impairment.
        """

        asset = self.asset_provider.random_asset()

        return asset

        
    def create_asset_disposal_transaction(
        self,
    ):
        """
        Create business transaction for asset disposal.
        """

        asset = self.asset_provider.random_asset()

        return asset

    def create_asset_sale_transaction(
        self,
    ):
        """
        Create business transaction for asset sale.
        """

        asset = self.asset_provider.random_asset()

        customer = self.customer_provider.random_customer()

        return asset, customer

    def create_inventory_transaction(
        self,
    ) -> Inventory:
        """
        Create one inventory transaction.
        """

        company = self.random_company()

        quantity = Decimal(str(self.random.randint(1, 100)))

        unit_price = Decimal(
            str(round(self.random.uniform(10, 500), 2))
        )

        total_amount = (quantity * unit_price).quantize(
            Decimal("0.01")
        )

        material_index = self.random.randint(
            0,
            len(self.material_codes) - 1,
        )

        supplier = self.supplier_provider.random_supplier()
        customer = self.customer_provider.random_customer()

        inventory_code = f"INV-{self.random.randint(10000, 99999)}"

        return Inventory(

            company_code=company.company_code,

            material_code=self.material_codes[material_index],

            material_name=self.material_names[material_index],

            warehouse_code=self.random.choice(
                self.warehouses
            ),

            storage_location=self.random.choice(
                self.storage_locations
            ),

            movement_date=self.random_invoice_date(),

            quantity=quantity,

            unit_price=unit_price,

            total_amount=total_amount,

            currency_code=company.currency_code,

            cost_center_code=self.random_cost_center(),

            department_code=self.random_department(),

            inventory_code=inventory_code,

            supplier_code=supplier.supplier_code,

            customer_code=customer.customer_code,

            source_warehouse=self.random.choice(
                self.warehouses
            ),

            target_warehouse=self.random.choice(
                self.warehouses
            ),

            country_code="CZ",

            city="Brno",

            location="Main Warehouse",
        )

# -------------------------------------------------------------------------
# Inventory Transactions
# -------------------------------------------------------------------------

    def create_inventory_receipt_transaction(
        self,
    ) -> Inventory:
        """
        Create inventory receipt transaction.
        """
        return self.create_inventory_transaction()


    def create_inventory_issue_transaction(
        self,
    ) -> Inventory:
        """
        Create inventory issue transaction.
        """
        return self.create_inventory_transaction()


    def create_inventory_transfer_transaction(
        self,
    ) -> Inventory:
        """
        Create inventory transfer transaction.
        """
        return self.create_inventory_transaction()


    def create_inventory_adjustment_transaction(
        self,
    ) -> Inventory:
        """
        Create inventory adjustment transaction.
        """
        return self.create_inventory_transaction()

    def create_payroll_transaction(
        self,
    ) -> Payroll:
        """
        Generate one payroll transaction.
        """

        gross_salary = Decimal(
            str(
                round(
                    self.random.uniform(28000, 95000),
                    2,
                )
            )
        )

        employer_contribution = (
            gross_salary * Decimal("0.338")
        ).quantize(Decimal("0.01"))

        employee_tax = (
            gross_salary * Decimal("0.15")
        ).quantize(Decimal("0.01"))

        bonus_amount = Decimal(
            str(
                round(
                    self.random.uniform(0, 12000),
                    2,
                )
            )
        )

        overtime_amount = Decimal(
            str(
                round(
                    self.random.uniform(0, 6000),
                    2,
                )
            )
        )

        vacation_accrual = Decimal(
            str(
                round(
                    self.random.uniform(0, 4000),
                    2,
                )
            )
        )

        company = self.random_company()

        return Payroll(

            company_code=company.company_code,

            employee_code=self.random_employee(),

            payroll_date=self.random_invoice_date(),

            gross_salary=gross_salary,

            employer_contribution=employer_contribution,

            employee_tax=employee_tax,

            bonus_amount=bonus_amount,

            overtime_amount=overtime_amount,

            vacation_accrual=vacation_accrual,

            currency_code=company.currency_code,

            cost_center_code=self.random_cost_center(),

            department_code=self.random_department(),

            description="Monthly Payroll",
        )

    def random_employee(self) -> str:
        return f"EMP{self.random.randint(1, 500):05d}"

    def random_decimal(
        self,
        min_val: Decimal,
        max_val: Decimal,
    ) -> Decimal:
        """
        Returns a random Decimal between min_val and max_val,
        rounded to 2 decimal places.
        """

        amount = self.random.uniform(
            float(min_val),
            float(max_val),
        )

        return Decimal(str(round(amount, 2)))

    def random_bank_account(self) -> str:
        """
        Returns a random bank account code.
        """

        return self.random.choice(
            [
                "CZ-KB-001",
                "CZ-CSOB-001",
                "SK-SLSP-001",
                "DE-DB-001",
                "AT-RBI-001",
                "PL-PKO-001",
            ]
        )

    def random_date(self) -> date:
        """
        Returns a random business date.
        """
        return self.calendar.random_business_date()

    def random_currency(self) -> str:
        """
        Returns a random currency code.
        """

        return self.random.choice(
            [
                "CZK",
                "EUR",
                "USD",
                "PLN",
                "GBP",
            ]
        )

    def random_customer_code(self) -> str | None:
        """
        Returns a random customer code or None.
        """

        customer = self.customer_provider.random_customer()
        return customer.customer_code

    def random_supplier_code(self) -> str | None:
        """
        Returns a random supplier code or None.
        """

        supplier = self.supplier_provider.random_supplier()
        return supplier.supplier_code

    def random_reference(self) -> str:
        """
        Returns a random reference number.
        """

        return f"REF-{self.random.randint(100000, 999999)}"

    def create_bank_transaction(self) -> BankTransaction:
        """
        Creates one random bank transaction.
        """

        company = self.random_company()

        amount = self.random_decimal(
            Decimal("100"),
            Decimal("500000"),
        )

        transaction_types = [
            "BANK_FEE",
            "INTEREST_INCOME",
            "INTEREST_EXPENSE",
            "LOAN_DRAWDOWN",
            "LOAN_REPAYMENT",
            "FX_GAIN",
            "FX_LOSS",
            "CASH_DEPOSIT",
            "CASH_WITHDRAWAL",
            "INTERNAL_TRANSFER",
        ]

        return BankTransaction(
            company_code=company.company_code,

            bank_account=self.random_bank_account(),

            transaction_date=self.random_date(),

            amount=amount,

            currency_code=company.currency_code,

            description="Bank Transaction",

            transaction_type=self.random.choice(
                transaction_types
            ),

            cost_center_code=self.random_cost_center(),

            department_code=self.random_department(),

            loan_term=self.random.choice(["SHORT", "LONG"]),

            customer_code=self.random_customer_code(),

            supplier_code=self.random_supplier_code(),

            reference_number=self.random_reference(),
        )

    def create_closing_transaction(
        self,
    ) -> ClosingTransaction:
        """
        Creates one random closing transaction.
        """

        company = self.random_company()

        amount = self.random_decimal(
            Decimal("5000"),
            Decimal("500000"),
        )

        closing_types = [
            "ACCRUED_EXPENSE",
            "ACCRUED_REVENUE",
            "PREPAID_EXPENSE",
            "DEFERRED_REVENUE",
            "PROVISION",
            "FX_REVALUATION",
        ]

        expense_accounts = [
            "502",
            "511",
            "518",
            "521",
            "524",
        ]

        revenue_accounts = [
            "601",
            "602",
            "604",
        ]

        balance_accounts = [
            "381",
            "384",
            "388",
            "389",
            "451",
        ]

        return ClosingTransaction(

            company_code=company.company_code,

            closing_date=self.random_date(),

            amount=amount,

            currency_code=company.currency_code,

            cost_center_code=self.random_cost_center(),

            department_code=self.random_department(),

            closing_type=self.random.choice(
                closing_types
            ),

            description="Period End Closing",

            expense_account=self.random.choice(
                expense_accounts
            ),

            revenue_account=self.random.choice(
                revenue_accounts
            ),

            balance_account=self.random.choice(
                balance_accounts
            ),
        )

    def create_deferred_revenue_transaction(
        self,
    ) -> ClosingTransaction:
        """
        Creates deferred revenue transaction.
        """

        company = self.random_company()

        return ClosingTransaction(

            company_code=company.company_code,

            closing_date=self.random_date(),

            amount=self.random_decimal(
                Decimal("5000"),
                Decimal("250000"),
            ),

            currency_code=company.currency_code,

            cost_center_code=self.random_cost_center(),

            department_code=self.random_department(),

            closing_type="DEFERRED_REVENUE",

            description="Deferred Revenue",

            revenue_account=self.random.choice(
                [
                    "602",
                    "604",
                    "648",
                ]
            ),
        )


    def create_provision_transaction(
        self,
    ) -> ClosingTransaction:
        """
        Creates provision transaction.
        """

        company = self.random_company()

        return ClosingTransaction(

            company_code=company.company_code,

            closing_date=self.random_date(),

            amount=self.random_decimal(
                Decimal("10000"),
                Decimal("500000"),
            ),

            currency_code=company.currency_code,

            cost_center_code=self.random_cost_center(),

            department_code=self.random_department(),

            closing_type="PROVISION",

            description="Provision",

            expense_account=self.random.choice(
                [
                    "554",
                    "548",
                ]
            ),

            provision_account=self.random.choice(
                [
                    "451",
                    "453",
                    "459",
                ]
            ),
        )

    def create_inventory_writeoff_transaction(
        self,
    ) -> ClosingTransaction:
        """
        Creates inventory write-off transaction.
        """

        company = self.random_company()

        return ClosingTransaction(

            company_code=company.company_code,

            closing_date=self.random_date(),

            amount=self.random_decimal(
                Decimal("5000"),
                Decimal("300000"),
            ),

            currency_code=company.currency_code,

            cost_center_code=self.random_cost_center(),

            department_code=self.random_department(),

            closing_type="INVENTORY_WRITEOFF",

            description="Inventory Write-off",

            expense_account=self.random.choice(
                [
                    "549",
                    "548",
                    "582",
                ]
            ),

            inventory_account=self.random.choice(
                [
                    "112",
                    "123",
                    "132",
                ]
            ),
        )

    def create_inventory_revaluation_transaction(
        self,
    ) -> ClosingTransaction:
        """
        Creates Inventory Revaluation transaction.
        """

        company = self.random_company()

        return ClosingTransaction(

            company_code=company.company_code,

            closing_date=self.random_date(),

            amount=self.random_decimal(
                Decimal("5000"),
                Decimal("600000"),
            ),

            currency_code=company.currency_code,

            cost_center_code=self.random_cost_center(),

            department_code=self.random_department(),

            closing_type="INVENTORY_REVALUATION",

            description="Inventory Revaluation",

            expense_account="549",

            balance_account="112",
        )

    def create_bad_debt_allowance_transaction(
        self,
    ) -> ClosingTransaction:
        """
        Creates bad debt allowance transaction.
        """

        company = self.random_company()

        return ClosingTransaction(

            company_code=company.company_code,

            closing_date=self.random_date(),

            amount=self.random_decimal(
                Decimal("1000"),
                Decimal("250000"),
            ),

            currency_code=company.currency_code,

            cost_center_code=self.random_cost_center(),

            department_code=self.random_department(),

            closing_type="BAD_DEBT_ALLOWANCE",

            description="Bad Debt Allowance",

            expense_account="558",

            allowance_account="391",
        )

    def create_foreign_currency_revaluation_transaction(
        self,
    ) -> ClosingTransaction:
        """
        Creates foreign currency revaluation transaction.
        """

        company = self.random_company()

        gain = self.random.choice([True, False])

        if gain:

            debit_account = "311"
            credit_account = "663"

        else:

            debit_account = "563"
            credit_account = "311"

        return ClosingTransaction(

            company_code=company.company_code,

            closing_date=self.random_date(),

            amount=self.random_decimal(
                Decimal("500"),
                Decimal("350000"),
            ),

            currency_code=company.currency_code,

            cost_center_code=self.random_cost_center(),

            department_code=self.random_department(),

            closing_type="FOREIGN_CURRENCY_REVALUATION",

            description="Foreign Currency Revaluation",

            debit_account=debit_account,

            credit_account=credit_account,
        )

    def create_income_tax_accrual_transaction(
        self,
    ) -> ClosingTransaction:
        """
        Creates income tax accrual transaction.
        """

        company = self.random_company()

        return ClosingTransaction(

            company_code=company.company_code,

            closing_date=self.random_date(),

            amount=self.random_decimal(
                Decimal("10000"),
                Decimal("2000000"),
            ),

            currency_code=company.currency_code,

            cost_center_code=self.random_cost_center(),

            department_code=self.random_department(),

            closing_type="INCOME_TAX_ACCRUAL",

            description="Income Tax Accrual",

            tax_expense_account="591",

            tax_liability_account="341",
        )

    def create_deferred_tax_transaction(
        self,
    ) -> ClosingTransaction:
        """
        Creates deferred tax transaction.
        """

        company = self.random_company()

        return ClosingTransaction(

            company_code=company.company_code,

            closing_date=self.random_date(),

            amount=self.random_decimal(
                Decimal("5000"),
                Decimal("500000"),
            ),

            currency_code=company.currency_code,

            cost_center_code=self.random_cost_center(),

            department_code=self.random_department(),

            closing_type="DEFERRED_TAX",

            description="Deferred Tax",

            deferred_tax_expense_account="592",

            deferred_tax_balance_account="481",
        )

    def create_profit_transfer_transaction(
        self,
    ) -> ClosingTransaction:
        """
        Creates year-end profit transfer transaction.
        """

        company = self.random_company()

        return ClosingTransaction(

            company_code=company.company_code,

            closing_date=self.random_date(),

            amount=self.random_decimal(
                Decimal("50000"),
                Decimal("10000000"),
            ),

            currency_code=company.currency_code,

            cost_center_code=self.random_cost_center(),

            department_code=self.random_department(),

            closing_type="PROFIT_TRANSFER",

            description="Year-End Profit Transfer",

            profit_account="710",

            retained_earnings_account="702",
        )

    def create_opening_balance_transaction(
        self,
    ) -> ClosingTransaction:
        """
        Creates opening balance transaction.
        """

        company = self.random_company()

        return ClosingTransaction(

            company_code=company.company_code,

            closing_date=self.random_date(),

            amount=self.random_decimal(
                Decimal("100000"),
                Decimal("50000000"),
            ),

            currency_code=company.currency_code,

            cost_center_code=self.random_cost_center(),

            department_code=self.random_department(),

            closing_type="OPENING_BALANCE",

            description="Opening Balance",

            opening_account="701",

            balance_account="702",
        )