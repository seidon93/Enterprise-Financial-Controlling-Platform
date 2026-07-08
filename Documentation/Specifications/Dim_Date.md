# Dimension Specification – Dim_Date

> Enterprise Financial Analytics Platform (EFAP)

---

# Document Information

| Property | Value |
|----------|-------|
| **Document ID** | EFAP-DIM-001 |
| **Category** | Data Architecture |
| **Object Type** | Dimension |
| **Layer** | Semantic Layer |
| **Version** | 1.0.0 |
| **Status** | Draft |
| **Owner** | Data Architecture |
| **Sprint** | Sprint 2 – Enterprise Data Foundation |
| **Created** | 2026-07-08 |
| **Last Updated** | 2026-07-08 |

---

# Purpose

The **Dim_Date** dimension provides a centralized enterprise calendar used across all analytical domains within the Enterprise Financial Analytics Platform (EFAP).

It enables consistent time-based reporting, budgeting, forecasting, financial analysis and Power BI Time Intelligence.

Dim_Date is a **Conformed Dimension** and is shared by all fact tables.

---

# Scope

This specification defines:

- Business purpose
- Data model
- Metadata
- Business rules
- Data quality requirements
- Refresh strategy
- Dependencies

---

# Business Context

Every business transaction occurs at a point in time.

A centralized Date Dimension ensures:

- consistent reporting
- reusable calendar logic
- fiscal calendar support
- elimination of duplicated date logic
- optimized Power BI performance

---

# Grain

**One row represents one calendar day.**

Example:

```
2026-07-08
```

---

# Primary Key

| Column | Description |
|---------|-------------|
| DateKey | Integer (YYYYMMDD) |

Example

```
20260708
```

---

# Business Key

| Column |
|---------|
| FullDate |

---

# Used By

- Fact_GL
- Fact_Budget
- Fact_CashFlow
- Fact_Sales
- Fact_AR
- Fact_AP
- Fact_Inventory

---

# Column Metadata

| Business Name | Technical Name | Data Type | Nullable | Source | Transformation | Data Owner | Sensitive |
|---------------|----------------|-----------|----------|--------|----------------|------------|-----------|
| Date Key | DateKey | Integer | No | Generated | YYYYMMDD | Finance | No |
| Calendar Date | FullDate | Date | No | Generated | None | Finance | No |
| Day | Day | TinyInt | No | Generated | Derived | Finance | No |
| Day Name | DayName | Varchar(20) | No | Generated | Derived | Finance | No |
| Day Of Week | DayOfWeek | TinyInt | No | Generated | ISO 8601 | Finance | No |
| ISO Week | ISOWeek | TinyInt | No | Generated | ISO 8601 | Finance | No |
| Month | Month | TinyInt | No | Generated | Derived | Finance | No |
| Month Name | MonthName | Varchar(20) | No | Generated | Derived | Finance | No |
| Quarter | Quarter | TinyInt | No | Generated | Derived | Finance | No |
| Quarter Name | QuarterName | Varchar(5) | No | Generated | Derived | Finance | No |
| Calendar Year | Year | SmallInt | No | Generated | Derived | Finance | No |
| Fiscal Month | FiscalMonth | TinyInt | No | Configurable | Derived | Finance | No |
| Fiscal Quarter | FiscalQuarter | TinyInt | No | Configurable | Derived | Finance | No |
| Fiscal Year | FiscalYear | SmallInt | No | Configurable | Derived | Finance | No |
| Is Weekend | IsWeekend | Boolean | No | Generated | Derived | Finance | No |
| Is Working Day | IsWorkingDay | Boolean | No | Generated | Derived | Finance | No |
| Is Month End | IsMonthEnd | Boolean | No | Generated | Derived | Finance | No |
| Is Quarter End | IsQuarterEnd | Boolean | No | Generated | Derived | Finance | No |
| Is Year End | IsYearEnd | Boolean | No | Generated | Derived | Finance | No |

---

# Business Rules

| Rule ID | Description |
|----------|-------------|
| BR-001 | One record per calendar day |
| BR-002 | No duplicate dates |
| BR-003 | DateKey must be unique |
| BR-004 | Fiscal calendar must be configurable |
| BR-005 | Calendar must contain future planning dates |
| BR-006 | Calendar must not contain gaps |

---

# Data Quality Rules

| Rule ID | Validation |
|----------|------------|
| DQ-001 | DateKey unique |
| DQ-002 | FullDate unique |
| DQ-003 | Continuous calendar |
| DQ-004 | Valid fiscal periods |
| DQ-005 | Valid ISO weeks |
| DQ-006 | No NULL values in mandatory columns |

---

# Refresh Strategy

| Property | Value |
|----------|-------|
| Refresh Frequency | Annual |
| Load Type | Full Refresh |
| Source | Generated |
| Retention | Unlimited |

---

# Dependencies

## Upstream

None

## Downstream

- Fact_GL
- Fact_Budget
- Fact_CashFlow
- Fact_Sales
- Fact_AR
- Fact_AP
- Fact_Inventory
- Power BI Semantic Model
- Time Intelligence Measures

---

# Related Documents

| Document ID | Document | Relationship |
|-------------|----------|--------------|
| EFAP-BUS-001 | 13_Enterprise_Bus_Matrix.md | Defines shared dimensions |
| EFAP-LDM-001 | 14_Logical_Data_Model.md | Defines logical model |
| EFAP-DD-001 | 05_Data_Dictionary.md | Metadata standards |
| EFAP-ADR-002 | ADR-002-Star-Schema.md | Dimensional modeling |
| EFAP-ADR-005 | ADR-005-Surrogate-Keys.md | Key strategy |

---

# Future Enhancements

- Multiple fiscal calendars
- Country-specific public holidays
- Company-specific holidays
- Manufacturing calendars
- 4-4-5 calendar support
- Relative date calculations
- Holiday dimension integration

---

# Revision History

| Version | Date | Author | Changes |
|----------|------|--------|----------|
| 1.0.0 | 2026-07-08 | Project Team | Initial version |