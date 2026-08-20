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
CREATE OR REPLACE VIEW mart.vw_working_capital_kpis_monthly AS
WITH
    base AS (
        SELECT
            w.calendar_year,
            w.calendar_month,
            w.year_month,
            w.receivables_balance,
            w.inventory_balance,
            w.current_liabilities_balance,
            p.revenue,
            p.operating_costs,
            (
                EXTRACT(
                    DAY
                    FROM
                        d.month_end_date
                )
            )::numeric AS days_in_period
        FROM
            mart.vw_working_capital_monthly w
            LEFT JOIN mart.vw_management_pnl p ON p.calendar_year = w.calendar_year
            AND p.calendar_month = w.calendar_month
            INNER JOIN warehouse.dim_date d ON d.calendar_year = w.calendar_year
            AND d.calendar_month = w.calendar_month
            AND d.day = 1
    ),
    with_lags AS (
        SELECT
            *,
            LAG(receivables_balance) OVER (
                ORDER BY
                    calendar_year,
                    calendar_month
            ) AS previous_receivables_balance,
            LAG(inventory_balance) OVER (
                ORDER BY
                    calendar_year,
                    calendar_month
            ) AS previous_inventory_balance,
            LAG(current_liabilities_balance) OVER (
                ORDER BY
                    calendar_year,
                    calendar_month
            ) AS previous_current_liabilities_balance
        FROM
            base
    ),
    averages AS (
        SELECT
            *,
            CASE
                WHEN previous_receivables_balance IS NULL THEN receivables_balance
                ELSE (
                    previous_receivables_balance + receivables_balance
                ) / 2
            END AS average_receivables,
            CASE
                WHEN previous_inventory_balance IS NULL THEN inventory_balance
                ELSE (previous_inventory_balance + inventory_balance) / 2
            END AS average_inventory,
            CASE
                WHEN previous_current_liabilities_balance IS NULL THEN current_liabilities_balance
                ELSE (
                    previous_current_liabilities_balance + current_liabilities_balance
                ) / 2
            END AS average_current_liabilities
        FROM
            with_lags
    )
SELECT
    calendar_year,
    calendar_month,
    year_month,
    revenue,
    operating_costs,
    receivables_balance,
    inventory_balance,
    current_liabilities_balance,
    average_receivables,
    average_inventory,
    average_current_liabilities,
    days_in_period,
    CASE
        WHEN revenue > 0 THEN average_receivables / revenue * days_in_period
        ELSE NULL
    END AS dso_days,
    CASE
        WHEN ABS(operating_costs) > 0 THEN average_inventory / ABS(operating_costs) * days_in_period
        ELSE NULL
    END AS dio_days,
    CASE
        WHEN ABS(operating_costs) > 0 THEN average_current_liabilities / ABS(operating_costs) * days_in_period
        ELSE NULL
    END AS dpo_days,
    (
        CASE
            WHEN revenue > 0 THEN average_receivables / revenue * days_in_period
            ELSE 0
        END
    ) + (
        CASE
            WHEN ABS(operating_costs) > 0 THEN average_inventory / ABS(operating_costs) * days_in_period
            ELSE 0
        END
    ) - (
        CASE
            WHEN ABS(operating_costs) > 0 THEN average_current_liabilities / ABS(operating_costs) * days_in_period
            ELSE 0
        END
    ) AS cash_conversion_cycle_days
FROM
    averages;