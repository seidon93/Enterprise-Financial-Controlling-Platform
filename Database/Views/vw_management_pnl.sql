-- ============================================================
-- EFAP - Management P&L
--
-- Object: mart.vw_management_pnl
-- Layer: Mart / Management Reporting
-- Grain: One row per calendar month
--
-- Purpose:
--   Management-oriented monthly P&L with:
--     Revenue
--     Other Operating Income
--     Operating Costs
--     Non-Core Operating Items
--     EBITDA Adjustments
--     EBITDA
--     EBIT
--     Financial Result
--     EBT
--     Income Tax
--     Net Profit
--     Margins
--
-- IMPORTANT:
--   signed_amount is calculated in mart.vw_pnl_detail
--   and aggregated in mart.vw_pnl_monthly.
--
--   signed_amount is NOT a column in warehouse.fact_gl.
--
-- Management presentation logic:
--
--   Revenue
--       Credit-normal P&L accounts are presented as positive.
--
--   Other Operating Income
--       Positive contribution.
--
--   Operating Costs
--       Presented as negative contribution.
--
--   Non-Core Operating Items
--       Presented as negative contribution.
--
--   EBITDA Adjustments
--       Presented as negative contribution.
--
--   Financial Result
--       Interest Income / FX Gains      -> positive
--       Interest Expense / FX Losses   -> negative
--       Other Financial Expenses       -> negative
--
--   Tax
--       Presented as negative contribution.
--
-- NOTE:
--   mart.dim_pnl_management_mapping does NOT contain account_name.
--   Account names are available in warehouse.dim_account.
--
-- ============================================================


DROP VIEW IF EXISTS mart.vw_management_pnl;


CREATE OR REPLACE VIEW mart.vw_management_pnl AS


WITH management_detail AS (

    SELECT

        d.calendar_year,
        d.calendar_month,
        d.month_name,
        d.year_month,

        d.account_number,
        d.account_name,

        m.management_group,
        m.management_line,

        m.management_sign,
        m.ebitda_included,
        m.sort_order,

        d.row_count,
        d.debit_amount,
        d.credit_amount,
        d.signed_amount,

        -- ====================================================
        -- MANAGEMENT PRESENTATION AMOUNT
        --
        -- We intentionally do NOT use:
        --
        --     signed_amount * management_sign
        --
        -- because management_sign in the current mapping
        -- is -1 for all P&L accounts.
        --
        -- Instead, management presentation is determined
        -- by the economic role of the management line.
        -- ====================================================

        CASE

            -- ==================================================
            -- REVENUE
            -- ==================================================
            WHEN m.management_group = 'Revenue'
                THEN d.signed_amount * -1


            -- ==================================================
            -- OTHER OPERATING INCOME
            -- ==================================================
            WHEN m.management_group = 'Other Operating Income'
                THEN d.signed_amount * -1


            -- ==================================================
            -- OPERATING COSTS
            -- ==================================================
            WHEN m.management_group = 'Operating Costs'
                THEN d.signed_amount * -1


            -- ==================================================
            -- NON-CORE OPERATING ITEMS
            -- ==================================================
            WHEN m.management_group = 'Non-Core Operating Items'
                THEN d.signed_amount * -1


            -- ==================================================
            -- EBITDA ADJUSTMENTS
            -- Depreciation / Provisions
            -- ==================================================
            WHEN m.management_group = 'EBITDA Adjustments'
                THEN d.signed_amount * -1


            -- ==================================================
            -- FINANCIAL RESULT
            --
            -- Income:
            --   Interest Income
            --   FX Gains
            --
            -- Expenses:
            --   Interest Expense
            --   FX Losses
            --   Other Financial Expenses
            -- ==================================================
            WHEN m.management_group = 'Financial Result'
                 AND m.management_line IN (
                     'Interest Income',
                     'FX Gains'
                 )
                THEN d.signed_amount


            WHEN m.management_group = 'Financial Result'
                 AND m.management_line IN (
                     'Interest Expense',
                     'FX Losses',
                     'Other Financial Expenses'
                 )
                THEN d.signed_amount * -1


            -- ==================================================
            -- TAX
            -- ==================================================
            WHEN m.management_group = 'Tax'
                THEN d.signed_amount * -1


            -- ==================================================
            -- FALLBACK
            -- ==================================================
            ELSE 0

        END AS management_amount


    FROM mart.vw_pnl_monthly d


    INNER JOIN mart.dim_pnl_management_mapping m
        ON d.account_number::text = m.account_number::text


    WHERE m.is_active = TRUE

),


