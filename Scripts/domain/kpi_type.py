"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : kpi_type.py
Object Type     : Domain Enumeration
Layer           : Domain
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Defines KPI categories for management controlling.
===============================================================================
"""

from enum import Enum


class KPIType(str, Enum):

    REVENUE = "Revenue"

    EXPENSE = "Expense"

    ASSET = "Asset"

    LIABILITY = "Liability"

    EQUITY = "Equity"

    CASHFLOW = "Cash Flow"

    PROFIT = "Profit"