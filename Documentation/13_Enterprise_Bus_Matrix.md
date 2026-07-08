# Enterprise Bus Matrix

**Project:** Enterprise Financial Controlling Solution

**Version:** 1.0

**Author:** Project Team

**Last Updated:** YYYY-MM-DD

---

# Purpose

The Enterprise Bus Matrix defines the relationship between business processes (fact tables) and shared dimensions (conformed dimensions).

It serves as the foundation of the enterprise dimensional model and ensures consistency across the analytical platform.

---

# Business Processes

| Business Process | Fact Table |
|------------------|------------|
| General Ledger | Fact_GL |
| Sales | Fact_Sales |
| Accounts Receivable | Fact_AR |
| Accounts Payable | Fact_AP |
| Budget & Forecast | Fact_Budget |
| Cash Flow | Fact_CashFlow |
| Inventory | Fact_Inventory |

---

# Enterprise Bus Matrix

| Business Process | Date | Company | Account | Cost Center | Department | Project | Customer | Supplier | Product | Currency |
|------------------|:----:|:-------:|:-------:|:-----------:|:----------:|:-------:|:--------:|:--------:|:-------:|:--------:|
| General Ledger | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | | | | ✔ |
| Sales | ✔ | ✔ | | ✔ | ✔ | ✔ | ✔ | | ✔ | ✔ |
| Accounts Receivable | ✔ | ✔ | | ✔ | ✔ | | ✔ | | | ✔ |
| Accounts Payable | ✔ | ✔ | | ✔ | ✔ | | | ✔ | | ✔ |
| Budget & Forecast | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | | | | ✔ |
| Cash Flow | ✔ | ✔ | ✔ | ✔ | ✔ | | | | | ✔ |
| Inventory | ✔ | ✔ | | ✔ | | | | ✔ | ✔ | ✔ |

---

# Conformed Dimensions

The following dimensions are shared across multiple business processes.

| Dimension | Description |
|-----------|-------------|
| Dim_Date | Calendar dimension |
| Dim_Company | Legal entity |
| Dim_Account | Chart of accounts |
| Dim_CostCenter | Cost center hierarchy |
| Dim_Department | Organizational structure |
| Dim_Project | Projects |
| Dim_Customer | Customers |
| Dim_Supplier | Suppliers |
| Dim_Product | Products |
| Dim_Currency | Reporting currencies |

---

# Design Principles

- One version of each business entity.
- Shared dimensions across all fact tables.
- Surrogate keys for every dimension.
- Star Schema preferred over Snowflake Schema.
- Single-direction relationships.
- Facts contain only measurable events.
- Dimensions contain descriptive attributes.

---

# Future Expansion

The architecture supports future business domains, including:

- Human Resources
- Manufacturing
- Fixed Assets
- Procurement
- CRM
- Planning
- Forecasting
- ESG Reporting

without requiring structural redesign.

---

# Related Documents

- 04_Data_Model.md
- 05_Data_Dictionary.md
- 08_ETL_Design.md
- ADR-002-Star-Schema.md
- ADR-005-Surrogate-Keys.md
