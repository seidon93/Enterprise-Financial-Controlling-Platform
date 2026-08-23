"""
EFAP - Power BI Analytics Reporting Export

Object:
    Scripts/Python/build_powerbi_analytics_export.py

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

QA guarantees:
    - Exactly one row per calendar month
    - ACTUAL / FORECAST split is authoritative
    - Exactly six consecutive forecast months
    - Revenue / Expense / Cash forecast horizons must match
    - ACTUAL rows cannot contain ML forecast metrics
    - FORECAST rows cannot contain historical-only metrics
    - Management sign conventions are validated
    - Forecast prediction intervals are validated
    - Forecast metadata is preserved
    - Cash Flow forecast selection reason is preserved
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd


# ============================================================
# PROJECT ROOT RESOLUTION
# ============================================================

def resolve_project_root() -> Path:
    """
    Resolve the EFAP project root dynamically.

    The script location is not assumed to be at a fixed depth.
    The root is identified by expected project directories.
    """

    script_path = (
        Path(__file__)
        .resolve()
    )

    candidates = [
        script_path.parent,
        *script_path.parents,
    ]

    for candidate in candidates:

        required_directories = {
            "data",
            "Scripts",
        }

        if all(
            (
                candidate / directory
            ).is_dir()
            for directory
            in required_directories
        ):

            return candidate

    raise RuntimeError(
        "Unable to resolve EFAP project root.\n"
        f"Script location: {script_path}\n"
        "Expected project root to contain:\n"
        "  - data\\\n"
        "  - Scripts\\\n"
    )


PROJECT_ROOT = (
    resolve_project_root()
)


# ============================================================
# PATHS
# ============================================================

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
# FILE VALIDATION
# ============================================================

def validate_files() -> None:
    """
    Validate mandatory source files before processing.

    Required:
        controller KPI time series
        revenue prediction
        expense forecast

    Cash Flow prediction is also required because the final
    Power BI export must contain a complete Cash ML layer.
    """

    required_files = {
        "controller KPI time series":
            CONTROLLER_TIMESERIES_FILE,

        "revenue prediction":
            PREDICTION_DIR
            / "revenue_prediction.csv",

        "expense forecast":
            FORECAST_DIR
            / "expense_forecast.csv",

        "cash flow prediction":
            PREDICTION_DIR
            / "cash_flow_prediction.csv",
    }

    missing = []

    for name, path in required_files.items():

        if not path.exists():

            missing.append(
                f"{name}: {path}"
            )

    if missing:

        raise FileNotFoundError(
            "Missing required files:\n"
            + "\n".join(missing)
        )

    logger.info(
        "Required source file validation passed."
    )

    logger.info(
        "EFAP project root: %s",
        PROJECT_ROOT,
    )


# ============================================================
# FILE LOADING
# ============================================================

def load_required_csv(
    path: Path,
    dataset_name: str,
) -> pd.DataFrame:
    """
    Load a required CSV dataset.
    """

    if not path.exists():

        raise FileNotFoundError(
            f"{dataset_name} not found: {path}"
        )

    logger.info(
        "Loading %s: %s",
        dataset_name,
        path,
    )

    df = pd.read_csv(
        path
    )

    if df.empty:

        raise ValueError(
            f"{dataset_name} is empty: {path}"
        )

    return df


def load_optional_csv(
    path: Path,
    dataset_name: str,
) -> pd.DataFrame:
    """
    Load an optional CSV dataset.
    """

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

    df = pd.read_csv(
        path
    )

    if df.empty:

        logger.warning(
            "%s exists but contains no rows: %s",
            dataset_name,
            path,
        )

    return df


def normalize_period(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Normalize period column to monthly-start timestamp.

    All reporting sources must use the same monthly key.
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
                load_required_csv(
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
                load_required_csv(
                    PREDICTION_DIR
                    / "revenue_prediction.csv",
                    "Revenue ML prediction",
                )
            ),

        "cash_prediction":
            normalize_period(
                load_required_csv(
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
    Determine the authoritative last actual financial month.
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
    Build complete monthly reporting calendar.

    Grain:
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

        periods.extend(
            values
        )

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
        .dropna(
            subset=["period"]
        )
        .drop_duplicates(
            "period"
        )
        .sort_values(
            "period"
        )
        .reset_index(
            drop=True
        )
    )

    calendar["year_month"] = (
        calendar["period"]
        .dt.strftime(
            "%Y-%m"
        )
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

    missing = (
        required
        - set(df.columns)
    )

    if missing:

        logger.warning(
            "Rolling forecast missing columns: %s",
            ", ".join(
                sorted(missing)
            ),
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

    numeric_columns = [
        "revenue",
        "operating_costs",
        "forecast_horizon_month",
    ]

    for column in numeric_columns:

        result[column] = pd.to_numeric(
            result[column],
            errors="coerce",
        )

    # --------------------------------------------------------
    # MANAGEMENT SIGN CONVENTION
    # --------------------------------------------------------

    result[
        "rolling_revenue"
    ] = (
        result[
            "revenue"
        ].abs()
    )

    result[
        "rolling_operating_costs"
    ] = (
        -result[
            "operating_costs"
        ].abs()
    )

    result[
        "rolling_ebitda"
    ] = (
        result[
            "rolling_revenue"
        ]
        +
        result[
            "rolling_operating_costs"
        ]
    )

    result[
        "rolling_ebitda_margin"
    ] = (
        result[
            "rolling_ebitda"
        ]
        .div(
            result[
                "rolling_revenue"
            ].replace(
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
        .reset_index(
            drop=True
        )
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

    Source grain:
        Account + month

    Target grain:
        One row per forecast month
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

    missing = (
        required
        - set(df.columns)
    )

    if missing:

        raise RuntimeError(
            "Expense forecast missing columns: "
            + ", ".join(
                sorted(missing)
            )
        )

    result = df.copy()

    result["period"] = (
        pd.to_datetime(
            result["forecast_period"],
            errors="coerce",
        )
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    if result[
        "period"
    ].isna().any():

        raise RuntimeError(
            "Expense forecast contains invalid "
            "forecast_period values."
        )

    result = result[
        result["period"]
        >
        actual_cutoff
    ].copy()

    if result.empty:

        logger.warning(
            "Expense forecast contains no future periods."
        )

        return pd.DataFrame()

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

    if result[
        numeric_columns
    ].isna().any().any():

        raise RuntimeError(
            "Expense forecast contains invalid numeric values."
        )

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
    # MANAGEMENT SIGN
    # --------------------------------------------------------

    monthly[
        "ml_predicted_operating_costs"
    ] = (
        -monthly[
            "ml_predicted_expense_magnitude"
        ].abs()
    )

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
            "Expense prediction interval is invalid "
            "after sign normalization."
        )

    invalid_costs = (
        monthly[
            "ml_predicted_operating_costs"
        ]
        > 0
    )

    if invalid_costs.any():

        raise RuntimeError(
            "Expense forecast contains positive operating "
            "costs after sign normalization."
        )

    monthly = (
        monthly
        .sort_values(
            "period"
        )
        .reset_index(
            drop=True
        )
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
        ].to_string(
            index=False
        ),
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

    missing = (
        required
        - set(df.columns)
    )

    if missing:

        logger.warning(
            "Anomaly dataset missing columns: %s",
            ", ".join(
                sorted(missing)
            ),
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

    result = df[
        columns
    ].copy()

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
        .sort_values(
            "period"
        )
        .drop_duplicates(
            "period",
            keep="last",
        )
        .reset_index(
            drop=True
        )
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

    missing = (
        required
        - set(df.columns)
    )

    if missing:

        logger.warning(
            "Variance dataset missing columns: %s",
            ", ".join(
                sorted(missing)
            ),
        )

        return pd.DataFrame()

    rows = []

    for period, group in df.groupby(
        "period",
        sort=True,
    ):

        row = {
            "period":
                period
        }

        for _, item in group.iterrows():

            metric = str(
                item["metric"]
            ).lower()

            metric = (
                metric
                .replace(
                    " ",
                    "_",
                )
                .replace(
                    "-",
                    "_",
                )
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

        rows.append(
            row
        )

    result = pd.DataFrame(
        rows
    )

    return (
        result
        .sort_values(
            "period"
        )
        .drop_duplicates(
            "period",
            keep="last",
        )
        .reset_index(
            drop=True
        )
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

    missing = (
        required
        - set(df.columns)
    )

    if missing:

        logger.warning(
            "PVM dataset missing columns: %s",
            ", ".join(
                sorted(missing)
            ),
        )

        return pd.DataFrame()

    rows = []

    for period, group in df.groupby(
        "period",
        sort=True,
    ):

        row = {
            "period":
                period
        }

        for _, item in group.iterrows():

            analysis_type = str(
                item["analysis_type"]
            ).upper()

            if analysis_type == "REVENUE":

                prefix = (
                    "revenue_pvm"
                )

            elif analysis_type in {
                "OPERATING_COST",
                "OPERATING_COSTS",
            }:

                prefix = (
                    "operating_cost_pvm"
                )

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

        rows.append(
            row
        )

    result = pd.DataFrame(
        rows
    )

    return (
        result
        .sort_values(
            "period"
        )
        .drop_duplicates(
            "period",
            keep="last",
        )
        .reset_index(
            drop=True
        )
    )


# ============================================================
# REVENUE ML PREDICTION
# ============================================================

def prepare_revenue_prediction(
    df: pd.DataFrame,
    actual_cutoff: pd.Timestamp,
) -> pd.DataFrame:
    """
    Prepare Revenue ML prediction.

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

    missing = (
        required
        - set(df.columns)
    )

    if missing:

        raise RuntimeError(
            "Revenue prediction missing columns: "
            + ", ".join(
                sorted(missing)
            )
        )

    result = df[
        [
            "period",
            "predicted_revenue",
            "lower_bound",
            "upper_bound",
            "validation_rmse",
        ]
    ].copy()

    result["period"] = (
        pd.to_datetime(
            result["period"],
            errors="coerce",
        )
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    result = result[
        result["period"]
        >
        actual_cutoff
    ].copy()

    if result.empty:

        logger.warning(
            "Revenue prediction contains no future periods."
        )

        return pd.DataFrame()

    numeric_columns = [
        "predicted_revenue",
        "lower_bound",
        "upper_bound",
        "validation_rmse",
    ]

    for column in numeric_columns:

        result[column] = pd.to_numeric(
            result[column],
            errors="coerce",
        )

    if result[
        numeric_columns
    ].isna().any().any():

        raise RuntimeError(
            "Revenue prediction contains invalid numeric values."
        )

    # --------------------------------------------------------
    # MANAGEMENT SIGN
    # --------------------------------------------------------

    result[
        "ml_predicted_revenue"
    ] = (
        result[
            "predicted_revenue"
        ].abs()
    )

    result[
        "ml_revenue_lower_bound"
    ] = (
        result[
            "lower_bound"
        ].abs()
    )

    result[
        "ml_revenue_upper_bound"
    ] = (
        result[
            "upper_bound"
        ].abs()
    )

    result[
        "revenue_prediction_rmse"
    ] = (
        result[
            "validation_rmse"
        ]
    )

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

    invalid_prediction_position = (
        (
            result[
                "ml_predicted_revenue"
            ]
            <
            result[
                "ml_revenue_lower_bound"
            ]
        )
        |
        (
            result[
                "ml_predicted_revenue"
            ]
            >
            result[
                "ml_revenue_upper_bound"
            ]
        )
    )

    if invalid_prediction_position.any():

        raise RuntimeError(
            "Revenue prediction lies outside its "
            "prediction interval."
        )

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
        .sort_values(
            "period"
        )
        .drop_duplicates(
            "period",
            keep="last",
        )
        .reset_index(
            drop=True
        )
    )

    logger.info(
        "Revenue prediction prepared: %s forecast periods.",
        len(result),
    )

    return result


