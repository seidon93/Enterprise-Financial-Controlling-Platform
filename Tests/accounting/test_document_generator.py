"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : test_document_generator.py
Object Type     : Unit Tests
Layer           : Tests
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Unit tests for DocumentGenerator.
===============================================================================
"""

from datetime import date

from Scripts.accounting.document_generator import DocumentGenerator
from Scripts.accounting.enums import DocumentType

def test_create_document():

    generator = DocumentGenerator()

    doc = generator.create(

        document_type=DocumentType.AR,

        posting_date=date(2024, 5, 15),

        document_date=date(2024, 5, 15),

        due_date=date(2024, 6, 15),
    )

    assert doc.document_type == "AR"

    assert doc.fiscal_year == 2024

    assert doc.fiscal_period == 5

def test_document_number():

    generator = DocumentGenerator()

    doc = generator.create(

        document_type=DocumentType.AR,

        posting_date=date(2024, 1, 1),

        document_date=date(2024, 1, 1),

        due_date=date(2024, 1, 31),
    )

    assert (
        doc.document_number
        == f"{DocumentType.AR.value}-2024-000001"
    )

def test_sequence_increment():

    generator = DocumentGenerator()

    first = generator.create(

        document_type=DocumentType.AR,

        posting_date=date(2024, 1, 1),

        document_date=date(2024, 1, 1),

        due_date=date(2024, 1, 31),
    )

    second = generator.create(

        document_type=DocumentType.AR,

        posting_date=date(2024, 1, 2),

        document_date=date(2024, 1, 2),

        due_date=date(2024, 2, 2),
    )

    assert first.document_number.endswith("000001")

    assert second.document_number.endswith("000002")

def test_document_type_counter():

    generator = DocumentGenerator()

    sales = generator.create(

        document_type=DocumentType.AR,

        posting_date=date(2024, 1, 1),

        document_date=date(2024, 1, 1),

        due_date=date(2024, 1, 31),
    )

    purchase = generator.create(

        document_type=DocumentType.AP,

        posting_date=date(2024, 1, 1),

        document_date=date(2024, 1, 1),

        due_date=date(2024, 1, 31),
    )

    assert sales.document_number.endswith("000001")

    assert purchase.document_number.endswith("000001")

def test_new_year_counter():

    generator = DocumentGenerator()

    old = generator.create(

        document_type=DocumentType.AR,

        posting_date=date(2024, 12, 31),

        document_date=date(2024, 12, 31),

        due_date=date(2025, 1, 31),
    )

    new = generator.create(

        document_type=DocumentType.AR,

        posting_date=date(2025, 1, 1),

        document_date=date(2025, 1, 1),

        due_date=date(2025, 1, 31),
    )

    assert old.document_number.endswith("000001")

    assert new.document_number.endswith("000001")

def test_fiscal_period():

    generator = DocumentGenerator()

    doc = generator.create(

        document_type=DocumentType.GL,

        posting_date=date(2024, 9, 20),

        document_date=date(2024, 9, 20),

        due_date=date(2024, 10, 20),
    )

    assert doc.fiscal_period == 9

def test_custom_start_number():

    generator = DocumentGenerator(start_number=500)

    doc = generator.create(

        document_type=DocumentType.AR,

        posting_date=date(2024, 1, 1),

        document_date=date(2024, 1, 1),

        due_date=date(2024, 1, 31),
    )

    assert doc.document_number.endswith("000500")