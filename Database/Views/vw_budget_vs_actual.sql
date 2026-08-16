CREATE OR REPLACE VIEW mart.vw_budget_detail AS
SELECT
    b.budget_entry_key,
    -- Date
    b.budget_date_key,
    d.full_date,
    d.calendar_year,
    d.calendar_month,
    d.month_name,
    d.year_month,
    d.calendar_quarter,
    d.quarter_name,
    -- Company
    b.company_key,
    -- Account
    b.account_key,
    a.account_number,
    a.account_name,
    -- P&L Mapping
    pm.reporting_group,
    pm.reporting_category,
    -- Organizational dimensions
    b.cost_center_key,
    b.department_key,
    b.currency_key,
    -- Budget metadata
    b.budget_version,
    b.scenario,
    -- Budget
    b.budget_amount,
    b.budget_amount_local,
    -- Actual
    COALESCE(SUM(g.signed_amount), 0) AS actual_amount,
    -- Variance
    COALESCE(SUM(g.signed_amount), 0) - b.budget_amount_local AS variance_amount,
    CASE
        WHEN b.budget_amount_local = 0 THEN NULL
        ELSE (
            COALESCE(SUM(g.signed_amount), 0) - b.budget_amount_local
        ) / ABS(b.budget_amount_local) * 100
    END AS variance_pct,
    -- Source
    b.source_system,
    b.created_at,
    b.batch_id
FROM
    warehouse.fact_budget b
    LEFT JOIN warehouse.dim_date d ON d.date_key = b.budget_date_key
    LEFT JOIN warehouse.dim_account a ON a.account_key = b.account_key
    LEFT JOIN warehouse.dim_pnl_mapping pm ON pm.account_key = b.account_key
    LEFT JOIN warehouse.fact_gl g ON g.posting_date_key = b.budget_date_key
    AND g.company_key = b.company_key
    AND g.account_key = b.account_key
    AND (
        b.cost_center_key IS NULL
        OR g.cost_center_key = b.cost_center_key
    )
    AND (
        b.department_key IS NULL
        OR g.department_key = b.department_key
    )
GROUP BY
    b.budget_entry_key,
    b.budget_date_key,
    d.full_date,
    d.calendar_year,
    d.calendar_month,
    d.month_name,
    d.year_month,
    d.calendar_quarter,
    d.quarter_name,
    b.company_key,
    b.account_key,
    a.account_number,
    a.account_name,
    pm.reporting_group,
    pm.reporting_category,
    b.cost_center_key,
    b.department_key,
    b.currency_key,
    b.budget_version,
    b.scenario,
    b.budget_amount,
    b.budget_amount_local,
    b.source_system,
    b.created_at,
    b.batch_id;