# ============================================================
# CASH FLOW ML PREDICTION
# ============================================================

def prepare_cash_prediction(
    df: pd.DataFrame,
    actual_cutoff: pd.Timestamp,
) -> pd.DataFrame:
    """
    Prepare Cash Flow prediction for Power BI.

    This function supports the current Cash Flow output schema:

        validation_mae
        validation_rmse
        validation_smape_pct
        validation_stabilized_mape_pct
        validation_residual_std
        forecast_interval_width
        prediction_type
        forecast_selection_reason
        forecast_quality
        forecast_confidence
        model
        ml_improvement_vs_baseline

    It intentionally does not require validation_mape_pct,
    because the current Cash Flow generator no longer produces
    that legacy field.
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
        "validation_mae",
        "validation_rmse",
        "validation_smape_pct",
        "validation_stabilized_mape_pct",
        "validation_residual_std",
        "forecast_interval_width",
        "prediction_type",
        "forecast_selection_reason",
        "forecast_quality_status",
        "forecast_confidence",
        "model",
        "ml_improvement_vs_baseline_pct",
    }

    missing = (
        required
        - set(df.columns)
    )

    if missing:

        raise RuntimeError(
            "Cash prediction missing columns: "
            + ", ".join(
                sorted(missing)
            )
        )

    selected_columns = [
        "period",
        "predicted_operating_cash_flow",
        "predicted_closing_cash",
        "ocf_lower_bound",
        "ocf_upper_bound",
        "cash_lower_bound",
        "cash_upper_bound",
        "validation_mae",
        "validation_rmse",
        "validation_smape_pct",
        "validation_stabilized_mape_pct",
        "validation_residual_std",
        "forecast_interval_width",
        "prediction_type",
        "forecast_selection_reason",
        "forecast_quality_status",
        "forecast_confidence",
        "model",
        "ml_improvement_vs_baseline_pct",
    ]

    result = df[
        selected_columns
    ].copy()

    # --------------------------------------------------------
    # PERIOD
    # --------------------------------------------------------

    result["period"] = (
        pd.to_datetime(
            result["period"],
            errors="coerce",
        )
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    if result["period"].isna().any():

        raise RuntimeError(
            "Cash prediction contains invalid period values."
        )

    # --------------------------------------------------------
    # FUTURE ONLY
    # --------------------------------------------------------

    result = result[
        result["period"]
        >
        actual_cutoff
    ].copy()

    if result.empty:

        logger.warning(
            "Cash prediction contains no future periods."
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
        "validation_mae",
        "validation_rmse",
        "validation_smape_pct",
        "validation_stabilized_mape_pct",
        "validation_residual_std",
        "forecast_interval_width",
        "ml_improvement_vs_baseline_pct",
    ]

    for column in numeric_columns:

        result[column] = pd.to_numeric(
            result[column],
            errors="coerce",
        )

    if result[
        numeric_columns
    ].isna().any().any():

        invalid_columns = [
            column
            for column in numeric_columns
            if result[
                column
            ].isna().any()
        ]

        raise RuntimeError(
            "Cash prediction contains invalid numeric values "
            "in columns: "
            + ", ".join(
                invalid_columns
            )
        )

    # --------------------------------------------------------
    # STRING NORMALIZATION
    # --------------------------------------------------------

    string_columns = [
        "prediction_type",
        "forecast_selection_reason",
        "forecast_quality_status",
        "forecast_confidence",
        "model",
    ]

    for column in string_columns:

        result[column] = (
            result[column]
            .astype("string")
            .str.strip()
        )

    # --------------------------------------------------------
    # RENAME TO POWER BI MODEL
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

            "validation_mae":
                "cash_prediction_mae",

            "validation_rmse":
                "cash_prediction_rmse",

            "validation_smape_pct":
                "cash_prediction_smape_pct",

            "validation_stabilized_mape_pct":
                "cash_prediction_stabilized_mape_pct",

            "validation_residual_std":
                "cash_prediction_residual_std",

            "forecast_interval_width":
                "cash_forecast_interval_width",

            "prediction_type":
                "cash_prediction_type",

            "forecast_selection_reason":
                "cash_forecast_selection_reason",

            "forecast_quality_status":
                "cash_forecast_quality",

            "forecast_confidence":
                "cash_forecast_confidence",

            "model":
                "cash_prediction_model",

            "ml_improvement_vs_baseline_pct":
                "cash_ml_improvement_vs_baseline",
        }
    )

    # --------------------------------------------------------
    # OCF INTERVAL VALIDATION
    # --------------------------------------------------------

    invalid_ocf_interval = (
        result[
            "ml_ocf_lower_bound"
        ]
        >
        result[
            "ml_ocf_upper_bound"
        ]
    )

    if invalid_ocf_interval.any():

        raise RuntimeError(
            "Cash OCF prediction interval is invalid."
        )

    invalid_ocf_position = (
        (
            result[
                "ml_predicted_operating_cf"
            ]
            <
            result[
                "ml_ocf_lower_bound"
            ]
        )
        |
        (
            result[
                "ml_predicted_operating_cf"
            ]
            >
            result[
                "ml_ocf_upper_bound"
            ]
        )
    )

    if invalid_ocf_position.any():

        raise RuntimeError(
            "Predicted Operating Cash Flow lies outside "
            "its prediction interval."
        )

    # --------------------------------------------------------
    # CASH INTERVAL VALIDATION
    # --------------------------------------------------------

    invalid_cash_interval = (
        result[
            "ml_cash_lower_bound"
        ]
        >
        result[
            "ml_cash_upper_bound"
        ]
    )

    if invalid_cash_interval.any():

        raise RuntimeError(
            "Closing cash prediction interval is invalid."
        )

    invalid_cash_position = (
        (
            result[
                "ml_predicted_closing_cash"
            ]
            <
            result[
                "ml_cash_lower_bound"
            ]
        )
        |
        (
            result[
                "ml_predicted_closing_cash"
            ]
            >
            result[
                "ml_cash_upper_bound"
            ]
        )
    )

    if invalid_cash_position.any():

        raise RuntimeError(
            "Predicted Closing Cash lies outside "
            "its prediction interval."
        )

    # --------------------------------------------------------
    # FORECAST QUALITY VALIDATION
    # --------------------------------------------------------

    allowed_quality = {
        "HIGH_CONFIDENCE",
        "MEDIUM_CONFIDENCE",
        "LOW_CONFIDENCE",
        "VERY_LOW",
        "VERY_LOW_CONFIDENCE",
    }

    observed_quality = set(
        result[
            "cash_forecast_quality"
        ]
        .dropna()
        .astype(str)
        .str.upper()
        .unique()
    )

    unknown_quality = (
        observed_quality
        - allowed_quality
    )

    if unknown_quality:

        raise RuntimeError(
            "Unknown cash forecast quality values: "
            + ", ".join(
                sorted(unknown_quality)
            )
        )

    # --------------------------------------------------------
    # FORECAST CONFIDENCE VALIDATION
    # --------------------------------------------------------

    allowed_confidence = {
        "HIGH",
        "MEDIUM",
        "LOW",
        "VERY_LOW",
        "HIGH_CONFIDENCE",
        "MEDIUM_CONFIDENCE",
        "LOW_CONFIDENCE",
        "VERY_LOW_CONFIDENCE",
    }

    observed_confidence = set(
        result[
            "cash_forecast_confidence"
        ]
        .dropna()
        .astype(str)
        .str.upper()
        .unique()
    )

    unknown_confidence = (
        observed_confidence
        - allowed_confidence
    )

    if unknown_confidence:

        raise RuntimeError(
            "Unknown cash forecast confidence values: "
            + ", ".join(
                sorted(unknown_confidence)
            )
        )

    # --------------------------------------------------------
    # SELECTION REASON
    # --------------------------------------------------------

    allowed_selection_reasons = {
        "ML_OUTPERFORMED_BASELINE",
        "ML_DID_NOT_OUTPERFORM_BASELINE",
        "BASELINE_SELECTED",
        "ML_SELECTED",
    }

    observed_selection_reasons = set(
        result[
            "cash_forecast_selection_reason"
        ]
        .dropna()
        .astype(str)
        .str.upper()
        .unique()
    )

    unknown_selection_reasons = (
        observed_selection_reasons
        - allowed_selection_reasons
    )

    if unknown_selection_reasons:

        logger.warning(
            "Unknown cash forecast selection reason(s): %s",
            ", ".join(
                sorted(
                    unknown_selection_reasons
                )
            ),
        )

    # --------------------------------------------------------
    # ONE ROW PER PERIOD
    # --------------------------------------------------------

    if (
        result["period"]
        .duplicated()
        .any()
    ):

        duplicate_periods = (
            result.loc[
                result["period"].duplicated(
                    keep=False
                ),
                "period",
            ]
            .dt.strftime(
                "%Y-%m"
            )
            .unique()
            .tolist()
        )

        raise RuntimeError(
            "Cash prediction contains duplicate periods: "
            + ", ".join(
                duplicate_periods
            )
        )

    result = (
        result
        .sort_values(
            "period"
        )
        .reset_index(
            drop=True
        )
    )

    logger.info(
        "Cash prediction prepared: %s forecast periods.",
        len(result),
    )

    logger.info(
        "Cash prediction method: %s",
        ", ".join(
            result[
                "cash_prediction_model"
            ]
            .dropna()
            .astype(str)
            .unique()
        ),
    )

    logger.info(
        "Cash forecast selection reason: %s",
        ", ".join(
            result[
                "cash_forecast_selection_reason"
            ]
            .dropna()
            .astype(str)
            .unique()
        ),
    )

    logger.info(
        "Cash forecast quality: %s",
        ", ".join(
            result[
                "cash_forecast_quality"
            ]
            .dropna()
            .astype(str)
            .unique()
        ),
    )

    logger.info(
        "Cash forecast confidence: %s",
        ", ".join(
            result[
                "cash_forecast_confidence"
            ]
            .dropna()
            .astype(str)
            .unique()
        ),
    )

    return result[
        [
            "period",

            "ml_predicted_operating_cf",
            "ml_predicted_closing_cash",

            "ml_ocf_lower_bound",
            "ml_ocf_upper_bound",

            "ml_cash_lower_bound",
            "ml_cash_upper_bound",

            "cash_prediction_mae",
            "cash_prediction_rmse",
            "cash_prediction_smape_pct",
            "cash_prediction_stabilized_mape_pct",
            "cash_prediction_residual_std",
            "cash_forecast_interval_width",

            "cash_prediction_type",
            "cash_forecast_selection_reason",
            "cash_forecast_quality",
            "cash_forecast_confidence",
            "cash_prediction_model",
            "cash_ml_improvement_vs_baseline",
        ]
    ]


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
        .sort_values(
            "period"
        )
        .drop_duplicates(
            "period",
            keep="last",
        )
        .reset_index(
            drop=True
        )
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
        dataset[
            "period"
        ].duplicated(
            keep=False
        )
    )

    if duplicate_mask.any():

        duplicates = (
            dataset.loc[
                duplicate_mask,
                "period",
            ]
            .dt.strftime(
                "%Y-%m"
            )
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
) -> pd.Series:
    """
    Validate six consecutive future forecast months.
    """

    future = reporting[
        (
            reporting["period"]
            >
            actual_cutoff
        )
        &
        (
            reporting[
                "reporting_data_type"
            ]
            ==
            "FORECAST"
        )
    ].copy()

    future_periods = (
        future[
            "period"
        ]
        .drop_duplicates()
        .sort_values()
        .reset_index(
            drop=True
        )
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

    logger.info(
        "Validated forecast periods: %s -> %s",
        future_periods.iloc[0].strftime(
            "%Y-%m"
        ),
        future_periods.iloc[-1].strftime(
            "%Y-%m"
        ),
    )

    return future_periods


# ============================================================
# PREDICTION HORIZON ALIGNMENT
# ============================================================

def validate_prediction_horizons(
    revenue_prediction: pd.DataFrame,
    expense_prediction: pd.DataFrame,
    cash_prediction: pd.DataFrame,
    expected_periods: pd.Series,
) -> None:
    """
    Validate Revenue, Expense and Cash ML layers
    against the same six forecast periods.
    """

    expected = (
        pd.to_datetime(
            expected_periods
        )
        .dt.to_period("M")
        .dt.to_timestamp()
        .reset_index(
            drop=True
        )
    )

    layers = {
        "Revenue ML":
            revenue_prediction,

        "Expense ML":
            expense_prediction,

        "Cash ML":
            cash_prediction,
    }

    for layer_name, dataset in layers.items():

        if dataset.empty:

            raise RuntimeError(
                f"{layer_name} dataset is empty."
            )

        if "period" not in dataset.columns:

            raise RuntimeError(
                f"{layer_name} dataset is missing period."
            )

        periods = (
            pd.to_datetime(
                dataset["period"],
                errors="coerce",
            )
            .dropna()
            .dt.to_period("M")
            .dt.to_timestamp()
            .drop_duplicates()
            .sort_values()
            .reset_index(
                drop=True
            )
        )

        if not periods.equals(
            expected
        ):

            raise RuntimeError(
                f"{layer_name} forecast horizon mismatch.\n"
                f"Expected: "
                f"{expected.dt.strftime('%Y-%m').tolist()}\n"
                f"Found: "
                f"{periods.dt.strftime('%Y-%m').tolist()}"
            )

        logger.info(
            "%s horizon validated: %s months.",
            layer_name,
            len(periods),
        )

    logger.info(
        "Revenue / Expense / Cash forecast horizons "
        "are fully aligned."
    )


# ============================================================
# PREDICTION COMPLETENESS
# ============================================================

def validate_forecast_prediction_completeness(
    reporting: pd.DataFrame,
    actual_cutoff: pd.Timestamp,
) -> None:
    """
    Validate that all required forecast layers contain
    values for every future month.
    """

    future = (
        reporting[
            reporting["period"]
            >
            actual_cutoff
        ]
        .sort_values(
            "period"
        )
        .reset_index(
            drop=True
        )
    )

    if future.empty:

        raise RuntimeError(
            "No future forecast periods available."
        )

    required_columns = {
        "Revenue":
            "ml_predicted_revenue",

        "Expense":
            "ml_predicted_operating_costs",

        "Cash":
            "ml_predicted_operating_cf",
    }

    missing_layers = []

    for layer_name, column_name in (
        required_columns.items()
    ):

        if column_name not in reporting.columns:

            missing_layers.append(
                f"{layer_name} ({column_name})"
            )

            continue

        missing_mask = (
            future[
                column_name
            ].isna()
        )

        if missing_mask.any():

            missing_periods = (
                future.loc[
                    missing_mask,
                    "period",
                ]
                .dt.strftime(
                    "%Y-%m"
                )
                .tolist()
            )

            missing_layers.append(
                f"{layer_name}: "
                + ", ".join(
                    missing_periods
                )
            )

    if missing_layers:

        raise RuntimeError(
            "Forecast prediction completeness validation "
            "failed: "
            + " | ".join(
                missing_layers
            )
        )

    logger.info(
        "Forecast prediction completeness validation passed."
    )


# ============================================================
# ACTUAL / FORECAST SEMANTIC CLEANUP
# ============================================================

def clear_context_specific_metrics(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Clear metrics that are not semantically applicable
    to ACTUAL or FORECAST periods.
    """

    result = df.copy()

    forecast_mask = (
        result[
            "reporting_data_type"
        ]
        ==
        "FORECAST"
    )

    actual_mask = (
        result[
            "reporting_data_type"
        ]
        ==
        "ACTUAL"
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
            or column.startswith(
                "anomaly_"
            )
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
            column.startswith(
                "ml_"
            )
            or column.endswith(
                "_prediction_rmse"
            )
            or column.endswith(
                "_prediction_mae"
            )
            or column.endswith(
                "_prediction_smape_pct"
            )
            or column.endswith(
                "_prediction_stabilized_mape_pct"
            )
            or column.endswith(
                "_prediction_residual_std"
            )
            or column.endswith(
                "_forecast_interval_width"
            )
            or column.startswith(
                "cash_forecast_"
            )
            or column.startswith(
                "cash_prediction_"
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
# ACTUAL / FORECAST BOUNDARY VALIDATION
# ============================================================

def validate_actual_forecast_boundary(
    reporting: pd.DataFrame,
    actual_cutoff: pd.Timestamp,
) -> None:
    """
    Validate semantic boundary between ACTUAL and FORECAST.
    """

    actual_rows = reporting[
        reporting[
            "reporting_data_type"
        ]
        ==
        "ACTUAL"
    ]

    forecast_rows = reporting[
        reporting[
            "reporting_data_type"
        ]
        ==
        "FORECAST"
    ]

    if actual_rows.empty:

        raise RuntimeError(
            "No ACTUAL rows found."
        )

    if forecast_rows.empty:

        raise RuntimeError(
            "No FORECAST rows found."
        )

    latest_actual = (
        actual_rows[
            "period"
        ].max()
    )

    earliest_forecast = (
        forecast_rows[
            "period"
        ].min()
    )

    if latest_actual != actual_cutoff:

        raise RuntimeError(
            "Latest ACTUAL period does not match "
            "authoritative actual cutoff."
        )

    expected_first_forecast = (
        actual_cutoff
        +
        pd.offsets.MonthBegin(
            1
        )
    )

    if earliest_forecast != (
        expected_first_forecast
    ):

        raise RuntimeError(
            "FORECAST does not start immediately after "
            "the last ACTUAL month."
        )

    logger.info(
        "ACTUAL / FORECAST boundary validated: "
        "%s ACTUAL -> %s FORECAST",
        latest_actual.strftime(
            "%Y-%m"
        ),
        earliest_forecast.strftime(
            "%Y-%m"
        ),
    )


# ============================================================
# MONTHLY GRAIN VALIDATION
# ============================================================

def validate_monthly_grain(
    df: pd.DataFrame,
) -> None:
    """
    Validate exactly one row per calendar month.
    """

    if "period" not in df.columns:

        raise RuntimeError(
            "Final dataset is missing period."
        )

    if df.empty:

        raise RuntimeError(
            "Final dataset is empty."
        )

    if df["period"].duplicated().any():

        duplicates = (
            df.loc[
                df["period"].duplicated(
                    keep=False
                ),
                "period",
            ]
            .dt.strftime(
                "%Y-%m"
            )
            .unique()
            .tolist()
        )

        raise RuntimeError(
            "Final dataset contains duplicate months: "
            + ", ".join(
                duplicates
            )
        )

    sorted_periods = (
        df[
            "period"
        ]
        .sort_values()
        .reset_index(
            drop=True
        )
    )

    expected = pd.Series(
        pd.date_range(
            start=sorted_periods.iloc[0],
            end=sorted_periods.iloc[-1],
            freq="MS",
        )
    )

    if not sorted_periods.equals(
        expected
    ):

        raise RuntimeError(
            "Final dataset contains gaps in the monthly calendar."
        )

    logger.info(
        "Monthly grain validation passed: "
        "%s continuous monthly rows.",
        len(df),
    )


# ============================================================
# SIGN CONVENTION VALIDATION
# ============================================================

def validate_sign_convention(
    df: pd.DataFrame,
) -> None:
    """
    Validate management sign conventions.
    """

    forecast = df[
        df[
            "reporting_data_type"
        ]
        ==
        "FORECAST"
    ].copy()

    if forecast.empty:

        return

    # --------------------------------------------------------
    # Rolling revenue
    # --------------------------------------------------------

    revenue = forecast.get(
        "rolling_revenue",
        pd.Series(dtype=float),
    ).dropna()

    if (
        not revenue.empty
        and
        (revenue < 0).any()
    ):

        raise RuntimeError(
            "Rolling revenue contains negative values."
        )

    # --------------------------------------------------------
    # ML revenue
    # --------------------------------------------------------

    ml_revenue = forecast.get(
        "ml_predicted_revenue",
        pd.Series(dtype=float),
    ).dropna()

    if (
        not ml_revenue.empty
        and
        (ml_revenue < 0).any()
    ):

        raise RuntimeError(
            "ML revenue contains negative values."
        )

    # --------------------------------------------------------
    # Rolling costs
    # --------------------------------------------------------

    costs = forecast.get(
        "rolling_operating_costs",
        pd.Series(dtype=float),
    ).dropna()

    if (
        not costs.empty
        and
        (costs > 0).any()
    ):

        raise RuntimeError(
            "Rolling operating costs contain positive values."
        )

    # --------------------------------------------------------
    # ML costs
    # --------------------------------------------------------

    ml_costs = forecast.get(
        "ml_predicted_operating_costs",
        pd.Series(dtype=float),
    ).dropna()

    if (
        not ml_costs.empty
        and
        (ml_costs > 0).any()
    ):

        raise RuntimeError(
            "ML operating costs contain positive values."
        )

    logger.info(
        "Management sign convention validation passed."
    )


# ============================================================
# INTERVAL VALIDATION
# ============================================================

def validate_forecast_intervals(
    df: pd.DataFrame,
) -> None:
    """
    Validate prediction intervals in the final dataset.
    """

    forecast = (
        df[
            df[
                "reporting_data_type"
            ]
            ==
            "FORECAST"
        ]
        .copy()
    )

    if forecast.empty:

        return

    # --------------------------------------------------------
    # Revenue interval
    # --------------------------------------------------------

    revenue_columns = {
        "ml_revenue_lower_bound",
        "ml_predicted_revenue",
        "ml_revenue_upper_bound",
    }

    if revenue_columns.issubset(
        forecast.columns
    ):

        invalid = (
            (
                forecast[
                    "ml_revenue_lower_bound"
                ]
                >
                forecast[
                    "ml_predicted_revenue"
                ]
            )
            |
            (
                forecast[
                    "ml_predicted_revenue"
                ]
                >
                forecast[
                    "ml_revenue_upper_bound"
                ]
            )
        )

        if invalid.any():

            raise RuntimeError(
                "Revenue forecast contains predictions "
                "outside prediction intervals."
            )

    # --------------------------------------------------------
    # Expense interval
    # --------------------------------------------------------

    expense_columns = {
        "ml_expense_lower_bound",
        "ml_predicted_operating_costs",
        "ml_expense_upper_bound",
    }

    if expense_columns.issubset(
        forecast.columns
    ):

        invalid = (
            (
                forecast[
                    "ml_expense_lower_bound"
                ]
                >
                forecast[
                    "ml_predicted_operating_costs"
                ]
            )
            |
            (
                forecast[
                    "ml_predicted_operating_costs"
                ]
                >
                forecast[
                    "ml_expense_upper_bound"
                ]
            )
        )

        if invalid.any():

            raise RuntimeError(
                "Expense forecast contains predictions "
                "outside prediction intervals."
            )

    # --------------------------------------------------------
    # Cash OCF interval
    # --------------------------------------------------------

    ocf_columns = {
        "ml_ocf_lower_bound",
        "ml_predicted_operating_cf",
        "ml_ocf_upper_bound",
    }

    if ocf_columns.issubset(
        forecast.columns
    ):

        invalid = (
            (
                forecast[
                    "ml_ocf_lower_bound"
                ]
                >
                forecast[
                    "ml_predicted_operating_cf"
                ]
            )
            |
            (
                forecast[
                    "ml_predicted_operating_cf"
                ]
                >
                forecast[
                    "ml_ocf_upper_bound"
                ]
            )
        )

        if invalid.any():

            raise RuntimeError(
                "Cash flow forecast contains predictions "
                "outside prediction intervals."
            )

    # --------------------------------------------------------
    # Closing cash interval
    # --------------------------------------------------------

    cash_columns = {
        "ml_cash_lower_bound",
        "ml_predicted_closing_cash",
        "ml_cash_upper_bound",
    }

    if cash_columns.issubset(
        forecast.columns
    ):

        invalid = (
            (
                forecast[
                    "ml_cash_lower_bound"
                ]
                >
                forecast[
                    "ml_predicted_closing_cash"
                ]
            )
            |
            (
                forecast[
                    "ml_predicted_closing_cash"
                ]
                >
                forecast[
                    "ml_cash_upper_bound"
                ]
            )
        )

        if invalid.any():

            raise RuntimeError(
                "Closing cash forecast contains predictions "
                "outside prediction intervals."
            )

    logger.info(
        "Forecast interval validation passed."
    )


# ============================================================
# CASH FORECAST METADATA VALIDATION
# ============================================================

def validate_cash_forecast_metadata(
    df: pd.DataFrame,
) -> None:
    """
    Validate Cash Flow forecast metadata required by Power BI.
    """

    forecast = df[
        df[
            "reporting_data_type"
        ]
        ==
        "FORECAST"
    ].copy()

    if forecast.empty:

        return

    required_columns = {
        "cash_prediction_type",
        "cash_forecast_selection_reason",
        "cash_forecast_quality",
        "cash_forecast_confidence",
        "cash_prediction_model",
        "cash_ml_improvement_vs_baseline",
    }

    missing = (
        required_columns
        - set(forecast.columns)
    )

    if missing:

        raise RuntimeError(
            "Cash Flow forecast metadata missing: "
            + ", ".join(
                sorted(missing)
            )
        )

    for column in [
        "cash_prediction_type",
        "cash_forecast_selection_reason",
        "cash_forecast_quality",
        "cash_forecast_confidence",
        "cash_prediction_model",
    ]:

        if (
            forecast[column]
            .isna()
            .any()
        ):

            missing_periods = (
                forecast.loc[
                    forecast[column].isna(),
                    "period",
                ]
                .dt.strftime(
                    "%Y-%m"
                )
                .tolist()
            )

            raise RuntimeError(
                f"Cash Flow metadata column '{column}' "
                "contains missing values for: "
                + ", ".join(
                    missing_periods
                )
            )

    logger.info(
        "Cash Flow forecast metadata validation passed."
    )


# ============================================================
# BUILD FINAL DATASET
# ============================================================

def build_reporting_dataset(
    sources: dict[str, pd.DataFrame],
) -> tuple[
    pd.DataFrame,
    pd.Timestamp,
]:
    """
    Build complete Power BI reporting dataset.

    Returns:
        reporting
        actual_cutoff
    """

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

    result = (
        build_monthly_calendar(
            sources,
            actual_cutoff,
        )
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
            sources[
                "anomaly"
            ]
        )
    )

    variance = (
        prepare_variance(
            sources[
                "variance"
            ]
        )
    )

    pvm = (
        prepare_pvm(
            sources[
                "pvm"
            ]
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

    result = (
        clear_context_specific_metrics(
            result
        )
    )

    # --------------------------------------------------------
    # FORECAST HORIZON
    # --------------------------------------------------------

    forecast_periods = (
        validate_forecast_horizon(
            result,
            actual_cutoff,
        )
    )

    # --------------------------------------------------------
    # PREDICTION HORIZON ALIGNMENT
    # --------------------------------------------------------

    validate_prediction_horizons(
        revenue_prediction,
        expense_prediction,
        cash_prediction,
        forecast_periods,
    )

    # --------------------------------------------------------
    # PREDICTION COMPLETENESS
    # --------------------------------------------------------

    validate_forecast_prediction_completeness(
        result,
        actual_cutoff,
    )

    # --------------------------------------------------------
    # CASH METADATA
    # --------------------------------------------------------

    validate_cash_forecast_metadata(
        result
    )

    # --------------------------------------------------------
    # ACTUAL / FORECAST BOUNDARY
    # --------------------------------------------------------

    validate_actual_forecast_boundary(
        result,
        actual_cutoff,
    )

    # --------------------------------------------------------
    # SORT
    # --------------------------------------------------------

    result = (
        result
        .sort_values(
            "period"
        )
        .reset_index(
            drop=True
        )
    )

    # --------------------------------------------------------
    # GRAIN
    # --------------------------------------------------------

    validate_monthly_grain(
        result
    )

    return (
        result,
        actual_cutoff,
    )


# ============================================================
# FORECAST SAMPLE LOGGING
# ============================================================

def log_forecast_samples(
    df: pd.DataFrame,
) -> None:
    """
    Log forecast samples for manual QA.
    """

    forecast = (
        df[
            df[
                "reporting_data_type"
            ]
            ==
            "FORECAST"
        ]
        .sort_values(
            "period"
        )
        .reset_index(
            drop=True
        )
    )

    if forecast.empty:

        return

    # --------------------------------------------------------
    # REVENUE
    # --------------------------------------------------------

    if {
        "period",
        "ml_predicted_revenue",
        "ml_revenue_lower_bound",
        "ml_revenue_upper_bound",
    }.issubset(
        forecast.columns
    ):

        logger.info(
            "Forecast revenue sample:\n%s",
            forecast[
                [
                    "period",
                    "ml_predicted_revenue",
                    "ml_revenue_lower_bound",
                    "ml_revenue_upper_bound",
                ]
            ].to_string(
                index=False
            ),
        )

    # --------------------------------------------------------
    # EXPENSE
    # --------------------------------------------------------

    if {
        "period",
        "ml_predicted_expense_magnitude",
        "ml_predicted_operating_costs",
    }.issubset(
        forecast.columns
    ):

        logger.info(
            "Forecast expense sample:\n%s",
            forecast[
                [
                    "period",
                    "ml_predicted_expense_magnitude",
                    "ml_predicted_operating_costs",
                ]
            ].to_string(
                index=False
            ),
        )

    # --------------------------------------------------------
    # CASH
    # --------------------------------------------------------

    if {
        "period",
        "ml_predicted_operating_cf",
        "ml_predicted_closing_cash",
        "cash_forecast_selection_reason",
        "cash_forecast_quality",
        "cash_forecast_confidence",
    }.issubset(
        forecast.columns
    ):

        logger.info(
            "Forecast cash sample:\n%s",
            forecast[
                [
                    "period",
                    "ml_predicted_operating_cf",
                    "ml_predicted_closing_cash",
                    "cash_forecast_selection_reason",
                    "cash_forecast_quality",
                    "cash_forecast_confidence",
                ]
            ].to_string(
                index=False
            ),
        )


# ============================================================
# FINAL VALIDATION LOGGING
# ============================================================

def log_final_validation(
    df: pd.DataFrame,
    actual_cutoff: pd.Timestamp,
) -> None:
    """
    Log final dataset structure.
    """

    actual_count = int(
        (
            df[
                "reporting_data_type"
            ]
            ==
            "ACTUAL"
        ).sum()
    )

    forecast_count = int(
        (
            df[
                "reporting_data_type"
            ]
            ==
            "FORECAST"
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
        df[
            "period"
        ].min().strftime(
            "%Y-%m"
        ),
    )

    logger.info(
        "Last period: %s",
        df[
            "period"
        ].max().strftime(
            "%Y-%m"
        ),
    )

    logger.info(
        "Authoritative ACTUAL cutoff: %s",
        actual_cutoff.strftime(
            "%Y-%m"
        ),
    )

    logger.info(
        "Expected FORECAST horizon: %s months",
        EXPECTED_FORECAST_HORIZON,
    )

    logger.info(
        "Forecast periods:\n%s",
        df.loc[
            df[
                "reporting_data_type"
            ]
            ==
            "FORECAST",
            [
                "period",
                "reporting_data_type",
                "cash_prediction_type",
                "cash_forecast_selection_reason",
                "cash_forecast_quality",
                "cash_forecast_confidence",
            ],
        ].to_string(
            index=False
        ),
    )


# ============================================================
# SAVE
# ============================================================

def save_output(
    df: pd.DataFrame,
) -> None:
    """
    Save final Power BI reporting dataset.
    """

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
    """
    Run EFAP Power BI reporting export.
    """

    try:

        logger.info(
            "Starting EFAP Power BI Analytics Export."
        )

        # ----------------------------------------------------
        # PROJECT / FILE VALIDATION
        # ----------------------------------------------------

        validate_files()

        # ----------------------------------------------------
        # LOAD
        # ----------------------------------------------------

        sources = (
            load_all_sources()
        )

        # ----------------------------------------------------
        # BUILD
        # ----------------------------------------------------

        (
            reporting,
            actual_cutoff,
        ) = build_reporting_dataset(
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

        validate_forecast_intervals(
            reporting
        )

        validate_cash_forecast_metadata(
            reporting
        )

        # ----------------------------------------------------
        # DEBUG / QA
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
        # FINAL LOGGING
        # ----------------------------------------------------

        log_final_validation(
            reporting,
            actual_cutoff,
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