"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : asset_accounts.py
Object Type     : Asset Account Constants
Layer           : Accounting
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Chart of accounts used by the Asset Accounting module.
===============================================================================
"""

from __future__ import annotations


class AssetAccounts:
    """
    General Ledger accounts used for Fixed Assets.
    """

    # Fixed Assets
    ASSET_IN_PROGRESS = "042"
    FIXED_ASSETS = "022"
    ACCUMULATED_DEPRECIATION = "082"

    # Expenses
    DEPRECIATION_EXPENSE = "551"
    ASSET_DISPOSAL_EXPENSE = "541"

    # Revenue
    ASSET_DISPOSAL_REVENUE = "641"

    # Liabilities
    TRADE_PAYABLES = "321"

    # Cash / Bank
    BANK_ACCOUNT = "221"

    # VAT
    INPUT_VAT = "343"