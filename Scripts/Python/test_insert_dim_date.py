from datetime import date

import pandas as pd

from common.database import engine

df = pd.DataFrame(
    [
        {
            "date_key": 20260101,
            "full_date": date(2026, 1, 1),
            "day": 1,
            "day_name": "Thursday",
            "day_short_name": "Thu",
            "day_of_week": 4,
            "week_of_year": 1,
            "calendar_month": 1,
            "month_name": "January",
            "month_short_name": "Jan",
            "calendar_quarter": 1,
            "quarter_name": "Q1",
            "calendar_year": 2026,
            "fiscal_month": 1,
            "fiscal_quarter": 1,
            "fiscal_year": 2026,
            "year_month": "2026-01",
            "year_month_key": 202601,
            "month_start_date": date(2026, 1, 1),
            "month_end_date": date(2026, 1, 31),
            "quarter_start_date": date(2026, 1, 1),
            "quarter_end_date": date(2026, 3, 31),
            "year_start_date": date(2026, 1, 1),
            "year_end_date": date(2026, 12, 31),
            "is_weekend": False,
            "is_working_day": True,
            "is_month_end": False,
            "is_quarter_end": False,
            "is_year_end": False,
            "is_current_date": False,
            "is_current_month": False,
            "is_current_quarter": False,
            "is_current_year": False,
        }
    ]
)
from sqlalchemy import text

with engine.connect() as conn:
    # Delete existing test row (if any) to allow re-runs
    conn.execute(
        text("DELETE FROM warehouse.dim_date WHERE date_key = :dk"),
        {"dk": 20260101},
    )

    df.to_sql(
        name="dim_date",
        schema="warehouse",
        con=conn,
        if_exists="append",
        index=False,
    )

    conn.commit()

print("Test row inserted successfully.")