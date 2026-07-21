"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : business_event_type.py
Object Type     : Business Event Types
Layer           : Domain
Version         : 1.0.0
Status          : Development
===============================================================================
"""

from Scripts.Python.Generators import generate_dim_customer
from enum import Enum, auto


class BusinessEventType(str, Enum):
    """
    Supported business events.
    """

    SALES_INVOICE = "SALES_INVOICE"

    PURCHASE_INVOICE = "PURCHASE_INVOICE"

    CUSTOMER_PAYMENT = "CUSTOMER_PAYMENT"

    SUPPLIER_PAYMENT = "SUPPLIER_PAYMENT"

    PAYROLL = "PAYROLL"

    BANK_FEE = "BANK_FEE"

    DEPRECIATION = "DEPRECIATION"

    FX_REVALUATION = "FX_REVALUATION"

    ASSET_ACQUISITION = auto()

    ASSET_CAPITALIZATION = auto()

    ASSET_DEPRECIATION = auto()

    ASSET_IMPAIRMENT = auto()

    ASSET_REVALUATION = auto()

    ASSET_DISPOSAL = auto()

    ASSET_SALE = auto()