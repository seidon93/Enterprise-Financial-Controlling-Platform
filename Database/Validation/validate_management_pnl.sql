-- ============================================================
-- EFAP - Validation: Management P&L
--
-- Object:
--   mart.vw_management_pnl
--
-- Purpose:
--   Validate:
--     1. Monthly grain
--     2. Duplicate months
--     3. NULL values
--     4. EBITDA calculation
--     5. EBIT calculation
--     6. EBT calculation
--     7. Net Profit calculation
--     8. Margin calculations
--     9. Revenue consistency
--    10. Mapping coverage
--    11. Source-to-management reconciliation
--
-- Expected result:
--   Every validation query should return 0 failing rows
--   unless the validation explicitly identifies an expected
--   business/data exception.
-- ============================================================
-- ============================================================
-- 1. BASIC DATA AVAILABILITY
-- ============================================================
SELECT
    COUNT(*) AS row_count,
    MIN(year_month) AS min_year_month,
    MAX(year_month) AS max_year_month
FROM
    mart.vw_management_pnl;

-- ============================================================
-- 2. MONTHLY GRAIN VALIDATION
--
-- Expected:
--   Exactly one row per calendar month.
--
-- Result:
--   0 rows = PASS
-- ============================================================
SELECT
    calendar_year,
    calendar_month,
    year_month,
    COUNT(*) AS row_count
FROM
    mart.vw_management_pnl
GROUP BY
    calendar_year,
    calendar_month,
    year_month
HAVING
    COUNT(*) <> 1
ORDER BY
    calendar_year,
    calendar_month;

-- ============================================================
-- 3. YEAR_MONTH CONSISTENCY
--
-- Example:
--   calendar_year = 2026
--   calendar_month = 8
--   year_month = 2026-08
--
-- Expected:
--   0 rows = PASS
-- ============================================================
SELECT
    calendar_year,
    calendar_month,
    year_month
FROM
    mart.vw_management_pnl
WHERE
    year_month <> TO_CHAR(
        MAKE_DATE(calendar_year, calendar_month, 1),
        'YYYY-MM'
    )
ORDER BY
    calendar_year,
    calendar_month;

-- ============================================================
-- 4. NULL VALIDATION
--
-- Core financial metrics should not be NULL.
--
-- Expected:
--   0 rows = PASS
-- ============================================================
SELECT
    year_month,
    COUNT(*) FILTER (
        WHERE
            revenue IS NULL
    ) AS null_revenue,
    COUNT(*) FILTER (
        WHERE
            other_operating_income IS NULL
    ) AS null_other_operating_income,
    COUNT(*) FILTER (
        WHERE
            operating_costs IS NULL
    ) AS null_operating_costs,
    COUNT(*) FILTER (
        WHERE
            non_core_operating_items IS NULL
    ) AS null_non_core_operating_items,
    COUNT(*) FILTER (
        WHERE
            ebitda_adjustments IS NULL
    ) AS null_ebitda_adjustments,
    COUNT(*) FILTER (
        WHERE
            financial_result IS NULL
    ) AS null_financial_result,
    COUNT(*) FILTER (
        WHERE
            income_tax IS NULL
    ) AS null_income_tax,
    COUNT(*) FILTER (
        WHERE
            ebitda IS NULL
    ) AS null_ebitda,
    COUNT(*) FILTER (
        WHERE
            ebit IS NULL
    ) AS null_ebit,
    COUNT(*) FILTER (
        WHERE
            ebt IS NULL
    ) AS null_ebt,
    COUNT(*) FILTER (
        WHERE
            net_profit IS NULL
    ) AS null_net_profit
FROM
    mart.vw_management_pnl
GROUP BY
    year_month
