-- ============================================================
-- EFAP - Cash Flow YTD
--
-- Object: mart.vw_cash_flow_ytd
-- Layer: Mart / Financial Controlling
-- Grain: One row per calendar year and month
-- ============================================================
CREATE
OR REPLACE VIEW mart.vw_cash_flow_ytd AS
SELECT
    calendar_year,
    calendar_month,
    year_month,
    net_profit,
    operating_cash_flow,
    investing_cash_flow,
    financing_cash_flow,
    net_cash_change,
    SUM(operating_cash_flow) OVER (
        PARTITION BY
            calendar_year
        ORDER BY
            calendar_month ROWS BETWEEN UNBOUNDED PRECEDING
            AND CURRENT ROW
    ) AS operating_cash_flow_ytd,
    SUM(investing_cash_flow) OVER (
        PARTITION BY
            calendar_year
        ORDER BY
            calendar_month ROWS BETWEEN UNBOUNDED PRECEDING
            AND CURRENT ROW
    ) AS investing_cash_flow_ytd,
    SUM(financing_cash_flow) OVER (
        PARTITION BY
            calendar_year
        ORDER BY
            calendar_month ROWS BETWEEN UNBOUNDED PRECEDING
            AND CURRENT ROW
    ) AS financing_cash_flow_ytd,
    SUM(net_cash_change) OVER (
        PARTITION BY
            calendar_year
        ORDER BY
            calendar_month ROWS BETWEEN UNBOUNDED PRECEDING
            AND CURRENT ROW
    ) AS net_cash_change_ytd
FROM
    mart.vw_cash_flow_monthly;