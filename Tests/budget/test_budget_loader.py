import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from decimal import Decimal

from Scripts.budget.budget_line import BudgetLine
from Scripts.budget.budget_loader import BudgetLoader


def test_csv_to_budget_line(tmp_path):

    csv_file = tmp_path / "budget.csv"

    csv_file.write_text(
        "company,cost_center,account,department,fiscal_year,fiscal_period,amount\n"
        "1000,100,601,FIN,2025,1,125000.50\n",
        encoding="utf-8",
    )

    loader = BudgetLoader()

    rows = loader.load_csv(csv_file)

    budget_line = loader.to_budget_line(rows[0])

    assert isinstance(budget_line, BudgetLine)

    assert budget_line.company_code == "1000"

    assert budget_line.cost_center_code == "100"

    assert budget_line.account_number == "601"

    assert budget_line.amount == Decimal("125000.50")

def test_convert_multiple_budget_lines(tmp_path):

    csv_file = tmp_path / "budget.csv"

    csv_file.write_text(
        "company,cost_center,account,department,fiscal_year,fiscal_period,amount\n"
        "1000,100,601,FIN,2025,1,100000\n"
        "1000,200,602,FIN,2025,2,50000\n",
        encoding="utf-8",
    )

    loader = BudgetLoader()

    rows = loader.load_csv(csv_file)

    budget_lines = [
        loader.to_budget_line(row)
        for row in rows
    ]

    assert len(budget_lines) == 2

    assert budget_lines[1].cost_center_code == "200"


def test_load_budget_lines(tmp_path):

    csv_file = tmp_path / "budget.csv"

    csv_file.write_text(
        "company,cost_center,account,department,fiscal_year,fiscal_period,amount\n"
        "1000,100,601,FIN,2025,1,100000\n",
        encoding="utf-8",
    )

    loader = BudgetLoader()

    lines = loader.load_budget_lines(csv_file)

    assert len(lines) == 1

    assert isinstance(lines[0], BudgetLine)