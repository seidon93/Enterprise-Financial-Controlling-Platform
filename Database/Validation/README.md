# Database Validation

## Overview

The **Validation** layer contains SQL scripts used to verify the integrity, consistency, and quality of the Enterprise Financial Analytics Platform (EFAP) data warehouse after each ETL execution.

The validation process ensures that all loaded accounting data satisfies business rules, dimensional integrity, and accounting principles before being consumed by Power BI or downstream analytical processes.

---

## Validation Strategy

The validation process is divided into several logical areas.

| Script | Purpose |
|----------|---------|
| Validation_all.sql | Executes the complete validation process |
| validation_statistics.sql | Dataset statistics and row counts |
| validation_dimensions.sql | Dimension integrity and surrogate key validation |
| validation_documents.sql | Document consistency and duplicate checks |
| validation_balancing.sql | Accounting balance validation (Debit = Credit) |
| Validation.sql | General validation queries |

---

## Validation Categories

### 1. Dimension Validation

Checks that every fact record references existing dimensions.

Examples:

- Company
- Account
- Cost Center
- Department
- Currency
- Customer
- Supplier
- Date

Typical checks:

- Missing surrogate keys
- Invalid foreign key references
- NULL dimension keys

---

### 2. Document Validation

Verifies accounting document consistency.

Examples:

- Duplicate document numbers
- Duplicate document lines
- Missing line numbers
- Invalid document types

---

### 3. Accounting Validation

Verifies accounting correctness.

Examples:

- Debit equals Credit
- Document balancing
- Missing accounting lines
- Invalid account combinations

---

### 4. Statistical Validation

Provides an overview of the loaded warehouse.

Typical metrics include:

- Number of documents
- Number of journal lines
- Number of companies
- Number of customers
- Number of suppliers
- Number of accounting periods
- Number of currencies

---

## Execution Order

Validation scripts should be executed after every ETL load.

Recommended order:

1. validation_statistics.sql
2. validation_dimensions.sql
3. validation_documents.sql
4. validation_balancing.sql
5. Validation_all.sql

---

## Expected Result

A successful validation should produce:

- No missing surrogate keys
- No orphan dimension references
- No duplicate accounting lines
- No unbalanced accounting documents
- No critical validation errors

All validation scripts are expected to return **zero failed records**.

---

## Integration

The validation layer is designed to become part of the automated ETL pipeline.

Future versions will execute the validation process automatically after every batch load and produce a validation summary report.

---

## Enterprise Design Principles

The validation framework follows enterprise data warehouse best practices:

- Data Quality
- Referential Integrity
- Accounting Integrity
- Repeatable Validation
- Transparent ETL Monitoring
- Production Readiness