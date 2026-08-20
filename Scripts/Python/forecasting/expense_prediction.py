"""
EFAP - Expense Prediction

Object:
    Python/models/expense_prediction.py

Purpose:
    Predict major monthly expense lines using supervised
    machine learning.

Input:
    data/processed/controller_kpi_timeseries.csv

Model:
    HistGradientBoostingRegressor

Expense lines:
    501 Material Consumption
    502 Energy Consumption
    504 Cost of Goods Sold
    511 Repairs & Maintenance
    518 Other Services
    521 Payroll Costs
    524 Social & Health Insurance
    548 Other Operating Costs
    549 Shortages & Damages
    582 Inventory Change

Output:
    data/predictions/expense_prediction.csv

Important:
    This module is a predictive ML layer.
    It does not replace the statistical Expense Forecast.
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Final

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
    from sklearn.ensemble import HistGradientBoostingRegressor
    from sklearn.metrics import (
        mean_absolute_error,
        mean_squared_error,
    )
except ImportError as exc:
    raise ImportError(
        "Missing dependency 'scikit-learn'. "
        "Install with: pip install scikit-learn"
    ) from exc


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT: Final[Path] = (
    Path(__file__).resolve().parents[3]
)

ENV_FILE: Final[Path] = (
    PROJECT_ROOT / ".env"
)

OUTPUT_DIR: Final[Path] = (
    PROJECT_ROOT
    / "data"
    / "predictions"
)

OUTPUT_FILE: Final[Path] = (
    OUTPUT_DIR
    / "expense_prediction.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

HORIZON: Final[int] = 6

VALIDATION_MONTHS: Final[int] = 6

MIN_HISTORY: Final[int] = 24

RANDOM_STATE: Final[int] = 42


# ============================================================
# EXPENSE ACCOUNTS
# ============================================================

EXPENSE_ACCOUNTS: Final[dict[int, str]] = {
    501: "Material Consumption",
    502: "Energy Consumption",
    504: "Cost of Goods Sold",
    511: "Repairs & Maintenance",
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

DB_CONFIG: Final[dict[str, object]] = {
    "host": os.getenv(
        "DB_HOST",
        "localhost",
    ),
    "port": int(
        os.getenv(
            "DB_PORT",
            "5432",
        )
    ),
    "database": os.getenv(
        "DB_NAME",
        "EFAP",
    ),
    "user": os.getenv(
        "DB_USER",
        "",
    ),
    "password": os.getenv(
        "DB_PASSWORD",
        "",
    ),
}


# ============================================================
# SOURCE QUERY
# ============================================================

SOURCE_QUERY: Final[str] = """
SELECT

    p.calendar_year,
    p.calendar_month,
    p.year_month,

    p.account_number,
    p.account_name,

    m.management_group,
    m.management_line,
    m.management_sign,

    p.signed_amount

FROM mart.vw_pnl_monthly p

INNER JOIN mart.dim_pnl_management_mapping m
    ON p.account_number::text
     = m.account_number::text

WHERE
    m.management_group = 'Operating Costs'
    AND m.is_active = TRUE

ORDER BY
    p.calendar_year,
    p.calendar_month,
    p.account_number;
