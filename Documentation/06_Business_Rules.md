# Business Rules

> **Project:** Enterprise Financial Analytics Platform (EFAP)  
> **Document ID:** SD-06  
> **Version:** 1.0  
> **Status:** Draft  
> **Owner:** BI Solution Architect  
> **Last Updated:** July 2026

---

# Navigation

⬅️ Previous: [Data Dictionary](05_Data_Dictionary.md)

➡️ Next: [KPI Catalog](07_KPI_Catalog.md)

---

# Document Control

| Field | Value |
|------|-------|
| Document Name | Business Rules |
| Document ID | SD-06 |
| Version | 1.0 |
| Status | Draft |
| Owner | BI Solution Architect |
| Classification | Internal |

---

# Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | July 2026 | Ondřej Seidl | Initial version |

---

# 1. Purpose

This document defines the financial and analytical business rules used within the Enterprise Financial Analytics Platform (EFAP).

The purpose is to ensure that all reports, dashboards, and KPI calculations use consistent business definitions.

The rules defined in this document represent the agreed interpretation of financial measures.

---

# 2. Business Rule Principles

The following principles apply:

| Principle | Description |
|-|-|
| Single Definition | Each metric has one approved definition |
| Transparency | Calculation logic is documented |
| Consistency | Same logic across reports |
| Traceability | Every KPI can be linked to source data |

---

# 3. Financial Statement Rules

## 3.1 Revenue Definition

### Business Definition

Revenue represents income generated from business activities.

### Calculation Logic

```text
Revenue =
SUM(Transaction Amount)
WHERE Account Category = Revenue
```

### Source

- Fact_GL
- Dim_Account

---

# 3.2 Cost Definition

### Business Definition

Cost represents expenses required to operate the business.

### Calculation Logic

```text
Cost =
SUM(Transaction Amount)
WHERE Account Category = Cost
```

### Source

- Fact_GL
- Dim_Account

---

# 3.3 Gross Profit Definition

### Business Definition

Gross Profit represents revenue after deduction of direct costs.

### Calculation

```text
Gross Profit =
Revenue - Cost of Goods Sold
```

---

# 3.4 EBITDA Definition

### Business Definition

EBITDA represents operating profitability before interest, taxes, depreciation, and amortization.

### Calculation

```text
EBITDA =
Gross Profit - Operating Expenses
```

---

# 3.5 Net Result Definition

### Business Definition

Net Result represents the final financial result after all expenses.

### Calculation

```text
Net Result =
Total Income - Total Expenses
```

---

# 4. Budget Analysis Rules

## 4.1 Actual vs Budget

Actual and budget values are compared using the same dimensional structure:

- Company
- Account
- Cost Center
- Time Period

---

## 4.2 Budget Variance

### Definition

Difference between actual financial performance and approved budget.

### Calculation

```text
Budget Variance =
Actual Amount - Budget Amount
```

---

## 4.3 Budget Variance Percentage

### Calculation

```text
Budget Variance % =
(Actual Amount - Budget Amount)
/
Budget Amount
```

### Exception Handling

If Budget Amount equals zero:

```text
Variance % = NULL
```

---

# 5. Forecast Rules

## 5.1 Forecast Version

Forecast data must contain a defined forecast version.

Examples:

- Forecast V1
- Forecast V2
- Rolling Forecast

---

## 5.2 Forecast Accuracy

### Definition

Measures the quality of forecast prediction.

### Calculation

```text
Forecast Accuracy =
1 -
ABS(Actual - Forecast)
/
Actual
```

Interpretation:

| Result | Meaning |
|-|-|
| 100% | Perfect forecast |
| Lower value | Higher deviation |

---

# 6. Time Intelligence Rules

## 6.1 Month-To-Date (MTD)

Definition:

Current month financial value from the first day of the selected month.

---

## 6.2 Year-To-Date (YTD)

Definition:

Accumulated value from the beginning of fiscal year until selected period.

---

## 6.3 Rolling 12 Months

Definition:

Financial value calculated for current period and previous eleven periods.

Example:

```text
July 2026

=
August 2025
to
July 2026
```

---

# 7. Data Classification Rules

Financial accounts are classified using the account hierarchy.

Example:

```text
Account Group

    |
    ▼

Account Category

    |
    ▼

Account
```

Classification controls:

- Revenue
- Cost
- Operating Expense
- Asset
- Liability
- Other

---

# 8. Exception Handling

The following rules apply:

| Situation | Handling |
|-|-|
| Missing account mapping | Record as unmapped |
| Missing cost center | Assign default value |
| Zero denominator | Return NULL |
| Missing forecast | Exclude from accuracy calculation |
| Invalid period | Reject record |

---

# 9. Related Documents

- [Data Model](04_Data_Model.md)
- [Data Dictionary](05_Data_Dictionary.md)
- [KPI Catalog](07_KPI_Catalog.md)
- [ETL Design](08_ETL_Design.md)
- [Solution Architecture](02_Solution_Architecture.md)

Related ADRs:

- [ADR-001 - Layered Architecture](ADR/ADR-001-Layered-Architecture.md)
- [ADR-002 - Star Schema](ADR/ADR-002-Star-Schema.md)

---

# End of Document