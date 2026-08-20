"""
EFAP - Variance Root Cause Analysis

Object:
    Python/controlling/variance_root_cause.py

Purpose:
    Explain Actual vs Budget variance by identifying the
    largest account-level contributors.

Analysis:
    Revenue
    Operating Costs
    EBITDA
    Net Profit

Output:
    data/analytics/variance_root_causes.csv

Important:
    This module performs contribution analysis.
    It does not claim statistical causality.

Architecture:
    PostgreSQL / Mart
        ->
    Account Actual vs Budget
        ->
    Contribution analysis
        ->
    Top variance drivers
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

OUTPUT_DIR: Final[Path] = (
    PROJECT_ROOT
    / "data"
    / "analytics"
)

OUTPUT_FILE: Final[Path] = (
    OUTPUT_DIR
    / "variance_root_causes.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

TOP_N_DRIVERS: Final[int] = 10


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
# METRIC DEFINITIONS
# ============================================================

METRIC_GROUPS: Final[dict[str, list[str]]] = {
    "REVENUE": [
        "Revenue",
    ],

    "OPERATING_COSTS": [
        "Operating Costs",
    ],

    "EBITDA": [
        "Revenue",
        "Other Operating Income",
        "Operating Costs",
        "Non-Core Operating Items",
    ],

    "NET_PROFIT": [
        "Revenue",
        "Other Operating Income",
        "Operating Costs",
        "Non-Core Operating Items",
        "EBITDA Adjustments",
        "Financial Result",
        "Tax",
    ],
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


# ============================================================
# SOURCE QUERY
# ============================================================

SOURCE_QUERY: Final[str] = """
WITH actual AS (

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
        ) AS actual_amount

    FROM mart.vw_pnl_monthly p

    INNER JOIN mart.dim_pnl_management_mapping m
        ON p.account_number::text
         = m.account_number::text

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
        m.management_sign
),

budget AS (

    SELECT
        d.calendar_year,
        d.calendar_month,
        d.year_month,

        da.account_number,
        da.account_name,

        m.management_group,
        m.management_line,
        m.management_sign,

        SUM(
            CASE

                WHEN m.management_group IN (
                    'Revenue',
                    'Other Operating Income'
                )
                    THEN b.budget_amount

                WHEN m.management_group IN (
                    'Operating Costs',
                    'Non-Core Operating Items',
                    'EBITDA Adjustments',
                    'Tax'
                )
                    THEN -b.budget_amount

                WHEN m.management_group = 'Financial Result'
                     AND m.management_sign = 1
                    THEN b.budget_amount

                WHEN m.management_group = 'Financial Result'
                     AND m.management_sign = -1
                    THEN -b.budget_amount

                ELSE 0

            END
        ) AS plan_amount

    FROM warehouse.fact_budget b

    INNER JOIN warehouse.dim_date d
        ON b.budget_date_key = d.date_key

    INNER JOIN warehouse.dim_account da
        ON b.account_key = da.account_key

    INNER JOIN mart.dim_pnl_management_mapping m
        ON da.account_number::text
         = m.account_number::text

    WHERE
        b.budget_version = 'BUDGET_' || d.calendar_year::text
        AND b.scenario = 'BASE'
        AND m.is_active = TRUE

    GROUP BY
        d.calendar_year,
        d.calendar_month,
        d.year_month,
        da.account_number,
        da.account_name,
        m.management_group,
        m.management_line,
        m.management_sign
)

SELECT

    COALESCE(
        a.calendar_year,
        b.calendar_year
    ) AS calendar_year,

    COALESCE(
        a.calendar_month,
        b.calendar_month
    ) AS calendar_month,

    COALESCE(
        a.year_month,
        b.year_month
    ) AS year_month,

    COALESCE(
        a.account_number,
        b.account_number
    ) AS account_number,

    COALESCE(
        a.account_name,
        b.account_name
    ) AS account_name,

    COALESCE(
        a.management_group,
        b.management_group
    ) AS management_group,

    COALESCE(
        a.management_line,
        b.management_line
    ) AS management_line,

    COALESCE(
        a.management_sign,
        b.management_sign
    ) AS management_sign,

    COALESCE(
        a.actual_amount,
        0
    ) AS actual_amount,

    COALESCE(
        b.plan_amount,
        0
    ) AS plan_amount

