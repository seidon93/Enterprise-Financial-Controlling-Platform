from Scripts.accounting.account import Account
from Scripts.repositories.chart_of_accounts_repository import (
    ChartOfAccountsRepository,
)


def create_account() -> Account:
    return Account(
        account_code="601",
        account_name="Tržby za vlastní výrobky",
    )


def test_repository_empty():

    repo = ChartOfAccountsRepository()

    assert repo.count() == 0


def test_save_account():

    repo = ChartOfAccountsRepository()

    repo.save(create_account())

    assert repo.count() == 1


def test_get_by_code():

    repo = ChartOfAccountsRepository()

    repo.save(create_account())

    account = repo.get_by_code("601")

    assert account is not None
    assert account.account_code == "601"


def test_exists():

    repo = ChartOfAccountsRepository()

    repo.save(create_account())

    assert repo.exists("601") is True
    assert repo.exists("999") is False


def test_clear():

    repo = ChartOfAccountsRepository()

    repo.save(create_account())

    repo.clear()

    assert repo.count() == 0