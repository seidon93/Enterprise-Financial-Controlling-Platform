"""
EFAP - Financial Anomaly Driver Analysis

Object:
    Python/anomaly_detection/explain_financial_anomalies.py

Purpose:
    Explain detected financial anomalies by identifying the
    strongest contributing financial drivers.

Input:
    data/analytics/financial_anomalies.csv

PostgreSQL sources:
    mart.vw_pnl_monthly
    mart.dim_pnl_management_mapping
    mart.vw_balance_sheet_detail
    mart.vw_working_capital_monthly
    mart.vw_cash_flow_monthly
    mart.vw_management_pnl

Output:
    data/analytics/financial_anomaly_drivers.csv

Principle:
    This module performs contribution analysis.
    It does not claim statistical causality or fraud detection.
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


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT: Final[Path] = (
    Path(__file__).resolve().parents[3]
)

ENV_FILE: Final[Path] = (
    PROJECT_ROOT / ".env"
)

ANOMALY_FILE: Final[Path] = (
    PROJECT_ROOT
    / "data"
    / "analytics"
    / "financial_anomalies.csv"
)

OUTPUT_DIR: Final[Path] = (
    PROJECT_ROOT
    / "data"
    / "analytics"
)

OUTPUT_FILE: Final[Path] = (
    OUTPUT_DIR
    / "financial_anomaly_drivers.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

TOP_N_DRIVERS: Final[int] = 5

BASELINE_MONTHS: Final[int] = 12

MIN_BASELINE_MONTHS: Final[int] = 6


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

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "EFAP"),
    "user": os.getenv("DB_USER", ""),
    "password": os.getenv("DB_PASSWORD", ""),
}


# ============================================================
# DATABASE
# ============================================================

def validate_db_config() -> None:
    """Validate database configuration."""

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


def load_sql(
    connection,
    query: str,
) -> pd.DataFrame:
    """Execute SQL and return dataframe."""

    return pd.read_sql_query(
        query,
        connection,
    )


# ============================================================
# INPUT
# ============================================================

def load_anomalies() -> pd.DataFrame:
    """Load detected anomaly records."""

    if not ANOMALY_FILE.exists():
        raise FileNotFoundError(
            f"Anomaly file not found: {ANOMALY_FILE}"
        )

    df = pd.read_csv(
        ANOMALY_FILE
    )

    required = {
        "period",
        "metric",
        "metric_label",
        "actual_value",
        "baseline_median",
        "anomaly_flag",
        "combined_anomaly",
    }

    missing = (
        required - set(df.columns)
    )

    if missing:
        raise ValueError(
            "Anomaly dataset is missing columns: "
            + ", ".join(sorted(missing))
        )

    df["period"] = pd.to_datetime(
        df["period"],
        errors="coerce",
    )

    df["actual_value"] = pd.to_numeric(
        df["actual_value"],
        errors="coerce",
    )

    df["baseline_median"] = pd.to_numeric(
        df["baseline_median"],
        errors="coerce",
    )

    df = df[
        df["combined_anomaly"] == True
    ].copy()

    df = df.dropna(
        subset=[
            "period",
            "metric",
            "actual_value",
        ]
    )

    return df.reset_index(
        drop=True
    )


# ============================================================
# SQL SOURCES
# ============================================================

P_AND_L_QUERY: Final[str] = """
SELECT
    p.calendar_year,
    p.calendar_month,
    p.year_month,

    p.account_number,
    p.account_name,

    m.management_group,
    m.management_line,
    m.management_sign,

    SUM(
        p.signed_amount
        * m.management_sign
    ) AS management_amount

FROM mart.vw_pnl_monthly p

INNER JOIN mart.dim_pnl_management_mapping m
    ON p.account_number::text = m.account_number::text

WHERE
    m.is_active = TRUE

GROUP BY
    p.calendar_year,
    p.calendar_month,
    p.year_month,
    p.account_number,
    p.account_name,
    m.management_group,
    m.management_line,
    m.management_sign;
"""


BALANCE_SHEET_QUERY: Final[str] = """
SELECT
    calendar_year,
    calendar_month,
    year_month,

    account_number,
    account_name,

    reporting_group,
    reporting_category,

    closing_balance

