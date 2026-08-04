from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from Scripts.budget.budget_loader import BudgetLoader


def test_loader_exists():

    loader = BudgetLoader()

    assert loader is not None

def test_missing_file():

    loader = BudgetLoader()

    with pytest.raises(FileNotFoundError):

        loader.load_csv(
            Path("missing.csv")
        )

def test_load_csv_rows(tmp_path):

    csv_file = tmp_path / "budget.csv"

    csv_file.write_text(
        "company,cost_center,account,amount\n"
        "1000,100,601000,100000\n",
        encoding="utf-8",
    )

    loader = BudgetLoader()

    rows = loader.load_csv(csv_file)

    assert len(rows) == 1

    assert rows[0]["company"] == "1000"

    assert rows[0]["account"] == "601000"


def test_empty_csv(tmp_path):

    csv_file = tmp_path / "budget.csv"

    csv_file.write_text(
        "company,cost_center,account,amount\n",
        encoding="utf-8",
    )

    loader = BudgetLoader()

    rows = loader.load_csv(csv_file)

    assert rows == []


def test_multiple_rows(tmp_path):

    csv_file = tmp_path / "budget.csv"

    csv_file.write_text(
        "company,cost_center,account,amount\n"
        "1000,100,601000,100000\n"
        "1000,100,602000,50000\n",
        encoding="utf-8",
    )

    loader = BudgetLoader()

    rows = loader.load_csv(csv_file)

    assert len(rows) == 2