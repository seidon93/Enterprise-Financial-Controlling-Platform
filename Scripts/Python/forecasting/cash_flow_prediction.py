"""
EFAP - Cash Flow Prediction

Object:
    Python/forecasting/cash_flow_prediction.py

Purpose:
    Predict future Operating Cash Flow and Closing Cash.

Sources:
    data/processed/controller_kpi_timeseries.csv
    data/predictions/revenue_prediction.csv
    data/forecasts/expense_forecast.csv

Model:
    HistGradientBoostingRegressor

Targets:
    Operating Cash Flow
    Closing Cash

Forecast horizon:
    6 months

Management sign convention:
    Revenue              positive
    Operating Costs      negative
    Operating Cash Flow  signed
    Closing Cash         signed

Important:
    - PostgreSQL remains the financial source of truth.
    - This module performs predictive analytics only.
    - No database credentials are stored in source code.
    - Future Revenue and Operating Costs come from dedicated
      forecast layers.
    - Future Net Profit and Working Capital are NOT artificially
      held constant.
    - Closing Cash is derived from previous Closing Cash + predicted OCF.
    - Cash uncertainty accumulates through the forecast horizon.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Final

import numpy as np
import pandas as pd

from sklearn.ensemble import HistGradientBoostingRegressor
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

# Forecast blend:
# ML model provides the main prediction.
# A cash-conversion baseline stabilizes the model
# when the historical sample is small/noisy.
ML_WEIGHT: Final[float] = 0.75
BASELINE_WEIGHT: Final[float] = 0.25

# Confidence interval:
# Approximate 95% interval using residual standard deviation.
CONFIDENCE_Z: Final[float] = 1.96

# Lower limit for denominator in stabilized MAPE.
MAPE_EPSILON: Final[float] = 1_000_000.0


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
        "controller KPI time series":
            TIME_SERIES_FILE,

        "revenue prediction":
            REVENUE_PREDICTION_FILE,

        "expense forecast":
            EXPENSE_FORECAST_FILE,
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
# GENERIC PERIOD NORMALIZATION
# ============================================================

def normalize_month(
    series: pd.Series,
) -> pd.Series:
    """Normalize dates to monthly-start timestamps."""

    return (
        pd.to_datetime(
            series,
            errors="coerce",
        )
        .dt.to_period("M")
        .dt.to_timestamp()
    )


# ============================================================
# LOAD HISTORICAL DATA
# ============================================================

def load_historical_data() -> pd.DataFrame:
    """Load and normalize historical controller KPI data."""

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

    df["period"] = normalize_month(
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

    # --------------------------------------------------------
    # MANAGEMENT SIGN CONVENTION
    # --------------------------------------------------------

    df["revenue"] = (
        df["revenue"]
        .abs()
    )

    df["operating_costs"] = (
        -df["operating_costs"]
        .abs()
    )

    if len(df) < MIN_HISTORY:
        raise ValueError(
            f"At least {MIN_HISTORY} monthly observations "
            f"are required. Found {len(df)}."
        )

    # --------------------------------------------------------
    # MONTHLY CONTINUITY
    # --------------------------------------------------------

    expected_periods = pd.date_range(
        start=df["period"].min(),
        end=df["period"].max(),
        freq="MS",
    )

    actual_periods = (
        df["period"]
        .drop_duplicates()
        .sort_values()
    )

    if not actual_periods.equals(
        pd.Series(
            expected_periods,
            name="period",
        )
    ):
        raise RuntimeError(
            "Historical financial time series is not continuous "
            "at monthly grain."
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
    """Load Revenue ML forecast."""

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

    df["period"] = normalize_month(
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

    # Revenue must follow positive management convention.
    df["predicted_revenue"] = (
        df["predicted_revenue"]
        .abs()
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

    Current EFAP source contract:

        forecast_period
        account_number
        account_name
        forecast_expense
        lower_bound
        upper_bound
        selected_model
        validation_rmse

    The data is aggregated to monthly expense magnitude.
    """

    logger.info(
        "Loading Expense forecast: %s",
        EXPENSE_FORECAST_FILE,
    )

    df = pd.read_csv(
        EXPENSE_FORECAST_FILE
    )

    # --------------------------------------------------------
    # SOURCE PERIOD
    # --------------------------------------------------------

    if "forecast_period" in df.columns:
        period_column = "forecast_period"

    elif "period" in df.columns:
        period_column = "period"

    else:
        raise ValueError(
            "Expense forecast must contain either "
            "'forecast_period' or 'period'."
        )

    # --------------------------------------------------------
    # SOURCE EXPENSE
    # --------------------------------------------------------

    if "forecast_expense" in df.columns:
        expense_column = "forecast_expense"

    elif "predicted_expense" in df.columns:
        expense_column = "predicted_expense"

    else:
        raise ValueError(
            "Expense forecast must contain either "
            "'forecast_expense' or 'predicted_expense'."
        )

    df["period"] = normalize_month(
        df[period_column]
    )

    df["expense_magnitude"] = pd.to_numeric(
        df[expense_column],
        errors="coerce",
    ).abs()

    df = df.dropna(
        subset=[
            "period",
            "expense_magnitude",
        ]
    )

    # --------------------------------------------------------
    # FUTURE MONTHLY AGGREGATION
    # --------------------------------------------------------

    monthly = (
        df
        .groupby(
            "period",
            as_index=False,
        )
        .agg(
            predicted_expense=(
                "expense_magnitude",
                "sum",
            )
        )
        .sort_values("period")
        .reset_index(drop=True)
    )

    logger.info(
        "Expense forecast periods: %s",
        len(monthly),
    )

    return monthly


