"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : budget_loader.py
Object Type     : Budget Loader
Layer           : Budget
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Loads budgets from external sources.
===============================================================================
"""

from __future__ import annotations
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

class BudgetLoader:

    def load_csv(
        self,
        path: Path,
    ):

        if not path.exists():
            raise FileNotFoundError(path)