FROM actual a

FULL OUTER JOIN budget b

    ON  a.calendar_year = b.calendar_year
    AND a.calendar_month = b.calendar_month
    AND a.account_number = b.account_number
    AND a.management_group = b.management_group
    AND a.management_line = b.management_line;
"""


# ============================================================
# LOAD DATA
# ============================================================

def load_data() -> pd.DataFrame:
    """Load Account Actual vs Budget data."""

    connection = None

    try:

        connection = get_connection()

        logger.info(
            "Loading Actual vs Budget account data."
        )

        df = pd.read_sql_query(
            SOURCE_QUERY,
            connection,
        )

        if df.empty:
            raise ValueError(
                "Actual vs Budget dataset is empty."
            )

        return df

    finally:

        if connection is not None:
            connection.close()


# ============================================================
# PREPARE DATA
# ============================================================

def prepare_data(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Prepare variance dataset."""

    df = df.copy()

    df["calendar_year"] = pd.to_numeric(
        df["calendar_year"],
        errors="coerce",
    ).astype("Int64")

    df["calendar_month"] = pd.to_numeric(
        df["calendar_month"],
        errors="coerce",
    ).astype("Int64")

    df["account_number"] = pd.to_numeric(
        df["account_number"],
        errors="coerce",
    ).astype("Int64")

    df["actual_amount"] = pd.to_numeric(
        df["actual_amount"],
        errors="coerce",
    ).fillna(0)

    df["plan_amount"] = pd.to_numeric(
        df["plan_amount"],
        errors="coerce",
    ).fillna(0)

    df["period"] = pd.to_datetime(
        df["year_month"] + "-01",
        errors="coerce",
    )

    # ========================================================
    # VARIANCE
    # ========================================================

    df["variance"] = (
        df["actual_amount"]
        - df["plan_amount"]
    )

    # ========================================================
    # PERCENTAGE VARIANCE
    # ========================================================

    df["variance_pct"] = np.where(
        df["plan_amount"] != 0,
        (
            df["variance"]
            / df["plan_amount"].abs()
        )
        * 100,
        np.nan,
    )

    return df.dropna(
        subset=["period"]
    )


# ============================================================
# DRIVER DIRECTION
# ============================================================

def determine_direction(
    metric: str,
    variance: float,
) -> str:
    """
    Determine whether a driver is favorable or unfavorable.

    Revenue:
        positive variance = favorable

    Costs:
        negative variance = favorable

    EBITDA / Net Profit:
        positive variance = favorable
    """

    if variance == 0:
        return "ON_PLAN"

    if metric == "OPERATING_COSTS":

        if variance < 0:
            return "FAVORABLE"

        return "UNFAVORABLE"

    if variance > 0:
        return "FAVORABLE"

    return "UNFAVORABLE"


# ============================================================
# DRIVER CONTRIBUTION
# ============================================================

