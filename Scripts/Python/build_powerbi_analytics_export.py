"""
EFAP - Power BI Analytics Reporting Export

Object:
    Scripts/Python/reporting/build_powerbi_analytics_export.py

Purpose:
    Consolidate EFAP analytical outputs into one Power BI-ready
    monthly reporting dataset.

Grain:
    Exactly one row per calendar month.

Authoritative ACTUAL / FORECAST boundary:
    data/processed/controller_kpi_timeseries.csv

Management sign convention:
    Revenue              positive
    Operating Costs      negative
    EBITDA               signed result
    EBIT                 signed result
    Net Profit           signed result
    Cash Flow            signed result

Important:
    This script consolidates and normalizes reporting outputs.
    It does not replace the underlying financial business logic.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CONTROLLER_TIMESERIES_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "controller_kpi_timeseries.csv"
)

ANALYTICS_DIR = (
    PROJECT_ROOT
    / "data"
    / "analytics"
)

FORECAST_DIR = (
    PROJECT_ROOT
    / "data"
    / "forecasts"
)

PREDICTION_DIR = (
    PROJECT_ROOT
    / "data"
    / "predictions"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "powerbi"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "efap_analytics_reporting.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

EXPECTED_FORECAST_HORIZON = 6


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# ============================================================
# FILE LOADING
# ============================================================

def load_required_csv(
    path: Path,
    dataset_name: str,
) -> pd.DataFrame:
    """Load a required CSV dataset."""

    if not path.exists():
        raise FileNotFoundError(
            f"{dataset_name} not found: {path}"
        )

    logger.info(
        "Loading %s: %s",
        dataset_name,
        path,
    )

    df = pd.read_csv(path)

    if df.empty:
        raise ValueError(
            f"{dataset_name} is empty: {path}"
        )

    return df


def load_optional_csv(
    path: Path,
    dataset_name: str,
) -> pd.DataFrame:
    """Load an optional CSV dataset."""

    if not path.exists():
        logger.warning(
            "Optional dataset not found: %s",
            path,
        )
        return pd.DataFrame()

    logger.info(
        "Loading %s: %s",
        dataset_name,
        path,
    )

    return pd.read_csv(path)


def normalize_period(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Normalize period column to monthly-start timestamp.

    This ensures that all datasets can be safely merged
    on the same monthly key.
    """

    if df.empty:
        return df

    result = df.copy()

    if "period" in result.columns:

        result["period"] = (
            pd.to_datetime(
                result["period"],
                errors="coerce",
            )
            .dt.to_period("M")
            .dt.to_timestamp()
        )

    return result


# ============================================================
# LOAD ALL SOURCES
# ============================================================

def load_all_sources() -> dict[str, pd.DataFrame]:
    """
    Load all EFAP reporting sources.

    Important:
        Expense forecast is sourced from:
            data/forecasts/expense_forecast.csv

        Revenue and Cash ML predictions are sourced from:
            data/predictions/
    """

    return {
        "controller_timeseries":
            normalize_period(
                load_required_csv(
                    CONTROLLER_TIMESERIES_FILE,
                    "Controller KPI time series",
                )
            ),

        "rolling_forecast":
            normalize_period(
                load_optional_csv(
                    FORECAST_DIR
                    / "rolling_forecast.csv",
                    "Rolling forecast",
                )
            ),

        "expense_forecast":
            normalize_period(
                load_optional_csv(
                    FORECAST_DIR
                    / "expense_forecast.csv",
                    "Expense forecast",
                )
            ),

        "anomaly":
            normalize_period(
                load_optional_csv(
                    ANALYTICS_DIR
                    / "financial_anomaly_monthly_summary.csv",
                    "Financial anomaly monthly summary",
                )
            ),

        "variance":
            normalize_period(
                load_optional_csv(
                    ANALYTICS_DIR
                    / "variance_root_cause_controller_summary.csv",
                    "Variance root cause summary",
                )
            ),

        "pvm":
            normalize_period(
                load_optional_csv(
                    ANALYTICS_DIR
                    / "price_volume_summary.csv",
                    "Price / Volume / Mix summary",
                )
            ),

        "revenue_prediction":
            normalize_period(
                load_optional_csv(
                    PREDICTION_DIR
                    / "revenue_prediction.csv",
                    "Revenue ML prediction",
                )
            ),

        "cash_prediction":
            normalize_period(
                load_optional_csv(
                    PREDICTION_DIR
                    / "cash_flow_prediction.csv",
                    "Cash Flow ML prediction",
                )
            ),

        "classification":
            normalize_period(
                load_optional_csv(
                    PREDICTION_DIR
                    / "financial_classification_predictions.csv",
                    "Financial classification predictions",
                )
            ),
    }


# ============================================================
# ACTUAL CUTOFF
# ============================================================

