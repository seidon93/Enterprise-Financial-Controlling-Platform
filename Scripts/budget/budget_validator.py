from decimal import Decimal

from Scripts.budget.budget import Budget


class BudgetValidationError(Exception):
    """Budget validation error."""
    pass


class BudgetValidator:

    @staticmethod
    def validate(budget: Budget):

        if len(budget.lines) == 0:

            raise BudgetValidationError(
                "Budget must contain at least one line."
            )

        for line in budget.lines:

            if not line.account_number:

                raise BudgetValidationError(
                    "Account number is required."
                )

            if not line.company_code:

                raise BudgetValidationError(
                    "Company code is required."
                )

            if line.amount < Decimal("0"):

                raise BudgetValidationError(
                    "Budget amount cannot be negative."
                )

            if line.fiscal_period < 1 or line.fiscal_period > 12:

                raise BudgetValidationError(
                    "Fiscal period must be between 1 and 12."
                )