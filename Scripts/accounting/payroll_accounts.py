"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : payroll_accounts.py
Object Type     : Payroll Chart of Accounts
Layer           : ETL
Version         : 1.0.0
Status          : Development
-------------------------------------------------------------------------------
Description:
Enterprise payroll accounts used by payroll accounting scenarios.
===============================================================================
"""


class PayrollAccounts:
    """
    Enterprise Payroll Chart of Accounts.
    """

    # Payroll expense
    SALARY_EXPENSE = "521"

    # Employer social & health insurance
    EMPLOYER_CONTRIBUTIONS = "524"

    # Employees payable
    PAYROLL_LIABILITY = "331"

    # Social insurance payable
    SOCIAL_INSURANCE = "336"

    # Income tax payable
    PAYROLL_TAX = "342"

    # Bank account
    BANK = "221"
