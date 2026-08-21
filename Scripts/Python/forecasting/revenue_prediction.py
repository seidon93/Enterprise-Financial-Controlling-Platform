"""
EFAP - Revenue Prediction

Object:
    Scripts/Python/forecasting/revenue_prediction.py

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
    - time index
    - revenue lags
    - rolling revenue
    - EBITDA lag
    - net profit lag
    - working capital lag

Process:
    1. Load canonical controller data
    2. Normalize Revenue to management sign convention
    3. Create time-series features
    4. Time-ordered train/test validation
    5. Refit model on complete historical dataset
    6. Recursive 6-month prediction
    7. Validate forecast output
    8. Export Power BI-ready prediction dataset

Management sign convention:
    Revenue              positive
    Operating Costs      negative
    EBITDA               signed
    EBIT                 signed
    Net Profit           signed
    Cash Flow            signed

Important:
    The canonical controller dataset may use an accounting
    sign convention where Revenue is negative.

    The ML layer deliberately normalizes Revenue before
    feature engineering so that:
        Revenue >= 0

    This ensures that:
        - revenue lags
        - rolling revenue
        - recursive predictions
        - prediction intervals

    all use the same management convention.

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

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
)


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
    """
    Load canonical EFAP controller time series.

    The canonical controller dataset may use accounting
    sign convention where Revenue is negative.

    The ML layer normalizes Revenue to positive management
    convention before any feature engineering takes place.
    """

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    logger.info(
        "Loading Revenue Prediction input: %s",
        INPUT_FILE,
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

    # --------------------------------------------------------
    # PERIOD
    # --------------------------------------------------------

    df["period"] = pd.to_datetime(
        df["period"],
        errors="coerce",
    )

    # --------------------------------------------------------
    # NUMERIC COLUMNS
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # BASIC CLEANUP
    # --------------------------------------------------------

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
        .dropna(
            subset=[
                "period"
            ]
        )
        .sort_values(
            "period"
        )
        .drop_duplicates(
            "period"
        )
        .reset_index(
            drop=True
        )
    )

    if df.empty:

        raise ValueError(
            "Revenue Prediction input contains no valid "
            "monthly observations."
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

    if len(df) < MIN_HISTORY:

        raise ValueError(
            f"At least {MIN_HISTORY} monthly observations "
            f"are required. Found {len(df)}."
        )

    # --------------------------------------------------------
    # MANAGEMENT SIGN NORMALIZATION
    # --------------------------------------------------------
    #
    # Canonical controller source:
    #
    #     Revenue may be negative.
    #
    # ML management convention:
    #
    #     Revenue >= 0
    #
    # We normalize BEFORE feature engineering.
    #
    # This is critical because the following features depend
    # on Revenue:
    #
    #     revenue_lag_1
    #     revenue_lag_2
    #     revenue_lag_3
    #     revenue_lag_6
    #     revenue_lag_12
    #     revenue_rolling_3
    #     revenue_rolling_6
    #     revenue_rolling_12
    #
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

    # --------------------------------------------------------
    # POST-NORMALIZATION VALIDATION
    # --------------------------------------------------------

    if (
        df["revenue"]
        < 0
    ).any():

        raise RuntimeError(
            "Revenue management normalization failed. "
            "Negative Revenue values remain after abs()."
        )

    logger.info(
        "Revenue sign normalized to management convention: "
        "Revenue >= 0."
    )

    # --------------------------------------------------------
    # MONTHLY FREQUENCY
    # --------------------------------------------------------

    df = (
        df
        .set_index(
            "period"
        )
        .asfreq(
            "MS"
        )
    )

    # --------------------------------------------------------
    # DEFENSIVE VALIDATION AFTER FREQUENCY ALIGNMENT
    # --------------------------------------------------------

    missing_months = int(
        df["revenue"]
        .isna()
        .sum()
    )

    if missing_months > 0:

        raise ValueError(
            "Revenue Prediction input contains missing "
            f"monthly observations after monthly frequency "
            f"alignment: {missing_months} month(s)."
        )

    return (
        df
        .reset_index()
    )


# ============================================================
# FEATURE ENGINEERING
# ============================================================

def create_features(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create lagged and seasonal features.

    Revenue is already normalized to the positive management
    convention by load_data().
    """

    result = df.copy()

    # --------------------------------------------------------
    # CALENDAR FEATURES
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
    # REVENUE HISTORY
    # --------------------------------------------------------

    result["revenue_lag_1"] = (
        result["revenue"]
        .shift(1)
    )

    result["revenue_lag_2"] = (
        result["revenue"]
        .shift(2)
    )

    result["revenue_lag_3"] = (
        result["revenue"]
        .shift(3)
    )

    result["revenue_lag_6"] = (
        result["revenue"]
        .shift(6)
    )

    result["revenue_lag_12"] = (
        result["revenue"]
        .shift(12)
    )

    # --------------------------------------------------------
    # ROLLING REVENUE
    # --------------------------------------------------------
    #
    # shift(1) is intentional:
    #
    # the current month's Revenue must not be included when
    # constructing a feature used to predict that same month.
    #
    # --------------------------------------------------------

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
    # FINANCIAL CONTEXT
    # --------------------------------------------------------

    result["ebitda_lag_1"] = (
        result["ebitda"]
        .shift(1)
    )

    result["ebitda_lag_3"] = (
        result["ebitda"]
        .shift(3)
    )

    result["net_profit_lag_1"] = (
        result["net_profit"]
        .shift(1)
    )

    result["nwc_lag_1"] = (
        result["net_working_capital"]
        .shift(1)
    )

    return result


