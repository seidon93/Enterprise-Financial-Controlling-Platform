"""
EFAP - Expense Forecast

Object:
    Python/forecasting/forecast_expenses.py

Purpose:
    Forecast major operating expense lines individually.

Input:
    PostgreSQL
        mart.vw_pnl_monthly
        mart.dim_pnl_management_mapping

Models:
    1. Seasonal Naive baseline
    2. Holt-Winters Exponential Smoothing

Output:
    data/forecasts/expense_forecast.csv

Forecast horizon:
    6 months

Important:
    Financial/business logic stays in PostgreSQL.
    Python performs analytical forecasting only.
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

try:
    import psycopg2
except ImportError as exc:
    raise ImportError(
        "Missing dependency 'psycopg2'. "
        "Install with: pip install psycopg2-binary"
    ) from exc

try:
    from dotenv import load_dotenv
except ImportError as exc:
    raise ImportError(
        "Missing dependency 'python-dotenv'. "
        "Install with: pip install python-dotenv"
    ) from exc

try:
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
except ImportError as exc:
    raise ImportError(
        "Missing dependency 'statsmodels'. "
        "Install with: pip install statsmodels"
    ) from exc


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

ENV_FILE = PROJECT_ROOT / ".env"

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "forecasts"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "expense_forecast.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

FORECAST_HORIZON = 6
VALIDATION_MONTHS = 6
SEASON_LENGTH = 12
MIN_REQUIRED_MONTHS = 18


# ============================================================
# FORECAST ACCOUNTS
# ============================================================

EXPENSE_ACCOUNTS = {
    501: "Material Consumption",
    502: "Energy Consumption",
    504: "Cost of Goods Sold",
    518: "Other Services",
    521: "Payroll Costs",
    524: "Social & Health Insurance",
    548: "Other Operating Costs",
    549: "Shortages & Damages",
    582: "Inventory Change",
}


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv(ENV_FILE)


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "EFAP"),
    "user": os.getenv("DB_USER", ""),
    "password": os.getenv("DB_PASSWORD", ""),
}


# ============================================================
# SOURCE QUERY
# ============================================================

SOURCE_QUERY = """
SELECT

    p.calendar_year,
    p.calendar_month,
    p.month_name,
    p.year_month,

    p.account_number,
    p.account_name,

    m.management_group,
    m.management_line,
    m.management_sign,

    p.signed_amount

FROM mart.vw_pnl_monthly p

INNER JOIN mart.dim_pnl_management_mapping m
    ON p.account_number::text = m.account_number::text

WHERE
    m.management_group = 'Operating Costs'
    AND m.is_active = TRUE
    AND p.account_number::integer IN (
        501,
        502,
        504,
        518,
        521,
        524,
        548,
        549,
        582
    )

ORDER BY
    p.calendar_year,
    p.calendar_month,
    p.account_number;
"""


# ============================================================
# VALIDATION METRICS
# ============================================================

def mae(
    actual: np.ndarray,
    predicted: np.ndarray,
) -> float:
    """Mean Absolute Error."""
    return float(
        np.mean(
            np.abs(actual - predicted)
        )
    )


def rmse(
    actual: np.ndarray,
    predicted: np.ndarray,
) -> float:
    """Root Mean Squared Error."""
    return float(
        np.sqrt(
            np.mean(
                (actual - predicted) ** 2
            )
        )
    )


def mape(
    actual: np.ndarray,
    predicted: np.ndarray,
) -> float:
    """
    Mean Absolute Percentage Error.

    Zero actual values are excluded.
    """
    mask = actual != 0

    if not np.any(mask):
        return float("nan")

    return float(
        np.mean(
            np.abs(
                (
                    actual[mask]
                    - predicted[mask]
                )
                / actual[mask]
            )
        )
        * 100
    )


# ============================================================
# DATABASE
# ============================================================

def validate_db_config() -> None:
    """Validate required database configuration."""

    required = {
        "DB_HOST": DB_CONFIG["host"],
        "DB_PORT": DB_CONFIG["port"],
        "DB_NAME": DB_CONFIG["database"],
        "DB_USER": DB_CONFIG["user"],
        "DB_PASSWORD": DB_CONFIG["password"],
    }

    missing = [
        key
        for key, value in required.items()
        if value is None or value == ""
    ]

    if missing:
        raise RuntimeError(
            "Missing database environment variables: "
            + ", ".join(missing)
        )


def get_connection():
    """Create PostgreSQL connection."""
    validate_db_config()
    return psycopg2.connect(**DB_CONFIG)


# ============================================================
# DATA LOADING
# ============================================================

def load_data() -> pd.DataFrame:
    """Load operating cost history from PostgreSQL."""

    connection = None

    try:
        logger.info(
            "Loading operating cost history from PostgreSQL."
        )

        connection = get_connection()

        df = pd.read_sql_query(
            SOURCE_QUERY,
            connection,
        )

        if df.empty:
            raise ValueError(
                "Expense source dataset is empty."
            )

        return df

    finally:
        if connection is not None:
            connection.close()


# ============================================================
# PREPARATION
# ============================================================

def prepare_data(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Prepare monthly management-sign expense series."""

    required_columns = {
        "year_month",
        "account_number",
        "account_name",
        "management_line",
        "management_sign",
        "signed_amount",
    }

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(sorted(missing))
        )

    df = df.copy()

    df["period"] = pd.to_datetime(
        df["year_month"] + "-01",
        errors="coerce",
    )

    df["account_number"] = (
        pd.to_numeric(
            df["account_number"],
            errors="raise",
        )
        .astype(int)
    )

    df["signed_amount"] = pd.to_numeric(
        df["signed_amount"],
        errors="coerce",
    )

    df["management_sign"] = pd.to_numeric(
        df["management_sign"],
        errors="raise",
    )

    df["management_amount"] = (
        df["signed_amount"]
        * df["management_sign"]
    )

    # Management costs should be negative.
    # We forecast the positive consumption amount because
    # this is easier to interpret in controller reports.
    df["expense_amount"] = (
        -df["management_amount"]
    )

    df = df.dropna(
        subset=[
            "period",
            "expense_amount",
        ]
    )

    return df.sort_values(
        [
            "account_number",
            "period",
        ]
    )


