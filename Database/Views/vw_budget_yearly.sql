CREATE OR REPLACE VIEW mart.vw_budget_yearly AS
SELECT
    calendar_year,
    reporting_group,
    reporting_category,
    account_number,
    account_name,
    budget_version,
    scenario,
    COUNT(*) AS month_row_count,
    SUM(budget_amount) AS budget_amount,
    SUM(budget_amount_local) AS budget_amount_local
FROM
    mart.vw_budget_monthly
GROUP BY
    calendar_year,
    reporting_group,
    reporting_category,
    account_number,
    account_name,
    budget_version,
    scenario;