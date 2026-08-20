"""
EFAP - Revenue Prediction

Object:
    Python/forecasting/revenue_prediction.py

Purpose:
    Predict monthly Revenue using supervised machine learning.

Input:
    data/processed/controller_kpi_timeseries.csv

Model:
    HistGradientBoostingRegressor

Features:
    - month
    - quarter
    - seasonal sin/cos
    - revenue lags
    - rolling revenue
    - EBITDA lag
    - net profit lag
    - working capital lag

Process:
    1. Time-ordered train/test split
    2. Model validation
    3. Refit on complete history
    4. Recursive 6-month prediction

Output:
    data/predictions/revenue_prediction.csv

Important:
    This is a predictive ML layer.
    It does not replace the existing Revenue Forecast.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

try:
    from sklearn.ensemble import HistGradientBoostingRegressor
except ImportError as exc:
    raise ImportError(
        "Missing dependency 'scikit-learn'. "
        "Install with: pip install scikit-learn"
    ) from exc

from sklearn.metrics import mean_absolute_error, mean_squared_error


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = (
    Path(__file__).resolve().parents[3]
)

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "controller_kpi_timeseries.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "predictions"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "revenue_prediction.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

HORIZON = 6
VALIDATION_MONTHS = 6
MIN_HISTORY = 24

RANDOM_STATE = 42


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
    """Load canonical EFAP time-series dataset."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    df = pd.read_csv(
        INPUT_FILE
    )

    required = {
        "period",
        "revenue",
        "ebitda",
        "net_profit",
        "net_working_capital",
    }

    missing = (
        required
        - set(df.columns)
    )

    if missing:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(
                sorted(missing)
            )
        )

    df["period"] = pd.to_datetime(
        df["period"],
        errors="coerce",
    )

    numeric_columns = [
        "revenue",
        "ebitda",
        "net_profit",
        "net_working_capital",
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
                "ebitda",
                "net_profit",
                "net_working_capital",
            ]
        ]
        .dropna(subset=["period"])
        .sort_values("period")
        .drop_duplicates("period")
        .reset_index(drop=True)
    )

    if len(df) < MIN_HISTORY:
        raise ValueError(
            f"At least {MIN_HISTORY} monthly observations "
            f"are required. Found {len(df)}."
        )

    # Ensure monthly frequency.
    df = (
        df
        .set_index("period")
        .asfreq("MS")
    )

    return df.reset_index()


# ============================================================
# FEATURE ENGINEERING
# ============================================================

