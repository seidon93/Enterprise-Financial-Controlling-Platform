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
    ),
    cutoff AS (
        SELECT
            MAX(full_date) AS actual_through_date
        FROM
            mart.vw_pnl_detail
        WHERE
            calendar_year = 2026
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
    c.actual_through_date,
    CASE
        WHEN a.actual_amount IS NOT NULL THEN 'ACTUAL_AVAILABLE'
        ELSE 'NO_ACTUAL'
    END AS actual_status,
    CASE
        WHEN COALESCE(a.calendar_year, b.calendar_year) = EXTRACT(
            YEAR
            FROM
                c.actual_through_date
        )
        AND COALESCE(a.calendar_month, b.calendar_month) < EXTRACT(
            MONTH
            FROM
                c.actual_through_date
        ) THEN 'CLOSED'
        WHEN COALESCE(a.calendar_year, b.calendar_year) = EXTRACT(
            YEAR
            FROM
                c.actual_through_date
        )
        AND COALESCE(a.calendar_month, b.calendar_month) = EXTRACT(
            MONTH
            FROM
                c.actual_through_date
        ) THEN 'PARTIAL'
        ELSE 'NO_ACTUAL'
    END AS period_status,
    CASE
        WHEN COALESCE(a.calendar_year, b.calendar_year) = EXTRACT(
            YEAR
            FROM
                c.actual_through_date
        )
        AND COALESCE(a.calendar_month, b.calendar_month) < EXTRACT(
            MONTH
            FROM
                c.actual_through_date
        ) THEN a.actual_amount
        ELSE NULL
    END AS actual_amount,
    b.budget_amount,
    CASE
        WHEN COALESCE(a.calendar_year, b.calendar_year) = EXTRACT(
            YEAR
            FROM
                c.actual_through_date
        )
        AND COALESCE(a.calendar_month, b.calendar_month) < EXTRACT(
            MONTH
            FROM
                c.actual_through_date
        ) THEN a.actual_amount - b.budget_amount
        ELSE NULL
    END AS variance_amount,
    CASE
        WHEN COALESCE(a.calendar_year, b.calendar_year) = EXTRACT(
            YEAR
            FROM
                c.actual_through_date
        )
        AND COALESCE(a.calendar_month, b.calendar_month) < EXTRACT(
            MONTH
            FROM
                c.actual_through_date
        )
        AND b.budget_amount <> 0 THEN (a.actual_amount - b.budget_amount) / ABS(b.budget_amount) * 100
        ELSE NULL
    END AS variance_pct
FROM
    actual a
    FULL OUTER JOIN budget b ON a.calendar_year = b.calendar_year
    AND a.calendar_month = b.calendar_month
    AND a.reporting_group = b.reporting_group
    AND a.reporting_category = b.reporting_category
    AND a.account_number = b.account_number
    CROSS JOIN cutoff c;