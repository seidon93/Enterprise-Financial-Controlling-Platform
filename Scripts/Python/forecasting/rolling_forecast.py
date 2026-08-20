"""
EFAP - Rolling Forecast

Object:
    Python/forecasting/rolling_forecast.py

Purpose:
    Combines actual financial history with the latest Revenue
    and Expense forecasts into one rolling management forecast.

Sources:
    data/processed/controller_kpi_timeseries.csv
    data/forecasts/revenue_forecast.csv
    data/forecasts/expense_forecast.csv

Output:
    data/forecasts/rolling_forecast.csv

Current scope:
    Revenue
    Operating Expenses
    EBITDA
    EBITDA Margin

Important:
    EBIT, EBT, Net Profit and Cash Flow are intentionally not
    fabricated here. They will be added when corresponding
    forecast models exist.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

ACTUAL_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "controller_kpi_timeseries.csv"
)

REVENUE_FORECAST_FILE = (
    PROJECT_ROOT
    / "data"
    / "forecasts"
    / "revenue_forecast.csv"
)

EXPENSE_FORECAST_FILE = (
    PROJECT_ROOT
    / "data"
    / "forecasts"
    / "expense_forecast.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "forecasts"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "rolling_forecast.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

ROLLING_HISTORY_MONTHS = 6
ROLLING_FORECAST_MONTHS = 6


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# ============================================================
# FILE VALIDATION
# ============================================================

def validate_input_files() -> None:
    """Validate required input files."""

    required_files = {
        "Actual time series": ACTUAL_FILE,
        "Revenue forecast": REVENUE_FORECAST_FILE,
        "Expense forecast": EXPENSE_FORECAST_FILE,
    }

    missing = [
        f"{name}: {path}"
        for name, path in required_files.items()
        if not path.exists()
    ]

    if missing:
        raise FileNotFoundError(
            "Missing required input files:\n"
            + "\n".join(missing)
        )


# ============================================================
# LOAD ACTUALS
# ============================================================

def load_actuals() -> pd.DataFrame:
    """Load canonical actual KPI time series."""

    df = pd.read_csv(
        ACTUAL_FILE
    )

    required = {
        "period",
        "revenue",
        "operating_costs",
        "ebitda",
        "ebitda_margin",
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            "Actual dataset is missing columns: "
            + ", ".join(sorted(missing))
        )

    df["period"] = pd.to_datetime(
        df["period"],
        errors="coerce",
    )

    numeric_columns = [
        "revenue",
        "operating_costs",
        "ebitda",
        "ebitda_margin",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    df = (
        df[
            [
                "period",
                "revenue",
                "operating_costs",
                "ebitda",
                "ebitda_margin",
            ]
        ]
        .dropna(subset=["period"])
        .sort_values("period")
        .drop_duplicates("period")
        .reset_index(drop=True)
    )

    return df


# ============================================================
# LOAD REVENUE FORECAST
# ============================================================

def load_revenue_forecast() -> pd.DataFrame:
    """Load revenue forecast."""

    df = pd.read_csv(
        REVENUE_FORECAST_FILE
    )

    required = {
        "forecast_period",
        "forecast_revenue",
        "lower_bound",
        "upper_bound",
        "model",
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            "Revenue forecast is missing columns: "
            + ", ".join(sorted(missing))
        )

    df["forecast_period"] = pd.to_datetime(
        df["forecast_period"],
        errors="coerce",
    )

    for column in [
        "forecast_revenue",
        "lower_bound",
        "upper_bound",
    ]:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    return (
        df[
            [
                "forecast_period",
                "forecast_revenue",
                "lower_bound",
                "upper_bound",
                "model",
            ]
        ]
        .dropna(
            subset=["forecast_period"]
        )
        .sort_values("forecast_period")
        .drop_duplicates(
            "forecast_period"
        )
        .reset_index(drop=True)
    )


# ============================================================
# LOAD EXPENSE FORECAST
# ============================================================

def load_expense_forecast() -> pd.DataFrame:
    """Load detailed expense forecasts."""

    df = pd.read_csv(
        EXPENSE_FORECAST_FILE
    )

    required = {
        "forecast_period",
        "account_number",
        "account_name",
        "forecast_expense",
        "lower_bound",
        "upper_bound",
        "selected_model",
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            "Expense forecast is missing columns: "
            + ", ".join(sorted(missing))
        )

    df["forecast_period"] = pd.to_datetime(
        df["forecast_period"],
        errors="coerce",
    )

    df["forecast_expense"] = pd.to_numeric(
        df["forecast_expense"],
        errors="coerce",
    )

    df["lower_bound"] = pd.to_numeric(
        df["lower_bound"],
        errors="coerce",
    )

    df["upper_bound"] = pd.to_numeric(
        df["upper_bound"],
        errors="coerce",
    )

    return (
        df
        .dropna(
            subset=["forecast_period"]
        )
        .sort_values(
            [
                "forecast_period",
                "account_number",
            ]
        )
        .reset_index(drop=True)
    )


# ============================================================
# AGGREGATE EXPENSE FORECAST
# ============================================================

def aggregate_expenses(
    expense_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Aggregate detailed expense forecasts to monthly operating
    expenses.

    Expense forecast values are positive consumption amounts.

    The management reporting layer uses operating costs as
    negative values, so we convert them to negative presentation
    values here.
    """

    monthly = (
        expense_df
        .groupby(
            "forecast_period",
            as_index=False,
        )
        .agg(
            forecast_expense_positive=(
                "forecast_expense",
                "sum",
            ),
            expense_lower_bound_positive=(
                "lower_bound",
                "sum",
            ),
            expense_upper_bound_positive=(
                "upper_bound",
                "sum",
            ),
        )
    )

    monthly["forecast_operating_costs"] = (
        -monthly[
            "forecast_expense_positive"
        ]
    )

    monthly["operating_costs_lower_bound"] = (
        -monthly[
            "expense_upper_bound_positive"
        ]
    )

    monthly["operating_costs_upper_bound"] = (
        -monthly[
            "expense_lower_bound_positive"
        ]
    )

    return monthly[
        [
            "forecast_period",
            "forecast_operating_costs",
            "operating_costs_lower_bound",
            "operating_costs_upper_bound",
        ]
    ]


