-- ============================================================
-- EFAP - Balance Sheet Detail
--
-- Object: mart.vw_balance_sheet_detail
-- Layer: Mart / Balance Sheet
-- Grain: One row per month and balance-sheet account
--
-- Purpose:
--   Provides monthly closing balances for Balance Sheet accounts.
--
-- Important:
--   signed_amount is CALCULATED here from fact_gl using
--   dim_account.normal_balance.
--
--   It does NOT exist in warehouse.fact_gl.
--
-- Balance logic:
--   Debit-normal account:
--       debit - credit
--
--   Credit-normal account:
--       credit - debit
--
-- Balance Sheet balance:
--   cumulative sum of monthly signed movements.
--
-- ============================================================
CREATE
OR REPLACE VIEW mart.vw_balance_sheet_detail AS
WITH
    fact_limits AS (
        SELECT
            MIN(posting_date_key) AS min_posting_date_key,
            MAX(posting_date_key) AS max_posting_date_key
        FROM
            warehouse.fact_gl
    ),
    month_calendar AS (
        SELECT DISTINCT
            d.calendar_year,
            d.calendar_month,
            d.month_name,
            d.year_month,
            d.month_start_date,
            d.month_end_date
        FROM
            warehouse.dim_date d
            CROSS JOIN fact_limits f
        WHERE
            d.date_key BETWEEN f.min_posting_date_key AND f.max_posting_date_key
    ),
    balance_sheet_accounts AS (
        SELECT
            a.account_key,
            a.account_number,
            a.account_name,
            a.account_type,
            a.account_class,
            a.account_group,
            a.statement_type,
            a.reporting_group,
            a.reporting_category,
            a.normal_balance,
            a.is_posting_account,
            a.is_active
        FROM
            warehouse.dim_account a
        WHERE
            a.statement_type = 'Balance Sheet'
            AND a.is_active = TRUE
    ),
    monthly_movements AS (
        SELECT
            d.calendar_year,
            d.calendar_month,
            d.year_month,
            f.account_key,
            SUM(
                CASE
                    WHEN a.normal_balance = 'Debit' THEN f.debit_amount - f.credit_amount
                    WHEN a.normal_balance = 'Credit' THEN f.credit_amount - f.debit_amount
                    ELSE f.debit_amount - f.credit_amount
                END
            ) AS monthly_signed_amount
        FROM
            warehouse.fact_gl f
            INNER JOIN warehouse.dim_account a ON f.account_key = a.account_key
            INNER JOIN warehouse.dim_date d ON f.posting_date_key = d.date_key
        WHERE
            a.statement_type = 'Balance Sheet'
            AND a.is_active = TRUE
        GROUP BY
            d.calendar_year,
            d.calendar_month,
            d.year_month,
            f.account_key
    ),
    account_months AS (
        SELECT
            m.calendar_year,
            m.calendar_month,
            m.month_name,
            m.year_month,
            m.month_start_date,
            m.month_end_date,
            a.account_key,
            a.account_number,
            a.account_name,
            a.account_type,
            a.account_class,
            a.account_group,
            a.statement_type,
            a.reporting_group,
            a.reporting_category,
            a.normal_balance,
            a.is_posting_account,
            a.is_active,
            COALESCE(mm.monthly_signed_amount, 0) AS monthly_signed_amount
        FROM
            month_calendar m
            CROSS JOIN balance_sheet_accounts a
            LEFT JOIN monthly_movements mm ON mm.calendar_year = m.calendar_year
            AND mm.calendar_month = m.calendar_month
            AND mm.account_key = a.account_key
    ),
    balances AS (
        SELECT
            calendar_year,
            calendar_month,
            month_name,
            year_month,
            month_start_date,
            month_end_date,
            account_key,
            account_number,
            account_name,
            account_type,
            account_class,
            account_group,
            statement_type,
            reporting_group,
            reporting_category,
            normal_balance,
            is_posting_account,
            is_active,
            monthly_signed_amount,
            SUM(monthly_signed_amount) OVER (
                PARTITION BY
                    account_key
                ORDER BY
                    calendar_year,
                    calendar_month ROWS BETWEEN UNBOUNDED PRECEDING
                    AND CURRENT ROW
            ) AS closing_balance
        FROM
            account_months
    )
SELECT
    calendar_year,
    calendar_month,
    month_name,
    year_month,
    month_start_date,
    month_end_date,
    account_key,
    account_number,
    account_name,
    account_type,
    account_class,
    account_group,
    statement_type,
    reporting_group,
    reporting_category,
    normal_balance,
    is_posting_account,
    is_active,
    monthly_signed_amount,
    closing_balance
FROM
    balances;