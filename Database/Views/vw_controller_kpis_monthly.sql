-- ============================================================
-- EFAP - Controller KPIs Monthly
--
-- Object: mart.vw_controller_kpis_monthly
-- Layer: Mart / Financial Controlling
-- Grain: One row per calendar month
-- ============================================================
CREATE
OR REPLACE VIEW mart.vw_controller_kpis_monthly AS
SELECT
    p.calendar_year,
    p.calendar_month,
    p.year_month,
    -- ========================================================
    -- P&L
    -- ========================================================
    p.revenue,
    p.other_operating_income,
    p.operating_costs,
    p.non_core_operating_items,
    p.ebitda_adjustments,
    p.ebitda,
    p.ebit,
    p.financial_result,
    p.ebt,
    p.income_tax,
    p.net_profit,
    p.ebitda_margin,
    p.ebit_margin,
    p.ebt_margin,
    p.net_profit_margin,
    -- ========================================================
    -- WORKING CAPITAL
    -- ========================================================
    w.cash_balance,
    w.inventory_balance,
    w.receivables_balance,
    w.other_current_assets_balance,
    w.current_assets,
    w.current_liabilities_balance,
    w.net_working_capital,
    w.operating_working_capital,
    w.nwc_change,
    w.current_ratio,
    w.quick_ratio,
    w.cash_ratio,
    -- ========================================================
    -- DSO / DIO / DPO / CCC
    -- ========================================================
    k.dso_days,
    k.dio_days,
    k.dpo_days,
    k.cash_conversion_cycle_days,
    -- ========================================================
    -- CASH FLOW
    -- ========================================================
    cf.operating_cash_flow,
    cf.investing_cash_flow,
    cf.financing_cash_flow,
    cf.net_cash_change,
    cf.opening_cash,
    cf.closing_cash,
    cf.cash_reconciliation_difference,
    liq.free_cash_flow,
    -- ========================================================
    -- STATUS
    -- ========================================================
    CASE
        WHEN p.ebitda < 0 THEN 'NEGATIVE_EBITDA'
        WHEN p.ebitda = 0 THEN 'ZERO_EBITDA'
        ELSE 'POSITIVE_EBITDA'
    END AS ebitda_status,
    CASE
        WHEN w.net_working_capital < 0 THEN 'NEGATIVE_NWC'
        WHEN w.net_working_capital = 0 THEN 'ZERO_NWC'
        ELSE 'POSITIVE_NWC'
    END AS working_capital_status,
    CASE
        WHEN w.current_ratio < 1 THEN 'LIQUIDITY_RISK'
        WHEN w.current_ratio < 1.5 THEN 'WATCH'
        ELSE 'HEALTHY'
    END AS liquidity_status,
    liq.cash_flow_status
FROM
    mart.vw_management_pnl p
    LEFT JOIN mart.vw_working_capital_monthly w ON w.calendar_year = p.calendar_year
    AND w.calendar_month = p.calendar_month
    LEFT JOIN mart.vw_working_capital_kpis_monthly k ON k.calendar_year = p.calendar_year
    AND k.calendar_month = p.calendar_month
    LEFT JOIN mart.vw_cash_flow_monthly cf ON cf.calendar_year = p.calendar_year
    AND cf.calendar_month = p.calendar_month
    LEFT JOIN mart.vw_liquidity_monthly liq ON liq.calendar_year = p.calendar_year
    AND liq.calendar_month = p.calendar_month;