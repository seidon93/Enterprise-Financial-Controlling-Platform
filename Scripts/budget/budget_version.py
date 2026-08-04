from enum import Enum


class BudgetVersion(str, Enum):
    """Budget versions."""

    ORIGINAL = "Original Budget"

    FORECAST_1 = "Forecast 1"

    FORECAST_2 = "Forecast 2"

    LATEST_ESTIMATE = "Latest Estimate"

    ACTUAL = "Actual"