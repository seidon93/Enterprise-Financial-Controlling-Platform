"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : business_calendar.py
Object Type     : Business Calendar
Layer           : Domain
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Provides business dates for enterprise simulations.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
import random


@dataclass(slots=True)
class BusinessCalendar:
    """
    Enterprise business calendar.
    """

    start_date: date
    end_date: date
    seed: int = 42
    _random: random.Random = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._random = random.Random(self.seed)

    def random_business_date(self) -> date:
        """
        Returns a random business day (Monday-Friday).
        """

        while True:

            days = (self.end_date - self.start_date).days

            candidate = self.start_date + timedelta(
                days=self._random.randint(0, days)
            )

            if candidate.weekday() < 5:
                return candidate

    @staticmethod
    def is_business_day(value: date) -> bool:
        """
        Returns True if the date is Monday-Friday.
        """

        return value.weekday() < 5