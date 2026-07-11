"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : validator.py
Object Type     : Journal Entry Validator
Layer           : ETL
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Validates accounting journal entries before loading them into Fact_GL.
===============================================================================
"""

from __future__ import annotations

from decimal import Decimal
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from accounting.models import JournalEntry


class ValidationError(Exception):
    """Raised when journal entry validation fails."""
    pass


class JournalEntryValidator:
    """Validates JournalEntry objects."""

    @staticmethod
    def validate(entry: JournalEntry) -> None:
        """
        Validate a journal entry.

        Raises:
            ValidationError: If any validation rule fails.
        """

        if len(entry.lines) < 2:
            raise ValidationError(
                "Journal entry must contain at least two lines."
            )

        if not entry.is_balanced:
            raise ValidationError(
                f"Journal entry '{entry.document.document_number}' "
                "is not balanced."
            )

        for line in entry.lines:

            if not line.account_number:
                raise ValidationError("Account number is required.")

            if not line.company_code:
                raise ValidationError("Company code is required.")

            if not line.currency_code:
                raise ValidationError("Currency code is required.")

            if line.debit_amount < Decimal("0"):
                raise ValidationError(
                    "Debit amount cannot be negative."
                )

            if line.credit_amount < Decimal("0"):
                raise ValidationError(
                    "Credit amount cannot be negative."
                )

            if line.amount_local < Decimal("0"):
                raise ValidationError(
                    "Local amount cannot be negative."
                )

