# 19. Fact_GL Design

**Project:** Enterprise Financial Analytics Platform (EFAP)

**Document Type:** Fact Table Design

**Version:** 1.0.0

**Status:** Draft

---

# 1. Purpose

Fact_GL (General Ledger Fact) is the central transactional fact table of the Enterprise Financial Analytics Platform.

It stores accounting journal line items and serves as the primary source for financial reporting and controlling.

Typical reports include:

- Profit & Loss Statement
- Balance Sheet
- Trial Balance
- Cash Flow
- Budget vs Actual
- Cost Center Reporting
- Department Reporting
- Management Reporting
- KPI Dashboard

---

# 2. Grain

One record represents one accounting journal line.

Examples:

Document FV202600001

Line 1

311 Customer Receivable

121 000 CZK

---

Document FV202600001

Line 2

604 Sales Revenue

100 000 CZK

---

Document FV202600001

Line 3

343 VAT Output

21 000 CZK

---

# 3. Fact Table Structure

| Column | Type | Description |
|---------|------|-------------|
| gl_entry_key | BIGINT | Surrogate Key |
| document_number | VARCHAR(30) | Accounting document |
| line_number | INTEGER | Document line |
| posting_date_key | INTEGER | FK → Dim_Date |
| company_key | INTEGER | FK → Dim_Company |
| account_key | INTEGER | FK → Dim_Account |
| cost_center_key | INTEGER | FK → Dim_Cost_Center |
| department_key | INTEGER | FK → Dim_Department |
| currency_key | INTEGER | FK → Dim_Currency |
| debit_amount | NUMERIC(18,2) | Debit |
| credit_amount | NUMERIC(18,2) | Credit |
| amount_local | NUMERIC(18,2) | Signed Amount |
| quantity | NUMERIC(18,3) | Quantity |
| description | VARCHAR(255) | Description |
| source_system | VARCHAR(50) | ERP Source |
| created_at | TIMESTAMP | ETL Timestamp |
| batch_id | VARCHAR(50) | ETL Batch |

---

# 4. Dimension Relationships

| Dimension | FK |
|------------|----|
| Dim_Date | posting_date_key |
| Dim_Company | company_key |
| Dim_Account | account_key |
| Dim_Cost_Center | cost_center_key |
| Dim_Department | department_key |
| Dim_Currency | currency_key |

---

# 5. Business Rules

- Every record belongs to exactly one accounting document.
- Every record represents one journal entry.
- Debit and Credit values cannot be negative.
- Signed amount = Debit − Credit.
- Every record must reference valid dimension keys.
- All reporting is based on journal line level.

---

# 6. Measures

The following measures will be created in Power BI.

Financial

- Revenue
- Expenses
- Gross Profit
- EBITDA
- EBIT
- Net Profit

Balance Sheet

- Assets
- Liabilities
- Equity

Management

- Budget vs Actual
- Forecast vs Actual
- Cost Center Variance
- Department Variance

---

# 7. Future Extensions

Planned future enhancements:

- Multi-company consolidation
- Multi-currency reporting
- IFRS Adjustments
- Budget Fact
- Forecast Fact
- Actual vs Budget
- Scenario Planning

---

# 8. Implementation Status

| Component | Status |
|------------|--------|
| Business Design | Completed |
| Star Schema | Completed |
| SQL DDL | Planned |
| Python Generator | Planned |
| PostgreSQL Load | Planned |
| Power BI | Planned |