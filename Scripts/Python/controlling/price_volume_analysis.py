"""
EFAP - Price / Volume / Mix Analysis

Object:
    Python/controlling/price_volume_analysis.py

Purpose:
    Decompose actual Revenue and Operating Cost changes into:

        Price Effect
        Volume Effect
        Mix Effect
        Total Variance

Comparison:
    Same month previous year (YoY)

Source:
    warehouse.fact_gl
    warehouse.dim_account
    warehouse.dim_date
    mart.dim_pnl_management_mapping

Output:
    data/analytics/price_volume_analysis.csv
    data/analytics/price_volume_summary.csv

Important:
    This module only performs analytical decomposition.
    Business/account mapping remains in PostgreSQL.
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

DETAIL_OUTPUT: Final[Path] = (
    OUTPUT_DIR
    / "price_volume_analysis.csv"
)

SUMMARY_OUTPUT: Final[Path] = (
    OUTPUT_DIR
    / "price_volume_summary.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

REVENUE_ACCOUNTS: Final[set[int]] = {
    601,
    602,
    604,
}

OPERATING_COST_ACCOUNTS: Final[set[int]] = {
    501,
    502,
    504,
    511,
    518,
    521,
    524,
    548,
    549,
    582,
}

MIN_QUANTITY: Final[float] = 0.000001


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
    """Validate PostgreSQL configuration."""

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
    """Open PostgreSQL connection."""

    validate_db_config()

    return psycopg2.connect(
        **DB_CONFIG
    )


# ============================================================
# SOURCE QUERY
# ============================================================

SOURCE_QUERY: Final[str] = """
SELECT

    d.calendar_year,
    d.calendar_month,
    d.year_month,

    d.full_date,

    f.gl_entry_key,
    f.account_key,

    a.account_number,
    a.account_name,
    a.normal_balance,

    m.management_group,
    m.management_line,

    f.quantity,
    f.unit_price,

    f.debit_amount,
    f.credit_amount,
    f.amount_local

FROM warehouse.fact_gl f

INNER JOIN warehouse.dim_account a
    ON f.account_key = a.account_key

INNER JOIN warehouse.dim_date d
    ON f.posting_date_key = d.date_key

INNER JOIN mart.dim_pnl_management_mapping m
    ON a.account_number::text = m.account_number::text

WHERE
    m.is_active = TRUE

    AND a.account_number::integer IN (
        501,
        502,
        504,
        511,
        518,
        521,
        524,
        548,
        549,
        582,
        601,
        602,
        604
    )

ORDER BY
    d.calendar_year,
    d.calendar_month,
    a.account_number;
"""


# ============================================================
# DATA LOADING
# ============================================================

def load_data() -> pd.DataFrame:
    """Load transaction-level P/V/M source data."""

    connection = None

    try:

        logger.info(
            "Loading transaction-level P/V/M data."
        )

        connection = get_connection()

        df = pd.read_sql_query(
            SOURCE_QUERY,
            connection,
        )

        if df.empty:
            raise ValueError(
                "P/V/M source dataset is empty."
            )

        return df

    finally:

        if connection is not None:
            connection.close()


# ============================================================
# PREPARATION
# ============================================================

def prepare_data(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Prepare transaction-level analytical dataset."""

    df = df.copy()

    df["period"] = pd.to_datetime(
        df["year_month"] + "-01",
        errors="coerce",
    )

    df["account_number"] = pd.to_numeric(
        df["account_number"],
        errors="coerce",
    ).astype("Int64")

    for column in [
        "quantity",
        "unit_price",
        "debit_amount",
        "credit_amount",
        "amount_local",
    ]:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    # --------------------------------------------------------
    # Management amount
    #
    # Revenue:
    #   Credit - Debit
    #
    # Cost:
    #   Debit - Credit
    # --------------------------------------------------------

    df["management_amount"] = np.where(
        df["normal_balance"] == "Credit",
        df["credit_amount"].fillna(0)
        - df["debit_amount"].fillna(0),
        df["debit_amount"].fillna(0)
        - df["credit_amount"].fillna(0),
    )

    # --------------------------------------------------------
    # Analysis family
    # --------------------------------------------------------

    df["analysis_type"] = np.select(
        [
            df["account_number"].isin(
                REVENUE_ACCOUNTS
            ),

            df["account_number"].isin(
                OPERATING_COST_ACCOUNTS
            ),
        ],
        [
            "REVENUE",
            "OPERATING_COST",
        ],
        default="OTHER",
    )

    df = df[
        df["analysis_type"].isin(
            [
                "REVENUE",
                "OPERATING_COST",
            ]
        )
    ].copy()

    return df.dropna(
        subset=["period"]
    )


