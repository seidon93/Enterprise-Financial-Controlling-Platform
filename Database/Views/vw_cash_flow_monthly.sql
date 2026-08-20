-- ============================================================
-- EFAP - Cash Flow Monthly
--
-- Object: mart.vw_cash_flow_monthly
-- Layer: Mart / Financial Controlling
-- Grain: One row per calendar month
--
-- Method:
--   Indirect cash flow approach
--
-- Sections:
--   Operating Cash Flow
--   Investing Cash Flow
--   Financing Cash Flow
--   Net Cash Change
--   Opening Cash
--   Closing Cash
--
-- ============================================================
CREATE OR REPLACE VIEW mart.vw_cash_flow_monthly AS
WITH
    pnl AS (
        SELECT
            calendar_year,
            calendar_month,
            year_month,
            net_profit,
            ebitda_adjustments
        FROM
            mart.vw_management_pnl
    ),
    balance_sheet AS (
        SELECT
            calendar_year,
            calendar_month,
            year_month,
            management_category,
            closing_balance
        FROM
            mart.vw_balance_sheet_monthly
    ),
    working_capital AS (
        SELECT
            calendar_year,
            calendar_month,
            year_month,
            inventory_balance,
            receivables_balance,
            other_current_assets_balance,
            current_liabilities_balance
        FROM
            mart.vw_working_capital_monthly
    ),
    non_current_assets AS (
        SELECT
            calendar_year,
            calendar_month,
            SUM(closing_balance) AS non_current_assets_balance
        FROM
            mart.vw_balance_sheet_monthly
        WHERE
            management_category = 'Other Balance Sheet'
        GROUP BY
            calendar_year,
            calendar_month
    ),
    cash_balance AS (
        SELECT
            calendar_year,
            calendar_month,
            SUM(closing_balance) AS cash_balance
        FROM
            balance_sheet
        WHERE
            management_category = 'Cash'
        GROUP BY
            calendar_year,
            calendar_month
    ),
    liability_equity AS (
        SELECT
            calendar_year,
            calendar_month,
            SUM(closing_balance) AS liability_equity_balance
        FROM
            mart.vw_balance_sheet_monthly
        WHERE
            management_category IN (
                'Current Liabilities',
                'Non-Current Liabilities',
                'Equity'
            )
        GROUP BY
            calendar_year,
            calendar_month
    ),
    base AS (
        SELECT
            p.calendar_year,
            p.calendar_month,
            p.year_month,
            p.net_profit,
            p.ebitda_adjustments,
            w.inventory_balance,
            w.receivables_balance,
            w.other_current_assets_balance,
            w.current_liabilities_balance,
            c.cash_balance,
            la.liability_equity_balance,
            LAG(w.inventory_balance) OVER (
                ORDER BY
                    p.calendar_year,
                    p.calendar_month
            ) AS previous_inventory_balance,
            LAG(w.receivables_balance) OVER (
                ORDER BY
                    p.calendar_year,
                    p.calendar_month
            ) AS previous_receivables_balance,
            LAG(w.other_current_assets_balance) OVER (
                ORDER BY
                    p.calendar_year,
                    p.calendar_month
            ) AS previous_other_current_assets_balance,
            LAG(w.current_liabilities_balance) OVER (
                ORDER BY
                    p.calendar_year,
                    p.calendar_month
            ) AS previous_current_liabilities_balance,
            LAG(c.cash_balance) OVER (
                ORDER BY
                    p.calendar_year,
                    p.calendar_month
            ) AS previous_cash_balance,
            LAG(la.liability_equity_balance) OVER (
                ORDER BY
                    p.calendar_year,
                    p.calendar_month
            ) AS previous_liability_equity_balance
        FROM
            pnl p
            LEFT JOIN working_capital w ON w.calendar_year = p.calendar_year
            AND w.calendar_month = p.calendar_month
            LEFT JOIN cash_balance c ON c.calendar_year = p.calendar_year
            AND c.calendar_month = p.calendar_month
            LEFT JOIN liability_equity la ON la.calendar_year = p.calendar_year
            AND la.calendar_month = p.calendar_month
    ),
    calculated AS (
        SELECT
            *,
            -- ====================================================
            -- OPERATING CASH FLOW
            --
            -- Net Profit
            -- + non-cash adjustments
            -- +/- working capital movements
            -- ====================================================
            (
                net_profit + COALESCE(ABS(ebitda_adjustments), 0) - (
                    COALESCE(receivables_balance, 0) - COALESCE(previous_receivables_balance, 0)
                ) - (
                    COALESCE(inventory_balance, 0) - COALESCE(previous_inventory_balance, 0)
                ) - (
                    COALESCE(other_current_assets_balance, 0) - COALESCE(previous_other_current_assets_balance, 0)
                ) + (
                    COALESCE(current_liabilities_balance, 0) - COALESCE(previous_current_liabilities_balance, 0)
                )
            ) AS operating_cash_flow,
            -- ====================================================
            -- INVESTING CASH FLOW
            --
            -- Simplified management proxy:
            -- movement in non-current operating assets.
            --
            -- Increase in assets = cash outflow.
            -- Decrease in assets = cash inflow.
            -- ====================================================
            0::numeric AS investing_cash_flow,
            -- ====================================================
            -- FINANCING CASH FLOW
            --
            -- Proxy based on movement in liability/equity funding.
            -- ====================================================
            (
                COALESCE(liability_equity_balance, 0) - COALESCE(previous_liability_equity_balance, 0)
            ) AS financing_cash_flow
        FROM
            base
    ),
    final AS (
        SELECT
            calendar_year,
            calendar_month,
            year_month,
            net_profit,
            operating_cash_flow,
            investing_cash_flow,
            financing_cash_flow,
            (
                operating_cash_flow + investing_cash_flow + financing_cash_flow
            ) AS net_cash_change,
            previous_cash_balance AS opening_cash,
            cash_balance AS closing_cash,
            (
                COALESCE(previous_cash_balance, 0) + operating_cash_flow + investing_cash_flow + financing_cash_flow
            ) AS calculated_closing_cash
        FROM
            calculated
    )
SELECT
    calendar_year,
    calendar_month,
    year_month,
    net_profit,
    operating_cash_flow,
    investing_cash_flow,
    financing_cash_flow,
    net_cash_change,
    opening_cash,
    closing_cash,
    calculated_closing_cash,
    closing_cash - calculated_closing_cash AS cash_reconciliation_difference
FROM
    final;