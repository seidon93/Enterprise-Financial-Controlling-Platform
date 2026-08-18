-- ============================================================
-- EFAP - Management Plan vs Actual
--
-- Object:
--   mart.vw_pnl_plan_vs_actual
--
-- Layer:
--   Mart / Management Reporting
--
-- Grain:
--   One row per calendar month + management line
--
-- Purpose:
--
--   Management-oriented Plan vs Actual analysis:
--
--     Actual
--     Plan / Budget
--     Variance
--     Variance %
--     Revenue
--     Other Operating Income
--     Operating Costs
--     Non-Core Operating Items
--     EBITDA Adjustments
--     Financial Result
--     Tax
--
--   Derived management KPIs:
--
--     EBITDA Actual
--     EBITDA Plan
--     EBITDA Variance
--
--     EBIT Actual
--     EBIT Plan
--     EBIT Variance
--
--     EBT Actual
--     EBT Plan
--     EBT Variance
--
--     Net Profit Actual
--     Net Profit Plan
--     Net Profit Variance
--
-- Important:
--
--   Source:
--     warehouse.vw_pnl_budget_vs_actual
--
--   Mapping:
--     mart.dim_pnl_management_mapping
--
--   The source view is assumed to provide:
--
--     calendar_year
--     calendar_month
--     month_name
--     year_month
--     company_id
--     cost_center_id
--     department_id
--     account_number
--     actual_amount
--     budget_amount
--     variance_amount
--     status
--
--   Management signs are applied through:
--
--     management_sign
--
--   This ensures that Plan and Actual use the same
--   management presentation logic.
--
-- ============================================================
DROP VIEW IF EXISTS mart.vw_pnl_plan_vs_actual;