# ============================================================
# MODEL FUNCTIONS
# ============================================================

def seasonal_naive_forecast(
    train: pd.Series,
    horizon: int,
    season_length: int = 12,
) -> np.ndarray:
    """Seasonal naive forecast."""

    values = train.to_numpy(
        dtype=float
    )

    if len(values) < season_length:
        return np.repeat(
            values[-1],
            horizon,
        )

    forecast = []

    for step in range(horizon):

        index = (
            len(values)
            - season_length
            + step
        )

        if index < len(values):
            forecast.append(
                values[index]
            )
        else:
            forecast.append(
                forecast[-season_length]
            )

    return np.asarray(
        forecast,
        dtype=float,
    )


def holt_winters_forecast(
    train: pd.Series,
    horizon: int,
) -> np.ndarray:
    """Holt-Winters additive trend and seasonality."""

    model = ExponentialSmoothing(
        train.astype(float),
        trend="add",
        seasonal="add",
        seasonal_periods=12,
        initialization_method="estimated",
    )

    fitted = model.fit(
        optimized=True,
        use_brute=True,
    )

    forecast = fitted.forecast(
        horizon
    )

    return np.asarray(
        forecast,
        dtype=float,
    )


# ============================================================
# MODEL VALIDATION
# ============================================================

def validate_models(
    series: pd.Series,
) -> pd.DataFrame:
    """Backtest forecasting models."""

    if len(series) < (
        VALIDATION_MONTHS + 3
    ):
        raise ValueError(
            "Not enough observations for validation."
        )

    train = series.iloc[
        :-VALIDATION_MONTHS
    ]

    test = series.iloc[
        -VALIDATION_MONTHS:
    ]

    actual = test.to_numpy(
        dtype=float
    )

    results = []

    # --------------------------------------------------------
    # Seasonal Naive
    # --------------------------------------------------------

    naive_prediction = (
        seasonal_naive_forecast(
            train=train,
            horizon=VALIDATION_MONTHS,
            season_length=SEASON_LENGTH,
        )
    )

    results.append(
        {
            "model": "SeasonalNaive",
            "mae": mae(
                actual,
                naive_prediction,
            ),
            "rmse": rmse(
                actual,
                naive_prediction,
            ),
            "mape_pct": mape(
                actual,
                naive_prediction,
            ),
        }
    )

    # --------------------------------------------------------
    # Holt-Winters
    # --------------------------------------------------------

    try:

        hw_prediction = (
            holt_winters_forecast(
                train=train,
                horizon=VALIDATION_MONTHS,
            )
        )

        results.append(
            {
                "model": "HoltWinters",
                "mae": mae(
                    actual,
                    hw_prediction,
                ),
                "rmse": rmse(
                    actual,
                    hw_prediction,
                ),
                "mape_pct": mape(
                    actual,
                    hw_prediction,
                ),
            }
        )

    except Exception as exc:

        logger.warning(
            "Holt-Winters failed during validation: %s",
            exc,
        )

    return pd.DataFrame(
        results
    )


def select_model(
    validation: pd.DataFrame,
) -> str:
    """Select model with lowest RMSE."""

    if validation.empty:
        raise ValueError(
            "No forecasting model available."
        )

    best = (
        validation
        .sort_values("rmse")
        .iloc[0]
    )

    return str(
        best["model"]
    )


