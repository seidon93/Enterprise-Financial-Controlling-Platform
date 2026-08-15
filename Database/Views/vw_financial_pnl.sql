CREATE OR REPLACE VIEW mart.vw_financial_pnl AS
SELECT
    f.gl_entry_key,
    f.document_number,
    f.line_number,
    f.document_type,
    f.posting_date_key,
    f.document_date_key,
    f.due_date_key,
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
    f.quantity,
    f.unit_price,
    f.material_code,
    f.description,
    f.source_system,
    f.created_at,
    f.batch_id
FROM
    warehouse.fact_gl f
    INNER JOIN warehouse.dim_account a ON f.account_key = a.account_key
WHERE
    a.statement_type = 'Profit and Loss'
    AND a.account_number NOT IN ('697', '698', '701', '702', '710', '799');