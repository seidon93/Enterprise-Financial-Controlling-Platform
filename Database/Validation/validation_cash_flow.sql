-- ============================================================
-- EFAP - Cash Flow Validation
-- ============================================================
SELECT
    COUNT(*) AS row_count,
    MIN(year_month) AS first_month,
    MAX(year_month) AS last_month
FROM
    mart.vw_cash_flow_monthly;

SELECT
    *
FROM
    mart.vw_cash_flow_monthly
ORDER BY
    calendar_year DESC,
    calendar_month DESC
LIMIT
    1;

SELECT
    year_month,
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
ORDER BY
    calendar_year,
    calendar_month;

SELECT
    year_month,
    cash_balance,
    net_working_capital,
    current_ratio,
    quick_ratio,
    cash_ratio,
    operating_cash_flow,
    free_cash_flow,
    liquidity_status,
    cash_flow_status
FROM
    mart.vw_liquidity_monthly
ORDER BY
    calendar_year,
    calendar_month;