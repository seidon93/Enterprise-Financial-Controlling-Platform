-- ============================================================
-- EFAP - Liquidity Monthly
--
-- Object: mart.vw_liquidity_monthly
-- Layer: Mart / Financial Controlling
-- Grain: One row per calendar month
--
-- KPIs:
--   Cash
--   Net Working Capital
--   Current Ratio
--   Quick Ratio
--   Cash Ratio
--   Operating Cash Flow
--   Free Cash Flow proxy
--   Cash Burn / Generation Status
--
-- ============================================================
CREATE
OR REPLACE VIEW mart.vw_liquidity_monthly AS
SELECT
    c.calendar_year,
    c.calendar_month,
    c.year_month,
    w.cash_balance,
    w.current_assets,
    w.current_liabilities_balance,
    w.net_working_capital,
    w.operating_working_capital,
    w.current_ratio,
    w.quick_ratio,
    w.cash_ratio,
    c.operating_cash_flow,
    c.investing_cash_flow,
    c.financing_cash_flow,
    c.net_cash_change,
    c.opening_cash,
    c.closing_cash,
    c.cash_reconciliation_difference,
    -- ========================================================
    -- FREE CASH FLOW PROXY
    --
    -- Until a dedicated CAPEX transaction layer exists,
    -- investing CF remains the explicit proxy defined above.
    -- ========================================================
    (c.operating_cash_flow + c.investing_cash_flow) AS free_cash_flow,
    -- ========================================================
    -- LIQUIDITY STATUS
    -- ========================================================
    CASE
        WHEN w.current_ratio < 1 THEN 'LIQUIDITY_RISK'
        WHEN w.current_ratio < 1.5 THEN 'WATCH'
        ELSE 'HEALTHY'
    END AS liquidity_status,
    -- ========================================================
    -- CASH FLOW STATUS
    -- ========================================================
    CASE
        WHEN c.operating_cash_flow < 0
        AND c.net_cash_change < 0 THEN 'CASH_OUTFLOW'
        WHEN c.operating_cash_flow > 0
        AND c.net_cash_change > 0 THEN 'CASH_GENERATION'
        WHEN c.operating_cash_flow > 0
        AND c.net_cash_change <= 0 THEN 'OPERATING_CASH_CONVERTED_TO_OTHER_USES'
        ELSE 'MIXED'
    END AS cash_flow_status
FROM
    mart.vw_cash_flow_monthly c
    LEFT JOIN mart.vw_working_capital_monthly w ON w.calendar_year = c.calendar_year
    AND w.calendar_month = c.calendar_month;