# ============================================================
# FORECAST ONE SERIES
# ============================================================

def forecast_series(
    series: pd.Series,
) -> tuple[str, pd.DataFrame]:
    """Validate, select and forecast one expense series."""

    series = (
        series
        .sort_index()
        .asfreq("MS")
    )

    if series.isna().any():
        # Missing months represent zero recorded expense
        # for this management line.
        series = series.fillna(0)

    if len(series) < MIN_REQUIRED_MONTHS:
        raise ValueError(
            "Not enough history for forecasting."
        )

    validation = validate_models(
        series
    )

    selected_model = select_model(
        validation
    )

    logger.info(
        "Selected %s",
        selected_model,
    )

    if selected_model == "SeasonalNaive":

        forecast_values = (
            seasonal_naive_forecast(
                train=series,
                horizon=FORECAST_HORIZON,
                season_length=SEASON_LENGTH,
            )
        )

    elif selected_model == "HoltWinters":

        forecast_values = (
            holt_winters_forecast(
                train=series,
                horizon=FORECAST_HORIZON,
            )
        )

    else:
        raise ValueError(
            f"Unsupported model: {selected_model}"
        )

    selected_metrics = validation[
        validation["model"] == selected_model
    ]

    rmse_value = float(
        selected_metrics.iloc[0]["rmse"]
    )

    last_period = series.index.max()

    future_index = pd.date_range(
        start=(
            last_period
            + pd.offsets.MonthBegin(1)
        ),
        periods=FORECAST_HORIZON,
        freq="MS",
    )

    result = pd.DataFrame(
        {
            "forecast_period": future_index,
            "forecast_expense": np.maximum(
                forecast_values,
                0,
            ),
            "model": selected_model,
            "validation_rmse": rmse_value,
        }
    )

    result["lower_bound"] = np.maximum(
        result["forecast_expense"]
        - 1.96 * rmse_value,
        0,
    )

    result["upper_bound"] = (
        result["forecast_expense"]
        + 1.96 * rmse_value
    )

    result["year_month"] = (
        result["forecast_period"]
        .dt.strftime("%Y-%m")
    )

    return (
        selected_model,
        result,
    )


# ============================================================
# MAIN FORECAST PIPELINE
# ============================================================

def create_expense_forecast(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Forecast all configured operating cost lines."""

    output_frames = []

    for account_number, account_label in (
        EXPENSE_ACCOUNTS.items()
    ):

        logger.info(
            "Forecasting account %s - %s",
            account_number,
            account_label,
        )

        account_df = df[
            df["account_number"]
            == account_number
        ].copy()

        if account_df.empty:
            logger.warning(
                "No history found for account %s.",
                account_number,
            )
            continue

        series = (
            account_df
            .groupby("period")[
                "expense_amount"
            ]
            .sum()
            .sort_index()
        )

        if len(series) < MIN_REQUIRED_MONTHS:
            logger.warning(
                "Skipping %s - only %s observations.",
                account_number,
                len(series),
            )
            continue

        try:

            selected_model, forecast = (
                forecast_series(series)
            )

            forecast["account_number"] = (
                account_number
            )

            forecast["account_name"] = (
                account_label
            )

            forecast["selected_model"] = (
                selected_model
            )

            output_frames.append(
                forecast
            )

        except Exception as exc:

            logger.exception(
                "Forecast failed for account %s: %s",
                account_number,
                exc,
            )

    if not output_frames:
        raise RuntimeError(
            "No expense forecasts were generated."
        )

    result = pd.concat(
        output_frames,
        ignore_index=True,
    )

    result = result[
        [
            "forecast_period",
            "year_month",
            "account_number",
            "account_name",
            "forecast_expense",
            "lower_bound",
            "upper_bound",
            "selected_model",
            "validation_rmse",
        ]
    ]

    return result.sort_values(
        [
            "forecast_period",
            "account_number",
        ]
    ).reset_index(drop=True)


# ============================================================
# SAVE
# ============================================================

def save_output(
    df: pd.DataFrame,
) -> None:
    """Save expense forecast CSV."""

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    logger.info(
        "Expense forecast saved to %s",
        OUTPUT_FILE,
    )


# ============================================================
# MAIN
# ============================================================

def main() -> int:
    """Run expense forecasting."""

    try:

        logger.info(
            "Starting EFAP Expense Forecast."
        )

        source = load_data()

        prepared = prepare_data(
            source
        )

        result = create_expense_forecast(
            prepared
        )

        save_output(
            result
        )

        logger.info(
            "Expense Forecast completed successfully."
        )

        logger.info(
            "Generated %s forecast rows.",
            len(result),
        )

        return 0

    except Exception as exc:

        logger.exception(
            "Expense Forecast failed: %s",
            exc,
        )

        return 1


if __name__ == "__main__":
    sys.exit(main())