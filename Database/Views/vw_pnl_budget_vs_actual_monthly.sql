CREATE OR REPLACE VIEW mart.vw_pnl_budget_vs_actual_monthly AS
WITH
    actual AS (
        SELECT
            d.calendar_year,
            d.calendar_month,
            d.year_month,
            g.company_key,
            g.account_key,
            g.cost_center_key,
            g.department_key,
            g.currency_key,
            a.account_number,
            a.account_name,
            a.account_type,
            a.account_class,
            a.account_group,
            a.statement_type,
            a.reporting_group,
            a.reporting_category,
            a.normal_balance,
            SUM(
                CASE
                    WHEN a.normal_balance = 'Debit' THEN g.debit_amount - g.credit_amount
                    WHEN a.normal_balance = 'Credit' THEN g.credit_amount - g.debit_amount
                    ELSE g.debit_amount - g.credit_amount
                END
            ) AS actual_amount
        FROM
            warehouse.fact_gl g
            INNER JOIN warehouse.dim_date d ON d.date_key = g.posting_date_key
            INNER JOIN warehouse.dim_account a ON a.account_key = g.account_key
        WHERE
            a.statement_type = 'Profit and Loss'
        GROUP BY
            d.calendar_year,
            d.calendar_month,
            d.year_month,
            g.company_key,
            g.account_key,
            g.cost_center_key,
            g.department_key,
            g.currency_key,
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
            b.account_key,
            b.cost_center_key,
            b.department_key,
            b.currency_key,
            a.account_number,
            a.account_name,
            a.account_type,
            a.account_class,
            a.account_group,
            a.statement_type,
            a.reporting_group,
            a.reporting_category,
            a.normal_balance,
            SUM(b.budget_amount_local) AS budget_amount
        FROM
            warehouse.fact_budget b
            INNER JOIN warehouse.dim_date d ON d.date_key = b.budget_date_key
            INNER JOIN warehouse.dim_account a ON a.account_key = b.account_key
        WHERE
            a.statement_type = 'Profit and Loss'
        GROUP BY
            d.calendar_year,
            d.calendar_month,
            d.year_month,
            b.company_key,
            b.account_key,
            b.cost_center_key,
            b.department_key,
            b.currency_key,
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
    combined AS (
        SELECT
            COALESCE(a.calendar_year, b.calendar_year) AS calendar_year,
            COALESCE(a.calendar_month, b.calendar_month) AS calendar_month,
            COALESCE(a.year_month, b.year_month) AS year_month,
            COALESCE(a.company_key, b.company_key) AS company_key,
            COALESCE(a.account_key, b.account_key) AS account_key,
            COALESCE(a.cost_center_key, b.cost_center_key) AS cost_center_key,
            COALESCE(a.department_key, b.department_key) AS department_key,
            COALESCE(a.currency_key, b.currency_key) AS currency_key,
            COALESCE(a.account_number, b.account_number) AS account_number,
            COALESCE(a.account_name, b.account_name) AS account_name,
            COALESCE(a.account_type, b.account_type) AS account_type,
            COALESCE(a.account_class, b.account_class) AS account_class,
            COALESCE(a.account_group, b.account_group) AS account_group,
            COALESCE(a.statement_type, b.statement_type) AS statement_type,
            COALESCE(a.reporting_group, b.reporting_group) AS reporting_group,
            COALESCE(a.reporting_category, b.reporting_category) AS reporting_category,
            COALESCE(a.normal_balance, b.normal_balance) AS normal_balance,
            a.actual_amount,
            b.budget_amount
        FROM
            actual a
            FULL OUTER JOIN budget b ON a.calendar_year = b.calendar_year
            AND a.calendar_month = b.calendar_month
            AND a.company_key = b.company_key
            AND a.account_key = b.account_key
            AND COALESCE(a.cost_center_key, -1) = COALESCE(b.cost_center_key, -1)
            AND COALESCE(a.department_key, -1) = COALESCE(b.department_key, -1)
            AND COALESCE(a.currency_key, -1) = COALESCE(b.currency_key, -1)
    )
SELECT
    calendar_year,
    calendar_month,
    year_month,
    company_key,
    account_key,
    cost_center_key,
    department_key,
    currency_key,
    account_number,
    account_name,
    account_type,
    account_class,
    account_group,
    statement_type,
    reporting_group,
    reporting_category,
    normal_balance,
    actual_amount,
    budget_amount,
    CASE
        WHEN actual_amount IS NULL THEN NULL
        WHEN budget_amount IS NULL THEN NULL
        ELSE actual_amount - budget_amount
    END AS variance_amount,
    CASE
        WHEN actual_amount IS NULL
        OR budget_amount IS NULL
        OR budget_amount = 0 THEN NULL
        ELSE (actual_amount - budget_amount) / ABS(budget_amount) * 100
    END AS variance_pct,
    CASE
        WHEN actual_amount IS NULL
        AND budget_amount IS NOT NULL THEN 'BUDGET_ONLY'
        WHEN actual_amount IS NOT NULL
        AND budget_amount IS NULL THEN 'ACTUAL_ONLY'
        WHEN actual_amount IS NOT NULL
        AND budget_amount IS NOT NULL THEN 'BOTH'
        ELSE 'NO_DATA'
    END AS data_status
FROM
    combined;