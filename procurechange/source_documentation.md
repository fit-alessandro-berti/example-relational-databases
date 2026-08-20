# ProcureChange — industrial procure-to-pay: source documentation

## Purpose

This is a synthetic **source-system** SQLite database for practicing object-centric extraction. It is not an event log and it does not contain the OCEL exchange tables. The independent oracle is `ground_truth.ocel2.sqlite`.

## Persistence pattern

Generic CDHDR/CDPOS field sets are decoded with fixed-width key metadata, then fused with application documents and archived changes.

Primary evidence families:

- `cdhdr`
- `req_header`
- `goods_movement_header`
- `inspection_lot`
- `invoice_header`
- `accounting_header`
- `payment_run`

### Table families and meanings

- `cdhdr/cdpos` — change header plus field-level string changes with packed application keys.
- `archive_cdhdr/archive_cdpos` — older change documents with deliberate live/archive overlap.
- `tabkey_layout/field_catalog` — metadata needed to decode keys and typed old/new values.
- `document_flow/po_history` — many-to-many item-level predecessor and follow-on document relations.
- `application header/item tables` — authoritative material, receipt, invoice, accounting, and payment documents.
- `approval_workflow/approval_step` — approval state and technical workflow history.

The database deliberately contains mixed business and technical records, late recording times, redundant evidence, shared master/asset references, and historical relationships. Text codes are technical source codes. Current-state fields, update timestamps, retries, and administrative corrections are not automatically business events.

## Deterministic ambiguity rules

- Decode packed keys using tabkey_layout before joining application rows.
- Union archive and live change documents and retain the live copy during overlap.
- Classify the complete field-change set per change number and deduplicate application evidence.

## Time and identity

Business timestamps are normalized to UTC only by the extraction views. Source timestamps intentionally use ISO strings, split dates/times, epoch seconds, or effective/load pairs as appropriate. Canonical identities use the technical relationships or workflow scopes; no universal source event table exists.

## Case views

The primary case notion is `PurchaseRequisition`. The secondary-object view uses `Invoice` as an independent case notion. Exception and multi-object views retain complete primary-case traces and add explicit event flags. Every CSV is ordered first by `case_id`, then by `timestamp`, with `source_record_id` used only to break ties deterministically.

## Reproduction

Run `python generate_data.py`. Generation is deterministic with seed 20260820 and 3,000 primary instances. The script recreates the source database, OCEL oracle, validation report, and all case-view CSV files.

The final activity-mapping queries are intentionally absent from this document. They are present only in the case-view SQL exercises.
