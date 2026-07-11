"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : document_generator.py
Object Type     : Document Generator
Layer           : ETL
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Generates accounting document metadata and document numbers.
===============================================================================
"""

from __future__ import annotations

import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

# Add Scripts to path so 'accounting' and 'common' packages are discoverable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from accounting.enums import DocumentType
from accounting.models import DocumentInfo


class DocumentGenerator:
    """
    Generates accounting documents.

    One generator instance is intended for one ETL batch.
    """

    def __init__(self, start_number: int = 1) -> None:
        self._counters: dict[tuple[DocumentType, int], int] = defaultdict(
            lambda: start_number - 1
        )

    @staticmethod
    def _get_fiscal_period(posting_date: date) -> int:
        """Returns fiscal period (month)."""
        return posting_date.month

    def create(
        self,
        *,
        document_type: DocumentType,
        posting_date: date,
        document_date: date,
        due_date: date,
    ) -> DocumentInfo:
        """
        Create a new accounting document.
        """

        fiscal_year = posting_date.year
        fiscal_period = self._get_fiscal_period(posting_date)

        key = (document_type, fiscal_year)

        self._counters[key] += 1

        sequence = self._counters[key]

        document_number = (
            f"{document_type.value}-{fiscal_year}-{sequence:06d}"
        )

        return DocumentInfo(
            document_number=document_number,
            document_type=document_type.value,
            posting_date=posting_date,
            document_date=document_date,
            due_date=due_date,
            fiscal_year=fiscal_year,
            fiscal_period=fiscal_period,
        )
