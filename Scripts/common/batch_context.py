"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : batch_context.py
Object Type     : Batch Context
Layer           : Common
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Represents metadata for one ETL batch execution.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass(slots=True, frozen=True)
class BatchContext:
    """
    Metadata describing one ETL batch.
    """

    batch_id: str = field(
        default_factory=lambda: uuid4().hex
    )

    source_system: str = "EFAP"

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

