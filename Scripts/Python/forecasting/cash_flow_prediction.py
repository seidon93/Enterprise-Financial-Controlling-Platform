"""
EFAP - Cash Flow Prediction

Object:
    Scripts/Python/forecasting/cash_flow_prediction.py

Purpose:
    Predict future Operating Cash Flow and Closing Cash.

Sources:
    data/processed/controller_kpi_timeseries.csv
    data/predictions/revenue_prediction.csv
    data/forecasts/expense_forecast.csv

Models:
    - Robust historical baseline
    - HistGradientBoostingRegressor

Forecast logic:
    1. Load historical financial data.
    2. Normalize management sign conventions.
    3. Load Revenue ML forecast.
    4. Load Expense forecast.
    5. Build a robust historical OCF baseline.
    6. Validate baseline.
    7. Validate HistGradientBoosting.
    8. Select the better forecasting method.
    9. Forecast Operating Cash Flow for six months.
    10. Build Closing Cash recursively.
    11. Validate forecast quality and cash bridge.
    12. Export Power BI-ready prediction output.

Management sign convention:
    Revenue              >= 0
    Operating Costs      <= 0
    Operating Cash Flow  signed
    Closing Cash         >= 0 unless historical data proves otherwise

Important:
    - PostgreSQL remains the financial source of truth.
    - This module performs predictive / forecasting analytics only.
    - No database credentials are stored in source code.
    - ML is not automatically preferred over the baseline.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Final

import numpy as np
import pandas as pd

try:
    from sklearn.ensemble import HistGradientBoostingRegressor
except ImportError as exc:
    raise ImportError(
        "Missing dependency 'scikit-learn'. "
        "Install with: pip install scikit-learn"
    ) from exc

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
)


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT: Final[Path] = (
    Path(__file__).resolve().parents[3]
)

TIME_SERIES_FILE: Final[Path] = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "controller_kpi_timeseries.csv"
)

REVENUE_PREDICTION_FILE: Final[Path] = (
    PROJECT_ROOT
    / "data"
    / "predictions"
    / "revenue_prediction.csv"
)

EXPENSE_FORECAST_FILE: Final[Path] = (
    PROJECT_ROOT
    / "data"
    / "forecasts"
    / "expense_forecast.csv"
)

OUTPUT_DIR: Final[Path] = (
    PROJECT_ROOT
    / "data"
    / "predictions"
)

OUTPUT_FILE: Final[Path] = (
    OUTPUT_DIR
    / "cash_flow_prediction.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

HORIZON: Final[int] = 6

VALIDATION_MONTHS: Final[int] = 6

MIN_HISTORY: Final[int] = 24

RANDOM_STATE: Final[int] = 42

# ------------------------------------------------------------
# MODEL SELECTION
# ------------------------------------------------------------

# ML must outperform the baseline by at least this amount
# to become the selected production forecast method.
ML_MIN_IMPROVEMENT_PCT: Final[float] = 5.0

# Composite score weights.
# Lower score = better model.
RMSE_WEIGHT: Final[float] = 0.50
SMAPE_WEIGHT: Final[float] = 0.30
RESIDUAL_STD_WEIGHT: Final[float] = 0.20

# Stabilized MAPE denominator.
MAPE_EPSILON: Final[float] = 1_000_000.0

# Robust baseline window.
BASELINE_WINDOW: Final[int] = 6

# Confidence thresholds.
HIGH_CONFIDENCE_SMAPE: Final[float] = 50.0
MEDIUM_CONFIDENCE_SMAPE: Final[float] = 100.0


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

def validate_files() -> None:
    """Validate required source files."""

    required_files = {
        "controller KPI time series": TIME_SERIES_FILE,
        "Revenue prediction": REVENUE_PREDICTION_FILE,
        "Expense forecast": EXPENSE_FORECAST_FILE,
    }

    missing = [
        f"{name}: {path}"
        for name, path in required_files.items()
        if not path.exists()
    ]

    if missing:
        raise FileNotFoundError(
            "Missing required EFAP Cash Flow source files:\n"
            + "\n".join(missing)
        )


# ============================================================
# PERIOD HELPERS
# ============================================================

def normalize_period_series(
    series: pd.Series,
) -> pd.Series:
    """
    Normalize dates to monthly-start timestamps.
    """

    return (
        pd.to_datetime(
            series,
            errors="coerce",
        )
        .dt.to_period("M")
        .dt.to_timestamp()
    )


# ============================================================
# METRIC HELPERS
# ============================================================

def calculate_smape(
    actual: np.ndarray,
    predicted: np.ndarray,
) -> float:
    """
    Calculate symmetric MAPE.
    """

    denominator = (
        np.abs(actual)
        + np.abs(predicted)
    )

    valid = denominator > 0

    if not np.any(valid):
        return 0.0

    numerator = (
        2.0
        * np.abs(
            actual[valid]
            - predicted[valid]
        )
    )

    percentage_errors = (
        numerator
        / denominator[valid]
    )

    return float(
        np.mean(
            percentage_errors
        ) * 100.0
    )

def calculate_stabilized_mape(
    actual: np.ndarray,
    predicted: np.ndarray,
    epsilon: float = MAPE_EPSILON,
) -> float:
    """
    Calculate stabilized MAPE.

    Prevents very small actual values from creating
    mathematically extreme percentages.
    """

    denominator = np.maximum(
        np.abs(actual),
        epsilon,
    )

    percentage_errors = np.abs(
        (actual - predicted)
        / denominator
    )

    return float(
        np.mean(
            percentage_errors
        ) * 100.0
    )

def calculate_metrics(
    actual: np.ndarray,
    predicted: np.ndarray,
) -> dict[str, float]:
    """
    Calculate forecast validation metrics.
    """

    mae = mean_absolute_error(
        actual,
        predicted,
    )

    rmse = np.sqrt(
        mean_squared_error(
            actual,
            predicted,
        )
    )

    smape = calculate_smape(
        actual,
        predicted,
    )

    stabilized_mape = (
        calculate_stabilized_mape(
            actual,
            predicted,
        )
    )

    residuals = (
        actual
        - predicted
    )

    residual_std = float(
        np.std(
            residuals,
            ddof=1,
        )
        if len(residuals) > 1
        else 0.0
    )

    return {
        "mae": float(mae),
        "rmse": float(rmse),
        "smape_pct": float(smape),
        "stabilized_mape_pct": float(
            stabilized_mape
        ),
        "residual_std": residual_std,
    }


def calculate_composite_score(
    metrics: dict[str, float],
) -> float:
    """
    Calculate normalized composite model score.

    Lower score is better.

    The score is intentionally based on relative scale-normalized
    error components instead of simply summing raw currency values.
    """

    rmse = abs(
        metrics["rmse"]
    )

    smape = abs(
        metrics["smape_pct"]
    )

    residual_std = abs(
        metrics["residual_std"]
    )

    # Currency-scale metrics are normalized using RMSE itself
    # when possible, preventing one component from dominating
    # purely because of units.
    normalized_rmse = (
        1.0
        if rmse > 0
        else 0.0
    )

    normalized_residual_std = (
        residual_std / rmse
        if rmse > 0
        else 0.0
    )

    normalized_smape = (
        smape / 100.0
    )

    score = (
        RMSE_WEIGHT
        * normalized_rmse
        + SMAPE_WEIGHT
        * normalized_smape
        + RESIDUAL_STD_WEIGHT
        * normalized_residual_std
    )

    return float(score)


# ============================================================
# LOAD HISTORICAL DATA
# ============================================================

def load_historical_data() -> pd.DataFrame:
    """
    Load canonical historical controller KPI time series.

    Revenue is normalized to positive management convention.
    Operating costs remain negative.
    """

    logger.info(
        "Loading Cash Flow Prediction input: %s",
        TIME_SERIES_FILE,
    )

    df = pd.read_csv(
        TIME_SERIES_FILE
    )

    required = {
        "period",
        "revenue",
        "operating_costs",
        "net_profit",
        "net_working_capital",
        "operating_cash_flow",
        "closing_cash",
    }

    missing = (
        required
        - set(df.columns)
    )

    if missing:
        raise ValueError(
            "Historical data is missing columns: "
            + ", ".join(
                sorted(missing)
            )
        )

    df["period"] = normalize_period_series(
        df["period"]
    )

    numeric_columns = [
        "revenue",
        "operating_costs",
        "net_profit",
        "net_working_capital",
        "operating_cash_flow",
        "closing_cash",
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
                "net_profit",
                "net_working_capital",
                "operating_cash_flow",
                "closing_cash",
            ]
        ]
        .dropna(
            subset=[
                "period",
                "revenue",
                "operating_costs",
                "operating_cash_flow",
                "closing_cash",
            ]
        )
        .sort_values("period")
        .drop_duplicates(
            "period",
            keep="last",
        )
        .reset_index(drop=True)
    )

    if df.empty:
        raise RuntimeError(
            "Historical Cash Flow dataset is empty."
        )

    # --------------------------------------------------------
    # MANAGEMENT SIGN CONVENTION
    # --------------------------------------------------------

    negative_revenue_count = int(
        (
            df["revenue"]
            < 0
        ).sum()
    )

    if negative_revenue_count > 0:

        logger.info(
            "Normalizing %s negative Revenue values "
            "to positive management convention.",
            negative_revenue_count,
        )

        df["revenue"] = (
            df["revenue"]
            .abs()
        )

    logger.info(
        "Revenue sign normalized to management convention: "
        "Revenue >= 0."
    )

    # Operating costs must be negative.
    df["operating_costs"] = (
        -df["operating_costs"]
        .abs()
    )

    # --------------------------------------------------------
    # MONTHLY FREQUENCY
    # --------------------------------------------------------

    df = (
        df
        .set_index("period")
        .asfreq("MS")
        .reset_index()
    )

    if len(df) < MIN_HISTORY:
        raise ValueError(
            f"At least {MIN_HISTORY} monthly observations "
            f"are required. Found {len(df)}."
        )

    logger.info(
        "Loaded %s historical monthly observations.",
        len(df),
    )

    logger.info(
        "Historical period: %s -> %s",
        df["period"].min().strftime("%Y-%m"),
        df["period"].max().strftime("%Y-%m"),
    )

    return df


# ============================================================
# LOAD REVENUE PREDICTION
# ============================================================

def load_revenue_prediction() -> pd.DataFrame:
    """
    Load Revenue ML prediction.

    Revenue is normalized to positive management convention.
    """

    logger.info(
        "Loading Revenue prediction: %s",
        REVENUE_PREDICTION_FILE,
    )

    df = pd.read_csv(
        REVENUE_PREDICTION_FILE
    )

    required = {
        "period",
        "predicted_revenue",
    }

    missing = (
        required
        - set(df.columns)
    )

    if missing:
        raise ValueError(
            "Revenue prediction is missing columns: "
            + ", ".join(
                sorted(missing)
            )
        )

    df["period"] = normalize_period_series(
        df["period"]
    )

    df["predicted_revenue"] = pd.to_numeric(
        df["predicted_revenue"],
        errors="coerce",
    )

    df = (
        df[
            [
                "period",
                "predicted_revenue",
            ]
        ]
        .dropna(
            subset=[
                "period",
                "predicted_revenue",
            ]
        )
        .sort_values("period")
        .drop_duplicates(
            "period",
            keep="last",
        )
        .reset_index(drop=True)
    )

    # --------------------------------------------------------
    # MANAGEMENT SIGN CONVENTION
    # --------------------------------------------------------

    negative_predictions = int(
        (
            df["predicted_revenue"]
            < 0
        ).sum()
    )

    if negative_predictions > 0:

        logger.warning(
            "Revenue prediction contains %s negative "
            "values. Normalizing with absolute value.",
            negative_predictions,
        )

        df["predicted_revenue"] = (
            df["predicted_revenue"]
            .abs()
        )

    df["predicted_revenue"] = (
        df["predicted_revenue"]
        .clip(lower=0)
    )

    logger.info(
        "Revenue prediction periods: %s",
        len(df),
    )

    return df


# ============================================================
# LOAD EXPENSE FORECAST
# ============================================================

def load_expense_forecast() -> pd.DataFrame:
    """
    Load account-level expense forecast.

    Source schema:

        forecast_period
        year_month
        account_number
        account_name
        forecast_expense
        lower_bound
        upper_bound
        selected_model
        validation_rmse

    The source contains positive expense magnitude.

    Management reporting convention:

        Operating Costs = negative magnitude
    """

    logger.info(
        "Loading Expense forecast: %s",
        EXPENSE_FORECAST_FILE,
    )

    df = pd.read_csv(
        EXPENSE_FORECAST_FILE
    )

    required = {
        "forecast_period",
        "forecast_expense",
    }

    missing = (
        required
        - set(df.columns)
    )

    if missing:
        raise ValueError(
            "Expense forecast is missing columns: "
            + ", ".join(
                sorted(missing)
            )
        )

    df["period"] = normalize_period_series(
        df["forecast_period"]
    )

    df["forecast_expense"] = pd.to_numeric(
        df["forecast_expense"],
        errors="coerce",
    )

    df = df.dropna(
        subset=[
            "period",
            "forecast_expense",
        ]
    ).copy()

    # Forecast expense is an expense magnitude.
    # Convert to positive magnitude first.
    df["forecast_expense"] = (
        df["forecast_expense"]
        .abs()
    )

    # --------------------------------------------------------
    # MONTHLY AGGREGATION
    # --------------------------------------------------------

    monthly = (
        df
        .groupby(
            "period",
            as_index=False,
        )
        .agg(
            predicted_expense=(
                "forecast_expense",
                "sum",
            )
        )
        .sort_values("period")
        .reset_index(drop=True)
    )

    if monthly.empty:
        raise RuntimeError(
            "Expense forecast produced no monthly periods."
        )

    logger.info(
        "Expense forecast periods: %s",
        len(monthly),
    )

    return monthly


# ============================================================
# BUILD FUTURE DRIVER DATASET
# ============================================================

def build_future_driver_dataset(
    history: pd.DataFrame,
    revenue_prediction: pd.DataFrame,
    expense_forecast: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build six-month future driver dataset.

    Revenue:
        positive

    Operating costs:
        negative

    Net profit / NWC:
        unknown and therefore not used directly as future
        external drivers in the selected baseline.

    Expense forecast may contain an extra historical/current
    month; only the six future months after the latest actual
    are used.
    """

    actual_cutoff = (
        history["period"]
        .max()
    )

    future_revenue = (
        revenue_prediction[
            revenue_prediction["period"]
            > actual_cutoff
        ]
        .copy()
    )

    future_expense = (
        expense_forecast[
            expense_forecast["period"]
            > actual_cutoff
        ]
        .copy()
    )

    # --------------------------------------------------------
    # LIMIT TO EXPECTED HORIZON
    # --------------------------------------------------------

    future_revenue = (
        future_revenue
        .sort_values("period")
        .head(HORIZON)
    )

    future_expense = (
        future_expense
        .sort_values("period")
        .head(HORIZON)
    )

    if (
        len(future_revenue)
        != HORIZON
    ):
        raise RuntimeError(
            "Revenue prediction horizon mismatch: "
            f"expected {HORIZON}, "
            f"found {len(future_revenue)}."
        )

    if (
        len(future_expense)
        != HORIZON
    ):
        raise RuntimeError(
            "Expense forecast horizon mismatch: "
            f"expected {HORIZON}, "
            f"found {len(future_expense)}."
        )

    future_periods = (
        pd.date_range(
            start=(
                actual_cutoff
                + pd.offsets.MonthBegin(1)
            ),
            periods=HORIZON,
            freq="MS",
        )
    )

    revenue_periods = set(
        future_revenue["period"]
    )

    expense_periods = set(
        future_expense["period"]
    )

    expected_periods = set(
        future_periods
    )

    if revenue_periods != expected_periods:
        raise RuntimeError(
            "Revenue prediction periods do not match "
            "the expected six-month horizon."
        )

    if expense_periods != expected_periods:
        raise RuntimeError(
            "Expense forecast periods do not match "
            "the expected six-month horizon."
        )

    future = pd.DataFrame(
        {
            "period": future_periods
        }
    )

    future = (
        future
        .merge(
            future_revenue[
                [
                    "period",
                    "predicted_revenue",
                ]
            ],
            on="period",
            how="left",
            validate="one_to_one",
        )
        .merge(
            future_expense[
                [
                    "period",
                    "predicted_expense",
                ]
            ],
            on="period",
            how="left",
            validate="one_to_one",
        )
    )

    future["predicted_revenue"] = (
        future["predicted_revenue"]
        .abs()
        .clip(lower=0)
    )

    future["predicted_expense"] = (
        future["predicted_expense"]
        .abs()
    )

    future["predicted_operating_costs"] = (
        -future["predicted_expense"]
    )

    if (
        future[
            "predicted_revenue"
        ].isna().any()
    ):
        raise RuntimeError(
            "Future Revenue driver contains missing values."
        )

    if (
        future[
            "predicted_operating_costs"
        ].isna().any()
    ):
        raise RuntimeError(
            "Future Expense driver contains missing values."
        )

    logger.info(
        "Future driver horizon: %s months.",
        len(future),
    )

    logger.info(
        "Forecast period: %s -> %s",
        future["period"].min().strftime("%Y-%m"),
        future["period"].max().strftime("%Y-%m"),
    )

    return future