# ============================================================
# BUILD FORECAST PERIOD
# ============================================================

def build_forecast_period(
    latest_actual_period: pd.Timestamp,
    revenue_forecast: pd.DataFrame,
    expense_forecast: pd.DataFrame,
) -> pd.DatetimeIndex:
    """Build common future forecast period."""

    last_revenue = (
        revenue_forecast["forecast_period"]
        .max()
    )

    last_expense = (
        expense_forecast["forecast_period"]
        .max()
    )

    latest_available = min(
        last_revenue,
        last_expense,
    )

    if latest_available <= latest_actual_period:
        raise ValueError(
            "Forecast periods do not extend beyond "
            "the latest actual period."
        )

    forecast_end = min(
        latest_available,
        latest_actual_period
        + pd.DateOffset(
            months=ROLLING_FORECAST_MONTHS
        ),
    )

    return pd.date_range(
        start=(
            latest_actual_period
            + pd.offsets.MonthBegin(1)
        ),
        end=forecast_end,
        freq="MS",
    )


# ============================================================
# CALCULATE FORECAST
# ============================================================

def build_future_forecast(
    latest_actual_period: pd.Timestamp,
    revenue_forecast: pd.DataFrame,
    expense_forecast: pd.DataFrame,
) -> pd.DataFrame:
    """Build future rolling forecast months."""

    expense_monthly = aggregate_expenses(
        expense_forecast
    )

    future_periods = build_forecast_period(
        latest_actual_period,
        revenue_forecast,
        expense_monthly,
    )

    revenue = (
        revenue_forecast[
            revenue_forecast["forecast_period"]
            .isin(future_periods)
        ]
        .copy()
    )

    expenses = (
        expense_monthly[
            expense_monthly["forecast_period"]
            .isin(future_periods)
        ]
        .copy()
    )

    result = (
        revenue
        .merge(
            expenses,
            left_on="forecast_period",
            right_on="forecast_period",
            how="inner",
        )
    )

    if result.empty:
        raise ValueError(
            "No overlapping Revenue and Expense "
            "forecast periods found."
        )

    result = result.rename(
        columns={
            "forecast_period": "period",
            "forecast_revenue": "revenue",
            "lower_bound": "revenue_lower_bound",
            "upper_bound": "revenue_upper_bound",
            "model": "revenue_model",
        }
    )

    # --------------------------------------------------------
    # EBITDA
    # --------------------------------------------------------

    result["operating_costs"] = (
        result["forecast_operating_costs"]
    )

    result["ebitda"] = (
        result["revenue"]
        + result["operating_costs"]
    )

    result["ebitda_lower_bound"] = (
        result["revenue_lower_bound"]
        + result["operating_costs_lower_bound"]
    )

    result["ebitda_upper_bound"] = (
        result["revenue_upper_bound"]
        + result["operating_costs_upper_bound"]
    )

    # --------------------------------------------------------
    # EBITDA Margin
    # --------------------------------------------------------

    result["ebitda_margin"] = np.where(
        result["revenue"] != 0,
        result["ebitda"]
        / result["revenue"],
        np.nan,
    )

    result["ebitda_margin_lower_bound"] = np.where(
        result["revenue_lower_bound"] != 0,
        result["ebitda_lower_bound"]
        / result["revenue_lower_bound"],
        np.nan,
    )

    result["ebitda_margin_upper_bound"] = np.where(
        result["revenue_upper_bound"] != 0,
        result["ebitda_upper_bound"]
        / result["revenue_upper_bound"],
        np.nan,
    )

    result["data_type"] = "FORECAST"

    result["forecast_horizon_month"] = (
        (
            result["period"].dt.year
            - latest_actual_period.year
        )
        * 12
        + (
            result["period"].dt.month
            - latest_actual_period.month
        )
    )

    return result[
        [
            "period",
            "data_type",

            "forecast_horizon_month",

            "revenue",
            "revenue_lower_bound",
            "revenue_upper_bound",
            "revenue_model",

            "operating_costs",
            "operating_costs_lower_bound",
            "operating_costs_upper_bound",

            "ebitda",
            "ebitda_lower_bound",
            "ebitda_upper_bound",

            "ebitda_margin",
            "ebitda_margin_lower_bound",
            "ebitda_margin_upper_bound",
        ]
    ]


