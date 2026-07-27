"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : payroll.py
Object Type     : Payroll Business Object
Layer           : Domain
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Represents payroll transaction used by Payroll scenarios.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(slots=True, frozen=True)
class Payroll:
    """
    Enterprise payroll transaction.
    """

    company_code: str

    employee_code: str

    payroll_date: date

    gross_salary: Decimal

    employer_contribution: Decimal

    employee_tax: Decimal

    bonus_amount: Decimal

    overtime_amount: Decimal

    vacation_accrual: Decimal

    currency_code: str

    cost_center_code: str

    department_code: str

    description: str