monthly_pnl AS (

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
                WHEN management_group = 'Revenue'
                    THEN management_amount
                ELSE 0
            END
        ) AS revenue,


        -- ====================================================
        -- OTHER OPERATING INCOME
        -- ====================================================

        SUM(
            CASE
                WHEN management_group = 'Other Operating Income'
                    THEN management_amount
                ELSE 0
            END
        ) AS other_operating_income,


        -- ====================================================
        -- OPERATING COSTS
        -- ====================================================

        SUM(
            CASE
                WHEN management_group = 'Operating Costs'
                    THEN management_amount
                ELSE 0
            END
        ) AS operating_costs,


        -- ====================================================
        -- NON-CORE OPERATING ITEMS
        -- ====================================================

        SUM(
            CASE
                WHEN management_group = 'Non-Core Operating Items'
                    THEN management_amount
                ELSE 0
            END
        ) AS non_core_operating_items,


        -- ====================================================
        -- EBITDA ADJUSTMENTS
        -- ====================================================

        SUM(
            CASE
                WHEN management_group = 'EBITDA Adjustments'
                    THEN management_amount
                ELSE 0
            END
        ) AS ebitda_adjustments,


        -- ====================================================
        -- FINANCIAL RESULT
        -- ====================================================

        SUM(
            CASE
                WHEN management_group = 'Financial Result'
                    THEN management_amount
                ELSE 0
            END
        ) AS financial_result,


        -- ====================================================
        -- INCOME TAX
        -- ====================================================

        SUM(
            CASE
                WHEN management_group = 'Tax'
                    THEN management_amount
                ELSE 0
            END
        ) AS income_tax


    FROM management_detail


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


    -- ========================================================
    -- BASE P&L COMPONENTS
    -- ========================================================

    revenue,
    other_operating_income,
    operating_costs,
    non_core_operating_items,
    ebitda_adjustments,
    financial_result,
    income_tax,


    -- ========================================================
    -- EBITDA
    --
    -- Revenue
    -- + Other Operating Income
    -- + Operating Costs
    -- + Non-Core Operating Items
    --
    -- Costs are already negative in management presentation.
    -- ========================================================

    (
        revenue
        + other_operating_income
        + operating_costs
        + non_core_operating_items
    ) AS ebitda,


    -- ========================================================
    -- EBIT
    --
    -- EBITDA
    -- + EBITDA Adjustments
    -- ========================================================

    (
        revenue
        + other_operating_income
        + operating_costs
        + non_core_operating_items
        + ebitda_adjustments
    ) AS ebit,


    -- ========================================================
    -- EBT
    --
    -- EBIT
    -- + Financial Result
    -- ========================================================

    (
        revenue
        + other_operating_income
        + operating_costs
        + non_core_operating_items
        + ebitda_adjustments
        + financial_result
    ) AS ebt,


    -- ========================================================
    -- NET PROFIT
    --
    -- EBT
    -- + Income Tax
    -- ========================================================

    (
        revenue
        + other_operating_income
        + operating_costs
        + non_core_operating_items
        + ebitda_adjustments
        + financial_result
        + income_tax
    ) AS net_profit,


    -- ========================================================
    -- EBITDA MARGIN
    -- ========================================================

    CASE

        WHEN revenue <> 0

        THEN
            (
                revenue
                + other_operating_income
                + operating_costs
                + non_core_operating_items
            ) / revenue

        ELSE NULL

    END AS ebitda_margin,


    -- ========================================================
    -- EBIT MARGIN
    -- ========================================================

    CASE

        WHEN revenue <> 0

        THEN
            (
                revenue
                + other_operating_income
                + operating_costs
                + non_core_operating_items
                + ebitda_adjustments
            ) / revenue

        ELSE NULL

    END AS ebit_margin,


    -- ========================================================
    -- EBT MARGIN
    -- ========================================================

    CASE

        WHEN revenue <> 0

        THEN
            (
                revenue
                + other_operating_income
                + operating_costs
                + non_core_operating_items
                + ebitda_adjustments
                + financial_result
            ) / revenue

        ELSE NULL

    END AS ebt_margin,


    -- ========================================================
    -- NET PROFIT MARGIN
    -- ========================================================

    CASE

        WHEN revenue <> 0

        THEN
            (
                revenue
                + other_operating_income
                + operating_costs
                + non_core_operating_items
                + ebitda_adjustments
                + financial_result
                + income_tax
            ) / revenue

        ELSE NULL

    END AS net_profit_margin


FROM monthly_pnl;