from tests.helpers.factories import (
    create_sales_invoice,
    create_purchase_invoice,
)

from Scripts.repositories.journal_repository import JournalRepository


def test_repository_stores_multiple_journals():

    repository = JournalRepository()

    repository.save(create_sales_invoice())
    repository.save(create_purchase_invoice())

    journals = repository.get_all()

    assert len(journals) == 2


def test_repository_count():

    repository = JournalRepository()

    repository.save(create_sales_invoice())

    assert repository.count() == 1


def test_repository_clear():

    repository = JournalRepository()

    repository.save(create_sales_invoice())
    repository.save(create_purchase_invoice())

    repository.clear()

    assert repository.count() == 0