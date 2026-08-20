"""
EFAP - Classification Models

Object:
    Python/models/classification_models.py

Purpose:
    Supervised classification of financial controller states.

Classification tasks:

    1. Financial Anomaly Risk
       NORMAL / WATCH / HIGH / CRITICAL

    2. Liquidity Risk
       HEALTHY / WATCH / LIQUIDITY_RISK

    3. EBITDA Performance
       NEGATIVE / ZERO / POSITIVE

Input sources:
    data/processed/controller_kpi_timeseries.csv
    data/analytics/financial_anomaly_monthly_summary.csv

Model:
    RandomForestClassifier

Design principle:
    Avoid target leakage by using lagged and rolling financial
    features instead of current target values.

Outputs:
    data/predictions/financial_classification_predictions.csv
    data/predictions/classification_model_metrics.csv
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Final

import numpy as np
import pandas as pd

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import (
        accuracy_score,
        classification_report,
        f1_score,
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

TIME_SERIES_FILE: Final[Path] = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "controller_kpi_timeseries.csv"
)

ANOMALY_SUMMARY_FILE: Final[Path] = (
    PROJECT_ROOT
    / "data"
    / "analytics"
    / "financial_anomaly_monthly_summary.csv"
)

OUTPUT_DIR: Final[Path] = (
    PROJECT_ROOT
    / "data"
    / "predictions"
)

PREDICTION_OUTPUT: Final[Path] = (
    OUTPUT_DIR
    / "financial_classification_predictions.csv"
)

METRICS_OUTPUT: Final[Path] = (
    OUTPUT_DIR
    / "classification_model_metrics.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

VALIDATION_MONTHS: Final[int] = 6

MIN_HISTORY: Final[int] = 24

RANDOM_STATE: Final[int] = 42

N_ESTIMATORS: Final[int] = 300


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# ============================================================
# LOAD DATA
# ============================================================

def load_time_series() -> pd.DataFrame:
    """Load canonical controller time series."""

    if not TIME_SERIES_FILE.exists():
        raise FileNotFoundError(
            f"Missing file: {TIME_SERIES_FILE}"
        )

    df = pd.read_csv(
        TIME_SERIES_FILE
    )

    required = {
        "period",
        "revenue",
        "operating_costs",
        "ebitda",
        "net_profit",
        "net_working_capital",
        "current_ratio",
        "quick_ratio",
        "cash_ratio",
        "closing_cash",
        "operating_cash_flow",
        "dso_days",
        "dio_days",
        "dpo_days",
        "cash_conversion_cycle_days",
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            "Time-series dataset is missing columns: "
            + ", ".join(sorted(missing))
        )

    df["period"] = pd.to_datetime(
        df["period"],
        errors="coerce",
    )

    numeric_columns = [
        column
        for column in required
        if column != "period"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    df = (
        df
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
            f"At least {MIN_HISTORY} observations are required. "
            f"Found {len(df)}."
        )

    return df


def load_anomaly_summary() -> pd.DataFrame:
    """Load anomaly classification labels."""

    if not ANOMALY_SUMMARY_FILE.exists():
        raise FileNotFoundError(
            f"Missing file: {ANOMALY_SUMMARY_FILE}"
        )

    df = pd.read_csv(
        ANOMALY_SUMMARY_FILE
    )

    required = {
        "period",
        "controller_status",
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            "Anomaly summary is missing columns: "
            + ", ".join(sorted(missing))
        )

    df["period"] = pd.to_datetime(
        df["period"],
        errors="coerce",
    )

    return (
        df[
            [
                "period",
                "controller_status",
            ]
        ]
        .dropna(subset=["period"])
        .drop_duplicates("period")
        .sort_values("period")
    )


# ============================================================
# FEATURE ENGINEERING
# ============================================================

def create_features(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create features based only on information available before
    the classification month.

    This is important to avoid target leakage.
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

    result["revenue_rolling_3"] = (
        result["revenue"]
        .shift(1)
        .rolling(3, min_periods=3)
        .mean()
    )

    result["revenue_rolling_12"] = (
        result["revenue"]
        .shift(1)
        .rolling(12, min_periods=12)
        .mean()
    )

    # --------------------------------------------------------
    # EBITDA
    # --------------------------------------------------------

    result["ebitda_lag_1"] = (
        result["ebitda"].shift(1)
    )

    result["ebitda_lag_3"] = (
        result["ebitda"].shift(3)
    )

    result["ebitda_margin_lag_1"] = (
        (
            result["ebitda"]
            / result["revenue"].replace(
                0,
                np.nan,
            )
        )
        .shift(1)
    )

    # --------------------------------------------------------
    # Net Profit
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

    result["nwc_change_lag_1"] = (
        result["net_working_capital"]
        .diff()
        .shift(1)
    )

    # --------------------------------------------------------
    # Liquidity
    # --------------------------------------------------------

    result["current_ratio_lag_1"] = (
        result["current_ratio"].shift(1)
    )

    result["quick_ratio_lag_1"] = (
        result["quick_ratio"].shift(1)
    )

    result["cash_ratio_lag_1"] = (
        result["cash_ratio"].shift(1)
    )

    # --------------------------------------------------------
    # Cash Flow
    # --------------------------------------------------------

    result["ocf_lag_1"] = (
        result["operating_cash_flow"].shift(1)
    )

    result["ocf_lag_3"] = (
        result["operating_cash_flow"].shift(3)
    )

    result["cash_lag_1"] = (
        result["closing_cash"].shift(1)
    )

    result["cash_lag_3"] = (
        result["closing_cash"].shift(3)
    )

    # --------------------------------------------------------
    # Working Capital Days
    # --------------------------------------------------------

    result["dso_lag_1"] = (
        result["dso_days"].shift(1)
    )

    result["dio_lag_1"] = (
        result["dio_days"].shift(1)
    )

    result["dpo_lag_1"] = (
        result["dpo_days"].shift(1)
    )

    result["ccc_lag_1"] = (
        result[
            "cash_conversion_cycle_days"
        ].shift(1)
    )

    return result


FEATURE_COLUMNS: Final[list[str]] = [
    "month",
    "quarter",
    "month_sin",
    "month_cos",

    "revenue_lag_1",
    "revenue_lag_3",
    "revenue_lag_12",
    "revenue_rolling_3",
    "revenue_rolling_12",

    "ebitda_lag_1",
    "ebitda_lag_3",
    "ebitda_margin_lag_1",

    "net_profit_lag_1",
    "net_profit_lag_3",

    "nwc_lag_1",
    "nwc_change_lag_1",

    "current_ratio_lag_1",
    "quick_ratio_lag_1",
    "cash_ratio_lag_1",

    "ocf_lag_1",
    "ocf_lag_3",

    "cash_lag_1",
    "cash_lag_3",

    "dso_lag_1",
    "dio_lag_1",
    "dpo_lag_1",
    "ccc_lag_1",
]


# ============================================================
# LABEL CREATION
# ============================================================

def create_labels(
    df: pd.DataFrame,
    anomaly_summary: pd.DataFrame,
) -> pd.DataFrame:
    """Create classification targets."""

    result = df.copy()

    # --------------------------------------------------------
    # Anomaly label
    # --------------------------------------------------------

    result = result.merge(
        anomaly_summary,
        on="period",
        how="left",
    )

    result["anomaly_class"] = (
        result["controller_status"]
        .fillna("NORMAL")
    )

    # --------------------------------------------------------
    # Liquidity label
    #
    # This reproduces the existing controller definition but
    # the classifier will use only lagged values as features.
    # --------------------------------------------------------

    result["liquidity_class"] = np.select(
        [
            result["current_ratio"] < 1,
            result["current_ratio"] < 1.5,
        ],
        [
            "LIQUIDITY_RISK",
            "WATCH",
        ],
        default="HEALTHY",
    )

    # --------------------------------------------------------
    # EBITDA performance label
    # --------------------------------------------------------

    result["ebitda_class"] = np.select(
        [
            result["ebitda"] < 0,
            result["ebitda"] > 0,
        ],
        [
            "NEGATIVE",
            "POSITIVE",
        ],
        default="ZERO",
    )

    return result


# ============================================================
# MODEL
# ============================================================

def create_model() -> RandomForestClassifier:
    """Create Random Forest classifier."""

    return RandomForestClassifier(
        n_estimators=N_ESTIMATORS,
        max_depth=8,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )


# ============================================================
# TRAINING
# ============================================================

def prepare_dataset(
    df: pd.DataFrame,
    target: str,
) -> tuple[
    pd.DataFrame,
    pd.Series,
]:
    """Prepare feature/target dataset."""

    data = create_features(
        df
    )

    # Determine which feature columns are usable.
    # Drop any that are entirely NaN (e.g. dso_days may be
    # absent from the source data).
    usable_features = [
        col
        for col in FEATURE_COLUMNS
        if col in data.columns
        and data[col].notna().any()
    ]

    if not usable_features:
        raise ValueError(
            "No usable feature columns remain "
            "after removing all-NaN columns."
        )

    dropped = set(FEATURE_COLUMNS) - set(usable_features)

    if dropped:
        logger.info(
            "Dropped all-NaN features: %s",
            ", ".join(sorted(dropped)),
        )

    data = data.dropna(
        subset=usable_features + [target]
    ).copy()

    if data.empty:
        raise ValueError(
            f"No valid observations for target '{target}'."
        )

    X = data[usable_features]

    # RandomForestClassifier cannot handle NaN.
    # Fill remaining sparse NaN with 0.
    X = X.fillna(0)

    y = data[target]

    return X, y


def validate_target(
    y: pd.Series,
    target_name: str,
) -> None:
    """Validate that enough classes exist."""

    class_count = y.nunique()

    logger.info(
        "%s contains %s classes.",
        target_name,
        class_count,
    )

    if class_count < 2:
        raise ValueError(
            f"Target '{target_name}' contains fewer than "
            "two classes and cannot be classified."
        )


# ============================================================
# MODEL EVALUATION
# ============================================================

def evaluate_model(
    X: pd.DataFrame,
    y: pd.Series,
    target_name: str,
) -> tuple[
    RandomForestClassifier,
    dict[str, float],
    pd.DataFrame,
]:
    """Train and evaluate one classifier."""

    validate_target(
        y,
        target_name,
    )

    if len(X) <= VALIDATION_MONTHS:
        raise ValueError(
            f"Not enough observations for '{target_name}'."
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

    predictions = model.predict(
        X_test
    )

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    macro_f1 = f1_score(
        y_test,
        predictions,
        average="macro",
        zero_division=0,
    )

    report = classification_report(
        y_test,
        predictions,
        output_dict=True,
        zero_division=0,
    )

    metrics = {
        "target": target_name,
        "accuracy": float(accuracy),
        "macro_f1": float(macro_f1),
        "validation_rows": int(
            len(y_test)
        ),
        "class_count": int(
            y.nunique()
        ),
    }

    logger.info(
        "%s | Accuracy %.3f | Macro F1 %.3f",
        target_name,
        accuracy,
        macro_f1,
    )

    return (
        model,
        metrics,
        pd.DataFrame(report).T.reset_index(
            names="class"
        ),
    )


# ============================================================
# PREDICTIONS
# ============================================================

def fit_and_predict(
    df: pd.DataFrame,
    target: str,
    target_name: str,
) -> tuple[
    pd.DataFrame,
    dict[str, float],
]:
    """Fit classifier on full history and classify each month."""

    X, y = prepare_dataset(
        df,
        target,
    )

    _, metrics, _ = evaluate_model(
        X,
        y,
        target_name,
    )

    validate_target(
        y,
        target_name,
    )

    final_model = create_model()

    final_model.fit(
        X,
        y,
    )

    predictions = final_model.predict(
        X
    )

    probabilities = (
        final_model.predict_proba(
            X
        ).max(axis=1)
    )

    output = pd.DataFrame(
        {
            "period": df.loc[
                X.index,
                "period",
            ].values,

            f"{target_name}_predicted":
                predictions,

            f"{target_name}_confidence":
                probabilities,
        }
    )

    return output, metrics


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

def get_feature_importance(
    df: pd.DataFrame,
    target: str,
    target_name: str,
) -> pd.DataFrame:
    """Train final model and export feature importance."""

    X, y = prepare_dataset(
        df,
        target,
    )

    validate_target(
        y,
        target_name,
    )

    model = create_model()

    model.fit(
        X,
        y,
    )

    importance = pd.DataFrame(
        {
            "target": target_name,
            "feature": list(X.columns),
            "importance":
                model.feature_importances_,
        }
    )

    return importance.sort_values(
        "importance",
        ascending=False,
    )


# ============================================================
# SAVE
# ============================================================

def save_outputs(
    predictions: pd.DataFrame,
    metrics: pd.DataFrame,
    feature_importance: pd.DataFrame,
) -> None:
    """Save classification outputs."""

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    predictions.to_csv(
        PREDICTION_OUTPUT,
        index=False,
    )

    metrics.to_csv(
        METRICS_OUTPUT,
        index=False,
    )

    feature_file = (
        OUTPUT_DIR
        / "classification_feature_importance.csv"
    )

    feature_importance.to_csv(
        feature_file,
        index=False,
    )

    logger.info(
        "Classification predictions saved to %s",
        PREDICTION_OUTPUT,
    )

    logger.info(
        "Classification metrics saved to %s",
        METRICS_OUTPUT,
    )

    logger.info(
        "Feature importance saved to %s",
        feature_file,
    )


# ============================================================
# MAIN
# ============================================================

def main() -> int:
    """Run classification pipeline."""

    try:

        logger.info(
            "Starting EFAP Classification Models."
        )

        time_series = load_time_series()

        anomaly_summary = load_anomaly_summary()

        dataset = create_labels(
            time_series,
            anomaly_summary,
        )

        prediction_outputs = []
        metric_outputs = []
        importance_outputs = []

        targets = [
            (
                "anomaly_class",
                "anomaly_risk",
            ),
            (
                "liquidity_class",
                "liquidity_risk",
            ),
            (
                "ebitda_class",
                "ebitda_performance",
            ),
        ]

        for target, target_name in targets:

            logger.info(
                "Training classifier: %s",
                target_name,
            )

            try:

                prediction, metrics = (
                    fit_and_predict(
                        dataset,
                        target,
                        target_name,
                    )
                )

                prediction_outputs.append(
                    prediction
                )

                metric_outputs.append(
                    pd.DataFrame(
                        [metrics]
                    )
                )

                importance = (
                    get_feature_importance(
                        dataset,
                        target,
                        target_name,
                    )
                )

                importance_outputs.append(
                    importance
                )

            except ValueError as exc:

                logger.warning(
                    "Skipping %s: %s",
                    target_name,
                    exc,
                )

        if not prediction_outputs:
            raise RuntimeError(
                "No classification model could be trained."
            )

        # ----------------------------------------------------
        # Combine prediction outputs
        # ----------------------------------------------------

        predictions = prediction_outputs[0]

        for prediction in prediction_outputs[1:]:

            predictions = predictions.merge(
                prediction,
                on="period",
                how="outer",
            )

        predictions = (
            predictions
            .sort_values("period")
            .reset_index(drop=True)
        )

        # ----------------------------------------------------
        # Metrics
        # ----------------------------------------------------

        metrics_df = pd.concat(
            metric_outputs,
            ignore_index=True,
        )

        # ----------------------------------------------------
        # Feature importance
        # ----------------------------------------------------

        importance_df = pd.concat(
            importance_outputs,
            ignore_index=True,
        )

        save_outputs(
            predictions,
            metrics_df,
            importance_df,
        )

        logger.info(
            "Classification Models completed successfully."
        )

        return 0

    except Exception as exc:

        logger.exception(
            "Classification Models failed: %s",
            exc,
        )

        return 1


if __name__ == "__main__":
    sys.exit(main())