-- ============================================================
-- EFAP - Controller Plan vs Actual
-- ============================================================
CREATE
OR REPLACE VIEW mart.vw_controller_plan_vs_actual_monthly AS
SELECT
    calendar_year,
    calendar_month,
    year_month,
    plan_revenue,
    actual_revenue,
    revenue_variance,
    revenue_variance_pct,
    revenue_status,
    plan_operating_costs,
    actual_operating_costs,
    cost_variance,
    cost_variance_pct,
    cost_status,
    plan_ebitda,
    actual_ebitda,
    ebitda_variance,
    ebitda_variance_pct,
    ebitda_status,
    plan_ebitda_margin,
    actual_ebitda_margin,
    ebitda_margin_variance_pp,
    actual_net_profit
FROM
    mart.vw_pnl_plan_vs_actual_kpis_monthly;