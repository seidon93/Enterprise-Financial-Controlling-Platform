-- ============================================================
-- EFAP
-- Seed: fact_budget
-- ============================================================
--
-- Target:
--     warehouse.fact_budget
--
-- Purpose:
--     Generate a realistic 2026 monthly budget from
--     2025 actual General Ledger data.
--
-- Method:
--     2026 Budget = 2025 Actual × 1.05
--
-- Grain:
--     Month
--     Company
--     Account
--     Cost Center
--     Department
--     Currency
--
-- Budget date:
--     First day of each month
--
-- Version:
--     BUDGET_2026
--
-- Scenario:
--     BASE
--
-- Source:
--     warehouse.fact_gl
--
-- ============================================================
-- ============================================================
-- 1. CLEAN PREVIOUS SEED
-- ============================================================
TRUNCATE TABLE warehouse.fact_budget;

-- ============================================================
-- 2. GENERATE 2026 MONTHLY BUDGET
-- ============================================================
INSERT INTO
    warehouse.fact_budget (
        budget_date_key,
        company_key,
        account_key,
        cost_center_key,
        department_key,
        currency_key,
        budget_version,
        scenario,
        budget_amount,
        budget_amount_local,
        source_system,
        created_at,
        batch_id
    )
WITH
    actual_2025_monthly AS (
        -- --------------------------------------------------------
        -- 2025 ACTUAL
        -- Aggregate General Ledger to monthly grain.
        --
        -- signed_amount is calculated as:
        --
        --     debit_amount - credit_amount
        --
        -- because fact_gl does not contain a physical
        -- signed_amount column.
        -- --------------------------------------------------------
        SELECT
            DATE_TRUNC('month', d.full_date)::date AS month_start_date,
            fg.company_key,
            fg.account_key,
            fg.cost_center_key,
            fg.department_key,
            fg.currency_key,
            SUM(
                COALESCE(fg.debit_amount, 0) - COALESCE(fg.credit_amount, 0)
            ) AS actual_amount
        FROM
            warehouse.fact_gl fg
            INNER JOIN warehouse.dim_date d ON d.date_key = fg.posting_date_key
            INNER JOIN warehouse.dim_account da ON da.account_key = fg.account_key
        WHERE
            d.calendar_year = 2025
            -- P&L accounts
            AND da.account_number::integer BETWEEN 500 AND 699
        GROUP BY
            DATE_TRUNC('month', d.full_date)::date,
            fg.company_key,
            fg.account_key,
            fg.cost_center_key,
            fg.department_key,
            fg.currency_key
    ),
    budget_2026 AS (
        -- --------------------------------------------------------
        -- APPLY BUDGET ASSUMPTION
        --
        -- Base budget:
        --     2025 Actual × 1.05
        --
        -- The 2025 month is shifted to the corresponding
        -- month in 2026.
        -- --------------------------------------------------------
        SELECT
            (month_start_date + INTERVAL '1 year')::date AS budget_month_start_date,
            company_key,
            account_key,
            cost_center_key,
            department_key,
            currency_key,
            ROUND(actual_amount * 1.05, 2) AS budget_amount
        FROM
            actual_2025_monthly
    )
SELECT
    d.date_key AS budget_date_key,
    b.company_key,
    b.account_key,
    b.cost_center_key,
    b.department_key,
    b.currency_key,
    'BUDGET_2026' AS budget_version,
    'BASE' AS scenario,
    b.budget_amount AS budget_amount,
    b.budget_amount AS budget_amount_local,
    'EFAP_SEED' AS source_system,
    CURRENT_TIMESTAMP AS created_at,
    'SEED_BUDGET_2026' AS batch_id
FROM
    budget_2026 b
    INNER JOIN warehouse.dim_date d ON d.full_date = b.budget_month_start_date
ORDER BY
    b.budget_month_start_date,
    b.company_key,
    b.account_key,
    b.cost_center_key,
    b.department_key,
    b.currency_key;

-- ============================================================
-- 3. BASIC VALIDATION
-- ============================================================
SELECT
    COUNT(*) AS budget_row_count,
    MIN(budget_date_key) AS min_budget_date_key,
    MAX(budget_date_key) AS max_budget_date_key,
    COUNT(DISTINCT company_key) AS company_count,
    COUNT(DISTINCT account_key) AS account_count,
    COUNT(DISTINCT cost_center_key) AS cost_center_count,
    COUNT(DISTINCT department_key) AS department_count,
    COUNT(DISTINCT currency_key) AS currency_count,
    SUM(budget_amount) AS total_budget_amount,
    SUM(budget_amount_local) AS total_budget_amount_local
FROM
    warehouse.fact_budget;

-- ============================================================
-- 4. VALIDATE MONTHLY BUDGET
-- ============================================================
SELECT
    d.calendar_year,
    d.calendar_month,
    d.month_name,
    COUNT(*) AS budget_row_count,
    SUM(fb.budget_amount) AS budget_amount,
    SUM(fb.budget_amount_local) AS budget_amount_local
FROM
    warehouse.fact_budget fb
    INNER JOIN warehouse.dim_date d ON d.date_key = fb.budget_date_key
GROUP BY
    d.calendar_year,
    d.calendar_month,
    d.month_name
ORDER BY
    d.calendar_year,
    d.calendar_month;

-- ============================================================
-- 5. VALIDATE BUDGET BY ACCOUNT
-- ============================================================
SELECT
    da.account_number,
    da.account_name,
    COUNT(*) AS budget_row_count,
    SUM(fb.budget_amount) AS budget_amount
FROM
    warehouse.fact_budget fb
    INNER JOIN warehouse.dim_account da ON da.account_key = fb.account_key
GROUP BY
    da.account_number,
    da.account_name
ORDER BY
    da.account_number;

-- ============================================================
-- 6. VALIDATE BUDGET BY COMPANY
-- ============================================================
SELECT
    fb.company_key,
    COUNT(*) AS budget_row_count,
    SUM(fb.budget_amount) AS budget_amount
FROM
    warehouse.fact_budget fb
GROUP BY
    fb.company_key
ORDER BY
    fb.company_key;

-- ============================================================
-- 7. VALIDATE BUDGET VERSION / SCENARIO
-- ============================================================
SELECT
    budget_version,
    scenario,
    COUNT(*) AS row_count,
    SUM(budget_amount) AS budget_amount
FROM
    warehouse.fact_budget
GROUP BY
    budget_version,
    scenario
ORDER BY
    budget_version,
    scenario;

-- ============================================================
-- 8. VALIDATE MONTH GRAIN
-- ============================================================
--
-- There should be exactly one budget date per month.
-- budget_date_key should therefore correspond to the
-- first day of each month.
--
-- ============================================================
SELECT
    d.calendar_year,
    d.calendar_month,
    MIN(d.full_date) AS budget_date,
    COUNT(DISTINCT fb.budget_date_key) AS distinct_budget_dates
FROM
    warehouse.fact_budget fb
    INNER JOIN warehouse.dim_date d ON d.date_key = fb.budget_date_key
GROUP BY
    d.calendar_year,
    d.calendar_month
ORDER BY
    d.calendar_year,
    d.calendar_month;

-- ============================================================
-- 9. FINAL TOTAL CHECK
-- ============================================================
SELECT
    budget_version,
    scenario,
    MIN(budget_date_key) AS min_date_key,
    MAX(budget_date_key) AS max_date_key,
    COUNT(*) AS row_count,
    SUM(budget_amount) AS total_budget
FROM
    warehouse.fact_budget
GROUP BY
    budget_version,
    scenario;