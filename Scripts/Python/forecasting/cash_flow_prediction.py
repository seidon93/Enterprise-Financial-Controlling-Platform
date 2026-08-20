"""
EFAP - Cash Flow Prediction

Object:
    Python/models/cash_flow_prediction.py

Purpose:
    Predict future Operating Cash Flow and Closing Cash.

Sources:
    data/processed/controller_kpi_timeseries.csv
    data/predictions/revenue_prediction.csv
    data/predictions/expense_prediction.csv

Model:
    HistGradientBoostingRegressor

Targets:
    Operating Cash Flow
    Closing Cash

Forecast horizon:
    6 months

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

EXPENSE_PREDICTION_FILE: Final[Path] = (
    PROJECT_ROOT
    / "data"
    / "predictions"
    / "expense_prediction.csv"
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
        "expense prediction": EXPENSE_PREDICTION_FILE,
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
# LOAD HISTORICAL DATA
# ============================================================

def load_historical_data() -> pd.DataFrame:
    """Load historical controller KPI time series."""

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

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            "Historical data is missing columns: "
            + ", ".join(sorted(missing))
        )

    df["period"] = pd.to_datetime(
        df["period"],
        errors="coerce",
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
        .dropna(subset=["period"])
        .sort_values("period")
        .drop_duplicates("period")
        .reset_index(drop=True)
    )

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

    return df


# ============================================================
# LOAD REVENUE PREDICTION
# ============================================================

def load_revenue_prediction() -> pd.DataFrame:
    """Load ML revenue predictions."""

    df = pd.read_csv(
        REVENUE_PREDICTION_FILE
    )

    required = {
        "period",
        "predicted_revenue",
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            "Revenue prediction is missing columns: "
            + ", ".join(sorted(missing))
        )

    df["period"] = pd.to_datetime(
        df["period"],
        errors="coerce",
    )

    df["predicted_revenue"] = pd.to_numeric(
        df["predicted_revenue"],
        errors="coerce",
    )

    return (
        df[
            [
                "period",
                "predicted_revenue",
            ]
        ]
        .dropna(subset=["period"])
        .sort_values("period")
        .drop_duplicates("period")
        .reset_index(drop=True)
    )


# ============================================================
# LOAD EXPENSE PREDICTION
# ============================================================

def load_expense_prediction() -> pd.DataFrame:
    """
    Load account-level ML expense predictions and aggregate
    them to monthly expense magnitude.
    """

    df = pd.read_csv(
        EXPENSE_PREDICTION_FILE
    )

    required = {
        "period",
        "account_number",
        "predicted_expense",
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            "Expense prediction is missing columns: "
            + ", ".join(sorted(missing))
        )

    df["period"] = pd.to_datetime(
        df["period"],
        errors="coerce",
    )

    df["predicted_expense"] = pd.to_numeric(
        df["predicted_expense"],
        errors="coerce",
    )

    df = df.dropna(
        subset=["period"]
    )

    monthly = (
        df
        .groupby(
            "period",
            as_index=False,
        )["predicted_expense"]
        .sum()
    )

    return monthly.sort_values(
        "period"
    ).reset_index(drop=True)


# ============================================================
# FEATURE ENGINEERING
# ============================================================

def create_cash_flow_features(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create features for Operating Cash Flow prediction.

    Historical target:
        operating_cash_flow

    Closing cash is predicted separately.
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
    # Revenue
    # --------------------------------------------------------

    result["revenue_lag_1"] = (
        result["revenue"].shift(1)
    )

    result["revenue_lag_3"] = (
        result["revenue"].shift(3)
    )

    result["revenue_lag_12"] = (
        result["revenue"].shift(12)
    )

    # --------------------------------------------------------
    # Operating costs
    # --------------------------------------------------------

    result["operating_costs_lag_1"] = (
        result["operating_costs"].shift(1)
    )

    result["operating_costs_lag_3"] = (
        result["operating_costs"].shift(3)
    )

    # --------------------------------------------------------
    # Profit
    # --------------------------------------------------------

    result["net_profit_lag_1"] = (
        result["net_profit"].shift(1)
    )

    result["net_profit_lag_3"] = (
        result["net_profit"].shift(3)
    )

    # --------------------------------------------------------
    # Working Capital
    # --------------------------------------------------------

    result["nwc_lag_1"] = (
        result["net_working_capital"].shift(1)
    )

    result["nwc_lag_3"] = (
        result["net_working_capital"].shift(3)
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
        result["closing_cash"].shift(1)
    )

    result["cash_lag_3"] = (
        result["closing_cash"].shift(3)
    )

    result["cash_lag_12"] = (
        result["closing_cash"].shift(12)
    )

    # --------------------------------------------------------
    # Operating Cash Flow
    # --------------------------------------------------------

    result["ocf_lag_1"] = (
        result["operating_cash_flow"].shift(1)
    )

    result["ocf_lag_3"] = (
        result["operating_cash_flow"].shift(3)
    )

    result["ocf_lag_12"] = (
        result["operating_cash_flow"].shift(12)
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

    # --------------------------------------------------------
    # Cash change
    # --------------------------------------------------------

    result["cash_change_lag_1"] = (
        result["closing_cash"]
        .diff()
        .shift(1)
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

    "cash_change_lag_1",
]


# ============================================================
# MODEL
# ============================================================

def create_model() -> HistGradientBoostingRegressor:
    """Create Cash Flow prediction model."""

    return HistGradientBoostingRegressor(
        learning_rate=0.05,
        max_iter=350,
        max_leaf_nodes=15,
        l2_regularization=1.0,
        random_state=RANDOM_STATE,
    )


# ============================================================
# METRICS
# ============================================================

def calculate_metrics(
    actual: np.ndarray,
    predicted: np.ndarray,
) -> dict[str, float]:
    """Calculate prediction metrics."""

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
                    / np.abs(
                        actual[non_zero]
                    )
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
# PREPARE TRAINING DATA
# ============================================================

def prepare_training_data(
    history: pd.DataFrame,
) -> tuple[
    pd.DataFrame,
    pd.Series,
]:
    """Prepare supervised OCF dataset."""

    features = create_cash_flow_features(
        history
    )

    training = features.dropna(
        subset=FEATURE_COLUMNS
        + [
            "operating_cash_flow"
        ]
    ).copy()

    if training.empty:
        raise ValueError(
            "No valid OCF training observations."
        )

    return (
        training[FEATURE_COLUMNS],
        training["operating_cash_flow"],
    )


# ============================================================
# VALIDATION
# ============================================================

def validate_ocf_model(
    history: pd.DataFrame,
) -> dict[str, float]:
    """Time-ordered validation of OCF model."""

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

    prediction = model.predict(
        X_test
    )

    metrics = calculate_metrics(
        y_test.to_numpy(),
        prediction,
    )

    logger.info(
        "Operating CF validation | "
        "MAE %.2f | RMSE %.2f | MAPE %.2f%%",
        metrics["mae"],
        metrics["rmse"],
        metrics["mape_pct"],
    )

    return metrics


# ============================================================
# FUTURE FEATURE DATASET
# ============================================================

def prepare_future_history(
    history: pd.DataFrame,
    revenue_prediction: pd.DataFrame,
    expense_prediction: pd.DataFrame,
) -> pd.DataFrame:
    """
    Extend historical data with future revenue and expense
    predictions.

    Future OCF and cash remain unknown and are generated
    recursively.
    """

    future_periods = sorted(
        set(
            revenue_prediction["period"]
        )
        & set(
            expense_prediction["period"]
        )
    )

    if not future_periods:
        raise ValueError(
            "No overlapping Revenue and Expense "
            "prediction periods found."
        )

    future = pd.DataFrame(
        {
            "period": future_periods,
        }
    )

    revenue = revenue_prediction[
        [
            "period",
            "predicted_revenue",
        ]
    ].rename(
        columns={
            "predicted_revenue":
                "revenue"
        }
    )

    expenses = expense_prediction[
        [
            "period",
            "predicted_expense",
        ]
    ].rename(
        columns={
            "predicted_expense":
                "operating_expense_magnitude"
        }
    )

    future = (
        future
        .merge(
            revenue,
            on="period",
            how="left",
        )
        .merge(
            expenses,
            on="period",
            how="left",
        )
    )

    # Operating costs in SQL are negative.
    future["operating_costs"] = (
        -future[
            "operating_expense_magnitude"
        ]
    )

    # Unknown future variables.
    future["net_profit"] = np.nan
    future["net_working_capital"] = np.nan
    future["operating_cash_flow"] = np.nan
    future["closing_cash"] = np.nan

    required_columns = [
        "revenue",
        "operating_costs",
        "net_profit",
        "net_working_capital",
        "operating_cash_flow",
        "closing_cash",
    ]

    future = future[
        [
            "period",
            *required_columns,
        ]
    ]

    return future


# ============================================================
# RECURSIVE OCF PREDICTION
# ============================================================

def recursive_ocf_prediction(
    history: pd.DataFrame,
    model: HistGradientBoostingRegressor,
    revenue_prediction: pd.DataFrame,
    expense_prediction: pd.DataFrame,
) -> pd.DataFrame:
    """
    Predict future Operating Cash Flow recursively.

    Unknown future context fields are carried using the latest
    available values. This is deliberately conservative and
    transparent until dedicated Working Capital Prediction is
    implemented.
    """

    working = history.copy()

    future = prepare_future_history(
        history=history,
        revenue_prediction=revenue_prediction,
        expense_prediction=expense_prediction,
    )

    predictions = []

    for _, future_row in future.iterrows():

        period = future_row["period"]

        row = future_row.to_dict()

        # ----------------------------------------------------
        # Context values not yet separately forecast:
        #
        # Carry forward latest known values.
        # ----------------------------------------------------

        for column in [
            "net_profit",
            "net_working_capital",
        ]:

            row[column] = float(
                working[column]
                .dropna()
                .iloc[-1]
            )

        row["operating_cash_flow"] = np.nan

        # Closing cash is carried forward from latest known
        # cash before the new OCF is calculated.
        row["closing_cash"] = float(
            working["closing_cash"]
            .dropna()
            .iloc[-1]
        )

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
            create_cash_flow_features(
                working
            )
        )

        current = engineered.iloc[
            [-1]
        ][FEATURE_COLUMNS]

        current = (
            current
            .ffill(
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

        working.loc[
            working["period"] == period,
            "operating_cash_flow",
        ] = prediction

        # ----------------------------------------------------
        # Closing cash = prior closing cash + OCF
        #
        # Until separate investing/financing CF prediction
        # is implemented, we explicitly keep those components
        # at zero here rather than inventing values.
        # ----------------------------------------------------

        previous_cash = float(
            working.loc[
                working["period"] < period,
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
            working["period"] == period,
            "closing_cash",
        ] = predicted_cash

    return pd.DataFrame(
        predictions
    )


# ============================================================
# BUILD FINAL OUTPUT
# ============================================================

def build_output(
    history: pd.DataFrame,
    ocf_forecast: pd.DataFrame,
    metrics: dict[str, float],
) -> pd.DataFrame:
    """Build cash flow prediction output."""

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

    rmse = metrics["rmse"]

    outputs = []

    running_cash = actual_cash

    for _, row in ocf_forecast.iterrows():

        operating_cf = float(
            row[
                "predicted_operating_cash_flow"
            ]
        )

        running_cash += operating_cf

        outputs.append(
            {
                "period": row["period"],
                "predicted_operating_cash_flow":
                    operating_cf,
                "predicted_closing_cash":
                    running_cash,
                "ocf_lower_bound":
                    operating_cf
                    - 1.96 * rmse,
                "ocf_upper_bound":
                    operating_cf
                    + 1.96 * rmse,
                "cash_lower_bound":
                    running_cash
                    - 1.96 * rmse,
                "cash_upper_bound":
                    running_cash
                    + 1.96 * rmse,
            }
        )

    result = pd.DataFrame(
        outputs
    )

    result["predicted_closing_cash"] = (
        result[
            "predicted_closing_cash"
        ].astype(float)
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
    """Run Cash Flow Prediction pipeline."""

    try:

        logger.info(
            "Starting EFAP Cash Flow Prediction."
        )

        validate_files()

        history = load_historical_data()

        revenue_prediction = (
            load_revenue_prediction()
        )

        expense_prediction = (
            load_expense_prediction()
        )

        metrics = validate_ocf_model(
            history
        )

        X, y = prepare_training_data(
            history
        )

        model = create_model()

        model.fit(
            X,
            y,
        )

        ocf_forecast = (
            recursive_ocf_prediction(
                history=history,
                model=model,
                revenue_prediction=revenue_prediction,
                expense_prediction=expense_prediction,
            )
        )

        output = build_output(
            history=history,
            ocf_forecast=ocf_forecast,
            metrics=metrics,
        )

        save_output(
            output
        )

        logger.info(
            "Generated %s Cash Flow prediction months.",
            len(output),
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


if __name__ == "__main__":
    sys.exit(main())