HAVING
    COUNT(*) FILTER (
        WHERE
            revenue IS NULL
    ) > 0
    OR COUNT(*) FILTER (
        WHERE
            other_operating_income IS NULL
    ) > 0
    OR COUNT(*) FILTER (
        WHERE
            operating_costs IS NULL
    ) > 0
    OR COUNT(*) FILTER (
        WHERE
            non_core_operating_items IS NULL
    ) > 0
    OR COUNT(*) FILTER (
        WHERE
            ebitda_adjustments IS NULL
    ) > 0
    OR COUNT(*) FILTER (
        WHERE
            financial_result IS NULL
    ) > 0
    OR COUNT(*) FILTER (
        WHERE
            income_tax IS NULL
    ) > 0
    OR COUNT(*) FILTER (
        WHERE
            ebitda IS NULL
    ) > 0
    OR COUNT(*) FILTER (
        WHERE
            ebit IS NULL
    ) > 0
    OR COUNT(*) FILTER (
        WHERE
            ebt IS NULL
    ) > 0
    OR COUNT(*) FILTER (
        WHERE
            net_profit IS NULL
    ) > 0
ORDER BY
    year_month;

-- ============================================================
-- 5. EBITDA VALIDATION
--
-- EBITDA =
--   Revenue
-- + Other Operating Income
-- + Operating Costs
-- + Non-Core Operating Items
--
-- Expected:
--   0 rows = PASS
-- ============================================================
SELECT
    year_month,
    revenue,
    other_operating_income,
    operating_costs,
    non_core_operating_items,
    ebitda,
    (
        revenue + other_operating_income + operating_costs + non_core_operating_items
    ) AS calculated_ebitda,
    ebitda - (
        revenue + other_operating_income + operating_costs + non_core_operating_items
    ) AS difference
FROM
    mart.vw_management_pnl
WHERE
    ABS(
        ebitda - (
            revenue + other_operating_income + operating_costs + non_core_operating_items
        )
    ) > 0.01
ORDER BY
    year_month;

-- ============================================================
-- 6. EBIT VALIDATION
--
-- EBIT = EBITDA + EBITDA Adjustments
--
-- Expected:
--   0 rows = PASS
-- ============================================================
SELECT
    year_month,
    ebitda,
    ebitda_adjustments,
    ebit,
    ebitda + ebitda_adjustments AS calculated_ebit,
    ebit - (ebitda + ebitda_adjustments) AS difference
FROM
    mart.vw_management_pnl
WHERE
    ABS(ebit - (ebitda + ebitda_adjustments)) > 0.01
ORDER BY
    year_month;

-- ============================================================
-- 7. EBT VALIDATION
--
-- EBT = EBIT + Financial Result
--
-- Expected:
--   0 rows = PASS
-- ============================================================
SELECT
    year_month,
    ebit,
    financial_result,
    ebt,
    ebit + financial_result AS calculated_ebt,
    ebt - (ebit + financial_result) AS difference
FROM
    mart.vw_management_pnl
WHERE
    ABS(ebt - (ebit + financial_result)) > 0.01
ORDER BY
    year_month;

-- ============================================================
-- 8. NET PROFIT VALIDATION
--
-- Net Profit = EBT + Income Tax
--
-- Expected:
--   0 rows = PASS
-- ============================================================
SELECT
    year_month,
    ebt,
    income_tax,
    net_profit,
    ebt + income_tax AS calculated_net_profit,
    net_profit - (ebt + income_tax) AS difference
FROM
    mart.vw_management_pnl
WHERE
    ABS(net_profit - (ebt + income_tax)) > 0.01
ORDER BY
    year_month;

-- ============================================================
-- 9. EBITDA MARGIN VALIDATION
--
-- EBITDA Margin = EBITDA / Revenue
--
-- Expected:
--   0 rows = PASS
-- ============================================================
SELECT
    year_month,
    revenue,
    ebitda,
    ebitda_margin,
    CASE
        WHEN revenue <> 0 THEN ebitda / revenue
        ELSE NULL
    END AS calculated_margin,
    ebitda_margin - CASE
        WHEN revenue <> 0 THEN ebitda / revenue
        ELSE NULL
    END AS difference
FROM
    mart.vw_management_pnl
WHERE
    (
        revenue <> 0
        AND ABS(ebitda_margin - (ebitda / revenue)) > 0.000001
    )
    OR (
        revenue = 0
        AND ebitda_margin IS NOT NULL
    )
ORDER BY
    year_month;

-- ============================================================
-- 10. EBIT MARGIN VALIDATION
--
-- EBIT Margin = EBIT / Revenue
--
-- Expected:
--   0 rows = PASS
-- ============================================================
SELECT
    year_month,
    revenue,
    ebit,
    ebit_margin,
    CASE
        WHEN revenue <> 0 THEN ebit / revenue
        ELSE NULL
    END AS calculated_margin,
    ebit_margin - CASE
        WHEN revenue <> 0 THEN ebit / revenue
        ELSE NULL
    END AS difference
