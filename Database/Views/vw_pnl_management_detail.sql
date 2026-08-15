CREATE OR REPLACE VIEW mart.vw_pnl_management_detail AS
SELECT
    d.posting_date_key,
    d.calendar_year,
    d.calendar_month,
    d.month_name,
    d.year_month,
    d.account_number,
    d.account_name,
    m.management_group,
    m.management_line,
    m.management_sign,
    m.ebitda_included,
    m.sort_order,
    d.row_count,
    d.debit_amount,
    d.credit_amount,
    d.signed_amount,
    d.signed_amount * m.management_sign AS management_amount
FROM
    mart.vw_pnl_monthly d
    INNER JOIN mart.dim_pnl_management_mapping m ON d.account_number::varchar = m.account_number::varchar
WHERE
    m.is_active = true;