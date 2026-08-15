CREATE OR REPLACE VIEW mart.vw_management_pnl AS
WITH
    pnl AS (
        SELECT
            calendar_year,
            calendar_month,
            month_name,
            year_month,
            SUM(
                CASE
                    WHEN reporting_group = 'Revenue' THEN signed_amount
                    ELSE 0
                END
            ) AS revenue,
            SUM(
                CASE
                    WHEN reporting_group = 'Operating Costs' THEN signed_amount
                    ELSE 0
                END
            ) AS operating_costs,
            SUM(
                CASE
                    WHEN reporting_group = 'Financial Result' THEN signed_amount
                    ELSE 0
                END
            ) AS financial_result,
            SUM(
                CASE
                    WHEN reporting_group = 'Tax' THEN signed_amount
                    ELSE 0
                END
            ) AS income_tax
        FROM
            mart.vw_pnl_monthly
        GROUP BY
            calendar_year,
            calendar_month,
            month_name,
            year_month
    )
SELECT
    calendar_year,
    calendar_month,
    month_name,
    year_month,
    revenue,
    operating_costs,
    financial_result,
    income_tax,
    -- EBITDA
    revenue - operating_costs AS ebitda,
    -- EBIT
    revenue - operating_costs AS ebit,
    -- EBT
    revenue - operating_costs + financial_result AS ebt,
    -- Net Profit
    revenue - operating_costs + financial_result - income_tax AS net_profit,
    -- EBITDA Margin
    CASE
        WHEN revenue <> 0 THEN (revenue - operating_costs) / revenue
        ELSE NULL
    END AS ebitda_margin,
    -- EBIT Margin
    CASE
        WHEN revenue <> 0 THEN (revenue - operating_costs) / revenue
        ELSE NULL
    END AS ebit_margin,
    -- Net Profit Margin
    CASE
        WHEN revenue <> 0 THEN (
            revenue - operating_costs + financial_result - income_tax
        ) / revenue
        ELSE NULL
    END AS net_profit_margin
FROM
    pnl;