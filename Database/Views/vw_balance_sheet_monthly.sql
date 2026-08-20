-- ============================================================
-- EFAP - Balance Sheet Monthly
--
-- Object: mart.vw_balance_sheet_monthly
-- Layer: Mart / Balance Sheet
-- Grain: One row per month and management category
-- ============================================================
CREATE OR REPLACE VIEW mart.vw_balance_sheet_monthly AS
WITH
    classified AS (
        SELECT
            calendar_year,
            calendar_month,
            month_name,
            year_month,
            account_key,
            account_number,
            account_name,
            account_type,
            account_class,
            account_group,
            reporting_group,
            reporting_category,
            normal_balance,
            monthly_signed_amount,
            closing_balance,
            CASE
                WHEN account_type = 'A'
                AND account_group = 0 THEN 'Non-Current Assets'
                WHEN account_type = 'A'
                AND account_group IN (1, 2, 3) THEN 'Current Assets'
                WHEN account_type = 'P'
                AND account_group IN (2, 3) THEN 'Current Liabilities'
                WHEN account_type = 'P'
                AND account_group IN (4, 5)
                AND reporting_category = 'Equity' THEN 'Equity'
                WHEN account_type = 'P' THEN 'Non-Current Liabilities'
                ELSE 'Other Balance Sheet'
            END AS balance_sheet_section,
            CASE
                WHEN account_type = 'A'
                AND account_number::integer IN (211, 221) THEN 'Cash'
                WHEN account_type = 'A'
                AND account_number::integer BETWEEN 100 AND 199  THEN 'Inventory'
                WHEN account_type = 'A'
                AND account_number::integer BETWEEN 300 AND 399  THEN 'Receivables'
                WHEN account_type = 'A'
                AND account_number::integer BETWEEN 200 AND 299  THEN 'Other Current Assets'
                WHEN account_type = 'P'
                AND account_number::integer BETWEEN 200 AND 399  THEN 'Current Liabilities'
                WHEN account_type = 'P'
                AND reporting_category = 'Equity' THEN 'Equity'
                WHEN account_type = 'P' THEN 'Non-Current Liabilities'
                ELSE 'Other Balance Sheet'
            END AS management_category,
            CASE
                WHEN account_type = 'A'
                AND account_number::integer IN (211, 221) THEN 'CASH'
                WHEN account_type = 'A'
                AND account_number::integer BETWEEN 100 AND 199  THEN 'INVENTORY'
                WHEN account_type = 'A'
                AND account_number::integer BETWEEN 300 AND 399  THEN 'RECEIVABLES'
                WHEN account_type = 'A'
                AND account_number::integer BETWEEN 200 AND 299  THEN 'OTHER_CURRENT_ASSETS'
                WHEN account_type = 'P'
                AND account_number::integer BETWEEN 200 AND 399  THEN 'CURRENT_LIABILITY'
                ELSE NULL
            END AS working_capital_class
        FROM
            mart.vw_balance_sheet_detail
    )
SELECT
    calendar_year,
    calendar_month,
    month_name,
    year_month,
    balance_sheet_section,
    management_category,
    working_capital_class,
    COUNT(*) AS account_count,
    SUM(monthly_signed_amount) AS monthly_signed_amount,
    SUM(closing_balance) AS closing_balance
FROM
    classified
GROUP BY
    calendar_year,
    calendar_month,
    month_name,
    year_month,
    balance_sheet_section,
    management_category,
    working_capital_class;