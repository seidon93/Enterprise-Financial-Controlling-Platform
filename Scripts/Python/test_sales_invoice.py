from datetime import date
from decimal import Decimal
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from accounting.document_generator import DocumentGenerator
from scenarios.sales_invoice import (
    SalesInvoiceScenario,
    SalesInvoiceRequest,
)

generator = DocumentGenerator()

scenario = SalesInvoiceScenario(generator)

request = SalesInvoiceRequest(
    company_code="CZ01",
    cost_center_code="CC100",
    department_code="FIN",
    currency_code="CZK",
    invoice_date=date(2026, 7, 11),
    due_date=date(2026, 8, 10),
    net_amount=Decimal("100000.00"),
    vat_rate=Decimal("0.21"),
    description="Invoice #1001",
)

entry = scenario.create(request)

print("=" * 60)
print("DOCUMENT")
print("=" * 60)

print(entry.document)

print()

print("=" * 60)
print("LINES")
print("=" * 60)

for line in entry.lines:
    print(line)

print()

print("=" * 60)
print("TOTALS")
print("=" * 60)

print("Debit :", entry.total_debit)
print("Credit:", entry.total_credit)
print("Balanced:", entry.is_balanced)