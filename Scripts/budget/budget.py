"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : budget.py
Object Type     : Domain Model
Layer           : Budget
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Represents a complete Budget with header info and budget lines.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field

from Scripts.budget.budget_line import BudgetLine
from Scripts.budget.budget_version import BudgetVersion


@dataclass(slots=True)
class Budget:

    name: str

    fiscal_year: int

    version: BudgetVersion

    _lines: list[BudgetLine] = field(
        default_factory=list,
        init=False,
        repr=False,
    )

    def add_line(self, line: BudgetLine) -> None:

        self._lines.append(line)

    @property
    def lines(self) -> list[BudgetLine]:

        return list(self._lines)