# ============================================================
# ACTUAL HISTORY
# ============================================================

def build_actual_history(
    actuals: pd.DataFrame,
) -> pd.DataFrame:
    """Return latest actual months for rolling context."""

    latest_period = actuals["period"].max()

    history_start = (
        latest_period
        - pd.DateOffset(
            months=ROLLING_HISTORY_MONTHS - 1
        )
    )

    history = actuals[
        actuals["period"] >= history_start
    ].copy()

    history["data_type"] = "ACTUAL"

    history["forecast_horizon_month"] = 0

    history["revenue_lower_bound"] = np.nan
    history["revenue_upper_bound"] = np.nan
    history["revenue_model"] = None

    history["operating_costs_lower_bound"] = np.nan
    history["operating_costs_upper_bound"] = np.nan

    history["ebitda_lower_bound"] = np.nan
    history["ebitda_upper_bound"] = np.nan

    history["ebitda_margin_lower_bound"] = np.nan
    history["ebitda_margin_upper_bound"] = np.nan

    return history[
        [
            "period",
            "data_type",

            "forecast_horizon_month",

            "revenue",
            "revenue_lower_bound",
            "revenue_upper_bound",
            "revenue_model",

            "operating_costs",
            "operating_costs_lower_bound",
            "operating_costs_upper_bound",

            "ebitda",
            "ebitda_lower_bound",
            "ebitda_upper_bound",

            "ebitda_margin",
            "ebitda_margin_lower_bound",
            "ebitda_margin_upper_bound",
        ]
    ]


# ============================================================
# ROLLING FORECAST
# ============================================================

def build_rolling_forecast(
    actuals: pd.DataFrame,
    revenue_forecast: pd.DataFrame,
    expense_forecast: pd.DataFrame,
) -> pd.DataFrame:
    """Combine actual history and future forecast."""

    latest_actual_period = (
        actuals["period"].max()
    )

    actual_history = build_actual_history(
        actuals
    )

    future_forecast = build_future_forecast(
        latest_actual_period,
        revenue_forecast,
        expense_forecast,
    )

    rolling = pd.concat(
        [
            actual_history,
            future_forecast,
        ],
        ignore_index=True,
    )

    rolling = (
        rolling
        .sort_values("period")
        .drop_duplicates(
            "period",
            keep="last",
        )
        .reset_index(drop=True)
    )

    rolling["year_month"] = (
        rolling["period"]
        .dt.strftime("%Y-%m")
    )

    rolling["calendar_year"] = (
        rolling["period"]
        .dt.year
    )

    rolling["calendar_month"] = (
        rolling["period"]
        .dt.month
    )

    return rolling[
        [
            "period",
            "year_month",
            "calendar_year",
            "calendar_month",
            "data_type",

            "forecast_horizon_month",

            "revenue",
            "revenue_lower_bound",
            "revenue_upper_bound",
            "revenue_model",

            "operating_costs",
            "operating_costs_lower_bound",
            "operating_costs_upper_bound",

            "ebitda",
            "ebitda_lower_bound",
            "ebitda_upper_bound",

            "ebitda_margin",
            "ebitda_margin_lower_bound",
            "ebitda_margin_upper_bound",
        ]
    ]


