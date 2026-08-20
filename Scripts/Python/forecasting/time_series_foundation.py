"""
EFAP - Time Series Foundation

Object:
    Python/forecasting/time_series_foundation.py

Purpose:
    Creates the canonical monthly time-series dataset used by
    forecasting, anomaly detection and predictive models.

Source:
    mart.vw_controller_kpis_monthly

Output:
    data/processed/controller_kpi_timeseries.csv

Design principles:
    - PostgreSQL is the single source of truth.
    - No financial logic is duplicated in Python.
    - SQL/Mart remains responsible for business definitions.
    - Python is responsible for analytical feature preparation.
    - No database password is stored in source code.
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Final

import pandas as pd

try:
    import psycopg2
except ImportError as exc:
    raise ImportError(
        "Missing dependency 'psycopg2'. "
        "Install it with: pip install psycopg2-binary"
    ) from exc

try:
    from dotenv import load_dotenv
except ImportError as exc:
    raise ImportError(
        "Missing dependency 'python-dotenv'. "
        "Install it with: pip install python-dotenv"
    ) from exc


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parents[3]

ENV_FILE: Final[Path] = PROJECT_ROOT / ".env"

OUTPUT_DIR: Final[Path] = (
    PROJECT_ROOT / "data" / "processed"
)

OUTPUT_FILE: Final[Path] = (
    OUTPUT_DIR / "controller_kpi_timeseries.csv"
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
# CONFIGURATION
# ============================================================

load_dotenv(ENV_FILE)


DB_CONFIG: Final[dict[str, object]] = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "EFAP"),
    "user": os.getenv("DB_USER", ""),
    "password": os.getenv("DB_PASSWORD", ""),
}


# ============================================================
# SOURCE QUERY
# ============================================================

SOURCE_QUERY: Final[str] = """
SELECT
    calendar_year,
    calendar_month,
    year_month,

    revenue,
    other_operating_income,
    operating_costs,
    non_core_operating_items,
    ebitda_adjustments,

    ebitda,
    ebit,
    financial_result,
    ebt,
    income_tax,
    net_profit,

    ebitda_margin,
    ebit_margin,
    ebt_margin,
    net_profit_margin,

    cash_balance,
    inventory_balance,
    receivables_balance,
    other_current_assets_balance,

    current_assets,
    current_liabilities_balance,

    net_working_capital,
    operating_working_capital,
    nwc_change,

    current_ratio,
    quick_ratio,
    cash_ratio,

    dso_days,
    dio_days,
    dpo_days,
    cash_conversion_cycle_days,

    operating_cash_flow,
    investing_cash_flow,
    financing_cash_flow,
    net_cash_change,

    opening_cash,
    closing_cash,

    free_cash_flow,

    ebitda_status,
    working_capital_status,
    liquidity_status,
    cash_flow_status

FROM mart.vw_controller_kpis_monthly

ORDER BY
    calendar_year,
    calendar_month;