FROM
    mart.vw_management_pnl
WHERE
    (
        revenue <> 0
        AND ABS(ebit_margin - (ebit / revenue)) > 0.000001
    )
    OR (
        revenue = 0
        AND ebit_margin IS NOT NULL
    )
ORDER BY
    year_month;

-- ============================================================
-- 11. EBT MARGIN VALIDATION
--
-- EBT Margin = EBT / Revenue
--
-- Expected:
--   0 rows = PASS
-- ============================================================
SELECT
    year_month,
    revenue,
    ebt,
    ebt_margin,
    CASE
        WHEN revenue <> 0 THEN ebt / revenue
        ELSE NULL
    END AS calculated_margin,
    ebt_margin - CASE
        WHEN revenue <> 0 THEN ebt / revenue
        ELSE NULL
    END AS difference
FROM
    mart.vw_management_pnl
WHERE
    (
        revenue <> 0
        AND ABS(ebt_margin - (ebt / revenue)) > 0.000001
    )
    OR (
        revenue = 0
        AND ebt_margin IS NOT NULL
    )
ORDER BY
    year_month;

-- ============================================================
-- 12. NET PROFIT MARGIN VALIDATION
--
-- Net Profit Margin = Net Profit / Revenue
--
-- Expected:
--   0 rows = PASS
-- ============================================================
SELECT
    year_month,
    revenue,
    net_profit,
    net_profit_margin,
    CASE
        WHEN revenue <> 0 THEN net_profit / revenue
        ELSE NULL
    END AS calculated_margin,
    net_profit_margin - CASE
        WHEN revenue <> 0 THEN net_profit / revenue
        ELSE NULL
    END AS difference
FROM
    mart.vw_management_pnl
WHERE
    (
        revenue <> 0
        AND ABS(net_profit_margin - (net_profit / revenue)) > 0.000001
    )
    OR (
        revenue = 0
        AND net_profit_margin IS NOT NULL
    )
ORDER BY
    year_month;

-- ============================================================
-- 13. MANAGEMENT P&L LOGICAL CONSISTENCY
--
-- Basic P&L hierarchy:
--
-- EBITDA
--   -> EBIT
--   -> EBT
--   -> Net Profit
--
-- This query identifies unexpected hierarchy breaks.
-- It does NOT assume that each result must be positive.
--
-- Expected:
--   0 rows = PASS
-- ============================================================
SELECT
    year_month,
    ebitda,
    ebitda_adjustments,
    ebit,
    financial_result,
    ebt,
    income_tax,
    net_profit
FROM
    mart.vw_management_pnl
WHERE
    ebit <> ebitda + ebitda_adjustments
    OR ebt <> ebit + financial_result
    OR net_profit <> ebt + income_tax
ORDER BY
    year_month;

-- ============================================================
-- 14. MARGIN RANGE / DATA QUALITY CHECK
--
-- Margins outside +/- 1000% are flagged.
--
-- This is a DATA QUALITY warning, not necessarily an error.
-- Extreme margins can be legitimate when revenue is very low.
--
-- Expected:
--   Ideally 0 rows.
-- ============================================================
SELECT
    year_month,
    revenue,
    ebitda_margin,
    ebit_margin,
    ebt_margin,
    net_profit_margin
FROM
    mart.vw_management_pnl
WHERE
    ABS(ebitda_margin) > 10
    OR ABS(ebit_margin) > 10
    OR ABS(ebt_margin) > 10
    OR ABS(net_profit_margin) > 10
ORDER BY
    year_month;

-- ============================================================
-- 15. REVENUE ZERO CHECK
--
-- Months with zero revenue are important because margins
-- should become NULL instead of causing division errors.
--
-- Expected:
--   Informational result.
-- ============================================================
SELECT
    year_month,
    revenue,
    ebitda,
    ebit,
    ebt,
    net_profit,
    ebitda_margin,
    ebit_margin,
    ebt_margin,
    net_profit_margin
FROM
    mart.vw_management_pnl
WHERE
    revenue = 0
ORDER BY
    year_month;

