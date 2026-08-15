CREATE OR REPLACE VIEW mart.vw_pnl_monthly AS
SELECT
    posting_date_key,
    calendar_year,
    calendar_month,
    month_name,
    year_month,
    reporting_group,
    reporting_category,
    account_number,
    account_name,
    COUNT(*) AS row_count,
    SUM(debit_amount) AS debit_amount,
    SUM(credit_amount) AS credit_amount,
    SUM(signed_amount) AS signed_amount
FROM
    mart.vw_pnl_detail
GROUP BY
    posting_date_key,
    calendar_year,
    calendar_month,
    month_name,
    year_month,
    reporting_group,
    reporting_category,
    account_number,
    account_name;