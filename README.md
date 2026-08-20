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
SQLite oracle written by PM4Py, a validation report, and three reproducible
case-centric SQL/CSV views.

Regenerate everything with:

```bash
python generate_all.py
```
