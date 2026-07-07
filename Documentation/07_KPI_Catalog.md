# KPI Catalog

> **Project:** Enterprise Financial Analytics Platform (EFAP)  
> **Document ID:** SD-07  
> **Version:** 1.0  
> **Status:** Draft  
> **Owner:** BI Solution Architect  
> **Last Updated:** July 2026

---

# Navigation

⬅️ Previous: [Business Rules](06_Business_Rules.md)

➡️ Next: [ETL Design](08_ETL_Design.md)

---

# Document Control

| Field | Value |
|------|-------|
| Document Name | KPI Catalog |
| Document ID | SD-07 |
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

This document defines the key performance indicators used within the Enterprise Financial Analytics Platform (EFAP).

The KPI Catalog provides:

- standardized KPI definitions,
- calculation logic,
- source data references,
- Power BI implementation guidance,
- reporting usage.

---

# 2. KPI Governance Principles

The following principles apply:

| Principle | Description |
|-|-|
| Single Definition | One approved KPI definition |
| Business Ownership | KPI meaning is controlled by finance |
| Traceability | KPI can be traced to source data |
| Reusability | KPI is shared across reports |
| Transparency | Calculation logic is documented |

---

# 3. Financial Performance KPIs

---

# 3.1 Revenue

## Definition

Total income generated from business activities.

## Formula

```text
Revenue =
SUM(Fact_GL[Amount])
WHERE Account Category = Revenue
```

## Attributes

| Field | Value |
|-|-|
| KPI Name | Revenue |
| DAX Measure | [Revenue] |
| Source Table | Fact_GL |
| Dimensions | Dim_Date, Dim_Account, Dim_Company |
| Used In | Financial Overview, Management Dashboard |

---

# 3.2 Total Cost

## Definition

Total operating and production costs.

## Formula

```text
Total Cost =
SUM(Fact_GL[Amount])
WHERE Account Category = Cost
```

## Attributes

| Field | Value |
|-|-|
| KPI Name | Total Cost |
| DAX Measure | [Total Cost] |
| Source Table | Fact_GL |

---

# 3.3 Gross Profit

## Definition

Revenue after deduction of direct costs.

## Formula

```text
Gross Profit =
Revenue - Cost of Goods Sold
```

## Attributes

| Field | Value |
|-|-|
| KPI Name | Gross Profit |
| DAX Measure | [Gross Profit] |
| Source Tables | Fact_GL |

---

# 3.4 EBITDA

## Definition

Operating profitability before interest, taxes, depreciation, and amortization.

## Formula

```text
EBITDA =
Gross Profit - Operating Expenses
```

## Attributes

| Field | Value |
|-|-|
| KPI Name | EBITDA |
| DAX Measure | [EBITDA] |
| Source Tables | Fact_GL |

---

# 3.5 Net Result

## Definition

Final financial result after all expenses.

## Formula

```text
Net Result =
Total Income - Total Expenses
```

## Attributes

| Field | Value |
|-|-|
| KPI Name | Net Result |
| DAX Measure | [Net Result] |

---

# 4. Budget Management KPIs

---

# 4.1 Actual Amount

## Definition

Actual financial value posted in the ERP system.

## Formula

```text
Actual Amount =
SUM(Fact_GL[Amount])
```

## DAX Measure

```text
[Actual Amount]
```

---

# 4.2 Budget Amount

## Definition

Approved planned financial value.

## Formula

```text
Budget Amount =
SUM(Fact_Budget[Budget_Amount])
```

## DAX Measure

```text
[Budget Amount]
```

---

# 4.3 Budget Variance

## Definition

Difference between actual performance and approved budget.

## Formula

```text
Budget Variance =
Actual Amount - Budget Amount
```

## DAX Measure

```text
[Budget Variance]
```

---

# 4.4 Budget Variance %

## Definition

Relative deviation from budget.

## Formula

```text
Budget Variance % =
DIVIDE(
Budget Variance,
Budget Amount
)
```

## DAX Measure

```text
[Budget Variance %]
```

---

# 5. Forecast KPIs

---

# 5.1 Forecast Amount

## Definition

Expected future financial value.

## Formula

```text
Forecast Amount =
SUM(Fact_Forecast[Forecast_Amount])
```

## DAX Measure

```text
[Forecast Amount]
```

---

# 5.2 Forecast Accuracy

## Definition

Measures forecast prediction quality.

## Formula

```text
Forecast Accuracy =
1 -
ABS(
Actual Amount - Forecast Amount
)
/
Actual Amount
```

## DAX Measure

```text
[Forecast Accuracy %]
```

---

# 6. Efficiency KPIs

---

# 6.1 EBITDA Margin %

## Definition

Profitability ratio measuring EBITDA against revenue.

## Formula

```text
EBITDA Margin % =
EBITDA / Revenue
```

## DAX Measure

```text
[EBITDA Margin %]
```

---

# 6.2 Cost Ratio %

## Definition

Measures cost level compared to revenue.

## Formula

```text
Cost Ratio % =
Total Cost / Revenue
```

## DAX Measure

```text
[Cost Ratio %]
```

---

# 7. Time Intelligence KPIs

## 7.1 Revenue YTD

## Definition

Year-to-date revenue.

## Formula

```text
Revenue YTD =
Revenue accumulated
from fiscal year start
to selected period
```

## DAX Measure

```text
[Revenue YTD]
```

---

# 7.2 Rolling 12 Months Revenue

## Definition

Revenue calculated over the last twelve months.

## Formula

```text
Rolling 12M Revenue =
Current Month
+
Previous 11 Months
```

## DAX Measure

```text
[Revenue Rolling 12M]
```

---

# 8. KPI Implementation Mapping

| KPI Layer | Implementation |
|-|-|
| Business Definition | Business Rules |
| Metadata | KPI Catalog |
| Calculation | DAX Measures |
| Visualization | Power BI Reports |

---

# 9. Measure Naming Convention

Rules:

- Measures use business names.
- Time calculations use suffixes.
- Percentages use `%`.

Examples:

```
[Revenue]

[Revenue YTD]

[Budget Variance]

[Budget Variance %]

[EBITDA Margin %]
```

---

# 10. Related Documents

- [Business Rules](06_Business_Rules.md)
- [Data Model](04_Data_Model.md)
- [Data Dictionary](05_Data_Dictionary.md)
- [ETL Design](08_ETL_Design.md)
- [Solution Architecture](02_Solution_Architecture.md)

Related ADRs:

- [ADR-001 - Layered Architecture](ADR/ADR-001-Layered-Architecture.md)
- [ADR-002 - Star Schema](ADR/ADR-002-Star-Schema.md)

---

# End of Document