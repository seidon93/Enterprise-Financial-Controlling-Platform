"""
EFAP - Power BI Analytics Reporting Export

Object:
    reporting/build_powerbi_analytics_export.py

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
    This script consolidates and normalizes analytical outputs.
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
# GENERAL HELPERS
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

    df = pd.read_csv(path)

    if df.empty:

        logger.warning(
            "%s exists but is empty.",
            dataset_name,
        )

    return df


def normalize_columns(
    df: pd.DataFrame,
) -> pd.DataFrame:

    if df.empty:
        return df

    result = df.copy()

    result.columns = [
        str(column).strip()
        for column in result.columns
    ]

    return result


def normalize_period(
    df: pd.DataFrame,
) -> pd.DataFrame:

    if df.empty:
        return df

    result = normalize_columns(df)

    if "period" not in result.columns:
        return result

    result["period"] = pd.to_datetime(
        result["period"],
        errors="coerce",
    )

    result["period"] = (
        result["period"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    return result


def require_columns(
    df: pd.DataFrame,
    required: set[str],
    dataset_name: str,
) -> None:

    missing = required - set(df.columns)

    if missing:

        raise RuntimeError(
            f"{dataset_name} missing required columns: "
            f"{', '.join(sorted(missing))}"
        )


def validate_unique_period(
    df: pd.DataFrame,
    dataset_name: str,
) -> None:

    if df.empty:
        return

    if "period" not in df.columns:
        raise RuntimeError(
            f"{dataset_name} does not contain 'period'."
        )

    duplicate_mask = (
        df["period"]
        .duplicated(
            keep=False
        )
    )

    if duplicate_mask.any():

        duplicate_periods = (
            df.loc[
                duplicate_mask,
                "period",
            ]
            .dt.strftime("%Y-%m")
            .unique()
            .tolist()
        )

        raise RuntimeError(
            f"{dataset_name} contains duplicate periods: "
            f"{duplicate_periods}"
        )


def safe_numeric(
    series: pd.Series,
) -> pd.Series:

    return pd.to_numeric(
        series,
        errors="coerce",
    )


# ============================================================
# LOAD ALL SOURCES
# ============================================================

def load_all_sources() -> dict[str, pd.DataFrame]:

    sources = {

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

    return sources


# ============================================================
# ACTUAL CUTOFF
# ============================================================

def determine_actual_cutoff(
    controller_timeseries: pd.DataFrame,
) -> pd.Timestamp:

    require_columns(
        controller_timeseries,
        {"period"},
        "Controller KPI time series",
    )

    periods = (
        controller_timeseries["period"]
        .dropna()
        .sort_values()
    )

    if periods.empty:

        raise RuntimeError(
            "Controller KPI time series contains no valid periods."
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

    periods: list[pd.Timestamp] = []

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
            lambda value:
            "ACTUAL"
            if value <= actual_cutoff
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

    require_columns(
        df,
        required,
        "Rolling forecast",
    )

    result = df[
        [
            "period",
            "data_type",
            "forecast_horizon_month",
            "revenue",
            "operating_costs",
        ]
    ].copy()

    result["revenue"] = safe_numeric(
        result["revenue"]
    )

    result["operating_costs"] = safe_numeric(
        result["operating_costs"]
    )

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

    validate_unique_period(
        result,
        "Prepared rolling forecast",
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

    require_columns(
        df,
        required,
        "Anomaly summary",
    )

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

    result = (
        result
        .sort_values("period")
        .drop_duplicates(
            "period",
            keep="last",
        )
        .reset_index(drop=True)
    )

    validate_unique_period(
        result,
        "Prepared anomaly summary",
    )

    return result


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

    require_columns(
        df,
        required,
        "Variance root cause summary",
    )

    rows: list[dict] = []

    for period, group in df.groupby(
        "period",
        sort=True,
    ):

        row = {
            "period": period
        }

        for _, item in group.iterrows():

            metric = (
                str(item["metric"])
                .strip()
                .lower()
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

    validate_unique_period(
        result,
        "Prepared variance root cause",
    )

    return result


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

    require_columns(
        df,
        required,
        "Price / Volume / Mix summary",
    )

    rows: list[dict] = []

    for period, group in df.groupby(
        "period",
        sort=True,
    ):

        row = {
            "period": period
        }

        for _, item in group.iterrows():

            analysis_type = (
                str(item["analysis_type"])
                .strip()
                .upper()
            )

            # Current management reporting specification:
            # Revenue PVM is authoritative.
            if analysis_type != "REVENUE":
                continue

            prefix = "revenue_pvm"

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

    validate_unique_period(
        result,
        "Prepared PVM summary",
    )

    return result


# ============================================================
# REVENUE PREDICTION
# ============================================================

def prepare_revenue_prediction(
    df: pd.DataFrame,
) -> pd.DataFrame:

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
    # Expected source schema
    #
    # period
    # predicted_revenue
    # lower_bound
    # upper_bound
    # validation_rmse
    # validation_mape_pct
    #
    # --------------------------------------------------------

    required = {
        "period",
        "predicted_revenue",
        "lower_bound",
        "upper_bound",
        "validation_rmse",
    }

    require_columns(
        df,
        required,
        "Revenue prediction",
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

    result[
        "predicted_revenue"
    ] = safe_numeric(
        result[
            "predicted_revenue"
        ]
    )

    result[
        "lower_bound"
    ] = safe_numeric(
        result[
            "lower_bound"
        ]
    )

    result[
        "upper_bound"
    ] = safe_numeric(
        result[
            "upper_bound"
        ]
    )

    result[
        "validation_rmse"
    ] = safe_numeric(
        result[
            "validation_rmse"
        ]
    )

    # --------------------------------------------------------
    # Revenue management convention
    # --------------------------------------------------------
    #
    # Source may contain negative accounting-style revenue.
    #
    # Power BI management layer:
    #
    #   predicted revenue > 0
    #   lower bound > 0
    #   upper bound > lower bound
    #
    # --------------------------------------------------------

    result[
        "ml_predicted_revenue"
    ] = result[
        "predicted_revenue"
    ].abs()

    raw_lower = result[
        "lower_bound"
    ].abs()

    raw_upper = result[
        "upper_bound"
    ].abs()

    result[
        "ml_revenue_lower_bound"
    ] = pd.concat(
        [
            raw_lower,
            raw_upper,
        ],
        axis=1,
    ).min(axis=1)

    result[
        "ml_revenue_upper_bound"
    ] = pd.concat(
        [
            raw_lower,
            raw_upper,
        ],
        axis=1,
    ).max(axis=1)

    result[
        "revenue_prediction_rmse"
    ] = result[
        "validation_rmse"
    ]

    if "validation_mape_pct" in df.columns:

        result[
            "revenue_prediction_mape_pct"
        ] = safe_numeric(
            df[
                "validation_mape_pct"
            ]
        )

    else:

        result[
            "revenue_prediction_mape_pct"
        ] = pd.NA

    result = result[
        [
            "period",
            "revenue_prediction_rmse",
            "revenue_prediction_mape_pct",
            "ml_predicted_revenue",
            "ml_revenue_lower_bound",
            "ml_revenue_upper_bound",
        ]
    ]

    result = (
        result
        .sort_values("period")
        .drop_duplicates(
            "period",
            keep="last",
        )
        .reset_index(drop=True)
    )

    # --------------------------------------------------------
    # Revenue prediction validation
    # --------------------------------------------------------

    invalid_point = (
        result["ml_predicted_revenue"]
        < 0
    )

    invalid_lower = (
        result["ml_revenue_lower_bound"]
        < 0
    )

    invalid_interval = (
        result["ml_revenue_lower_bound"]
        >
        result["ml_revenue_upper_bound"]
    )

    if (
        invalid_point.any()
        or invalid_lower.any()
        or invalid_interval.any()
    ):

        raise RuntimeError(
            "Revenue prediction contains invalid "
            "management-normalized values."
        )

    logger.info(
        "Revenue prediction prepared: %s forecast periods.",
        len(result),
    )

    validate_unique_period(
        result,
        "Prepared revenue prediction",
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

    require_columns(
        df,
        required,
        "Expense prediction",
    )

    result = df.copy()

    for column in [
        "predicted_expense",
        "lower_bound",
        "upper_bound",
        "validation_rmse",
    ]:

        result[column] = safe_numeric(
            result[column]
        )

    # --------------------------------------------------------
    # Expense prediction may be account-level.
    # First aggregate by month.
    # --------------------------------------------------------

    aggregated = (
        result
        .groupby(
            "period",
            as_index=False,
        )
        .agg(
            ml_predicted_expense_magnitude=(
                "predicted_expense",
                lambda values:
                values.abs().sum(),
            ),

            raw_expense_lower_bound=(
                "lower_bound",
                lambda values:
                values.abs().sum(),
            ),

            raw_expense_upper_bound=(
                "upper_bound",
                lambda values:
                values.abs().sum(),
            ),

            expense_prediction_rmse=(
                "validation_rmse",
                "mean",
            ),
        )
    )

    aggregated[
        "ml_predicted_operating_costs"
    ] = (
        -aggregated[
            "ml_predicted_expense_magnitude"
        ].abs()
    )

    lower = aggregated[
        "raw_expense_lower_bound"
    ].abs()

    upper = aggregated[
        "raw_expense_upper_bound"
    ].abs()

    aggregated[
        "ml_expense_lower_bound"
    ] = -pd.concat(
        [
            lower,
            upper,
        ],
        axis=1,
    ).max(axis=1)

    aggregated[
        "ml_expense_upper_bound"
    ] = -pd.concat(
        [
            lower,
            upper,
        ],
        axis=1,
    ).min(axis=1)

    result = aggregated[
        [
            "period",
            "ml_predicted_expense_magnitude",
            "expense_prediction_rmse",
            "ml_predicted_operating_costs",
            "ml_expense_lower_bound",
            "ml_expense_upper_bound",
        ]
    ].copy()

    # --------------------------------------------------------
    # Expense validation
    #
    # Costs must be negative in management layer.
    #
    # Lower bound is more negative.
    #
    # --------------------------------------------------------

    if (
        result[
            "ml_predicted_operating_costs"
        ]
        > 0
    ).any():

        raise RuntimeError(
            "Expense prediction contains positive "
            "operating-cost values."
        )

    if (
        result[
            "ml_expense_lower_bound"
        ]
        >
        result[
            "ml_expense_upper_bound"
        ]
    ).any():

        raise RuntimeError(
            "Expense prediction interval is invalid."
        )

    result = (
        result
        .sort_values("period")
        .drop_duplicates(
            "period",
            keep="last",
        )
        .reset_index(drop=True)
    )

    validate_unique_period(
        result,
        "Prepared expense prediction",
    )

    return result


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

    require_columns(
        df,
        required,
        "Cash Flow prediction",
    )

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

        result[column] = safe_numeric(
            result[column]
        )

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
    # Normalize cash / OCF intervals
    # --------------------------------------------------------

    ocf_low = result[
        "ml_ocf_lower_bound"
    ]

    ocf_high = result[
        "ml_ocf_upper_bound"
    ]

    result[
        "ml_ocf_lower_bound"
    ] = pd.concat(
        [
            ocf_low,
            ocf_high,
        ],
        axis=1,
    ).min(axis=1)

    result[
        "ml_ocf_upper_bound"
    ] = pd.concat(
        [
            ocf_low,
            ocf_high,
        ],
        axis=1,
    ).max(axis=1)

    cash_low = result[
        "ml_cash_lower_bound"
    ]

    cash_high = result[
        "ml_cash_upper_bound"
    ]

    result[
        "ml_cash_lower_bound"
    ] = pd.concat(
        [
            cash_low,
            cash_high,
        ],
        axis=1,
    ).min(axis=1)

    result[
        "ml_cash_upper_bound"
    ] = pd.concat(
        [
            cash_low,
            cash_high,
        ],
        axis=1,
    ).max(axis=1)

    result = (
        result
        .sort_values("period")
        .drop_duplicates(
            "period",
            keep="last",
        )
        .reset_index(drop=True)
    )

    if (
        result[
            "ml_ocf_lower_bound"
        ]
        >
        result[
            "ml_ocf_upper_bound"
        ]
    ).any():

        raise RuntimeError(
            "Cash Flow OCF prediction interval is invalid."
        )

    if (
        result[
            "ml_cash_lower_bound"
        ]
        >
        result[
            "ml_cash_upper_bound"
        ]
    ).any():

        raise RuntimeError(
            "Cash prediction interval is invalid."
        )

    validate_unique_period(
        result,
        "Prepared cash flow prediction",
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

    require_columns(
        df,
        {"period"},
        "Classification predictions",
    )

    result = (
        df
        .sort_values("period")
        .drop_duplicates(
            "period",
            keep="last",
        )
        .reset_index(drop=True)
    )

    validate_unique_period(
        result,
        "Prepared classification predictions",
    )

    return result


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

    validate_unique_period(
        dataset,
        dataset_name,
    )

    before_rows = len(base)

    result = base.merge(
        dataset,
        on="period",
        how="left",
        validate="one_to_one",
    )

    after_rows = len(result)

    if after_rows != before_rows:

        raise RuntimeError(
            f"Merge with {dataset_name} changed row count: "
            f"{before_rows} -> {after_rows}"
        )

    return result


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
# CONTEXT CLEANUP
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
    # Historical analytical metrics:
    # only meaningful for ACTUAL periods.
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
            or column == "high_critical_anomaly_count"
            or column == "max_robust_score"
        )
    ]

    if historical_only_columns:

        result.loc[
            forecast_mask,
            historical_only_columns,
        ] = pd.NA

    # --------------------------------------------------------
    # ML prediction metrics:
    # only meaningful for FORECAST periods.
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
# FORECAST PREDICTION COMPLETENESS
# ============================================================

def validate_forecast_predictions(
    reporting: pd.DataFrame,
) -> None:

    forecast = reporting[
        reporting[
            "reporting_data_type"
        ] == "FORECAST"
    ].copy()

    if forecast.empty:
        raise RuntimeError(
            "No forecast rows available."
        )

    required_prediction_columns = [
        "ml_predicted_revenue",
        "ml_revenue_lower_bound",
        "ml_revenue_upper_bound",
        "ml_predicted_expense_magnitude",
        "ml_predicted_operating_costs",
        "ml_expense_lower_bound",
        "ml_expense_upper_bound",
        "ml_predicted_operating_cf",
        "ml_predicted_closing_cash",
        "ml_ocf_lower_bound",
        "ml_ocf_upper_bound",
        "ml_cash_lower_bound",
        "ml_cash_upper_bound",
    ]

    missing_columns = [
        column
        for column in required_prediction_columns
        if column not in forecast.columns
    ]

    if missing_columns:

        raise RuntimeError(
            "Forecast is missing prediction columns: "
            f"{missing_columns}"
        )

    null_summary = {}

    for column in required_prediction_columns:

        null_count = int(
            forecast[column]
            .isna()
            .sum()
        )

        if null_count > 0:

            null_summary[column] = null_count

    if null_summary:

        raise RuntimeError(
            "Forecast prediction layer contains NULL values: "
            f"{null_summary}"
        )

    # --------------------------------------------------------
    # Revenue
    # --------------------------------------------------------

    if (
        forecast[
            "ml_predicted_revenue"
        ]
        < 0
    ).any():

        raise RuntimeError(
            "Forecast revenue contains negative values."
        )

    if (
        forecast[
            "ml_revenue_lower_bound"
        ]
        >
        forecast[
            "ml_revenue_upper_bound"
        ]
    ).any():

        raise RuntimeError(
            "Revenue prediction interval is invalid."
        )

    # --------------------------------------------------------
    # Operating costs
    # --------------------------------------------------------

    if (
        forecast[
            "ml_predicted_operating_costs"
        ]
        > 0
    ).any():

        raise RuntimeError(
            "Forecast operating costs contain positive values."
        )

    if (
        forecast[
            "ml_expense_lower_bound"
        ]
        >
        forecast[
            "ml_expense_upper_bound"
        ]
    ).any():

        raise RuntimeError(
            "Expense prediction interval is invalid."
        )

    # --------------------------------------------------------
    # Cash / OCF
    # --------------------------------------------------------

    if (
        forecast[
            "ml_ocf_lower_bound"
        ]
        >
        forecast[
            "ml_ocf_upper_bound"
        ]
    ).any():

        raise RuntimeError(
            "Operating cash flow prediction interval is invalid."
        )

    if (
        forecast[
            "ml_cash_lower_bound"
        ]
        >
        forecast[
            "ml_cash_upper_bound"
        ]
    ).any():

        raise RuntimeError(
            "Closing cash prediction interval is invalid."
        )

    logger.info(
        "Forecast prediction completeness validation passed."
    )


# ============================================================
# SIGN CONVENTION VALIDATION
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

    # Revenue

    if (
        forecast["rolling_revenue"]
        .dropna()
        < 0
    ).any():

        raise RuntimeError(
            "Rolling revenue contains negative values."
        )

    if (
        forecast["ml_predicted_revenue"]
        .dropna()
        < 0
    ).any():

        raise RuntimeError(
            "ML predicted revenue contains negative values."
        )

    # Operating costs

    if (
        forecast["rolling_operating_costs"]
        .dropna()
        > 0
    ).any():

        raise RuntimeError(
            "Rolling operating costs contain positive values."
        )

    if (
        forecast[
            "ml_predicted_operating_costs"
        ]
        .dropna()
        > 0
    ).any():

        raise RuntimeError(
            "ML predicted operating costs contain positive values."
        )

    logger.info(
        "Management sign convention validation passed."
    )


# ============================================================
# FINAL COLUMN ORDER
# ============================================================

FINAL_COLUMNS = [
    # Calendar / reporting
    "period",
    "year_month",
    "calendar_year",
    "calendar_month",
    "reporting_data_type",

    # Rolling forecast
    "rolling_data_type",
    "forecast_horizon_month",
    "rolling_revenue",
    "rolling_operating_costs",
    "rolling_ebitda",
    "rolling_ebitda_margin",

    # Anomaly
    "anomaly_count",
    "high_critical_anomaly_count",
    "max_robust_score",
    "anomaly_max_severity",
    "anomaly_controller_status",

    # EBITDA root cause
    "ebitda_root_cause_variance",
    "ebitda_root_cause_primary_account",
    "ebitda_root_cause_primary_driver",
    "ebitda_root_cause_primary_variance",
    "ebitda_root_cause_primary_contribution_pct",
    "ebitda_root_cause_interpretation",

    # Net profit root cause
    "net_profit_root_cause_variance",
    "net_profit_root_cause_primary_account",
    "net_profit_root_cause_primary_driver",
    "net_profit_root_cause_primary_variance",
    "net_profit_root_cause_primary_contribution_pct",
    "net_profit_root_cause_interpretation",

    # Operating costs root cause
    "operating_costs_root_cause_variance",
    "operating_costs_root_cause_primary_account",
    "operating_costs_root_cause_primary_driver",
    "operating_costs_root_cause_primary_variance",
    "operating_costs_root_cause_primary_contribution_pct",
    "operating_costs_root_cause_interpretation",

    # Revenue root cause
    "revenue_root_cause_variance",
    "revenue_root_cause_primary_account",
    "revenue_root_cause_primary_driver",
    "revenue_root_cause_primary_variance",
    "revenue_root_cause_primary_contribution_pct",
    "revenue_root_cause_interpretation",

    # Revenue PVM
    "revenue_pvm_total_variance",
    "revenue_pvm_price_effect",
    "revenue_pvm_volume_effect",
    "revenue_pvm_mix_effect",
    "revenue_pvm_reconciliation_check",
    "revenue_pvm_top_driver_account",
    "revenue_pvm_top_driver_name",
    "revenue_pvm_top_driver_variance",
    "revenue_pvm_price_status",
    "revenue_pvm_volume_status",
    "revenue_pvm_mix_status",

    # Revenue ML
    "revenue_prediction_rmse",
    "revenue_prediction_mape_pct",
    "ml_predicted_revenue",
    "ml_revenue_lower_bound",
    "ml_revenue_upper_bound",

    # Expense ML
    "ml_predicted_expense_magnitude",
    "expense_prediction_rmse",
    "ml_predicted_operating_costs",
    "ml_expense_lower_bound",
    "ml_expense_upper_bound",

    # Cash Flow ML
    "ml_predicted_operating_cf",
    "ml_predicted_closing_cash",
    "ml_ocf_lower_bound",
    "ml_ocf_upper_bound",
    "ml_cash_lower_bound",
    "ml_cash_upper_bound",
    "cash_prediction_rmse",
    "cash_prediction_mape_pct",

    # Classification
    "anomaly_risk_predicted",
    "anomaly_risk_confidence",
]


# ============================================================
# FINAL DATASET
# ============================================================

def build_reporting_dataset(
    sources: dict[str, pd.DataFrame],
) -> pd.DataFrame:

    actual_cutoff = determine_actual_cutoff(
        sources[
            "controller_timeseries"
        ]
    )

    result = build_monthly_calendar(
        sources,
        actual_cutoff,
    )

    # --------------------------------------------------------
    # Prepare all datasets
    # --------------------------------------------------------

    rolling = prepare_rolling_forecast(
        sources["rolling_forecast"]
    )

    anomaly = prepare_anomaly(
        sources["anomaly"]
    )

    variance = prepare_variance(
        sources["variance"]
    )

    pvm = prepare_pvm(
        sources["pvm"]
    )

    revenue_prediction = prepare_revenue_prediction(
        sources["revenue_prediction"]
    )

    expense_prediction = prepare_expense_prediction(
        sources["expense_prediction"]
    )

    cash_prediction = prepare_cash_prediction(
        sources["cash_prediction"]
    )

    classification = prepare_classification(
        sources["classification"]
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
    # Remove contextually invalid metrics
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
    # Prediction completeness
    # --------------------------------------------------------

    validate_forecast_predictions(
        result
    )

    # --------------------------------------------------------
    # Final ordering
    # --------------------------------------------------------

    missing_final_columns = [
        column
        for column in FINAL_COLUMNS
        if column not in result.columns
    ]

    if missing_final_columns:

        logger.warning(
            "Final schema columns missing from source consolidation: %s",
            missing_final_columns,
        )

        for column in missing_final_columns:
            result[column] = pd.NA

    result = result[
        FINAL_COLUMNS
    ].copy()

    # --------------------------------------------------------
    # Final sort
    # --------------------------------------------------------

    result = (
        result
        .sort_values("period")
        .reset_index(drop=True)
    )

    # --------------------------------------------------------
    # Grain validation
    # --------------------------------------------------------

    if result["period"].duplicated().any():

        raise RuntimeError(
            "Final dataset contains duplicate months."
        )

    return result


# ============================================================
# FINAL VALIDATION LOG
# ============================================================

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

    forecast = df[
        df["reporting_data_type"]
        == "FORECAST"
    ].copy()

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

    # --------------------------------------------------------
    # Forecast diagnostics
    # --------------------------------------------------------

    if not forecast.empty:

        logger.info(
            "Forecast revenue sample:\n%s",
            forecast[
                [
                    "period",
                    "ml_predicted_revenue",
                    "ml_revenue_lower_bound",
                    "ml_revenue_upper_bound",
                ]
            ]
            .to_string(index=False)
        )

        logger.info(
            "Forecast expense sample:\n%s",
            forecast[
                [
                    "period",
                    "ml_predicted_expense_magnitude",
                    "ml_predicted_operating_costs",
                ]
            ]
            .to_string(index=False)
        )

        logger.info(
            "Forecast cash sample:\n%s",
            forecast[
                [
                    "period",
                    "ml_predicted_operating_cf",
                    "ml_predicted_closing_cash",
                ]
            ]
            .to_string(index=False)
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