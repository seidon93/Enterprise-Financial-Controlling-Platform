/* ============================================================
EFAP - Management P&L
Object: mart.vw_management_pnl
Layer: Mart / Management Reporting
Grain: One row per calendar month

Purpose:
Management-oriented Profit & Loss statement based on the
standardized P&L management mapping.

Source:
mart.vw_pnl_management_detail

Important:
signed_amount is a calculated field produced upstream.
It does NOT exist in warehouse.fact_gl.

Management logic:
Revenue                  +
Other Operating Income   +
Operating Costs          -
Non-Core Operating Items -
--------------------------------
EBITDA

EBITDA
+ EBITDA Adjustments
--------------------------------
EBIT

EBIT
+ Financial Result
--------------------------------
EBT

EBT
+ Tax
--------------------------------
Net Profit

Technical / closing accounts
701, 702, 710 are excluded from management P&L.

============================================================ */
DROP VIEW IF EXISTS mart.vw_management_pnl;

CREATE VIEW mart.vw_management_pnl AS
WITH
    management_monthly AS (
        SELECT
            calendar_year,
            calendar_month,
            month_name,
            year_month,
            /* ====================================================
            REVENUE
            ==================================================== */
            SUM(
                CASE
                    WHEN management_group = 'Revenue' THEN management_amount
                    ELSE 0
                END
            ) AS revenue,
            /* ====================================================
            OTHER OPERATING INCOME
            ==================================================== */
            SUM(
                CASE
                    WHEN management_group = 'Other Operating Income' THEN management_amount
                    ELSE 0
                END
            ) AS other_operating_income,
            /* ====================================================
            OPERATING COSTS
            ==================================================== */
            SUM(
                CASE
                    WHEN management_group = 'Operating Costs' THEN management_amount
                    ELSE 0
                END
            ) AS operating_costs,
            /* ====================================================
            NON-CORE OPERATING ITEMS
            ==================================================== */
            SUM(
                CASE
                    WHEN management_group = 'Non-Core Operating Items' THEN management_amount
                    ELSE 0
                END
            ) AS non_core_operating_items,
            /* ====================================================
            EBITDA ADJUSTMENTS
            Depreciation, provisions, etc.
            Excluded from EBITDA.
            ==================================================== */
            SUM(
                CASE
                    WHEN management_group = 'EBITDA Adjustments' THEN management_amount
                    ELSE 0
                END
            ) AS ebitda_adjustments,
            /* ====================================================
            FINANCIAL RESULT
            ==================================================== */
            SUM(
                CASE
                    WHEN management_group = 'Financial Result' THEN management_amount
                    ELSE 0
                END
            ) AS financial_result,
            /* ====================================================
            TAX
            ==================================================== */
            SUM(
                CASE
                    WHEN management_group = 'Tax' THEN management_amount
                    ELSE 0
                END
            ) AS income_tax,
            /* ====================================================
            DATA QUALITY / TRACEABILITY
            ==================================================== */
            COUNT(*) AS management_row_count
        FROM
            mart.vw_pnl_management_detail
        WHERE
            management_group <> 'Closing Accounts'
        GROUP BY
            calendar_year,
            calendar_month,
            month_name,
            year_month
    ),
    calculated_pnl AS (
        SELECT
            calendar_year,
            calendar_month,
            month_name,
            year_month,
            revenue,
            other_operating_income,
            operating_costs,
            non_core_operating_items,
            ebitda_adjustments,
            financial_result,
            income_tax,
            management_row_count,
            /* ====================================================
            EBITDA
            
            Revenue
            + Other Operating Income
            + Operating Costs
            + Non-Core Operating Items
            
            Costs are already negative because of
            management_sign = -1.
            ==================================================== */
            (
                revenue + other_operating_income + operating_costs + non_core_operating_items
            ) AS ebitda
        FROM
            management_monthly
    ),
    calculated_ebit AS (
        SELECT
            calendar_year,
            calendar_month,
            month_name,
            year_month,
            revenue,
            other_operating_income,
            operating_costs,
            non_core_operating_items,
            ebitda_adjustments,
            financial_result,
            income_tax,
            management_row_count,
            ebitda,
            /* ====================================================
            EBIT
            
            EBITDA
            + Depreciation / Provisions / other EBITDA adjustments
            ==================================================== */
            (ebitda + ebitda_adjustments) AS ebit
        FROM
            calculated_pnl
    )
SELECT
    /* ========================================================
    PERIOD
    ======================================================== */
    calendar_year,
    calendar_month,
    month_name,
    year_month,
    /* ========================================================
    MANAGEMENT P&L COMPONENTS
    ======================================================== */
    revenue,
    other_operating_income,
    operating_costs,
    non_core_operating_items,
    ebitda_adjustments,
    financial_result,
    income_tax,
    /* ========================================================
    PROFITABILITY METRICS
    ======================================================== */
    ebitda,
    ebit,
    /* ========================================================
    EBT
    ======================================================== */
    (ebit + financial_result) AS ebt,
    /* ========================================================
    NET PROFIT
    ======================================================== */
    (ebit + financial_result + income_tax) AS net_profit,
    /* ========================================================
    EBITDA MARGIN
    ======================================================== */
    CASE
        WHEN NULLIF(revenue, 0) IS NOT NULL THEN ebitda / NULLIF(revenue, 0)
        ELSE NULL
    END AS ebitda_margin,
    /* ========================================================
    EBIT MARGIN
    ======================================================== */
    CASE
        WHEN NULLIF(revenue, 0) IS NOT NULL THEN ebit / NULLIF(revenue, 0)
        ELSE NULL
    END AS ebit_margin,
    /* ========================================================
    EBT MARGIN
    ======================================================== */
    CASE
        WHEN NULLIF(revenue, 0) IS NOT NULL THEN (ebit + financial_result) / NULLIF(revenue, 0)
        ELSE NULL
    END AS ebt_margin,
    /* ========================================================
    NET PROFIT MARGIN
    ======================================================== */
    CASE
        WHEN NULLIF(revenue, 0) IS NOT NULL THEN (ebit + financial_result + income_tax) / NULLIF(revenue, 0)
        ELSE NULL
    END AS net_profit_margin,
    /* ========================================================
    TRACEABILITY
    ======================================================== */
    management_row_count
FROM
    calculated_ebit;