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
