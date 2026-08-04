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