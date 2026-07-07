# Data Dictionary

> **Project:** Enterprise Financial Analytics Platform (EFAP)  
> **Document ID:** SD-05  
> **Version:** 1.0  
> **Status:** Draft  
> **Owner:** BI Solution Architect  
> **Last Updated:** July 2026

---

# Navigation

⬅️ Previous: [Data Model](04_Data_Model.md)

➡️ Next: [Business Rules](06_Business_Rules.md)

---

# Document Control

| Field | Value |
|------|-------|
| Document Name | Data Dictionary |
| Document ID | SD-05 |
| Version | 1.0 |
| Status | Draft |
| Owner | BI Solution Architect |
| Classification | Internal |

---

# Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | July 2026 | Ondřej Seidl| Initial version |

---

# 1. Purpose

This document defines the technical and business metadata of the Enterprise Financial Analytics Platform data model.

The Data Dictionary provides:

- standardized column definitions,
- data ownership,
- business meaning,
- transformation expectations,
- data quality requirements.

---

# 2. Data Dictionary Principles

The following rules apply:

| Principle | Description |
|-|-|
| Consistency | Common definitions across reports |
| Traceability | Every attribute has a known origin |
| Governance | Controlled business terminology |
| Transparency | Clear transformation logic |

---

# 3. Fact Tables

# 3.1 Fact_GL

## Description

Stores actual financial transactions from the ERP system.

## Grain

One row represents one financial posting.

| Column Name | Data Type | Nullable | Business Definition | Source System | Transformation Rule |
|-|-|-|-|-|-|
| GL_ID | Integer | No | Unique transaction identifier | ERP | Generated during extraction |
| Date_Key | Integer | No | Transaction date reference | ERP | Converted to YYYYMMDD |
| Company_Key | Integer | No | Company reference | ERP | Lookup to Dim_Company |
| Account_Key | Integer | No | Account reference | ERP | Lookup to Dim_Account |
| CostCenter_Key | Integer | Yes | Cost center reference | ERP | Mapping applied |
| ProfitCenter_Key | Integer | Yes | Profit center reference | ERP | Mapping applied |
| Currency_Key | Integer | No | Currency reference | ERP | Lookup to Dim_Currency |
| Amount | Decimal(18,2) | No | Financial transaction value | ERP | Currency conversion if required |

---

# 3.2 Fact_Budget

## Description

Stores approved budget values.

| Column Name | Data Type | Nullable | Business Definition | Source System | Transformation Rule |
|-|-|-|-|-|-|
| Budget_ID | Integer | No | Budget record identifier | Budget File | Generated during load |
| Date_Key | Integer | No | Budget period | Excel | Converted to date key |
| Company_Key | Integer | No | Company reference | Excel | Mapping applied |
| Account_Key | Integer | No | Account reference | Excel | Mapping applied |
| CostCenter_Key | Integer | Yes | Cost center reference | Excel | Mapping applied |
| Budget_Amount | Decimal(18,2) | No | Planned financial value | Excel | Validation applied |

---

# 3.3 Fact_Forecast

## Description

Stores forecast scenarios.

| Column Name | Data Type | Nullable | Business Definition | Source System | Transformation Rule |
|-|-|-|-|-|-|
| Forecast_ID | Integer | No | Forecast identifier | CSV | Generated during load |
| Date_Key | Integer | No | Forecast period | CSV | Converted to date key |
| Company_Key | Integer | No | Company reference | CSV | Mapping applied |
| Account_Key | Integer | No | Account reference | CSV | Mapping applied |
| CostCenter_Key | Integer | Yes | Cost center reference | CSV | Mapping applied |
| Forecast_Amount | Decimal(18,2) | No | Forecast value | CSV | Validation applied |

---

# 4. Dimension Tables

# 4.1 Dim_Date

| Column Name | Data Type | Nullable | Business Definition |
|-|-|-|-|
| Date_Key | Integer | No | Surrogate date identifier |
| Date | Date | No | Calendar date |
| Year | Integer | No | Calendar year |
| Quarter | String | No | Calendar quarter |
| Month | Integer | No | Calendar month |
| Fiscal_Year | Integer | No | Financial reporting year |
| Fiscal_Period | Integer | No | Financial period |

---

# 4.2 Dim_Account

| Column Name | Data Type | Nullable | Business Definition |
|-|-|-|-|
| Account_Key | Integer | No | Surrogate account identifier |
| Account_Code | String | No | Financial account code |
| Account_Name | String | No | Account description |
| Account_Group | String | Yes | Financial hierarchy group |
| Account_Category | String | Yes | Account classification |

---

# 4.3 Dim_Company

| Column Name | Data Type | Nullable | Business Definition |
|-|-|-|-|
| Company_Key | Integer | No | Company identifier |
| Company_Code | String | No | Legal entity code |
| Company_Name | String | No | Company description |
| Country | String | Yes | Country |
| Region | String | Yes | Geographic region |

---

# 4.4 Dim_CostCenter

| Column Name | Data Type | Nullable | Business Definition |
|-|-|-|-|
| CostCenter_Key | Integer | No | Cost center identifier |
| CostCenter_Code | String | No | Cost center code |
| CostCenter_Name | String | No | Cost center description |
| Department | String | Yes | Department ownership |

---

# 4.5 Dim_ProfitCenter

| Column Name | Data Type | Nullable | Business Definition |
|-|-|-|-|
| ProfitCenter_Key | Integer | No | Profit center identifier |
| ProfitCenter_Code | String | No | Profit center code |
| Business_Unit | String | Yes | Business segment |

---

# 4.6 Dim_Currency

| Column Name | Data Type | Nullable | Business Definition |
|-|-|-|-|
| Currency_Key | Integer | No | Currency identifier |
| Currency_Code | String | No | Currency ISO code |
| Currency_Name | String | No | Currency description |
| Exchange_Rate_Type | String | Yes | Conversion method |

---

# 5. Data Type Standards

| Type | Usage |
|-|-|
| Integer | Keys and identifiers |
| Decimal(18,2) | Financial amounts |
| Date | Calendar attributes |
| String | Descriptive attributes |

---

# 6. Naming Standards

Rules:

- Fact tables use prefix `Fact_`
- Dimension tables use prefix `Dim_`
- Keys use suffix `_Key`
- Measures are not stored as columns

Examples:

- Fact_GL
- Dim_Date
- Account_Key

---

# 7. Related Documents

- [Source Systems](03_Source_Systems.md)
- [Data Model](04_Data_Model.md)
- [Business Rules](06_Business_Rules.md)
- [ETL Design](08_ETL_Design.md)
- [KPI Catalog](07_KPI_Catalog.md)

Related ADRs:

- [ADR-001 - Layered Architecture](ADR/ADR-001-Layered-Architecture.md)
- [ADR-002 - Star Schema](ADR/ADR-002-Star-Schema.md)

---

# End of Document