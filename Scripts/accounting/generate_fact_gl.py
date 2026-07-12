"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : generate_fact_gl.py
Object Type     : ETL Entry Point
Layer           : Application
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Generates sample accounting transactions and loads them into Fact_GL.
===============================================================================
"""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datetime import date
from decimal import Decimal

from accounting.document_generator import DocumentGenerator
from accounting.dimension_mapper import DimensionMapper
from accounting.loader import FactGLLoader

from scenarios.sales_invoice import (
    SalesInvoiceScenario,
    SalesInvoiceRequest,
)

from common.batch_context import BatchContext
from common.database import db


def main() -> None:

    print("=" * 70)
    print("EFAP - Generate Fact_GL")
    print("=" * 70)

    # Infrastructure
    mapper = DimensionMapper(db)
    mapper.initialize()
    loader = FactGLLoader(db, mapper)
    generator = DocumentGenerator()
    batch = BatchContext()

    # Business scenario
    scenario = SalesInvoiceScenario(generator)

    request = SalesInvoiceRequest(
        company_code="CZ001",
        cost_center_code="1000",
        department_code="FIN",
        currency_code="CZK",

        invoice_date=date.today(),
        due_date=date.today(),

        net_amount=Decimal("10000.00"),
        vat_rate=Decimal("0.21"),

        description="Test Sales Invoice",
    )

    # Create accounting entry
    entry = scenario.create(request)

    print(f"Document : {entry.document.document_number}")
    print(f"Lines    : {len(entry.lines)}")

    # Load into Data Warehouse
    inserted = loader.load(entry, batch)

    print(f"Inserted rows : {inserted}")
    print(f"Batch ID      : {batch.batch_id}")

    print("=" * 70)
    print("FINISHED")
    print("=" * 70)


if __name__ == "__main__":
    main()