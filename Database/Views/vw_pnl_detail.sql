CREATE OR REPLACE VIEW mart.vw_pnl_detail AS
SELECT
    f.gl_entry_key,
    f.document_number,
    f.line_number,
    f.document_type,
    f.posting_date_key,
    d.full_date,
    d.calendar_year,
    d.calendar_month,
    d.month_name,
    d.year_month,
    d.calendar_quarter,
    d.quarter_name,
    f.company_key,
    f.account_key,
    a.account_number,
    a.account_name,
    a.account_type,
    a.account_class,
    a.account_group,
    a.statement_type,
    a.reporting_group,
    a.reporting_category,
    a.normal_balance,
    f.cost_center_key,
    f.department_key,
    f.customer_key,
    f.supplier_key,
    f.asset_key,
    f.currency_key,
    f.debit_amount,
    f.credit_amount,
    f.amount_local,
    CASE
        WHEN a.normal_balance = 'Debit' THEN f.debit_amount - f.credit_amount
        WHEN a.normal_balance = 'Credit' THEN f.credit_amount - f.debit_amount
        ELSE f.debit_amount - f.credit_amount
    END AS signed_amount,
    f.quantity,
    f.unit_price,
    f.material_code,
    f.description,
    f.source_system,
    f.created_at,
    f.batch_id
FROM
    warehouse.fact_gl f
    LEFT JOIN warehouse.dim_account a ON f.account_key = a.account_key
    LEFT JOIN warehouse.dim_date d ON f.posting_date_key = d.date_key
WHERE
    a.statement_type = 'Profit and Loss';