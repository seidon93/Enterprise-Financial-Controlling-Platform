"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : general_ledger_engine.py
Object Type     : General Ledger Engine
Layer           : Accounting
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Posts validated Journal Entries into the General Ledger.
===============================================================================
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from Scripts.accounting.models import JournalEntry



class GeneralLedgerEngine:
    """
    In-memory General Ledger.

    Acts as posting engine between Journal Entries
    and reporting layer.
    """

    def __init__(self) -> None:

        self._entries: list[JournalEntry] = []

    def post(self, entry: JournalEntry) -> None:
        """
        Post Journal Entry into ledger.
        """

        self._entries.append(entry)

    @property
    def entries(self) -> list[JournalEntry]:

        return list(self._entries)

    @property
    def number_of_entries(self) -> int:

        return len(self._entries)