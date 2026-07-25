TRUNCATE TABLE warehouse.fact_gl,
warehouse.dim_account,
warehouse.dim_asset,
warehouse.dim_company,
warehouse.dim_cost_center,
warehouse.dim_currency,
warehouse.dim_customer,
warehouse.dim_date,
warehouse.dim_department,
warehouse.dim_supplier,
warehouse.etl_batch_history RESTART IDENTITY CASCADE;

SELECT
    'TRUNCATE TABLE ' || string_agg (
        quote_ident (schemaname) || '.' || quote_ident (tablename),
        ', '
    ) || ' RESTART IDENTITY CASCADE;'
FROM
    pg_tables
WHERE
    schemaname = 'warehouse';