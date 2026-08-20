"""
EFAP - Financial Anomaly Detection

Object:
    Python/anomaly_detection/detect_financial_anomalies.py

Purpose:
    Detect unusual financial observations using:

        1. Rolling robust baseline
           - rolling median
           - rolling IQR

        2. Multivariate Isolation Forest

    The module does NOT classify anomalies as fraud.
    It identifies observations that deserve controller review.

Input:
    data/processed/controller_kpi_timeseries.csv

Outputs:
    data/analytics/financial_anomalies.csv
    data/analytics/financial_anomaly_monthly_summary.csv

Metrics monitored:
    Revenue
    Operating Costs
    EBITDA
    Net Profit
    Closing Cash
    Net Working Capital
    Operating Cash Flow
    Free Cash Flow
    DSO
    DIO
    DPO
    Cash Conversion Cycle
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Final

import numpy as np
import pandas as pd

try:
    from sklearn.ensemble import IsolationForest
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

INPUT_FILE: Final[Path] = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "controller_kpi_timeseries.csv"
)

OUTPUT_DIR: Final[Path] = (
    PROJECT_ROOT
    / "data"
    / "analytics"
)

DETAIL_OUTPUT: Final[Path] = (
    OUTPUT_DIR
    / "financial_anomalies.csv"
)

SUMMARY_OUTPUT: Final[Path] = (
    OUTPUT_DIR
    / "financial_anomaly_monthly_summary.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

ROLLING_WINDOW: Final[int] = 12

MIN_ROLLING_OBSERVATIONS: Final[int] = 6

IQR_MULTIPLIER: Final[float] = 1.5

ISOLATION_CONTAMINATION: Final[str] = "auto"

RANDOM_STATE: Final[int] = 42


# ============================================================
# METRICS
# ============================================================

MONITORED_METRICS: Final[dict[str, str]] = {
    "revenue": "Revenue",
    "operating_costs": "Operating Costs",
    "ebitda": "EBITDA",
    "net_profit": "Net Profit",
    "closing_cash": "Closing Cash",
    "net_working_capital": "Net Working Capital",
    "operating_cash_flow": "Operating Cash Flow",
    "free_cash_flow": "Free Cash Flow",
    "dso_days": "DSO",
    "dio_days": "DIO",
    "dpo_days": "DPO",
    "cash_conversion_cycle_days": "Cash Conversion Cycle",
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
# DATA LOADING
# ============================================================

def load_data() -> pd.DataFrame:
    """Load canonical EFAP time series."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    logger.info(
        "Loading time series from %s",
        INPUT_FILE,
    )

    df = pd.read_csv(
        INPUT_FILE
    )

    required_columns = {
        "period",
        *MONITORED_METRICS.keys(),
    }

    missing = (
        required_columns
        - set(df.columns)
    )

    if missing:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(sorted(missing))
        )

    df["period"] = pd.to_datetime(
        df["period"],
        errors="coerce",
    )

    df = (
        df
        .dropna(subset=["period"])
        .sort_values("period")
        .drop_duplicates(
            subset=["period"]
        )
        .reset_index(drop=True)
    )

    if df.empty:
        raise ValueError(
            "Time-series dataset is empty."
        )

    for metric in MONITORED_METRICS:
        df[metric] = pd.to_numeric(
            df[metric],
            errors="coerce",
        )

    return df


# ============================================================
# UNIVARIATE ANOMALY DETECTION
# ============================================================

def detect_rolling_iqr(
    series: pd.Series,
) -> pd.DataFrame:
    """
    Detect anomalies using rolling median and IQR.

    Observation is anomalous when:
        value > Q3 + multiplier * IQR
        OR
        value < Q1 - multiplier * IQR

    Rolling statistics are shifted by one month, so the
    current observation does not influence its own baseline.
    """

    rolling = series.rolling(
        window=ROLLING_WINDOW,
        min_periods=MIN_ROLLING_OBSERVATIONS,
    )

    q1 = rolling.quantile(0.25).shift(1)
    q3 = rolling.quantile(0.75).shift(1)

    median = rolling.median().shift(1)

    iqr = q3 - q1

    lower_bound = (
        q1 - IQR_MULTIPLIER * iqr
    )

    upper_bound = (
        q3 + IQR_MULTIPLIER * iqr
    )

    anomaly = (
        (series < lower_bound)
        | (series > upper_bound)
    )

    deviation = np.where(
        series > upper_bound,
        series - upper_bound,
        np.where(
            series < lower_bound,
            series - lower_bound,
            0.0,
        ),
    )

    robust_score = np.where(
        iqr > 0,
        deviation / iqr,
        0.0,
    )

    result = pd.DataFrame(
        {
            "value": series,
            "baseline_median": median,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "deviation": deviation,
            "robust_score": robust_score,
            "iqr_anomaly": anomaly,
        },
        index=series.index,
    )

    return result