"""


# ============================================================
# EXPECTED COLUMNS
# ============================================================

EXPECTED_COLUMNS: Final[set[str]] = {
    "calendar_year",
    "calendar_month",
    "year_month",

    "revenue",
    "other_operating_income",
    "operating_costs",
    "non_core_operating_items",
    "ebitda_adjustments",

    "ebitda",
    "ebit",
    "financial_result",
    "ebt",
    "income_tax",
    "net_profit",

    "ebitda_margin",
    "ebit_margin",
    "ebt_margin",
    "net_profit_margin",

    "cash_balance",
    "inventory_balance",
    "receivables_balance",
    "other_current_assets_balance",

    "current_assets",
    "current_liabilities_balance",

    "net_working_capital",
    "operating_working_capital",
    "nwc_change",

    "current_ratio",
    "quick_ratio",
    "cash_ratio",

    "dso_days",
    "dio_days",
    "dpo_days",
    "cash_conversion_cycle_days",

    "operating_cash_flow",
    "investing_cash_flow",
    "financing_cash_flow",
    "net_cash_change",

    "opening_cash",
    "closing_cash",
    "free_cash_flow",

    "ebitda_status",
    "working_capital_status",
    "liquidity_status",
    "cash_flow_status",
}


# ============================================================
# NUMERIC COLUMNS
# ============================================================

NUMERIC_COLUMNS: Final[list[str]] = [
    "revenue",
    "other_operating_income",
    "operating_costs",
    "non_core_operating_items",
    "ebitda_adjustments",

    "ebitda",
    "ebit",
    "financial_result",
    "ebt",
    "income_tax",
    "net_profit",

    "ebitda_margin",
    "ebit_margin",
    "ebt_margin",
    "net_profit_margin",

    "cash_balance",
    "inventory_balance",
    "receivables_balance",
    "other_current_assets_balance",

    "current_assets",
    "current_liabilities_balance",

    "net_working_capital",
    "operating_working_capital",
    "nwc_change",

    "current_ratio",
    "quick_ratio",
    "cash_ratio",

    "dso_days",
    "dio_days",
    "dpo_days",
    "cash_conversion_cycle_days",

    "operating_cash_flow",
    "investing_cash_flow",
    "financing_cash_flow",
    "net_cash_change",

    "opening_cash",
    "closing_cash",
    "free_cash_flow",
]


# ============================================================
# DATABASE
# ============================================================

def validate_db_config() -> None:
    """Validate required database configuration."""
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


def get_connection() -> psycopg2.extensions.connection:
    """Create a PostgreSQL connection."""
    validate_db_config()

    logger.info(
        "Connecting to PostgreSQL database '%s' at %s:%s",
        DB_CONFIG["database"],
        DB_CONFIG["host"],
        DB_CONFIG["port"],
    )

    return psycopg2.connect(**DB_CONFIG)


# ============================================================
# EXTRACTION
# ============================================================

def load_source_data(
    connection: psycopg2.extensions.connection,
) -> pd.DataFrame:
    """Load controller KPI time-series data from PostgreSQL."""
    logger.info(
        "Loading monthly controller KPI data from "
        "mart.vw_controller_kpis_monthly"
    )

    dataframe = pd.read_sql_query(
        SOURCE_QUERY,
        connection,
    )

    logger.info(
        "Loaded %s rows and %s columns",
        len(dataframe),
        len(dataframe.columns),
    )

    return dataframe


# ============================================================
# VALIDATION
# ============================================================

def validate_schema(dataframe: pd.DataFrame) -> None:
    """Validate source dataframe columns."""
    actual_columns = set(dataframe.columns)

    missing = EXPECTED_COLUMNS - actual_columns

    if missing:
        raise ValueError(
            "Source view is missing expected columns: "
            + ", ".join(sorted(missing))
        )


def validate_time_index(dataframe: pd.DataFrame) -> None:
    """Validate monthly time-series structure."""
    if dataframe.empty:
        raise ValueError("Controller KPI dataset is empty.")

    dataframe["calendar_year"] = (
        pd.to_numeric(
            dataframe["calendar_year"],
            errors="raise",
        )
        .astype(int)
    )

    dataframe["calendar_month"] = (
        pd.to_numeric(
            dataframe["calendar_month"],
            errors="raise",
        )
        .astype(int)
    )

    if not dataframe["calendar_month"].between(1, 12).all():
        raise ValueError(
            "calendar_month contains values outside 1-12."
        )

    dataframe["period"] = pd.to_datetime(
        dataframe["year_month"] + "-01",
        errors="coerce",
    )

    if dataframe["period"].isna().any():
        raise ValueError(
            "Invalid year_month values detected."
        )

    if dataframe["period"].duplicated().any():
        duplicates = dataframe.loc[
            dataframe["period"].duplicated(),
            "period",
        ].tolist()

        raise ValueError(
            "Duplicate monthly periods detected: "
            + ", ".join(map(str, duplicates))
        )

    expected_periods = pd.date_range(
        start=dataframe["period"].min(),
        end=dataframe["period"].max(),
        freq="MS",
    )

    actual_periods = (
        dataframe["period"]
        .sort_values()
        .reset_index(drop=True)
    )

    if not actual_periods.equals(
        pd.Series(expected_periods)
    ):
        logger.warning(
            "Time series contains missing monthly periods."
        )


def convert_numeric_columns(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Convert analytical columns to numeric values."""
    for column in NUMERIC_COLUMNS:
        dataframe[column] = pd.to_numeric(
            dataframe[column],
            errors="coerce",
        )

    return dataframe


# ============================================================
# FEATURE ENGINEERING
# ============================================================

