"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : chart_of_accounts_repository.py
Object Type     : Repository
Layer           : Infrastructure
Version         : 1.0.0
Status          : Development
===============================================================================
"""

from Scripts.accounting.account import Account


class ChartOfAccountsRepository:
    """
    In-memory repository for Chart of Accounts.
    """

    def __init__(self) -> None:
        self._accounts: list[Account] = []

    def save(self, account: Account) -> None:
        self._accounts.append(account)

    def get_all(self) -> list[Account]:
        return list(self._accounts)

    def count(self) -> int:
        return len(self._accounts)

    def clear(self) -> None:
        self._accounts.clear()

    def get_by_code(self, account_code: str) -> Account | None:
        for account in self._accounts:
            if account.account_code == account_code:
                return account
        return None

    def exists(self, account_code: str) -> bool:
        return self.get_by_code(account_code) is not None