def create_features(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Create lagged and seasonal features."""

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
    # Revenue history
    # --------------------------------------------------------

    result["revenue_lag_1"] = (
        result["revenue"].shift(1)
    )

    result["revenue_lag_2"] = (
        result["revenue"].shift(2)
    )

    result["revenue_lag_3"] = (
        result["revenue"].shift(3)
    )

    result["revenue_lag_6"] = (
        result["revenue"].shift(6)
    )

    result["revenue_lag_12"] = (
        result["revenue"].shift(12)
    )

    result["revenue_rolling_3"] = (
        result["revenue"]
        .shift(1)
        .rolling(
            3,
            min_periods=3,
        )
        .mean()
    )

    result["revenue_rolling_6"] = (
        result["revenue"]
        .shift(1)
        .rolling(
            6,
            min_periods=6,
        )
        .mean()
    )

    result["revenue_rolling_12"] = (
        result["revenue"]
        .shift(1)
        .rolling(
            12,
            min_periods=12,
        )
        .mean()
    )

    # --------------------------------------------------------
    # Financial context
    # --------------------------------------------------------

    result["ebitda_lag_1"] = (
        result["ebitda"].shift(1)
    )

    result["ebitda_lag_3"] = (
        result["ebitda"].shift(3)
    )

    result["net_profit_lag_1"] = (
        result["net_profit"].shift(1)
    )

    result["nwc_lag_1"] = (
        result["net_working_capital"].shift(1)
    )

    return result


FEATURE_COLUMNS = [
    "month",
    "quarter",
    "month_sin",
    "month_cos",
    "time_index",

    "revenue_lag_1",
    "revenue_lag_2",
    "revenue_lag_3",
    "revenue_lag_6",
    "revenue_lag_12",

    "revenue_rolling_3",
    "revenue_rolling_6",
    "revenue_rolling_12",

    "ebitda_lag_1",
    "ebitda_lag_3",
    "net_profit_lag_1",
    "nwc_lag_1",
]


# ============================================================
# MODEL
# ============================================================

def create_model() -> HistGradientBoostingRegressor:
    """Create ML prediction model."""

    return HistGradientBoostingRegressor(
        learning_rate=0.05,
        max_iter=300,
        max_leaf_nodes=15,
        l2_regularization=1.0,
        random_state=RANDOM_STATE,
    )


# ============================================================
# PREPARE TRAINING DATA
# ============================================================

def prepare_training_data(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series]:
    """Prepare supervised learning dataset."""

    features = create_features(
        df
    )

    training = features.dropna(
        subset=FEATURE_COLUMNS + ["revenue"]
    ).copy()

    if training.empty:
        raise ValueError(
            "No valid observations available "
            "after feature engineering."
        )

    X = training[
        FEATURE_COLUMNS
    ]

    y = training[
        "revenue"
    ]

    return X, y


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

def split_train_test(
    X: pd.DataFrame,
    y: pd.Series,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.Series,
    pd.Series,
]:
    """Create time-ordered validation split."""

    if len(X) <= VALIDATION_MONTHS:
        raise ValueError(
            "Not enough observations for validation."
        )

    split_index = (
        len(X)
        - VALIDATION_MONTHS
    )

    X_train = X.iloc[
        :split_index
    ]

    X_test = X.iloc[
        split_index:
    ]

    y_train = y.iloc[
        :split_index
    ]

    y_test = y.iloc[
        split_index:
    ]

    return (
        X_train,
        X_test,
        y_train,
        y_test,
    )


# ============================================================
# METRICS
# ============================================================

def calculate_metrics(
    actual: np.ndarray,
    predicted: np.ndarray,
) -> dict[str, float]:
    """Calculate validation metrics."""

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

    non_zero = actual != 0

    if np.any(non_zero):
        mape = (
            np.mean(
                np.abs(
                    (
                        actual[non_zero]
                        - predicted[non_zero]
                    )
                    / actual[non_zero]
                )
            )
            * 100
        )
    else:
        mape = np.nan

    return {
        "mae": float(mae),
        "rmse": float(rmse),
        "mape_pct": float(mape),
    }


# ============================================================
# VALIDATION
# ============================================================

def validate_model(
    df: pd.DataFrame,
) -> dict[str, float]:
    """Validate model using latest historical months."""

    X, y = prepare_training_data(
        df
    )

    (
        X_train,
        X_test,
        y_train,
        y_test,
    ) = split_train_test(
        X,
        y,
    )

    model = create_model()

    model.fit(
        X_train,
        y_train,
    )

    prediction = model.predict(
        X_test
    )

    metrics = calculate_metrics(
        y_test.to_numpy(),
        prediction,
    )

    logger.info(
        "Revenue Prediction validation:"
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
        "MAPE: %.2f%%",
        metrics["mape_pct"],
    )

    return metrics


# ============================================================
# RECURSIVE FUTURE PREDICTION
# ============================================================

def recursive_predict(
    df: pd.DataFrame,
    model: HistGradientBoostingRegressor,
    horizon: int,
) -> pd.DataFrame:
    """
    Generate recursive future predictions.

    Each predicted month becomes an input for later lag features.
    """

    history = df[
        [
            "period",
            "revenue",
            "ebitda",
            "net_profit",
            "net_working_capital",
        ]
    ].copy()

    predictions = []

    for _ in range(horizon):

        next_period = (
            history["period"].max()
            + pd.offsets.MonthBegin(1)
        )

        temp = pd.concat(
            [
                history,
                pd.DataFrame(
                    {
                        "period": [
                            next_period
                        ],
                        "revenue": [
                            np.nan
                        ],
                        "ebitda": [
                            np.nan
                        ],
                        "net_profit": [
                            np.nan
                        ],
                        "net_working_capital": [
                            np.nan
                        ],
                    }
                ),
            ],
            ignore_index=True,
        )

        engineered = create_features(
            temp
        )

        current_row = engineered.iloc[
            [-1]
        ].copy()

        # For future periods we do not know future EBITDA,
        # net profit or NWC. Their lag values remain based on
        # known history/predictions.
        X_next = current_row[
            FEATURE_COLUMNS
        ]

        # Missing future contextual values are replaced with
        # the latest available values.
        X_next = X_next.ffill(
            axis=0
        )

        X_next = X_next.fillna(
            0
        )

        prediction = float(
            model.predict(
                X_next
            )[0]
        )

        # Revenue cannot be negative in this model.
        prediction = max(
            prediction,
            0.0,
        )

        predictions.append(
            {
                "period": next_period,
                "predicted_revenue": prediction,
            }
        )

        history = pd.concat(
            [
                history,
                pd.DataFrame(
                    {
                        "period": [
                            next_period
                        ],
                        "revenue": [
                            prediction
                        ],
                        "ebitda": [
                            np.nan
                        ],
                        "net_profit": [
                            np.nan
                        ],
                        "net_working_capital": [
                            np.nan
                        ],
                    }
                ),
            ],
            ignore_index=True,
        )

    return pd.DataFrame(
        predictions
    )


# ============================================================
# OUTPUT
# ============================================================

def build_output(
    forecast: pd.DataFrame,
    metrics: dict[str, float],
) -> pd.DataFrame:
    """Build prediction output dataset."""

    rmse = metrics[
        "rmse"
    ]

    result = forecast.copy()

    result["lower_bound"] = np.maximum(
        result["predicted_revenue"]
        - 1.96 * rmse,
        0,
    )

    result["upper_bound"] = (
        result["predicted_revenue"]
        + 1.96 * rmse
    )

    result["model"] = (
        "HistGradientBoosting"
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

            "predicted_revenue",
            "lower_bound",
            "upper_bound",

            "model",
            "validation_mae",
            "validation_rmse",
            "validation_mape_pct",

            "prediction_type",
        ]
    ]


def save_output(
    df: pd.DataFrame,
) -> None:
    """Save Revenue Prediction dataset."""

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    logger.info(
        "Revenue prediction saved to %s",
        OUTPUT_FILE,
    )


# ============================================================
# MAIN
# ============================================================

def main() -> int:
    """Run Revenue Prediction pipeline."""

    try:

        logger.info(
            "Starting EFAP Revenue Prediction."
        )

        df = load_data()

        metrics = validate_model(
            df
        )

        X, y = prepare_training_data(
            df
        )

        model = create_model()

        model.fit(
            X,
            y,
        )

        forecast = recursive_predict(
            df=df,
            model=model,
            horizon=HORIZON,
        )

        output = build_output(
            forecast,
            metrics,
        )

        save_output(
            output
        )

        logger.info(
            "Generated %s Revenue prediction months.",
            len(output),
        )

        logger.info(
            "Revenue Prediction completed successfully."
        )

        return 0

    except Exception as exc:

        logger.exception(
            "Revenue Prediction failed: %s",
            exc,
        )

        return 1


if __name__ == "__main__":
    sys.exit(main())