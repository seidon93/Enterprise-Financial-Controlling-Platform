SELECT
    COUNT(*) AS fact_rows
FROM
    warehouse.fact_gl;

SELECT
    document_type,
    COUNT(*) rows
FROM
    warehouse.fact_gl
GROUP BY
    document_type
ORDER BY
    document_type;

SELECT
    COUNT(DISTINCT document_number) documents
FROM
    warehouse.fact_gl;