def determine_actual_cutoff(
    controller_timeseries: pd.DataFrame,
) -> pd.Timestamp:
    """
    Determine authoritative last actual financial month.
    """

    if "period" not in controller_timeseries.columns:
        raise ValueError(
            "Controller KPI time series is missing 'period'."
        )

    periods = (
        pd.to_datetime(
            controller_timeseries["period"],
            errors="coerce",
        )
        .dropna()
    )

    if periods.empty:
        raise RuntimeError(
            "No valid periods found in controller KPI time series."
        )

    cutoff = (
        periods
        .dt.to_period("M")
        .dt.to_timestamp()
        .max()
    )

    logger.info(
        "Last ACTUAL financial period: %s",
        cutoff.strftime("%Y-%m"),
    )

    return cutoff


# ============================================================
# MONTHLY CALENDAR
# ============================================================

def build_monthly_calendar(
    sources: dict[str, pd.DataFrame],
    actual_cutoff: pd.Timestamp,
) -> pd.DataFrame:
    """
    Build complete monthly calendar from all available sources.

    Exactly one row per month.
    """

    periods = []

    for name, df in sources.items():

        if df.empty:
            continue

        if "period" not in df.columns:
            continue

        values = (
            df["period"]
            .dropna()
            .unique()
            .tolist()
        )

        periods.extend(values)

        logger.info(
            "%s contributes %s unique periods.",
            name,
            len(set(values)),
        )

    if not periods:
        raise RuntimeError(
            "No reporting periods found."
        )

    calendar = pd.DataFrame(
        {
            "period": sorted(
                set(periods)
            )
        }
    )

    calendar["period"] = (
        pd.to_datetime(
            calendar["period"],
            errors="coerce",
        )
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    calendar = (
        calendar
        .dropna(subset=["period"])
        .drop_duplicates("period")
        .sort_values("period")
        .reset_index(drop=True)
    )

    calendar["year_month"] = (
        calendar["period"]
        .dt.strftime("%Y-%m")
    )

    calendar["calendar_year"] = (
        calendar["period"]
        .dt.year
    )

    calendar["calendar_month"] = (
        calendar["period"]
        .dt.month
    )

    calendar["reporting_data_type"] = (
        calendar["period"]
        .apply(
            lambda period:
            "ACTUAL"
            if period <= actual_cutoff
            else "FORECAST"
        )
    )

    return calendar


# ============================================================
# ROLLING FORECAST
# ============================================================

def prepare_rolling_forecast(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepare rolling forecast.

    Source:
        rolling_forecast.csv

    Output:
        rolling_revenue
        rolling_operating_costs
        rolling_ebitda
        rolling_ebitda_margin
    """

    if df.empty:
        return pd.DataFrame()

    required = {
        "period",
        "data_type",
        "forecast_horizon_month",
        "revenue",
        "operating_costs",
    }

    missing = required - set(df.columns)

    if missing:
        logger.warning(
            "Rolling forecast missing columns: %s",
            ", ".join(sorted(missing)),
        )
        return pd.DataFrame()

    result = df[
        [
            "period",
            "data_type",
            "forecast_horizon_month",
            "revenue",
            "operating_costs",
        ]
    ].copy()

    for column in [
        "revenue",
        "operating_costs",
        "forecast_horizon_month",
    ]:
        result[column] = pd.to_numeric(
            result[column],
            errors="coerce",
        )

    # --------------------------------------------------------
    # MANAGEMENT SIGN CONVENTION
    # --------------------------------------------------------

    result["rolling_revenue"] = (
        result["revenue"].abs()
    )

    result["rolling_operating_costs"] = (
        -result["operating_costs"].abs()
    )

    result["rolling_ebitda"] = (
        result["rolling_revenue"]
        + result["rolling_operating_costs"]
    )

    result["rolling_ebitda_margin"] = (
        result["rolling_ebitda"]
        .div(
            result["rolling_revenue"].replace(
                0,
                pd.NA,
            )
        )
        * 100
    )

    result = (
        result[
            [
                "period",
                "data_type",
                "forecast_horizon_month",
                "rolling_revenue",
                "rolling_operating_costs",
                "rolling_ebitda",
                "rolling_ebitda_margin",
            ]
        ]
        .rename(
            columns={
                "data_type":
                    "rolling_data_type",
            }
        )
        .sort_values(
            [
                "period",
                "rolling_data_type",
            ]
        )
        .drop_duplicates(
            "period",
            keep="last",
        )
        .reset_index(drop=True)
    )

    return result


# ============================================================
# EXPENSE FORECAST
# ============================================================

def prepare_expense_prediction(
    df: pd.DataFrame,
    actual_cutoff: pd.Timestamp,
) -> pd.DataFrame:
    """
    Prepare account-level expense forecast.

    Source:
        data/forecasts/expense_forecast.csv

    Source grain:
        Account + month

    Target grain:
        One row per forecast month.

    Management sign convention:
        Operating costs are negative.

    Important:
        Any rows on or before the actual cutoff are excluded.
        Therefore 2026-08 is never treated as ML FORECAST.
    """

    if df.empty:
        return pd.DataFrame()

    required = {
        "forecast_period",
        "forecast_expense",
        "lower_bound",
        "upper_bound",
        "validation_rmse",
    }

    missing = required - set(df.columns)

    if missing:
        logger.warning(
            "Expense forecast missing columns: %s",
            ", ".join(sorted(missing)),
        )
        return pd.DataFrame()

    result = df.copy()

    # --------------------------------------------------------
    # NORMALIZE PERIOD
    # --------------------------------------------------------

    result["period"] = (
        pd.to_datetime(
            result["forecast_period"],
            errors="coerce",
        )
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    if result["period"].isna().any():
        raise RuntimeError(
            "Expense forecast contains invalid forecast_period values."
        )

    # --------------------------------------------------------
    # KEEP FUTURE FORECAST ONLY
    # --------------------------------------------------------

    result = result[
        result["period"] > actual_cutoff
    ].copy()

    if result.empty:
        logger.warning(
            "Expense forecast contains no periods after actual cutoff."
        )
        return pd.DataFrame()

    # --------------------------------------------------------
    # NUMERIC NORMALIZATION
    # --------------------------------------------------------

    numeric_columns = [
        "forecast_expense",
        "lower_bound",
        "upper_bound",
        "validation_rmse",
    ]

    for column in numeric_columns:
        result[column] = pd.to_numeric(
            result[column],
            errors="coerce",
        )

    if result[numeric_columns].isna().any().any():
        raise RuntimeError(
            "Expense forecast contains invalid numeric values."
        )

    # --------------------------------------------------------
    # ACCOUNT-LEVEL -> MONTHLY AGGREGATION
    # --------------------------------------------------------

    monthly = (
        result
        .groupby(
            "period",
            as_index=False,
        )
        .agg(
            ml_predicted_expense_magnitude=(
                "forecast_expense",
                "sum",
            ),

            ml_expense_lower_bound_magnitude=(
                "lower_bound",
                "sum",
            ),

            ml_expense_upper_bound_magnitude=(
                "upper_bound",
                "sum",
            ),

            expense_prediction_rmse=(
                "validation_rmse",
                "mean",
            ),
        )
    )

    # --------------------------------------------------------
    # MANAGEMENT SIGN CONVENTION
    #
    # Source:
    #     positive expense magnitude
    #
    # Management reporting:
    #     negative operating costs
    # --------------------------------------------------------

    monthly[
        "ml_predicted_operating_costs"
    ] = (
        -monthly[
            "ml_predicted_expense_magnitude"
        ].abs()
    )

    # Source:
    # lower_bound <= forecast_expense <= upper_bound
    #
    # Management sign inversion:
    # lower bound = negative source upper
    # upper bound = negative source lower

    monthly[
        "ml_expense_lower_bound"
    ] = (
        -monthly[
            "ml_expense_upper_bound_magnitude"
        ].abs()
    )

    monthly[
        "ml_expense_upper_bound"
    ] = (
        -monthly[
            "ml_expense_lower_bound_magnitude"
        ].abs()
    )

    # --------------------------------------------------------
    # VALIDATE INTERVAL
    # --------------------------------------------------------

    invalid_interval = (
        monthly[
            "ml_expense_lower_bound"
        ]
        >
        monthly[
            "ml_expense_upper_bound"
        ]
    )

    if invalid_interval.any():
        raise RuntimeError(
            "Expense prediction interval is invalid after "
            "management sign normalization."
        )

    # --------------------------------------------------------
    # VALIDATE SIGN CONVENTION
    # --------------------------------------------------------

    invalid_costs = (
        monthly[
            "ml_predicted_operating_costs"
        ]
        > 0
    )

    if invalid_costs.any():
        raise RuntimeError(
            "Expense forecast contains positive operating "
            "cost values after sign normalization."
        )

    # --------------------------------------------------------
    # FINALIZE
    # --------------------------------------------------------

    monthly = (
        monthly
        .sort_values("period")
        .reset_index(drop=True)
    )

    logger.info(
        "Expense forecast prepared: %s forecast periods.",
        len(monthly),
    )

    logger.info(
        "Expense forecast sample:\n%s",
        monthly[
            [
                "period",
                "ml_predicted_expense_magnitude",
                "ml_predicted_operating_costs",
            ]
        ].to_string(index=False),
    )

    return monthly[
        [
            "period",
            "ml_predicted_expense_magnitude",
            "expense_prediction_rmse",
            "ml_predicted_operating_costs",
            "ml_expense_lower_bound",
            "ml_expense_upper_bound",
        ]
    ]


# ============================================================
# ANOMALY
# ============================================================

def prepare_anomaly(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Prepare monthly anomaly summary."""

    if df.empty:
        return pd.DataFrame()

    required = {
        "period",
        "anomaly_count",
        "high_or_critical_count",
        "max_severity",
        "controller_status",
    }

    missing = required - set(df.columns)

    if missing:
        logger.warning(
            "Anomaly dataset missing columns: %s",
            ", ".join(sorted(missing)),
        )
        return pd.DataFrame()

    columns = [
        "period",
        "anomaly_count",
        "high_or_critical_count",
        "max_severity",
        "controller_status",
    ]

    if "max_robust_score" in df.columns:
        columns.insert(
            3,
            "max_robust_score",
        )

    result = df[columns].copy()

    result = result.rename(
        columns={
            "high_or_critical_count":
                "high_critical_anomaly_count",

            "max_severity":
                "anomaly_max_severity",

            "controller_status":
                "anomaly_controller_status",
        }
    )

    return (
        result
        .sort_values("period")
        .drop_duplicates(
            "period",
            keep="last",
        )
        .reset_index(drop=True)
    )


# ============================================================
# VARIANCE ROOT CAUSE
# ============================================================

def prepare_variance(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Prepare controller variance root-cause output."""

    if df.empty:
        return pd.DataFrame()

    required = {
        "period",
        "metric",
        "total_variance",
        "primary_driver_account",
        "primary_driver_name",
        "primary_driver_variance",
        "primary_driver_contribution_pct",
        "controller_interpretation",
    }

    missing = required - set(df.columns)

    if missing:
        logger.warning(
            "Variance dataset missing columns: %s",
            ", ".join(sorted(missing)),
        )
        return pd.DataFrame()

    rows = []

    for period, group in df.groupby(
        "period",
        sort=True,
    ):

        row = {
            "period": period
        }

        for _, item in group.iterrows():

            metric = str(
                item["metric"]
            ).lower()

            metric = (
                metric
                .replace(" ", "_")
                .replace("-", "_")
            )

            prefix = (
                f"{metric}_root_cause"
            )

            row[
                f"{prefix}_variance"
            ] = item[
                "total_variance"
            ]

            row[
                f"{prefix}_primary_account"
            ] = item[
                "primary_driver_account"
            ]

            row[
                f"{prefix}_primary_driver"
            ] = item[
                "primary_driver_name"
            ]

            row[
                f"{prefix}_primary_variance"
            ] = item[
                "primary_driver_variance"
            ]

            row[
                f"{prefix}_primary_contribution_pct"
            ] = item[
                "primary_driver_contribution_pct"
            ]

            row[
                f"{prefix}_interpretation"
            ] = item[
                "controller_interpretation"
            ]

        rows.append(row)

    result = pd.DataFrame(rows)

    return (
        result
        .sort_values("period")
        .drop_duplicates(
            "period",
            keep="last",
        )
        .reset_index(drop=True)
    )


# ============================================================
# PRICE / VOLUME / MIX
# ============================================================

def prepare_pvm(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Prepare Price / Volume / Mix analysis."""

    if df.empty:
        return pd.DataFrame()

    required = {
        "period",
        "analysis_type",
        "total_variance",
        "price_effect",
        "volume_effect",
        "mix_effect",
        "reconciliation_check",
        "top_driver_account",
        "top_driver_name",
        "top_driver_variance",
        "price_status",
        "volume_status",
        "mix_status",
    }

    missing = required - set(df.columns)

    if missing:
        logger.warning(
            "PVM dataset missing columns: %s",
            ", ".join(sorted(missing)),
        )
        return pd.DataFrame()

    rows = []

    for period, group in df.groupby(
        "period",
        sort=True,
    ):

        row = {
            "period": period
        }

        for _, item in group.iterrows():

            analysis_type = str(
                item["analysis_type"]
            ).upper()

            if analysis_type == "REVENUE":

                prefix = "revenue_pvm"

            elif analysis_type in {
                "OPERATING_COST",
                "OPERATING_COSTS",
            }:

                prefix = "operating_cost_pvm"

            else:
                continue

            row[
                f"{prefix}_total_variance"
            ] = item[
                "total_variance"
            ]

            row[
                f"{prefix}_price_effect"
            ] = item[
                "price_effect"
            ]

            row[
                f"{prefix}_volume_effect"
            ] = item[
                "volume_effect"
            ]

            row[
                f"{prefix}_mix_effect"
            ] = item[
                "mix_effect"
            ]

            row[
                f"{prefix}_reconciliation_check"
            ] = item[
                "reconciliation_check"
            ]

            row[
                f"{prefix}_top_driver_account"
            ] = item[
                "top_driver_account"
            ]

            row[
                f"{prefix}_top_driver_name"
            ] = item[
                "top_driver_name"
            ]

            row[
                f"{prefix}_top_driver_variance"
            ] = item[
                "top_driver_variance"
            ]

            row[
                f"{prefix}_price_status"
            ] = item[
                "price_status"
            ]

            row[
                f"{prefix}_volume_status"
            ] = item[
                "volume_status"
            ]

            row[
                f"{prefix}_mix_status"
            ] = item[
                "mix_status"
            ]

        rows.append(row)

    result = pd.DataFrame(rows)

    return (
        result
        .sort_values("period")
        .drop_duplicates(
            "period",
            keep="last",
        )
        .reset_index(drop=True)
    )


# ============================================================
# REVENUE PREDICTION
# ============================================================

def prepare_revenue_prediction(
    df: pd.DataFrame,
    actual_cutoff: pd.Timestamp,
) -> pd.DataFrame:
    """
    Prepare Revenue ML prediction.

    Expected source:
        period
        predicted_revenue
        lower_bound
        upper_bound
        validation_rmse

    Revenue is normalized to positive management convention.
    """

    if df.empty:
        return pd.DataFrame()

    required = {
        "period",
        "predicted_revenue",
        "lower_bound",
        "upper_bound",
        "validation_rmse",
    }

    missing = required - set(df.columns)

    if missing:
        logger.warning(
            "Revenue prediction missing columns: %s",
            ", ".join(sorted(missing)),
        )
        return pd.DataFrame()

    result = df[
        [
            "period",
            "predicted_revenue",
            "lower_bound",
            "upper_bound",
            "validation_rmse",
        ]
    ].copy()

    # --------------------------------------------------------
    # FUTURE ONLY
    # --------------------------------------------------------

    result = result[
        result["period"] > actual_cutoff
    ].copy()

    if result.empty:
        logger.warning(
            "Revenue prediction contains no periods after "
            "actual cutoff."
        )
        return pd.DataFrame()

    # --------------------------------------------------------
    # NUMERIC
    # --------------------------------------------------------

    for column in [
        "predicted_revenue",
        "lower_bound",
        "upper_bound",
        "validation_rmse",
    ]:
        result[column] = pd.to_numeric(
            result[column],
            errors="coerce",
        )

    if result[
        [
            "predicted_revenue",
            "lower_bound",
            "upper_bound",
            "validation_rmse",
        ]
    ].isna().any().any():
        raise RuntimeError(
            "Revenue prediction contains invalid numeric values."
        )

    # --------------------------------------------------------
    # MANAGEMENT SIGN
    # --------------------------------------------------------

    result["ml_predicted_revenue"] = (
        result["predicted_revenue"].abs()
    )

    result["ml_revenue_lower_bound"] = (
        result["lower_bound"].abs()
    )

    result["ml_revenue_upper_bound"] = (
        result["upper_bound"].abs()
    )

    result["revenue_prediction_rmse"] = (
        result["validation_rmse"]
    )

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    invalid_interval = (
        result[
            "ml_revenue_lower_bound"
        ]
        >
        result[
            "ml_revenue_upper_bound"
        ]
    )

    if invalid_interval.any():
        raise RuntimeError(
            "Revenue prediction interval is invalid "
            "after sign normalization."
        )

    # --------------------------------------------------------
    # ONE ROW PER PERIOD
    # --------------------------------------------------------

    result = (
        result[
            [
                "period",
                "revenue_prediction_rmse",
                "ml_predicted_revenue",
                "ml_revenue_lower_bound",
                "ml_revenue_upper_bound",
            ]
        ]
        .sort_values("period")
        .drop_duplicates(
            "period",
            keep="last",
        )
        .reset_index(drop=True)
    )

    logger.info(
        "Revenue prediction prepared: %s forecast periods.",
        len(result),
    )

    return result


# ============================================================
# CASH FLOW PREDICTION
# ============================================================

def prepare_cash_prediction(
    df: pd.DataFrame,
    actual_cutoff: pd.Timestamp,
) -> pd.DataFrame:
    """
    Prepare Cash Flow ML prediction.
    """

    if df.empty:
        return pd.DataFrame()

    required = {
        "period",
        "predicted_operating_cash_flow",
        "predicted_closing_cash",
        "ocf_lower_bound",
        "ocf_upper_bound",
        "cash_lower_bound",
        "cash_upper_bound",
        "validation_rmse",
        "validation_mape_pct",
    }

    missing = required - set(df.columns)

    if missing:
        logger.warning(
            "Cash prediction missing columns: %s",
            ", ".join(sorted(missing)),
        )
        return pd.DataFrame()

    result = df[
        [
            "period",
            "predicted_operating_cash_flow",
            "predicted_closing_cash",
            "ocf_lower_bound",
            "ocf_upper_bound",
            "cash_lower_bound",
            "cash_upper_bound",
            "validation_rmse",
            "validation_mape_pct",
        ]
    ].copy()

    result = result[
        result["period"] > actual_cutoff
    ].copy()

    if result.empty:
        logger.warning(
            "Cash prediction contains no periods after "
            "actual cutoff."
        )
        return pd.DataFrame()

    # --------------------------------------------------------
    # NUMERIC
    # --------------------------------------------------------

    numeric_columns = [
        "predicted_operating_cash_flow",
        "predicted_closing_cash",
        "ocf_lower_bound",
        "ocf_upper_bound",
        "cash_lower_bound",
        "cash_upper_bound",
        "validation_rmse",
        "validation_mape_pct",
    ]

    for column in numeric_columns:
        result[column] = pd.to_numeric(
            result[column],
            errors="coerce",
        )

    if result[numeric_columns].isna().any().any():
        raise RuntimeError(
            "Cash prediction contains invalid numeric values."
        )

    # --------------------------------------------------------
    # RENAME
    # --------------------------------------------------------

    result = result.rename(
        columns={
            "predicted_operating_cash_flow":
                "ml_predicted_operating_cf",

            "predicted_closing_cash":
                "ml_predicted_closing_cash",

            "ocf_lower_bound":
                "ml_ocf_lower_bound",

            "ocf_upper_bound":
                "ml_ocf_upper_bound",

            "cash_lower_bound":
                "ml_cash_lower_bound",

            "cash_upper_bound":
                "ml_cash_upper_bound",

            "validation_rmse":
                "cash_prediction_rmse",

            "validation_mape_pct":
                "cash_prediction_mape_pct",
        }
    )

    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    result = (
        result
        .sort_values("period")
        .drop_duplicates(
            "period",
            keep="last",
        )
        .reset_index(drop=True)
    )

    logger.info(
        "Cash prediction prepared: %s forecast periods.",
        len(result),
    )

    return result


# ============================================================
# CLASSIFICATION
# ============================================================

def prepare_classification(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Prepare financial classification predictions."""

    if df.empty:
        return pd.DataFrame()

    if "period" not in df.columns:
        return pd.DataFrame()

    return (
        df
        .sort_values("period")
        .drop_duplicates(
            "period",
            keep="last",
        )
        .reset_index(drop=True)
    )


# ============================================================
# SAFE MERGE
# ============================================================

def safe_merge(
    base: pd.DataFrame,
    dataset: pd.DataFrame,
    dataset_name: str,
) -> pd.DataFrame:
    """
    Perform validated one-to-one monthly merge.
    """

    if dataset.empty:
        return base

    if "period" not in dataset.columns:
        logger.warning(
            "Skipping %s because period is missing.",
            dataset_name,
        )
        return base

    duplicate_mask = (
        dataset["period"]
        .duplicated(
            keep=False
        )
    )

    if duplicate_mask.any():

        duplicates = (
            dataset.loc[
                duplicate_mask,
                "period",
            ]
            .dt.strftime("%Y-%m")
            .unique()
            .tolist()
        )

        raise RuntimeError(
            f"Dataset '{dataset_name}' contains duplicate "
            f"periods: {duplicates}"
        )

    logger.info(
        "Merging %s: %s rows.",
        dataset_name,
        len(dataset),
    )

    return base.merge(
        dataset,
        on="period",
        how="left",
        validate="one_to_one",
    )


# ============================================================
# FORECAST HORIZON
# ============================================================

def validate_forecast_horizon(
    reporting: pd.DataFrame,
    actual_cutoff: pd.Timestamp,
) -> None:
    """Validate six consecutive future forecast months."""

    future = reporting[
        (
            reporting["period"]
            > actual_cutoff
        )
        &
        (
            reporting["reporting_data_type"]
            == "FORECAST"
        )
    ]

    future_periods = (
        future["period"]
        .drop_duplicates()
        .sort_values()
        .reset_index(drop=True)
    )

    if future_periods.empty:
        raise RuntimeError(
            "No FORECAST periods found."
        )

    horizon = len(
        future_periods
    )

    logger.info(
        "Final forecast horizon: %s months.",
        horizon,
    )

    if horizon != EXPECTED_FORECAST_HORIZON:
        raise RuntimeError(
            "Invalid forecast horizon: "
            f"expected {EXPECTED_FORECAST_HORIZON}, "
            f"found {horizon}."
        )

    expected = pd.Series(
        pd.date_range(
            start=future_periods.iloc[0],
            periods=EXPECTED_FORECAST_HORIZON,
            freq="MS",
        )
    )

    if not future_periods.equals(
        expected
    ):
        raise RuntimeError(
            "Forecast periods are not consecutive."
        )


# ============================================================
# PREDICTION COMPLETENESS
# ============================================================

def validate_forecast_prediction_completeness(
    reporting: pd.DataFrame,
    actual_cutoff: pd.Timestamp,
) -> None:
    """
    Validate that ML forecast layers contain all future months.

    Required:
        Revenue prediction
        Expense prediction
        Cash prediction
    """

    future = (
        reporting[
            reporting["period"] > actual_cutoff
        ]
        .sort_values("period")
        .reset_index(drop=True)
    )

    if future.empty:
        raise RuntimeError(
            "No future forecast periods available."
        )

    required_columns = {
        "Revenue": "ml_predicted_revenue",
        "Expense": "ml_predicted_operating_costs",
        "Cash": "ml_predicted_operating_cf",
    }

    missing_layers = []

    for layer_name, column_name in required_columns.items():

        if column_name not in reporting.columns:
            missing_layers.append(
                f"{layer_name} ({column_name})"
            )
            continue

        missing_mask = (
            future[column_name]
            .isna()
        )

        if missing_mask.any():
            missing_periods = (
                future.loc[
                    missing_mask,
                    "period",
                ]
                .dt.strftime("%Y-%m")
                .tolist()
            )

            missing_layers.append(
                f"{layer_name}: "
                + ", ".join(missing_periods)
            )

    if missing_layers:
        raise RuntimeError(
            "Forecast prediction completeness validation "
            "failed: "
            + " | ".join(missing_layers)
        )

    logger.info(
        "Forecast prediction completeness validation passed."
    )


# ============================================================
# SEMANTIC CLEANUP
# ============================================================

def clear_context_specific_metrics(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Clear metrics that do not semantically apply to
    ACTUAL or FORECAST months.
    """

    result = df.copy()

    forecast_mask = (
        result["reporting_data_type"]
        == "FORECAST"
    )

    actual_mask = (
        result["reporting_data_type"]
        == "ACTUAL"
    )

    # --------------------------------------------------------
    # Historical-only metrics
    # --------------------------------------------------------

    historical_only_columns = [
        column
        for column in result.columns
        if (
            "_root_cause_" in column
            or "_pvm_" in column
            or column.startswith("anomaly_")
        )
    ]

    if historical_only_columns:
        result.loc[
            forecast_mask,
            historical_only_columns,
        ] = pd.NA

    # --------------------------------------------------------
    # Forecast-only ML metrics
    # --------------------------------------------------------

    prediction_columns = [
        column
        for column in result.columns
        if (
            column.startswith("ml_")
            or column.endswith(
                "_prediction_rmse"
            )
            or column.endswith(
                "_prediction_mape_pct"
            )
        )
    ]

    if prediction_columns:
        result.loc[
            actual_mask,
            prediction_columns,
        ] = pd.NA

    # --------------------------------------------------------
    # Expense magnitude is ML-only too.
    # --------------------------------------------------------

    if (
        "ml_predicted_expense_magnitude"
        in result.columns
    ):
        result.loc[
            actual_mask,
            "ml_predicted_expense_magnitude",
        ] = pd.NA

    return result


# ============================================================
# BUILD FINAL DATASET
# ============================================================

def build_reporting_dataset(
    sources: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Build the complete Power BI reporting dataset."""

    # --------------------------------------------------------
    # ACTUAL CUTOFF
    # --------------------------------------------------------

    actual_cutoff = (
        determine_actual_cutoff(
            sources[
                "controller_timeseries"
            ]
        )
    )

    # --------------------------------------------------------
    # MONTHLY CALENDAR
    # --------------------------------------------------------

    result = build_monthly_calendar(
        sources,
        actual_cutoff,
    )

    # --------------------------------------------------------
    # PREPARE DATASETS
    # --------------------------------------------------------

    rolling = (
        prepare_rolling_forecast(
            sources[
                "rolling_forecast"
            ]
        )
    )

    expense_prediction = (
        prepare_expense_prediction(
            sources[
                "expense_forecast"
            ],
            actual_cutoff,
        )
    )

    anomaly = (
        prepare_anomaly(
            sources["anomaly"]
        )
    )

    variance = (
        prepare_variance(
            sources["variance"]
        )
    )

    pvm = (
        prepare_pvm(
            sources["pvm"]
        )
    )

    revenue_prediction = (
        prepare_revenue_prediction(
            sources[
                "revenue_prediction"
            ],
            actual_cutoff,
        )
    )

    cash_prediction = (
        prepare_cash_prediction(
            sources[
                "cash_prediction"
            ],
            actual_cutoff,
        )
    )

    classification = (
        prepare_classification(
            sources[
                "classification"
            ]
        )
    )

    # --------------------------------------------------------
    # SAFE MERGES
    # --------------------------------------------------------

    result = safe_merge(
        result,
        rolling,
        "rolling_forecast",
    )

    result = safe_merge(
        result,
        anomaly,
        "anomaly",
    )

    result = safe_merge(
        result,
        variance,
        "variance",
    )

    result = safe_merge(
        result,
        pvm,
        "pvm",
    )

    result = safe_merge(
        result,
        revenue_prediction,
        "revenue_prediction",
    )

    result = safe_merge(
        result,
        expense_prediction,
        "expense_forecast",
    )

    result = safe_merge(
        result,
        cash_prediction,
        "cash_prediction",
    )

    result = safe_merge(
        result,
        classification,
        "classification",
    )

    # --------------------------------------------------------
    # CONTEXT CLEANUP
    # --------------------------------------------------------

    result = clear_context_specific_metrics(
        result
    )

    # --------------------------------------------------------
    # FORECAST VALIDATION
    # --------------------------------------------------------

    validate_forecast_horizon(
        result,
        actual_cutoff,
    )

    validate_forecast_prediction_completeness(
        result,
        actual_cutoff,
    )

    # --------------------------------------------------------
    # FINAL SORT
    # --------------------------------------------------------

    result = (
        result
        .sort_values("period")
        .reset_index(drop=True)
    )

    # --------------------------------------------------------
    # FINAL GRAIN VALIDATION
    # --------------------------------------------------------

    if result["period"].duplicated().any():
        raise RuntimeError(
            "Final dataset contains duplicate months."
        )

    return result


# ============================================================
# SIGN CONVENTION VALIDATION
# ============================================================

def validate_sign_convention(
    df: pd.DataFrame,
) -> None:
    """Validate management sign conventions."""

    forecast = df[
        df["reporting_data_type"]
        == "FORECAST"
    ].copy()

    if forecast.empty:
        return

    # --------------------------------------------------------
    # Revenue
    # --------------------------------------------------------

    revenue = forecast.get(
        "rolling_revenue",
        pd.Series(dtype=float),
    ).dropna()

    if not revenue.empty and (
        revenue < 0
    ).any():
        raise RuntimeError(
            "Rolling revenue contains negative values "
            "after sign normalization."
        )

    ml_revenue = forecast.get(
        "ml_predicted_revenue",
        pd.Series(dtype=float),
    ).dropna()

    if not ml_revenue.empty and (
        ml_revenue < 0
    ).any():
        raise RuntimeError(
            "ML revenue prediction contains negative values."
        )

    # --------------------------------------------------------
    # Rolling operating costs
    # --------------------------------------------------------

    costs = forecast.get(
        "rolling_operating_costs",
        pd.Series(dtype=float),
    ).dropna()

    if not costs.empty and (
        costs > 0
    ).any():
        raise RuntimeError(
            "Rolling operating costs contain positive values "
            "after sign normalization."
        )

    # --------------------------------------------------------
    # ML operating costs
    # --------------------------------------------------------

    ml_costs = forecast.get(
        "ml_predicted_operating_costs",
        pd.Series(dtype=float),
    ).dropna()

    if not ml_costs.empty and (
        ml_costs > 0
    ).any():
        raise RuntimeError(
            "ML operating costs contain positive values "
            "after sign normalization."
        )

    logger.info(
        "Management sign convention validation passed."
    )


# ============================================================
# FORECAST SAMPLE LOGGING
# ============================================================

def log_forecast_samples(
    df: pd.DataFrame,
) -> None:
    """Log forecast samples for manual validation."""

    forecast = (
        df[
            df["reporting_data_type"]
            == "FORECAST"
        ]
        .sort_values("period")
        .reset_index(drop=True)
    )

    if forecast.empty:
        return

    if {
        "period",
        "ml_predicted_revenue",
        "ml_revenue_lower_bound",
        "ml_revenue_upper_bound",
    }.issubset(forecast.columns):

        logger.info(
            "Forecast revenue sample:\n%s",
            forecast[
                [
                    "period",
                    "ml_predicted_revenue",
                    "ml_revenue_lower_bound",
                    "ml_revenue_upper_bound",
                ]
            ].to_string(index=False),
        )

    if {
        "period",
        "ml_predicted_expense_magnitude",
        "ml_predicted_operating_costs",
    }.issubset(forecast.columns):

        logger.info(
            "Forecast expense sample:\n%s",
            forecast[
                [
                    "period",
                    "ml_predicted_expense_magnitude",
                    "ml_predicted_operating_costs",
                ]
            ].to_string(index=False),
        )

    if {
        "period",
        "ml_predicted_operating_cf",
        "ml_predicted_closing_cash",
    }.issubset(forecast.columns):

        logger.info(
            "Forecast cash sample:\n%s",
            forecast[
                [
                    "period",
                    "ml_predicted_operating_cf",
                    "ml_predicted_closing_cash",
                ]
            ].to_string(index=False),
        )


# ============================================================
# FINAL LOGGING
# ============================================================

def log_final_validation(
    df: pd.DataFrame,
) -> None:
    """Log final dataset structure."""

    actual_count = int(
        (
            df["reporting_data_type"]
            == "ACTUAL"
        ).sum()
    )

    forecast_count = int(
        (
            df["reporting_data_type"]
            == "FORECAST"
        ).sum()
    )

    logger.info(
        "Final rows: %s",
        len(df),
    )

    logger.info(
        "ACTUAL rows: %s",
        actual_count,
    )

    logger.info(
        "FORECAST rows: %s",
        forecast_count,
    )

    logger.info(
        "First period: %s",
        df["period"].min().strftime(
            "%Y-%m"
        ),
    )

    logger.info(
        "Last period: %s",
        df["period"].max().strftime(
            "%Y-%m"
        ),
    )


# ============================================================
# SAVE
# ============================================================

def save_output(
    df: pd.DataFrame,
) -> None:
    """Save final Power BI reporting dataset."""

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    logger.info(
        "Power BI reporting export saved to %s",
        OUTPUT_FILE,
    )


# ============================================================
# MAIN
# ============================================================

def main() -> int:
    """Run the EFAP Power BI reporting export."""

    try:

        logger.info(
            "Starting EFAP Power BI Analytics Export."
        )

        # ----------------------------------------------------
        # LOAD
        # ----------------------------------------------------

        sources = load_all_sources()

        # ----------------------------------------------------
        # BUILD
        # ----------------------------------------------------

        reporting = build_reporting_dataset(
            sources
        )

        if reporting.empty:
            raise RuntimeError(
                "Final reporting dataset is empty."
            )

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        validate_sign_convention(
            reporting
        )

        # ----------------------------------------------------
        # DEBUG / QA SAMPLES
        # ----------------------------------------------------

        log_forecast_samples(
            reporting
        )

        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        save_output(
            reporting
        )

        # ----------------------------------------------------
        # FINAL VALIDATION
        # ----------------------------------------------------

        log_final_validation(
            reporting
        )

        logger.info(
            "EFAP Power BI Analytics Export "
            "completed successfully."
        )

        return 0

    except Exception as exc:

        logger.exception(
            "Power BI Analytics Export failed: %s",
            exc,
        )

        return 1


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    raise SystemExit(
        main()
    )