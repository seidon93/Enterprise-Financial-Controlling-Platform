-- ============================================================
-- EFAP - Cash Flow Controller Monthly
--
-- Object: mart.vw_cash_flow_controller_monthly
-- Layer: Mart / Financial Controlling
-- Grain: One row per calendar month
--
-- Purpose:
--   Controller-oriented cash flow view combining:
--     - Indirect cash flow components (Operating / Investing / Financing)
--     - Free Cash Flow proxy
--     - Month-over-month cash flow trends
--     - Year-to-date cumulations
--     - Liquidity ratios (Current / Quick / Cash)
--     - Controller status flags
--
-- Sources:
--   mart.vw_cash_flow_monthly   - indirect cash flow
--   mart.vw_liquidity_monthly   - liquidity KPIs & FCF
--   mart.vw_cash_flow_ytd       - YTD cumulations
--
-- ============================================================
CREATE OR REPLACE VIEW mart.vw_cash_flow_controller_monthly AS
WITH
    cf AS (
        SELECT
            calendar_year,
            calendar_month,
            year_month,
            net_profit,
            operating_cash_flow,
            investing_cash_flow,
            financing_cash_flow,
            net_cash_change,
            opening_cash,
            closing_cash,
            calculated_closing_cash,
            cash_reconciliation_difference
        FROM
            mart.vw_cash_flow_monthly
    ),
    liq AS (
        SELECT
            calendar_year,
            calendar_month,
            cash_balance,
            current_assets,
            current_liabilities_balance,
            net_working_capital,
            operating_working_capital,
            current_ratio,
            quick_ratio,
            cash_ratio,
            free_cash_flow,
            liquidity_status,
            cash_flow_status
        FROM
            mart.vw_liquidity_monthly
    ),
    ytd AS (
        SELECT
            calendar_year,
            calendar_month,
            operating_cash_flow_ytd,
            investing_cash_flow_ytd,
            financing_cash_flow_ytd,
            net_cash_change_ytd
        FROM
            mart.vw_cash_flow_ytd
    ),
    combined AS (
        SELECT
            cf.calendar_year,
            cf.calendar_month,
            cf.year_month,
            -- ========================================================
            -- NET PROFIT (starting point for indirect CF)
            -- ========================================================
            cf.net_profit,
            -- ========================================================
            -- CASH FLOW COMPONENTS
            -- ========================================================
            cf.operating_cash_flow,
            cf.investing_cash_flow,
            cf.financing_cash_flow,
            cf.net_cash_change,
            -- ========================================================
            -- FREE CASH FLOW
            -- ========================================================
            liq.free_cash_flow,
            -- ========================================================
            -- CASH POSITIONS
            -- ========================================================
            cf.opening_cash,
            cf.closing_cash,
            cf.calculated_closing_cash,
            cf.cash_reconciliation_difference,
            -- ========================================================
            -- MONTH-OVER-MONTH TRENDS
            -- ========================================================
            LAG(cf.operating_cash_flow) OVER (
                ORDER BY
                    cf.calendar_year,
                    cf.calendar_month
            ) AS prev_operating_cash_flow,
            LAG(cf.net_cash_change) OVER (
                ORDER BY
                    cf.calendar_year,
                    cf.calendar_month
            ) AS prev_net_cash_change,
            LAG(liq.free_cash_flow) OVER (
                ORDER BY
                    cf.calendar_year,
                    cf.calendar_month
            ) AS prev_free_cash_flow,
            LAG(cf.closing_cash) OVER (
                ORDER BY
                    cf.calendar_year,
                    cf.calendar_month
            ) AS prev_closing_cash,
            -- ========================================================
            -- YTD CUMULATIONS
            -- ========================================================
            ytd.operating_cash_flow_ytd,
            ytd.investing_cash_flow_ytd,
            ytd.financing_cash_flow_ytd,
            ytd.net_cash_change_ytd,
            -- ========================================================
            -- LIQUIDITY RATIOS
            -- ========================================================
            liq.cash_balance,
            liq.current_assets,
            liq.current_liabilities_balance,
            liq.net_working_capital,
            liq.operating_working_capital,
            liq.current_ratio,
            liq.quick_ratio,
            liq.cash_ratio,
            -- ========================================================
            -- STATUS FLAGS FROM LIQUIDITY
            -- ========================================================
            liq.liquidity_status,
            liq.cash_flow_status
        FROM
            cf
            LEFT JOIN liq ON liq.calendar_year = cf.calendar_year
            AND liq.calendar_month = cf.calendar_month
            LEFT JOIN ytd ON ytd.calendar_year = cf.calendar_year
            AND ytd.calendar_month = cf.calendar_month
    )
