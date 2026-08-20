-- ============================================================
-- EFAP - Controller KPI Validation
-- ============================================================
-- 1. Monthly KPI layer
SELECT
    COUNT(*) AS row_count,
    MIN(year_month) AS first_month,
    MAX(year_month) AS last_month
FROM
    mart.vw_controller_kpis_monthly;

-- 2. Latest available month
SELECT
    *
FROM
    mart.vw_controller_kpis_monthly
ORDER BY
    calendar_year DESC,
    calendar_month DESC
LIMIT
    1;

-- 3. Working Capital KPIs
SELECT
    year_month,
    dso_days,
    dio_days,
    dpo_days,
    cash_conversion_cycle_days,
    current_ratio,
    quick_ratio,
    cash_ratio
FROM
    mart.vw_controller_kpis_monthly
ORDER BY
    calendar_year,
    calendar_month;

-- 4. Controller status overview
SELECT
    year_month,
    ebitda_status,
    working_capital_status,
    liquidity_status,
    working_capital_efficiency_status
FROM
    mart.vw_controller_kpis_monthly
ORDER BY
    calendar_year,
    calendar_month;