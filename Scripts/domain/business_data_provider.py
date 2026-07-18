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

class BusinessDataProvider:
    """
    Provides realistic enterprise business data.
    """

    def __init__(self, seed: int = 42):

        self.random = random.Random(seed)
        self.calendar = BusinessCalendar(
            start_date=date(2021, 1, 1),
            end_date=date(2025, 12, 31),
            seed=seed,
        )
        self.customer_provider = CustomerProvider()

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
        """

        company = self.random_company()

        invoice_date = self.random_invoice_date()
        customer = self.customer_provider.random_customer()

        return BusinessTransaction(
            company_code=company.company_code,
            cost_center_code=self.random_cost_center(),
            department_code=self.random_department(),
            currency_code=company.currency_code,
            invoice_date=invoice_date,
            due_date=self.random_due_date(invoice_date),
            amount=self.random_invoice_amount(company),
            vat_rate=self.random_vat_rate(),
            description="Sales Invoice",
            customer_code=customer.customer_code,
        )

    def create_purchase_transaction(self) -> BusinessTransaction:
        """
        Create business transaction for Purchase Invoice.
        """

        company = self.random_company()

        invoice_date = self.random_invoice_date()

        customer = self.customer_provider.random_customer()

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
            customer_code=customer.customer_code,
        )


    def create_customer_payment_transaction(self) -> BusinessTransaction:
        """
        Create business transaction for Customer Payment.
        """

        company = self.random_company()

        payment_date = self.random_invoice_date()

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
        )

    def create_supplier_payment_transaction(self) -> BusinessTransaction:
        """
        Create business transaction for Supplier Payment.
        """

        company = self.random_company()

        payment_date = self.random_invoice_date()

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