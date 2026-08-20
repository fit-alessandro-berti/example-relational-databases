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

## Tables and fields

The following tables and columns are present in `source.sqlite`:

- `claim_projection` — `claim_ref` TEXT, `current_state_code` TEXT, `last_global_position` INTEGER, `projection_json` TEXT
- `command_log` — `command_id` TEXT, `stream_id` TEXT, `command_type` TEXT, `accepted_at` TEXT, `payload_json` TEXT
- `command_result` — `result_id` TEXT, `stream_id` TEXT, `event_type` TEXT, `semantic_code` TEXT, `result_code` TEXT, `occurred_at` TEXT, `recorded_at` TEXT, `payload_json` TEXT, `correlation_id` TEXT, `actor_code` TEXT
- `document_index` — `document_id` TEXT, `stream_id` TEXT, `event_type` TEXT, `semantic_code` TEXT, `effective_at` TEXT, `indexed_at` TEXT, `payload_json` TEXT, `correlation_id` TEXT, `index_status` TEXT
- `event_store` — `global_position` INTEGER, `stream_id` TEXT, `stream_type` TEXT, `stream_version` INTEGER, `event_type` TEXT, `schema_version` INTEGER, `occurred_at` TEXT, `recorded_at` TEXT, `payload_json` TEXT, `metadata_json` TEXT, `correlation_id` TEXT, `causation_id` TEXT, `tenant_id` TEXT, `is_redacted` INTEGER
- `event_type_alias` — `event_type` TEXT, `schema_version` INTEGER, `semantic_code` TEXT
- `exposure_projection` — `exposure_ref` TEXT, `claim_ref` TEXT, `current_state_code` TEXT, `last_global_position` INTEGER
- `inbox_message` — `message_id` TEXT, `sender_ref` TEXT, `event_type` TEXT, `semantic_code` TEXT, `occurred_at` TEXT, `recorded_at` TEXT, `payload_json` TEXT, `correlation_id` TEXT, `processed_flag` INTEGER
- `outbox_message` — `message_id` TEXT, `correlation_id` TEXT, `topic_code` TEXT, `payload_json` TEXT, `queued_at` TEXT, `sent_at` TEXT
- `party_projection` — `party_ref` TEXT, `masked_identity` TEXT, `current_role_code` TEXT
- `payment_projection` — `payment_ref` TEXT, `claim_ref` TEXT, `current_state_code` TEXT, `amount_value` REAL
- `projection_checkpoint` — `projection_name` TEXT, `global_position` INTEGER, `updated_at` TEXT
- `redacted_identity_map` — `redacted_ref` TEXT, `stable_party_ref` TEXT, `redacted_at` TEXT
- `repair_projection` — `repair_ref` TEXT, `claim_ref` TEXT, `current_state_code` TEXT
- `saga_state` — `saga_id` TEXT, `correlation_id` TEXT, `state_code` TEXT, `payload_json` TEXT, `checkpoint_at` TEXT
- `schema_upcaster_rule` — `event_type` TEXT, `from_version` INTEGER, `to_version` INTEGER, `rule_json` TEXT
- `snapshot_store` — `stream_id` TEXT, `stream_version` INTEGER, `snapshot_type` TEXT, `snapshot_json` TEXT, `written_at` TEXT
- `stream_alias` — `alias_id` TEXT, `canonical_stream_id` TEXT, `valid_from` TEXT, `valid_to` TEXT

## Deterministic ambiguity rules

- Exclude technical stream types and technical event aliases before business classification.
- Upcast money and identifier fields according to schema version before correlation.
- Fuse retries and cross-stream echoes by correlation ID plus semantic code; use payload effectiveAt as business time.

## Time and identity

Business timestamps are normalized to UTC only by the extraction views. Source timestamps intentionally use ISO strings, split dates/times, epoch seconds, or effective/load pairs as appropriate. Canonical identities use the technical relationships or workflow scopes; no universal source event table exists.

## Case views

The primary case notion is `Claim`. The secondary-object view uses `Exposure` as an independent case notion. Exception and multi-object views retain complete primary-case traces and add explicit event flags. Every CSV is ordered first by `case_id`, then by `timestamp`, with `source_record_id` used only to break ties deterministically.

## Reproduction

Run `python generate_data.py`. Generation is deterministic with seed 20260820 and 3,000 primary instances. The script recreates the source database, OCEL oracle, validation report, and all case-view CSV files.

The final activity-mapping queries are intentionally absent from this document. They are present only in the case-view SQL exercises.
