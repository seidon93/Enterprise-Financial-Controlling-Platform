"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : enums.py
Object Type     : Enumerations
Layer           : ETL
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Shared enumerations used across the ETL framework.
===============================================================================
"""

from enum import Enum


class DocumentType(str, Enum):
    """Accounting document types."""

    AR = "AR"              # Accounts Receivable
    AP = "AP"              # Accounts Payable
    BANK = "BANK"          # Bank Transactions
    GL = "GL"              # General Ledger
    PAYROLL = "PAYROLL"    # Payroll
    DEPR = "DEPR"          # Depreciation
    VAT = "VAT"            # VAT Settlement
    CP = "CP"              # Customer Payment
    SP = "SP"              # Supplier Payment
    FA = "FA"              # Fixed Assets
    JV = "JV"              # Journal Voucher
    GR = "GR"              # Goods Receipt
    GI = "GI"              # Goods Issue

class ScenarioType(str, Enum):
    """Accounting scenario types."""

    SALES_INVOICE = "Sales Invoice"
    PURCHASE_INVOICE = "Purchase Invoice"
    CUSTOMER_PAYMENT = "Customer Payment"
    SUPPLIER_PAYMENT = "Supplier Payment"
    PAYROLL = "Payroll"
    DEPRECIATION = "Depreciation"
    BANK = "Bank"
    VAT_SETTLEMENT = "VAT Settlement"


class StatementType(str, Enum):
    """Financial statement classification."""

    BALANCE_SHEET = "Balance Sheet"
    PROFIT_AND_LOSS = "Profit and Loss"


class NormalBalance(str, Enum):
    """Natural account balance."""

    DEBIT = "Debit"
    CREDIT = "Credit"


class SourceSystem(str, Enum):
    """Source systems."""

    EFAP = "EFAP"
    ERP = "ERP"
    IMPORT = "IMPORT"