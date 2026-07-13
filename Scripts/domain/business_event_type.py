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

from enum import Enum


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