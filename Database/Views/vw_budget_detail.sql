CREATE
OR REPLACE VIEW mart.vw_budget_detail AS
SELECT
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
    a.account_type,
    a.account_class,
    a.account_group,
    a.statement_type,
    a.reporting_group,
    a.reporting_category,
    a.normal_balance,
    b.cost_center_key,
    b.department_key,
    b.currency_key,
    b.budget_version,
    b.scenario,
    b.budget_amount,
    b.budget_amount_local,
    b.source_system,
    b.created_at,
    b.batch_id
FROM
    warehouse.fact_budget b
    LEFT JOIN warehouse.dim_date d ON b.budget_date_key = d.date_key
    LEFT JOIN warehouse.dim_account a ON b.account_key = a.account_key;