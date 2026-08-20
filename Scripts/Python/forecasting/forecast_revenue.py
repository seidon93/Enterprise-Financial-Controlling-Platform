"""
EFAP - Revenue Forecast

Object:
    Python/forecasting/forecast_revenue.py

Purpose:
    Forecast monthly Revenue using:
        1. Seasonal Naive baseline
        2. Holt-Winters Exponential Smoothing

Input:
    data/processed/controller_kpi_timeseries.csv

Output:
    data/forecasts/revenue_forecast.csv

Forecast horizon:
    6 months

Model selection:
    Lowest validation RMSE

Important:
    Financial definitions remain in PostgreSQL.
    This Python module only performs forecasting.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

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

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "controller_kpi_timeseries.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "forecasts"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "revenue_forecast.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

FORECAST_HORIZON = 6

VALIDATION_MONTHS = 6

MIN_REQUIRED_MONTHS = 18


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# ============================================================
# DATA LOADING
# ============================================================

def load_data() -> pd.DataFrame:
    """Load the canonical EFAP time-series dataset."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    logger.info(
        "Loading revenue time-series data from %s",
        INPUT_FILE,
    )

    df = pd.read_csv(INPUT_FILE)

    required_columns = {
        "period",
        "revenue",
    }

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(sorted(missing))
        )

    df["period"] = pd.to_datetime(
        df["period"],
        errors="coerce",
    )

    df["revenue"] = pd.to_numeric(
        df["revenue"],
        errors="coerce",
    )

    df = (
        df[
            [
                "period",
                "revenue",
            ]
        ]
        .dropna()
        .sort_values("period")
        .drop_duplicates("period")
        .reset_index(drop=True)
    )

    if len(df) < MIN_REQUIRED_MONTHS:
        raise ValueError(
            f"At least {MIN_REQUIRED_MONTHS} monthly observations "
            f"are required. Found {len(df)}."
        )

    return df


# ============================================================
# METRICS
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
# SEASONAL NAIVE
# ============================================================

def seasonal_naive_forecast(
    train: pd.Series,
    horizon: int,
    season_length: int = 12,
) -> np.ndarray:
    """
    Seasonal naive forecast.

    Forecast = same month from previous year.

    Fallback:
        If fewer than 12 observations exist, use last value.
    """

    if len(train) < season_length:
        return np.repeat(
            train.iloc[-1],
            horizon,
        )

    values = train.to_numpy()

    forecast = []

    for step in range(horizon):
        source_index = (
            len(values)
            - season_length
            + step
        )

        if source_index < len(values):
            forecast.append(
                values[source_index]
            )
        else:
            forecast.append(
                forecast[-season_length]
            )

    return np.asarray(
        forecast,
        dtype=float,
    )


# ============================================================
# HOLT-WINTERS
# ============================================================

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
# BACKTEST
# ============================================================

def validate_models(
    series: pd.Series,
) -> pd.DataFrame:
    """
    Backtest both models on the latest validation window.
    """

    if len(series) <= VALIDATION_MONTHS:
        raise ValueError(
            "Not enough observations for validation."
        )

    train = series.iloc[
        :-VALIDATION_MONTHS
    ]

    test = series.iloc[
        -VALIDATION_MONTHS:
    ]

    actual = test.to_numpy()

    # --------------------------------------------------------
    # Seasonal Naive
    # --------------------------------------------------------

    naive_pred = seasonal_naive_forecast(
        train=train,
        horizon=VALIDATION_MONTHS,
        season_length=12,
    )

    naive_metrics = {
        "model": "SeasonalNaive",
        "mae": mae(actual, naive_pred),
        "rmse": rmse(actual, naive_pred),
        "mape_pct": mape(actual, naive_pred),
    }

    results = [
        naive_metrics
    ]

    # --------------------------------------------------------
    # Holt-Winters
    # --------------------------------------------------------

    try:
        hw_pred = holt_winters_forecast(
            train=train,
            horizon=VALIDATION_MONTHS,
        )

        results.append(
            {
                "model": "HoltWinters",
                "mae": mae(actual, hw_pred),
                "rmse": rmse(actual, hw_pred),
                "mape_pct": mape(actual, hw_pred),
            }
        )

    except Exception as exc:
        logger.warning(
            "Holt-Winters validation failed: %s",
            exc,
        )

    return pd.DataFrame(results)


