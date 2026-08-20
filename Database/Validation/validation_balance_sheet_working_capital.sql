-- ============================================================
-- EFAP - Balance Sheet / Working Capital Validation
-- ============================================================
-- ============================================================
-- 1. Row count
-- ============================================================
SELECT
    COUNT(*) AS row_count
FROM
    mart.vw_working_capital_monthly;

-- ============================================================
-- 2. Latest available month
-- ============================================================
SELECT
    *
FROM
    mart.vw_working_capital_monthly
ORDER BY
    calendar_year DESC,
    calendar_month DESC
LIMIT
    1;

-- ============================================================
-- 3. Balance Sheet categories
-- ============================================================
SELECT
    calendar_year,
    calendar_month,
    management_category,
    SUM(closing_balance) AS closing_balance
FROM
    mart.vw_balance_sheet_monthly
GROUP BY
    calendar_year,
    calendar_month,
    management_category
ORDER BY
    calendar_year,
    calendar_month,
    management_category;

-- ============================================================
-- 4. Working Capital KPIs
-- ============================================================
SELECT
    calendar_year,
    calendar_month,
    year_month,
    cash_balance,
    inventory_balance,
    receivables_balance,
    other_current_assets_balance,
    current_assets,
    current_liabilities_balance,
    net_working_capital,
    operating_working_capital,
    nwc_change,
    current_ratio,
    quick_ratio,
    cash_ratio
FROM
    mart.vw_working_capital_monthly
ORDER BY
    calendar_year,
    calendar_month;