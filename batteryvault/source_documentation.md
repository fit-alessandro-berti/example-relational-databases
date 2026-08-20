# BatteryVault — circular battery lifecycle: source documentation

## Purpose

This is a synthetic **source-system** SQLite database for practicing object-centric extraction. It is not an event log and it does not contain the OCEL exchange tables. The independent oracle is `ground_truth.ocel2.sqlite`.

## Persistence pattern

Effective-time satellite transitions are deduplicated by hashdiff and source precedence; paired ledger entries form one movement despite two postings.

Primary evidence families:

- `sat_pack_status`
- `sat_pack_test`
- `sat_passport_data`
- `sat_diagnostic_result`
- `sat_service_status`
- `sat_campaign_status`
- `sat_claim_status`
- `sat_recall_status`
- `sat_shipment_status`
- `sat_second_life_status`
- `sat_recycling_status`
- `sat_certificate_status`
- `sat_incident_status`
- `asset_journal`

### Table families and meanings

- `hub_*` — stable hashed/business identities loaded from contributing systems.
- `link_* and link_effectivity` — historized assembly, ownership, shipment, service, and genealogy relations.
- `sat_*` — bitemporal status and attribute histories with replay/correction controls.
- `asset_journal/asset_ledger_entry` — balanced ownership or custody movements.
- `business_key_crosswalk/retired_identifier` — effective-dated identity resolution across source identifiers.
- `source_precedence` — attribute-domain-specific trust order for contradictory facts.

The database deliberately contains mixed business and technical records, late recording times, redundant evidence, shared master/asset references, and historical relationships. Text codes are technical source codes. Current-state fields, update timestamps, retries, and administrative corrections are not automatically business events.

## Tables and fields

The following tables and columns are present in `source.sqlite`:

- `asset_journal` — `journal_id` TEXT, `movement_code` TEXT, `effective_at` TEXT, `posted_at` TEXT, `source_system` TEXT, `status_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `location_code` TEXT, `amount_value` REAL
- `asset_ledger_entry` — `entry_id` TEXT, `journal_id` TEXT, `account_type` TEXT, `account_id` TEXT, `asset_type` TEXT, `asset_hub_key` TEXT, `direction` TEXT, `quantity` REAL, `effective_at` TEXT, `posted_at` TEXT, `reversal_of_entry_id` TEXT, `source_system` TEXT
- `business_key_crosswalk` — `source_system` TEXT, `source_identifier` TEXT, `canonical_hub_key` TEXT, `effective_from` TEXT, `effective_to` TEXT
- `hub_battery_pack` — `hub_key` TEXT, `business_key` TEXT, `load_dts` TEXT, `record_source` TEXT
- `hub_cell_batch` — `hub_key` TEXT, `business_key` TEXT, `load_dts` TEXT, `record_source` TEXT
- `hub_certificate` — `hub_key` TEXT, `business_key` TEXT, `load_dts` TEXT, `record_source` TEXT
- `hub_diagnostic` — `hub_key` TEXT, `business_key` TEXT, `load_dts` TEXT, `record_source` TEXT
- `hub_firmware_campaign` — `hub_key` TEXT, `business_key` TEXT, `load_dts` TEXT, `record_source` TEXT
- `hub_incident` — `hub_key` TEXT, `business_key` TEXT, `load_dts` TEXT, `record_source` TEXT
- `hub_material_batch` — `hub_key` TEXT, `business_key` TEXT, `load_dts` TEXT, `record_source` TEXT
- `hub_module` — `hub_key` TEXT, `business_key` TEXT, `load_dts` TEXT, `record_source` TEXT
- `hub_party` — `hub_key` TEXT, `business_key` TEXT, `load_dts` TEXT, `record_source` TEXT
- `hub_passport` — `hub_key` TEXT, `business_key` TEXT, `load_dts` TEXT, `record_source` TEXT
- `hub_recall_campaign` — `hub_key` TEXT, `business_key` TEXT, `load_dts` TEXT, `record_source` TEXT
- `hub_recycling_order` — `hub_key` TEXT, `business_key` TEXT, `load_dts` TEXT, `record_source` TEXT
- `hub_second_life_system` — `hub_key` TEXT, `business_key` TEXT, `load_dts` TEXT, `record_source` TEXT
- `hub_service_order` — `hub_key` TEXT, `business_key` TEXT, `load_dts` TEXT, `record_source` TEXT
- `hub_shipment` — `hub_key` TEXT, `business_key` TEXT, `load_dts` TEXT, `record_source` TEXT
- `hub_vehicle` — `hub_key` TEXT, `business_key` TEXT, `load_dts` TEXT, `record_source` TEXT
- `hub_warehouse` — `hub_key` TEXT, `business_key` TEXT, `load_dts` TEXT, `record_source` TEXT
- `hub_warranty_claim` — `hub_key` TEXT, `business_key` TEXT, `load_dts` TEXT, `record_source` TEXT
- `ledger_account` — `account_type` TEXT, `account_id` TEXT, `valid_from` TEXT, `valid_to` TEXT
- `ledger_reversal` — `reversal_journal_id` TEXT, `original_journal_id` TEXT, `reason_code` TEXT, `reversed_at` TEXT
- `link_certificate_subject` — `link_key` TEXT, `certificate_hub_key` TEXT, `subject_hub_key` TEXT, `subject_type` TEXT, `load_dts` TEXT, `record_source` TEXT
- `link_effectivity` — `link_key` TEXT, `load_dts` TEXT, `effective_from` TEXT, `effective_to` TEXT, `is_active` INTEGER, `record_source` TEXT
- `link_incident_subject` — `link_key` TEXT, `incident_hub_key` TEXT, `subject_hub_key` TEXT, `subject_type` TEXT, `load_dts` TEXT, `record_source` TEXT
- `link_module_cell_batch` — `link_key` TEXT, `module_hub_key` TEXT, `cell_batch_hub_key` TEXT, `load_dts` TEXT, `record_source` TEXT
- `link_pack_diagnostic` — `link_key` TEXT, `pack_hub_key` TEXT, `diagnostic_hub_key` TEXT, `load_dts` TEXT, `record_source` TEXT
- `link_pack_firmware_campaign` — `link_key` TEXT, `pack_hub_key` TEXT, `campaign_hub_key` TEXT, `load_dts` TEXT, `record_source` TEXT
- `link_pack_module` — `link_key` TEXT, `pack_hub_key` TEXT, `module_hub_key` TEXT, `load_dts` TEXT, `record_source` TEXT
- `link_pack_owner` — `link_key` TEXT, `pack_hub_key` TEXT, `owner_hub_key` TEXT, `load_dts` TEXT, `record_source` TEXT
- `link_pack_passport` — `link_key` TEXT, `pack_hub_key` TEXT, `passport_hub_key` TEXT, `load_dts` TEXT, `record_source` TEXT
- `link_pack_recall` — `link_key` TEXT, `pack_hub_key` TEXT, `recall_hub_key` TEXT, `load_dts` TEXT, `record_source` TEXT
- `link_pack_recycling_order` — `link_key` TEXT, `pack_hub_key` TEXT, `recycling_hub_key` TEXT, `load_dts` TEXT, `record_source` TEXT
- `link_pack_second_life` — `link_key` TEXT, `pack_hub_key` TEXT, `second_life_hub_key` TEXT, `load_dts` TEXT, `record_source` TEXT
- `link_pack_service` — `link_key` TEXT, `pack_hub_key` TEXT, `service_hub_key` TEXT, `load_dts` TEXT, `record_source` TEXT
- `link_pack_shipment` — `link_key` TEXT, `pack_hub_key` TEXT, `shipment_hub_key` TEXT, `load_dts` TEXT, `record_source` TEXT
- `link_pack_warranty_claim` — `link_key` TEXT, `pack_hub_key` TEXT, `claim_hub_key` TEXT, `load_dts` TEXT, `record_source` TEXT
- `link_recycling_material_batch` — `link_key` TEXT, `recycling_hub_key` TEXT, `material_hub_key` TEXT, `load_dts` TEXT, `record_source` TEXT
- `link_shipment_warehouse` — `link_key` TEXT, `shipment_hub_key` TEXT, `warehouse_hub_key` TEXT, `qualifier_code` TEXT, `load_dts` TEXT, `record_source` TEXT
- `link_vehicle_pack` — `link_key` TEXT, `vehicle_hub_key` TEXT, `pack_hub_key` TEXT, `load_dts` TEXT, `record_source` TEXT
- `record_source_catalog` — `record_source` TEXT, `source_kind` TEXT, `timezone_name` TEXT
- `retired_identifier` — `identifier` TEXT, `hub_key` TEXT, `retired_at` TEXT, `reason_code` TEXT
- `sat_campaign_status` — `satellite_id` TEXT, `parent_key` TEXT, `load_dts` TEXT, `effective_from` TEXT, `effective_to` TEXT, `hashdiff` TEXT, `record_source` TEXT, `source_sequence` INT, `is_correction` INT, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT
- `sat_cell_batch_status` — `satellite_id` TEXT, `parent_key` TEXT, `load_dts` TEXT, `effective_from` TEXT, `effective_to` TEXT, `hashdiff` TEXT, `record_source` TEXT, `source_sequence` INTEGER, `is_correction` INTEGER, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT
- `sat_certificate_status` — `satellite_id` TEXT, `parent_key` TEXT, `load_dts` TEXT, `effective_from` TEXT, `effective_to` TEXT, `hashdiff` TEXT, `record_source` TEXT, `source_sequence` INT, `is_correction` INT, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT
- `sat_claim_status` — `satellite_id` TEXT, `parent_key` TEXT, `load_dts` TEXT, `effective_from` TEXT, `effective_to` TEXT, `hashdiff` TEXT, `record_source` TEXT, `source_sequence` INT, `is_correction` INT, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT
- `sat_diagnostic_result` — `satellite_id` TEXT, `parent_key` TEXT, `load_dts` TEXT, `effective_from` TEXT, `effective_to` TEXT, `hashdiff` TEXT, `record_source` TEXT, `source_sequence` INT, `is_correction` INT, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT
- `sat_incident_status` — `satellite_id` TEXT, `parent_key` TEXT, `load_dts` TEXT, `effective_from` TEXT, `effective_to` TEXT, `hashdiff` TEXT, `record_source` TEXT, `source_sequence` INT, `is_correction` INT, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT
- `sat_module_status` — `satellite_id` TEXT, `parent_key` TEXT, `load_dts` TEXT, `effective_from` TEXT, `effective_to` TEXT, `hashdiff` TEXT, `record_source` TEXT, `source_sequence` INT, `is_correction` INT, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT
- `sat_ownership_role` — `satellite_id` TEXT, `parent_key` TEXT, `load_dts` TEXT, `effective_from` TEXT, `effective_to` TEXT, `hashdiff` TEXT, `record_source` TEXT, `source_sequence` INT, `is_correction` INT, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT
- `sat_pack_specification` — `satellite_id` TEXT, `parent_key` TEXT, `load_dts` TEXT, `effective_from` TEXT, `effective_to` TEXT, `hashdiff` TEXT, `record_source` TEXT, `source_sequence` INT, `is_correction` INT, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT
- `sat_pack_status` — `satellite_id` TEXT, `parent_key` TEXT, `load_dts` TEXT, `effective_from` TEXT, `effective_to` TEXT, `hashdiff` TEXT, `record_source` TEXT, `source_sequence` INT, `is_correction` INT, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT
- `sat_pack_test` — `satellite_id` TEXT, `parent_key` TEXT, `load_dts` TEXT, `effective_from` TEXT, `effective_to` TEXT, `hashdiff` TEXT, `record_source` TEXT, `source_sequence` INT, `is_correction` INT, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT
- `sat_passport_data` — `satellite_id` TEXT, `parent_key` TEXT, `load_dts` TEXT, `effective_from` TEXT, `effective_to` TEXT, `hashdiff` TEXT, `record_source` TEXT, `source_sequence` INT, `is_correction` INT, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT
- `sat_recall_status` — `satellite_id` TEXT, `parent_key` TEXT, `load_dts` TEXT, `effective_from` TEXT, `effective_to` TEXT, `hashdiff` TEXT, `record_source` TEXT, `source_sequence` INT, `is_correction` INT, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT
- `sat_recycling_status` — `satellite_id` TEXT, `parent_key` TEXT, `load_dts` TEXT, `effective_from` TEXT, `effective_to` TEXT, `hashdiff` TEXT, `record_source` TEXT, `source_sequence` INT, `is_correction` INT, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT
- `sat_second_life_status` — `satellite_id` TEXT, `parent_key` TEXT, `load_dts` TEXT, `effective_from` TEXT, `effective_to` TEXT, `hashdiff` TEXT, `record_source` TEXT, `source_sequence` INT, `is_correction` INT, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT
- `sat_service_status` — `satellite_id` TEXT, `parent_key` TEXT, `load_dts` TEXT, `effective_from` TEXT, `effective_to` TEXT, `hashdiff` TEXT, `record_source` TEXT, `source_sequence` INT, `is_correction` INT, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT
- `sat_shipment_status` — `satellite_id` TEXT, `parent_key` TEXT, `load_dts` TEXT, `effective_from` TEXT, `effective_to` TEXT, `hashdiff` TEXT, `record_source` TEXT, `source_sequence` INT, `is_correction` INT, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT
- `sat_telemetry_summary` — `satellite_id` TEXT, `parent_key` TEXT, `load_dts` TEXT, `effective_from` TEXT, `effective_to` TEXT, `hashdiff` TEXT, `record_source` TEXT, `source_sequence` INT, `is_correction` INT, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT
- `sat_vehicle_status` — `satellite_id` TEXT, `parent_key` TEXT, `load_dts` TEXT, `effective_from` TEXT, `effective_to` TEXT, `hashdiff` TEXT, `record_source` TEXT, `source_sequence` INT, `is_correction` INT, `state_code` TEXT, `related_refs_json` TEXT, `actor_code` TEXT, `amount_value` REAL, `location_code` TEXT
- `source_precedence` — `attribute_domain` TEXT, `record_source` TEXT, `priority_no` INTEGER, `valid_from` TEXT, `valid_to` TEXT

## Deterministic ambiguity rules

- Order satellite facts by effective_from, then source precedence and load_dts; ignore hashdiff replays.
- Corrections with the same effective interval change attributes without adding an activity.
- Balance debit and credit entries by journal and asset before emitting one custody or ownership movement.

## Time and identity

Business timestamps are normalized to UTC only by the extraction views. Source timestamps intentionally use ISO strings, split dates/times, epoch seconds, or effective/load pairs as appropriate. Canonical identities use the technical relationships or workflow scopes; no universal source event table exists.

## Case views

The primary case notion is `BatteryPack`. The secondary-object view uses `ServiceOrder` as an independent case notion. Exception and multi-object views retain complete primary-case traces and add explicit event flags. Every CSV is ordered first by `case_id`, then by `timestamp`, with `source_record_id` used only to break ties deterministically.

## Reproduction

Run `python generate_data.py`. Generation is deterministic with seed 20260820 and 3,000 primary instances. The script recreates the source database, OCEL oracle, validation report, and all case-view CSV files.

The final activity-mapping queries are intentionally absent from this document. They are present only in the case-view SQL exercises.
