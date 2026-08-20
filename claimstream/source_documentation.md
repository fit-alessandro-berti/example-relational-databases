# ClaimStream — property-insurance claims: source documentation

## Purpose

This is a synthetic **source-system** SQLite database for practicing object-centric extraction. It is not an event log and it does not contain the OCEL exchange tables. The independent oracle is `ground_truth.ocel2.sqlite`.

## Persistence pattern

Append-only domain events are correlated across streams, payload versions are upcast, and projections/snapshots remain non-authoritative technical artifacts.

Primary evidence families:

- `event_store`
- `command_result`
- `inbox_message`
- `document_index`

### Table families and meanings

- `event_store` — append-only aggregate streams with schema-versioned JSON payloads.
- `command_result/inbox_message` — accepted commands and external facts that can supply business evidence.
- `snapshot_store/projections` — stale-capable query optimizations, never authoritative history.
- `event_type_alias/schema_upcaster_rule` — technical type normalization and old-payload conversion metadata.
- `stream_alias` — effective-dated external-to-canonical stream identity.
- `saga_state/outbox_message` — technical orchestration and integration artifacts.

The database deliberately contains mixed business and technical records, late recording times, redundant evidence, shared master/asset references, and historical relationships. Text codes are technical source codes. Current-state fields, update timestamps, retries, and administrative corrections are not automatically business events.

## Deterministic ambiguity rules

- Exclude technical stream types and technical event aliases before business classification.
- Upcast money and identifier fields according to schema version before correlation.
- Fuse retries and cross-stream echoes by correlation ID plus semantic code; use payload effectiveAt as business time.

## Time and identity

Business timestamps are normalized to UTC only by the extraction views. Source timestamps intentionally use ISO strings, split dates/times, epoch seconds, or effective/load pairs as appropriate. Canonical identities use the technical relationships or workflow scopes; no universal source event table exists.

## Reproduction

Run `python generate_data.py`. Generation is deterministic with seed 20260820 and 3,000 primary instances. The script recreates the source database, OCEL oracle, validation report, and all case-view CSV files.

The final activity-mapping queries are intentionally absent from this document. They are present only in the case-view SQL exercises.
