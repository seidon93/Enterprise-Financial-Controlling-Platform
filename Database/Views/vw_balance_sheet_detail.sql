-- ============================================================
-- EFAP - Balance Sheet Detail
--
-- Object: mart.vw_balance_sheet_detail
-- Layer: Mart / Balance Sheet
-- Grain: One row per month and Balance Sheet account
-- ============================================================
CREATE OR REPLACE VIEW mart.vw_balance_sheet_detail AS
WITH
    monthly_movements AS (
        SELECT
            d.calendar_year,
            d.calendar_month,
            d.month_name,
            d.year_month,
            d.month_start_date,
            d.month_end_date,
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
            d.month_name,
            d.year_month,
            d.month_start_date,
            d.month_end_date,
            f.account_key
    ),
    balances AS (
        SELECT
            mm.calendar_year,
            mm.calendar_month,
            mm.month_name,
            mm.year_month,
            mm.month_start_date,
            mm.month_end_date,
            mm.account_key,
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
            mm.monthly_signed_amount,
            SUM(mm.monthly_signed_amount) OVER (
                PARTITION BY
                    mm.account_key
                ORDER BY
                    mm.calendar_year,
                    mm.calendar_month ROWS BETWEEN UNBOUNDED PRECEDING
                    AND CURRENT ROW
            ) AS closing_balance
        FROM
            monthly_movements mm
            INNER JOIN warehouse.dim_account a ON mm.account_key = a.account_key
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