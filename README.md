# End-to-end Synthetic HR Formation Pipeline 

This project creates a confidentiality-safe imitation of an HR formation
fulfillment pipeline. It does not copy real employee, organization, or job
catalogue values. Instead, it preserves the analytical shape of the source
problem:

```text
monthly employee snapshots + wide formation targets
        -> actual headcount vs target formation
        -> fulfillment gap and fulfillment rate
```

## Generate Data

```bash
python3 -m generator.main
```

Generated files:

```text
data/raw/master_data/report_Master Data_01Jan25.csv
data/raw/master_data/report_Master Data_01Feb25.csv
...
data/raw/formation/Formation Main Branch.csv
data/raw/formation/Formation Sub Branch.csv
data/raw/formation/Formation Branch.csv
```

## Generator Technical Flow

```text
generator/config.py
  defines snapshot months, row counts, org names, job titles, event rates

generator/org_structure.py
  builds a clean synthetic hierarchy:
  Main Branch -> Sub Branch -> Branch

generator/generate_master_data.py
  maintains a stable active employee roster across months
  applies monthly events: termination, transfer, promotion, status change
  exports messy source-like monthly CSV snapshots

generator/generate_formation_data.py
  creates wide target formation files by org level

generator/source_messiness.py
  applies controlled inconsistencies at export time only
```

The internal employee records stay clean so the generator remains easy to
reason about. Messiness is added only when writing raw files.

---

## Ingest Raw Data

The ingestion phase loads generated CSV files into SQL Server running in Docker.
It follows two production-style ideas:

- **Source contracts**: [ingestion/source_contracts.py](ingestion/source_contracts.py)
  defines expected files, columns, target tables, and keys.
- **Audit data**: every file load writes metadata to `audit.ingestion_runs`, and
  every contract validation writes rows to `audit.source_contract_checks`.

Start the SQL database:

```bash
cp .env.example .env
docker compose up -d sqlserver
```

Generate raw files if needed:

```bash
uv run python -m generator.main
```

Run ingestion:

```bash
uv run python -m ingestion.main
```

This loads:

```text
raw.master_data
raw.formation_level1
raw.formation_level2
raw.formation_level3
audit.ingestion_runs
audit.source_contract_checks
```

## Validate With DBeaver CE

Create a SQL Server connection in DBeaver CE:

```text
Host: localhost
Port: 1433
Database: hc_fulfillment
Username: sa
Password: value of MSSQL_SA_PASSWORD in .env
Trust server certificate: enabled
```

Useful validation queries:

```sql
select source_name, target_table, source_file_name, row_count, status, finished_at
from audit.ingestion_runs
order by finished_at desc;

select source_name, source_file_name, check_name, status, expected_value, actual_value
from audit.source_contract_checks
order by checked_at desc;

select snapshot_date, count(*) as rows
from raw.master_data
group by snapshot_date
order by snapshot_date;

select count(*) from raw.formation_level1;
select count(*) from raw.formation_level2;
select count(*) from raw.formation_level3;
```

Stop the database:

```bash
docker compose down
```

Remove the database volume only when you want to reset all loaded data:

```bash
docker compose down -v
```

---

# To be continued...
