CREATE OR REPLACE VIEW mart.vw_pnl_yoy AS

WITH yearly AS (
    SELECT
        calendar_year,
        reporting_group,
        reporting_category,
        account_number,
        account_name,

        debit_amount,
        credit_amount,
        signed_amount

    FROM mart.vw_pnl_yearly
),

with_previous_year AS (
    SELECT
        y.*,

        LAG(y.signed_amount) OVER (
            PARTITION BY
                y.reporting_group,
                y.reporting_category,
                y.account_number,
                y.account_name
            ORDER BY
                y.calendar_year
        ) AS previous_year_signed_amount

    FROM yearly y
)

SELECT
    calendar_year,
    reporting_group,
    reporting_category,
    account_number,
    account_name,

    signed_amount,
    previous_year_signed_amount,

    signed_amount
        - COALESCE(previous_year_signed_amount, 0)
        AS yoy_change,

    CASE
        WHEN previous_year_signed_amount IS NULL
             OR previous_year_signed_amount = 0
        THEN NULL

        ELSE
            (
                signed_amount
                - previous_year_signed_amount
            )
            / ABS(previous_year_signed_amount)
            * 100
    END AS yoy_change_pct

FROM with_previous_year;Sign in to enable AI completions, or disable inline completions in Settings (DBCode > AI).