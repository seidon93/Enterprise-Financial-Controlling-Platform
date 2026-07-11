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
Generates accounting document numbers and line numbers.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class DocumentInfo:
    """Accounting document metadata."""

    document_number: str
    line_number: int
    document_type: str
    posting_date: date
    document_date: date
    due_date: date


class DocumentGenerator:
    """
    Generates accounting document identifiers.
    """

    def __init__(self) -> None:
        self._counters = {}

    def next_document_number(
        self,
        posting_date: date,
        document_type: str,
    ) -> str:
        """
        Example:
            AR2026000001
            AP2026000001
            GL2026000001
        """

        year = posting_date.year
        key = (document_type, year)

        current = self._counters.get(key, 0) + 1
        self._counters[key] = current

        return f"{document_type}{year}{current:06d}"

    @staticmethod
    def create_document(
        document_number: str,
        line_number: int,
        document_type: str,
        posting_date: date,
        document_date: date,
        due_date: date,
    ) -> DocumentInfo:

        return DocumentInfo(
            document_number=document_number,
            line_number=line_number,
            document_type=document_type,
            posting_date=posting_date,
            document_date=document_date,
            due_date=due_date,
        )