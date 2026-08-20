-- ============================================================
-- EFAP - Working Capital Monthly
--
-- Object: mart.vw_working_capital_monthly
-- Layer: Mart / Financial Controlling
-- Grain: One row per calendar month
--
-- Purpose:
--   Working Capital and liquidity KPIs for Financial Controlling.
--
-- KPIs:
--   Cash
--   Inventory
--   Receivables
--   Other Current Assets
--   Current Assets
--   Current Liabilities
--   Net Working Capital
--   Operating Working Capital
--   Current Ratio
--   Quick Ratio
--   Cash Ratio
--   NWC Change
--
-- Definitions:
--
--   Current Assets =
--       Cash
--     + Inventory
--     + Receivables
--     + Other Current Assets
--
--   Net Working Capital =
--       Current Assets
--     - Current Liabilities
--
--   Operating Working Capital =
--       Inventory
--     + Receivables
--     + Other Current Assets
--     - Current Liabilities
--
--   Current Ratio =
--       Current Assets / Current Liabilities
--
--   Quick Ratio =
--       (Cash + Receivables) / Current Liabilities
--
--   Cash Ratio =
--       Cash / Current Liabilities
--
-- ============================================================
CREATE OR REPLACE VIEW mart.vw_working_capital_monthly AS
WITH
    monthly AS (
        SELECT
            calendar_year,
            calendar_month,
            month_name,
            year_month,
            month_start_date,
            month_end_date,
            COALESCE(
                SUM(
                    CASE
                        WHEN management_category = 'Cash' THEN closing_balance
                        ELSE 0
                    END
                ),
                0
            ) AS cash_balance,
            COALESCE(
                SUM(
                    CASE
                        WHEN management_category = 'Inventory' THEN closing_balance
                        ELSE 0
                    END
                ),
                0
            ) AS inventory_balance,
            COALESCE(
                SUM(
                    CASE
                        WHEN management_category = 'Receivables' THEN closing_balance
                        ELSE 0
                    END
                ),
                0
            ) AS receivables_balance,
            COALESCE(
                SUM(
                    CASE
                        WHEN management_category = 'Other Current Assets' THEN closing_balance
                        ELSE 0
                    END
                ),
                0
            ) AS other_current_assets_balance,
            COALESCE(
                SUM(
                    CASE
                        WHEN management_category = 'Current Liabilities' THEN closing_balance
                        ELSE 0
                    END
                ),
                0
            ) AS current_liabilities_balance
        FROM
            mart.vw_balance_sheet_monthly
        GROUP BY
            calendar_year,
            calendar_month,
            month_name,
            year_month,
            month_start_date,
            month_end_date
    ),
    calculated AS (
        SELECT
            calendar_year,
            calendar_month,
            month_name,
            year_month,
            month_start_date,
            month_end_date,
            cash_balance,
            inventory_balance,
            receivables_balance,
            other_current_assets_balance,
            current_liabilities_balance,
            -- ====================================================
            -- CURRENT ASSETS
            -- ====================================================
            (
                cash_balance + inventory_balance + receivables_balance + other_current_assets_balance
            ) AS current_assets,
            -- ====================================================
            -- NET WORKING CAPITAL
            -- ====================================================
            (
                cash_balance + inventory_balance + receivables_balance + other_current_assets_balance - current_liabilities_balance
            ) AS net_working_capital,
            -- ====================================================
            -- OPERATING WORKING CAPITAL
            --
            -- Cash excluded.
            -- ====================================================
            (
                inventory_balance + receivables_balance + other_current_assets_balance - current_liabilities_balance
            ) AS operating_working_capital
        FROM
            monthly
    ),
    with_changes AS (
        SELECT
            *,
            LAG(net_working_capital) OVER (
                ORDER BY
                    calendar_year,
                    calendar_month
            ) AS previous_net_working_capital
        FROM
            calculated
    )
SELECT
    calendar_year,
    calendar_month,
    month_name,
    year_month,
    month_start_date,
    month_end_date,
    cash_balance,
    inventory_balance,
    receivables_balance,
    other_current_assets_balance,
    current_assets,
    current_liabilities_balance,
    net_working_capital,
    operating_working_capital,
    -- ========================================================
    -- CHANGE IN NWC
    -- ========================================================
    net_working_capital - previous_net_working_capital AS nwc_change,
    -- ========================================================
    -- CURRENT RATIO
    -- ========================================================
    CASE
        WHEN current_liabilities_balance <> 0 THEN current_assets / current_liabilities_balance
        ELSE NULL
    END AS current_ratio,
    -- ========================================================
    -- QUICK RATIO
    --
    -- Cash + Receivables
    -- ==================
    -- Current Liabilities
    -- ========================================================
    CASE
        WHEN current_liabilities_balance <> 0 THEN (cash_balance + receivables_balance) / current_liabilities_balance
        ELSE NULL
    END AS quick_ratio,
    -- ========================================================
    -- CASH RATIO
    -- ========================================================
    CASE
        WHEN current_liabilities_balance <> 0 THEN cash_balance / current_liabilities_balance
        ELSE NULL
    END AS cash_ratio
FROM
    with_changes;