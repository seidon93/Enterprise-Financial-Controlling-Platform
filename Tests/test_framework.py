import sys
from pathlib import Path

# Add Scripts/Python to path so 'common' package is discoverable
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Scripts" / "Python"))

# pyrefly: ignore [missing-import]
from common.validation import (
    validate_not_empty,
    validate_unique,
)

import pandas as pd


def test_validation():

    df = pd.DataFrame(
        {
            "id": [1, 2, 3]
        }
    )

    validate_not_empty(df)

    validate_unique(df, "id")

    print("Validation OK")


if __name__ == "__main__":

    test_validation()