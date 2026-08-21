"""
EFAP - Power BI Analytics Reporting Export

Object:
    Python/reporting/build_powerbi_analytics_export.py

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

    if df.empty:
        return df

    result = df.copy()

    if "period" in result.columns:

        result["period"] = pd.to_datetime(
            result["period"],
            errors="coerce",
        )

    return result


# ============================================================
# LOAD ALL SOURCES
# ============================================================

def load_all_sources() -> dict[str, pd.DataFrame]:

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

        "expense_prediction":
            normalize_period(
                load_optional_csv(
                    PREDICTION_DIR
                    / "expense_prediction.csv",
                    "Expense ML prediction",
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

    if "period" not in controller_timeseries.columns:

        raise ValueError(
            "Controller KPI time series is missing "
            "'period'."
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
            "No valid periods found in controller "
            "KPI time series."
        )

    cutoff = periods.max()

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

    calendar["year_month"] = (
        calendar["period"]
        .dt.strftime("%Y-%m")
    )

    calendar["calendar_year"] = (
        calendar["period"].dt.year
    )

    calendar["calendar_month"] = (
        calendar["period"].dt.month
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

    if df.empty:
        return pd.DataFrame()

    required = {
        "period",
        "data_type",
        "forecast_horizon_month",
        "revenue",
        "operating_costs",
    }

    missing = (
        required
        - set(df.columns)
    )

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

    # --------------------------------------------------------
    # MANAGEMENT SIGN CONVENTION
    # --------------------------------------------------------
    #
    # Revenue:
    #     always positive
    #
    # Operating Costs:
    #     always negative
    #
    # EBITDA:
    #     Revenue + Operating Costs
    #
    # This deliberately normalizes the source forecast rather
    # than copying an inconsistent sign convention downstream.
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
            result["rolling_revenue"]
            .replace(0, pd.NA)
        )
        * 100
    )

    result = result[
        [
            "period",
            "data_type",
            "forecast_horizon_month",
            "rolling_revenue",
            "rolling_operating_costs",
            "rolling_ebitda",
            "rolling_ebitda_margin",
        ]
    ].rename(
        columns={
            "data_type":
                "rolling_data_type",
        }
    )

    result = (
        result
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
# ANOMALY
# ============================================================

def prepare_anomaly(
    df: pd.DataFrame,
) -> pd.DataFrame:

    if df.empty:
        return pd.DataFrame()

    required = {
        "period",
        "anomaly_count",
        "high_or_critical_count",
        "max_severity",
        "controller_status",
    }

    missing = (
        required
        - set(df.columns)
    )

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

    missing = (
        required
        - set(df.columns)
    )

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

    missing = (
        required
        - set(df.columns)
    )

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
) -> pd.DataFrame:
    """
    Prepare revenue ML prediction and normalize it to the
    EFAP management sign convention.

    Source structure:
        forecast_period
        forecast_revenue
        lower_bound
        upper_bound
        model
        validation_rmse
        forecast_year
        forecast_month
        year_month

    Source convention:
        Revenue is negative.

    Management convention:
        Revenue is positive.

    Important:
        Because the source interval is negative, lower/upper
        bounds must be reversed after sign normalization.
    """

    if df.empty:
        return pd.DataFrame()

    logger.info(
    "Revenue prediction source columns: %s",
    list(df.columns),
    )

    logger.info(
        "Revenue prediction source rows: %s",
        len(df),
    )

    # --------------------------------------------------------
    # Expected source columns
    # --------------------------------------------------------

    required = {
        "period",
        "predicted_revenue",
        "lower_bound",
        "upper_bound",
        "validation_rmse",
    }

    missing = (
        required
        - set(df.columns)
    )

    if missing:

        logger.warning(
            "Revenue prediction missing columns: %s",
            ", ".join(sorted(missing)),
        )

        return pd.DataFrame()

    # --------------------------------------------------------
    # Prepare source data
    # --------------------------------------------------------

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
    # Normalize period
    # --------------------------------------------------------

    result["period"] = pd.to_datetime(
        result["period"],
        errors="coerce",
    )

    # Remove invalid / empty source rows
    result = result[
        result["period"].notna()
    ].copy()

    if result.empty:
        return pd.DataFrame()

    # --------------------------------------------------------
    # Revenue prediction
    #
    # Source:
    #   -7,537,122.84
    #
    # Management:
    #   +7,537,122.84
    # --------------------------------------------------------

    result["ml_predicted_revenue"] = (
        result["predicted_revenue"]
        .abs()
    )

    result["ml_revenue_lower_bound"] = (
        result["lower_bound"]
        .abs()
    )

    result["ml_revenue_upper_bound"] = (
        result["upper_bound"]
        .abs()
    )

    # --------------------------------------------------------
    # Validation metric
    # --------------------------------------------------------

    result["revenue_prediction_rmse"] = (
        result["validation_rmse"]
    )

    # --------------------------------------------------------
    # Keep only reporting columns
    # --------------------------------------------------------

    result = result[
        [
            "period",
            "revenue_prediction_rmse",
            "ml_predicted_revenue",
            "ml_revenue_lower_bound",
            "ml_revenue_upper_bound",
        ]
    ].copy()

    # --------------------------------------------------------
    # Defensive validation
    # --------------------------------------------------------

    invalid_interval = (
        result["ml_revenue_lower_bound"]
        >
        result["ml_revenue_upper_bound"]
    )

    if invalid_interval.any():

        logger.warning(
            "Revenue prediction contains invalid "
            "prediction intervals."
        )

        raise RuntimeError(
            "Revenue prediction interval is invalid "
            "after sign normalization."
        )

    # --------------------------------------------------------
    # One row per forecast period
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
        "Revenue prediction prepared: %s forecast periods.",
        len(result),
    )

    return result

    # --------------------------------------------------------
    # Rename source columns
    # --------------------------------------------------------

    result = result.rename(
        columns={
            "predicted_revenue":
                "_source_revenue",

            "lower_bound":
                "_source_lower_bound",

            "upper_bound":
                "_source_upper_bound",

            "validation_rmse":
                "revenue_prediction_rmse",
        }
    )

    # --------------------------------------------------------
    # Normalize revenue sign
    #
    # Source:
    #     forecast_revenue < 0
    #
    # Management:
    #     revenue > 0
    # --------------------------------------------------------

    result["ml_predicted_revenue"] = (
        result["_source_revenue"]
        .abs()
    )

    # --------------------------------------------------------
    # Normalize prediction interval.
    # --------------------------------------------------------

    result["ml_revenue_lower_bound"] = (
        result["_source_lower_bound"]
        .abs()
    )

    result["ml_revenue_upper_bound"] = (
        result["_source_upper_bound"]
        .abs()
    )

    # --------------------------------------------------------
    # Remove temporary source columns
    # --------------------------------------------------------

    result = result.drop(
        columns=[
            "_source_revenue",
            "_source_lower_bound",
            "_source_upper_bound",
        ]
    )

    # --------------------------------------------------------
    # Defensive validation
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
            "Revenue prediction interval is invalid after "
            "sign normalization."
        )

    # --------------------------------------------------------
    # One row per forecast period
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

    return result

# ============================================================
# EXPENSE PREDICTION
# ============================================================

def prepare_expense_prediction(
    df: pd.DataFrame,
) -> pd.DataFrame:

    if df.empty:
        return pd.DataFrame()

    required = {
        "period",
        "predicted_expense",
        "lower_bound",
        "upper_bound",
        "validation_rmse",
    }

    missing = (
        required
        - set(df.columns)
    )

    if missing:

        logger.warning(
            "Expense prediction missing columns: %s",
            ", ".join(sorted(missing)),
        )

        return pd.DataFrame()

    result = (
        df
        .groupby(
            "period",
            as_index=False,
        )
        .agg(
            ml_predicted_expense_magnitude=(
                "predicted_expense",
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
    # Management signed values
    # --------------------------------------------------------

    result[
        "ml_predicted_operating_costs"
    ] = (
        -result[
            "ml_predicted_expense_magnitude"
        ].abs()
    )

    result[
        "ml_expense_lower_bound"
    ] = (
        -result[
            "ml_expense_upper_bound_magnitude"
        ].abs()
    )

    result[
        "ml_expense_upper_bound"
    ] = (
        -result[
            "ml_expense_lower_bound_magnitude"
        ].abs()
    )

    return (
        result
        .drop(
            columns=[
                "ml_expense_lower_bound_magnitude",
                "ml_expense_upper_bound_magnitude",
            ]
        )
        .sort_values("period")
        .reset_index(drop=True)
    )


# ============================================================
# CASH FLOW PREDICTION
# ============================================================

def prepare_cash_prediction(
    df: pd.DataFrame,
) -> pd.DataFrame:

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

    missing = (
        required
        - set(df.columns)
    )

    if missing:

        logger.warning(
            "Cash prediction missing columns: %s",
            ", ".join(sorted(missing)),
        )

        return pd.DataFrame()

    result = (
        df[
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
        ]
        .rename(
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
        .sort_values("period")
        .drop_duplicates(
            "period",
            keep="last",
        )
        .reset_index(drop=True)
    )

    return result


# ============================================================
# CLASSIFICATION
# ============================================================

def prepare_classification(
    df: pd.DataFrame,
) -> pd.DataFrame:

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
# SEMANTIC CLEANUP
# ============================================================

def clear_context_specific_metrics(
    df: pd.DataFrame,
) -> pd.DataFrame:

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
    # ML prediction metrics
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

    return result


# ============================================================
# BUILD FINAL DATASET
# ============================================================

def build_reporting_dataset(
    sources: dict[str, pd.DataFrame],
) -> pd.DataFrame:

    actual_cutoff = (
        determine_actual_cutoff(
            sources[
                "controller_timeseries"
            ]
        )
    )

    result = build_monthly_calendar(
        sources,
        actual_cutoff,
    )

    # --------------------------------------------------------
    # Prepare datasets
    # --------------------------------------------------------

    rolling = (
        prepare_rolling_forecast(
            sources[
                "rolling_forecast"
            ]
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
            ]
        )
    )

    expense_prediction = (
        prepare_expense_prediction(
            sources[
                "expense_prediction"
            ]
        )
    )

    cash_prediction = (
        prepare_cash_prediction(
            sources[
                "cash_prediction"
            ]
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
    # Safe merges
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
        "expense_prediction",
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
    # Context cleanup
    # --------------------------------------------------------

    result = clear_context_specific_metrics(
        result
    )

    # --------------------------------------------------------
    # Forecast validation
    # --------------------------------------------------------

    validate_forecast_horizon(
        result,
        actual_cutoff,
    )

    # --------------------------------------------------------
    # Final sorting
    # --------------------------------------------------------

    result = (
        result
        .sort_values("period")
        .reset_index(drop=True)
    )

    # --------------------------------------------------------
    # Final grain validation
    # --------------------------------------------------------

    if result["period"].duplicated().any():

        raise RuntimeError(
            "Final dataset contains duplicate months."
        )

    return result


# ============================================================
# FINAL VALIDATION
# ============================================================

def validate_sign_convention(
    df: pd.DataFrame,
) -> None:

    forecast = df[
        df["reporting_data_type"]
        == "FORECAST"
    ].copy()

    if forecast.empty:
        return

    # Revenue should be positive.
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

    # Operating costs should be negative.
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


def log_final_validation(
    df: pd.DataFrame,
) -> None:

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

    try:

        logger.info(
            "Starting EFAP Power BI Analytics Export."
        )

        sources = load_all_sources()

        reporting = build_reporting_dataset(
            sources
        )

        if reporting.empty:

            raise RuntimeError(
                "Final reporting dataset is empty."
            )

        validate_sign_convention(
            reporting
        )

        save_output(
            reporting
        )

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


if __name__ == "__main__":
    raise SystemExit(
        main()
    )