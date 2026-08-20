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

## Tables and fields

The following tables and columns are present in `source.sqlite`:

- `adverse_event_v` — `record_id` TEXT, `logical_id` TEXT, `version_no` INT, `valid_from` TEXT, `valid_to` TEXT, `recorded_at` TEXT, `edit_session_id` TEXT, `supersedes_version_no` INT, `change_kind` TEXT, `change_reason_code` TEXT, `changed_by` TEXT, `is_current` INT, `is_deleted` INT, `row_hash` TEXT, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT, `payload_json` TEXT
- `aliquot_v` — `record_id` TEXT, `logical_id` TEXT, `version_no` INT, `valid_from` TEXT, `valid_to` TEXT, `recorded_at` TEXT, `edit_session_id` TEXT, `supersedes_version_no` INT, `change_kind` TEXT, `change_reason_code` TEXT, `changed_by` TEXT, `is_current` INT, `is_deleted` INT, `row_hash` TEXT, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT, `payload_json` TEXT
- `code_dictionary` — `domain_code` TEXT, `value_code` TEXT, `language_code` TEXT, `display_text` TEXT
- `consent_v` — `record_id` TEXT, `logical_id` TEXT, `version_no` INT, `valid_from` TEXT, `valid_to` TEXT, `recorded_at` TEXT, `edit_session_id` TEXT, `supersedes_version_no` INT, `change_kind` TEXT, `change_reason_code` TEXT, `changed_by` TEXT, `is_current` INT, `is_deleted` INT, `row_hash` TEXT, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT, `payload_json` TEXT
- `data_query_v` — `record_id` TEXT, `logical_id` TEXT, `version_no` INT, `valid_from` TEXT, `valid_to` TEXT, `recorded_at` TEXT, `edit_session_id` TEXT, `supersedes_version_no` INT, `change_kind` TEXT, `change_reason_code` TEXT, `changed_by` TEXT, `is_current` INT, `is_deleted` INT, `row_hash` TEXT, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT, `payload_json` TEXT
- `dispensation_v` — `record_id` TEXT, `logical_id` TEXT, `version_no` INT, `valid_from` TEXT, `valid_to` TEXT, `recorded_at` TEXT, `edit_session_id` TEXT, `supersedes_version_no` INT, `change_kind` TEXT, `change_reason_code` TEXT, `changed_by` TEXT, `is_current` INT, `is_deleted` INT, `row_hash` TEXT, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT, `payload_json` TEXT
- `dose_v` — `record_id` TEXT, `logical_id` TEXT, `version_no` INT, `valid_from` TEXT, `valid_to` TEXT, `recorded_at` TEXT, `edit_session_id` TEXT, `supersedes_version_no` INT, `change_kind` TEXT, `change_reason_code` TEXT, `changed_by` TEXT, `is_current` INT, `is_deleted` INT, `row_hash` TEXT, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT, `payload_json` TEXT
- `drug_kit_v` — `record_id` TEXT, `logical_id` TEXT, `version_no` INT, `valid_from` TEXT, `valid_to` TEXT, `recorded_at` TEXT, `edit_session_id` TEXT, `supersedes_version_no` INT, `change_kind` TEXT, `change_reason_code` TEXT, `changed_by` TEXT, `is_current` INT, `is_deleted` INT, `row_hash` TEXT, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT, `payload_json` TEXT
- `edit_session` — `edit_session_id` TEXT, `edited_by` TEXT, `recorded_at` TEXT, `session_kind` TEXT, `reason_code` TEXT
- `investigator_v` — `record_id` TEXT, `logical_id` TEXT, `version_no` INT, `valid_from` TEXT, `valid_to` TEXT, `recorded_at` TEXT, `edit_session_id` TEXT, `supersedes_version_no` INT, `change_kind` TEXT, `change_reason_code` TEXT, `changed_by` TEXT, `is_current` INT, `is_deleted` INT, `row_hash` TEXT, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT, `payload_json` TEXT
- `lab_order_v` — `record_id` TEXT, `logical_id` TEXT, `version_no` INT, `valid_from` TEXT, `valid_to` TEXT, `recorded_at` TEXT, `edit_session_id` TEXT, `supersedes_version_no` INT, `change_kind` TEXT, `change_reason_code` TEXT, `changed_by` TEXT, `is_current` INT, `is_deleted` INT, `row_hash` TEXT, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT, `payload_json` TEXT
- `lab_result_v` — `record_id` TEXT, `logical_id` TEXT, `version_no` INT, `valid_from` TEXT, `valid_to` TEXT, `recorded_at` TEXT, `edit_session_id` TEXT, `supersedes_version_no` INT, `change_kind` TEXT, `change_reason_code` TEXT, `changed_by` TEXT, `is_current` INT, `is_deleted` INT, `row_hash` TEXT, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT, `payload_json` TEXT
- `lab_test_v` — `record_id` TEXT, `logical_id` TEXT, `version_no` INT, `valid_from` TEXT, `valid_to` TEXT, `recorded_at` TEXT, `edit_session_id` TEXT, `supersedes_version_no` INT, `change_kind` TEXT, `change_reason_code` TEXT, `changed_by` TEXT, `is_current` INT, `is_deleted` INT, `row_hash` TEXT, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT, `payload_json` TEXT
- `object_relation_v` — `relation_id` TEXT, `source_type` TEXT, `source_logical_id` TEXT, `target_type` TEXT, `target_logical_id` TEXT, `qualifier_code` TEXT, `valid_from` TEXT, `valid_to` TEXT, `recorded_at` TEXT, `edit_session_id` TEXT, `change_kind` TEXT
- `participant_v` — `record_id` TEXT, `logical_id` TEXT, `version_no` INT, `valid_from` TEXT, `valid_to` TEXT, `recorded_at` TEXT, `edit_session_id` TEXT, `supersedes_version_no` INT, `change_kind` TEXT, `change_reason_code` TEXT, `changed_by` TEXT, `is_current` INT, `is_deleted` INT, `row_hash` TEXT, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT, `payload_json` TEXT
- `protocol_deviation_v` — `record_id` TEXT, `logical_id` TEXT, `version_no` INT, `valid_from` TEXT, `valid_to` TEXT, `recorded_at` TEXT, `edit_session_id` TEXT, `supersedes_version_no` INT, `change_kind` TEXT, `change_reason_code` TEXT, `changed_by` TEXT, `is_current` INT, `is_deleted` INT, `row_hash` TEXT, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT, `payload_json` TEXT
- `protocol_v` — `record_id` TEXT, `logical_id` TEXT, `version_no` INT, `valid_from` TEXT, `valid_to` TEXT, `recorded_at` TEXT, `edit_session_id` TEXT, `supersedes_version_no` INT, `change_kind` TEXT, `change_reason_code` TEXT, `changed_by` TEXT, `is_current` INT, `is_deleted` INT, `row_hash` TEXT, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT, `payload_json` TEXT
- `sample_shipment_v` — `record_id` TEXT, `logical_id` TEXT, `version_no` INT, `valid_from` TEXT, `valid_to` TEXT, `recorded_at` TEXT, `edit_session_id` TEXT, `supersedes_version_no` INT, `change_kind` TEXT, `change_reason_code` TEXT, `changed_by` TEXT, `is_current` INT, `is_deleted` INT, `row_hash` TEXT, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT, `payload_json` TEXT
- `sample_v` — `record_id` TEXT, `logical_id` TEXT, `version_no` INT, `valid_from` TEXT, `valid_to` TEXT, `recorded_at` TEXT, `edit_session_id` TEXT, `supersedes_version_no` INT, `change_kind` TEXT, `change_reason_code` TEXT, `changed_by` TEXT, `is_current` INT, `is_deleted` INT, `row_hash` TEXT, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT, `payload_json` TEXT
- `shipment_item_v` — `record_id` TEXT, `logical_id` TEXT, `version_no` INT, `valid_from` TEXT, `valid_to` TEXT, `recorded_at` TEXT, `edit_session_id` TEXT, `supersedes_version_no` INT, `change_kind` TEXT, `change_reason_code` TEXT, `changed_by` TEXT, `is_current` INT, `is_deleted` INT, `row_hash` TEXT, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT, `payload_json` TEXT
- `site_timezone` — `site_logical_id` TEXT, `valid_from` TEXT, `valid_to` TEXT, `timezone_name` TEXT
- `site_v` — `record_id` TEXT, `logical_id` TEXT, `version_no` INT, `valid_from` TEXT, `valid_to` TEXT, `recorded_at` TEXT, `edit_session_id` TEXT, `supersedes_version_no` INT, `change_kind` TEXT, `change_reason_code` TEXT, `changed_by` TEXT, `is_current` INT, `is_deleted` INT, `row_hash` TEXT, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT, `payload_json` TEXT
- `study_v` — `record_id` TEXT, `logical_id` TEXT, `version_no` INTEGER, `valid_from` TEXT, `valid_to` TEXT, `recorded_at` TEXT, `edit_session_id` TEXT, `supersedes_version_no` INTEGER, `change_kind` TEXT, `change_reason_code` TEXT, `changed_by` TEXT, `is_current` INTEGER, `is_deleted` INTEGER, `row_hash` TEXT, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT, `payload_json` TEXT
- `visit_v` — `record_id` TEXT, `logical_id` TEXT, `version_no` INT, `valid_from` TEXT, `valid_to` TEXT, `recorded_at` TEXT, `edit_session_id` TEXT, `supersedes_version_no` INT, `change_kind` TEXT, `change_reason_code` TEXT, `changed_by` TEXT, `is_current` INT, `is_deleted` INT, `row_hash` TEXT, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT, `payload_json` TEXT

## Deterministic ambiguity rules

- Order versions by version_no for recording precedence and use valid_from for business time.
- Only BUSINESS versions with a classified semantic state can produce events; corrections update attributes.
- Resolve versioned relations at the event's valid time, never from a stale is_current flag.

## Time and identity

Business timestamps are normalized to UTC only by the extraction views. Source timestamps intentionally use ISO strings, split dates/times, epoch seconds, or effective/load pairs as appropriate. Canonical identities use the technical relationships or workflow scopes; no universal source event table exists.

## Case views

The primary case notion is `Participant`. The secondary-object view uses `Sample` as an independent case notion. Exception and multi-object views retain complete primary-case traces and add explicit event flags. Every CSV is ordered first by `case_id`, then by `timestamp`, with `source_record_id` used only to break ties deterministically.

## Reproduction

Run `python generate_data.py`. Generation is deterministic with seed 20260820 and 3,000 primary instances. The script recreates the source database, OCEL oracle, validation report, and all case-view CSV files.

The final activity-mapping queries are intentionally absent from this document. They are present only in the case-view SQL exercises.
