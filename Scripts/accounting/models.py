"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : models.py
Object Type     : Data Models
Layer           : ETL
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Shared data models used by the EFAP ETL framework.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal


# ============================================================================
# Document
# ============================================================================

@dataclass(slots=True, frozen=True)
class DocumentInfo:
    """
    Accounting document metadata.
    """

    document_number: str
    document_type: str

    posting_date: date
    document_date: date
    due_date: date

    fiscal_year: int
    fiscal_period: int


# ============================================================================
# Journal Line
# ============================================================================

@dataclass(slots=True)
class JournalLine:

    line_number: int

    account_number: str

    company_code: str

    cost_center_code: str

    department_code: str

    currency_code: str

    debit_amount: Decimal

    credit_amount: Decimal

    amount_local: Decimal

    description: str

    customer_code: str | None = None


# ============================================================================
# Journal Entry
# ============================================================================

@dataclass(slots=True)
class JournalEntry:
    """
    Complete accounting document.
    """

    document: DocumentInfo

    lines: list[JournalLine] = field(default_factory=list)

    def add_line(self, line: JournalLine) -> None:
        """Add journal line."""
        self.lines.append(line)

    @property
    def total_debit(self) -> Decimal:
        """Total debit amount."""
        return sum((line.debit_amount for line in self.lines), Decimal("0"))

    @property
    def total_credit(self) -> Decimal:
        """Total credit amount."""
        return sum((line.credit_amount for line in self.lines), Decimal("0"))

    @property
    def is_balanced(self) -> bool:
        """Check accounting balance."""
        return self.total_debit == self.total_credit