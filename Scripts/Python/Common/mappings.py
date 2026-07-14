"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : mappings.py
Object Type     : Business Mappings
Layer           : Common
Version         : 1.0.0
Status          : Development

Description:
Central business mapping definitions used across ETL generators.
===============================================================================
"""

# =============================================================================
# Financial Statement
# =============================================================================

STATEMENT_TYPE = {
    0: "Balance Sheet",
    1: "Balance Sheet",
    2: "Balance Sheet",
    3: "Balance Sheet",
    4: "Balance Sheet",
    5: "Profit and Loss",
    6: "Profit and Loss",
    7: "Profit and Loss",
    8: "Profit and Loss",
    9: "Balance Sheet",
}

# =============================================================================
# Normal Balance
# =============================================================================

NORMAL_BALANCE = {
    0: "Debit",
    1: "Credit",
    2: "Debit",
    3: "Debit",
    4: "Credit",
    5: "Debit",
    6: "Credit",
    7: "Credit",
    8: "Credit",
    9: "Debit",
}

# =============================================================================
# Reporting Groups
# =============================================================================

REPORTING_GROUP = {
    0: "Fixed Assets",
    1: "Inventory",
    2: "Receivables",
    3: "Cash",
    4: "Equity and Liabilities",
    5: "Operating Costs",
    6: "Financial Result",
    7: "Closing Accounts",
    8: "Other Income",
    9: "Assets",
}

# =============================================================================
# Reporting Categories
# =============================================================================

REPORTING_CATEGORY = {
    0: "Assets",
    1: "Assets",
    2: "Assets",
    3: "Assets",
    4: "Liabilities",
    5: "Operating",
    6: "Financial",
    7: "Closing",
    8: "Other Income",
    9: "Assets",
}