"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : financial_controller_service.py
Object Type     : Service Layer
Layer           : Services
Version         : 1.0.0
===============================================================================
"""

try:
    from Scripts.services.models import FinancialControllerReport
except ModuleNotFoundError:
    from .models import FinancialControllerReport


class FinancialControllerService:

    @staticmethod
    def create_report(
        *,
        trial_balance,
        income_statement,
        balance_sheet,
        variances,
    ) -> FinancialControllerReport:

        return FinancialControllerReport(
            trial_balance=trial_balance,
            income_statement=income_statement,
            balance_sheet=balance_sheet,
            variances=variances,
        )