FROM mart.vw_balance_sheet_detail;
"""


WORKING_CAPITAL_QUERY: Final[str] = """
SELECT
    calendar_year,
    calendar_month,
    year_month,

    cash_balance,
    inventory_balance,
    receivables_balance,
    other_current_assets_balance,
    current_liabilities_balance,
    net_working_capital,
    operating_working_capital

FROM mart.vw_working_capital_monthly;
"""


CASH_FLOW_QUERY: Final[str] = """
SELECT
    calendar_year,
    calendar_month,
    year_month,

    net_profit,
    operating_cash_flow,
    investing_cash_flow,
    financing_cash_flow,
    net_cash_change

FROM mart.vw_cash_flow_monthly;
"""


# ============================================================
# PREPARATION
# ============================================================

def prepare_pnl(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Prepare P&L driver dataset."""

    df = df.copy()

    df["period"] = pd.to_datetime(
        df["year_month"] + "-01"
    )

    df["account_number"] = pd.to_numeric(
        df["account_number"],
        errors="coerce",
    ).astype("Int64")

    df["management_amount"] = pd.to_numeric(
        df["management_amount"],
        errors="coerce",
    )

    return df.dropna(
        subset=["period"]
    )


def prepare_balance_sheet(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Prepare Balance Sheet driver dataset."""

    df = df.copy()

    df["period"] = pd.to_datetime(
        df["year_month"] + "-01"
    )

    df["closing_balance"] = pd.to_numeric(
        df["closing_balance"],
        errors="coerce",
    )

    return df


# ============================================================
# BASELINE
# ============================================================

def calculate_driver_baseline(
    df: pd.DataFrame,
    value_column: str,
    group_columns: list[str],
) -> pd.DataFrame:
    """
    Calculate previous-period rolling median baseline.

    The current period is excluded from the baseline.
    """

    df = df.sort_values(
        group_columns + ["period"]
    ).copy()

    grouped = (
        df
        .groupby(
            group_columns,
            group_keys=False,
        )
    )

    df["driver_baseline"] = (
        grouped[value_column]
        .transform(
            lambda series:
            series
            .shift(1)
            .rolling(
                window=BASELINE_MONTHS,
                min_periods=MIN_BASELINE_MONTHS,
            )
            .median()
        )
    )

    return df


# ============================================================
# P&L DRIVER ANALYSIS
# ============================================================

def explain_pnl_metric(
    anomaly: pd.Series,
    pnl: pd.DataFrame,
) -> pd.DataFrame:
    """Explain P&L anomaly using account contributions."""

    metric = str(
        anomaly["metric"]
    )

    period = pd.Timestamp(
        anomaly["period"]
    )

    actual_value = float(
        anomaly["actual_value"]
    )

    baseline_value = float(
        anomaly.get(
            "baseline_median",
            np.nan,
        )
    )

    month_data = pnl[
        pnl["period"] == period
    ].copy()

    if month_data.empty:
        return pd.DataFrame()

    # --------------------------------------------------------
    # Driver selection
    # --------------------------------------------------------

    if metric == "revenue":

        month_data = month_data[
            month_data["management_group"]
            == "Revenue"
        ]

    elif metric == "operating_costs":

        month_data = month_data[
            month_data["management_group"]
            == "Operating Costs"
        ]

    elif metric == "ebitda":

        month_data = month_data[
            month_data["management_group"].isin(
                [
                    "Revenue",
                    "Other Operating Income",
                    "Operating Costs",
                    "Non-Core Operating Items",
                ]
            )
        ]

    elif metric == "net_profit":

        month_data = month_data[
            month_data["management_group"].isin(
                [
                    "Revenue",
                    "Other Operating Income",
                    "Operating Costs",
                    "Non-Core Operating Items",
                    "EBITDA Adjustments",
                    "Financial Result",
                    "Tax",
                ]
            )
        ]

    else:
        return pd.DataFrame()

    if month_data.empty:
        return pd.DataFrame()

    # --------------------------------------------------------
    # Driver baseline
    # --------------------------------------------------------

    driver_group_columns = [
        "account_number",
        "account_name",
        "management_group",
        "management_line",
    ]

    baseline_source = pnl[
        pnl["account_number"].isin(
            month_data["account_number"]
        )
    ].copy()

    baseline_source = calculate_driver_baseline(
        baseline_source,
        value_column="management_amount",
        group_columns=driver_group_columns,
    )

    baseline_month = baseline_source[
        baseline_source["period"] == period
    ][
        driver_group_columns
        + [
            "management_amount",
            "driver_baseline",
        ]
    ].copy()

    if baseline_month.empty:
        return pd.DataFrame()

    baseline_month["driver_variance"] = (
        baseline_month["management_amount"]
        - baseline_month["driver_baseline"]
    )

    # First-period observations have no baseline.
    baseline_month = baseline_month.dropna(
        subset=["driver_baseline"]
    )

    if baseline_month.empty:
        return pd.DataFrame()

    # --------------------------------------------------------
    # Contribution
    # --------------------------------------------------------

    total_abs_variance = (
        baseline_month[
            "driver_variance"
        ]
        .abs()
        .sum()
    )

    if total_abs_variance == 0:
        return pd.DataFrame()

    baseline_month[
        "contribution_pct"
    ] = (
        baseline_month[
            "driver_variance"
        ]
        .abs()
        / total_abs_variance
        * 100
    )

    baseline_month = (
        baseline_month
        .sort_values(
            "contribution_pct",
            ascending=False,
        )
        .head(TOP_N_DRIVERS)
        .copy()
    )

    # --------------------------------------------------------
    # Direction
    # --------------------------------------------------------

    def direction(
        value: float,
    ) -> str:

        if value > 0:
            return "POSITIVE"

        if value < 0:
            return "NEGATIVE"

        return "NEUTRAL"

    baseline_month["driver_direction"] = (
        baseline_month[
            "driver_variance"
        ]
        .apply(direction)
    )

    # --------------------------------------------------------
    # Output
    # --------------------------------------------------------

    baseline_month["period"] = period
    baseline_month["metric"] = metric
    baseline_month["metric_label"] = (
        anomaly["metric_label"]
    )

    baseline_month["anomaly_value"] = (
        actual_value
    )

    baseline_month["anomaly_baseline"] = (
        baseline_value
    )

    baseline_month["anomaly_deviation"] = (
        actual_value - baseline_value
    )

    baseline_month["driver_type"] = (
        "ACCOUNT"
    )

    baseline_month["root_cause_status"] = (
        "DRIVER_IDENTIFIED"
    )

    baseline_month["explanation_level"] = (
        "P&L_ACCOUNT"
    )

    return baseline_month[
        [
            "period",
            "metric",
            "metric_label",

            "anomaly_value",
            "anomaly_baseline",
            "anomaly_deviation",

            "driver_type",
            "account_number",
            "account_name",
            "management_group",
            "management_line",

            "management_amount",
            "driver_baseline",
            "driver_variance",
            "contribution_pct",

            "driver_direction",

            "root_cause_status",
            "explanation_level",
        ]
    ].rename(
        columns={
            "management_amount":
                "driver_actual",
            "driver_baseline":
                "driver_expected",
        }
    )


# ============================================================
# WORKING CAPITAL DRIVERS
# ============================================================

def explain_working_capital_metric(
    anomaly: pd.Series,
    working_capital: pd.DataFrame,
) -> pd.DataFrame:
    """Explain Working Capital anomalies."""

    metric = str(
        anomaly["metric"]
    )

    period = pd.Timestamp(
        anomaly["period"]
    )

    if metric not in {
        "closing_cash",
        "net_working_capital",
    }:
        return pd.DataFrame()

    month_data = working_capital[
        working_capital["period"] == period
    ].copy() if "period" in working_capital.columns else None

    if month_data is None or month_data.empty:
        return pd.DataFrame()

    if metric == "closing_cash":

        driver_map = {
            "cash_balance": "Cash",
            "receivables_balance": "Receivables",
            "inventory_balance": "Inventory",
            "other_current_assets_balance":
                "Other Current Assets",
            "current_liabilities_balance":
                "Current Liabilities",
        }

    else:

        driver_map = {
            "receivables_balance":
                "Receivables",
            "inventory_balance":
                "Inventory",
            "other_current_assets_balance":
                "Other Current Assets",
            "current_liabilities_balance":
                "Current Liabilities",
        }

    result_rows = []

    for column, label in driver_map.items():

        value = float(
            month_data.iloc[0][column]
        )

        previous = (
            working_capital[
                working_capital["period"] < period
            ]
            .sort_values("period")
            .tail(BASELINE_MONTHS)
        )

        if previous.empty:
            continue

        baseline = float(
            previous[column].median()
        )

        variance = (
            value - baseline
        )

        result_rows.append(
            {
                "period": period,
                "metric": metric,
                "metric_label":
                    anomaly["metric_label"],

                "anomaly_value":
                    anomaly["actual_value"],

                "anomaly_baseline":
                    anomaly["baseline_median"],

                "anomaly_deviation":
                    (
                        anomaly["actual_value"]
                        - anomaly["baseline_median"]
                    ),

                "driver_type":
                    "WORKING_CAPITAL_COMPONENT",

                "account_number":
                    None,

                "account_name":
                    label,

                "management_group":
                    "Working Capital",

                "management_line":
                    label,

                "driver_actual":
                    value,

                "driver_expected":
                    baseline,

                "driver_variance":
                    variance,

                "contribution_pct":
                    0.0,

                "driver_direction":
                    (
                        "POSITIVE"
                        if variance > 0
                        else "NEGATIVE"
                        if variance < 0
                        else "NEUTRAL"
                    ),

                "root_cause_status":
                    "DRIVER_IDENTIFIED",

                "explanation_level":
                    "WORKING_CAPITAL_COMPONENT",
            }
        )

    result = pd.DataFrame(
        result_rows
    )

    if result.empty:
        return result

    total_abs = (
        result["driver_variance"]
        .abs()
        .sum()
    )

    if total_abs > 0:

        result["contribution_pct"] = (
            result["driver_variance"]
            .abs()
            / total_abs
            * 100
        )

    return (
        result
        .sort_values(
            "contribution_pct",
            ascending=False,
        )
        .head(TOP_N_DRIVERS)
    )


# ============================================================
# CASH FLOW DRIVERS
# ============================================================

def explain_cash_flow_metric(
    anomaly: pd.Series,
    cash_flow: pd.DataFrame,
) -> pd.DataFrame:
    """Explain cash flow anomalies."""

    metric = str(
        anomaly["metric"]
    )

    if metric not in {
        "operating_cash_flow",
        "free_cash_flow",
    }:
        return pd.DataFrame()

    period = pd.Timestamp(
        anomaly["period"]
    )

    month = cash_flow[
        cash_flow["period"] == period
    ]

    history = cash_flow[
        cash_flow["period"] < period
    ].sort_values(
        "period"
    ).tail(
        BASELINE_MONTHS
    )

    if month.empty or history.empty:
        return pd.DataFrame()

    driver_columns = {
        "net_profit":
            "Net Profit",
        "operating_cash_flow":
            "Operating Cash Flow",
        "investing_cash_flow":
            "Investing Cash Flow",
        "financing_cash_flow":
            "Financing Cash Flow",
    }

    rows = []

    for column, label in driver_columns.items():

        actual = float(
            month.iloc[0][column]
        )

        expected = float(
            history[column].median()
        )

        variance = (
            actual - expected
        )

        rows.append(
            {
                "period": period,
                "metric": metric,
                "metric_label":
                    anomaly["metric_label"],

                "anomaly_value":
                    anomaly["actual_value"],

                "anomaly_baseline":
                    anomaly["baseline_median"],

                "anomaly_deviation":
                    (
                        anomaly["actual_value"]
                        - anomaly["baseline_median"]
                    ),

                "driver_type":
                    "CASH_FLOW_COMPONENT",

                "account_number":
                    None,

                "account_name":
                    label,

                "management_group":
                    "Cash Flow",

                "management_line":
                    label,

                "driver_actual":
                    actual,

                "driver_expected":
                    expected,

                "driver_variance":
                    variance,

                "driver_direction":
                    (
                        "POSITIVE"
                        if variance > 0
                        else "NEGATIVE"
                        if variance < 0
                        else "NEUTRAL"
                    ),

                "root_cause_status":
                    "DRIVER_IDENTIFIED",

                "explanation_level":
                    "CASH_FLOW_COMPONENT",
            }
        )

    result = pd.DataFrame(
        rows
    )

    if result.empty:
        return result

    total_abs = (
        result["driver_variance"]
        .abs()
        .sum()
    )

    result["contribution_pct"] = np.where(
        total_abs > 0,
        result["driver_variance"].abs()
        / total_abs
        * 100,
        0,
    )

    return (
        result
        .sort_values(
            "contribution_pct",
            ascending=False,
        )
        .head(TOP_N_DRIVERS)
    )


# ============================================================
# DRIVER ORCHESTRATION
# ============================================================

def explain_anomaly(
    anomaly: pd.Series,
    pnl: pd.DataFrame,
    working_capital: pd.DataFrame,
    cash_flow: pd.DataFrame,
) -> pd.DataFrame:
    """Select appropriate driver analysis."""

    metric = str(
        anomaly["metric"]
    )

    pnl_metrics = {
        "revenue",
        "operating_costs",
        "ebitda",
        "net_profit",
    }

    working_capital_metrics = {
        "closing_cash",
        "net_working_capital",
    }

    cash_flow_metrics = {
        "operating_cash_flow",
        "free_cash_flow",
    }

    if metric in pnl_metrics:

        return explain_pnl_metric(
            anomaly,
            pnl,
        )

    if metric in working_capital_metrics:

        return explain_working_capital_metric(
            anomaly,
            working_capital,
        )

    if metric in cash_flow_metrics:

        return explain_cash_flow_metric(
            anomaly,
            cash_flow,
        )

    # Ratios such as DSO/DIO/DPO/CCC do not have a sufficiently
    # reliable driver decomposition at this stage.
    return pd.DataFrame()


# ============================================================
# MAIN
# ============================================================

def main() -> int:
    """Run anomaly driver analysis."""

    connection = None

    try:

        logger.info(
            "Starting EFAP Anomaly Driver Analysis."
        )

        anomalies = load_anomalies()

        if anomalies.empty:
            logger.warning(
                "No anomalies found. "
                "Driver analysis will produce an empty dataset."
            )

            OUTPUT_DIR.mkdir(
                parents=True,
                exist_ok=True,
            )

            pd.DataFrame().to_csv(
                OUTPUT_FILE,
                index=False,
            )

            return 0

        connection = get_connection()

        logger.info(
            "Loading P&L driver data."
        )

        pnl = load_sql(
            connection,
            P_AND_L_QUERY,
        )

        logger.info(
            "Loading Working Capital data."
        )

        working_capital = load_sql(
            connection,
            WORKING_CAPITAL_QUERY,
        )

        working_capital["period"] = pd.to_datetime(
            working_capital["year_month"]
            + "-01"
        )

        logger.info(
            "Loading Cash Flow data."
        )

        cash_flow = load_sql(
            connection,
            CASH_FLOW_QUERY,
        )

        cash_flow["period"] = pd.to_datetime(
            cash_flow["year_month"]
            + "-01"
        )

        pnl = prepare_pnl(
            pnl
        )

        working_capital = working_capital.copy()

        if "period" not in working_capital:
            working_capital["period"] = pd.to_datetime(
                working_capital["year_month"]
                + "-01"
            )

        outputs = []

        for _, anomaly in anomalies.iterrows():

            logger.info(
                "Explaining %s anomaly for %s",
                anomaly["metric_label"],
                anomaly["period"].strftime(
                    "%Y-%m"
                ),
            )

            result = explain_anomaly(
                anomaly=anomaly,
                pnl=pnl,
                working_capital=working_capital,
                cash_flow=cash_flow,
            )

            if not result.empty:
                outputs.append(
                    result
                )

        if outputs:

            final = pd.concat(
                outputs,
                ignore_index=True,
            )

            final = final.sort_values(
                [
                    "period",
                    "metric",
                    "contribution_pct",
                ],
                ascending=[
                    True,
                    True,
                    False,
                ],
            )

        else:

            final = pd.DataFrame(
                columns=[
                    "period",
                    "metric",
                    "metric_label",
                    "anomaly_value",
                    "anomaly_baseline",
                    "anomaly_deviation",
                    "driver_type",
                    "account_number",
                    "account_name",
                    "management_group",
                    "management_line",
                    "driver_actual",
                    "driver_expected",
                    "driver_variance",
                    "contribution_pct",
                    "driver_direction",
                    "root_cause_status",
                    "explanation_level",
                ]
            )

        OUTPUT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        final.to_csv(
            OUTPUT_FILE,
            index=False,
        )

        logger.info(
            "Saved anomaly drivers to %s",
            OUTPUT_FILE,
        )

        logger.info(
            "Generated %s driver records.",
            len(final),
        )

        return 0

    except Exception as exc:

        logger.exception(
            "Anomaly Driver Analysis failed: %s",
            exc,
        )

        return 1

    finally:

        if connection is not None:
            connection.close()

            logger.info(
                "PostgreSQL connection closed."
            )


if __name__ == "__main__":
    sys.exit(main())