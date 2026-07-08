/*
 ===============================================================================
 Table:        Dim_Date
 Project:      Enterprise Financial Analytics Platform (EFAP)
 Layer:        Semantic Layer
 Object Type:  Dimension
 Version:      1.0.0
 ===============================================================================
 */
CREATE TABLE Dim_Date (
    DateKey INTEGER PRIMARY KEY,
    FullDate DATE NOT NULL,
    Day SMALLINT NOT NULL,
    DayName VARCHAR(20) NOT NULL,
    DayOfWeek SMALLINT NOT NULL,
    ISOWeek SMALLINT NOT NULL,
    Month SMALLINT NOT NULL,
    MonthName VARCHAR(20) NOT NULL,
    Quarter SMALLINT NOT NULL,
    QuarterName VARCHAR(5) NOT NULL,
    Year SMALLINT NOT NULL,
    FiscalMonth SMALLINT NOT NULL,
    FiscalQuarter SMALLINT NOT NULL,
    FiscalYear SMALLINT NOT NULL,
    IsWeekend BOOLEAN NOT NULL,
    IsWorkingDay BOOLEAN NOT NULL,
    IsMonthEnd BOOLEAN NOT NULL,
    IsQuarterEnd BOOLEAN NOT NULL,
    IsYearEnd BOOLEAN NOT NULL,
    CONSTRAINT UQ_Dim_Date_FullDate UNIQUE (FullDate),
    CONSTRAINT CHK_Dim_Date_Month CHECK (
        Month BETWEEN 1 AND 12
    ),
    CONSTRAINT CHK_Dim_Date_Quarter CHECK (
        Quarter BETWEEN 1 AND 4
    ),
    CONSTRAINT CHK_Dim_Date_Day CHECK (
        Day BETWEEN 1 AND 31
    )
);
CREATE INDEX IX_Dim_Date_Year ON Dim_Date (Year);
CREATE INDEX IX_Dim_Date_Month ON Dim_Date (Month);
CREATE INDEX IX_Dim_Date_FiscalYear ON Dim_Date (FiscalYear);
COMMENT ON TABLE Dim_Date IS 'Enterprise calendar dimension used across the EFAP semantic model.';
COMMENT ON COLUMN Dim_Date.DateKey IS 'Primary surrogate key in YYYYMMDD format.';
COMMENT ON COLUMN Dim_Date.FullDate IS 'Calendar date.';
COMMENT ON COLUMN Dim_Date.FiscalYear IS 'Configurable fiscal year.';
CreatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
UpdatedAt TIMESTAMP NULL