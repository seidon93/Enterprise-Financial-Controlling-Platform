"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : business_event.py
Object Type     : Business Event
Layer           : Domain
Version         : 1.0.0
Status          : Development
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from domain.business_event_type import BusinessEventType


@dataclass(slots=True, frozen=True)
class BusinessEvent:
    """
    Represents one business event.
    """

    event_type: BusinessEventType

    company_code: str

    event_date: date

    amount: Decimal

    currency_code: str

    description: str