CREATE OR REPLACE VIEW mart.vw_budget_vs_actual_monthly AS
WITH
    actual AS (
        SELECT
            calendar_year,
            calendar_month,
            month_name,
            year_month,
            reporting_group,
            reporting_category,
            account_number,
            account_name,
            SUM(signed_amount) AS actual_amount
        FROM
            mart.vw_pnl_monthly
        WHERE
            calendar_year = 2026
        GROUP BY
            calendar_year,
            calendar_month,
            month_name,
            year_month,
            reporting_group,
            reporting_category,
            account_number,
            account_name
    ),
    budget AS (
        SELECT
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
            SUM(budget_amount_local) AS budget_amount
        FROM
            mart.vw_budget_monthly
        GROUP BY
            calendar_year,
            calendar_month,
            month_name,
            year_month,
            reporting_group,
            reporting_category,
            account_number,
            account_name,
            budget_version,
            scenario
    )
SELECT
    COALESCE(a.calendar_year, b.calendar_year) AS calendar_year,
    COALESCE(a.calendar_month, b.calendar_month) AS calendar_month,
    COALESCE(a.month_name, b.month_name) AS month_name,
    COALESCE(a.year_month, b.year_month) AS year_month,
    COALESCE(a.reporting_group, b.reporting_group) AS reporting_group,
    COALESCE(a.reporting_category, b.reporting_category) AS reporting_category,
    COALESCE(a.account_number, b.account_number) AS account_number,
    COALESCE(a.account_name, b.account_name) AS account_name,
    b.budget_version,
    b.scenario,
    COALESCE(a.actual_amount, 0) AS actual_amount,
    COALESCE(b.budget_amount, 0) AS budget_amount,
    COALESCE(a.actual_amount, 0) - COALESCE(b.budget_amount, 0) AS variance_amount,
    CASE
        WHEN COALESCE(b.budget_amount, 0) = 0 THEN NULL
        ELSE (
            COALESCE(a.actual_amount, 0) - COALESCE(b.budget_amount, 0)
        ) / ABS(b.budget_amount) * 100
    END AS variance_pct
FROM
    actual a
    FULL OUTER JOIN budget b ON a.calendar_year = b.calendar_year
    AND a.calendar_month = b.calendar_month
    AND a.reporting_group = b.reporting_group
    AND a.reporting_category = b.reporting_category
    AND a.account_number = b.account_number;