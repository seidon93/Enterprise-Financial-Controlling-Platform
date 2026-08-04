from dataclasses import dataclass
from decimal import Decimal


@dataclass(slots=True)
class BudgetLine:

    company_code: str

    account_number: str

    cost_center_code: str

    department_code: str

    fiscal_year: int

    fiscal_period: int

    amount: Decimal