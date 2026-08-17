CREATE OR REPLACE VIEW mart.vw_budget_monthly AS
SELECT
    budget_date_key,
    calendar_year,
    calendar_month,
    month_name,
    year_month,
    reporting_group,
    reporting_category,
    account_number,
    account_name,
    budget_version,
    scenario,
    COUNT(*) AS row_count,
    SUM(budget_amount) AS budget_amount,
    SUM(budget_amount_local) AS budget_amount_local
FROM
    mart.vw_budget_detail
GROUP BY
    budget_date_key,
    calendar_year,
    calendar_month,
    month_name,
    year_month,
    reporting_group,
    reporting_category,
    account_number,
    account_name,
    budget_version,
    scenario;