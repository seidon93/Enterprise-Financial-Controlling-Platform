"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : models.py
Object Type     : Service Models
Layer           : Services
Version         : 1.0.0
===============================================================================
"""

from dataclasses import dataclass

try:
    from Scripts.reporting.trial_balance import TrialBalance
    from Scripts.reporting.income_statement import IncomeStatement
    from Scripts.reporting.balance_sheet import BalanceSheet
    from Scripts.reporting.variance_result import VarianceResult
except ModuleNotFoundError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from reporting.trial_balance import TrialBalance
    from reporting.income_statement import IncomeStatement
    from reporting.balance_sheet import BalanceSheet
    from reporting.variance_result import VarianceResult


@dataclass(slots=True)
class FinancialControllerReport:

    trial_balance: TrialBalance

    income_statement: IncomeStatement

    balance_sheet: BalanceSheet

    variances: list[VarianceResult]