SELECT
    calendar_year,
    calendar_month,
    year_month,
    -- ========================================================
    -- NET PROFIT
    -- ========================================================
    net_profit,
    -- ========================================================
    -- CASH FLOW COMPONENTS
    -- ========================================================
    operating_cash_flow,
    investing_cash_flow,
    financing_cash_flow,
    net_cash_change,
    free_cash_flow,
    -- ========================================================
    -- CASH POSITIONS
    -- ========================================================
    opening_cash,
    closing_cash,
    calculated_closing_cash,
    cash_reconciliation_difference,
    -- ========================================================
    -- MONTH-OVER-MONTH TRENDS
    -- ========================================================
    operating_cash_flow - COALESCE(prev_operating_cash_flow, 0) AS operating_cf_mom_change,
    CASE
        WHEN prev_operating_cash_flow <> 0
        THEN (operating_cash_flow - prev_operating_cash_flow) / ABS(prev_operating_cash_flow) * 100
        ELSE NULL
    END AS operating_cf_mom_change_pct,
    net_cash_change - COALESCE(prev_net_cash_change, 0) AS net_cash_mom_change,
    free_cash_flow - COALESCE(prev_free_cash_flow, 0) AS fcf_mom_change,
    CASE
        WHEN prev_free_cash_flow <> 0
        THEN (free_cash_flow - prev_free_cash_flow) / ABS(prev_free_cash_flow) * 100
        ELSE NULL
    END AS fcf_mom_change_pct,
    closing_cash - COALESCE(prev_closing_cash, 0) AS closing_cash_mom_change,
    -- ========================================================
    -- YTD CUMULATIONS
    -- ========================================================
    operating_cash_flow_ytd,
    investing_cash_flow_ytd,
    financing_cash_flow_ytd,
    net_cash_change_ytd,
    -- ========================================================
    -- CASH CONVERSION EFFICIENCY
    --
    -- How much of Net Profit converts to Operating CF.
    -- ========================================================
    CASE
        WHEN net_profit <> 0
        THEN operating_cash_flow / ABS(net_profit) * 100
        ELSE NULL
    END AS cash_conversion_ratio_pct,
    -- ========================================================
    -- LIQUIDITY RATIOS
    -- ========================================================
    cash_balance,
    current_assets,
    current_liabilities_balance,
    net_working_capital,
    operating_working_capital,
    current_ratio,
    quick_ratio,
    cash_ratio,
    -- ========================================================
    -- CONTROLLER STATUS FLAGS
    -- ========================================================
    liquidity_status,
    cash_flow_status,
    CASE
        WHEN operating_cash_flow > 0 AND free_cash_flow > 0 THEN 'STRONG'
        WHEN operating_cash_flow > 0 AND free_cash_flow <= 0 THEN 'ADEQUATE'
        WHEN operating_cash_flow <= 0 AND closing_cash > 0 THEN 'WATCH'
        ELSE 'ALERT'
    END AS cash_health_status,
    CASE
        WHEN cash_reconciliation_difference = 0 THEN 'RECONCILED'
        WHEN ABS(cash_reconciliation_difference) < 1 THEN 'MINOR_DIFF'
        ELSE 'UNRECONCILED'
    END AS reconciliation_status
FROM
    combined;