# ============================================================
# CONTROLLER FLAGS
# ============================================================

def add_controller_flags(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Add simple controller interpretation flags."""

    df = df.copy()

    df["ebitda_status"] = np.select(
        [
            df["ebitda"] > 0,
            df["ebitda"] < 0,
        ],
        [
            "POSITIVE",
            "NEGATIVE",
        ],
        default="ZERO",
    )

    df["revenue_trend_status"] = np.select(
        [
            df["revenue"].diff() > 0,
            df["revenue"].diff() < 0,
        ],
        [
            "IMPROVING",
            "DECLINING",
        ],
        default="STABLE",
    )

    df["forecast_risk_status"] = np.select(
        [
            (
                df["ebitda_margin_lower_bound"]
                < 0
            )
            & (
                df["data_type"] == "FORECAST"
            ),

            (
                (
                    df["ebitda_margin_lower_bound"]
                    >= 0
                )
                & (
                    df["ebitda_margin"]
                    < 0.10
                )
                & (
                    df["data_type"] == "FORECAST"
                )
            ),
        ],
        [
            "HIGH_RISK",
            "WATCH",
        ],
        default="NORMAL",
    )

    return df


# ============================================================
# VALIDATION
# ============================================================

def validate_output(
    df: pd.DataFrame,
) -> None:
    """Validate rolling forecast structure."""

    if df.empty:
        raise ValueError(
            "Rolling forecast is empty."
        )

    if df["period"].duplicated().any():
        raise ValueError(
            "Duplicate periods detected."
        )

    if (
        df["data_type"] == "FORECAST"
    ).sum() == 0:
        raise ValueError(
            "No forecast periods found."
        )

    forecast_periods = df.loc[
        df["data_type"] == "FORECAST",
        "period",
    ]

    if not forecast_periods.is_monotonic_increasing:
        raise ValueError(
            "Forecast periods are not ordered."
        )

    if (
        df.loc[
            df["data_type"] == "FORECAST",
            "forecast_horizon_month",
        ]
        < 1
    ).any():
        raise ValueError(
            "Forecast horizon must start at month 1."
        )


# ============================================================
# SAVE
# ============================================================

def save_output(
    df: pd.DataFrame,
) -> None:
    """Save rolling forecast dataset."""

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    logger.info(
        "Rolling forecast saved to %s",
        OUTPUT_FILE,
    )


# ============================================================
# MAIN
# ============================================================

def main() -> int:
    """Run Rolling Forecast pipeline."""

    try:

        logger.info(
            "Starting EFAP Rolling Forecast."
        )

        validate_input_files()

        actuals = load_actuals()

        revenue_forecast = (
            load_revenue_forecast()
        )

        expense_forecast = (
            load_expense_forecast()
        )

        rolling = build_rolling_forecast(
            actuals=actuals,
            revenue_forecast=revenue_forecast,
            expense_forecast=expense_forecast,
        )

        rolling = add_controller_flags(
            rolling
        )

        validate_output(
            rolling
        )

        save_output(
            rolling
        )

        logger.info(
            "Rolling Forecast completed successfully."
        )

        logger.info(
            "Output: %s rows | %s actual | %s forecast",
            len(rolling),
            (
                rolling["data_type"] == "ACTUAL"
            ).sum(),
            (
                rolling["data_type"] == "FORECAST"
            ).sum(),
        )

        return 0

    except Exception as exc:

        logger.exception(
            "Rolling Forecast failed: %s",
            exc,
        )

        return 1


if __name__ == "__main__":
    sys.exit(main())