# ============================================================
# SEVERITY
# ============================================================

def severity_from_score(
    score: float,
) -> str:
    """Convert anomaly score into controller severity."""

    if not np.isfinite(score):
        return "NORMAL"

    absolute = abs(score)

    if absolute >= 4:
        return "CRITICAL"

    if absolute >= 2.5:
        return "HIGH"

    if absolute >= 1.5:
        return "MEDIUM"

    if absolute > 0:
        return "LOW"

    return "NORMAL"


# ============================================================
# MONTHLY ANOMALY DETAIL
# ============================================================

def build_univariate_results(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Create one anomaly record per period and metric."""

    results: list[dict[str, object]] = []

    for metric, metric_label in MONITORED_METRICS.items():

        logger.info(
            "Analysing metric: %s",
            metric_label,
        )

        analysis = detect_rolling_iqr(
            df[metric]
        )

        for index in df.index:

            value = (
                analysis.loc[
                    index,
                    "value",
                ]
            )

            if pd.isna(value):
                continue

            baseline = (
                analysis.loc[
                    index,
                    "baseline_median",
                ]
            )

            lower_bound = (
                analysis.loc[
                    index,
                    "lower_bound",
                ]
            )

            upper_bound = (
                analysis.loc[
                    index,
                    "upper_bound",
                ]
            )

            deviation = (
                analysis.loc[
                    index,
                    "deviation",
                ]
            )

            score = (
                analysis.loc[
                    index,
                    "robust_score",
                ]
            )

            is_anomaly = bool(
                analysis.loc[
                    index,
                    "iqr_anomaly",
                ]
            )

            severity = (
                severity_from_score(
                    score
                )
                if is_anomaly
                else "NORMAL"
            )

            if (
                is_anomaly
                and value > upper_bound
            ):
                direction = "ABOVE_EXPECTED"

            elif (
                is_anomaly
                and value < lower_bound
            ):
                direction = "BELOW_EXPECTED"

            else:
                direction = "NORMAL"

            results.append(
                {
                    "period": df.loc[
                        index,
                        "period",
                    ],
                    "metric": metric,
                    "metric_label": metric_label,
                    "actual_value": value,
                    "baseline_median": baseline,
                    "lower_bound": lower_bound,
                    "upper_bound": upper_bound,
                    "deviation": deviation,
                    "robust_score": score,
                    "anomaly_flag": is_anomaly,
                    "severity": severity,
                    "direction": direction,
                    "detection_method": "ROLLING_IQR",
                }
            )

    return pd.DataFrame(
        results
    )


# ============================================================
# MULTIVARIATE ISOLATION FOREST
# ============================================================

def detect_isolation_forest(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Detect unusual monthly combinations of financial KPIs.

    Each month is treated as one observation.
    """

    features = list(
        MONITORED_METRICS.keys()
    )

    model_data = df[
        features
    ].copy()

    model_data = (
        model_data
        .replace(
            [np.inf, -np.inf],
            np.nan,
        )
    )

    # Fill missing KPI values with median so the model receives
    # a complete matrix.
    model_data = model_data.fillna(
        model_data.median()
    )

    if len(model_data) < 12:
        logger.warning(
            "Too few observations for Isolation Forest."
        )

        return pd.DataFrame(
            {
                "period": df["period"],
                "isolation_anomaly": False,
                "isolation_score": 0.0,
            }
        )

    model = IsolationForest(
        contamination=ISOLATION_CONTAMINATION,
        random_state=RANDOM_STATE,
        n_estimators=300,
    )

    predictions = model.fit_predict(
        model_data
    )

    scores = model.decision_function(
        model_data
    )

    return pd.DataFrame(
        {
            "period": df["period"],
            "isolation_anomaly": (
                predictions == -1
            ),
            "isolation_score": scores,
        }
    )


# ============================================================
# COMBINE RESULTS
# ============================================================

def combine_results(
    detail: pd.DataFrame,
    isolation: pd.DataFrame,
) -> pd.DataFrame:
    """Combine univariate and multivariate detection."""

    detail = detail.merge(
        isolation,
        on="period",
        how="left",
    )

    detail["combined_anomaly"] = (
        detail["anomaly_flag"]
        | detail["isolation_anomaly"]
    )

    detail["controller_action"] = np.select(
        [
            detail["severity"] == "CRITICAL",
            detail["severity"] == "HIGH",
            detail["severity"] == "MEDIUM",
            detail["combined_anomaly"],
        ],
        [
            "IMMEDIATE_REVIEW",
            "ROOT_CAUSE_REVIEW",
            "MANAGEMENT_REVIEW",
            "MONITOR",
        ],
        default="NO_ACTION",
    )

    return detail


# ============================================================
# MONTHLY SUMMARY
# ============================================================

def build_monthly_summary(
    detail: pd.DataFrame,
) -> pd.DataFrame:
    """
    Produce one controller-level row per month.
    """

    grouped = (
        detail
        .groupby(
            "period",
            as_index=False,
        )
        .agg(
            anomaly_count=(
                "combined_anomaly",
                "sum",
            ),
            high_or_critical_count=(
                "severity",
                lambda values: (
                    values.isin(
                        [
                            "HIGH",
                            "CRITICAL",
                        ]
                    ).sum()
                ),
            ),
            max_robust_score=(
                "robust_score",
                "max",
            ),
        )
    )

    # Highest-severity anomaly per month.
    severity_rank = {
        "NORMAL": 0,
        "LOW": 1,
        "MEDIUM": 2,
        "HIGH": 3,
        "CRITICAL": 4,
    }

    max_severity = (
        detail
        .assign(
            severity_rank=detail[
                "severity"
            ].map(severity_rank)
        )
        .groupby("period")[
            "severity_rank"
        ]
        .max()
        .reset_index()
    )

    reverse_rank = {
        value: key
        for key, value in severity_rank.items()
    }

    max_severity["max_severity"] = (
        max_severity["severity_rank"]
        .map(reverse_rank)
    )

    grouped = grouped.merge(
        max_severity[
            [
                "period",
                "max_severity",
            ]
        ],
        on="period",
        how="left",
    )

    grouped["controller_status"] = np.select(
        [
            grouped[
                "max_severity"
            ] == "CRITICAL",

            grouped[
                "max_severity"
            ] == "HIGH",

            grouped[
                "anomaly_count"
            ] > 0,
        ],
        [
            "CRITICAL",
            "HIGH",
            "WATCH",
        ],
        default="NORMAL",
    )

    return grouped.sort_values(
        "period"
    ).reset_index(
        drop=True
    )


# ============================================================
# SAVE
# ============================================================

def save_outputs(
    detail: pd.DataFrame,
    summary: pd.DataFrame,
) -> None:
    """Save anomaly datasets."""

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    detail.to_csv(
        DETAIL_OUTPUT,
        index=False,
    )

    summary.to_csv(
        SUMMARY_OUTPUT,
        index=False,
    )

    logger.info(
        "Detailed anomalies saved to %s",
        DETAIL_OUTPUT,
    )

    logger.info(
        "Monthly anomaly summary saved to %s",
        SUMMARY_OUTPUT,
    )


# ============================================================
# MAIN
# ============================================================

def main() -> int:
    """Run anomaly detection pipeline."""

    try:

        logger.info(
            "Starting EFAP Financial Anomaly Detection."
        )

        df = load_data()

        detail = build_univariate_results(
            df
        )

        isolation = detect_isolation_forest(
            df
        )

        detail = combine_results(
            detail,
            isolation,
        )

        summary = build_monthly_summary(
            detail
        )

        save_outputs(
            detail,
            summary,
        )

        total_anomalies = int(
            detail[
                "combined_anomaly"
            ].sum()
        )

        logger.info(
            "Detected %s metric-level anomalies.",
            total_anomalies,
        )

        logger.info(
            "Anomaly Detection completed successfully."
        )

        return 0

    except Exception as exc:

        logger.exception(
            "Anomaly Detection failed: %s",
            exc,
        )

        return 1


if __name__ == "__main__":
    sys.exit(main())