def create_time_series_features(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create reusable analytical features.

    These features are intentionally generic so that the same
    dataset can feed multiple future models.
    """

    dataframe = dataframe.sort_values(
        "period"
    ).reset_index(drop=True)

    # --------------------------------------------------------
    # Calendar features
    # --------------------------------------------------------

    dataframe["month"] = dataframe["period"].dt.month
    dataframe["quarter"] = dataframe["period"].dt.quarter

    dataframe["month_sin"] = (
        __import__("numpy").sin(
            2
            * __import__("numpy").pi
            * dataframe["month"]
            / 12
        )
    )

    dataframe["month_cos"] = (
        __import__("numpy").cos(
            2
            * __import__("numpy").pi
            * dataframe["month"]
            / 12
        )
    )

    # --------------------------------------------------------
    # Revenue lags
    # --------------------------------------------------------

    dataframe["revenue_lag_1"] = (
        dataframe["revenue"].shift(1)
    )

    dataframe["revenue_lag_3"] = (
        dataframe["revenue"].shift(3)
    )

    dataframe["revenue_lag_12"] = (
        dataframe["revenue"].shift(12)
    )

    # --------------------------------------------------------
    # EBITDA lags
    # --------------------------------------------------------

    dataframe["ebitda_lag_1"] = (
        dataframe["ebitda"].shift(1)
    )

    dataframe["ebitda_lag_12"] = (
        dataframe["ebitda"].shift(12)
    )

    # --------------------------------------------------------
    # Net profit lags
    # --------------------------------------------------------

    dataframe["net_profit_lag_1"] = (
        dataframe["net_profit"].shift(1)
    )

    dataframe["net_profit_lag_12"] = (
        dataframe["net_profit"].shift(12)
    )

    # --------------------------------------------------------
    # Cash lags
    # --------------------------------------------------------

    dataframe["cash_lag_1"] = (
        dataframe["closing_cash"].shift(1)
    )

    dataframe["cash_lag_12"] = (
        dataframe["closing_cash"].shift(12)
    )

    # --------------------------------------------------------
    # Working Capital lags
    # --------------------------------------------------------

    dataframe["nwc_lag_1"] = (
        dataframe["net_working_capital"].shift(1)
    )

    dataframe["nwc_lag_12"] = (
        dataframe["net_working_capital"].shift(12)
    )

    # --------------------------------------------------------
    # Rolling metrics
    # --------------------------------------------------------

    dataframe["revenue_rolling_3m"] = (
        dataframe["revenue"]
        .rolling(window=3, min_periods=1)
        .mean()
    )

    dataframe["revenue_rolling_6m"] = (
        dataframe["revenue"]
        .rolling(window=6, min_periods=1)
        .mean()
    )

    dataframe["revenue_rolling_12m"] = (
        dataframe["revenue"]
        .rolling(window=12, min_periods=1)
        .mean()
    )

    dataframe["ebitda_rolling_3m"] = (
        dataframe["ebitda"]
        .rolling(window=3, min_periods=1)
        .mean()
    )

    dataframe["cash_rolling_3m"] = (
        dataframe["closing_cash"]
        .rolling(window=3, min_periods=1)
        .mean()
    )

    # --------------------------------------------------------
    # Growth rates
    # --------------------------------------------------------

    dataframe["revenue_mom_pct"] = (
        dataframe["revenue"]
        .pct_change(fill_method=None)
        * 100
    )

    dataframe["revenue_yoy_pct"] = (
        dataframe["revenue"]
        .pct_change(
            periods=12,
            fill_method=None,
        )
        * 100
    )

    dataframe["ebitda_yoy_pct"] = (
        dataframe["ebitda"]
        .pct_change(
            periods=12,
            fill_method=None,
        )
        * 100
    )

    dataframe["net_profit_yoy_pct"] = (
        dataframe["net_profit"]
        .pct_change(
            periods=12,
            fill_method=None,
        )
        * 100
    )

    # --------------------------------------------------------
    # Margin dynamics
    # --------------------------------------------------------

    dataframe["ebitda_margin_change_pp"] = (
        dataframe["ebitda_margin"]
        .diff()
        * 100
    )

    dataframe["net_margin_change_pp"] = (
        dataframe["net_profit_margin"]
        .diff()
        * 100
    )

    return dataframe


# ============================================================
# OUTPUT
# ============================================================

def prepare_output(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Prepare canonical output dataset."""

    dataframe = dataframe.copy()

    dataframe["period"] = pd.to_datetime(
        dataframe["period"]
    )

    # Keep period close to the front.
    preferred_order = [
        "period",
        "calendar_year",
        "calendar_month",
        "year_month",
    ]

    remaining_columns = [
        column
        for column in dataframe.columns
        if column not in preferred_order
    ]

    dataframe = dataframe[
        preferred_order + remaining_columns
    ]

    return dataframe


def save_output(dataframe: pd.DataFrame) -> None:
    """Save prepared time-series dataset."""
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    logger.info(
        "Saved time-series dataset to %s",
        OUTPUT_FILE,
    )


# ============================================================
# MAIN
# ============================================================

def main() -> int:
    """Run the complete time-series foundation pipeline."""
    connection = None

    try:
        logger.info("Starting EFAP Time Series Foundation.")

        connection = get_connection()

        dataframe = load_source_data(
            connection
        )

        validate_schema(
            dataframe
        )

        dataframe = convert_numeric_columns(
            dataframe
        )

        validate_time_index(
            dataframe
        )

        dataframe = create_time_series_features(
            dataframe
        )

        dataframe = prepare_output(
            dataframe
        )

        save_output(
            dataframe
        )

        logger.info(
            "Time Series Foundation completed successfully."
        )

        logger.info(
            "Final dataset shape: %s rows × %s columns",
            len(dataframe),
            len(dataframe.columns),
        )

        return 0

    except Exception as exc:
        logger.exception(
            "Time Series Foundation failed: %s",
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