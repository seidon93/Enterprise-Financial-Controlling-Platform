-- ============================================================
-- EFAP - P&L Plan vs Actual KPI Layer
--
-- Object: mart.vw_pnl_plan_vs_actual_kpis_monthly
-- Grain: One row per calendar month
-- ============================================================
CREATE
OR REPLACE VIEW mart.vw_pnl_plan_vs_actual_kpis_monthly AS
WITH
    pnl AS (
        SELECT
            calendar_year,
            calendar_month,
            year_month,
            revenue AS actual_revenue,
            operating_costs AS actual_operating_costs,
            ebitda AS actual_ebitda,
            ebitda_margin AS actual_ebitda_margin,
            net_profit AS actual_net_profit
        FROM
            mart.vw_management_pnl
    ),
    budget AS (
        SELECT
            calendar_year,
            calendar_month,
            year_month,
            SUM(
                CASE
                    WHEN management_group = 'Revenue' THEN management_amount
                    ELSE 0
                END
            ) AS plan_revenue,
            SUM(
                CASE
                    WHEN management_group = 'Operating Costs' THEN management_amount
                    ELSE 0
                END
            ) AS plan_operating_costs,
            SUM(
                CASE
                    WHEN management_group IN (
                        'Revenue',
                        'Other Operating Income',
                        'Operating Costs',
                        'Non-Core Operating Items'
                    ) THEN management_amount
                    ELSE 0
                END
            ) AS plan_ebitda,
            SUM(
                CASE
                    WHEN management_group IN (
                        'Revenue',
                        'Other Operating Income',
                        'Operating Costs',
                        'Non-Core Operating Items'
                    ) THEN management_amount
                    ELSE 0
                END
            ) / NULLIF(
                SUM(
                    CASE
                        WHEN management_group = 'Revenue' THEN management_amount
                        ELSE 0
                    END
                ),
                0
            ) AS plan_ebitda_margin
        FROM
            mart.vw_pnl_management_detail
        GROUP BY
            calendar_year,
            calendar_month,
            year_month
    )
SELECT
    p.calendar_year,
    p.calendar_month,
    p.year_month,
    -- ========================================================
    -- REVENUE
    -- ========================================================
    b.plan_revenue,
    p.actual_revenue,
    p.actual_revenue - b.plan_revenue AS revenue_variance,
    CASE
        WHEN b.plan_revenue <> 0 THEN (p.actual_revenue - b.plan_revenue) / ABS(b.plan_revenue) * 100
        ELSE NULL
    END AS revenue_variance_pct,
    -- ========================================================
    -- OPERATING COSTS
    -- ========================================================
    b.plan_operating_costs,
    p.actual_operating_costs,
    p.actual_operating_costs - b.plan_operating_costs AS cost_variance,
    CASE
        WHEN b.plan_operating_costs <> 0 THEN (p.actual_operating_costs - b.plan_operating_costs) / ABS(b.plan_operating_costs) * 100
        ELSE NULL
    END AS cost_variance_pct,
    -- ========================================================
    -- EBITDA
    -- ========================================================
    b.plan_ebitda,
    p.actual_ebitda,
    p.actual_ebitda - b.plan_ebitda AS ebitda_variance,
    CASE
        WHEN b.plan_ebitda <> 0 THEN (p.actual_ebitda - b.plan_ebitda) / ABS(b.plan_ebitda) * 100
        ELSE NULL
    END AS ebitda_variance_pct,
    -- ========================================================
    -- EBITDA MARGIN
    -- ========================================================
    b.plan_ebitda_margin,
    p.actual_ebitda_margin,
    (p.actual_ebitda_margin - b.plan_ebitda_margin) * 100 AS ebitda_margin_variance_pp,
    -- ========================================================
    -- NET PROFIT
    -- ========================================================
    p.actual_net_profit,
    -- ========================================================
    -- CONTROLLER FLAGS
    -- ========================================================
    CASE
        WHEN p.actual_revenue > b.plan_revenue THEN 'ABOVE_PLAN'
        WHEN p.actual_revenue < b.plan_revenue THEN 'BELOW_PLAN'
        ELSE 'ON_PLAN'
    END AS revenue_status,
    CASE
        WHEN p.actual_operating_costs < b.plan_operating_costs THEN 'FAVORABLE'
        WHEN p.actual_operating_costs > b.plan_operating_costs THEN 'UNFAVORABLE'
        ELSE 'ON_PLAN'
    END AS cost_status,
    CASE
        WHEN p.actual_ebitda > b.plan_ebitda THEN 'ABOVE_PLAN'
        WHEN p.actual_ebitda < b.plan_ebitda THEN 'BELOW_PLAN'
        ELSE 'ON_PLAN'
    END AS ebitda_status
FROM
    pnl p
    LEFT JOIN budget b ON b.calendar_year = p.calendar_year
    AND b.calendar_month = p.calendar_month;