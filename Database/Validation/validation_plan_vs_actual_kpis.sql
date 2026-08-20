-- ============================================================
-- EFAP - Plan vs Actual KPI Validation
-- ============================================================
-- 1. Row count and date range
SELECT
    COUNT(*) AS row_count,
    MIN(year_month) AS first_month,
    MAX(year_month) AS last_month
FROM
    mart.vw_pnl_plan_vs_actual_kpis_monthly;

-- 2. Latest available month
SELECT
    *
FROM
    mart.vw_controller_plan_vs_actual_monthly
ORDER BY
    calendar_year DESC,
    calendar_month DESC
LIMIT
    1;

-- 3. Monthly controller KPIs
SELECT
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
    ebitda_margin_variance_pp
FROM
    mart.vw_controller_plan_vs_actual_monthly
ORDER BY
    calendar_year,
    calendar_month;