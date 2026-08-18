-- ============================================================
-- EFAP
-- View: mart.vw_management_pnl
-- Layer: Mart / Management Reporting
-- Grain: One row per calendar month
--
-- Purpose:
--   Management P&L based on the P&L management mapping.
--
-- Source:
--   mart.vw_pnl_management_detail
--
-- Important:
--   signed_amount is CALCULATED in the upstream P&L view.
--   It does NOT exist in warehouse.fact_gl.
--
-- Management sign convention:
--   Revenue / income       -> positive
--   Operating costs       -> negative
--   Financial expenses    -> negative
--   Taxes                 -> negative
--
-- P&L structure:
--   Revenue
--   + Other Operating Income
--   + Operating Costs
--   + Non-Core Operating Items
--   = EBITDA
--
--   EBITDA
--   + EBITDA Adjustments
--   = EBIT
--
--   EBIT
--   + Financial Result
--   = EBT
--
--   EBT
--   + Tax
--   = Net Profit
-- ============================================================
DROP VIEW IF EXISTS mart.vw_management_pnl;

CREATE OR REPLACE VIEW mart.vw_management_pnl AS
WITH
    monthly_pnl AS (
        SELECT
            calendar_year,
            calendar_month,
            month_name,
            year_month,
            -- ====================================================
            -- REVENUE
            -- ====================================================
            COALESCE(
                SUM(
                    CASE
                        WHEN management_group = 'Revenue' THEN management_amount
                        ELSE 0
                    END
                ),
                0
            ) AS revenue,
            -- ====================================================
            -- OTHER OPERATING INCOME
            -- ====================================================
            COALESCE(
                SUM(
                    CASE
                        WHEN management_group = 'Other Operating Income' THEN management_amount
                        ELSE 0
                    END
                ),
                0
            ) AS other_operating_income,
            -- ====================================================
            -- OPERATING COSTS
            -- ====================================================
            COALESCE(
                SUM(
                    CASE
                        WHEN management_group = 'Operating Costs' THEN management_amount
                        ELSE 0
                    END
                ),
                0
            ) AS operating_costs,
            -- ====================================================
            -- NON-CORE OPERATING ITEMS
            -- ====================================================
            COALESCE(
                SUM(
                    CASE
                        WHEN management_group = 'Non-Core Operating Items' THEN management_amount
                        ELSE 0
                    END
                ),
                0
            ) AS non_core_operating_items,
            -- ====================================================
            -- EBITDA ADJUSTMENTS
            -- ====================================================
            COALESCE(
                SUM(
                    CASE
                        WHEN management_group = 'EBITDA Adjustments' THEN management_amount
                        ELSE 0
                    END
                ),
                0
            ) AS ebitda_adjustments,
            -- ====================================================
            -- FINANCIAL RESULT
            -- ====================================================
            COALESCE(
                SUM(
                    CASE
                        WHEN management_group = 'Financial Result' THEN management_amount
                        ELSE 0
                    END
                ),
                0
            ) AS financial_result,
            -- ====================================================
            -- TAX
            -- ====================================================
            COALESCE(
                SUM(
                    CASE
                        WHEN management_group = 'Tax' THEN management_amount
                        ELSE 0
                    END
                ),
                0
            ) AS income_tax
        FROM
            mart.vw_pnl_management_detail
        GROUP BY
            calendar_year,
            calendar_month,
            month_name,
            year_month
    )
SELECT
    calendar_year,
    calendar_month,
    month_name,
    year_month,
    -- ========================================================
    -- P&L COMPONENTS
    -- ========================================================
    revenue,
    other_operating_income,
    operating_costs,
    non_core_operating_items,
    ebitda_adjustments,
    financial_result,
    income_tax,
    -- ========================================================
    -- EBITDA
    --
    -- Revenue
    -- + Other Operating Income
    -- + Operating Costs
    -- + Non-Core Operating Items
    -- ========================================================
    (
        revenue + other_operating_income + operating_costs + non_core_operating_items
    ) AS ebitda,
    -- ========================================================
    -- EBIT
    --
    -- EBITDA
    -- + EBITDA Adjustments
    -- ========================================================
    (
        revenue + other_operating_income + operating_costs + non_core_operating_items + ebitda_adjustments
    ) AS ebit,
    -- ========================================================
    -- EBT
    --
    -- EBIT
    -- + Financial Result
    -- ========================================================
    (
        revenue + other_operating_income + operating_costs + non_core_operating_items + ebitda_adjustments + financial_result
    ) AS ebt,
    -- ========================================================
    -- NET PROFIT
    --
    -- EBT
    -- + Income Tax
    --
    -- Tax is already signed through management_sign,
    -- therefore it is ADDED rather than subtracted.
    -- ========================================================
    (
        revenue + other_operating_income + operating_costs + non_core_operating_items + ebitda_adjustments + financial_result + income_tax
    ) AS net_profit,
    -- ========================================================
    -- EBITDA MARGIN
    -- ========================================================
    CASE
        WHEN revenue <> 0 THEN (
            revenue + other_operating_income + operating_costs + non_core_operating_items
        ) / revenue
        ELSE NULL
    END AS ebitda_margin,
    -- ========================================================
    -- EBIT MARGIN
    -- ========================================================
    CASE
        WHEN revenue <> 0 THEN (
            revenue + other_operating_income + operating_costs + non_core_operating_items + ebitda_adjustments
        ) / revenue
        ELSE NULL
    END AS ebit_margin,
    -- ========================================================
    -- NET PROFIT MARGIN
    -- ========================================================
    CASE
        WHEN revenue <> 0 THEN (
            revenue + other_operating_income + operating_costs + non_core_operating_items + ebitda_adjustments + financial_result + income_tax
        ) / revenue
        ELSE NULL
    END AS net_profit_margin
FROM
    monthly_pnl;