CREATE OR REPLACE VIEW mart.vw_pnl_plan_vs_actual AS
-- ============================================================
-- 1. MANAGEMENT DETAIL
--
-- Bring budget/actual data together with management mapping.
-- ============================================================
WITH
    management_detail AS (
        SELECT
            p.calendar_year,
            p.calendar_month,
            TO_CHAR(MAKE_DATE(p.calendar_year, p.calendar_month, 1), 'Month') AS month_name,
            p.year_month,
            p.company_key,
            p.cost_center_key,
            p.department_key,
            p.account_number,
            m.management_group,
            m.management_line,
            m.management_sign,
            m.ebitda_included,
            m.sort_order,
            -- ====================================================
            -- ACTUAL
            -- ====================================================
            COALESCE(p.actual_amount, 0) * m.management_sign AS actual_amount,
            -- ====================================================
            -- PLAN / BUDGET
            -- ====================================================
            COALESCE(p.budget_amount, 0) * m.management_sign AS plan_amount
        FROM
            warehouse.vw_pnl_budget_vs_actual p
            INNER JOIN mart.dim_pnl_management_mapping m ON p.account_number::text = m.account_number::text
        WHERE
            m.is_active = TRUE
    ),
    -- ============================================================
    -- 2. MONTHLY MANAGEMENT P&L
    --
    -- Aggregate accounting-level data into management lines.
    -- ============================================================
    monthly_management AS (
        SELECT
            calendar_year,
            calendar_month,
            month_name,
            year_month,
            -- ====================================================
            -- REVENUE
            -- ====================================================
            SUM(
                CASE
                    WHEN management_group = 'Revenue' THEN actual_amount
                    ELSE 0
                END
            ) AS revenue_actual,
            SUM(
                CASE
                    WHEN management_group = 'Revenue' THEN plan_amount
                    ELSE 0
                END
            ) AS revenue_plan,
            -- ====================================================
            -- OTHER OPERATING INCOME
            -- ====================================================
            SUM(
                CASE
                    WHEN management_group = 'Other Operating Income' THEN actual_amount
                    ELSE 0
                END
            ) AS other_operating_income_actual,
            SUM(
                CASE
                    WHEN management_group = 'Other Operating Income' THEN plan_amount
                    ELSE 0
                END
            ) AS other_operating_income_plan,
            -- ====================================================
            -- OPERATING COSTS
            -- ====================================================
            SUM(
                CASE
                    WHEN management_group = 'Operating Costs' THEN actual_amount
                    ELSE 0
                END
            ) AS operating_costs_actual,
            SUM(
                CASE
                    WHEN management_group = 'Operating Costs' THEN plan_amount
                    ELSE 0
                END
            ) AS operating_costs_plan,
            -- ====================================================
            -- NON-CORE OPERATING ITEMS
            -- ====================================================
            SUM(
                CASE
                    WHEN management_group = 'Non-Core Operating Items' THEN actual_amount
                    ELSE 0
                END
            ) AS non_core_operating_items_actual,
            SUM(
                CASE
                    WHEN management_group = 'Non-Core Operating Items' THEN plan_amount
                    ELSE 0
                END
            ) AS non_core_operating_items_plan,
            -- ====================================================
            -- EBITDA ADJUSTMENTS
            --
            -- Depreciation + Provisions etc.
            -- ====================================================
            SUM(
                CASE
                    WHEN management_group = 'EBITDA Adjustments' THEN actual_amount
                    ELSE 0
                END
            ) AS ebitda_adjustments_actual,
            SUM(
                CASE
                    WHEN management_group = 'EBITDA Adjustments' THEN plan_amount
                    ELSE 0
                END
            ) AS ebitda_adjustments_plan,
            -- ====================================================
            -- FINANCIAL RESULT
            -- ====================================================
            SUM(
                CASE
                    WHEN management_group = 'Financial Result' THEN actual_amount
                    ELSE 0
                END
            ) AS financial_result_actual,
            SUM(
                CASE
                    WHEN management_group = 'Financial Result' THEN plan_amount
                    ELSE 0
                END
            ) AS financial_result_plan,
            -- ====================================================
            -- TAX
            -- ====================================================
            SUM(
                CASE
                    WHEN management_group = 'Tax' THEN actual_amount
                    ELSE 0
                END
            ) AS income_tax_actual,
            SUM(
                CASE
                    WHEN management_group = 'Tax' THEN plan_amount
                    ELSE 0
                END
            ) AS income_tax_plan
        FROM
            management_detail
        GROUP BY
            calendar_year,
            calendar_month,
            month_name,
            year_month
    ),
    -- ============================================================
    -- 3. P&L CALCULATIONS
    --
    -- Calculate Actual and Plan independently.
    -- ============================================================
    pnl_calculated AS (
        SELECT
            calendar_year,
            calendar_month,
            month_name,
            year_month,
            revenue_actual,
            revenue_plan,
            other_operating_income_actual,
            other_operating_income_plan,
            operating_costs_actual,
            operating_costs_plan,
            non_core_operating_items_actual,
            non_core_operating_items_plan,
            ebitda_adjustments_actual,
            ebitda_adjustments_plan,
            financial_result_actual,
            financial_result_plan,
            income_tax_actual,
            income_tax_plan,
            -- ====================================================
            -- EBITDA ACTUAL
            -- ====================================================
            (
                revenue_actual + other_operating_income_actual + operating_costs_actual + non_core_operating_items_actual
            ) AS ebitda_actual,
            -- ====================================================
            -- EBITDA PLAN
            -- ====================================================
            (
                revenue_plan + other_operating_income_plan + operating_costs_plan + non_core_operating_items_plan
            ) AS ebitda_plan,
            -- ====================================================
            -- EBIT ACTUAL
            -- ====================================================
            (
                revenue_actual + other_operating_income_actual + operating_costs_actual + non_core_operating_items_actual + ebitda_adjustments_actual
            ) AS ebit_actual,
            -- ====================================================
            -- EBIT PLAN
            -- ====================================================
            (
                revenue_plan + other_operating_income_plan + operating_costs_plan + non_core_operating_items_plan + ebitda_adjustments_plan
            ) AS ebit_plan,
            -- ====================================================
            -- EBT ACTUAL
            -- ====================================================
            (
                revenue_actual + other_operating_income_actual + operating_costs_actual + non_core_operating_items_actual + ebitda_adjustments_actual + financial_result_actual
            ) AS ebt_actual,
            -- ====================================================
            -- EBT PLAN
            -- ====================================================
            (
                revenue_plan + other_operating_income_plan + operating_costs_plan + non_core_operating_items_plan + ebitda_adjustments_plan + financial_result_plan
            ) AS ebt_plan,
            -- ====================================================
            -- NET PROFIT ACTUAL
            -- ====================================================
            (
                revenue_actual + other_operating_income_actual + operating_costs_actual + non_core_operating_items_actual + ebitda_adjustments_actual + financial_result_actual + income_tax_actual
            ) AS net_profit_actual,
            -- ====================================================
            -- NET PROFIT PLAN
            -- ====================================================
            (
                revenue_plan + other_operating_income_plan + operating_costs_plan + non_core_operating_items_plan + ebitda_adjustments_plan + financial_result_plan + income_tax_plan
            ) AS net_profit_plan
        FROM
            monthly_management
    )
    -- ============================================================
    -- 4. FINAL MANAGEMENT PLAN VS ACTUAL
    -- ============================================================
