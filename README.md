# Relational-to-OCEL benchmark databases

Six deterministic SQLite source-system simulations exercise distinct OCEL 2.0
extraction problems:

- `forgeflow` — normalized engineer-to-order OLTP
- `trialversion` — clinical-trial in-table versioning
- `procurechange` — SAP-style change documents
- `claimstream` — event-sourced insurance claims
- `permitflow` — workflow-engine history
- `batteryvault` — bitemporal Data Vault and asset ledger

Each folder contains `source.sqlite`, the source schema and generator,
documentation and glossary, a machine-readable challenge manifest, an OCEL 2.0
SQLite oracle written by PM4Py, a validation report, and four reproducible
case-centric SQL/CSV views. Every CSV is sorted by case ID and then timestamp;
the final source-record key is used only to break ties deterministically.

## Current generation statistics

These values describe the committed artifacts generated with the default 3,000
primary instances. “Event types” means canonical activity types in the OCEL;
“object types” means the declared OCEL object-type catalogue. They are useful
baselines for sizing further scenarios, not requirements that every scenario
must reproduce exactly.

| Scenario | Primary instances | Source rows | Events | Objects | Event types | Object types |
|---|---:|---:|---:|---:|---:|---:|
| ForgeFlow | 3,000 | 140,355 | 97,884 | 59,036 | 48 | 28 |
| TrialVersion | 3,000 | 240,809 | 74,661 | 33,858 | 56 | 19 |
| ProcureChange | 3,000 | 730,158 | 100,504 | 46,353 | 55 | 20 |
| ClaimStream | 3,000 | 115,248 | 99,715 | 40,610 | 58 | 21 |
| PermitFlow | 3,000 | 133,276 | 118,084 | 32,783 | 63 | 17 |
| BatteryVault | 3,000 | 158,791 | 88,346 | 25,779 | 60 | 18 |

The corresponding relation, history, and organizational statistics are:

| Scenario | E2O relations | O2O relations | Object changes | Changed object types | Roles | Least frequent event type |
|---|---:|---:|---:|---:|---:|---:|
| ForgeFlow | 353,436 | 31,200 | 97,884 | 22 | 11 | 300 |
| TrialVersion | 259,871 | 32,664 | 74,661 | 17 | 9 | 100 |
| ProcureChange | 416,109 | 33,000 | 100,504 | 17 | 9 | 81 |
| ClaimStream | 364,017 | 34,258 | 99,715 | 18 | 13 | 87 |
| PermitFlow | 426,586 | 33,703 | 118,084 | 14 | 12 | 51 |
| BatteryVault | 242,634 | 30,599 | 88,346 | 16 | 15 | 76 |

Every primary CSV currently has 100% activity, timestamp, case-ID, provenance,
and object-reference fidelity against its oracle. No transactional object is
shared by unrelated primary cases.

## Hard generation contracts

A further scenario should satisfy the same contracts enforced by
`benchmark.py` and `validate_all.py`:

- Generate at least 2,000 primary instances; use 3,000 by default.
- Generate at least 100,000 source rows, including realistic technical,
  duplicate, correction, retry, or historical records where appropriate.
- Keep the canonical oracle between 25,000 and 200,000 events.
- Emit every declared event type at least 50 times.
- Relate events to every declared object type and always include the semantic
  subject required by the activity rulebook.
- Use coherent stateful traces. Mutually exclusive outcomes must not coexist,
  and retries, reversals, rework, and reopening must occur at their correct
  position in the trace.
- Put at least 20% of primary instances on an explicit exception, loop,
  reversal, or rework path.
- Make at least 15% of events genuinely multi-object.
- Keep transactional object identities case-local. Only explicitly declared
  master or shared object types may reuse identities across primary cases.
- Add meaningful qualified O2O relations with `valid_from`, `valid_to`, and a
  relation state.
- Add temporal object attributes for several object types, not only the
  primary case object.
- Use activity-appropriate attributes. For example, monetary fields belong on
  invoice, payment, fee, reserve, or price activities rather than every event.
- Use role-specific actors and an appropriate human or 24x7 resource calendar.
- Ensure no single source table exposes more than half of the canonical event
  catalogue, and never store canonical activity labels directly in the source.
- Preserve stable source provenance and fuse redundant source evidence into
  exactly one canonical event.
- Produce four case views and make the primary extraction exactly match the
  oracle.
- Sort every CSV by `case_id`, then `timestamp`, then `source_record_id` as the
  deterministic tie-breaker.

The generated `validation_report.json` must have `status: "PASS"`, every entry
under `checks` must be `true`, and `csv_oracle_fidelity_fraction` must be `1.0`.

## How to add a scenario

### 1. Design the domain before the storage pattern

Choose a short lowercase slug, a folder name, a domain title, and a persistence
pattern that is materially different from the existing six. Define:

- a canonical activity catalogue, normally of comparable breadth to the
  current 48–63 event types;
- a useful object catalogue, with one primary case type, one independent
  secondary case type, transactional types, and genuine master/shared types;
