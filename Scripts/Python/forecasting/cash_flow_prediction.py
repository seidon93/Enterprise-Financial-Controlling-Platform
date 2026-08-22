"""
EFAP - Cash Flow Prediction

Object:
    Scripts/Python/forecasting/cash_flow_prediction.py

Purpose:
    Predict future Operating Cash Flow (OCF) and Closing Cash.

Design:
    - Direct driver-based forecasting.
    - No recursive OCF self-feeding.
    - Revenue and Operating Cost forecasts are explicit future drivers.
    - Robust baseline is evaluated against ML.
    - Better model is selected using time-ordered validation.
    - Closing Cash is calculated transparently from OCF.

Sources:
    data/processed/controller_kpi_timeseries.csv
    data/predictions/revenue_prediction.csv
    data/forecasts/expense_forecast.csv

Output:
    data/predictions/cash_flow_prediction.csv

Management sign convention:
    Revenue         >= 0
    Operating Costs <= 0
    Operating CF    signed
    Closing Cash    signed

Important:
    - PostgreSQL remains the financial source of truth.
    - This module performs predictive analytics only.
    - No database credentials are stored in source code.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Final

import numpy as np
import pandas as pd

from sklearn.ensemble import (
    HistGradientBoostingRegressor,
    RandomForestRegressor,
)
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

# Blend threshold:
# ML must beat baseline sufficiently to become preferred.
ML_IMPROVEMENT_THRESHOLD: Final[float] = 0.05

# Robust rolling windows.
SHORT_WINDOW: Final[int] = 3
MEDIUM_WINDOW: Final[int] = 6
LONG_WINDOW: Final[int] = 12

# Validation scoring weights.
MAE_WEIGHT: Final[float] = 0.50
RMSE_WEIGHT: Final[float] = 0.30
SMAPE_WEIGHT: Final[float] = 0.20

# Prediction interval.
INTERVAL_QUANTILE: Final[float] = 0.90


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
        "time series": TIME_SERIES_FILE,
        "revenue prediction": REVENUE_PREDICTION_FILE,
        "expense forecast": EXPENSE_FORECAST_FILE,
    }

    missing = [
        f"{name}: {path}"
        for name, path in required_files.items()
        if not path.exists()
    ]

    if missing:
        raise FileNotFoundError(
            "Missing required files:\n"
            + "\n".join(missing)
        )


# ============================================================
# GENERIC HELPERS
# ============================================================

def normalize_monthly_period(
    series: pd.Series,
) -> pd.Series:
    """Convert dates to monthly start timestamps."""

    return (
        pd.to_datetime(
            series,
            errors="coerce",
        )
        .dt.to_period("M")
        .dt.to_timestamp()
    )


def safe_divide(
    numerator: pd.Series,
    denominator: pd.Series,
) -> pd.Series:
    """Safe element-wise division."""

    denominator = denominator.replace(
        0,
        np.nan,
    )

    return numerator.div(
        denominator
    )


def smape(
    actual: np.ndarray,
    predicted: np.ndarray,
) -> float:
    """
    Symmetric Mean Absolute Percentage Error.

    Stable around zero compared with ordinary MAPE.
    """

    actual = np.asarray(
        actual,
        dtype=float,
    )

    predicted = np.asarray(
        predicted,
        dtype=float,
    )

    denominator = (
        np.abs(actual)
        + np.abs(predicted)
    )

    valid = denominator > 0

    if not np.any(valid):
        return 0.0

    value = (
        2.0
        * np.abs(
            actual[valid]
            - predicted[valid]
        )
        / denominator[valid]
    )

    return float(
        np.mean(value)
        * 100.0
    )


def stabilized_mape(
    actual: np.ndarray,
    predicted: np.ndarray,
) -> float:
    """
    Stabilized MAPE.

    Uses a scale floor based on the median absolute
    actual value, preventing tiny denominators from
    exploding the metric.
    """

    actual = np.asarray(
        actual,
        dtype=float,
    )

    predicted = np.asarray(
        predicted,
        dtype=float,
    )

    scale = np.median(
        np.abs(actual)
    )

    floor = max(
        scale * 0.10,
        1.0,
    )

    denominator = np.maximum(
        np.abs(actual),
        floor,
    )

    return float(
        np.mean(
            np.abs(
                actual
                - predicted
            )
            / denominator
        )
        * 100.0
    )


# ============================================================
# HISTORICAL DATA
# ============================================================

def load_historical_data() -> pd.DataFrame:
    """
    Load historical controller KPI time series.

    The OCF model uses historical financial drivers
    and historical Operating Cash Flow.
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

    df["period"] = normalize_monthly_period(
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
            subset=["period"]
        )
        .sort_values("period")
        .drop_duplicates(
            "period"
        )
        .reset_index(
            drop=True
        )
    )

    if df.empty:
        raise ValueError(
            "Historical Cash Flow dataset is empty."
        )

    # --------------------------------------------------------
    # MANAGEMENT SIGN NORMALIZATION
    # --------------------------------------------------------

    df["revenue"] = (
        df["revenue"]
        .abs()
    )

    df["operating_costs"] = (
        -df["operating_costs"].abs()
    )

    # --------------------------------------------------------
    # MONTHLY CONTINUITY
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

    missing_target_rows = df[
        [
            "operating_cash_flow",
            "closing_cash",
        ]
    ].isna().any(
        axis=1
    )

    if missing_target_rows.any():
        periods = (
            df.loc[
                missing_target_rows,
                "period",
            ]
            .dt.strftime("%Y-%m")
            .tolist()
        )

        raise ValueError(
            "Historical OCF / Closing Cash contains "
            f"missing monthly observations: {periods}"
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
# REVENUE PREDICTION
# ============================================================

def load_revenue_prediction() -> pd.DataFrame:
    """Load future Revenue prediction."""

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

    df["period"] = normalize_monthly_period(
        df["period"]
    )

    df["predicted_revenue"] = pd.to_numeric(
        df["predicted_revenue"],
        errors="coerce",
    )

    df["predicted_revenue"] = (
        df["predicted_revenue"]
        .abs()
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
            "period"
        )
        .reset_index(
            drop=True
        )
    )

    if df.empty:
        raise ValueError(
            "Revenue prediction contains no valid rows."
        )

    logger.info(
        "Revenue prediction periods: %s",
        len(df),
    )

    return df