# ============================================================
# OCF FEATURE ENGINEERING
# ============================================================

def create_ocf_features(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create historical features for Operating Cash Flow.

    Only lagged historical values are used to avoid leakage.
    """

    result = df.copy()

    result["month"] = (
        result["period"].dt.month
    )

    result["quarter"] = (
        result["period"].dt.quarter
    )

    result["month_sin"] = np.sin(
        2
        * np.pi
        * result["month"]
        / 12.0
    )

    result["month_cos"] = np.cos(
        2
        * np.pi
        * result["month"]
        / 12.0
    )

    result["time_index"] = np.arange(
        len(result)
    )

    # --------------------------------------------------------
    # Revenue
    # --------------------------------------------------------

    result["revenue_lag_1"] = (
        result["revenue"]
        .shift(1)
    )

    result["revenue_lag_3"] = (
        result["revenue"]
        .shift(3)
    )

    result["revenue_lag_12"] = (
        result["revenue"]
        .shift(12)
    )

    # --------------------------------------------------------
    # Operating Costs
    # --------------------------------------------------------

    result["operating_costs_lag_1"] = (
        result["operating_costs"]
        .shift(1)
    )

    result["operating_costs_lag_3"] = (
        result["operating_costs"]
        .shift(3)
    )

    result["operating_costs_lag_12"] = (
        result["operating_costs"]
        .shift(12)
    )

    # --------------------------------------------------------
    # Net Profit
    # --------------------------------------------------------

    result["net_profit_lag_1"] = (
        result["net_profit"]
        .shift(1)
    )

    result["net_profit_lag_3"] = (
        result["net_profit"]
        .shift(3)
    )

    # --------------------------------------------------------
    # Working Capital
    # --------------------------------------------------------

    result["nwc_lag_1"] = (
        result["net_working_capital"]
        .shift(1)
    )

    result["nwc_lag_3"] = (
        result["net_working_capital"]
        .shift(3)
    )

    result["nwc_change_lag_1"] = (
        result["net_working_capital"]
        .diff()
        .shift(1)
    )

    # --------------------------------------------------------
    # Cash
    # --------------------------------------------------------

    result["cash_lag_1"] = (
        result["closing_cash"]
        .shift(1)
    )

    result["cash_lag_3"] = (
        result["closing_cash"]
        .shift(3)
    )

    result["cash_lag_12"] = (
        result["closing_cash"]
        .shift(12)
    )

    # --------------------------------------------------------
    # OCF
    # --------------------------------------------------------

    result["ocf_lag_1"] = (
        result["operating_cash_flow"]
        .shift(1)
    )

    result["ocf_lag_3"] = (
        result["operating_cash_flow"]
        .shift(3)
    )

    result["ocf_lag_12"] = (
        result["operating_cash_flow"]
        .shift(12)
    )

    result["ocf_rolling_3"] = (
        result["operating_cash_flow"]
        .shift(1)
        .rolling(
            BASELINE_WINDOW,
            min_periods=3,
        )
        .mean()
    )

    result["ocf_rolling_6"] = (
        result["operating_cash_flow"]
        .shift(1)
        .rolling(
            6,
            min_periods=6,
        )
        .mean()
    )

    return result


FEATURE_COLUMNS: Final[list[str]] = [
    "month",
    "quarter",
    "month_sin",
    "month_cos",
    "time_index",

    "revenue_lag_1",
    "revenue_lag_3",
    "revenue_lag_12",

    "operating_costs_lag_1",
    "operating_costs_lag_3",
    "operating_costs_lag_12",

    "net_profit_lag_1",
    "net_profit_lag_3",

    "nwc_lag_1",
    "nwc_lag_3",
    "nwc_change_lag_1",

    "cash_lag_1",
    "cash_lag_3",
    "cash_lag_12",

    "ocf_lag_1",
    "ocf_lag_3",
    "ocf_lag_12",

    "ocf_rolling_3",
    "ocf_rolling_6",
]


# ============================================================
# ML MODEL
# ============================================================

def create_ml_model() -> HistGradientBoostingRegressor:
    """
    Create HistGradientBoosting regression model.
    """

    return HistGradientBoostingRegressor(
        learning_rate=0.05,
        max_iter=350,
        max_leaf_nodes=15,
        l2_regularization=1.0,
        random_state=RANDOM_STATE,
    )


# ============================================================
# TRAINING DATA
# ============================================================

def prepare_ml_training_data(
    history: pd.DataFrame,
) -> tuple[
    pd.DataFrame,
    pd.Series,
]:
    """
    Prepare historical OCF supervised learning dataset.
    """

    features = create_ocf_features(
        history
    )

    training = (
        features
        .dropna(
            subset=FEATURE_COLUMNS
            + ["operating_cash_flow"]
        )
        .copy()
    )

    if training.empty:
        raise RuntimeError(
            "No valid OCF observations remain after "
            "feature engineering."
        )

    return (
        training[FEATURE_COLUMNS],
        training["operating_cash_flow"],
    )


# ============================================================
# BASELINE
# ============================================================

def build_robust_baseline_predictions(
    train_history: pd.DataFrame,
    prediction_periods: pd.Series,
) -> np.ndarray:
    """
    Generate robust baseline OCF predictions.

    The baseline combines:
        - latest OCF
        - trailing 3-month OCF
        - same-month previous-year OCF
        - recent OCF / Revenue conversion ratio

    The objective is a stable controller-oriented baseline,
    not a high-complexity statistical model.
    """

    history = (
        train_history
        .sort_values("period")
        .reset_index(drop=True)
        .copy()
    )

    ocf = (
        history[
            "operating_cash_flow"
        ]
        .astype(float)
    )

    revenue = (
        history[
            "revenue"
        ]
        .astype(float)
        .replace(
            0,
            np.nan,
        )
    )

    recent_ocf = ocf.tail(
        BASELINE_WINDOW
    )

    latest_ocf = float(
        ocf.iloc[-1]
    )

    trailing_mean = float(
        recent_ocf.mean()
    )

    # --------------------------------------------------------
    # OCF / Revenue conversion
    # --------------------------------------------------------

    conversion = (
        ocf
        .tail(
            BASELINE_WINDOW
        )
        / revenue
        .tail(
            BASELINE_WINDOW
        )
    )

    conversion = conversion.replace(
        [np.inf, -np.inf],
        np.nan,
    ).dropna()

    if conversion.empty:
        recent_conversion = -1.0
    else:
        recent_conversion = float(
            conversion.median()
        )

    # --------------------------------------------------------
    # Forecast one month at a time.
    # --------------------------------------------------------

    predictions: list[float] = []

    working = history.copy()

    for period in prediction_periods:

        current_revenue = np.nan

        # Revenue is not part of this historical baseline
        # calculation directly. We therefore use the recent
        # Revenue median as a stable reference only when
        # calculating the conversion-based estimate.
        recent_revenue = (
            working[
                "revenue"
            ]
            .tail(
                BASELINE_WINDOW
            )
            .dropna()
        )

        if not recent_revenue.empty:
            current_revenue = float(
                recent_revenue.median()
            )

        conversion_based = (
            recent_conversion
            * current_revenue
            if pd.notna(current_revenue)
            else trailing_mean
        )

        # Robust ensemble:
        # 40% trailing mean
        # 30% latest OCF
        # 30% conversion-based estimate
        baseline_prediction = (
            0.40
            * trailing_mean
            + 0.30
            * latest_ocf
            + 0.30
            * conversion_based
        )

        predictions.append(
            float(
                baseline_prediction
            )
        )

        # Add predicted period to working history
        working = pd.concat(
            [
                working,
                pd.DataFrame(
                    {
                        "period": [period],
                        "revenue": [
                            current_revenue
                        ],
                        "operating_costs": [
                            np.nan
                        ],
                        "net_profit": [
                            np.nan
                        ],
                        "net_working_capital": [
                            np.nan
                        ],
                        "operating_cash_flow": [
                            baseline_prediction
                        ],
                        "closing_cash": [
                            np.nan
                        ],
                    }
                ),
            ],
            ignore_index=True,
        )

        latest_ocf = (
            baseline_prediction
        )

        trailing_mean = float(
            working[
                "operating_cash_flow"
            ]
            .tail(
                BASELINE_WINDOW
            )
            .mean()
        )

    return np.array(
        predictions,
        dtype=float,
    )


# ============================================================
# VALIDATION DATA
# ============================================================

def split_validation(
    X: pd.DataFrame,
    y: pd.Series,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.Series,
    pd.Series,
]:
    """
    Create chronological validation split.
    """

    if len(X) <= VALIDATION_MONTHS:
        raise ValueError(
            "Not enough OCF observations for validation."
        )

    split_index = (
        len(X)
        - VALIDATION_MONTHS
    )

    return (
        X.iloc[:split_index],
        X.iloc[split_index:],
        y.iloc[:split_index],
        y.iloc[split_index:],
    )


def validate_baseline_model(
    history: pd.DataFrame,
) -> dict[str, object]:
    """
    Validate robust baseline against latest historical months.
    """

    if len(history) < (
        VALIDATION_MONTHS
        + 12
    ):
        raise ValueError(
            "Insufficient history for robust baseline validation."
        )

    validation_start = (
        len(history)
        - VALIDATION_MONTHS
    )

    train_history = history.iloc[
        :validation_start
    ].copy()

    validation_history = history.iloc[
        validation_start:
    ].copy()

    predictions = (
        build_robust_baseline_predictions(
            train_history=train_history,
            prediction_periods=validation_history[
                "period"
            ],
        )
    )

    actual = (
        validation_history[
            "operating_cash_flow"
        ]
        .to_numpy(
            dtype=float
        )
    )

    metrics = calculate_metrics(
        actual=actual,
        predicted=predictions,
    )

    score = calculate_composite_score(
        metrics
    )

    logger.info(
        "Baseline validation:"
    )

    logger.info(
        "MAE: %.2f",
        metrics["mae"],
    )

    logger.info(
        "RMSE: %.2f",
        metrics["rmse"],
    )

    logger.info(
        "Stabilized MAPE: %.2f%%",
        metrics[
            "stabilized_mape_pct"
        ],
    )

    logger.info(
        "sMAPE: %.2f%%",
        metrics[
            "smape_pct"
        ],
    )

    logger.info(
        "Residual standard deviation: %.2f",
        metrics[
            "residual_std"
        ],
    )

    return {
        "metrics": metrics,
        "score": score,
        "predictions": predictions,
    }


# ============================================================
# ML VALIDATION
# ============================================================

def validate_ml_model(
    history: pd.DataFrame,
) -> dict[str, object]:
    """
    Validate HistGradientBoosting model.
    """

    X, y = (
        prepare_ml_training_data(
            history
        )
    )

    (
        X_train,
        X_test,
        y_train,
        y_test,
    ) = split_validation(
        X,
        y,
    )

    model = create_ml_model()

    model.fit(
        X_train,
        y_train,
    )

    prediction = (
        model.predict(
            X_test
        )
    )

    metrics = calculate_metrics(
        actual=y_test.to_numpy(
            dtype=float
        ),
        predicted=prediction,
    )

    score = (
        calculate_composite_score(
            metrics
        )
    )

    logger.info(
        "HistGradientBoosting validation:"
    )

    logger.info(
        "MAE: %.2f",
        metrics["mae"],
    )

    logger.info(
        "RMSE: %.2f",
        metrics["rmse"],
    )

    logger.info(
        "Stabilized MAPE: %.2f%%",
        metrics[
            "stabilized_mape_pct"
        ],
    )

    logger.info(
        "sMAPE: %.2f%%",
        metrics[
            "smape_pct"
        ],
    )

    logger.info(
        "Residual standard deviation: %.2f",
        metrics[
            "residual_std"
        ],
    )

    return {
        "metrics": metrics,
        "score": score,
        "predictions": prediction,
        "model": model,
    }


# ============================================================
# MODEL SELECTION
# ============================================================

def select_forecast_method(
    baseline_validation: dict[str, object],
    ml_validation: dict[str, object],
) -> dict[str, object]:
    """
    Select baseline or ML according to validation performance.

    ML is selected only when it improves the baseline by at
    least ML_MIN_IMPROVEMENT_PCT.
    """

    baseline_score = float(
        baseline_validation[
            "score"
        ]
    )

    ml_score = float(
        ml_validation[
            "score"
        ]
    )

    if baseline_score <= 0:
        improvement_pct = 0.0

    else:
        improvement_pct = (
            (
                baseline_score
                - ml_score
            )
            / baseline_score
        
        * 100.0
    )

    logger.info(
        "Baseline score: %.6f",
        baseline_score,
    )

    logger.info(
        "Best ML score: %.6f",
        ml_score,
    )

    logger.info(
        "ML improvement vs baseline: %.2f%%",
        improvement_pct,
    )

    if (
        improvement_pct
        >= ML_MIN_IMPROVEMENT_PCT
    ):

        method = (
            "HistGradientBoosting"
        )

        reason = (
            "ML_OUTPERFORMED_BASELINE"
        )

        logger.info(
            "ML sufficiently outperformed baseline."
        )

    else:

        method = (
            "RobustBaseline"
        )

        reason = (
            "ML_DID_NOT_OUTPERFORM_BASELINE"
        )

        logger.info(
            "ML did not sufficiently outperform baseline."
        )

    logger.info(
        "Selected forecast method: %s",
        method,
    )

    return {
        "method": method,
        "reason": reason,
        "improvement_pct": (
            float(
                improvement_pct
            )
        ),
    }


# ============================================================
# FORECAST QUALITY
# ============================================================

def classify_forecast_quality(
    metrics: dict[str, float],
) -> tuple[str, str]:
    """
    Convert validation quality into controller-readable labels.

    These labels are intentionally conservative.
    """

    smape = abs(
        metrics["smape_pct"]
    )

    if smape <= HIGH_CONFIDENCE_SMAPE:

        return (
            "HIGH_CONFIDENCE",
            "HIGH",
        )

    if smape <= MEDIUM_CONFIDENCE_SMAPE:

        return (
            "MEDIUM_CONFIDENCE",
            "MEDIUM",
        )

    return (
        "LOW_CONFIDENCE",
        "VERY_LOW",
    )


# ============================================================
# FUTURE ML PREDICTION
# ============================================================

def train_final_ml_model(
    history: pd.DataFrame,
) -> HistGradientBoostingRegressor:
    """
    Train final ML model on the complete valid history.
    """

    X, y = (
        prepare_ml_training_data(
            history
        )
    )

    logger.info(
        "Training final Cash Flow model on %s observations.",
        len(X),
    )

    model = create_ml_model()

    model.fit(
        X,
        y,
    )

    return model


def recursive_ml_ocf_prediction(
    history: pd.DataFrame,
    future_drivers: pd.DataFrame,
    model: HistGradientBoostingRegressor,
) -> pd.DataFrame:
    """
    Predict future OCF recursively with future Revenue and
    Operating Cost drivers.

    Unknown Net Profit / NWC values are carried forward using
    the latest available historical context.
    """

    working = history.copy()

    predictions = []

    latest_net_profit = float(
        history[
            "net_profit"
        ]
        .dropna()
        .iloc[-1]
    )

    latest_nwc = float(
        history[
            "net_working_capital"
        ]
        .dropna()
        .iloc[-1]
    )

    latest_cash = float(
        history[
            "closing_cash"
        ]
        .dropna()
        .iloc[-1]
    )

    for _, driver in future_drivers.iterrows():

        period = driver[
            "period"
        ]

        revenue = float(
            driver[
                "predicted_revenue"
            ]
        )

        operating_costs = float(
            driver[
                "predicted_operating_costs"
            ]
        )

        row = {
            "period": period,
            "revenue": revenue,
            "operating_costs": operating_costs,
            "net_profit": latest_net_profit,
            "net_working_capital": latest_nwc,
            "operating_cash_flow": np.nan,
            "closing_cash": latest_cash,
        }

        working = pd.concat(
            [
                working,
                pd.DataFrame(
                    [row]
                ),
            ],
            ignore_index=True,
        )

        engineered = (
            create_ocf_features(
                working
            )
        )

        current = (
            engineered
            .iloc[
                [-1]
            ][FEATURE_COLUMNS]
            .copy()
        )

        # Any context features that cannot be known in advance
        # are carried forward from the latest valid values.
        current = (
            current
            .ffill(
                axis=0
            )
            .bfill(
                axis=0
            )
            .fillna(0)
        )

        prediction = float(
            model.predict(
                current
            )[0]
        )

        predictions.append(
            {
                "period": period,
                "predicted_operating_cash_flow":
                    prediction,
            }
        )

        # Update recursive state.
        working.loc[
            working["period"]
            == period,
            "operating_cash_flow",
        ] = prediction

        previous_cash = float(
            working.loc[
                working["period"]
                < period,
                "closing_cash",
            ]
            .dropna()
            .iloc[-1]
        )

        predicted_cash = (
            previous_cash
            + prediction
        )

        working.loc[
            working["period"]
            == period,
            "closing_cash",
        ] = predicted_cash

        latest_cash = (
            predicted_cash
        )

    return pd.DataFrame(
        predictions
    )


# ============================================================
# BASELINE FUTURE FORECAST
# ============================================================

def forecast_future_baseline(
    history: pd.DataFrame,
    future_periods: pd.Series,
) -> pd.DataFrame:
    """
    Generate final six-month robust baseline forecast.
    """

    predictions = (
        build_robust_baseline_predictions(
            train_history=history,
            prediction_periods=future_periods,
        )
    )

    return pd.DataFrame(
        {
            "period": future_periods,
            "predicted_operating_cash_flow":
                predictions,
        }
    )


# ============================================================
# CASH BRIDGE
# ============================================================

def build_cash_bridge(
    history: pd.DataFrame,
    ocf_forecast: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build recursive Closing Cash forecast.

    Closing Cash_t =
        Closing Cash_(t-1)
        + Operating Cash Flow_t

    Investing and financing flows are intentionally excluded
    because they are not independently forecast in this layer.
    """

    actual_cutoff = (
        history["period"]
        .max()
    )

    last_cash = float(
        history.loc[
            history["period"]
            == actual_cutoff,
            "closing_cash",
        ].iloc[0]
    )

    outputs = []

    running_cash = last_cash

    for _, row in ocf_forecast.iterrows():

        operating_cf = float(
            row[
                "predicted_operating_cash_flow"
            ]
        )

        running_cash = (
            running_cash
            + operating_cf
        )

        outputs.append(
            {
                "period": row[
                    "period"
                ],
                "predicted_operating_cash_flow":
                    operating_cf,
                "predicted_closing_cash":
                    running_cash,
            }
        )

    return pd.DataFrame(
        outputs
    )


# ============================================================
# FORECAST INTERVALS
# ============================================================

def build_forecast_intervals(
    forecast: pd.DataFrame,
    metrics: dict[str, float],
) -> pd.DataFrame:
    """
    Build uncertainty intervals from validation RMSE and
    residual volatility.

    Uses a conservative 95% interval.

    Important:
        These intervals are scenario ranges, not statistical
        guarantees.
    """

    rmse = float(
        metrics["rmse"]
    )

    residual_std = float(
        metrics["residual_std"]
    )

    interval_error = max(
        rmse,
        residual_std,
    )

    multiplier = 1.96

    width = (
        multiplier
        * interval_error
    )

    result = forecast.copy()

    result["ocf_lower_bound"] = (
        result[
            "predicted_operating_cash_flow"
        ]
        - width
    )

    result["ocf_upper_bound"] = (
        result[
            "predicted_operating_cash_flow"
        ]
        + width
    )

    result["cash_lower_bound"] = (
        result[
            "predicted_closing_cash"
        ]
        - width
    )

    result["cash_upper_bound"] = (
        result[
            "predicted_closing_cash"
        ]
        + width
    )

    result["forecast_interval_width"] = (
        width
        * 2.0
    )

    return result


# ============================================================
# VALIDATION
# ============================================================

def validate_forecast_output(
    output: pd.DataFrame,
    history: pd.DataFrame,
) -> None:
    """
    Validate final Cash Flow prediction output.
    """

    if output.empty:
        raise RuntimeError(
            "Cash Flow prediction output is empty."
        )

    if len(output) != HORIZON:
        raise RuntimeError(
            "Invalid Cash Flow forecast horizon: "
            f"expected {HORIZON}, "
            f"found {len(output)}."
        )

    expected_periods = pd.date_range(
        start=(
            history["period"].max()
            + pd.offsets.MonthBegin(1)
        ),
        periods=HORIZON,
        freq="MS",
    )

    actual_periods = (
        output[
            "period"
        ]
        .sort_values()
        .reset_index(
            drop=True
        )
    )

    if not actual_periods.equals(
        pd.Series(
            expected_periods
        )
    ):
        raise RuntimeError(
            "Cash Flow forecast periods are not aligned "
            "with the expected six-month horizon."
        )

    # --------------------------------------------------------
    # Sign validation
    # --------------------------------------------------------

    revenue_validation = (
        history["revenue"]
        >= 0
    )

    if not revenue_validation.all():
        raise RuntimeError(
            "Historical Revenue contains negative values "
            "after management sign normalization."
        )

    # --------------------------------------------------------
    # Cash bridge validation
    # --------------------------------------------------------

    actual_cash = float(
        history[
            "closing_cash"
        ]
        .iloc[-1]
    )

    running_cash = (
        actual_cash
    )

    for _, row in (
        output
        .sort_values("period")
        .iterrows()
    ):

        running_cash += float(
            row[
                "predicted_operating_cash_flow"
            ]
        )

        expected_cash = float(
            row[
                "predicted_closing_cash"
            ]
        )

        if not np.isclose(
            running_cash,
            expected_cash,
            atol=0.01,
        ):
            raise RuntimeError(
                "Cash bridge validation failed for "
                f"{row['period']}."
            )

    # --------------------------------------------------------
    # Forecast interval validation
    # --------------------------------------------------------

    interval_checks = [
        (
            output[
                "ocf_lower_bound"
            ]
            <=
            output[
                "predicted_operating_cash_flow"
            ]
        ),
        (
            output[
                "predicted_operating_cash_flow"
            ]
            <=
            output[
                "ocf_upper_bound"
            ]
        ),
        (
            output[
                "cash_lower_bound"
            ]
            <=
            output[
                "predicted_closing_cash"
            ]
        ),
        (
            output[
                "predicted_closing_cash"
            ]
            <=
            output[
                "cash_upper_bound"
            ]
        ),
    ]

    for check in interval_checks:

        if not check.all():
            raise RuntimeError(
                "Forecast interval validation failed."
            )

    required_columns = {
        "period",
        "predicted_operating_cash_flow",
        "predicted_closing_cash",
        "ocf_lower_bound",
        "ocf_upper_bound",
        "cash_lower_bound",
        "cash_upper_bound",
        "forecast_method",
        "forecast_selection_reason",
        "forecast_quality_status",
        "forecast_confidence",
    }

    missing_columns = (
        required_columns
        - set(output.columns)
    )

    if missing_columns:
        raise RuntimeError(
            "Cash Flow output missing required columns: "
            + ", ".join(
                sorted(missing_columns)
            )
        )

    logger.info(
        "Cash Flow forecast output validation passed."
    )


# ============================================================
# BUILD OUTPUT
# ============================================================

def build_output(
    history: pd.DataFrame,
    ocf_forecast: pd.DataFrame,
    selected_method: str,
    selection_reason: str,
    ml_improvement_pct: float,
    selected_metrics: dict[str, float],
    prediction_type: str,
) -> pd.DataFrame:
    """
    Build final Power BI-ready Cash Flow prediction dataset.
    """

    bridge = build_cash_bridge(
        history=history,
        ocf_forecast=ocf_forecast,
    )

    bridge = build_forecast_intervals(
        forecast=bridge,
        metrics=selected_metrics,
    )

    forecast_quality, forecast_confidence = (
        classify_forecast_quality(
            selected_metrics
        )
    )

    result = bridge.copy()

    result["model"] = (
        selected_method
    )

    result["forecast_method"] = (
        selected_method
    )

    result["forecast_selection_reason"] = (
        selection_reason
    )

    result["ml_improvement_vs_baseline_pct"] = (
        float(
            ml_improvement_pct
        )
    )

    result["forecast_quality_status"] = (
        forecast_quality
    )

    result["forecast_confidence"] = (
        forecast_confidence
    )

    result["validation_mae"] = (
        selected_metrics[
            "mae"
        ]
    )

    result["validation_rmse"] = (
        selected_metrics[
            "rmse"
        ]
    )

    result["validation_smape_pct"] = (
        selected_metrics[
            "smape_pct"
        ]
    )

    result["validation_stabilized_mape_pct"] = (
        selected_metrics[
            "stabilized_mape_pct"
        ]
    )

    result["validation_residual_std"] = (
        selected_metrics[
            "residual_std"
        ]
    )

    result["prediction_type"] = (
        prediction_type
    )

    result["year_month"] = (
        result["period"]
        .dt.strftime("%Y-%m")
    )

    result["forecast_year"] = (
        result["period"]
        .dt.year
    )

    result["forecast_month"] = (
        result["period"]
        .dt.month
    )

    return result[
        [
            "period",
            "year_month",
            "forecast_year",
            "forecast_month",

            "predicted_operating_cash_flow",
            "ocf_lower_bound",
            "ocf_upper_bound",

            "predicted_closing_cash",
            "cash_lower_bound",
            "cash_upper_bound",

            "model",
            "forecast_method",
            "forecast_selection_reason",
            "ml_improvement_vs_baseline_pct",

            "forecast_quality_status",
            "forecast_confidence",

            "validation_mae",
            "validation_rmse",
            "validation_smape_pct",
            "validation_stabilized_mape_pct",
            "validation_residual_std",

            "forecast_interval_width",

            "prediction_type",
        ]
    ]


# ============================================================
# LOGGING
# ============================================================

def log_latest_context(
    history: pd.DataFrame,
) -> None:
    """
    Log latest actual financial context.
    """

    latest = (
        history
        .sort_values("period")
        .iloc[-1]
    )

    logger.info(
        "Latest actual financial context:"
    )

    logger.info(
        "Revenue: %.2f",
        float(
            latest[
                "revenue"
            ]
        ),
    )

    logger.info(
        "Operating Costs: %.2f",
        float(
            latest[
                "operating_costs"
            ]
        ),
    )

    logger.info(
        "Operating Cash Flow: %.2f",
        float(
            latest[
                "operating_cash_flow"
            ]
        ),
    )

    logger.info(
        "Closing Cash: %.2f",
        float(
            latest[
                "closing_cash"
            ]
        ),
    )


def log_forecast_results(
    output: pd.DataFrame,
) -> None:
    """
    Log monthly Cash Flow forecast.
    """

    forecast = (
        output
        .sort_values("period")
        .reset_index(drop=True)
    )

    for index, row in (
        forecast
        .iterrows()
    ):

        logger.info(
            "Cash Flow forecast %s/%s | %s | "
            "OCF %.2f | Cash %.2f",
            index + 1,
            len(forecast),
            row[
                "period"
            ].strftime("%Y-%m"),
            row[
                "predicted_operating_cash_flow"
            ],
            row[
                "predicted_closing_cash"
            ],
        )


def log_forecast_quality(
    output: pd.DataFrame,
) -> None:
    """
    Log selected forecast method and quality.
    """

    first_row = (
        output
        .sort_values("period")
        .iloc[0]
    )

    logger.info(
        "Selected Cash Flow method: %s",
        first_row[
            "forecast_method"
        ],
    )

    logger.info(
        "Prediction type: %s",
        first_row[
            "prediction_type"
        ],
    )

    logger.info(
        "Forecast selection reason: %s",
        first_row[
            "forecast_selection_reason"
        ],
    )

    logger.info(
        "Forecast quality: %s",
        first_row[
            "forecast_quality_status"
        ],
    )

    logger.info(
        "Forecast confidence: %s",
        first_row[
            "forecast_confidence"
        ],
    )

    logger.info(
        "ML improvement vs baseline: %.2f%%",
        first_row[
            "ml_improvement_vs_baseline_pct"
        ],
    )


# ============================================================
# SAVE
# ============================================================

def save_output(
    df: pd.DataFrame,
) -> None:
    """
    Save Cash Flow prediction output.
    """

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    logger.info(
        "Cash Flow prediction saved to %s",
        OUTPUT_FILE,
    )


# ============================================================
# MAIN
# ============================================================

def main() -> int:
    """
    Run EFAP Cash Flow Prediction pipeline.
    """

    try:

        logger.info(
            "Starting EFAP Cash Flow Prediction."
        )

        # ----------------------------------------------------
        # FILES
        # ----------------------------------------------------

        validate_files()

        # ----------------------------------------------------
        # HISTORICAL DATA
        # ----------------------------------------------------

        history = (
            load_historical_data()
        )

        # ----------------------------------------------------
        # FUTURE DRIVERS
        # ----------------------------------------------------

        revenue_prediction = (
            load_revenue_prediction()
        )

        expense_forecast = (
            load_expense_forecast()
        )

        future_drivers = (
            build_future_driver_dataset(
                history=history,
                revenue_prediction=(
                    revenue_prediction
                ),
                expense_forecast=(
                    expense_forecast
                ),
            )
        )

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        baseline_validation = (
            validate_baseline_model(
                history
            )
        )

        ml_validation = (
            validate_ml_model(
                history
            )
        )

        # ----------------------------------------------------
        # MODEL SELECTION
        # ----------------------------------------------------

        selection = (
            select_forecast_method(
                baseline_validation=(
                    baseline_validation
                ),
                ml_validation=(
                    ml_validation
                ),
            )
        )

        selected_method = (
            selection[
                "method"
            ]
        )

        selection_reason = (
            selection[
                "reason"
            ]
        )

        ml_improvement_pct = (
            selection[
                "improvement_pct"
            ]
        )

        # ----------------------------------------------------
        # TRAIN FINAL ML MODEL
        # ----------------------------------------------------

        final_ml_model = (
            train_final_ml_model(
                history
            )
        )

        # ----------------------------------------------------
        # FUTURE OCF FORECAST
        # ----------------------------------------------------

        if (
            selected_method
            == "HistGradientBoosting"
        ):

            ml_forecast = (
                recursive_ml_ocf_prediction(
                    history=history,
                    future_drivers=(
                        future_drivers
                    ),
                    model=(
                        final_ml_model
                    ),
                )
            )

            ocf_forecast = (
                ml_forecast
            )

            selected_metrics = (
                ml_validation[
                    "metrics"
                ]
            )

            prediction_type = (
                "ML_PREDICTION"
            )

        else:

            baseline_forecast = (
                forecast_future_baseline(
                    history=history,
                    future_periods=(
                        future_drivers[
                            "period"
                        ]
                    ),
                )
            )

            ocf_forecast = (
                baseline_forecast
            )

            selected_metrics = (
                baseline_validation[
                    "metrics"
                ]
            )

            prediction_type = (
                "BASELINE_FORECAST"
            )

        # ----------------------------------------------------
        # LOG CONTEXT
        # ----------------------------------------------------

        log_latest_context(
            history
        )

        # ----------------------------------------------------
        # BUILD OUTPUT
        # ----------------------------------------------------

        output = build_output(
            history=history,
            ocf_forecast=(
                ocf_forecast
            ),
            selected_method=(
                selected_method
            ),
            selection_reason=(
                selection_reason
            ),
            ml_improvement_pct=(
                ml_improvement_pct
            ),
            selected_metrics=(
                selected_metrics
            ),
            prediction_type=(
                prediction_type
            ),
        )

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        validate_forecast_output(
            output=output,
            history=history,
        )

        # ----------------------------------------------------
        # LOGGING
        # ----------------------------------------------------

        log_forecast_quality(
            output
        )

        log_forecast_results(
            output
        )

        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        save_output(
            output
        )

        logger.info(
            "Generated %s Cash Flow prediction months.",
            len(output),
        )

        logger.info(
            "Forecast period: %s -> %s",
            output[
                "period"
            ].min().strftime(
                "%Y-%m"
            ),
            output[
                "period"
            ].max().strftime(
                "%Y-%m"
            ),
        )

        logger.info(
            "Cash Flow Prediction completed successfully."
        )

        return 0

    except Exception as exc:

        logger.exception(
            "Cash Flow Prediction failed: %s",
            exc,
        )

        return 1


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    sys.exit(
        main()
    )