"""


# ============================================================
# DATABASE
# ============================================================

def validate_db_config() -> None:
    """Validate PostgreSQL configuration."""

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

    return psycopg2.connect(
        **DB_CONFIG
    )


# ============================================================
# DATA LOADING
# ============================================================

def load_data() -> pd.DataFrame:
    """Load monthly expense history."""

    connection = None

    try:

        logger.info(
            "Loading expense history from PostgreSQL."
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
    """
    Prepare positive expense consumption values.

    PostgreSQL management amount is negative for costs.
    ML model works with positive expense magnitude.
    """

    df = df.copy()

    required = {
        "year_month",
        "account_number",
        "account_name",
        "management_sign",
        "signed_amount",
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(sorted(missing))
        )

    df["period"] = pd.to_datetime(
        df["year_month"] + "-01",
        errors="coerce",
    )

    df["account_number"] = pd.to_numeric(
        df["account_number"],
        errors="coerce",
    ).astype("Int64")

    df["signed_amount"] = pd.to_numeric(
        df["signed_amount"],
        errors="coerce",
    )

    df["management_sign"] = pd.to_numeric(
        df["management_sign"],
        errors="coerce",
    )

    df["management_amount"] = (
        df["signed_amount"]
        * df["management_sign"]
    )

    # Costs are negative in management presentation.
    # Convert to positive expense magnitude for prediction.
    df["expense_amount"] = (
        -df["management_amount"]
    )

    df = df[
        df["account_number"].isin(
            EXPENSE_ACCOUNTS.keys()
        )
    ].copy()

    return df.dropna(
        subset=[
            "period",
            "expense_amount",
        ]
    )


# ============================================================
# MONTHLY ACCOUNT SERIES
# ============================================================

def create_account_series(
    df: pd.DataFrame,
) -> dict[int, pd.Series]:
    """Create one monthly time series per expense account."""

    result: dict[int, pd.Series] = {}

    for account_number in EXPENSE_ACCOUNTS:

        account_df = df[
            df["account_number"]
            == account_number
        ].copy()

        if account_df.empty:
            logger.warning(
                "No history for account %s.",
                account_number,
            )
            continue

        series = (
            account_df
            .groupby("period")["expense_amount"]
            .sum()
            .sort_index()
            .asfreq("MS")
            .fillna(0)
        )

        if len(series) < MIN_HISTORY:

            logger.warning(
                "Skipping account %s: "
                "only %s monthly observations.",
                account_number,
                len(series),
            )

            continue

        result[account_number] = series

    if not result:
        raise RuntimeError(
            "No expense account has enough history "
            "for ML prediction."
        )

    return result


# ============================================================
# FEATURE ENGINEERING
# ============================================================

def create_features(
    series,
) -> pd.DataFrame:
    """Create supervised ML features for one expense series."""

    if isinstance(series, pd.DataFrame):
        df = series[["period", "expense"]].copy()
        df = df.reset_index(drop=True)
    else:
        df = pd.DataFrame(
            {
                "period": series.index,
                "expense": series.values,
            }
        )

    # --------------------------------------------------------
    # Calendar
    # --------------------------------------------------------

    df["month"] = (
        df["period"].dt.month
    )

    df["quarter"] = (
        df["period"].dt.quarter
    )

    df["month_sin"] = np.sin(
        2
        * np.pi
        * df["month"]
        / 12
    )

    df["month_cos"] = np.cos(
        2
        * np.pi
        * df["month"]
        / 12
    )

    df["time_index"] = np.arange(
        len(df)
    )

    # --------------------------------------------------------
    # Lags
    # --------------------------------------------------------

    df["expense_lag_1"] = (
        df["expense"].shift(1)
    )

    df["expense_lag_2"] = (
        df["expense"].shift(2)
    )

    df["expense_lag_3"] = (
        df["expense"].shift(3)
    )

    df["expense_lag_6"] = (
        df["expense"].shift(6)
    )

    df["expense_lag_12"] = (
        df["expense"].shift(12)
    )

    # --------------------------------------------------------
    # Rolling baselines
    #
    # Shift(1) prevents current observation leakage.
    # --------------------------------------------------------

    df["expense_rolling_3"] = (
        df["expense"]
        .shift(1)
        .rolling(
            3,
            min_periods=3,
        )
        .mean()
    )

    df["expense_rolling_6"] = (
        df["expense"]
        .shift(1)
        .rolling(
            6,
            min_periods=6,
        )
        .mean()
    )

    df["expense_rolling_12"] = (
        df["expense"]
        .shift(1)
        .rolling(
            12,
            min_periods=12,
        )
        .mean()
    )

    return df


FEATURE_COLUMNS: Final[list[str]] = [
    "month",
    "quarter",
    "month_sin",
    "month_cos",
    "time_index",

    "expense_lag_1",
    "expense_lag_2",
    "expense_lag_3",
    "expense_lag_6",
    "expense_lag_12",

    "expense_rolling_3",
    "expense_rolling_6",
    "expense_rolling_12",
]


# ============================================================
# MODEL
# ============================================================

def create_model() -> HistGradientBoostingRegressor:
    """Create expense prediction model."""

    return HistGradientBoostingRegressor(
        learning_rate=0.05,
        max_iter=300,
        max_leaf_nodes=15,
        l2_regularization=1.0,
        random_state=RANDOM_STATE,
    )


# ============================================================
# TRAINING DATA
# ============================================================

def prepare_training_data(
    series: pd.Series,
) -> tuple[
    pd.DataFrame,
    pd.Series,
]:
    """Prepare supervised learning data."""

    features = create_features(
        series
    )

    training = features.dropna(
        subset=FEATURE_COLUMNS + ["expense"]
    ).copy()

    if training.empty:
        raise ValueError(
            "No valid training observations."
        )

    X = training[
        FEATURE_COLUMNS
    ]

    y = training[
        "expense"
    ]

    return X, y


# ============================================================
# METRICS
# ============================================================

def calculate_metrics(
    actual: np.ndarray,
    predicted: np.ndarray,
) -> dict[str, float]:
    """Calculate model validation metrics."""

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

    mask = actual != 0

    if np.any(mask):

        mape = (
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

def validate_account_model(
    series: pd.Series,
) -> dict[str, float]:
    """Validate one expense account."""

    X, y = prepare_training_data(
        series
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

    model = create_model()

    model.fit(
        X_train,
        y_train,
    )

    prediction = model.predict(
        X_test
    )

    return calculate_metrics(
        y_test.to_numpy(),
        prediction,
    )


# ============================================================
# RECURSIVE PREDICTION
# ============================================================

def recursive_predict(
    series: pd.Series,
    model: HistGradientBoostingRegressor,
    horizon: int,
) -> pd.DataFrame:
    """
    Generate future predictions recursively.

    Future predicted expenses become lag values for later
    forecast periods.
    """

    history = pd.DataFrame(
        {
            "period": series.index,
            "expense": series.values,
        }
    )

    predictions: list[dict[str, object]] = []

    for _ in range(horizon):

        next_period = (
            history["period"].max()
            + pd.offsets.MonthBegin(1)
        )

        extended = pd.concat(
            [
                history,
                pd.DataFrame(
                    {
                        "period": [
                            next_period
                        ],
                        "expense": [
                            np.nan
                        ],
                    }
                ),
            ],
            ignore_index=True,
        )

        features = create_features(
            extended
        )

        current = features.iloc[
            [-1]
        ][FEATURE_COLUMNS]

        current = current.ffill(
            axis=0
        ).fillna(0)

        prediction = float(
            model.predict(
                current
            )[0]
        )

        # Expenses cannot be negative.
        prediction = max(
            prediction,
            0.0,
        )

        predictions.append(
            {
                "period": next_period,
                "predicted_expense": prediction,
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
                        "expense": [
                            prediction
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
# ACCOUNT PREDICTION
# ============================================================

def predict_account(
    account_number: int,
    account_name: str,
    series: pd.Series,
) -> pd.DataFrame:
    """Train and predict one expense account."""

    logger.info(
        "Predicting account %s - %s",
        account_number,
        account_name,
    )

    metrics = validate_account_model(
        series
    )

    logger.info(
        "Account %s | MAE %.2f | RMSE %.2f | MAPE %.2f%%",
        account_number,
        metrics["mae"],
        metrics["rmse"],
        metrics["mape_pct"],
    )

    X, y = prepare_training_data(
        series
    )

    model = create_model()

    model.fit(
        X,
        y,
    )

    forecast = recursive_predict(
        series=series,
        model=model,
        horizon=HORIZON,
    )

    forecast["account_number"] = (
        account_number
    )

    forecast["account_name"] = (
        account_name
    )

    forecast["model"] = (
        "HistGradientBoosting"
    )

    forecast["validation_mae"] = (
        metrics["mae"]
    )

    forecast["validation_rmse"] = (
        metrics["rmse"]
    )

    forecast["validation_mape_pct"] = (
        metrics["mape_pct"]
    )

    forecast["prediction_type"] = (
        "ML_PREDICTION"
    )

    # --------------------------------------------------------
    # Transparent uncertainty interval
    # --------------------------------------------------------

    forecast["lower_bound"] = np.maximum(
        forecast["predicted_expense"]
        - 1.96 * metrics["rmse"],
        0,
    )

    forecast["upper_bound"] = (
        forecast["predicted_expense"]
        + 1.96 * metrics["rmse"]
    )

    forecast["year_month"] = (
        forecast["period"]
        .dt.strftime("%Y-%m")
    )

    forecast["forecast_year"] = (
        forecast["period"]
        .dt.year
    )

    forecast["forecast_month"] = (
        forecast["period"]
        .dt.month
    )

    return forecast[
        [
            "period",
            "year_month",
            "forecast_year",
            "forecast_month",

            "account_number",
            "account_name",

            "predicted_expense",
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
# SAVE
# ============================================================

def save_output(
    df: pd.DataFrame,
) -> None:
    """Save Expense Prediction dataset."""

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    logger.info(
        "Expense prediction saved to %s",
        OUTPUT_FILE,
    )


# ============================================================
# MAIN
# ============================================================

def main() -> int:
    """Run Expense Prediction pipeline."""

    try:

        logger.info(
            "Starting EFAP Expense Prediction."
        )

        raw = load_data()

        prepared = prepare_data(
            raw
        )

        account_series = (
            create_account_series(
                prepared
            )
        )

        outputs = []

        for account_number, series in (
            account_series.items()
        ):

            account_name = (
                EXPENSE_ACCOUNTS[
                    account_number
                ]
            )

            try:

                result = predict_account(
                    account_number=account_number,
                    account_name=account_name,
                    series=series,
                )

                outputs.append(
                    result
                )

            except Exception as exc:

                logger.exception(
                    "Prediction failed for account "
                    "%s: %s",
                    account_number,
                    exc,
                )

        if not outputs:
            raise RuntimeError(
                "No Expense predictions were generated."
            )

        final = pd.concat(
            outputs,
            ignore_index=True,
        )

        final = final.sort_values(
            [
                "period",
                "account_number",
            ]
        ).reset_index(
            drop=True
        )

        save_output(
            final
        )

        logger.info(
            "Generated %s prediction rows.",
            len(final),
        )

        logger.info(
            "Expense Prediction completed successfully."
        )

        return 0

    except Exception as exc:

        logger.exception(
            "Expense Prediction failed: %s",
            exc,
        )

        return 1


if __name__ == "__main__":
    sys.exit(main())