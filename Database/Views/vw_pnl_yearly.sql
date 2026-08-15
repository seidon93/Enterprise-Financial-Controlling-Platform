CREATE OR REPLACE VIEW mart.vw_pnl_yearly AS
SELECT
    calendar_year,
    reporting_group,
    reporting_category,
    account_number,
    account_name,
    COUNT(*) AS month_row_count,
    SUM(debit_amount) AS debit_amount,
    SUM(credit_amount) AS credit_amount,
    SUM(signed_amount) AS signed_amount
FROM
    mart.vw_pnl_monthly
GROUP BY
    calendar_year,
    reporting_group,
    reporting_category,
    account_number,
    account_name;