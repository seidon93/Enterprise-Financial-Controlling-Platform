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

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dataclasses import dataclass

from reporting.trial_balance import TrialBalance
from reporting.income_statement import IncomeStatement
from reporting.balance_sheet import BalanceSheet


@dataclass(slots=True)
class FinancialControllerReport:
    """
    Aggregated Financial Controller Report.
    """

    trial_balance: TrialBalance
    income_statement: IncomeStatement
    balance_sheet: BalanceSheet
    financial_ratios: dict[str, float]
    revenue_budget: float = 0.0
    expense_budget: float = 0.0
    revenue_previous_year: float = 0.0
    net_profit_previous_year: float = 0.0

    previous_price: float = 0.0
    current_price: float = 0.0
    previous_volume: float = 0.0
    current_volume: float = 0.0