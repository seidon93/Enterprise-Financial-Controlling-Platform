"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : dimension_mapper.py
Object Type     : Dimension Mapper
Layer           : ETL
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Loads dimension tables into memory and provides fast business key to
surrogate key mapping.
===============================================================================
"""

from __future__ import annotations

import logging
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from common.database import DatabaseManager

logger = logging.getLogger(__name__)


class DimensionMapper:

    def __init__(self, database: DatabaseManager) -> None:

        self.database = database

        self.account_map: dict[str, int] = {}
        self.company_map: dict[str, int] = {}
        self.cost_center_map: dict[str, int] = {}
        self.department_map: dict[str, int] = {}
        self.currency_map: dict[str, int] = {}
        self.customer_map: dict[str, int] = {}

    def initialize(self) -> None:

        logger.info("Loading dimension mappings...")

        self.account_map = self._load_dimension(
            "warehouse.dim_account",
            "account_number",
            "account_key",
        )

        self.company_map = self._load_dimension(
            "warehouse.dim_company",
            "company_code",
            "company_key",
        )

        self.cost_center_map = self._load_dimension(
            "warehouse.dim_cost_center",
            "cost_center_code",
            "cost_center_key",
        )

        self.department_map = self._load_dimension(
            "warehouse.dim_department",
            "department_code",
            "department_key",
        )

        self.currency_map = self._load_dimension(
            "warehouse.dim_currency",
            "currency_code",
            "currency_key",
        )

        self.customer_map = self._load_dimension(
            "warehouse.dim_customer",
            "customer_code",
            "customer_key",
        )

        self.load_customers()

        logger.info("Dimension mappings loaded successfully.")

    def _load_dimension(
        self,
        table: str,
        business_key: str,
        surrogate_key: str,
    ) -> dict[str, int]:

        sql = f"""
            SELECT
                {business_key},
                {surrogate_key}
            FROM {table}
        """

        with self.database.cursor() as cursor:

            cursor.execute(sql)

            rows = cursor.fetchall()

        return {
            row[business_key]: row[surrogate_key]
            for row in rows
        }

    def load_customers(self) -> None:
        """
        Loads customer dimension.
        """

        sql = """
            SELECT
                customer_code,
                customer_key
            FROM warehouse.dim_customer
        """

        rows = self.db.fetch_all(sql)

        self.customer_map = {
            row["customer_code"]: row["customer_key"]
            for row in rows
        }


    def customer_key(
        self,
        customer_code: str | None,
    ) -> int | None:
        """
        Returns surrogate key for customer.
        """

        if customer_code is None:
            return None

        return self.customer_map.get(customer_code)

    def account_key(self, account_number: str) -> int:
        return self.account_map[account_number]

    def company_key(self, company_code: str) -> int:
        return self.company_map[company_code]

    def cost_center_key(self, cost_center_code: str) -> int:
        return self.cost_center_map[cost_center_code]

    def department_key(self, department_code: str) -> int:
        return self.department_map[department_code]

    def currency_key(self, currency_code: str) -> int:
        return self.currency_map[currency_code]

    @staticmethod
    def date_key(value: date) -> int:
        return int(value.strftime("%Y%m%d"))