# 19. Fact_GL Design

| Metadata | Value |
|----------|-------|
| **Project** | Enterprise Financial Analytics Platform (EFAP) |
| **Document Type** | Fact Table Design |
| **Version** | 1.0.0 |
| **Status** | Approved |
| **Owner** | Project Team |
| **Last Updated** | 2026-07-11 |

---

# 1. Purpose

The **Fact_GL (General Ledger Fact)** table is the central transactional fact table of the Enterprise Financial Analytics Platform (EFAP).

It stores accounting journal line items and serves as the primary source for financial reporting, financial controlling and management analytics.

The table is designed according to Kimball dimensional modeling principles and optimized for analytical workloads in PostgreSQL and Power BI.

---

# 2. Business Purpose

The table supports the following business processes:

- General Ledger
- Financial Accounting
- Financial Controlling
- Management Reporting
- Variance Analysis
- Cost Center Reporting
- Department Reporting
- Multi-period Financial Analysis

---

# 3. Grain

## Grain Definition

**One record represents one accounting journal line item.**

Example:

| Document | Line | Account | Debit | Credit |
|----------|------|---------|-------:|--------:|
| FV202600001 | 1 | 311 | 121000 | 0 |
| FV202600001 | 2 | 604 | 0 | 100000 |
| FV202600001 | 3 | 343 | 0 | 21000 |

This grain allows complete reconstruction of accounting documents while maintaining full analytical flexibility.

---

# 4. Star Schema Relationships

| Dimension | Foreign Key |
|------------|-------------|
| Dim_Date | posting_date_key |
| Dim_Date | document_date_key |
| Dim_Date | due_date_key |
| Dim_Company | company_key |
| Dim_Account | account_key |
| Dim_Cost_Center | cost_center_key |
| Dim_Department | department_key |
| Dim_Currency | currency_key |

---

# 5. Fact Table Structure

## Technical Keys

| Column | Data Type | Description |
|---------|-----------|-------------|
| gl_entry_key | BIGINT | Surrogate Key |
| document_number | VARCHAR(30) | Accounting Document Number |
| line_number | INTEGER | Line Number |

---

## Date Keys

| Column | Data Type | Description |
|---------|-----------|-------------|
| posting_date_key | INTEGER | Posting Date |
| document_date_key | INTEGER | Document Date |
| due_date_key | INTEGER | Due Date |

---

## Dimension Keys

| Column | Data Type | Description |
|---------|-----------|-------------|
| company_key | INTEGER | Company |
| account_key | INTEGER | Account |
| cost_center_key | INTEGER | Cost Center |
| department_key | INTEGER | Department |
| currency_key | INTEGER | Currency |

---

## Business Attributes

| Column | Data Type | Description |
|---------|-----------|-------------|
| document_type | VARCHAR(20) | AR / AP / BANK / GL / PAYROLL / DEPR |
| description | VARCHAR(255) | Journal Line Description |
| source_system | VARCHAR(50) | ERP Source |

---

## Measures

| Column | Data Type |
|---------|-----------|
| debit_amount | NUMERIC(18,2) |
| credit_amount | NUMERIC(18,2) |
| amount_local | NUMERIC(18,2) |
| quantity | NUMERIC(18,3) |

---

## Audit Columns

| Column | Data Type |
|---------|-----------|
| created_at | TIMESTAMP |
| batch_id | VARCHAR(50) |

---

# 6. Business Rules

## Mandatory Rules

- Every journal line belongs to one accounting document.
- Every journal line references valid dimension keys.
- Debit Amount must be greater than or equal to zero.
- Credit Amount must be greater than or equal to zero.
- Amount_Local = Debit Amount − Credit Amount.
- Each accounting document must balance (Σ Debit = Σ Credit).
- Document Number + Line Number must be unique.

---

# 7. Data Quality Rules

| Rule | Description |
|------|-------------|
| FK Validation | All foreign keys must exist |
| Positive Values | Debit and Credit cannot be negative |
| Balance Validation | Every document must balance |
| Duplicate Validation | No duplicate document lines |
| Mandatory Fields | Required columns cannot be NULL |

---

# 8. Expected Data Volume

| Environment | Estimated Rows |
|--------------|---------------:|
| Development | 100,000 |
| Test | 1,000,000 |
| Production | 10,000,000+ |

---

# 9. Power BI Measures

The Fact_GL table will serve as the source for:

## Financial Statements

- Profit & Loss
- Balance Sheet
- Trial Balance
- Cash Flow

## Management Reporting

- Budget vs Actual
- Forecast vs Actual
- Cost Center Analysis
- Department Analysis
- Monthly Closing
- Quarterly Closing
- Year-End Closing

## KPI

- Revenue
- Gross Margin
- EBITDA
- EBIT
- Net Profit
- Operating Margin
- Cost Ratio

---

# 10. Future Enhancements

Planned future extensions include:

- Budget Fact
- Forecast Fact
- Multi-company Consolidation
- Multi-currency Translation
- IFRS Adjustments
- Scenario Planning
- AI Forecasting

---

# 11. References

- 18_Star_Schema.md
- 14_Logical_Data_Model.md
- 02_Solution_Architecture.md
- ADR-001-Star-Schema.md

---

# 12. Revision History

| Version | Date | Description |
|----------|------|-------------|
| 1.0.0 | 2026-07-11 | Initial version |