from Scripts.repositories.journal_repository import JournalRepository
from tests.reporting.test_variance_engine import create_sales_invoice


def test_repository_empty():

    repo = JournalRepository()

    assert repo.count() == 0

def test_save_entry():

    repo = JournalRepository()

    entry = create_sales_invoice()

    repo.save(entry)

    assert repo.count() == 1

