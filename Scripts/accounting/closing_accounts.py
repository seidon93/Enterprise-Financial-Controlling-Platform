"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : closing_accounts.py
Object Type     : Closing Accounts
Layer           : Accounting
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Chart of accounts used for Closing & General Ledger scenarios.
===============================================================================
"""

from __future__ import annotations


class ClosingAccounts:
    """
    Enterprise Closing & General Ledger accounts.
    """

    # ------------------------------------------------------------------
    # Accruals & Deferrals
    # ------------------------------------------------------------------

    PREPAID_EXPENSES = "381"

    COMPLEX_DEFERRED_EXPENSES = "382"

    ACCRUED_EXPENSES = "383"

    DEFERRED_REVENUE = "384"

    ACCRUED_REVENUE = "385"

    ESTIMATED_RECEIVABLES = "388"

    ESTIMATED_LIABILITIES = "389"

    # ------------------------------------------------------------------
    # Provisions
    # ------------------------------------------------------------------

    SHORT_TERM_PROVISION = "323"

    LONG_TERM_PROVISION = "451"

    # ------------------------------------------------------------------
    # Foreign Exchange
    # ------------------------------------------------------------------

    FX_GAIN = "663"

    FX_LOSS = "563"

    # ------------------------------------------------------------------
    # Year End
    # ------------------------------------------------------------------

    PROFIT_AND_LOSS = "710"

    INCOME_SUMMARY = "702"

    RETAINED_EARNINGS = "431"

    # ------------------------------------------------------------------
    # General Ledger
    # ------------------------------------------------------------------

    GENERAL_LEDGER = "999"
    
    # ------------------------------------------------------------------
    # Inventory
    # ------------------------------------------------------------------
    INVENTORY_REVALUATION_EXPENSE = "549"
    INVENTORY_ACCOUNT = "112"