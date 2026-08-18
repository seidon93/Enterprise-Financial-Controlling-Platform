-- ============================================================
-- EFAP - Management P&L
-- Object: mart.vw_management_pnl
-- Layer: Mart / Management Reporting
-- Grain: One row per calendar month
--
-- Purpose:
--   Management-oriented monthly P&L with:
--     Revenue
--     Operating Costs
--     EBITDA
--     EBITDA Adjustments
--     EBIT
--     Financial Result
--     EBT
--     Income Tax
--     Net Profit
--     Margins
--
-- Important:
--   signed_amount is a CALCULATED field from mart.vw_pnl_monthly.
--   It does NOT exist in warehouse.fact_gl.
--
-- Source:
--   mart.vw_pnl_monthly
--   mart.dim_pnl_management_mapping
-- ============================================================
DROP VIEW IF EXISTS mart.vw_management_pnl;

CREATE
OR REPLACE VIEW mart.vw_management_pnl AS
WITH
    management_detail AS (
        SELECT
            d.calendar_year,
            d.calendar_month,
            d.month_name,
            d.year_month,
            d.account_number,
            d.account_name,
            m.management_group,
            m.management_line,
            m.management_sign,
            m.ebitda_included,
            m.sort_order,
            d.row_count,
            d.debit_amount,
            d.credit_amount,
            d.signed_amount,
            -- Management-adjusted amount.
            d.signed_amount * m.management_sign AS management_amount
        FROM
            mart.vw_pnl_monthly d
            INNER JOIN mart.dim_pnl_management_mapping m ON d.account_number::text = m.account_number::text
        WHERE
            m.is_active = TRUE
    ),
    monthly_pnl AS (
        SELECT
            calendar_year,
            calendar_month,
            month_name,
            year_month,
            -- ====================================================
            -- REVENUE
            -- ====================================================
            SUM(
                CASE
                    WHEN management_group = 'Revenue' THEN management_amount
                    ELSE 0
                END
            ) AS revenue,
            -- ====================================================
            -- OTHER OPERATING INCOME
            -- ====================================================
            SUM(
                CASE
                    WHEN management_group = 'Other Operating Income' THEN management_amount
                    ELSE 0
                END
            ) AS other_operating_income,
            -- ====================================================
            -- OPERATING COSTS
            -- ====================================================
            SUM(
                CASE
                    WHEN management_group = 'Operating Costs' THEN management_amount
                    ELSE 0
                END
            ) AS operating_costs,
            -- ====================================================
            -- NON-CORE OPERATING ITEMS
            -- ====================================================
            SUM(
                CASE
                    WHEN management_group = 'Non-Core Operating Items' THEN management_amount
                    ELSE 0
                END
            ) AS non_core_operating_items,
            -- ====================================================
            -- EBITDA ADJUSTMENTS
            -- Depreciation + Provisions
            -- ====================================================
            SUM(
                CASE
                    WHEN management_group = 'EBITDA Adjustments' THEN management_amount
                    ELSE 0
                END
            ) AS ebitda_adjustments,
            -- ====================================================
            -- FINANCIAL RESULT
            -- Interest + FX + Other financial result
            -- ====================================================
            SUM(
                CASE
                    WHEN management_group = 'Financial Result' THEN management_amount
                    ELSE 0
                END
            ) AS financial_result,
            -- ====================================================
            -- TAX
            -- ====================================================
            SUM(
                CASE
                    WHEN management_group = 'Tax' THEN management_amount
                    ELSE 0
                END
            ) AS income_tax
        FROM
            management_detail
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
    -- BASE P&L COMPONENTS
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
    -- EBITDA includes:
    --   Revenue
    --   Other Operating Income
    --   Operating Costs
    --   Non-Core Operating Items
    --
    -- Depreciation and provisions are excluded because
    -- ebitda_included = FALSE.
    -- ========================================================
    (
        revenue + other_operating_income + operating_costs + non_core_operating_items
    ) AS ebitda,
    -- ========================================================
    -- EBIT
    --
    -- EBITDA + EBITDA adjustments.
    --
    -- EBITDA adjustments are already signed negatively
    -- through management_sign.
    -- ========================================================
    (
        revenue + other_operating_income + operating_costs + non_core_operating_items + ebitda_adjustments
    ) AS ebit,
    -- ========================================================
    -- EBT
    --
    -- EBIT + Financial Result.
    -- ========================================================
    (
        revenue + other_operating_income + operating_costs + non_core_operating_items + ebitda_adjustments + financial_result
    ) AS ebt,
    -- ========================================================
    -- NET PROFIT
    --
    -- EBT + Income Tax.
    --
    -- Income tax is already negative because the mapping
    -- contains management_sign = -1.
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
    -- EBT MARGIN
    -- ========================================================
    CASE
        WHEN revenue <> 0 THEN (
            revenue + other_operating_income + operating_costs + non_core_operating_items + ebitda_adjustments + financial_result
        ) / revenue
        ELSE NULL
    END AS ebt_margin,
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