# ============================================================
# FEATURES USED BY THE MODEL
# ============================================================

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
    """Create the Revenue ML model."""

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
    """Prepare the supervised learning dataset."""

    features = create_features(
        df
    )

    training = (
        features
        .dropna(
            subset=(
                FEATURE_COLUMNS
                + [
                    "revenue"
                ]
            )
        )
        .copy()
    )

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

    # --------------------------------------------------------
    # TARGET VALIDATION
    # --------------------------------------------------------

    if (
        y < 0
    ).any():

        raise RuntimeError(
            "Training Revenue target contains negative values. "
            "Management sign normalization is inconsistent."
        )

    if (
        y.isna()
    ).any():

        raise RuntimeError(
            "Training Revenue target contains NaN values."
        )

    return (
        X,
        y,
    )


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
    """Create a time-ordered validation split."""

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

    if np.any(
        non_zero
    ):

        mape = (
            np.mean(
                np.abs(
                    (
                        actual[
                            non_zero
                        ]
                        -
                        predicted[
                            non_zero
                        ]
                    )
                    /
                    actual[
                        non_zero
                    ]
                )
            )
            * 100
        )

    else:

        mape = np.nan

    return {
        "mae": float(
            mae
        ),
        "rmse": float(
            rmse
        ),
        "mape_pct": float(
            mape
        ),
    }


# ============================================================
# VALIDATION
# ============================================================

