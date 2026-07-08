# Logical Data Model

**Project:** Enterprise Financial Analytics Platform (EFAP)

**Document Version:** 1.0

**Status:** Draft

**Sprint:** Sprint 2 – Enterprise Data Foundation

---

# Purpose

The Logical Data Model defines the core business entities, their relationships, and the analytical structure of the Enterprise Financial Controlling Solution.

It acts as the blueprint for the physical database model, ETL processes, and the Power BI semantic model.

---

# Design Principles

The data model follows the Kimball dimensional modeling methodology.

Core principles:

- Star Schema architecture
- Conformed dimensions
- Single source of truth
- Business-oriented design
- Scalable architecture
- Read-optimized analytical model

---

# Business Domains

The solution is divided into the following analytical domains.

| Domain | Description |
|----------|------------|
| Finance | General Ledger, Budget, Cash Flow |
| Sales | Revenue and Customers |
| Purchasing | Suppliers and Accounts Payable |
| Inventory | Stock Movements |
| Master Data | Shared dimensions |

---

# Core Dimensions

| Dimension | Description |
|-----------|-------------|
| Dim_Date | Calendar |
| Dim_Company | Legal Entity |
| Dim_Account | Chart of Accounts |
| Dim_CostCenter | Cost Centers |
| Dim_Department | Organizational Structure |
| Dim_Project | Projects |
| Dim_Currency | Reporting Currency |

---

# Business Dimensions

| Dimension | Description |
|-----------|-------------|
| Dim_Customer | Customers |
| Dim_Supplier | Suppliers |
| Dim_Product | Products |

---

# Fact Tables

| Fact Table | Description |
|-------------|------------|
| Fact_GL | General Ledger Transactions |
| Fact_Budget | Budget & Forecast |
| Fact_Sales | Sales Transactions |
| Fact_AR | Accounts Receivable |
| Fact_AP | Accounts Payable |
| Fact_CashFlow | Bank Transactions |
| Fact_Inventory | Inventory Movements |

---

# Grain Definition

| Fact Table | Grain |
|-------------|-------|
| Fact_GL | One journal entry line |
| Fact_Sales | One invoice line |
| Fact_AP | One supplier invoice line |
| Fact_AR | One customer invoice line |
| Fact_Budget | One account × period × cost center × scenario |
| Fact_CashFlow | One bank transaction |
| Fact_Inventory | One inventory movement |

---

# Conformed Dimensions

The following dimensions are shared across multiple business processes.

- Dim_Date
- Dim_Company
- Dim_Account
- Dim_CostCenter
- Dim_Department
- Dim_Project
- Dim_Currency

---

# High-Level Relationships

Every fact table references one or more conformed dimensions.

Example:

Fact_GL

- Date
- Company
- Account
- Cost Center
- Department
- Project
- Currency

Fact_Sales

- Date
- Company
- Customer
- Product
- Cost Center
- Department
- Currency

Fact_AP

- Date
- Company
- Supplier
- Cost Center
- Department
- Currency

---

# Future Extensions

The architecture supports future integration of:

- Human Resources
- Manufacturing
- Fixed Assets
- CRM
- ESG Reporting
- Forecasting
- Consolidation
- Multi-company Reporting

without structural redesign.

---

# Related Documents

- Enterprise Bus Matrix
- Data Dictionary
- Business Rules
- ETL Design
- Star Schema
- ADR-002 Star Schema
- ADR-005 Surrogate Keys