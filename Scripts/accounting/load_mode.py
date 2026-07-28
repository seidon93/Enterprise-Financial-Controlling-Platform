"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : load_mode.py
Object Type     : Load Mode Enumeration
Layer           : Accounting
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Defines supported ETL execution modes.
===============================================================================
"""

from enum import Enum


class LoadMode(str, Enum):
    """
    Supported ETL execution modes.
    """

    FULL = "FULL"

    SALES_ONLY = "SALES_ONLY"

    PURCHASE_ONLY = "PURCHASE_ONLY"

    CUSTOMER_PAYMENT_ONLY = "CUSTOMER_PAYMENT_ONLY"

    SUPPLIER_PAYMENT_ONLY = "SUPPLIER_PAYMENT_ONLY"

    ASSET_ONLY = "ASSET_ONLY"

    ASSET_ACQUISITION_ONLY = "ASSET_ACQUISITION_ONLY"

    ASSET_CAPITALIZATION_ONLY = "ASSET_CAPITALIZATION_ONLY"

    ASSET_DEPRECIATION_ONLY = "ASSET_DEPRECIATION_ONLY"

    ASSET_IMPAIRMENT_ONLY = "ASSET_IMPAIRMENT_ONLY"

    ASSET_DISPOSAL_ONLY = "ASSET_DISPOSAL_ONLY"

    ASSET_SALE_ONLY = "ASSET_SALE_ONLY"
    
    INVENTORY_ONLY = "INVENTORY_ONLY"

    PAYROLL_ONLY = "PAYROLL_ONLY"