# ============================================================
# MONTHLY AGGREGATION
# ============================================================

def aggregate_monthly(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Aggregate transactions to:

        Period
        Account
        Analysis Type

    Weighted average price is calculated as:

        Spend / Quantity
    """

    grouped = (
        df
        .groupby(
            [
                "period",
                "calendar_year",
                "calendar_month",
                "year_month",
                "account_number",
                "account_name",
                "management_group",
                "management_line",
                "analysis_type",
            ],
            as_index=False,
        )
        .agg(
            quantity=(
                "quantity",
                "sum",
            ),
            amount=(
                "management_amount",
                "sum",
            ),
            amount_local=(
                "amount_local",
                "sum",
            ),
        )
    )

    grouped["weighted_price"] = np.where(
        grouped["quantity"].abs()
        > MIN_QUANTITY,

        grouped["amount"].abs()
        / grouped["quantity"].abs(),

        np.nan,
    )

    return grouped


# ============================================================
# SAME MONTH PRIOR YEAR
# ============================================================

def add_prior_year_values(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Join each month with the same month from prior year."""

    current = df.copy()

    base = df[
        [
            "period",
            "account_number",
            "quantity",
            "amount",
            "weighted_price",
        ]
    ].copy()

    base["period"] = (
        base["period"]
        + pd.DateOffset(years=1)
    )

    base = base.rename(
        columns={
            "quantity": "prior_year_quantity",
            "amount": "prior_year_amount",
            "weighted_price":
                "prior_year_price",
        }
    )

    result = current.merge(
        base,
        on=[
            "period",
            "account_number",
        ],
        how="left",
    )

    return result


# ============================================================
# PVM DECOMPOSITION
# ============================================================

def calculate_pvm(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate Price / Volume / Mix effects.

    For each account:

        Volume Effect =
            (Q_current - Q_prior) * P_prior

        Price Effect =
            (P_current - P_prior) * Q_current

        Total Variance =
            Actual Current - Actual Prior

    Mix is calculated as the residual after the explicit
    price and volume effects across the portfolio.
    """

    df = df.copy()

    df["quantity_variance"] = (
        df["quantity"]
        - df["prior_year_quantity"]
    )

    df["price_variance"] = (
        df["weighted_price"]
        - df["prior_year_price"]
    )

    # --------------------------------------------------------
    # Volume effect
    # --------------------------------------------------------

    df["volume_effect"] = (
        df["quantity_variance"]
        * df["prior_year_price"]
    )

    # --------------------------------------------------------
    # Price effect
    # --------------------------------------------------------

    df["price_effect"] = (
        df["price_variance"]
        * df["quantity"]
    )

    # --------------------------------------------------------
    # Total variance
    # --------------------------------------------------------

    df["total_variance"] = (
        df["amount"]
        - df["prior_year_amount"]
    )

    # --------------------------------------------------------
    # Mix / residual effect
    #
    # At account level this represents the residual caused
    # by aggregation/portfolio interaction.
    # --------------------------------------------------------

    df["mix_effect"] = (
        df["total_variance"]
        - df["volume_effect"]
        - df["price_effect"]
    )

    # --------------------------------------------------------
    # Reconciliation
    # --------------------------------------------------------

    df["reconciliation_check"] = (
        df["price_effect"]
        + df["volume_effect"]
        + df["mix_effect"]
        - df["total_variance"]
    )

    # --------------------------------------------------------
    # Driver contribution
    # --------------------------------------------------------

    denominator = (
        df["total_variance"]
        .abs()
        .sum()
    )

    if denominator > 0:

        df["account_contribution_pct"] = (
            df["total_variance"]
            .abs()
            / denominator
            * 100
        )

    else:

        df["account_contribution_pct"] = 0.0

    return df


# ============================================================
# DIRECTION
# ============================================================

def determine_effect_status(
    analysis_type: str,
    effect_name: str,
    effect: float,
) -> str:
    """
    Determine whether a P/V effect is favorable.

    Revenue:
        positive = favorable
        negative = unfavorable

    Operating costs:
        positive cost effect = unfavorable
        negative cost effect = favorable
    """

    if abs(effect) < 1e-12:
        return "NEUTRAL"

    if analysis_type == "REVENUE":

        return (
            "FAVORABLE"
            if effect > 0
            else "UNFAVORABLE"
        )

    if analysis_type == "OPERATING_COST":

        return (
            "UNFAVORABLE"
            if effect > 0
            else "FAVORABLE"
        )

    return "NEUTRAL"


# ============================================================
# SUMMARY
# ============================================================

def build_summary(
    detail: pd.DataFrame,
) -> pd.DataFrame:
    """Build management-level P/V/M summary."""

    rows = []

    for (
        period,
        analysis_type,
    ), group in detail.groupby(
        [
            "period",
            "analysis_type",
        ]
    ):

        total_variance = (
            group["total_variance"]
            .sum()
        )

        total_price = (
            group["price_effect"]
            .sum()
        )

        total_volume = (
            group["volume_effect"]
            .sum()
        )

        total_mix = (
            group["mix_effect"]
            .sum()
        )

        top_account = (
            group
            .sort_values(
                "total_variance",
                key=lambda s: s.abs(),
                ascending=False,
            )
            .iloc[0]
        )

        rows.append(
            {
                "period": period,
                "analysis_type": analysis_type,

                "total_variance":
                    total_variance,

                "price_effect":
                    total_price,

                "volume_effect":
                    total_volume,

                "mix_effect":
                    total_mix,

                "reconciliation_check":
                    (
                        total_price
                        + total_volume
                        + total_mix
                        - total_variance
                    ),

                "top_driver_account":
                    top_account[
                        "account_number"
                    ],

                "top_driver_name":
                    top_account[
                        "management_line"
                    ],

                "top_driver_variance":
                    top_account[
                        "total_variance"
                    ],
            }
        )

    summary = pd.DataFrame(
        rows
    )

    if summary.empty:
        return summary

    summary["price_status"] = summary.apply(
        lambda row:
        determine_effect_status(
            row["analysis_type"],
            "PRICE",
            row["price_effect"],
        ),
        axis=1,
    )

    summary["volume_status"] = summary.apply(
        lambda row:
        determine_effect_status(
            row["analysis_type"],
            "VOLUME",
            row["volume_effect"],
        ),
        axis=1,
    )

    summary["mix_status"] = summary.apply(
        lambda row:
        determine_effect_status(
            row["analysis_type"],
            "MIX",
            row["mix_effect"],
        ),
        axis=1,
    )

    return summary.sort_values(
        [
            "period",
            "analysis_type",
        ]
    )


# ============================================================
# SAVE
# ============================================================

def save_outputs(
    detail: pd.DataFrame,
    summary: pd.DataFrame,
) -> None:
    """Save P/V/M outputs."""

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
        "Detailed P/V/M analysis saved to %s",
        DETAIL_OUTPUT,
    )

    logger.info(
        "P/V/M summary saved to %s",
        SUMMARY_OUTPUT,
    )


# ============================================================
# MAIN
# ============================================================

def main() -> int:
    """Run Price / Volume / Mix analysis."""

    try:

        logger.info(
            "Starting EFAP Price / Volume / Mix Analysis."
        )

        raw = load_data()

        prepared = prepare_data(
            raw
        )

        monthly = aggregate_monthly(
            prepared
        )

        comparison = add_prior_year_values(
            monthly
        )

        # We need both current and prior values
        # to perform a meaningful decomposition.
        comparison = comparison.dropna(
            subset=[
                "prior_year_quantity",
                "prior_year_amount",
                "prior_year_price",
            ]
        )

        if comparison.empty:

            raise RuntimeError(
                "No comparable current/prior-year "
                "observations available for P/V/M analysis."
            )

        detail = calculate_pvm(
            comparison
        )

        detail["price_status"] = detail.apply(
            lambda row:
            determine_effect_status(
                row["analysis_type"],
                "PRICE",
                row["price_effect"],
            ),
            axis=1,
        )

        detail["volume_status"] = detail.apply(
            lambda row:
            determine_effect_status(
                row["analysis_type"],
                "VOLUME",
                row["volume_effect"],
            ),
            axis=1,
        )

        detail["mix_status"] = detail.apply(
            lambda row:
            determine_effect_status(
                row["analysis_type"],
                "MIX",
                row["mix_effect"],
            ),
            axis=1,
        )

        detail["comparison_type"] = (
            "YOY_SAME_MONTH"
        )

        detail["analysis_level"] = (
            "ACCOUNT"
        )

        summary = build_summary(
            detail
        )

        save_outputs(
            detail,
            summary,
        )

        logger.info(
            "Generated %s detailed P/V/M rows.",
            len(detail),
        )

        logger.info(
            "Price / Volume / Mix analysis "
            "completed successfully."
        )

        return 0

    except Exception as exc:

        logger.exception(
            "Price / Volume / Mix analysis failed: %s",
            exc,
        )

        return 1


if __name__ == "__main__":
    sys.exit(main())