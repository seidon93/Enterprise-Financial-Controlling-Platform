DROP VIEW IF EXISTS warehouse.vw_profit_loss;

CREATE VIEW warehouse.vw_profit_loss AS
SELECT
    gl.gl_entry_key,
    gl.document_number,
    gl.line_number,
    gl.document_type,
    -- Dates
    gl.posting_date_key,
    d.full_date AS posting_date,
    d.day,
    d.month_name,
    d.month_short_name,
    d.calendar_month,
    d.calendar_quarter,
    d.quarter_name,
    d.calendar_year,
    d.fiscal_month,
    d.fiscal_quarter,
    d.fiscal_year,
    d.year_month,
    d.year_month_key,
    d.month_start_date,
    d.month_end_date,
    d.is_month_end,
    d.is_quarter_end,
    d.is_year_end,
    -- Account
    gl.account_key,
    gl.account_number,
    gl.account_name,
    gl.account_type,
    gl.account_class,
    gl.account_group,
    gl.statement_type,
    gl.reporting_group,
    gl.reporting_category,
    gl.normal_balance,
    -- Organization
    gl.company_key,
    gl.cost_center_key,
    gl.department_key,
    -- Business partners
    gl.customer_key,
    gl.supplier_key,
    gl.asset_key,
    -- Currency
    gl.currency_key,
    -- Amounts
    gl.debit_amount,
    gl.credit_amount,
    gl.amount_local,
    -- Transaction details
    gl.quantity,
    gl.unit_price,
    gl.material_code,
    gl.description,
    -- Technical metadata
    gl.source_system,
    gl.created_at,
    gl.batch_id,
    -- Signed P&L amount
    CASE
        WHEN gl.normal_balance = 'Debit' THEN gl.debit_amount - gl.credit_amount
        WHEN gl.normal_balance = 'Credit' THEN gl.credit_amount - gl.debit_amount
        ELSE gl.debit_amount - gl.credit_amount
    END AS signed_amount
FROM
    warehouse.vw_financial_gl AS gl
    LEFT JOIN warehouse.dim_date AS d ON gl.posting_date_key = d.date_key
WHERE
    gl.statement_type = 'Profit and Loss';

SELECT
    COUNT(*) AS row_count,
    COUNT(posting_date) AS rows_with_date,
    COUNT(signed_amount) AS rows_with_signed_amount
FROM
    warehouse.vw_profit_loss;

SELECT
    reporting_group,
    reporting_category,
    normal_balance,
    COUNT(*) AS row_count,
    SUM(debit_amount) AS total_debit,
    SUM(credit_amount) AS total_credit,
    SUM(signed_amount) AS total_signed
FROM
    warehouse.vw_profit_loss
GROUP BY
    reporting_group,
    reporting_category,
    normal_balance
ORDER BY
    reporting_group,
    reporting_category;