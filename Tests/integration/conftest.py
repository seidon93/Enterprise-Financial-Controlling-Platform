import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'Scripts')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import pytest

from Scripts.repositories.journal_repository import JournalRepository
from Scripts.repositories.budget_repository import BudgetRepository
from Scripts.repositories.chart_of_accounts_repository import (
    ChartOfAccountsRepository,
)
from tests.helpers.factories import create_sales_invoice, create_purchase_invoice

@pytest.fixture
def purchase_invoice():
    return create_purchase_invoice()

@pytest.fixture
def journal_repository():

    return JournalRepository()


@pytest.fixture
def budget_repository():

    return BudgetRepository()


@pytest.fixture
def chart_repository():

    return ChartOfAccountsRepository()

@pytest.fixture
def sales_invoice():

    return create_sales_invoice()