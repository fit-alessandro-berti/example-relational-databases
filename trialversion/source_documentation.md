# TrialVersion — clinical-trial execution: source documentation

## Purpose

This is a synthetic **source-system** SQLite database for practicing object-centric extraction. It is not an event log and it does not contain the OCEL exchange tables. The independent oracle is `ground_truth.ocel2.sqlite`.

## Persistence pattern

Successive logical versions must be compared. BUSINESS changes can create activities; CORRECTION, IMPORT_REPLAY, and SYSTEM_RECALCULATION versions cannot do so by insertion alone.

Primary evidence families:

- `study_v`
- `protocol_v`
- `site_v`
- `participant_v`
- `visit_v`
- `drug_kit_v`
- `sample_v`
- `sample_shipment_v`
- `lab_test_v`
- `lab_result_v`
- `adverse_event_v`
- `data_query_v`

### Table families and meanings

- `*_v` — coexisting logical row versions with valid time, recording time, edit session, and change kind.
- `object_relation_v` — historized participant, sample, shipment, investigator, and study scope relations.
- `edit_session` — one user or system save that can touch multiple versioned objects.
- `site_timezone` — effective-dated site time-zone rules.
- `code_dictionary` — technical domain values and language-dependent display text.

The database deliberately contains mixed business and technical records, late recording times, redundant evidence, shared master/asset references, and historical relationships. Text codes are technical source codes. Current-state fields, update timestamps, retries, and administrative corrections are not automatically business events.

## Deterministic ambiguity rules

- Order versions by version_no for recording precedence and use valid_from for business time.
- Only BUSINESS versions with a classified semantic state can produce events; corrections update attributes.
- Resolve versioned relations at the event's valid time, never from a stale is_current flag.

## Time and identity

Business timestamps are normalized to UTC only by the extraction views. Source timestamps intentionally use ISO strings, split dates/times, epoch seconds, or effective/load pairs as appropriate. Canonical identities use the technical relationships or workflow scopes; no universal source event table exists.

## Reproduction

Run `python generate_data.py`. Generation is deterministic with seed 20260820 and 3,000 primary instances. The script recreates the source database, OCEL oracle, validation report, and all case-view CSV files.

The final activity-mapping queries are intentionally absent from this document. They are present only in the case-view SQL exercises.
