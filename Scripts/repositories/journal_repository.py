"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : journal_repository.py
Object Type     : Repository
Layer           : Infrastructure
Version         : 1.0.0
Status          : Development
===============================================================================
"""

from accounting.models import JournalEntry


class JournalRepository:

    def __init__(self):

        self._entries: list[JournalEntry] = []

    def save(
        self,
        entry: JournalEntry,
    ) -> None:

        self._entries.append(entry)

    def get_all(self) -> list[JournalEntry]:

        return list(self._entries)

    def count(self) -> int:

        return len(self._entries)

    def clear(self) -> None:

        self._entries.clear()