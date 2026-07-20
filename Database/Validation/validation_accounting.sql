SELECT
    document_number,
    SUM(debit_amount) debit,
    SUM(credit_amount) credit
FROM
    warehouse.fact_gl
GROUP BY
    document_number
HAVING
    SUM(debit_amount) <> SUM(credit_amount);

SELECT
    document_type,
    COUNT(*) rows
FROM
    warehouse.fact_gl
GROUP BY
    document_type;

SELECT
    a.account_number,
    COUNT(*) rows
FROM
    warehouse.fact_gl f
    JOIN warehouse.dim_account a ON f.account_key = a.account_key
GROUP BY
    a.account_number
ORDER BY
    a.account_number;