"""
EFAP - Power BI Analytics Reporting Export

Purpose:
    Consolidate Python analytical outputs into one Power BI-ready
    reporting dataset.

Sources:
    rolling_forecast.csv
    financial_anomaly_monthly_summary.csv
    variance_root_cause_controller_summary.csv
    price_volume_summary.csv
    revenue_prediction.csv
    expense_prediction.csv
    cash_flow_prediction.csv
    financial_classification_predictions.csv

Output:
    data/powerbi/efap_analytics_reporting.csv

Principle:
    This script does not recalculate financial logic.
    It only consolidates analytical outputs for Power BI.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

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
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# ============================================================
# HELPERS
# ============================================================

def load_optional_csv(
    path: Path,
) -> pd.DataFrame:
    """
    Load CSV if available.

    Missing analytical outputs do not stop the whole reporting
    export.
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


def add_period(
    df: pd.DataFrame,
    column: str = "period",
) -> pd.DataFrame:
    """Normalize period column."""

    if df.empty:
        return df

    if column in df.columns:
        df[column] = pd.to_datetime(
            df[column],
            errors="coerce",
        )

    return df


# ============================================================
# LOAD
# ============================================================

def load_all_sources() -> dict[str, pd.DataFrame]:

    return {

        "rolling_forecast":
            add_period(
                load_optional_csv(
                    FORECAST_DIR
                    / "rolling_forecast.csv"
                )
            ),

        "anomaly":
            add_period(
                load_optional_csv(
                    ANALYTICS_DIR
                    / "financial_anomaly_monthly_summary.csv"
                )
            ),

        "variance":
            add_period(
                load_optional_csv(
                    ANALYTICS_DIR
                    / "variance_root_cause_controller_summary.csv"
                )
            ),

        "pvm":
            add_period(
                load_optional_csv(
                    ANALYTICS_DIR
                    / "price_volume_summary.csv"
                )
            ),

        "revenue_prediction":
            add_period(
                load_optional_csv(
                    PREDICTION_DIR
                    / "revenue_prediction.csv"
                )
            ),

        "expense_prediction":
            add_period(
                load_optional_csv(
                    PREDICTION_DIR
                    / "expense_prediction.csv"
                )
            ),

        "cash_prediction":
            add_period(
                load_optional_csv(
                    PREDICTION_DIR
                    / "cash_flow_prediction.csv"
                )
            ),

        "classification":
            add_period(
                load_optional_csv(
                    PREDICTION_DIR
                    / "financial_classification_predictions.csv"
                )
            ),
    }


# ============================================================
# MONTHLY FRAME
# ============================================================

def build_monthly_calendar(
    sources: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Create common monthly reporting calendar."""

    periods = []

    for df in sources.values():

        if df.empty:
            continue

        if "period" in df.columns:

            values = (
                df["period"]
                .dropna()
                .unique()
            )

            periods.extend(
                values.tolist()
            )

    if not periods:
        raise RuntimeError(
            "No analytical periods available."
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

    return calendar


# ============================================================
# AGGREGATIONS
# ============================================================

def prepare_revenue_prediction(
    df: pd.DataFrame,
) -> pd.DataFrame:

    if df.empty:
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
    )


def prepare_expense_prediction(
    df: pd.DataFrame,
) -> pd.DataFrame:

    if df.empty:
        return pd.DataFrame()

    result = (
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

    return result


def prepare_cash_prediction(
    df: pd.DataFrame,
) -> pd.DataFrame:

    if df.empty:
        return pd.DataFrame()

    return df[
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
    ].rename(
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


def prepare_rolling_forecast(
    df: pd.DataFrame,
) -> pd.DataFrame:

    if df.empty:
        return pd.DataFrame()

    return df[
        [
            "period",
            "data_type",
            "forecast_horizon_month",
            "revenue",
            "operating_costs",
            "ebitda",
            "ebitda_margin",
        ]
    ].rename(
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


def prepare_anomaly(
    df: pd.DataFrame,
) -> pd.DataFrame:

    if df.empty:
        return pd.DataFrame()

    return df.rename(
        columns={
            "anomaly_count":
                "anomaly_count",
            "high_or_critical_count":
                "high_critical_anomaly_count",
            "max_severity":
                "anomaly_max_severity",
            "controller_status":
                "anomaly_controller_status",
        }
    )


def prepare_variance(
    df: pd.DataFrame,
) -> pd.DataFrame:

    if df.empty:
        return pd.DataFrame()

    return df.rename(
        columns={
            "metric":
                "variance_metric",
            "total_variance":
                "root_cause_total_variance",
            "primary_driver_account":
                "root_cause_primary_account",
            "primary_driver_name":
                "root_cause_primary_driver",
            "primary_driver_variance":
                "root_cause_primary_variance",
            "primary_driver_contribution_pct":
                "root_cause_primary_contribution_pct",
            "controller_interpretation":
                "root_cause_controller_interpretation",
        }
    )[
        [
            "period",
            "variance_metric",
            "root_cause_total_variance",
            "root_cause_primary_account",
            "root_cause_primary_driver",
            "root_cause_primary_variance",
            "root_cause_primary_contribution_pct",
            "root_cause_controller_interpretation",
        ]
    ]


def prepare_pvm(
    df: pd.DataFrame,
) -> pd.DataFrame:

    if df.empty:
        return pd.DataFrame()

    return df.rename(
        columns={
            "total_variance":
                "pvm_total_variance",
            "price_effect":
                "pvm_price_effect",
            "volume_effect":
                "pvm_volume_effect",
            "mix_effect":
                "pvm_mix_effect",
            "top_driver_account":
                "pvm_top_driver_account",
            "top_driver_name":
                "pvm_top_driver_name",
            "top_driver_variance":
                "pvm_top_driver_variance",
        }
    )


def prepare_classification(
    df: pd.DataFrame,
) -> pd.DataFrame:

    if df.empty:
        return pd.DataFrame()

    return df


# ============================================================
# BUILD REPORTING DATASET
# ============================================================

def build_reporting_dataset(
    sources: dict[str, pd.DataFrame],
) -> pd.DataFrame:

    result = build_monthly_calendar(
        sources
    )

    prepared = [
        prepare_rolling_forecast(
            sources["rolling_forecast"]
        ),

        prepare_anomaly(
            sources["anomaly"]
        ),

        prepare_variance(
            sources["variance"]
        ),

        prepare_pvm(
            sources["pvm"]
        ),

        prepare_revenue_prediction(
            sources["revenue_prediction"]
        ),

        prepare_expense_prediction(
            sources["expense_prediction"]
        ),

        prepare_cash_prediction(
            sources["cash_prediction"]
        ),

        prepare_classification(
            sources["classification"]
        ),
    ]

    for dataset in prepared:

        if dataset.empty:
            continue

        result = result.merge(
            dataset,
            on="period",
            how="left",
        )

    return (
        result
        .sort_values("period")
        .reset_index(drop=True)
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
        "Power BI analytics export saved to %s",
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
            "Generated %s reporting rows "
            "and %s columns.",
            len(reporting),
            len(reporting.columns),
        )

        logger.info(
            "Power BI Analytics Export completed successfully."
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