SELECT
    calendar_year,
    calendar_month,
    month_name,
    year_month,
    -- ========================================================
    -- REVENUE
    -- ========================================================
    revenue_actual,
    revenue_plan,
    revenue_actual - revenue_plan AS revenue_variance,
    CASE
        WHEN revenue_plan <> 0 THEN (revenue_actual - revenue_plan) / ABS(revenue_plan)
        ELSE NULL
    END AS revenue_variance_pct,
    -- ========================================================
    -- OTHER OPERATING INCOME
    -- ========================================================
    other_operating_income_actual,
    other_operating_income_plan,
    other_operating_income_actual - other_operating_income_plan AS other_operating_income_variance,
    CASE
        WHEN other_operating_income_plan <> 0 THEN (
            other_operating_income_actual - other_operating_income_plan
        ) / ABS(other_operating_income_plan)
        ELSE NULL
    END AS other_operating_income_variance_pct,
    -- ========================================================
    -- OPERATING COSTS
    -- ========================================================
    operating_costs_actual,
    operating_costs_plan,
    operating_costs_actual - operating_costs_plan AS operating_costs_variance,
    CASE
        WHEN operating_costs_plan <> 0 THEN (operating_costs_actual - operating_costs_plan) / ABS(operating_costs_plan)
        ELSE NULL
    END AS operating_costs_variance_pct,
    -- ========================================================
    -- NON-CORE OPERATING ITEMS
    -- ========================================================
    non_core_operating_items_actual,
    non_core_operating_items_plan,
    non_core_operating_items_actual - non_core_operating_items_plan AS non_core_operating_items_variance,
    CASE
        WHEN non_core_operating_items_plan <> 0 THEN (
            non_core_operating_items_actual - non_core_operating_items_plan
        ) / ABS(non_core_operating_items_plan)
        ELSE NULL
    END AS non_core_operating_items_variance_pct,
    -- ========================================================
    -- EBITDA ADJUSTMENTS
    -- ========================================================
    ebitda_adjustments_actual,
    ebitda_adjustments_plan,
    ebitda_adjustments_actual - ebitda_adjustments_plan AS ebitda_adjustments_variance,
    CASE
        WHEN ebitda_adjustments_plan <> 0 THEN (
            ebitda_adjustments_actual - ebitda_adjustments_plan
        ) / ABS(ebitda_adjustments_plan)
        ELSE NULL
    END AS ebitda_adjustments_variance_pct,
    -- ========================================================
    -- EBITDA
    -- ========================================================
    ebitda_actual,
    ebitda_plan,
    ebitda_actual - ebitda_plan AS ebitda_variance,
    CASE
        WHEN ebitda_plan <> 0 THEN (ebitda_actual - ebitda_plan) / ABS(ebitda_plan)
        ELSE NULL
    END AS ebitda_variance_pct,
    -- ========================================================
    -- EBIT
    -- ========================================================
    ebit_actual,
    ebit_plan,
    ebit_actual - ebit_plan AS ebit_variance,
    CASE
        WHEN ebit_plan <> 0 THEN (ebit_actual - ebit_plan) / ABS(ebit_plan)
        ELSE NULL
    END AS ebit_variance_pct,
    -- ========================================================
    -- FINANCIAL RESULT
    -- ========================================================
    financial_result_actual,
    financial_result_plan,
    financial_result_actual - financial_result_plan AS financial_result_variance,
    CASE
        WHEN financial_result_plan <> 0 THEN (financial_result_actual - financial_result_plan) / ABS(financial_result_plan)
        ELSE NULL
    END AS financial_result_variance_pct,
    -- ========================================================
    -- EBT
    -- ========================================================
    ebt_actual,
    ebt_plan,
    ebt_actual - ebt_plan AS ebt_variance,
    CASE
        WHEN ebt_plan <> 0 THEN (ebt_actual - ebt_plan) / ABS(ebt_plan)
        ELSE NULL
    END AS ebt_variance_pct,
    -- ========================================================
    -- INCOME TAX
    -- ========================================================
    income_tax_actual,
    income_tax_plan,
    income_tax_actual - income_tax_plan AS income_tax_variance,
    CASE
        WHEN income_tax_plan <> 0 THEN (income_tax_actual - income_tax_plan) / ABS(income_tax_plan)
        ELSE NULL
    END AS income_tax_variance_pct,
    -- ========================================================
    -- NET PROFIT
    -- ========================================================
    net_profit_actual,
    net_profit_plan,
    net_profit_actual - net_profit_plan AS net_profit_variance,
    CASE
        WHEN net_profit_plan <> 0 THEN (net_profit_actual - net_profit_plan) / ABS(net_profit_plan)
        ELSE NULL
    END AS net_profit_variance_pct,
    -- ========================================================
    -- EBITDA MARGIN
    -- ========================================================
    CASE
        WHEN revenue_actual <> 0 THEN ebitda_actual / revenue_actual
        ELSE NULL
    END AS ebitda_margin_actual,
    CASE
        WHEN revenue_plan <> 0 THEN ebitda_plan / revenue_plan
        ELSE NULL
    END AS ebitda_margin_plan,
    CASE
        WHEN revenue_actual <> 0
        AND revenue_plan <> 0 THEN (ebitda_actual / revenue_actual) - (ebitda_plan / revenue_plan)
        ELSE NULL
    END AS ebitda_margin_variance,
    -- ========================================================
    -- EBIT MARGIN
    -- ========================================================
    CASE
        WHEN revenue_actual <> 0 THEN ebit_actual / revenue_actual
        ELSE NULL
    END AS ebit_margin_actual,
    CASE
        WHEN revenue_plan <> 0 THEN ebit_plan / revenue_plan
        ELSE NULL
    END AS ebit_margin_plan,
    CASE
        WHEN revenue_actual <> 0
        AND revenue_plan <> 0 THEN (ebit_actual / revenue_actual) - (ebit_plan / revenue_plan)
        ELSE NULL
    END AS ebit_margin_variance,
    -- ========================================================
    -- EBT MARGIN
    -- ========================================================
    CASE
        WHEN revenue_actual <> 0 THEN ebt_actual / revenue_actual
        ELSE NULL
    END AS ebt_margin_actual,
    CASE
        WHEN revenue_plan <> 0 THEN ebt_plan / revenue_plan
        ELSE NULL
    END AS ebt_margin_plan,
    CASE
        WHEN revenue_actual <> 0
        AND revenue_plan <> 0 THEN (ebt_actual / revenue_actual) - (ebt_plan / revenue_plan)
        ELSE NULL
    END AS ebt_margin_variance,
    -- ========================================================
    -- NET PROFIT MARGIN
    -- ========================================================
    CASE
        WHEN revenue_actual <> 0 THEN net_profit_actual / revenue_actual
        ELSE NULL
    END AS net_profit_margin_actual,
    CASE
        WHEN revenue_plan <> 0 THEN net_profit_plan / revenue_plan
        ELSE NULL
    END AS net_profit_margin_plan,
    CASE
        WHEN revenue_actual <> 0
        AND revenue_plan <> 0 THEN (net_profit_actual / revenue_actual) - (net_profit_plan / revenue_plan)
        ELSE NULL
    END AS net_profit_margin_variance
FROM
    pnl_calculated;