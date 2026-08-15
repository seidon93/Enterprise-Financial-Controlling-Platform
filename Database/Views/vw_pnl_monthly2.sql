CREATE
OR REPLACE VIEW mart.vw_pnl_monthly2 AS
SELECT
    d.calendar_year,
    d.calendar_month,
    d.year_month,
    p.reporting_group,
    p.reporting_category,
    COUNT(*) AS row_count,
    SUM(p.debit_amount) AS debit_amount,
    SUM(p.credit_amount) AS credit_amount,
    SUM(p.signed_amount) AS signed_amount
FROM
    mart.vw_pnl_detail p
    INNER JOIN warehouse.dim_date d ON p.posting_date_key = d.date_key
GROUP BY
    d.calendar_year,
    d.calendar_month,
    d.year_month,
    p.reporting_group,
    p.reporting_category;