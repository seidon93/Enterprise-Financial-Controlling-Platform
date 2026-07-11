# 18. Enterprise Star Schema

**Project:** Enterprise Financial Analytics Platform (EFAP)

**Document Type:** Data Warehouse Architecture

**Version:** 1.0.0

**Status:** Approved

---

# 1. Purpose

This document describes the Enterprise Star Schema used by the Enterprise Financial Analytics Platform (EFAP).

It defines the relationships between dimension tables and the central General Ledger fact table.

The model follows Kimball dimensional modeling principles and is optimized for analytical reporting in Power BI.

---

# 2. Data Warehouse Architecture

## Layer Overview

Source Data
    │
    ▼
Python ETL
    │
    ▼
PostgreSQL Data Warehouse
    │
    ▼
Power BI Semantic Model
    │
    ▼
Dashboards & KPI

---

# 3. Star Schema

```mermaid
erDiagram

FACT_GL {

BIGINT gl_entry_key

VARCHAR document_number

INTEGER line_number

NUMERIC amount_local

NUMERIC debit_amount

NUMERIC credit_amount

}

DIM_DATE {

INTEGER date_key

DATE full_date

}

DIM_COMPANY {

INTEGER company_key

VARCHAR company_code

}

DIM_ACCOUNT {

INTEGER account_key

VARCHAR account_number

}

DIM_COST_CENTER {

INTEGER cost_center_key

VARCHAR cost_center_code

}

DIM_DEPARTMENT {

INTEGER department_key

VARCHAR department_code

}

DIM_CURRENCY {

INTEGER currency_key

VARCHAR currency_code

}

FACT_GL }o--|| DIM_DATE : PostingDate

FACT_GL }o--|| DIM_DATE : DocumentDate

FACT_GL }o--|| DIM_DATE : DueDate

FACT_GL }o--|| DIM_COMPANY : Company

FACT_GL }o--|| DIM_ACCOUNT : Account

FACT_GL }o--|| DIM_COST_CENTER : CostCenter

FACT_GL }o--|| DIM_DEPARTMENT : Department

FACT_GL }o--|| DIM_CURRENCY : Currency