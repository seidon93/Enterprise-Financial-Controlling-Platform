CREATE OR REPLACE VIEW mart.vw_pnl_yoy AS
WITH
    yearly AS (
        SELECT
            calendar_year,
            reporting_group,
            reporting_category,
            account_number,
            account_name,
            debit_amount,
            credit_amount,
            signed_amount
        FROM
            mart.vw_pnl_yearly
    ),
    with_previous_year AS (
        SELECT
            *,
            LAG(signed_amount) OVER (
                PARTITION BY
                    reporting_group,
                    reporting_category,
                    account_number,
                    account_name
                ORDER BY
                    calendar_year
            ) AS previous_year_signed_amount
        FROM
            yearly
    )
SELECT
    calendar_year,
    reporting_group,
    reporting_category,
    account_number,
    account_name,
    signed_amount AS current_year_amount,
    previous_year_signed_amount,
    signed_amount - previous_year_signed_amount AS yoy_change,
    CASE
        WHEN previous_year_signed_amount IS NULL THEN NULL
        WHEN previous_year_signed_amount = 0 THEN NULL
        ELSE (
            (signed_amount - previous_year_signed_amount) / ABS(previous_year_signed_amount)
        ) * 100
    END AS yoy_change_pct
FROM
    with_previous_year;