def validate_model(
    df: pd.DataFrame,
) -> dict[str, float]:
    """Validate the model using the latest historical months."""

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

    logger.info(
        "Training validation Revenue model on %s observations.",
        len(X_train),
    )

    model.fit(
        X_train,
        y_train,
    )

    prediction = model.predict(
        X_test
    )

    # --------------------------------------------------------
    # VALIDATION PREDICTION CHECK
    # --------------------------------------------------------

    if np.any(
        prediction < 0
    ):

        logger.warning(
            "Validation model produced %s negative "
            "Revenue predictions.",
            int(
                np.sum(
                    prediction < 0
                )
            ),
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
    Generate recursive future Revenue predictions.

    Each predicted month becomes available as Revenue history
    for later months.

    Future EBITDA, Net Profit and NWC are unknown. Their
    lagged context therefore uses the latest known financial
    context available at the time of prediction.
    """

    history = (
        df[
            [
                "period",
                "revenue",
                "ebitda",
                "net_profit",
                "net_working_capital",
            ]
        ]
        .copy()
    )

    predictions = []

    latest_ebitda = (
        history[
            "ebitda"
        ]
        .dropna()
        .iloc[-1]
    )

    latest_net_profit = (
        history[
            "net_profit"
        ]
        .dropna()
        .iloc[-1]
    )

    latest_nwc = (
        history[
            "net_working_capital"
        ]
        .dropna()
        .iloc[-1]
    )

    logger.info(
        "Latest actual financial context:"
    )

    logger.info(
        "EBITDA: %.2f",
        latest_ebitda,
    )

    logger.info(
        "Net Profit: %.2f",
        latest_net_profit,
    )

    logger.info(
        "Net Working Capital: %.2f",
        latest_nwc,
    )

    # --------------------------------------------------------
    # RECURSIVE LOOP
    # --------------------------------------------------------

    for step in range(
        1,
        horizon + 1,
    ):

        next_period = (
            history[
                "period"
            ].max()
            +
            pd.offsets.MonthBegin(
                1
            )
        )

        # ----------------------------------------------------
        # Add future placeholder row.
        #
        # Revenue is unknown and will be predicted.
        # Financial context variables remain unknown.
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # Feature engineering
        # ----------------------------------------------------

        engineered = create_features(
            temp
        )

        current_row = (
            engineered
            .iloc[
                [-1]
            ]
            .copy()
        )

        # ----------------------------------------------------
        # FUTURE CONTEXT HANDLING
        # ----------------------------------------------------
        #
        # The current row's lag values are based on known
        # history. For additional defensive handling, any
        # remaining missing contextual features are replaced
        # with latest available known values.
        #
        # Revenue rolling features must NOT be replaced with
        # arbitrary values because recursive Revenue history
        # is the actual intended input.
        # ----------------------------------------------------

        contextual_columns = [
            "ebitda_lag_1",
            "ebitda_lag_3",
            "net_profit_lag_1",
            "nwc_lag_1",
        ]

        for column in contextual_columns:

            if (
                pd.isna(
                    current_row.iloc[0][column]
                )
            ):

                if column.startswith(
                    "ebitda"
                ):

                    current_row.loc[
                        current_row.index,
                        column,
                    ] = latest_ebitda

                elif column.startswith(
                    "net_profit"
                ):

                    current_row.loc[
                        current_row.index,
                        column,
                    ] = latest_net_profit

                elif column.startswith(
                    "nwc"
                ):

                    current_row.loc[
                        current_row.index,
                        column,
                    ] = latest_nwc

        # ----------------------------------------------------
        # Validate required feature availability
        # ----------------------------------------------------

        X_next = (
            current_row[
                FEATURE_COLUMNS
            ]
            .copy()
        )

        missing_features = (
            X_next.columns[
                X_next.iloc[0]
                .isna()
            ]
            .tolist()
        )

        if missing_features:

            raise RuntimeError(
                "Recursive Revenue prediction contains "
                "missing model features for "
                f"{next_period.strftime('%Y-%m')}: "
                + ", ".join(
                    missing_features
                )
            )

        # ----------------------------------------------------
        # MODEL PREDICTION
        # ----------------------------------------------------

        prediction = float(
            model.predict(
                X_next
            )[0]
        )

        # ----------------------------------------------------
        # NEGATIVE PREDICTION = HARD ERROR
        # ----------------------------------------------------
        #
        # We intentionally do NOT clip to zero.
        #
        # A negative prediction would indicate an inconsistency
        # between the target convention and the ML model.
        # ----------------------------------------------------

        if prediction < 0:

            raise RuntimeError(
                "Revenue ML model produced a negative "
                "prediction for "
                f"{next_period.strftime('%Y-%m')}: "
                f"{prediction:.2f}. "
                "Revenue target must use positive "
                "management sign convention."
            )

        # ----------------------------------------------------
        # Store prediction
        # ----------------------------------------------------

        predictions.append(
            {
                "period": next_period,
                "predicted_revenue": prediction,
            }
        )

        logger.info(
            "Revenue forecast %s/%s | %s | %.2f",
            step,
            horizon,
            next_period.strftime(
                "%Y-%m"
            ),
            prediction,
        )

        # ----------------------------------------------------
        # Add prediction to recursive history
        # ----------------------------------------------------

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
# FORECAST OUTPUT VALIDATION
# ============================================================

def validate_forecast_output(
    forecast: pd.DataFrame,
    horizon: int,
) -> None:
    """
    Validate the generated Revenue forecast.

    Prevents:
        - negative Revenue
        - duplicate periods
        - missing periods
        - collapsed recursive forecasts
        - missing predictions
    """

    required_columns = {
        "period",
        "predicted_revenue",
    }

    missing = (
        required_columns
        - set(
            forecast.columns
        )
    )

    if missing:

        raise RuntimeError(
            "Revenue forecast is missing columns: "
            + ", ".join(
                sorted(
                    missing
                )
            )
        )

    # --------------------------------------------------------
    # Row count
    # --------------------------------------------------------

    if len(forecast) != horizon:

        raise RuntimeError(
            "Invalid Revenue forecast horizon: "
            f"expected {horizon} rows, "
            f"found {len(forecast)}."
        )

    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------

    if (
        forecast[
            "predicted_revenue"
        ]
        .isna()
        .any()
    ):

        raise RuntimeError(
            "Revenue ML forecast contains missing "
            "predictions."
        )

    # --------------------------------------------------------
    # Negative values
    # --------------------------------------------------------

    if (
        forecast[
            "predicted_revenue"
        ]
        < 0
    ).any():

        raise RuntimeError(
            "Revenue ML forecast contains negative "
            "predictions."
        )

    # --------------------------------------------------------
    # Duplicate periods
    # --------------------------------------------------------

    if (
        forecast[
            "period"
        ]
        .duplicated()
        .any()
    ):

        raise RuntimeError(
            "Revenue ML forecast contains duplicate periods."
        )

    # --------------------------------------------------------
    # Consecutive months
    # --------------------------------------------------------

    periods = (
        forecast[
            "period"
        ]
        .sort_values()
        .reset_index(
            drop=True
        )
    )

    expected_periods = pd.Series(
        pd.date_range(
            start=periods.iloc[0],
            periods=horizon,
            freq="MS",
        )
    )

    if not periods.equals(
        expected_periods
    ):

        raise RuntimeError(
            "Revenue ML forecast periods are not "
            "consecutive monthly periods."
        )

    # --------------------------------------------------------
    # Collapsed forecast detection
    # --------------------------------------------------------
    #
    # A small amount of repetition can be legitimate.
    # Exact collapse to the same prediction across the entire
    # horizon indicates a broken recursive feature path.
    # --------------------------------------------------------

    unique_predictions = (
        forecast[
            "predicted_revenue"
        ]
        .round(6)
        .nunique()
    )

    if (
        unique_predictions
        == 1
        and horizon > 1
    ):

        raise RuntimeError(
            "Revenue ML forecast collapsed to a single "
            "prediction across all forecast months. "
            "This indicates a broken recursive feature path."
        )

    logger.info(
        "Revenue forecast output validation passed."
    )


# ============================================================
# OUTPUT
# ============================================================

def build_output(
    forecast: pd.DataFrame,
    metrics: dict[str, float],
) -> pd.DataFrame:
    """Build the Revenue prediction output dataset."""

    rmse = metrics[
        "rmse"
    ]

    result = (
        forecast
        .copy()
    )

    # --------------------------------------------------------
    # Prediction interval
    # --------------------------------------------------------
    #
    # Revenue is positive.
    #
    # Lower interval cannot be negative.
    #
    # --------------------------------------------------------

    result[
        "lower_bound"
    ] = np.maximum(
        result[
            "predicted_revenue"
        ]
        -
        1.96 * rmse,
        0,
    )

    result[
        "upper_bound"
    ] = (
        result[
            "predicted_revenue"
        ]
        +
        1.96 * rmse
    )

    # --------------------------------------------------------
    # Model metadata
    # --------------------------------------------------------

    result[
        "model"
    ] = (
        "HistGradientBoosting"
    )

    result[
        "validation_mae"
    ] = (
        metrics[
            "mae"
        ]
    )

    result[
        "validation_rmse"
    ] = (
        metrics[
            "rmse"
        ]
    )

    result[
        "validation_mape_pct"
    ] = (
        metrics[
            "mape_pct"
        ]
    )

    result[
        "prediction_type"
    ] = (
        "ML_PREDICTION"
    )

    # --------------------------------------------------------
    # Calendar attributes
    # --------------------------------------------------------

    result[
        "year_month"
    ] = (
        result[
            "period"
        ]
        .dt.strftime(
            "%Y-%m"
        )
    )

    result[
        "forecast_year"
    ] = (
        result[
            "period"
        ]
        .dt.year
    )

    result[
        "forecast_month"
    ] = (
        result[
            "period"
        ]
        .dt.month
    )

    # --------------------------------------------------------
    # Defensive interval validation
    # --------------------------------------------------------

    if (
        result[
            "lower_bound"
        ]
        >
        result[
            "upper_bound"
        ]
    ).any():

        raise RuntimeError(
            "Revenue prediction interval is invalid."
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


# ============================================================
# SAVE OUTPUT
# ============================================================

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
    """Run the Revenue Prediction pipeline."""

    try:

        logger.info(
            "Starting EFAP Revenue Prediction."
        )

        # ----------------------------------------------------
        # LOAD + NORMALIZE
        # ----------------------------------------------------

        df = load_data()

        # ----------------------------------------------------
        # MODEL VALIDATION
        # ----------------------------------------------------

        metrics = validate_model(
            df
        )

        # ----------------------------------------------------
        # FINAL TRAINING DATA
        # ----------------------------------------------------

        X, y = (
            prepare_training_data(
                df
            )
        )

        logger.info(
            "Training final Revenue model on %s observations.",
            len(X),
        )

        model = create_model()

        model.fit(
            X,
            y,
        )

        # ----------------------------------------------------
        # RECURSIVE FORECAST
        # ----------------------------------------------------

        forecast = recursive_predict(
            df=df,
            model=model,
            horizon=HORIZON,
        )

        # ----------------------------------------------------
        # FORECAST VALIDATION
        # ----------------------------------------------------

        validate_forecast_output(
            forecast,
            HORIZON,
        )

        # ----------------------------------------------------
        # BUILD OUTPUT
        # ----------------------------------------------------

        output = build_output(
            forecast,
            metrics,
        )

        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        save_output(
            output
        )

        # ----------------------------------------------------
        # FINAL SUMMARY
        # ----------------------------------------------------

        logger.info(
            "Generated %s Revenue prediction months.",
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
            "Revenue Prediction completed successfully."
        )

        return 0

    except Exception as exc:

        logger.exception(
            "Revenue Prediction failed: %s",
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