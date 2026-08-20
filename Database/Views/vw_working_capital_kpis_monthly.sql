-- ============================================================
-- EFAP - Working Capital KPIs Monthly
--
-- Object: mart.vw_working_capital_kpis_monthly
-- Layer: Mart / Financial Controlling
-- Grain: One row per calendar month
--
-- KPIs:
--   DSO
--   DIO
--   DPO
--   Cash Conversion Cycle
-- ============================================================
CREATE OR REPLACE VIEW mart.vw_working_capital_monthly AS
WITH
    monthly AS (
        SELECT
            calendar_year,
            calendar_month,
            month_name,
            year_month,
            COALESCE(
                SUM(
                    CASE
                        WHEN management_category = 'Cash' THEN closing_balance
                        ELSE 0
                    END
                ),
                0
            ) AS cash_balance,
            COALESCE(
                SUM(
                    CASE
                        WHEN management_category = 'Inventory' THEN closing_balance
                        ELSE 0
                    END
                ),
                0
            ) AS inventory_balance,
            COALESCE(
                SUM(
                    CASE
                        WHEN management_category = 'Receivables' THEN closing_balance
                        ELSE 0
                    END
                ),
                0
            ) AS receivables_balance,
            COALESCE(
                SUM(
                    CASE
                        WHEN management_category = 'Other Current Assets' THEN closing_balance
                        ELSE 0
                    END
                ),
                0
            ) AS other_current_assets_balance,
            COALESCE(
                SUM(
                    CASE
                        WHEN management_category = 'Current Liabilities' THEN closing_balance
                        ELSE 0
                    END
                ),
                0
            ) AS current_liabilities_balance
        FROM
            mart.vw_balance_sheet_monthly
        GROUP BY
            calendar_year,
            calendar_month,
            month_name,
            year_month
    ),
    calculated AS (
        SELECT
            calendar_year,
            calendar_month,
            month_name,
            year_month,
            cash_balance,
            inventory_balance,
            receivables_balance,
            other_current_assets_balance,
            current_liabilities_balance,
            (
                cash_balance + inventory_balance + receivables_balance + other_current_assets_balance
            ) AS current_assets,
            (
                cash_balance + inventory_balance + receivables_balance + other_current_assets_balance - current_liabilities_balance
            ) AS net_working_capital,
            (
                inventory_balance + receivables_balance + other_current_assets_balance - current_liabilities_balance
            ) AS operating_working_capital
        FROM
            monthly
    ),
    with_changes AS (
        SELECT
            *,
            LAG(net_working_capital) OVER (
                ORDER BY
                    calendar_year,
                    calendar_month
            ) AS previous_net_working_capital
        FROM
            calculated
    )
SELECT
    calendar_year,
    calendar_month,
    month_name,
    year_month,
    cash_balance,
    inventory_balance,
    receivables_balance,
    other_current_assets_balance,
    current_assets,
    current_liabilities_balance,
    net_working_capital,
    operating_working_capital,
    net_working_capital - previous_net_working_capital AS nwc_change,
    CASE
        WHEN current_liabilities_balance <> 0 THEN current_assets / current_liabilities_balance
        ELSE NULL
    END AS current_ratio,
    CASE
        WHEN current_liabilities_balance <> 0 THEN (cash_balance + receivables_balance) / current_liabilities_balance
        ELSE NULL
    END AS quick_ratio,
    CASE
        WHEN current_liabilities_balance <> 0 THEN cash_balance / current_liabilities_balance
        ELSE NULL
    END AS cash_ratio
FROM
    with_changes;