-- =============================================================================
-- EFAP
-- -----------------------------------------------------------------------------
-- Object       : vw_pnl_budget_vs_actual.sql
-- Object Type  : Grain View
-- Layer        : Reporting
-- Version      : 1.0.0
-- Status       : Development
--
-- Grain:
--   Year × Month × Company × Cost Center × Department × Account
--
-- Purpose:
--   P&L Budget vs Actual comparison at detailed reporting grain.
--
-- Important:
--   fact_gl does NOT contain:
--       - signed_amount
--       - account_type
--       - reporting_group
--       - reporting_category
--
--   Account attributes are therefore sourced from dim_account.
--   Actual amount is calculated from fact_gl.amount_local.
-- =============================================================================
CREATE OR REPLACE VIEW warehouse.vw_pnl_budget_vs_actual AS
WITH
    actual AS (
        SELECT
            d.calendar_year,
            d.calendar_month,
            d.year_month,
            g.company_key,
            g.cost_center_key,
            g.department_key,
            g.account_key,
            a.account_number,
            a.account_name,
            a.account_type,
            a.account_class,
            a.account_group,
            a.statement_type,
            a.reporting_group,
            a.reporting_category,
            a.normal_balance,
            SUM(COALESCE(g.amount_local, 0)) AS actual_amount,
            SUM(
                COALESCE(g.debit_amount, 0) - COALESCE(g.credit_amount, 0)
            ) AS actual_signed_amount_check,
            COUNT(*) AS actual_line_count
        FROM
            warehouse.fact_gl AS g
            INNER JOIN warehouse.dim_date AS d ON d.date_key = g.posting_date_key
            INNER JOIN warehouse.dim_account AS a ON a.account_key = g.account_key
        WHERE
            a.statement_type = 'Profit and Loss'
        GROUP BY
            d.calendar_year,
            d.calendar_month,
            d.year_month,
            g.company_key,
            g.cost_center_key,
            g.department_key,
            g.account_key,
            a.account_number,
            a.account_name,
            a.account_type,
            a.account_class,
            a.account_group,
            a.statement_type,
            a.reporting_group,
            a.reporting_category,
            a.normal_balance
    ),
    budget AS (
        SELECT
            d.calendar_year,
            d.calendar_month,
            d.year_month,
            b.company_key,
            b.cost_center_key,
            b.department_key,
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
            SUM(COALESCE(b.budget_amount_local, 0)) AS budget_amount,
            COUNT(*) AS budget_line_count
        FROM
            warehouse.fact_budget AS b
            INNER JOIN warehouse.dim_date AS d ON d.date_key = b.budget_date_key
            INNER JOIN warehouse.dim_account AS a ON a.account_key = b.account_key
        WHERE
            a.statement_type = 'Profit and Loss'
        GROUP BY
            d.calendar_year,
            d.calendar_month,
            d.year_month,
            b.company_key,
            b.cost_center_key,
            b.department_key,
            b.account_key,
            a.account_number,
            a.account_name,
            a.account_type,
            a.account_class,
            a.account_group,
            a.statement_type,
            a.reporting_group,
            a.reporting_category,
            a.normal_balance
    )
SELECT
    COALESCE(ac.calendar_year, bu.calendar_year) AS calendar_year,
    COALESCE(ac.calendar_month, bu.calendar_month) AS calendar_month,
    COALESCE(ac.year_month, bu.year_month) AS year_month,
    COALESCE(ac.company_key, bu.company_key) AS company_key,
    COALESCE(ac.cost_center_key, bu.cost_center_key) AS cost_center_key,
    COALESCE(ac.department_key, bu.department_key) AS department_key,
    COALESCE(ac.account_key, bu.account_key) AS account_key,
    COALESCE(ac.account_number, bu.account_number) AS account_number,
    COALESCE(ac.account_name, bu.account_name) AS account_name,
    COALESCE(ac.account_type, bu.account_type) AS account_type,
    COALESCE(ac.account_class, bu.account_class) AS account_class,
    COALESCE(ac.account_group, bu.account_group) AS account_group,
    COALESCE(ac.statement_type, bu.statement_type) AS statement_type,
    COALESCE(ac.reporting_group, bu.reporting_group) AS reporting_group,
    COALESCE(ac.reporting_category, bu.reporting_category) AS reporting_category,
    COALESCE(ac.normal_balance, bu.normal_balance) AS normal_balance,
    COALESCE(ac.actual_amount, 0) AS actual_amount,
    COALESCE(bu.budget_amount, 0) AS budget_amount,
    COALESCE(ac.actual_amount, 0) - COALESCE(bu.budget_amount, 0) AS variance_amount,
    CASE
        WHEN COALESCE(bu.budget_amount, 0) = 0 THEN NULL
        ELSE (
            COALESCE(ac.actual_amount, 0) - COALESCE(bu.budget_amount, 0)
        ) / ABS(bu.budget_amount) * 100
    END AS variance_pct,
    CASE
        WHEN ac.account_key IS NULL THEN 'BUDGET_ONLY'
        WHEN bu.account_key IS NULL THEN 'ACTUAL_ONLY'
        ELSE 'BOTH'
    END AS data_status,
    COALESCE(ac.actual_line_count, 0) AS actual_line_count,
    COALESCE(bu.budget_line_count, 0) AS budget_line_count,
    COALESCE(ac.actual_signed_amount_check, 0) AS actual_signed_amount_check
FROM
    actual AS ac
    FULL OUTER JOIN budget AS bu ON ac.calendar_year = bu.calendar_year
    AND ac.calendar_month = bu.calendar_month
    AND ac.company_key = bu.company_key
    AND ac.cost_center_key = bu.cost_center_key
    AND ac.department_key = bu.department_key
    AND ac.account_key = bu.account_key;