-- ============================================================
-- 16. MANAGEMENT MAPPING COVERAGE
--
-- Find P&L accounts that exist in vw_pnl_monthly but have
-- no active management mapping.
--
-- This is critical.
--
-- An unmapped account means the Management P&L can silently
-- exclude accounting data.
--
-- Expected:
--   Ideally 0 rows.
-- ============================================================
SELECT
    d.account_number,
    d.account_name,
    COUNT(*) AS source_rows,
    SUM(d.signed_amount) AS signed_amount
FROM
    mart.vw_pnl_monthly d
    LEFT JOIN mart.dim_pnl_management_mapping m ON d.account_number::text = m.account_number::text
    AND m.is_active = TRUE
WHERE
    m.account_number IS NULL
GROUP BY
    d.account_number,
    d.account_name
ORDER BY
    ABS(SUM(d.signed_amount)) DESC;

-- ============================================================
-- 17. MANAGEMENT MAPPING DUPLICATES
--
-- One account should normally have one active management
-- mapping.
--
-- Multiple active mappings can multiply accounting values
-- after the JOIN.
--
-- Expected:
--   0 rows = PASS
-- ============================================================
SELECT
    account_number,
    COUNT(*) AS active_mapping_count
FROM
    mart.dim_pnl_management_mapping
WHERE
    is_active = TRUE
GROUP BY
    account_number
HAVING
    COUNT(*) > 1
ORDER BY
    account_number;

-- ============================================================
-- 18. MANAGEMENT GROUP VALIDATION
--
-- Identify unexpected management groups.
--
-- Expected groups based on vw_management_pnl:
--
-- Revenue
-- Other Operating Income
-- Operating Costs
-- Non-Core Operating Items
-- EBITDA Adjustments
-- Financial Result
-- Tax
--
-- Expected:
--   0 rows = PASS
-- ============================================================
SELECT DISTINCT
    management_group
FROM
    mart.dim_pnl_management_mapping
WHERE
    is_active = TRUE
ORDER BY
    management_group;

-- ============================================================
-- 19. EBITDA INCLUDED FLAG VALIDATION
--
-- Check whether EBITDA Adjustments are correctly excluded
-- from EBITDA.
--
-- This is a mapping-level control.
--
-- Expected:
--   0 rows if the design is:
--     EBITDA Adjustments -> ebitda_included = FALSE
-- ============================================================
SELECT
    management_group,
    management_line,
    ebitda_included,
    COUNT(*) AS mapping_rows
FROM
    mart.dim_pnl_management_mapping
WHERE
    management_group = 'EBITDA Adjustments'
    AND is_active = TRUE
    AND ebitda_included = TRUE
GROUP BY
    management_group,
    management_line,
    ebitda_included
ORDER BY
    management_line;

-- ============================================================
-- 20. SIGN VALIDATION
--
-- Show the management mapping signs.
--
-- This is primarily an audit/debug query.
-- ============================================================
SELECT
    management_group,
    management_line,
    management_sign,
    COUNT(*) AS mapping_rows
FROM
    mart.dim_pnl_management_mapping
WHERE
    is_active = TRUE
GROUP BY
    management_group,
    management_line,
    management_sign
ORDER BY
    management_group,
    management_line,
    management_sign;

-- ============================================================
-- 21. SOURCE-TO-MANAGEMENT RECONCILIATION
--
-- Compare source monthly P&L totals with Management P&L.
--
-- The purpose is to identify whether mapped values are actually
-- flowing into the management layer.
--
-- Expected:
--   Differences should be explainable by:
--     - unmapped accounts
--     - inactive mappings
-- ============================================================
WITH
    source_monthly AS (
        SELECT
            year_month,
            SUM(signed_amount) AS source_signed_amount
        FROM
            mart.vw_pnl_monthly
        GROUP BY
            year_month
    ),
    management_monthly AS (
        SELECT
            year_month,
            (
                revenue + other_operating_income + operating_costs + non_core_operating_items + ebitda_adjustments + financial_result + income_tax
            ) AS management_total
        FROM
            mart.vw_management_pnl
    )
SELECT
    s.year_month,
    s.source_signed_amount,
    m.management_total,
    m.management_total - s.source_signed_amount AS difference