# ============================================================
# EXPENSE FORECAST
# ============================================================

def load_expense_forecast() -> pd.DataFrame:
    """
    Load account-level expense forecast and aggregate
    it to monthly operating cost magnitude.

    Source convention:
        forecast_expense >= 0
    Management convention:
        operating_costs <= 0
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

    df["period"] = normalize_monthly_period(
        df["forecast_period"]
    )

    df["forecast_expense"] = pd.to_numeric(
        df["forecast_expense"],
        errors="coerce",
    )

    df["forecast_expense"] = (
        df["forecast_expense"]
        .abs()
    )

    df = df.dropna(
        subset=[
            "period",
            "forecast_expense",
        ]
    )

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
        raise ValueError(
            "Expense forecast contains no valid rows."
        )

    logger.info(
        "Expense forecast periods: %s",
        len(monthly),
    )

    return monthly


# ============================================================
# HISTORICAL DRIVER FEATURES
# ============================================================

def create_features(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create direct-driver OCF prediction features.

    Important:
        Features intentionally avoid future OCF values.
        This prevents recursive error propagation.
    """

    result = df.copy()

    # --------------------------------------------------------
    # Calendar
    # --------------------------------------------------------

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
    # Core financial drivers
    # --------------------------------------------------------

    result["revenue_abs"] = (
        result["revenue"].abs()
    )

    result["operating_costs_abs"] = (
        result["operating_costs"].abs()
    )

    result["ebitda_proxy"] = (
        result["revenue_abs"]
        - result["operating_costs_abs"]
    )

    result["cost_to_revenue"] = safe_divide(
        result["operating_costs_abs"],
        result["revenue_abs"],
    )

    result["ocf_to_revenue"] = safe_divide(
        result["operating_cash_flow"],
        result["revenue_abs"],
    )

    # --------------------------------------------------------
    # Revenue history
    # --------------------------------------------------------

    result["revenue_lag_1"] = (
        result["revenue_abs"].shift(1)
    )

    result["revenue_lag_3"] = (
        result["revenue_abs"].shift(3)
    )

    result["revenue_lag_12"] = (
        result["revenue_abs"].shift(12)
    )

    result["revenue_change_1"] = (
        result["revenue_abs"]
        .pct_change()
        .replace(
            [np.inf, -np.inf],
            np.nan,
        )
    )

    # --------------------------------------------------------
    # Operating costs history
    # --------------------------------------------------------

    result["costs_lag_1"] = (
        result["operating_costs_abs"].shift(1)
    )

    result["costs_lag_3"] = (
        result["operating_costs_abs"].shift(3)
    )

    result["costs_lag_12"] = (
        result["operating_costs_abs"].shift(12)
    )

    # --------------------------------------------------------
    # OCF history
    # --------------------------------------------------------

    result["ocf_lag_1"] = (
        result["operating_cash_flow"]
        .shift(1)
    )

    result["ocf_lag_3"] = (
        result["operating_cash_flow"]
        .shift(3)
    )

    result["ocf_lag_6"] = (
        result["operating_cash_flow"]
        .shift(6)
    )

    result["ocf_lag_12"] = (
        result["operating_cash_flow"]
        .shift(12)
    )

    # --------------------------------------------------------
    # Robust rolling OCF
    # --------------------------------------------------------

    shifted_ocf = (
        result["operating_cash_flow"]
        .shift(1)
    )

    result["ocf_rolling_median_3"] = (
        shifted_ocf
        .rolling(
            SHORT_WINDOW,
            min_periods=SHORT_WINDOW,
        )
        .median()
    )

    result["ocf_rolling_median_6"] = (
        shifted_ocf
        .rolling(
            MEDIUM_WINDOW,
            min_periods=MEDIUM_WINDOW,
        )
        .median()
    )

    result["ocf_rolling_median_12"] = (
        shifted_ocf
        .rolling(
            LONG_WINDOW,
            min_periods=LONG_WINDOW,
        )
        .median()
    )

    result["ocf_rolling_mean_6"] = (
        shifted_ocf
        .rolling(
            MEDIUM_WINDOW,
            min_periods=MEDIUM_WINDOW,
        )
        .mean()
    )

    # --------------------------------------------------------
    # OCF / Revenue conversion history
    # --------------------------------------------------------

    historical_conversion = (
        result["ocf_to_revenue"]
        .replace(
            [np.inf, -np.inf],
            np.nan,
        )
        .shift(1)
    )

    result["conversion_median_3"] = (
        historical_conversion
        .rolling(
            SHORT_WINDOW,
            min_periods=SHORT_WINDOW,
        )
        .median()
    )

    result["conversion_median_6"] = (
        historical_conversion
        .rolling(
            MEDIUM_WINDOW,
            min_periods=MEDIUM_WINDOW,
        )
        .median()
    )

    result["conversion_median_12"] = (
        historical_conversion
        .rolling(
            LONG_WINDOW,
            min_periods=LONG_WINDOW,
        )
        .median()
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

    result["nwc_lag_12"] = (
        result["net_working_capital"]
        .shift(12)
    )

    result["nwc_change_lag_1"] = (
        result["net_working_capital"]
        .diff()
        .shift(1)
    )

    # --------------------------------------------------------
    # Net profit
    # --------------------------------------------------------

    result["net_profit_lag_1"] = (
        result["net_profit"]
        .shift(1)
    )

    result["net_profit_lag_3"] = (
        result["net_profit"]
        .shift(3)
    )

    result["net_profit_lag_12"] = (
        result["net_profit"]
        .shift(12)
    )

    return result


FEATURE_COLUMNS: Final[list[str]] = [
    "month",
    "quarter",
    "month_sin",
    "month_cos",
    "time_index",

    "revenue_abs",
    "operating_costs_abs",
    "ebitda_proxy",
    "cost_to_revenue",

    "revenue_lag_1",
    "revenue_lag_3",
    "revenue_lag_12",
    "revenue_change_1",

    "costs_lag_1",
    "costs_lag_3",
    "costs_lag_12",

    "ocf_lag_1",
    "ocf_lag_3",
    "ocf_lag_6",
    "ocf_lag_12",

    "ocf_rolling_median_3",
    "ocf_rolling_median_6",
    "ocf_rolling_median_12",
    "ocf_rolling_mean_6",

    "conversion_median_3",
    "conversion_median_6",
    "conversion_median_12",

    "nwc_lag_1",
    "nwc_lag_3",
    "nwc_lag_12",
    "nwc_change_lag_1",

    "net_profit_lag_1",
    "net_profit_lag_3",
    "net_profit_lag_12",
]


# ============================================================
# MODELS
# ============================================================

def create_hist_gradient_model() -> (
    HistGradientBoostingRegressor
):
    """Create robust gradient boosting model."""

    return HistGradientBoostingRegressor(
        learning_rate=0.035,
        max_iter=300,
        max_leaf_nodes=10,
        min_samples_leaf=5,
        l2_regularization=5.0,
        loss="absolute_error",
        random_state=RANDOM_STATE,
    )


def create_random_forest_model() -> (
    RandomForestRegressor
):
    """Create robust Random Forest model."""

    return RandomForestRegressor(
        n_estimators=500,
        max_depth=6,
        min_samples_leaf=3,
        max_features=0.70,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )


# ============================================================
# TRAINING DATA
# ============================================================

def prepare_training_data(
    history: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    """
    Prepare direct-driver supervised learning dataset.
    """

    features = create_features(
        history
    )

    training = features.dropna(
        subset=FEATURE_COLUMNS
        + [
            "operating_cash_flow",
        ]
    ).copy()

    if training.empty:
        raise ValueError(
            "No valid OCF training observations "
            "after feature engineering."
        )

    X = training[
        FEATURE_COLUMNS
    ]

    y = training[
        "operating_cash_flow"
    ]

    return (
        X,
        y,
        training,
    )


# ============================================================
# ROBUST BASELINE
# ============================================================

def baseline_prediction(
    history: pd.DataFrame,
    periods: pd.Series,
    driver_revenue: pd.Series,
) -> np.ndarray:
    """
    Generate a robust baseline forecast.

    Components:
        1. Seasonal naive OCF (12 months ago)
        2. Recent 6-month OCF median
        3. Robust OCF/Revenue conversion

    The three components are blended to avoid dependence
    on any one unstable historical observation.
    """

    history = (
        history
        .sort_values("period")
        .reset_index(drop=True)
    )

    ocf_series = history.set_index(
        "period"
    )["operating_cash_flow"]

    revenue_series = history.set_index(
        "period"
    )["revenue"].abs()

    historical_ratio = (
        safe_divide(
            history["operating_cash_flow"],
            history["revenue"].abs(),
        )
        .replace(
            [np.inf, -np.inf],
            np.nan,
        )
        .dropna()
    )

    if historical_ratio.empty:
        robust_ratio = 0.0
    else:
        lower = historical_ratio.quantile(
            0.10
        )
        upper = historical_ratio.quantile(
            0.90
        )

        clipped_ratio = historical_ratio.clip(
            lower=lower,
            upper=upper,
        )

        robust_ratio = float(
            clipped_ratio.median()
        )

    recent_ocf = (
        history["operating_cash_flow"]
        .tail(MEDIUM_WINDOW)
        .median()
    )

    recent_ocf = float(
        recent_ocf
    )

    predictions = []

    for period, revenue in zip(
        periods,
        driver_revenue,
    ):

        # ----------------------------------------------------
        # Seasonal naive
        # ----------------------------------------------------

        seasonal_period = (
            period
            - pd.DateOffset(
                months=12
            )
        )

        seasonal_value = ocf_series.get(
            seasonal_period,
            np.nan,
        )

        if pd.isna(
            seasonal_value
        ):
            seasonal_value = recent_ocf

        seasonal_value = float(
            seasonal_value
        )

        # ----------------------------------------------------
        # Conversion-based baseline
        # ----------------------------------------------------

        conversion_value = (
            robust_ratio
            * float(
                abs(revenue)
            )
        )

        # ----------------------------------------------------
        # Blend
        # ----------------------------------------------------

        prediction = (
            0.40
            * seasonal_value
            + 0.35
            * recent_ocf
            + 0.25
            * conversion_value
        )

        predictions.append(
            float(prediction)
        )

    return np.asarray(
        predictions,
        dtype=float,
    )


# ============================================================
# VALIDATION
# ============================================================

def calculate_validation_metrics(
    actual: np.ndarray,
    predicted: np.ndarray,
) -> dict[str, float]:
    """Calculate robust validation metrics."""

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

    stabilized = stabilized_mape(
        actual,
        predicted,
    )

    symmetric = smape(
        actual,
        predicted,
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
    ) if len(
        residuals
    ) > 1 else 0.0

    return {
        "mae": float(mae),
        "rmse": float(rmse),
        "stabilized_mape_pct": float(
            stabilized
        ),
        "smape_pct": float(
            symmetric
        ),
        "residual_std": residual_std,
    }


def composite_validation_score(
    metrics: dict[str, float],
) -> float:
    """
    Create comparable validation score.

    Lower is better.
    """

    mae = metrics["mae"]
    rmse = metrics["rmse"]
    smape_value = metrics["smape_pct"]

    scale = max(
        abs(
            metrics.get(
                "scale",
                1.0,
            )
        ),
        1.0,
    )

    normalized_mae = (
        mae / scale
    )

    normalized_rmse = (
        rmse / scale
    )

    normalized_smape = (
        smape_value / 100.0
    )

    return float(
        MAE_WEIGHT
        * normalized_mae
        + RMSE_WEIGHT
        * normalized_rmse
        + SMAPE_WEIGHT
        * normalized_smape
    )


def validate_models(
    history: pd.DataFrame,
) -> dict[str, object]:
    """
    Compare ML models against robust baseline
    using a time-ordered validation split.
    """

    X, y, training = (
        prepare_training_data(
            history
        )
    )

    if len(X) <= VALIDATION_MONTHS:
        raise ValueError(
            "Not enough observations for validation."
        )

    split = (
        len(X)
        - VALIDATION_MONTHS
    )

    X_train = X.iloc[
        :split
    ]

    X_test = X.iloc[
        split:
    ]

    y_train = y.iloc[
        :split
    ]

    y_test = y.iloc[
        split:
    ]

    validation_periods = training[
        "period"
    ].iloc[
        split:
    ].reset_index(
        drop=True
    )

    validation_revenue = training[
        "revenue_abs"
    ].iloc[
        split:
    ].reset_index(
        drop=True
    )

    # --------------------------------------------------------
    # Models
    # --------------------------------------------------------

    candidates = {
        "HistGradientBoosting":
            create_hist_gradient_model(),

        "RandomForest":
            create_random_forest_model(),
    }

    results: dict[str, dict[str, object]] = {}

    # --------------------------------------------------------
    # Baseline
    # --------------------------------------------------------

    history_before_validation = (
        history[
            history["period"]
            <
            validation_periods.iloc[0]
        ]
        .copy()
    )

    baseline_pred = baseline_prediction(
        history=history_before_validation,
        periods=validation_periods,
        driver_revenue=validation_revenue,
    )

    baseline_metrics = calculate_validation_metrics(
        y_test.to_numpy(),
        baseline_pred,
    )

    scale = max(
        float(
            np.median(
                np.abs(
                    y_test.to_numpy()
                )
            )
        ),
        1.0,
    )

    baseline_metrics[
        "scale"
    ] = scale

    baseline_score = (
        composite_validation_score(
            baseline_metrics
        )
    )

    results["Baseline"] = {
        "model": None,
        "prediction": baseline_pred,
        "metrics": baseline_metrics,
        "score": baseline_score,
    }

    logger.info(
        "Baseline validation:"
    )

    logger.info(
        "MAE: %.2f",
        baseline_metrics["mae"],
    )

    logger.info(
        "RMSE: %.2f",
        baseline_metrics["rmse"],
    )

    logger.info(
        "Stabilized MAPE: %.2f%%",
        baseline_metrics[
            "stabilized_mape_pct"
        ],
    )

    logger.info(
        "sMAPE: %.2f%%",
        baseline_metrics[
            "smape_pct"
        ],
    )

    # --------------------------------------------------------
    # ML candidates
    # --------------------------------------------------------

    for model_name, model in candidates.items():

        model.fit(
            X_train,
            y_train,
        )

        prediction = model.predict(
            X_test
        )

        metrics = calculate_validation_metrics(
            y_test.to_numpy(),
            prediction,
        )

        metrics[
            "scale"
        ] = scale

        score = (
            composite_validation_score(
                metrics
            )
        )

        results[model_name] = {
            "model": model,
            "prediction": prediction,
            "metrics": metrics,
            "score": score,
        }

        logger.info(
            "%s validation:",
            model_name,
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
            "Composite score: %.6f",
            score,
        )

    # --------------------------------------------------------
    # Select best ML
    # --------------------------------------------------------

    ml_names = [
        name
        for name in results
        if name != "Baseline"
    ]

    best_ml_name = min(
        ml_names,
        key=lambda name:
        results[name]["score"],
    )

    baseline_score = float(
        results["Baseline"]["score"]
    )

    best_ml_score = float(
        results[best_ml_name]["score"]
    )

    improvement = (
        (
            baseline_score
            - best_ml_score
        )
        / max(
            baseline_score,
            1e-12,
        )
    )

    logger.info(
        "Best ML model: %s",
        best_ml_name,
    )

    logger.info(
        "Baseline score: %.6f",
        baseline_score,
    )

    logger.info(
        "Best ML score: %.6f",
        best_ml_score,
    )

    logger.info(
        "ML improvement vs baseline: %.2f%%",
        improvement * 100.0,
    )

    if (
        improvement
        >= ML_IMPROVEMENT_THRESHOLD
    ):

        selected_type = "ML"

        selected_name = (
            best_ml_name
        )

        selected_result = (
            results[
                best_ml_name
            ]
        )

        logger.info(
            "Selected forecast method: %s",
            best_ml_name,
        )

    else:

        selected_type = "BASELINE"

        selected_name = (
            "RobustBaseline"
        )

        selected_result = (
            results[
                "Baseline"
            ]
        )

        logger.info(
            "ML did not sufficiently "
            "outperform baseline."
        )

        logger.info(
            "Selected forecast method: RobustBaseline"
        )

    return {
        "selected_type": selected_type,
        "selected_name": selected_name,
        "selected_model": selected_result[
            "model"
        ],
        "selected_metrics": selected_result[
            "metrics"
        ],
        "validation_results": results,
        "improvement_vs_baseline": improvement,
    }


# ============================================================
# FUTURE DRIVER DATA
# ============================================================

def build_future_drivers(
    history: pd.DataFrame,
    revenue_prediction: pd.DataFrame,
    expense_forecast: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build the future driver dataset.

    Future revenue and operating costs are known
    from independent forecast layers.
    """

    actual_cutoff = (
        history["period"].max()
    )

    future = (
        revenue_prediction[
            revenue_prediction["period"]
            > actual_cutoff
        ]
        .merge(
            expense_forecast,
            on="period",
            how="inner",
            validate="one_to_one",
        )
        .sort_values("period")
        .reset_index(drop=True)
    )

    if future.empty:
        raise ValueError(
            "No overlapping future Revenue "
            "and Expense forecast periods found."
        )

    future[
        "revenue"
    ] = (
        future[
            "predicted_revenue"
        ]
        .abs()
    )

    future[
        "operating_costs"
    ] = (
        -future[
            "predicted_expense"
        ].abs()
    )

    future[
        "net_profit"
    ] = np.nan

    future[
        "net_working_capital"
    ] = np.nan

    future[
        "operating_cash_flow"
    ] = np.nan

    future[
        "closing_cash"
    ] = np.nan

    return future[
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


# ============================================================
# BUILD FUTURE FEATURES
# ============================================================

def create_future_feature_rows(
    history: pd.DataFrame,
    future_drivers: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create future feature rows without recursive OCF.

    Historical OCF lags and robust statistics remain anchored
    in actual history.
    """

    history = (
        history
        .copy()
        .sort_values("period")
        .reset_index(drop=True)
    )

    feature_history = create_features(
        history
    )

    feature_history[
        "source_type"
    ] = "HISTORICAL"

    historical_ocf = (
        history[
            "operating_cash_flow"
        ]
        .copy()
    )

    historical_revenue = (
        history[
            "revenue"
        ]
        .abs()
        .copy()
    )

    historical_costs = (
        history[
            "operating_costs"
        ]
        .abs()
        .copy()
    )

    historical_nwc = (
        history[
            "net_working_capital"
        ]
        .copy()
    )

    historical_net_profit = (
        history[
            "net_profit"
        ]
        .copy()
    )

    rows = []

    for _, item in future_drivers.iterrows():

        period = item["period"]

        month = period.month
        quarter = period.quarter

        revenue = float(
            abs(
                item["revenue"]
            )
        )

        operating_costs_abs = float(
            abs(
                item["operating_costs"]
            )
        )

        # ----------------------------------------------------
        # Recent actual context
        # ----------------------------------------------------

        ocf_lag_1 = float(
            historical_ocf.iloc[-1]
        )

        ocf_lag_3 = float(
            historical_ocf.tail(3).iloc[0]
            if len(historical_ocf) >= 3
            else historical_ocf.iloc[-1]
        )

        ocf_lag_6 = float(
            historical_ocf.tail(6).iloc[0]
            if len(historical_ocf) >= 6
            else historical_ocf.iloc[-1]
        )

        ocf_lag_12 = float(
            historical_ocf.tail(12).iloc[0]
            if len(historical_ocf) >= 12
            else historical_ocf.iloc[-1]
        )

        recent_ocf_3 = float(
            historical_ocf.tail(
                SHORT_WINDOW
            ).median()
        )

        recent_ocf_6 = float(
            historical_ocf.tail(
                MEDIUM_WINDOW
            ).median()
        )

        recent_ocf_12 = float(
            historical_ocf.tail(
                LONG_WINDOW
            ).median()
        )

        recent_ocf_mean_6 = float(
            historical_ocf.tail(
                MEDIUM_WINDOW
            ).mean()
        )

        conversion = (
            historical_ocf
            / historical_revenue.replace(
                0,
                np.nan,
            )
        )

        conversion = conversion.replace(
            [np.inf, -np.inf],
            np.nan,
        ).dropna()

        if conversion.empty:
            conversion_median_3 = 0.0
            conversion_median_6 = 0.0
            conversion_median_12 = 0.0

        else:

            clipped = conversion.clip(
                lower=conversion.quantile(
                    0.10
                ),
                upper=conversion.quantile(
                    0.90
                ),
            )

            conversion_median_3 = float(
                clipped.tail(3).median()
            )

            conversion_median_6 = float(
                clipped.tail(6).median()
            )

            conversion_median_12 = float(
                clipped.tail(12).median()
            )

        latest_revenue = float(
            historical_revenue.iloc[-1]
        )

        prior_revenue = float(
            historical_revenue.iloc[-2]
            if len(historical_revenue) >= 2
            else latest_revenue
        )

        revenue_change_1 = (
            (
                latest_revenue
                - prior_revenue
            )
            / prior_revenue
            if prior_revenue != 0
            else 0.0
        )

        latest_cost = float(
            historical_costs.iloc[-1]
        )

        costs_lag_3 = float(
            historical_costs.tail(3).iloc[0]
            if len(historical_costs) >= 3
            else latest_cost
        )

        costs_lag_12 = float(
            historical_costs.tail(12).iloc[0]
            if len(historical_costs) >= 12
            else latest_cost
        )

        latest_nwc = float(
            historical_nwc.iloc[-1]
        )

        nwc_lag_3 = float(
            historical_nwc.tail(3).iloc[0]
            if len(historical_nwc) >= 3
            else latest_nwc
        )

        nwc_lag_12 = float(
            historical_nwc.tail(12).iloc[0]
            if len(historical_nwc) >= 12
            else latest_nwc
        )

        if len(historical_nwc) >= 2:
            nwc_change_lag_1 = float(
                historical_nwc.iloc[-1]
                - historical_nwc.iloc[-2]
            )
        else:
            nwc_change_lag_1 = 0.0

        latest_net_profit = float(
            historical_net_profit.iloc[-1]
        )

        net_profit_lag_3 = float(
            historical_net_profit.tail(3).iloc[0]
            if len(historical_net_profit) >= 3
            else latest_net_profit
        )

        net_profit_lag_12 = float(
            historical_net_profit.tail(12).iloc[0]
            if len(historical_net_profit) >= 12
            else latest_net_profit
        )

        # ----------------------------------------------------
        # Construct row
        # ----------------------------------------------------

        row = {
            "month": month,
            "quarter": quarter,

            "month_sin": np.sin(
                2
                * np.pi
                * month
                / 12.0
            ),

            "month_cos": np.cos(
                2
                * np.pi
                * month
                / 12.0
            ),

            "time_index":
                len(history)
                + len(rows),

            "revenue_abs":
                revenue,

            "operating_costs_abs":
                operating_costs_abs,

            "ebitda_proxy":
                revenue
                - operating_costs_abs,

            "cost_to_revenue":
                (
                    operating_costs_abs
                    / revenue
                    if revenue != 0
                    else 0.0
                ),

            "revenue_lag_1":
                latest_revenue,

            "revenue_lag_3":
                historical_revenue.tail(3).iloc[0]
                if len(historical_revenue) >= 3
                else latest_revenue,

            "revenue_lag_12":
                historical_revenue.tail(12).iloc[0]
                if len(historical_revenue) >= 12
                else latest_revenue,

            "revenue_change_1":
                revenue_change_1,

            "costs_lag_1":
                latest_cost,

            "costs_lag_3":
                costs_lag_3,

            "costs_lag_12":
                costs_lag_12,

            "ocf_lag_1":
                ocf_lag_1,

            "ocf_lag_3":
                ocf_lag_3,

            "ocf_lag_6":
                ocf_lag_6,

            "ocf_lag_12":
                ocf_lag_12,

            "ocf_rolling_median_3":
                recent_ocf_3,

            "ocf_rolling_median_6":
                recent_ocf_6,

            "ocf_rolling_median_12":
                recent_ocf_12,

            "ocf_rolling_mean_6":
                recent_ocf_mean_6,

            "conversion_median_3":
                conversion_median_3,

            "conversion_median_6":
                conversion_median_6,

            "conversion_median_12":
                conversion_median_12,

            "nwc_lag_1":
                latest_nwc,

            "nwc_lag_3":
                nwc_lag_3,

            "nwc_lag_12":
                nwc_lag_12,

            "nwc_change_lag_1":
                nwc_change_lag_1,

            "net_profit_lag_1":
                latest_net_profit,

            "net_profit_lag_3":
                net_profit_lag_3,

            "net_profit_lag_12":
                net_profit_lag_12,

            "period":
                period,
        }

        rows.append(
            row
        )

    return pd.DataFrame(
        rows
    )


# ============================================================
# FINAL FORECAST
# ============================================================

def generate_ocf_forecast(
    history: pd.DataFrame,
    future_drivers: pd.DataFrame,
    validation: dict[str, object],
) -> pd.DataFrame:
    """
    Generate six-month OCF forecast.

    The selected model is trained on the full available
    historical dataset.

    No future predicted OCF is fed back into the model.
    """

    selected_type = str(
        validation[
            "selected_type"
        ]
    )

    selected_name = str(
        validation[
            "selected_name"
        ]
    )

    metrics = (
        validation[
            "selected_metrics"
        ]
    )

    future_features = (
        create_future_feature_rows(
            history=history,
            future_drivers=future_drivers,
        )
    )

    X_future = future_features[
        FEATURE_COLUMNS
    ].copy()

    X_future = (
        X_future
        .replace(
            [np.inf, -np.inf],
            np.nan,
        )
        .fillna(0)
    )

    # --------------------------------------------------------
    # Baseline
    # --------------------------------------------------------

    baseline_pred = baseline_prediction(
        history=history,
        periods=future_drivers["period"],
        driver_revenue=future_drivers[
            "revenue"
        ],
    )

    # --------------------------------------------------------
    # ML
    # --------------------------------------------------------

    ml_prediction = None

    if selected_type == "ML":

        X, y, _ = prepare_training_data(
            history
        )

        if selected_name == (
            "HistGradientBoosting"
        ):
            model = (
                create_hist_gradient_model()
            )

        elif selected_name == (
            "RandomForest"
        ):
            model = (
                create_random_forest_model()
            )

        else:
            raise RuntimeError(
                f"Unknown selected model: "
                f"{selected_name}"
            )

        logger.info(
            "Training final Cash Flow model "
            "on %s observations.",
            len(X),
        )

        model.fit(
            X,
            y,
        )

        ml_prediction = (
            model.predict(
                X_future
            )
        )

        ml_prediction = np.asarray(
            ml_prediction,
            dtype=float,
        )

        # ----------------------------------------------------
        # Final defensive clipping
        # ----------------------------------------------------

        if not np.isfinite(
            ml_prediction
        ).all():
            raise RuntimeError(
                "ML OCF forecast contains "
                "non-finite values."
            )

    # --------------------------------------------------------
    # Select / blend
    # --------------------------------------------------------

    if selected_type == "ML":

        improvement = float(
            validation[
                "improvement_vs_baseline"
            ]
        )

        # Strongly outperforming ML:
        # use 80% ML / 20% baseline.
        #
        # Moderately outperforming ML:
        # use 65% ML / 35% baseline.
        #
        # This keeps the forecast stable.
        if improvement >= 0.20:
            ml_weight = 0.80
        else:
            ml_weight = 0.65

        baseline_weight = (
            1.0
            - ml_weight
        )

        final_prediction = (
            ml_weight
            * ml_prediction
            + baseline_weight
            * baseline_pred
        )

        logger.info(
            "Final OCF blend: ML %.0f%% / "
            "Baseline %.0f%%",
            ml_weight * 100.0,
            baseline_weight * 100.0,
        )

    else:

        final_prediction = (
            baseline_pred
        )

        logger.info(
            "Final OCF method: Robust Baseline"
        )

    # --------------------------------------------------------
    # Build forecast
    # --------------------------------------------------------

    result = future_drivers[
        [
            "period",
        ]
    ].copy()

    result[
        "predicted_operating_cash_flow"
    ] = (
        final_prediction
    )

    # Defensive finite check.
    if not np.isfinite(
        result[
            "predicted_operating_cash_flow"
        ]
    ).all():
        raise RuntimeError(
            "Final OCF forecast contains "
            "non-finite values."
        )

    # --------------------------------------------------------
    # Prediction interval
    # --------------------------------------------------------

    validation_results = (
        validation[
            "validation_results"
        ]
    )

    selected_validation = (
        validation_results[
            validation[
                "selected_name"
            ]
        ]
        if validation[
            "selected_type"
        ] == "ML"
        else validation_results[
            "Baseline"
        ]
    )

    validation_actual = (
        selected_validation[
            "metrics"
        ]
    )

    residuals = None

    actual_prediction = np.asarray(
        selected_validation[
            "prediction"
        ],
        dtype=float,
    )

    # The corresponding actual values are always
    # the validation tail.
    _, y, training = (
        prepare_training_data(
            history
        )
    )

    validation_actual_values = (
        y.iloc[
            -VALIDATION_MONTHS:
        ]
        .to_numpy()
    )

    residuals = (
        validation_actual_values
        - actual_prediction
    )

    absolute_residuals = np.abs(
        residuals
    )

    if len(
        absolute_residuals
    ) > 1:

        interval_width = float(
            np.quantile(
                absolute_residuals,
                INTERVAL_QUANTILE,
            )
        )

    else:

        interval_width = float(
            validation_actual[
                "residual_std"
            ]
        )

    if not np.isfinite(
        interval_width
    ) or interval_width <= 0:

        interval_width = float(
            validation_actual[
                "rmse"
            ]
        )

    result[
        "ocf_lower_bound"
    ] = (
        result[
            "predicted_operating_cash_flow"
        ]
        - interval_width
    )

    result[
        "ocf_upper_bound"
    ] = (
        result[
            "predicted_operating_cash_flow"
        ]
        + interval_width
    )

    result[
        "selected_method"
    ] = (
        selected_name
    )

    result[
        "validation_mae"
    ] = (
        validation_actual[
            "mae"
        ]
    )

    result[
        "validation_rmse"
    ] = (
        validation_actual[
            "rmse"
        ]
    )

    result[
        "validation_smape_pct"
    ] = (
        validation_actual[
            "smape_pct"
        ]
    )

    result[
        "validation_stabilized_mape_pct"
    ] = (
        validation_actual[
            "stabilized_mape_pct"
        ]
    )

    result[
        "validation_residual_std"
    ] = (
        validation_actual[
            "residual_std"
        ]
    )

    result[
        "forecast_interval_width"
    ] = (
        interval_width
    )

    return result


# ============================================================
# CLOSING CASH BRIDGE
# ============================================================

def build_cash_bridge(
    history: pd.DataFrame,
    ocf_forecast: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate Closing Cash from the OCF forecast.

    Formula:
        Closing Cash(t)
            = Closing Cash(t-1)
            + Forecast OCF(t)

    This explicitly assumes:
        Investing CF = 0
        Financing CF = 0

    until those components receive dedicated forecasts.
    """

    last_actual_period = (
        history["period"].max()
    )

    last_actual_row = (
        history[
            history["period"]
            == last_actual_period
        ]
        .iloc[0]
    )

    opening_cash = float(
        last_actual_row[
            "closing_cash"
        ]
    )

    running_cash = opening_cash

    rows = []

    monthly_half_width = (
        ocf_forecast[
            "forecast_interval_width"
        ]
    )

    cumulative_variance = 0.0

    for index, row in (
        ocf_forecast
        .sort_values("period")
        .reset_index(drop=True)
        .iterrows()
    ):

        operating_cf = float(
            row[
                "predicted_operating_cash_flow"
            ]
        )

        running_cash += (
            operating_cf
        )

        monthly_error = float(
            monthly_half_width.iloc[
                index
            ]
        )

        cumulative_variance += (
            monthly_error ** 2
        )

        cumulative_error = float(
            np.sqrt(
                cumulative_variance
            )
        )

        rows.append(
            {
                "period":
                    row["period"],

                "predicted_operating_cash_flow":
                    operating_cf,

                "ocf_lower_bound":
                    float(
                        row[
                            "ocf_lower_bound"
                        ]
                    ),

                "ocf_upper_bound":
                    float(
                        row[
                            "ocf_upper_bound"
                        ]
                    ),

                "predicted_closing_cash":
                    running_cash,

                "cash_lower_bound":
                    running_cash
                    - cumulative_error,

                "cash_upper_bound":
                    running_cash
                    + cumulative_error,
            }
        )

    result = pd.DataFrame(
        rows
    )

    return result


# ============================================================
# OUTPUT VALIDATION
# ============================================================

def validate_output(
    history: pd.DataFrame,
    output: pd.DataFrame,
) -> None:
    """Validate final forecast output."""

    if output.empty:
        raise RuntimeError(
            "Cash Flow forecast output is empty."
        )

    if len(output) != HORIZON:
        raise RuntimeError(
            "Invalid forecast horizon: "
            f"expected {HORIZON}, "
            f"found {len(output)}."
        )

    periods = (
        output["period"]
        .sort_values()
        .reset_index(
            drop=True
        )
    )

    expected = pd.Series(
        pd.date_range(
            start=periods.iloc[0],
            periods=HORIZON,
            freq="MS",
        )
    )

    if not periods.equals(
        expected
    ):
        raise RuntimeError(
            "Cash Flow forecast periods "
            "are not consecutive."
        )

    if output[
        "period"
    ].duplicated().any():
        raise RuntimeError(
            "Cash Flow forecast contains "
            "duplicate periods."
        )

    # --------------------------------------------------------
    # Numeric validation
    # --------------------------------------------------------

    numeric_columns = [
        "predicted_operating_cash_flow",
        "ocf_lower_bound",
        "ocf_upper_bound",
        "predicted_closing_cash",
        "cash_lower_bound",
        "cash_upper_bound",
    ]

    for column in numeric_columns:

        values = pd.to_numeric(
            output[column],
            errors="coerce",
        )

        if values.isna().any():
            raise RuntimeError(
                f"Cash Flow forecast column "
                f"'{column}' contains invalid values."
            )

        if not np.isfinite(
            values.to_numpy(
                dtype=float
            )
        ).all():
            raise RuntimeError(
                f"Cash Flow forecast column "
                f"'{column}' contains non-finite values."
            )

    # --------------------------------------------------------
    # Interval validation
    # --------------------------------------------------------

    invalid_ocf = (
        output[
            "ocf_lower_bound"
        ]
        >
        output[
            "ocf_upper_bound"
        ]
    )

    if invalid_ocf.any():
        raise RuntimeError(
            "OCF prediction interval is invalid."
        )

    invalid_cash = (
        output[
            "cash_lower_bound"
        ]
        >
        output[
            "cash_upper_bound"
        ]
    )

    if invalid_cash.any():
        raise RuntimeError(
            "Closing Cash prediction interval is invalid."
        )

    # --------------------------------------------------------
    # Cash bridge validation
    # --------------------------------------------------------

    previous_cash = float(
        history[
            history["period"]
            == history["period"].max()
        ]["closing_cash"].iloc[0]
    )

    for _, row in output.iterrows():

        expected_cash = (
            previous_cash
            + float(
                row[
                    "predicted_operating_cash_flow"
                ]
            )
        )

        actual_cash = float(
            row[
                "predicted_closing_cash"
            ]
        )

        if not np.isclose(
            expected_cash,
            actual_cash,
            atol=0.01,
        ):
            raise RuntimeError(
                "Closing Cash bridge validation failed "
                f"for {row['period']}: "
                f"expected {expected_cash}, "
                f"found {actual_cash}."
            )

        previous_cash = actual_cash

    logger.info(
        "Cash Flow forecast output validation passed."
    )


# ============================================================
# SAVE OUTPUT
# ============================================================

def save_output(
    df: pd.DataFrame,
) -> None:
    """Save Cash Flow prediction dataset."""

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
    """Run EFAP Cash Flow Prediction pipeline."""

    try:

        logger.info(
            "Starting EFAP Cash Flow Prediction."
        )

        # ----------------------------------------------------
        # VALIDATE FILES
        # ----------------------------------------------------

        validate_files()

        # ----------------------------------------------------
        # LOAD
        # ----------------------------------------------------

        history = (
            load_historical_data()
        )

        revenue_prediction = (
            load_revenue_prediction()
        )

        expense_forecast = (
            load_expense_forecast()
        )

        # ----------------------------------------------------
        # VALIDATION / MODEL SELECTION
        # ----------------------------------------------------

        validation = (
            validate_models(
                history
            )
        )

        # ----------------------------------------------------
        # FINAL MODEL / BASELINE FORECAST
        # ----------------------------------------------------

        future_drivers = (
            build_future_drivers(
                history=history,
                revenue_prediction=(
                    revenue_prediction
                ),
                expense_forecast=(
                    expense_forecast
                ),
            )
        )

        if len(
            future_drivers
        ) != HORIZON:

            raise RuntimeError(
                "Invalid future driver horizon: "
                f"expected {HORIZON}, "
                f"found {len(future_drivers)}."
            )

        logger.info(
            "Future driver horizon: %s months.",
            len(future_drivers),
        )

        logger.info(
            "Forecast period: %s -> %s",
            future_drivers[
                "period"
            ].min().strftime("%Y-%m"),
            future_drivers[
                "period"
            ].max().strftime("%Y-%m"),
        )

        # ----------------------------------------------------
        # OCF FORECAST
        # ----------------------------------------------------

        ocf_forecast = (
            generate_ocf_forecast(
                history=history,
                future_drivers=(
                    future_drivers
                ),
                validation=validation,
            )
        )

        # ----------------------------------------------------
        # CASH BRIDGE
        # ----------------------------------------------------

        cash_bridge = (
            build_cash_bridge(
                history=history,
                ocf_forecast=ocf_forecast,
            )
        )

        output = (
            ocf_forecast[
                [
                    "period",
                    "selected_method",
                    "validation_mae",
                    "validation_rmse",
                    "validation_smape_pct",
                    "validation_stabilized_mape_pct",
                    "validation_residual_std",
                    "forecast_interval_width",
                ]
            ]
            .merge(
                cash_bridge,
                on="period",
                how="inner",
                validate="one_to_one",
            )
        )

        # ----------------------------------------------------
        # OUTPUT METADATA
        # ----------------------------------------------------

        output[
            "model"
        ] = (
            output[
                "selected_method"
            ]
        )

        output[
            "prediction_type"
        ] = "ML_PREDICTION"

        output[
            "year_month"
        ] = (
            output[
                "period"
            ]
            .dt.strftime(
                "%Y-%m"
            )
        )

        output[
            "forecast_year"
        ] = (
            output[
                "period"
            ]
            .dt.year
        )

        output[
            "forecast_month"
        ] = (
            output[
                "period"
            ]
            .dt.month
        )

        output = output[
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

                "validation_mae",
                "validation_rmse",
                "validation_smape_pct",
                "validation_stabilized_mape_pct",
                "validation_residual_std",
                "forecast_interval_width",

                "prediction_type",
            ]
        ].copy()

        # ----------------------------------------------------
        # VALIDATE
        # ----------------------------------------------------

        validate_output(
            history=history,
            output=output,
        )

        # ----------------------------------------------------
        # LOG CONTEXT
        # ----------------------------------------------------

        last_actual_period = (
            history["period"].max()
        )

        latest = (
            history[
                history["period"]
                == last_actual_period
            ]
            .iloc[0]
        )

        logger.info(
            "Latest actual financial context:"
        )

        logger.info(
            "Revenue: %.2f",
            latest[
                "revenue"
            ],
        )

        logger.info(
            "Operating Costs: %.2f",
            latest[
                "operating_costs"
            ],
        )

        logger.info(
            "Operating Cash Flow: %.2f",
            latest[
                "operating_cash_flow"
            ],
        )

        logger.info(
            "Closing Cash: %.2f",
            latest[
                "closing_cash"
            ],
        )

        logger.info(
            "Selected Cash Flow method: %s",
            validation[
                "selected_name"
            ],
        )

        logger.info(
            "ML improvement vs baseline: %.2f%%",
            float(
                validation[
                    "improvement_vs_baseline"
                ]
            )
            * 100.0,
        )

        # ----------------------------------------------------
        # FORECAST LOG
        # ----------------------------------------------------

        for index, row in (
            output
            .sort_values("period")
            .reset_index(
                drop=True
            )
            .iterrows()
        ):

            logger.info(
                "Cash Flow forecast %s/%s | %s | "
                "OCF %.2f | Cash %.2f",
                index + 1,
                len(output),
                row[
                    "period"
                ].strftime(
                    "%Y-%m"
                ),
                row[
                    "predicted_operating_cash_flow"
                ],
                row[
                    "predicted_closing_cash"
                ],
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