# ============================================================
# MODEL SELECTION
# ============================================================

def select_model(
    validation_results: pd.DataFrame,
) -> str:
    """Select the model with the lowest RMSE."""

    if validation_results.empty:
        raise ValueError(
            "No forecasting model passed validation."
        )

    best = (
        validation_results
        .sort_values(
            by="rmse",
            ascending=True,
        )
        .iloc[0]
    )

    model_name = str(
        best["model"]
    )

    logger.info(
        "Selected model: %s | RMSE: %.2f",
        model_name,
        best["rmse"],
    )

    return model_name


# ============================================================
# FINAL FORECAST
# ============================================================

def create_forecast(
    df: pd.DataFrame,
    model_name: str,
) -> pd.DataFrame:
    """Fit selected model on all history and generate forecast."""

    series = (
        df
        .set_index("period")["revenue"]
        .asfreq("MS")
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

    # --------------------------------------------------------
    # Forecast
    # --------------------------------------------------------

    if model_name == "SeasonalNaive":

        forecast_values = (
            seasonal_naive_forecast(
                train=series,
                horizon=FORECAST_HORIZON,
                season_length=12,
            )
        )

    elif model_name == "HoltWinters":

        forecast_values = (
            holt_winters_forecast(
                train=series,
                horizon=FORECAST_HORIZON,
            )
        )

    else:
        raise ValueError(
            f"Unsupported model: {model_name}"
        )

    # --------------------------------------------------------
    # Estimate forecast uncertainty
    #
    # For a portfolio forecasting layer we use historical
    # validation residuals to create a transparent interval.
    # --------------------------------------------------------

    validation = validate_models(
        series
    )

    selected_row = validation[
        validation["model"] == model_name
    ]

    if selected_row.empty:
        raise ValueError(
            "Selected model has no validation results."
        )

    rmse_value = float(
        selected_row.iloc[0]["rmse"]
    )

    lower_bound = (
        forecast_values
        - 1.96 * rmse_value
    )

    upper_bound = (
        forecast_values
        + 1.96 * rmse_value
    )

    result = pd.DataFrame(
        {
            "forecast_period": future_index,
            "forecast_revenue": forecast_values,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "model": model_name,
            "validation_rmse": rmse_value,
        }
    )

    result["forecast_year"] = (
        result["forecast_period"]
        .dt.year
        .astype(int)
    )

    result["forecast_month"] = (
        result["forecast_period"]
        .dt.month
        .astype(int)
    )

    result["year_month"] = (
        result["forecast_period"]
        .dt.strftime("%Y-%m")
    )

    return result


# ============================================================
# OUTPUT
# ============================================================

def save_forecast(
    forecast_df: pd.DataFrame,
) -> None:
    """Save revenue forecast dataset."""

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    forecast_df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    logger.info(
        "Revenue forecast saved to %s",
        OUTPUT_FILE,
    )


# ============================================================
# MAIN
# ============================================================

def main() -> int:
    """Run revenue forecasting pipeline."""

    try:

        logger.info(
            "Starting EFAP Revenue Forecast."
        )

        df = load_data()

        series = (
            df
            .set_index("period")["revenue"]
            .asfreq("MS")
        )

        validation_results = validate_models(
            series
        )

        logger.info(
            "\n%s",
            validation_results.to_string(
                index=False
            ),
        )

        selected_model = select_model(
            validation_results
        )

        forecast_df = create_forecast(
            df=df,
            model_name=selected_model,
        )

        save_forecast(
            forecast_df
        )

        logger.info(
            "Forecast completed successfully."
        )

        return 0

    except Exception as exc:
        logger.exception(
            "Revenue Forecast failed: %s",
            exc,
        )

        return 1


if __name__ == "__main__":
    sys.exit(main())