FROM
    source_monthly s
    INNER JOIN management_monthly m ON s.year_month = m.year_month
WHERE
    ABS(m.management_total - s.source_signed_amount) > 0.01
ORDER BY
    s.year_month;

-- ============================================================
-- 22. FINAL VALIDATION SUMMARY
--
-- One compact result showing the main structural checks.
-- ============================================================
WITH
    duplicate_months AS (
        SELECT
            COUNT(*) AS failures
        FROM
            (
                SELECT
                    year_month
                FROM
                    mart.vw_management_pnl
                GROUP BY
                    year_month
                HAVING
                    COUNT(*) <> 1
            ) x
    ),
    invalid_dates AS (
        SELECT
            COUNT(*) AS failures
        FROM
            mart.vw_management_pnl
        WHERE
            year_month <> TO_CHAR(
                MAKE_DATE(calendar_year, calendar_month, 1),
                'YYYY-MM'
            )
    ),
    ebitda_errors AS (
        SELECT
            COUNT(*) AS failures
        FROM
            mart.vw_management_pnl
        WHERE
            ABS(
                ebitda - (
                    revenue + other_operating_income + operating_costs + non_core_operating_items
                )
            ) > 0.01
    ),
    ebit_errors AS (
        SELECT
            COUNT(*) AS failures
        FROM
            mart.vw_management_pnl
        WHERE
            ABS(ebit - (ebitda + ebitda_adjustments)) > 0.01
    ),
    ebt_errors AS (
        SELECT
            COUNT(*) AS failures
        FROM
            mart.vw_management_pnl
        WHERE
            ABS(ebt - (ebit + financial_result)) > 0.01
    ),
    net_profit_errors AS (
        SELECT
            COUNT(*) AS failures
        FROM
            mart.vw_management_pnl
        WHERE
            ABS(net_profit - (ebt + income_tax)) > 0.01
    ),
    unmapped_accounts AS (
        SELECT
            COUNT(*) AS failures
        FROM
            mart.vw_pnl_monthly d
            LEFT JOIN mart.dim_pnl_management_mapping m ON d.account_number::text = m.account_number::text
            AND m.is_active = TRUE
        WHERE
            m.account_number IS NULL
    ),
    duplicate_mappings AS (
        SELECT
            COUNT(*) AS failures
        FROM
            (
                SELECT
                    account_number
                FROM
                    mart.dim_pnl_management_mapping
                WHERE
                    is_active = TRUE
                GROUP BY
                    account_number
                HAVING
                    COUNT(*) > 1
            ) x
    )
SELECT
    'Monthly Grain' AS validation,
    failures,
    CASE
        WHEN failures = 0 THEN 'PASS'
        ELSE 'FAIL'
    END AS status
FROM
    duplicate_months
UNION ALL
SELECT
    'Year-Month Consistency',
    failures,
    CASE
        WHEN failures = 0 THEN 'PASS'
        ELSE 'FAIL'
    END
FROM
    invalid_dates
UNION ALL
SELECT
    'EBITDA Calculation',
    failures,
    CASE
        WHEN failures = 0 THEN 'PASS'
        ELSE 'FAIL'
    END
FROM
    ebitda_errors
UNION ALL
SELECT
    'EBIT Calculation',
    failures,
    CASE
        WHEN failures = 0 THEN 'PASS'
        ELSE 'FAIL'
    END
FROM
    ebit_errors
UNION ALL
SELECT
    'EBT Calculation',
    failures,
    CASE
        WHEN failures = 0 THEN 'PASS'
        ELSE 'FAIL'
    END
FROM
    ebt_errors
UNION ALL
SELECT
    'Net Profit Calculation',
    failures,
    CASE
        WHEN failures = 0 THEN 'PASS'
        ELSE 'FAIL'
    END
FROM
    net_profit_errors
UNION ALL
SELECT
    'Unmapped P&L Accounts',
    failures,
    CASE
        WHEN failures = 0 THEN 'PASS'
        ELSE 'FAIL'
    END
FROM
    unmapped_accounts
UNION ALL
SELECT
    'Duplicate Active Mappings',
    failures,
    CASE
        WHEN failures = 0 THEN 'PASS'
        ELSE 'FAIL'
    END
FROM
    duplicate_mappings
ORDER BY
    validation;