def calculate_metric_drivers(
    data: pd.DataFrame,
    metric: str,
) -> pd.DataFrame:
    """Calculate top account drivers for one metric."""

    if metric not in METRIC_GROUPS:
        raise ValueError(
            f"Unsupported metric: {metric}"
        )

    source = data[
        data["management_group"].isin(
            METRIC_GROUPS[metric]
        )
    ].copy()

    if source.empty:
        return pd.DataFrame()

    # ========================================================
    # IMPORTANT:
    #
    # EBITDA / Net Profit contain multiple groups.
    # Contribution is therefore measured against total
    # absolute variance of the selected metric.
    # ========================================================

    monthly = (
        source
        .groupby(
            [
                "calendar_year",
                "calendar_month",
                "year_month",
                "period",

                "account_number",
                "account_name",
                "management_group",
                "management_line",
            ],
            as_index=False,
        )
        .agg(
            actual_amount=(
                "actual_amount",
                "sum",
            ),
            plan_amount=(
                "plan_amount",
                "sum",
            ),
        )
    )

    monthly["variance"] = (
        monthly["actual_amount"]
        - monthly["plan_amount"]
    )

    results = []

    for period, period_data in (
        monthly.groupby("period")
    ):

        period_data = period_data.copy()

        total_variance = (
            period_data["variance"]
            .sum()
        )

        total_abs_variance = (
            period_data["variance"]
            .abs()
            .sum()
        )

        if total_abs_variance == 0:
            continue

        period_data["contribution_pct"] = (
            period_data["variance"]
            .abs()
            / total_abs_variance
            * 100
        )

        # ----------------------------------------------------
        # Signed contribution to total variance
        # ----------------------------------------------------

        if total_variance != 0:

            period_data[
                "variance_contribution_pct"
            ] = (
                period_data["variance"]
                / abs(total_variance)
                * 100
            )

        else:

            period_data[
                "variance_contribution_pct"
            ] = 0.0

        period_data["metric"] = metric

        period_data["driver_direction"] = (
            period_data["variance"]
            .apply(
                lambda value:
                determine_direction(
                    metric,
                    value,
                )
            )
        )

        period_data["driver_rank"] = (
            period_data["contribution_pct"]
            .rank(
                method="first",
                ascending=False,
            )
            .astype(int)
        )

        # Only top N drivers.
        period_data = period_data[
            period_data["driver_rank"]
            <= TOP_N_DRIVERS
        ]

        period_data["root_cause_status"] = (
            "DRIVER_IDENTIFIED"
        )

        period_data["analysis_level"] = (
            "ACCOUNT"
        )

        results.append(
            period_data
        )

    if not results:
        return pd.DataFrame()

    return pd.concat(
        results,
        ignore_index=True,
    )


# ============================================================
# MANAGEMENT LINE SUMMARY
# ============================================================

def calculate_management_line_drivers(
    data: pd.DataFrame,
) -> pd.DataFrame:
    """
    Summarize variance drivers one level above account:
        Management Group
        Management Line
    """

    grouped = (
        data
        .groupby(
            [
                "calendar_year",
                "calendar_month",
                "year_month",
                "period",

                "management_group",
                "management_line",
            ],
            as_index=False,
        )
        .agg(
            actual_amount=(
                "actual_amount",
                "sum",
            ),
            plan_amount=(
                "plan_amount",
                "sum",
            ),
        )
    )

    grouped["variance"] = (
        grouped["actual_amount"]
        - grouped["plan_amount"]
    )

    grouped["abs_variance"] = (
        grouped["variance"]
        .abs()
    )

    results = []

    for period, period_data in (
        grouped.groupby("period")
    ):

        period_data = period_data.copy()

        total_abs = (
            period_data[
                "abs_variance"
            ].sum()
        )

        if total_abs == 0:
            continue

        period_data["contribution_pct"] = (
            period_data["abs_variance"]
            / total_abs
            * 100
        )

        period_data["driver_rank"] = (
            period_data[
                "contribution_pct"
            ]
            .rank(
                method="first",
                ascending=False,
            )
            .astype(int)
        )

        period_data["driver_type"] = (
            "MANAGEMENT_LINE"
        )

        period_data[
            "root_cause_status"
        ] = "DRIVER_IDENTIFIED"

        period_data[
            "analysis_level"
        ] = "MANAGEMENT_LINE"

        results.append(
            period_data
        )

    if not results:
        return pd.DataFrame()

    return pd.concat(
        results,
        ignore_index=True,
    )


# ============================================================
# CONTROLLER SUMMARY
# ============================================================

