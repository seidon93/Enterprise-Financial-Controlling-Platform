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
            SUM(
                CASE
                    WHEN a.normal_balance = 'Credit' THEN COALESCE(g.credit_amount, 0) - COALESCE(g.debit_amount, 0)
                    WHEN a.normal_balance = 'Debit' THEN COALESCE(g.debit_amount, 0) - COALESCE(g.credit_amount, 0)
                    ELSE 0
                END
            ) AS actual_amount,
            COUNT(*) AS actual_line_count
        FROM
            warehouse.fact_gl g
            JOIN warehouse.dim_date d ON d.date_key = g.posting_date_key
            JOIN warehouse.dim_account a ON a.account_key = g.account_key
        WHERE
            a.statement_type = 'Profit and Loss'
        GROUP BY
            d.calendar_year,
            d.calendar_month,
            d.year_month,
            g.company_key,
            g.cost_center_key,
            g.department_key,
            g.account_key
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
            SUM(COALESCE(b.budget_amount_local, 0)) AS budget_amount,
            COUNT(*) AS budget_line_count
        FROM
            warehouse.fact_budget b
            JOIN warehouse.dim_date d ON d.date_key = b.budget_date_key
        GROUP BY
            d.calendar_year,
            d.calendar_month,
            d.year_month,
            b.company_key,
            b.cost_center_key,
            b.department_key,
            b.account_key
    )
SELECT
    COALESCE(ac.calendar_year, bu.calendar_year) AS calendar_year,
    COALESCE(ac.calendar_month, bu.calendar_month) AS calendar_month,
    COALESCE(ac.year_month, bu.year_month) AS year_month,
    COALESCE(ac.company_key, bu.company_key) AS company_key,
    COALESCE(ac.cost_center_key, bu.cost_center_key) AS cost_center_key,
    COALESCE(ac.department_key, bu.department_key) AS department_key,
    COALESCE(ac.account_key, bu.account_key) AS account_key,
    a.account_number,
    a.account_name,
    a.account_type,
    a.account_class,
    a.account_group,
    a.statement_type,
    a.reporting_group,
    a.reporting_category,
    a.normal_balance,
    ac.actual_amount,
    bu.budget_amount,
    COALESCE(ac.actual_amount, 0) - COALESCE(bu.budget_amount, 0) AS variance_amount,
    CASE
        WHEN COALESCE(bu.budget_amount, 0) = 0 THEN NULL
        ELSE (
            COALESCE(ac.actual_amount, 0) - COALESCE(bu.budget_amount, 0)
        ) / ABS(bu.budget_amount) * 100
    END AS variance_pct,
    CASE
        WHEN ac.account_key IS NOT NULL
        AND bu.account_key IS NOT NULL THEN 'BOTH'
        WHEN ac.account_key IS NOT NULL THEN 'ACTUAL_ONLY'
        ELSE 'BUDGET_ONLY'
    END AS data_status,
    COALESCE(ac.actual_line_count, 0) AS actual_line_count,
    COALESCE(bu.budget_line_count, 0) AS budget_line_count
FROM
    actual ac
    FULL OUTER JOIN budget bu ON ac.calendar_year = bu.calendar_year
    AND ac.calendar_month = bu.calendar_month
    AND ac.company_key = bu.company_key
    AND ac.cost_center_key IS NOT DISTINCT FROM bu.cost_center_key
    AND ac.department_key IS NOT DISTINCT FROM bu.department_key
    AND ac.account_key = bu.account_key
    JOIN warehouse.dim_account a ON a.account_key = COALESCE(ac.account_key, bu.account_key);