"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : financial_controller_report.py
Object Type     : Service
Layer           : Service Layer
Version         : 1.0.0
Status          : Development
===============================================================================
"""

from dataclasses import dataclass

from Scripts.reporting.trial_balance import TrialBalance
from Scripts.reporting.income_statement import IncomeStatement
from Scripts.reporting.balance_sheet import BalanceSheet


@dataclass(slots=True)
class FinancialControllerReport:
    """
    Aggregated financial controller report.
    """

    trial_balance: TrialBalance
    income_statement: IncomeStatement
    balance_sheet: BalanceSheet