def build_controller_summary(
    detail: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build one high-level explanation per metric/month.
    """

    if detail.empty:
        return pd.DataFrame()

    summaries = []

    for (
        metric,
        period,
    ), group in detail.groupby(
        [
            "metric",
            "period",
        ]
    ):

        group = group.sort_values(
            "contribution_pct",
            ascending=False,
        )

        total_variance = (
            group["variance"]
            .sum()
        )

        top_driver = (
            group.iloc[0]
        )

        top_drivers = (
            group.head(3)
            .apply(
                lambda row:
                f"{row['account_number']} "
                f"{row['management_line']} "
                f"({row['contribution_pct']:.1f}%)",
                axis=1,
            )
            .tolist()
        )

        summaries.append(
            {
                "period": period,
                "metric": metric,

                "total_variance":
                    total_variance,

                "primary_driver_account":
                    top_driver[
                        "account_number"
                    ],

                "primary_driver_name":
                    top_driver[
                        "management_line"
                    ],

                "primary_driver_variance":
                    top_driver[
                        "variance"
                    ],

                "primary_driver_contribution_pct":
                    top_driver[
                        "contribution_pct"
                    ],

                "top_3_drivers":
                    " | ".join(
                        top_drivers
                    ),

                "controller_interpretation":
                    (
                        "FAVORABLE"
                        if total_variance > 0
                        else "UNFAVORABLE"
                        if total_variance < 0
                        else "ON_PLAN"
                    ),
            }
        )

    return pd.DataFrame(
        summaries
    )


# ============================================================
# SAVE
# ============================================================

def save_output(
    detail: pd.DataFrame,
    line_summary: pd.DataFrame,
    controller_summary: pd.DataFrame,
) -> None:
    """Save variance root cause output."""

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Main detailed output
    # --------------------------------------------------------

    detail.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    logger.info(
        "Variance root causes saved to %s",
        OUTPUT_FILE,
    )

    # --------------------------------------------------------
    # Management line summary
    # --------------------------------------------------------

    line_file = (
        OUTPUT_DIR
        / "variance_root_causes_management_line.csv"
    )

    line_summary.to_csv(
        line_file,
        index=False,
    )

    logger.info(
        "Management-line drivers saved to %s",
        line_file,
    )

    # --------------------------------------------------------
    # Controller summary
    # --------------------------------------------------------

    controller_file = (
        OUTPUT_DIR
        / "variance_root_cause_controller_summary.csv"
    )

    controller_summary.to_csv(
        controller_file,
        index=False,
    )

    logger.info(
        "Controller summary saved to %s",
        controller_file,
    )


# ============================================================
# MAIN
# ============================================================

def main() -> int:
    """Run Variance Root Cause Analysis."""

    try:

        logger.info(
            "Starting EFAP Variance Root Cause Analysis."
        )

        raw = load_data()

        data = prepare_data(
            raw
        )

        # ----------------------------------------------------
        # Metric-level drivers
        # ----------------------------------------------------

        metric_results = []

        for metric in METRIC_GROUPS:

            logger.info(
                "Analysing %s",
                metric,
            )

            result = (
                calculate_metric_drivers(
                    data,
                    metric,
                )
            )

            if not result.empty:

                metric_results.append(
                    result
                )

        if metric_results:

            detail = pd.concat(
                metric_results,
                ignore_index=True,
            )

        else:

            detail = pd.DataFrame()

        # ----------------------------------------------------
        # Management-line analysis
        # ----------------------------------------------------

        line_summary = (
            calculate_management_line_drivers(
                data
            )
        )

        # ----------------------------------------------------
        # Controller-level summary
        # ----------------------------------------------------

        controller_summary = (
            build_controller_summary(
                detail
            )
        )

        if detail.empty:

            logger.warning(
                "No variance drivers identified."
            )

        save_output(
            detail,
            line_summary,
            controller_summary,
        )

        logger.info(
            "Generated %s detailed driver rows.",
            len(detail),
        )

        logger.info(
            "Variance Root Cause Analysis "
            "completed successfully."
        )

        return 0

    except Exception as exc:

        logger.exception(
            "Variance Root Cause Analysis failed: %s",
            exc,
        )

        return 1


if __name__ == "__main__":
    sys.exit(main())