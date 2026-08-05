from decimal import Decimal

import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_project_root))

from Scripts.reporting.variace_engine import VarianceEngine



def test_positive_variance():

    result = VarianceEngine.calculate(
        Decimal("1000"),
        Decimal("1200"),
    )

    assert result.variance == Decimal("200")

def test_negative_variance():

    result = VarianceEngine.calculate(
        Decimal("1000"),
        Decimal("800"),
    )

    assert result.variance == Decimal("-200")


def test_variance_percent():

    result = VarianceEngine.calculate(
        Decimal("1000"),
        Decimal("1200"),
    )

    assert result.variance_percent == Decimal("20")

def test_zero_budget():

    result = VarianceEngine.calculate(
        Decimal("0"),
        Decimal("500"),
    )

    assert result.variance_percent == Decimal("0")