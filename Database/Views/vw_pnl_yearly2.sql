CREATE VIEW mart.vw_pnl_yearly2 AS
SELECT
    calendar_year,
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
    calendar_year,
    reporting_group,
    reporting_category,
    account_number,
    account_name;