/*
 ===============================================================================
 Enterprise Financial Analytics Platform (EFAP)
 -------------------------------------------------------------------------------
 Object          : Dim_Date
 Object Type     : Table
 Schema          : warehouse
 Version         : 1.0.0
 Status          : Development
 -------------------------------------------------------------------------------
 Description:
 Creates the enterprise calendar dimension used by the semantic model.
 ===============================================================================
 */
DROP TABLE IF EXISTS warehouse.dim_date;
CREATE TABLE warehouse.dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL,
    day SMALLINT NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    day_short_name VARCHAR(5) NOT NULL,
    day_of_week SMALLINT NOT NULL,
    week_of_year SMALLINT NOT NULL,
    calendar_month SMALLINT NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    month_short_name VARCHAR(5) NOT NULL,
    calendar_quarter SMALLINT NOT NULL,
    quarter_name VARCHAR(2) NOT NULL,
    calendar_year INTEGER NOT NULL,
    fiscal_month SMALLINT NOT NULL,
    fiscal_quarter SMALLINT NOT NULL,
    fiscal_year INTEGER NOT NULL,
    year_month VARCHAR(7) NOT NULL,
    year_month_key INTEGER NOT NULL,
    month_start_date DATE NOT NULL,
    month_end_date DATE NOT NULL,
    quarter_start_date DATE NOT NULL,
    quarter_end_date DATE NOT NULL,
    year_start_date DATE NOT NULL,
    year_end_date DATE NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_working_day BOOLEAN NOT NULL,
    is_month_end BOOLEAN NOT NULL,
    is_quarter_end BOOLEAN NOT NULL,
    is_year_end BOOLEAN NOT NULL,
    is_current_date BOOLEAN NOT NULL,
    is_current_month BOOLEAN NOT NULL,
    is_current_quarter BOOLEAN NOT NULL,
    is_current_year BOOLEAN NOT NULL
);