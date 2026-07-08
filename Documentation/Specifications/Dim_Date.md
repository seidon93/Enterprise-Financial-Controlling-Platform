# Dimension Specification – Dim_Date

**Project:** Enterprise Financial Analytics Platform (EFAP)

**Object Type:** Dimension Table

**Table Name:** Dim_Date

**Layer:** Semantic Layer

**Status:** Approved

**Version:** 1.0

---

# Purpose

The Date Dimension provides a standardized calendar for all analytical processes within the Enterprise Financial Controlling Solution.

It supports financial reporting, budgeting, forecasting, operational analysis, and time intelligence calculations in Power BI.

This dimension is shared by all fact tables (Conformed Dimension).

---

# Grain

One record represents one calendar day.

Example:

2026-07-08

---

# Primary Key

| Column | Type |
|----------|------|
| DateKey | Integer (YYYYMMDD) |

Example:

20260708

---

# Business Key

| Column |
|----------|
| FullDate |

---

# Used By

- Fact_GL
- Fact_Sales
- Fact_AP
- Fact_AR
- Fact_Budget
- Fact_CashFlow
- Fact_Inventory

---

# Attributes

| Column | Data Type | Description |
|----------|-----------|-------------|
| DateKey | Integer | Surrogate key (YYYYMMDD) |
| FullDate | Date | Calendar date |
| Day | TinyInt | Day of month |
| DayName | Varchar | Monday, Tuesday... |
| DayOfWeek | TinyInt | ISO day number |
| Week | TinyInt | ISO week |
| Month | TinyInt | Month number |
| MonthName | Varchar | January |
| Quarter | TinyInt | Quarter number |
| QuarterName | Varchar | Q1–Q4 |
| Year | SmallInt | Calendar year |
| FiscalMonth | TinyInt | Fiscal month |
| FiscalQuarter | TinyInt | Fiscal quarter |
| FiscalYear | SmallInt | Fiscal year |
| IsWeekend | Boolean | Weekend flag |
| IsWorkingDay | Boolean | Working day flag |
| IsMonthEnd | Boolean | Last day of month |
| IsQuarterEnd | Boolean | Last day of quarter |
| IsYearEnd | Boolean | Last day of year |

---

# Recommended Future Attributes

- MonthShortName
- QuarterLabel
- MonthYear
- YearMonthKey
- WeekStartDate
- WeekEndDate
- MonthStartDate
- MonthEndDate
- RelativeMonthOffset
- RelativeQuarterOffset
- RelativeYearOffset
- IsCurrentMonth
- IsCurrentYear
- PublicHoliday
- HolidayName

---

# Business Rules

- One row per calendar day.
- No duplicate dates.
- No missing dates.
- Fiscal calendar must be configurable.
- DateKey must always be unique.
- Date range should support historical and future planning.

---

# Data Quality Rules

Validation includes:

- Unique DateKey
- Unique FullDate
- Continuous date sequence
- Valid fiscal periods
- Valid ISO week numbering
- No NULL values in mandatory columns

---

# Refresh Strategy

Refresh frequency:

Annual

The table is regenerated only when additional years are required.

---

# Example Record

| DateKey | FullDate | Day | Month | Quarter | Year | IsWorkingDay |
|----------|----------|-----|--------|----------|------|--------------|
| 20260708 | 2026-07-08 | 8 | 7 | 3 | 2026 | TRUE |

---

# Dependencies

Referenced by:

- All Fact Tables
- Time Intelligence Measures
- Financial Reporting
- Budget Analysis
- Forecasting
- KPI Layer

---

# Future Enhancements

Potential future improvements include:

- Multiple fiscal calendars
- Country-specific public holidays
- Company-specific holidays
- Manufacturing calendars
- 4-4-5 calendar support
- ISO fiscal calendar