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

# To be continued...