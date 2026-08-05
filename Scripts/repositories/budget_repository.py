"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : budget_repository.py
Object Type     : Repository
Layer           : Infrastructure
Version         : 1.0.0
Status          : Development
===============================================================================
"""


class BudgetRepository:

    def __init__(self):

        self._lines = []

    def save(self, line):

        self._lines.append(line)

    def get_all(self):

        return list(self._lines)

    def count(self):

        return len(self._lines)