-- ============================================================
-- EFAP - Power BI Management Reporting Layer
--
-- Object:
--     mart.vw_powerbi_management_reporting_monthly
--
-- Layer:
--     Mart / Power BI Reporting
--
-- Grain:
--     One row per calendar month
--
-- Purpose:
--     Single reporting-ready monthly dataset for Power BI.
--
-- Important:
--     This view does NOT recalculate business logic.
--     It only exposes already calculated measures from the
--     existing EFAP mart/controller layers.
--
-- Sources:
--     mart.vw_management_pnl
--     mart.vw_controller_plan_vs_actual_monthly
--     mart.vw_cash_flow_controller_monthly
-- ============================================================
DROP VIEW IF EXISTS mart.vw_powerbi_management_reporting_monthly;

CREATE VIEW mart.vw_powerbi_management_reporting_monthly AS
SELECT
    -- ========================================================
    -- CALENDAR
    -- ========================================================
    p.calendar_year,
    p.calendar_month,
    p.month_name,
    p.year_month,
    -- ========================================================
    -- MANAGEMENT P&L
    -- ========================================================
    p.revenue,
    p.other_operating_income,
    p.operating_costs,
    p.non_core_operating_items,
    p.ebitda_adjustments,
    p.ebitda,
    p.ebit_margin,
    p.financial_result,
    p.ebt,
    p.income_tax,
    p.net_profit,
    p.ebitda_margin,
    p.ebt_margin,
    p.net_profit_margin,
    -- ========================================================
    -- PLAN VS ACTUAL - REVENUE
    -- ========================================================
    v.plan_revenue,
    v.actual_revenue,
    v.revenue_variance,
    v.revenue_variance_pct,
    v.revenue_status,
    -- ========================================================
    -- PLAN VS ACTUAL - OPERATING COSTS
    -- ========================================================
    v.plan_operating_costs,
    v.actual_operating_costs,
    v.cost_variance,
    v.cost_variance_pct,
    v.cost_status,
    -- ========================================================
    -- PLAN VS ACTUAL - EBITDA
    -- ========================================================
    v.plan_ebitda,
    v.actual_ebitda,
    v.ebitda_variance,
    v.ebitda_variance_pct,
    v.ebitda_status,
    v.plan_ebitda_margin,
    v.actual_ebitda_margin,
    v.ebitda_margin_variance_pp,
    -- ========================================================
    -- PLAN VS ACTUAL - EBIT
    -- ========================================================
    v.plan_ebit,
    v.actual_ebit,
    v.ebit_variance,
    v.ebit_margin_variance_pp,
    -- ========================================================
    -- PLAN VS ACTUAL - EBT
    -- ========================================================
    v.plan_ebt,
    v.actual_ebt,
    v.ebt_variance,
    v.ebt_margin_variance_pp,
    -- ========================================================
    -- PLAN VS ACTUAL - NET PROFIT
    -- ========================================================
    v.plan_net_profit,
    v.actual_net_profit,
    v.net_profit_variance,
    v.net_profit_variance_pct,
    v.plan_net_profit_margin,
    v.actual_net_profit_margin,
    v.net_profit_margin_variance_pp,
    -- ========================================================
    -- CASH FLOW
    -- ========================================================
    c.net_profit AS cash_flow_net_profit,
    c.operating_cash_flow,
    c.investing_cash_flow,
    c.financing_cash_flow,
    c.net_cash_change,
    c.free_cash_flow,
    c.opening_cash,
    c.closing_cash,
    c.calculated_closing_cash,
    c.cash_reconciliation_difference,
    c.operating_cf_mom_change,
    c.operating_cf_mom_change_pct,
    c.net_cash_mom_change,
    c.fcf_mom_change,
    c.fcf_mom_change_pct,
    c.closing_cash_mom_change,
    -- ========================================================
    -- CASH FLOW YTD
    -- ========================================================
    c.operating_cash_flow_ytd,
    c.investing_cash_flow_ytd,
    c.financing_cash_flow_ytd,
    c.net_cash_change_ytd,
    -- ========================================================
    -- CASH CONVERSION
    -- ========================================================
    c.cash_conversion_ratio_pct,
    -- ========================================================
    -- LIQUIDITY / WORKING CAPITAL
    -- ========================================================
    c.cash_balance,
    c.current_assets,
    c.current_liabilities_balance,
    c.net_working_capital,
    c.operating_working_capital,
    c.current_ratio,
    c.quick_ratio,
    c.cash_ratio,
    -- ========================================================
    -- CONTROLLER STATUS
    -- ========================================================
    c.liquidity_status,
    c.cash_flow_status,
    c.cash_health_status,
    c.reconciliation_status
FROM
    mart.vw_management_pnl p
    LEFT JOIN mart.vw_controller_plan_vs_actual_monthly v ON v.calendar_year = p.calendar_year
    AND v.calendar_month = p.calendar_month
    LEFT JOIN mart.vw_cash_flow_controller_monthly c ON c.calendar_year = p.calendar_year
    AND c.calendar_month = p.calendar_month;