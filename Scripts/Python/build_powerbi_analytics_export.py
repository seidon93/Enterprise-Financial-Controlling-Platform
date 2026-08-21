"""
EFAP - Power BI Analytics Reporting Export

Purpose:
    Consolidate Python analytical outputs into one Power BI-ready
    monthly reporting dataset.

Grain:
    Exactly one row per calendar month.

Important semantic rules:

    ACTUAL periods:
        - anomalies
        - variance root cause
        - PVM
        - historical analytics
        - ML outputs only where they exist

    FORECAST periods:
        - rolling forecast
        - ML predictions
        - no actual anomaly/root-cause/PVM interpretation

Output:
    data/powerbi/efap_analytics_reporting.csv
"""

from __future__ import annotations

import logging
from pathlib import Path
import sys

import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = (
    Path(__file__).resolve().parents[2]
)

ANALYTICS_DIR = (
    PROJECT_ROOT
    / "Data"
    / "analytics"
)

FORECAST_DIR = (
    PROJECT_ROOT
    / "Data"
    / "forecasts"
)

PREDICTION_DIR = (
    PROJECT_ROOT
    / "Data"
    / "predictions"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "Data"
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
# LOAD HELPERS
# ============================================================

def load_optional_csv(
    path: Path,
) -> pd.DataFrame:
    """
    Load optional analytical CSV.

    Missing datasets do not stop the export pipeline.
    """

    if not path.exists():

        logger.warning(
            "Optional analytical file not found: %s",
            path,
        )

        return pd.DataFrame()

    logger.info(
        "Loading %s",
        path,
    )

    return pd.read_csv(path)


def normalize_period(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Normalize period to pandas datetime."""

    if df.empty:
        return df

    df = df.copy()

    if "period" in df.columns:

        df["period"] = pd.to_datetime(
            df["period"],
            errors="coerce",
        )

    return df


# ============================================================
# LOAD ALL SOURCES
# ============================================================

def load_all_sources() -> dict[str, pd.DataFrame]:

    return {

        "rolling_forecast":
            normalize_period(
                load_optional_csv(
                    FORECAST_DIR
                    / "rolling_forecast.csv"
                )
            ),

        "anomaly":
            normalize_period(
                load_optional_csv(
                    ANALYTICS_DIR
                    / "financial_anomaly_monthly_summary.csv"
                )
            ),

        "variance":
            normalize_period(
                load_optional_csv(
                    ANALYTICS_DIR
                    / "variance_root_cause_controller_summary.csv"
                )
            ),

        "pvm":
            normalize_period(
                load_optional_csv(
                    ANALYTICS_DIR
                    / "price_volume_summary.csv"
                )
            ),

        "revenue_prediction":
            normalize_period(
                load_optional_csv(
                    PREDICTION_DIR
                    / "revenue_prediction.csv"
                )
            ),

        "expense_prediction":
            normalize_period(
                load_optional_csv(
                    PREDICTION_DIR
                    / "expense_prediction.csv"
                )
            ),

        "cash_prediction":
            normalize_period(
                load_optional_csv(
                    PREDICTION_DIR
                    / "cash_flow_prediction.csv"
                )
            ),

        "classification":
            normalize_period(
                load_optional_csv(
                    PREDICTION_DIR
                    / "financial_classification_predictions.csv"
                )
            ),
    }


# ============================================================
# ACTUAL / FORECAST BOUNDARY
# ============================================================

def determine_actual_cutoff(
    rolling_forecast: pd.DataFrame,
) -> pd.Timestamp:
    """
    Determine the last actual month from rolling forecast data.

    The rolling forecast dataset explicitly contains:
        ACTUAL
        FORECAST

    Therefore it is the authoritative boundary for the
    Power BI reporting dataset.
    """

    if rolling_forecast.empty:
        raise RuntimeError(
            "Rolling forecast dataset is required to determine "
            "ACTUAL / FORECAST boundary."
        )

    required = {
        "period",
        "data_type",
    }

    missing = (
        required
        - set(rolling_forecast.columns)
    )

    if missing:
        raise ValueError(
            "Rolling forecast is missing columns: "
            + ", ".join(sorted(missing))
        )

    actual = rolling_forecast[
        rolling_forecast["data_type"]
        .astype(str)
        .str.upper()
        .eq("ACTUAL")
    ]

    if actual.empty:
        raise RuntimeError(
            "No ACTUAL periods found in rolling forecast."
        )

    cutoff = actual[
        "period"
    ].max()

    logger.info(
        "Last ACTUAL period: %s",
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
    Create one unique row per reporting month.
    """

    periods = []

    for df in sources.values():

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

    if not periods:
        raise RuntimeError(
            "No reporting periods available."
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

    # --------------------------------------------------------
    # Explicit reporting type
    # --------------------------------------------------------

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
        "ebitda",
        "ebitda_margin",
    }

    missing = required - set(df.columns)

    if missing:
        logger.warning(
            "Rolling forecast missing columns: %s",
            ", ".join(sorted(missing)),
        )

        return pd.DataFrame()

    result = (
        df[
            [
                "period",
                "data_type",
                "forecast_horizon_month",
                "revenue",
                "operating_costs",
                "ebitda",
                "ebitda_margin",
            ]
        ]
        .rename(
            columns={
                "data_type":
                    "rolling_data_type",

                "revenue":
                    "rolling_revenue",

                "operating_costs":
                    "rolling_operating_costs",

                "ebitda":
                    "rolling_ebitda",

                "ebitda_margin":
                    "rolling_ebitda_margin",
            }
        )
    )

    # Guarantee one row per period.
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

    return (
        df[
            [
                column
                for column in [
                    "period",
                    "anomaly_count",
                    "high_critical_anomaly_count",
                    "max_robust_score",
                    "max_severity",
                    "controller_status",
                ]
                if column in df.columns
            ]
        ]
        .rename(
            columns={
                "max_severity":
                    "anomaly_max_severity",

                "controller_status":
                    "anomaly_controller_status",
            }
        )
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

    return pd.DataFrame(rows)


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

    return pd.DataFrame(rows)


# ============================================================
# REVENUE PREDICTION
# ============================================================

def prepare_revenue_prediction(
    df: pd.DataFrame,
) -> pd.DataFrame:

    if df.empty:
        return pd.DataFrame()

    required = {
        "period",
        "predicted_revenue",
        "lower_bound",
        "upper_bound",
        "validation_rmse",
        "validation_mape_pct",
    }

    missing = required - set(df.columns)

    if missing:
        logger.warning(
            "Revenue prediction missing columns: %s",
            ", ".join(sorted(missing)),
        )

        return pd.DataFrame()

    return (
        df[
            [
                "period",
                "predicted_revenue",
                "lower_bound",
                "upper_bound",
                "validation_rmse",
                "validation_mape_pct",
            ]
        ]
        .rename(
            columns={
                "predicted_revenue":
                    "ml_predicted_revenue",

                "lower_bound":
                    "ml_revenue_lower_bound",

                "upper_bound":
                    "ml_revenue_upper_bound",

                "validation_rmse":
                    "revenue_prediction_rmse",

                "validation_mape_pct":
                    "revenue_prediction_mape_pct",
            }
        )
        .drop_duplicates("period")
    )


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

    missing = required - set(df.columns)

    if missing:
        logger.warning(
            "Expense prediction missing columns: %s",
            ", ".join(sorted(missing)),
        )

        return pd.DataFrame()

    return (
        df
        .groupby(
            "period",
            as_index=False,
        )
        .agg(
            ml_predicted_expenses=(
                "predicted_expense",
                "sum",
            ),

            ml_expense_lower_bound=(
                "lower_bound",
                "sum",
            ),

            ml_expense_upper_bound=(
                "upper_bound",
                "sum",
            ),

            expense_prediction_rmse=(
                "validation_rmse",
                "mean",
            ),
        )
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

    missing = required - set(df.columns)

    if missing:
        logger.warning(
            "Cash prediction missing columns: %s",
            ", ".join(sorted(missing)),
        )

        return pd.DataFrame()

    return (
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
        .drop_duplicates("period")
    )


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
        .drop_duplicates("period")
    )


# ============================================================
# MERGE ONE-ROW-PER-MONTH DATASETS
# ============================================================

def safe_merge(
    base: pd.DataFrame,
    dataset: pd.DataFrame,
    name: str,
) -> pd.DataFrame:
    """
    Merge only datasets that are guaranteed to have one row
    per period.
    """

    if dataset.empty:
        return base

    duplicated = (
        dataset["period"]
        .duplicated()
        .any()
    )

    if duplicated:

        raise RuntimeError(
            f"Dataset '{name}' still contains duplicate periods."
        )

    return base.merge(
        dataset,
        on="period",
        how="left",
        validate="one_to_one",
    )


# ============================================================
# FORECAST HORIZON VALIDATION
# ============================================================

def validate_forecast_horizon(
    df: pd.DataFrame,
    actual_cutoff: pd.Timestamp,
) -> None:
    """Validate number of future rolling forecast months."""

    future = df[
        (
            df["period"]
            > actual_cutoff
        )
        &
        (
            df["reporting_data_type"]
            == "FORECAST"
        )
    ].copy()

    if future.empty:

        logger.warning(
            "No future FORECAST months found."
        )

        return

    future_months = (
        future["period"]
        .sort_values()
        .drop_duplicates()
    )

    horizon = len(
        future_months
    )

    logger.info(
        "Detected forecast horizon: %s months.",
        horizon,
    )

    if horizon != EXPECTED_FORECAST_HORIZON:

        logger.warning(
            "Expected %s forecast months, "
            "found %s.",
            EXPECTED_FORECAST_HORIZON,
            horizon,
        )


# ============================================================
# FORECAST-ONLY SANITIZATION
# ============================================================

def clear_actual_only_metrics_for_forecast(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Remove actual-only interpretations from future months.

    These metrics must NOT be interpreted as known Actual vs
    Budget or Actual vs Prior Year values in forecast periods.
    """

    df = df.copy()

    forecast_mask = (
        df["reporting_data_type"]
        == "FORECAST"
    )

    # --------------------------------------------------------
    # Root Cause
    # --------------------------------------------------------

    root_cause_columns = [
        column
        for column in df.columns
        if (
            "_root_cause_"
            in column
        )
        or column.endswith(
            "_root_cause_variance"
        )
        or column.endswith(
            "_root_cause_interpretation"
        )
    ]

    # --------------------------------------------------------
    # PVM
    # --------------------------------------------------------

    pvm_columns = [
        column
        for column in df.columns
        if "_pvm_" in column
    ]

    columns_to_clear = sorted(
        set(
            root_cause_columns
            + pvm_columns
        )
    )

    if columns_to_clear:

        df.loc[
            forecast_mask,
            columns_to_clear,
        ] = pd.NA

    # --------------------------------------------------------
    # Anomaly historical classification
    # --------------------------------------------------------

    anomaly_columns = [
        column
        for column in df.columns
        if column.startswith(
            "anomaly_"
        )
    ]

    if anomaly_columns:

        df.loc[
            forecast_mask,
            anomaly_columns,
        ] = pd.NA

    return df


# ============================================================
# BUILD REPORTING DATASET
# ============================================================

def build_reporting_dataset(
    sources: dict[str, pd.DataFrame],
) -> pd.DataFrame:

    actual_cutoff = (
        determine_actual_cutoff(
            sources[
                "rolling_forecast"
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
    # Safe one-to-one merges
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
    # Validate forecast horizon
    # --------------------------------------------------------

    validate_forecast_horizon(
        result,
        actual_cutoff,
    )

    # --------------------------------------------------------
    # Clear future actual-only metrics
    # --------------------------------------------------------

    result = (
        clear_actual_only_metrics_for_forecast(
            result
        )
    )

    # --------------------------------------------------------
    # Final ordering
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

        duplicates = (
            result.loc[
                result["period"].duplicated(
                    keep=False
                ),
                "period",
            ]
            .dt.strftime("%Y-%m")
            .unique()
            .tolist()
        )

        raise RuntimeError(
            "Power BI reporting dataset contains duplicate "
            f"periods: {duplicates}"
        )

    return result


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
                "Reporting dataset is empty."
            )

        save_output(
            reporting
        )

        logger.info(
            "Generated %s rows and %s columns.",
            len(reporting),
            len(reporting.columns),
        )

        logger.info(
            "Power BI Analytics Export "
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
    sys.exit(main())