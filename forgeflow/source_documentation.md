# ForgeFlow — engineer-to-order manufacturing: source documentation

## Purpose

This is a synthetic **source-system** SQLite database for practicing object-centric extraction. It is not an event log and it does not contain the OCEL exchange tables. The independent oracle is `ground_truth.ocel2.sqlite`.

## Persistence pattern

Milestones are spread over commercial, engineering, supply, quality, fulfilment, and finance records. Transaction references fuse redundant outbox evidence.

Primary evidence families:

- `commercial_document`
- `engineering_execution`
- `supply_posting`
- `quality_observation`
- `fulfilment_record`
- `finance_posting`

### Table families and meanings

- `commercial_document` — commercial lifecycle evidence with split local date/time.
- `engineering_execution` — engineering and operation attempts with separate effective and recording times.
- `supply_posting` — procurement/inventory postings using compact dates and seconds since midnight.
- `quality_observation` — inspection and nonconformance facts stored as epoch milliseconds.
- `fulfilment_record` — package/shipment milestones stored as epoch seconds.
- `finance_posting` — invoice/payment postings with compact clocks.
- `document_conversion` — predecessor/successor scope bridge across heterogeneous documents.
- `integration_outbox` — redundant integration and technical messages; not an activity log.

The database deliberately contains mixed business and technical records, late recording times, redundant evidence, shared master/asset references, and historical relationships. Text codes are technical source codes. Current-state fields, update timestamps, retries, and administrative corrections are not automatically business events.

## Deterministic ambiguity rules

- Normalize each table's native time representation before ordering.
- Fuse outbox/package/movement evidence only when transaction reference and business scope agree.
- Treat current status and updated-at fields as state, not standalone events.

## Time and identity

Business timestamps are normalized to UTC only by the extraction views. Source timestamps intentionally use ISO strings, split dates/times, epoch seconds, or effective/load pairs as appropriate. Canonical identities use the technical relationships or workflow scopes; no universal source event table exists.

## Case views

The primary case notion is `SalesOrder`. The secondary-object view uses `Shipment` as an independent case notion. Exception and multi-object views retain complete primary-case traces and add explicit event flags. Every CSV is ordered first by `case_id`, then by `timestamp`, with `source_record_id` used only to break ties deterministically.

## Reproduction

Run `python generate_data.py`. Generation is deterministic with seed 20260820 and 3,000 primary instances. The script recreates the source database, OCEL oracle, validation report, and all case-view CSV files.

The final activity-mapping queries are intentionally absent from this document. They are present only in the case-view SQL exercises.
