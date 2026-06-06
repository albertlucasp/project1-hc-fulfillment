# Data Exploration Sub Report

**Dataset:** [report_Master Data_*]  
**Date Explored:** YYYY-MM-DD  
**Location:** [/home/albert/project/project1-hc-fulfillment/data/raw/master_data/*.csv]

---

## 1. Executive Summary

Grain: One employee record per month

---

## 2. Dataset Overview

| Metric | Value |
|--------|-------|
| **Format(s)** | CSV |
| **File Count** | 12 |
| **Total Size** | 12 MB |
| **Total Records** | 32018 Total |
| **Date Range** | 01/01/25 to 01/12/25 |
| **Schema Version** | [If applicable] |
| **Expected Update Frequency** | Monthly |
| **Partitioned By** | None |
| **Shape** | (2500+,30) |

---

## 3. Data Dictionary

| Column Name | Data Type | Description | Nullable | Cardinality | Notes |
|-------------|-----------|-------------|----------|-------------|-------|
| `employee_id`   | string | Stable synthetic employee identifier. | Yes | Vary (2500+) |
| `employee_name` | string | Generated employee name. | Yes | Vary (2500+) |
| `grade_level`   | string | Job or career grade. | Yes | Vary (2500+) |
| `pay_grade`     | string | Payroll grade from the source extract. | Yes | Vary (2500+) |
| `job_code`      | string | Source-system job code. | Yes | Vary (2500+) |
| `job_title`     | string | Source-system job title. | Yes | Vary (2500+) |
| `position_code` | string | Source-system position code. | Yes | Vary (2500+) |
| `position_title`| string | Position title assigned to the employee. | Yes | Vary (2500+) |
| `area_code`     | string | Broad organizational area code. | Yes | Vary (2500+) |
| `area_name`     | string | Broad organizational area name. | Yes | Vary (2500+) |
| `subarea_code`  | string | More specific organizational area code. | Yes | Vary (2500+) |
| `subarea_name`  | string | More specific organizational area name. | Yes | Vary (2500+) |
| `org_unit_code` | string | Source-system organization unit code. | Yes | Vary (2500+) |
| `org_unit_name` | string | Source-system organization unit name. | Yes | Vary (2500+) |
| `employment_group_code` | string | Employee group code. | Yes | Vary (2500+) |
| `employment_group_name` | string | Employee group label. | Yes | Vary (2500+) |
| `employment_subgroup_code` | string | Employee subgroup code. | Yes | Vary (2500+) |
| `employment_subgroup_name` | string | Employee subgroup label. | Yes | Vary (2500+) |
| `payroll_region_code` | string | Payroll region code. | Yes | Vary (2500+) |
| `payroll_region_name` | string | Payroll region label. | Yes | Vary (2500+) |
| `gender`     | string | Gender value, with optional inconsistent variants. | Yes | Vary (2500+) |
| `birth_date` | string | Date of birth. | Yes | Vary (2500+) |
| `birth_city` | string | City of birth. | Yes | Vary (2500+) |
| `entry_program_code` | string | Recruitment or entry program code. | Yes | Vary (2500+) |
| `entry_program_name` | string | Recruitment or entry program label. | Yes | Vary (2500+) |
| `tax_number`      | string | Tax number. | Yes | Vary (2500+) |
| `marital_status`  | string | Marital status. | Yes | Vary (2500+) |
| `dependent_count` | string | Dependent count. | Yes | Vary (2500+) |
| `company_join_date`| string | First company service date. | Yes | Vary (2500+) |
| `termination_date` | string | Termination date when applicable. | Yes | Vary (2500+) |

---

## 4. Data Quality Findings

### Nulls
- [ ] No nulls detected
- [ ] Nulls found in: [Column names]
  - Impact: [Critical/Warning/Low]
  - Details: [e.g., "12 records missing email (0.04%)"]

### Duplicates
- [ ] No duplicates found
- [ ] Duplicates detected: [Count]
  - Duplicate key(s): [Columns]
  - Impact: [Critical/Warning/Low]
  - Details: [e.g., "245 exact duplicate rows"]

### Data Type Issues
- [ ] All columns match expected types
- [ ] Type mismatches found:
  - Impact: [Critical/Warning/Low]
  - Details: [e.g., "Dates stored as strings instead of timestamps"]

### Format/Consistency Issues
- [ ] Formats are consistent
- [ ] Inconsistencies found:
  - Impact: [Critical/Warning/Low]
  - Details: [e.g., "Date format varies: YYYY-MM-DD vs MM/DD/YYYY"]

### Range/Logic Issues
- [ ] All value ranges are reasonable
- [ ] Anomalies detected:
  - Impact: [Critical/Warning/Low]
  - Details: [e.g., "Age values range 0-150, some records have -1"]

### Cross-File Issues (if multiple files)
- [ ] Schemas match across files
- [ ] Inconsistencies found:
  - Impact: [Critical/Warning/Low]
  - Details: [e.g., "File A has 'user_id', File B has 'userId'"]

---

## 5. Design & Production Plan

### Data Ingestion Strategy
- [ ] **Approach:** Raw → Staging → Warehouse / Raw → Warehouse / Other: [Specify]
- [ ] **Schema Validation:** Great Expectations / dbt tests / Custom / None
- [ ] **Deduplication:** Keep all / Keep first / Investigate with owner
- [ ] **Null Handling:** Reject records / Fill with default / Accept as-is
- [ ] **Data Cleaning:** None needed / Clean in ingestion / Clean in transform layer

### Quality Checks to Implement
- [ ] Not null constraints on: [Columns]
- [ ] Unique/primary key constraints on: [Columns]
- [ ] Value range checks on: [Columns]
- [ ] Foreign key validation on: [Columns]
- [ ] Row count thresholds (alert if outside bounds): [Min-Max]

### Transformation Logic Required
- [ ] Date standardization: [Details]
- [ ] Column renaming: [From → To]
- [ ] Data type casting: [Column: Type]
- [ ] Default values: [Column: Value]
- [ ] Other: [Description]

---

## 6. Blockers & Next Steps

### Blockers (Questions for Data Owner)
- [ ] None
- [ ] Issues to clarify:
  - [ ] Why do we have [X] duplicates? Should we keep them?
  - [ ] What timezone do timestamps represent?
  - [ ] Are [X] null values expected or data quality issues?
  - [ ] What's the expected format for [Column]?
  - [ ] Other: [Question]

### Next Steps
- [ ] [ ] Schedule sync with data owner to discuss findings
- [ ] [ ] Design dbt models / transformation logic
- [ ] [ ] Set up data quality tests (Great Expectations / dbt)
- [ ] [ ] Build ingestion pipeline
- [ ] [ ] Test with sample data
- [ ] [ ] Deploy to production
- [ ] [ ] Monitor and alert on quality issues

### Timeline
- [ ] Exploration complete: [Date]
- [ ] Design review: [Date]
- [ ] Pipeline ready: [Date]
- [ ] Production deployment: [Date]

---

## 7. Sign-Off

- [ ] Findings approved by data owner: [Name/Date]
- [ ] Design approved by engineering team: [Name/Date]
- [ ] Ready to build: Yes / No / Pending clarification

---

## Appendix: Raw Exploration Commands

*Optional: Include the code/commands you ran for reproducibility*

```python
# Example: Commands used to explore
df = pd.concat([pd.read_csv(f) for f in source_path.glob('*.csv')])
print(df.info())
print(df.isnull().sum())
print(f"Duplicates: {df.duplicated().sum()}")
```