- coherent happy paths and conditional exception paths;
- activity-specific subjects and context objects;
- semantic O2O edges and qualifiers;
- domain roles, resource calendars, business attributes, and temporal states;
- the source-system ambiguity that makes extraction non-trivial.

Add a `Scenario` entry to `SCENARIOS` in `benchmark.py`. Its `activities` and
`object_types` tuples are the authoritative catalogues. `evidence_tables` must
list the source tables that can provide business-event evidence; technical
padding tables are not evidence tables.

### 2. Add the semantic rules

Extend all applicable structures in `domain_rules.py`:

- `CASE_TYPES` and `SECONDARY_CASE_TYPES`;
- `SHARED_POOL_SIZES`, containing only real master/shared types;
- `build_route`, with a deterministic route for every primary instance;
- `SUBJECT_KEYWORDS` for activity names that cannot be inferred reliably from
  object-type names;
- `CONTEXT_BY_SUBJECT` for semantically relevant event context;
- `O2O_EDGES` for qualified relationships;
- `ROLE_KEYWORDS` for actor specialization.

Every activity returned by `build_route` must occur in the scenario catalogue.
Design modular cohorts carefully: a nested condition must still yield at least
50 occurrences at 3,000 instances, and an optional branch must not become
unreachable because an earlier terminal branch selects the same cohort.

### 3. Create the operational source schema

Create `<slug>/schema.sql` as a source-system schema, not as a disguised event
log. Use the chosen persistence pattern's native concepts and timestamps:
split dates and times, version intervals, change documents, workflow history,
JSON payloads, journals, or bitemporal satellites as appropriate.

The source must use technical state codes generated by `_code`; it must not
contain the canonical activity names. Include realistic noise and redundant
evidence so extraction has to distinguish business time from recording time,
filter technical records, and fuse duplicates. Foreign keys, uniqueness
constraints, and indexes should reflect the operational model.

### 4. Implement source insertion and extraction

Add `_insert_<slug>` and `_<slug>_query` functions to `benchmark.py`, then add
the insertion function to the dispatch in `build_scenario`. The insertion
function must:

1. translate canonical events into the source model;
2. call `_set_provenance` with the authoritative source table and record ID;
3. add corrections, retries, duplicates, history, and technical padding without
   turning them into extra canonical events;
4. reach the 100,000-source-row minimum; and
5. return the final extraction SQL.

The extraction query must return these columns in this order:

```text
case_id, activity, timestamp, source_table, source_record_id, actor, object_refs
```

`object_refs` must be a JSON array containing the complete canonical object set.
The query must normalize business timestamps to UTC, resolve the canonical
primary case ID, map technical codes with `_mapping_case`, filter technical or
corrective evidence, fuse duplicates, and end with:

```sql
ORDER BY case_id, timestamp, source_record_id
```

Also extend the scenario-specific duplicate-evidence query in `_validate` and
the rulebook/table-guide dictionaries in `_write_docs`.

### 5. Add the folder generator

Create `<slug>/generate_data.py` using the same thin wrapper as the existing
folders:

```python
#!/usr/bin/env python3
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from benchmark import build_scenario

if __name__ == "__main__":
    report = build_scenario("<slug>", Path(__file__).resolve().parent)
    print(f"<slug>: {report['status']} — {report['oracle_event_count']} events")
```

Generation creates or replaces:

```text
<slug>/source.sqlite
<slug>/ground_truth.ocel2.sqlite
<slug>/source_documentation.md
<slug>/business_glossary.md
<slug>/challenge_manifest.json
<slug>/validation_report.json
<slug>/case_views/primary_cases.{sql,csv}
<slug>/case_views/exception_cases.{sql,csv}
<slug>/case_views/multi_object_cases.{sql,csv}
<slug>/case_views/secondary_object_cases.{sql,csv}
```

The four views have distinct purposes:

- `primary_cases` is the complete primary case log and includes
  `is_exception_event`.
- `exception_cases` contains complete traces for primary cases with an
  exception; it is not an event-only filter.
- `multi_object_cases` contains complete traces for primary cases with a
  multi-object event and includes `is_multi_object_event`.
- `secondary_object_cases` changes the case notion to the declared secondary
  object and retains `primary_case_id` for traceability.

### 6. Generate, validate, and check reproducibility

Generate the new scenario first, then run the repository-wide checks:

```bash
python <slug>/generate_data.py
python validate_all.py
python -m py_compile benchmark.py domain_rules.py generate_all.py validate_all.py
git diff --check
```

Inspect `<slug>/validation_report.json`, including event/object counts, event
and object-type coverage, relation counts, minimum event-type frequency,
transactional sharing violations, role count, case-view row counts, fidelity,
and all Boolean checks. Read the OCEL back with PM4Py when changing the writer
or OCEL attributes.

Finally, record the `source_sha256` and `oracle_sha256` values, run the generator
again, and require the hashes to remain identical. Generation must not depend
on wall-clock time, unseeded randomness, unordered sets or maps, locale, or
external services.

## Commands

Regenerate every scenario:

```bash
python generate_all.py
```

Audit committed artifacts without regenerating them:

```bash
python validate_all.py
```