# ============================================================
# HISTORICAL FEATURE ENGINEERING
# ============================================================

def create_features(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create OCF forecasting features.

    Important design decision:
        Only variables that are realistically available
        for future forecasting are used as direct predictors.

    This avoids artificially fixing future Net Profit and NWC.
    """

    result = df.copy()

    # --------------------------------------------------------
    # Calendar
    # --------------------------------------------------------

    result["month"] = (
        result["period"]
        .dt.month
    )

    result["quarter"] = (
        result["period"]
        .dt.quarter
    )

    result["month_sin"] = np.sin(
        2
        * np.pi
        * result["month"]
        / 12
    )

    result["month_cos"] = np.cos(
        2
        * np.pi
        * result["month"]
        / 12
    )

    result["time_index"] = np.arange(
        len(result)
    )

    # --------------------------------------------------------
    # Current financial drivers
    # --------------------------------------------------------

    result["revenue_current"] = (
        result["revenue"]
    )

    result["operating_costs_current"] = (
        result["operating_costs"]
    )

    result["operating_cost_ratio"] = np.where(
        result["revenue"] != 0,
        result["operating_costs"]
        / result["revenue"].abs(),
        0.0,
    )

    # --------------------------------------------------------
    # Revenue history
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

    result["revenue_change_1"] = (
        result["revenue"]
        .diff()
        .shift(1)
    )

    # --------------------------------------------------------
    # Cost history
    # --------------------------------------------------------

    result["cost_lag_1"] = (
        result["operating_costs"]
        .shift(1)
    )

    result["cost_lag_3"] = (
        result["operating_costs"]
        .shift(3)
    )

    result["cost_lag_12"] = (
        result["operating_costs"]
        .shift(12)
    )

    result["cost_change_1"] = (
        result["operating_costs"]
        .diff()
        .shift(1)
    )

    # --------------------------------------------------------
    # OCF history
    # --------------------------------------------------------

    result["ocf_lag_1"] = (
        result["operating_cash_flow"]
        .shift(1)
    )

    result["ocf_lag_2"] = (
        result["operating_cash_flow"]
        .shift(2)
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

    result["ocf_rolling_3"] = (
        result["operating_cash_flow"]
        .shift(1)
        .rolling(
            3,
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

    result["ocf_margin_lag_1"] = np.where(
        result["revenue"].shift(1).abs() > 0,
        result["operating_cash_flow"].shift(1)
        / result["revenue"].shift(1).abs(),
        0.0,
    )

    result["ocf_margin_rolling_3"] = (
        result["ocf_margin_lag_1"]
        .rolling(
            3,
            min_periods=3,
        )
        .mean()
    )

    # --------------------------------------------------------
    # Cash history
    # --------------------------------------------------------

    result["cash_lag_1"] = (
        result["closing_cash"]
        .shift(1)
    )

    result["cash_lag_3"] = (
        result["closing_cash"]
        .shift(3)
    )

    result["cash_change_lag_1"] = (
        result["closing_cash"]
        .diff()
        .shift(1)
    )

    return result


FEATURE_COLUMNS: Final[list[str]] = [
    # Calendar
    "month",
    "quarter",
    "month_sin",
    "month_cos",
    "time_index",

    # Current financial drivers
    "revenue_current",
    "operating_costs_current",
    "operating_cost_ratio",

    # Revenue history
    "revenue_lag_1",
    "revenue_lag_3",
    "revenue_lag_12",
    "revenue_change_1",

    # Cost history
    "cost_lag_1",
    "cost_lag_3",
    "cost_lag_12",
    "cost_change_1",

    # OCF history
    "ocf_lag_1",
    "ocf_lag_2",
    "ocf_lag_3",
    "ocf_lag_6",
    "ocf_lag_12",
    "ocf_rolling_3",
    "ocf_rolling_6",
    "ocf_margin_lag_1",
    "ocf_margin_rolling_3",

    # Cash history
    "cash_lag_1",
    "cash_lag_3",
    "cash_change_lag_1",
]


# ============================================================
# MODEL
# ============================================================

def create_model() -> HistGradientBoostingRegressor:
    """Create the OCF prediction model."""

    return HistGradientBoostingRegressor(
        learning_rate=0.04,
        max_iter=400,
        max_leaf_nodes=12,
        min_samples_leaf=5,
        l2_regularization=3.0,
        random_state=RANDOM_STATE,
    )


# ============================================================
# METRICS
# ============================================================

def calculate_metrics(
    actual: np.ndarray,
    predicted: np.ndarray,
) -> dict[str, float]:
    """
    Calculate robust validation metrics.

    MAPE is stabilized because OCF may be negative and/or
    close to zero. We therefore use an epsilon denominator.
    """

    actual = np.asarray(
        actual,
        dtype=float,
    )

    predicted = np.asarray(
        predicted,
        dtype=float,
    )

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

    denominator = np.maximum(
        np.abs(actual),
        MAPE_EPSILON,
    )

    mape = (
        np.mean(
            np.abs(
                actual - predicted
            )
            / denominator
        )
        * 100
    )

    smape_denominator = (
        np.abs(actual)
        + np.abs(predicted)
    )

    smape_mask = (
        smape_denominator > 0
    )

    if np.any(smape_mask):
        smape = (
            np.mean(
                2
                * np.abs(
                    actual[smape_mask]
                    - predicted[smape_mask]
                )
                / smape_denominator[
                    smape_mask
                ]
            )
            * 100
        )
    else:
        smape = 0.0

    residuals = (
        actual - predicted
    )

    residual_std = float(
        np.std(
            residuals,
            ddof=1,
        )
    ) if len(residuals) > 1 else float(
        abs(rmse)
    )

    if not np.isfinite(residual_std):
        residual_std = float(
            abs(rmse)
        )

    return {
        "mae": float(mae),
        "rmse": float(rmse),
        "mape_pct": float(mape),
        "smape_pct": float(smape),
        "residual_std": residual_std,
    }


# ============================================================
# PREPARE TRAINING DATA
# ============================================================

def prepare_training_data(
    history: pd.DataFrame,
) -> tuple[
    pd.DataFrame,
    pd.Series,
]:
    """Prepare historical supervised learning dataset."""

    features = create_features(
        history
    )

    training = (
        features
        .dropna(
            subset=FEATURE_COLUMNS
            + [
                "operating_cash_flow"
            ]
        )
        .copy()
    )

    if training.empty:
        raise ValueError(
            "No valid OCF training observations."
        )

    X = training[
        FEATURE_COLUMNS
    ]

    y = training[
        "operating_cash_flow"
    ]

    return X, y


# ============================================================
# BASELINE
# ============================================================

def calculate_cash_conversion_baseline(
    history: pd.DataFrame,
) -> float:
    """
    Calculate a robust OCF baseline.

    Baseline:
        median OCF / Revenue ratio over recent history.

    The baseline is deliberately conservative and acts only
    as a stabilizer for the ML model.
    """

    recent = (
        history
        .copy()
        .sort_values("period")
        .tail(12)
    )

    denominator = (
        recent["revenue"]
        .abs()
        .replace(
            0,
            np.nan,
        )
    )

    ratio = (
        recent["operating_cash_flow"]
        / denominator
    )

    ratio = (
        ratio
        .replace(
            [np.inf, -np.inf],
            np.nan,
        )
        .dropna()
    )

    if ratio.empty:
        return 0.0

    # Robust limits prevent a single abnormal month
    # from dominating the baseline.
    q_low = ratio.quantile(0.10)
    q_high = ratio.quantile(0.90)

    clipped = ratio.clip(
        lower=q_low,
        upper=q_high,
    )

    baseline = float(
        clipped.median()
    )

    return baseline


# ============================================================
# VALIDATION
# ============================================================

def validate_ocf_model(
    history: pd.DataFrame,
) -> dict[str, float]:
    """
    Validate OCF model using a chronological holdout.

    This preserves the time-series nature of the problem.
    """

    X, y = prepare_training_data(
        history
    )

    if len(X) <= VALIDATION_MONTHS:
        raise ValueError(
            "Not enough observations for OCF validation."
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

    model = create_model()

    model.fit(
        X_train,
        y_train,
    )

    ml_prediction = model.predict(
        X_test
    )

    # --------------------------------------------------------
    # BASELINE ON VALIDATION
    # --------------------------------------------------------

    validation_features = (
        create_features(
            history
        )
    )

    recent_history = (
        history.iloc[
            :split + (
                len(history)
                - len(X)
            )
        ]
    )

    baseline_ratio = (
        calculate_cash_conversion_baseline(
            recent_history
        )
    )

    baseline_prediction = (
        validation_features
        .iloc[
            -VALIDATION_MONTHS:
        ]["revenue"]
        .abs()
        .to_numpy()
        * baseline_ratio
    )

    blended_prediction = (
        ML_WEIGHT
        * ml_prediction
        + BASELINE_WEIGHT
        * baseline_prediction
    )

    metrics = calculate_metrics(
        y_test.to_numpy(),
        blended_prediction,
    )

    logger.info(
        "Operating CF validation:"
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
        metrics["mape_pct"],
    )

    logger.info(
        "sMAPE: %.2f%%",
        metrics["smape_pct"],
    )

    logger.info(
        "Residual standard deviation: %.2f",
        metrics["residual_std"],
    )

    logger.info(
        "Validation blend: ML %.0f%% / Baseline %.0f%%",
        ML_WEIGHT * 100,
        BASELINE_WEIGHT * 100,
    )

    return metrics


# ============================================================
# FUTURE DATASET
# ============================================================

def prepare_future_inputs(
    revenue_prediction: pd.DataFrame,
    expense_prediction: pd.DataFrame,
    actual_cutoff: pd.Timestamp,
) -> pd.DataFrame:
    """
    Prepare the future six-month financial drivers.

    Future:
        Revenue -> dedicated Revenue ML
        Costs   -> dedicated Expense forecast

    This creates the current-period drivers used by the OCF model.
    """

    revenue = (
        revenue_prediction[
            revenue_prediction["period"]
            > actual_cutoff
        ]
        .copy()
    )

    expense = (
        expense_prediction[
            expense_prediction["period"]
            > actual_cutoff
        ]
        .copy()
    )

    revenue_periods = set(
        revenue["period"]
    )

    expense_periods = set(
        expense["period"]
    )

    overlapping = sorted(
        revenue_periods
        & expense_periods
    )

    if not overlapping:
        raise RuntimeError(
            "Revenue and Expense prediction layers "
            "have no overlapping future periods."
        )

    future = pd.DataFrame(
        {
            "period": overlapping,
        }
    )

    future = (
        future
        .merge(
            revenue[
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
            expense[
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

    future = future.rename(
        columns={
            "predicted_revenue":
                "revenue",

            "predicted_expense":
                "expense_magnitude",
        }
    )

    future["revenue"] = (
        pd.to_numeric(
            future["revenue"],
            errors="coerce",
        )
        .abs()
    )

    future["operating_costs"] = (
        -pd.to_numeric(
            future["expense_magnitude"],
            errors="coerce",
        ).abs()
    )

    if future[
        [
            "revenue",
            "operating_costs",
        ]
    ].isna().any().any():
        raise RuntimeError(
            "Future Revenue/Expense inputs contain "
            "invalid numeric values."
        )

    future = (
        future[
            [
                "period",
                "revenue",
                "operating_costs",
            ]
        ]
        .sort_values("period")
        .reset_index(drop=True)
    )

    return future


# ============================================================
# RECURSIVE FORECAST
# ============================================================

def recursive_ocf_prediction(
    history: pd.DataFrame,
    model: HistGradientBoostingRegressor,
    revenue_prediction: pd.DataFrame,
    expense_prediction: pd.DataFrame,
) -> tuple[
    pd.DataFrame,
    float,
]:
    """
    Generate six-month recursive OCF forecast.

    Only genuinely available future drivers are injected:
        Revenue
        Operating Costs

    Historical lagged OCF and Cash are then updated recursively.
    """

    actual_cutoff = (
        history["period"].max()
    )

    future = prepare_future_inputs(
        revenue_prediction=revenue_prediction,
        expense_prediction=expense_prediction,
        actual_cutoff=actual_cutoff,
    )

    if len(future) != HORIZON:
        raise RuntimeError(
            "Cash Flow forecast horizon mismatch: "
            f"expected {HORIZON}, "
            f"found {len(future)}."
        )

    expected_periods = pd.Series(
        pd.date_range(
            start=future["period"].min(),
            periods=HORIZON,
            freq="MS",
        )
    )

    if not future[
        "period"
    ].reset_index(drop=True).equals(
        expected_periods
    ):
        raise RuntimeError(
            "Cash Flow forecast periods are not "
            "six consecutive months."
        )

    working = history[
        [
            "period",
            "revenue",
            "operating_costs",
            "net_profit",
            "net_working_capital",
            "operating_cash_flow",
            "closing_cash",
        ]
    ].copy()

    baseline_ratio = (
        calculate_cash_conversion_baseline(
            history
        )
    )

    logger.info(
        "Recent OCF / Revenue baseline: %.4f",
        baseline_ratio,
    )

    predictions = []

    for index, future_row in future.iterrows():

        period = future_row[
            "period"
        ]

        revenue = float(
            future_row["revenue"]
        )

        operating_costs = float(
            future_row[
                "operating_costs"
            ]
        )

        # ----------------------------------------------------
        # Historical context
        # ----------------------------------------------------

        latest_nwc = float(
            working[
                "net_working_capital"
            ]
            .dropna()
            .iloc[-1]
        )

        latest_net_profit = float(
            working[
                "net_profit"
            ]
            .dropna()
            .iloc[-1]
        )

        previous_cash = float(
            working[
                "closing_cash"
            ]
            .dropna()
            .iloc[-1]
        )

        # For future periods these two variables are not used
        # as direct model features, but keeping them in the
        # working dataset preserves the schema.
        new_row = {
            "period": period,
            "revenue": revenue,
            "operating_costs": operating_costs,
            "net_profit": latest_net_profit,
            "net_working_capital": latest_nwc,
            "operating_cash_flow": np.nan,
            "closing_cash": previous_cash,
        }

        working = pd.concat(
            [
                working,
                pd.DataFrame(
                    [new_row]
                ),
            ],
            ignore_index=True,
        )

        # ----------------------------------------------------
        # Feature engineering
        # ----------------------------------------------------

        engineered = create_features(
            working
        )

        current = engineered.iloc[
            [-1]
        ][FEATURE_COLUMNS].copy()

        # Any remaining missing lag due to short history is
        # filled using the latest known observation.
        current = (
            current
            .ffill(
                axis=0
            )
            .bfill(
                axis=0
            )
            .fillna(0.0)
        )

        # ----------------------------------------------------
        # ML prediction
        # ----------------------------------------------------

        ml_prediction = float(
            model.predict(
                current
            )[0]
        )

        # ----------------------------------------------------
        # Baseline prediction
        #
        # Recent cash conversion ratio x forecast revenue.
        # ----------------------------------------------------

        baseline_prediction = (
            revenue
            * baseline_ratio
        )

        # ----------------------------------------------------
        # Blend
        # ----------------------------------------------------

        prediction = (
            ML_WEIGHT
            * ml_prediction
            + BASELINE_WEIGHT
            * baseline_prediction
        )

        if not np.isfinite(
            prediction
        ):
            raise RuntimeError(
                f"Non-finite OCF prediction for "
                f"{period:%Y-%m}."
            )

        predictions.append(
            {
                "period": period,
                "ml_prediction":
                    ml_prediction,
                "baseline_prediction":
                    baseline_prediction,
                "predicted_operating_cash_flow":
                    prediction,
            }
        )

        # ----------------------------------------------------
        # Update recursive history
        # ----------------------------------------------------

        working.loc[
            working["period"] == period,
            "operating_cash_flow",
        ] = prediction

        predicted_cash = (
            previous_cash
            + prediction
        )

        working.loc[
            working["period"] == period,
            "closing_cash",
        ] = predicted_cash

        logger.info(
            "Cash Flow forecast %s/%s | %s | "
            "ML %.2f | Baseline %.2f | Final %.2f | Cash %.2f",
            index + 1,
            HORIZON,
            period.strftime("%Y-%m"),
            ml_prediction,
            baseline_prediction,
            prediction,
            predicted_cash,
        )

    return (
        pd.DataFrame(
            predictions
        ),
        baseline_ratio,
    )


# ============================================================
# OUTPUT
# ============================================================

def build_output(
    history: pd.DataFrame,
    ocf_forecast: pd.DataFrame,
    metrics: dict[str, float],
) -> pd.DataFrame:
    """
    Build final six-month cash-flow prediction dataset.

    Cash uncertainty accumulates across forecast periods.
    """

    if ocf_forecast.empty:
        raise RuntimeError(
            "OCF forecast is empty."
        )

    last_actual_period = (
        history["period"].max()
    )

    actual_cash = float(
        history.loc[
            history["period"]
            == last_actual_period,
            "closing_cash",
        ].iloc[0]
    )

    residual_std = float(
        metrics[
            "residual_std"
        ]
    )

    if residual_std <= 0:
        residual_std = float(
            metrics["rmse"]
        )

    outputs = []

    running_cash = actual_cash

    for horizon_index, row in enumerate(
        ocf_forecast.itertuples(
            index=False
        ),
        start=1,
    ):

        operating_cf = float(
            row.predicted_operating_cash_flow
        )

        running_cash += (
            operating_cf
        )

        # ----------------------------------------------------
        # OCF uncertainty
        # ----------------------------------------------------

        ocf_margin = (
            CONFIDENCE_Z
            * residual_std
        )

        ocf_lower = (
            operating_cf
            - ocf_margin
        )

        ocf_upper = (
            operating_cf
            + ocf_margin
        )

        # ----------------------------------------------------
        # Cash uncertainty
        #
        # Independent monthly residuals are approximated using
        # root-sum-of-squares accumulation.
        # ----------------------------------------------------

        cumulative_cash_std = (
            residual_std
            * np.sqrt(
                horizon_index
            )
        )

        cash_margin = (
            CONFIDENCE_Z
            * cumulative_cash_std
        )

        cash_lower = (
            running_cash
            - cash_margin
        )

        cash_upper = (
            running_cash
            + cash_margin
        )

        outputs.append(
            {
                "period":
                    row.period,

                "predicted_operating_cash_flow":
                    operating_cf,

                "ocf_lower_bound":
                    ocf_lower,

                "ocf_upper_bound":
                    ocf_upper,

                "predicted_closing_cash":
                    running_cash,

                "cash_lower_bound":
                    cash_lower,

                "cash_upper_bound":
                    cash_upper,
            }
        )

    result = pd.DataFrame(
        outputs
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

    result["model"] = (
        "HistGradientBoosting+Baseline"
    )

    result["validation_mae"] = (
        metrics["mae"]
    )

    result["validation_rmse"] = (
        metrics["rmse"]
    )

    result["validation_mape_pct"] = (
        metrics["mape_pct"]
    )

    result["prediction_type"] = (
        "ML_PREDICTION"
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
            "validation_mae",
            "validation_rmse",
            "validation_mape_pct",

            "prediction_type",
        ]
    ]


# ============================================================
# OUTPUT VALIDATION
# ============================================================

def validate_forecast_output(
    output: pd.DataFrame,
    history: pd.DataFrame,
) -> None:
    """Validate final forecast dataset."""

    if output.empty:
        raise RuntimeError(
            "Cash Flow forecast output is empty."
        )

    if len(output) != HORIZON:
        raise RuntimeError(
            f"Expected {HORIZON} forecast rows, "
            f"found {len(output)}."
        )

    periods = (
        output["period"]
        .sort_values()
        .reset_index(drop=True)
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
            "Cash Flow forecast periods are not "
            "consecutive."
        )

    actual_cutoff = (
        history["period"].max()
    )

    if not (
        periods
        > actual_cutoff
    ).all():
        raise RuntimeError(
            "Cash Flow forecast contains a period "
            "inside the ACTUAL range."
        )

    numeric_columns = [
        "predicted_operating_cash_flow",
        "ocf_lower_bound",
        "ocf_upper_bound",
        "predicted_closing_cash",
        "cash_lower_bound",
        "cash_upper_bound",
    ]

    if output[
        numeric_columns
    ].isna().any().any():
        raise RuntimeError(
            "Cash Flow output contains NaN values."
        )

    if not np.isfinite(
        output[
            numeric_columns
        ].to_numpy()
    ).all():
        raise RuntimeError(
            "Cash Flow output contains non-finite values."
        )

    # Interval checks.
    if (
        output["ocf_lower_bound"]
        >
        output["ocf_upper_bound"]
    ).any():
        raise RuntimeError(
            "Invalid OCF prediction interval."
        )

    if (
        output["cash_lower_bound"]
        >
        output["cash_upper_bound"]
    ).any():
        raise RuntimeError(
            "Invalid cash prediction interval."
        )

    # Cash continuity.
    last_actual_cash = float(
        history.loc[
            history["period"]
            == actual_cutoff,
            "closing_cash",
        ].iloc[0]
    )

    expected_cash = (
        last_actual_cash
        + output[
            "predicted_operating_cash_flow"
        ].cumsum()
    )

    if not np.allclose(
        expected_cash.to_numpy(),
        output[
            "predicted_closing_cash"
        ].to_numpy(),
        rtol=1e-9,
        atol=1e-6,
    ):
        raise RuntimeError(
            "Closing Cash reconciliation failed."
        )

    logger.info(
        "Cash Flow forecast output validation passed."
    )


# ============================================================
# SAVE
# ============================================================

def save_output(
    df: pd.DataFrame,
) -> None:
    """Save Cash Flow Prediction dataset."""

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
    """Run the EFAP Cash Flow Prediction pipeline."""

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

        expense_prediction = (
            load_expense_forecast()
        )

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        metrics = (
            validate_ocf_model(
                history
            )
        )

        # ----------------------------------------------------
        # TRAIN FINAL MODEL
        # ----------------------------------------------------

        X, y = (
            prepare_training_data(
                history
            )
        )

        logger.info(
            "Training final Cash Flow model on %s observations.",
            len(X),
        )

        model = create_model()

        model.fit(
            X,
            y,
        )

        # ----------------------------------------------------
        # LATEST FINANCIAL CONTEXT
        # ----------------------------------------------------

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
            latest["revenue"],
        )

        logger.info(
            "Operating Costs: %.2f",
            latest["operating_costs"],
        )

        logger.info(
            "Operating Cash Flow: %.2f",
            latest["operating_cash_flow"],
        )

        logger.info(
            "Closing Cash: %.2f",
            latest["closing_cash"],
        )

        # ----------------------------------------------------
        # FORECAST
        # ----------------------------------------------------

        (
            ocf_forecast,
            baseline_ratio,
        ) = recursive_ocf_prediction(
            history=history,
            model=model,
            revenue_prediction=revenue_prediction,
            expense_prediction=expense_prediction,
        )

        logger.info(
            "Cash conversion baseline: %.4f",
            baseline_ratio,
        )

        # ----------------------------------------------------
        # BUILD OUTPUT
        # ----------------------------------------------------

        output = build_output(
            history=history,
            ocf_forecast=ocf_forecast,
            metrics=metrics,
        )

        # ----------------------------------------------------
        # VALIDATE OUTPUT
        # ----------------------------------------------------

        validate_forecast_output(
            output=output,
            history=history,
        )

        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        save_output(
            output
        )

        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        logger.info(
            "Generated %s Cash Flow prediction months.",
            len(output),
        )

        logger.info(
            "Forecast period: %s -> %s",
            output["period"].min().strftime(
                "%Y-%m"
            ),
            output["period"].max().strftime(
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