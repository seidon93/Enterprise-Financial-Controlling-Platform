"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : base.py
Object Type     : Base Accounting Scenario
Layer           : ETL
Version         : 1.0.0
Status          : Development
===============================================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from accounting.document_generator import DocumentGenerator
from accounting.models import JournalEntry
from accounting.validator import JournalEntryValidator


class AccountingScenario(ABC):
    """
    Base class for all accounting scenarios.
    """

    def __init__(
        self,
        document_generator: DocumentGenerator,
    ) -> None:

        self.document_generator = document_generator

    @abstractmethod
    def create(self, request: Any) -> JournalEntry:
        """
        Create accounting journal entry.
        """

    @staticmethod
    def validate(entry: JournalEntry) -> JournalEntry:

        JournalEntryValidator.validate(entry)

        return entry