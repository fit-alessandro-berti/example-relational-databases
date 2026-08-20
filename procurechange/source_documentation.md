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

## Tables and fields

The following tables and columns are present in `source.sqlite`:

- `accounting_header` — `record_key` TEXT, `document_ref` TEXT, `document_code` TEXT, `posting_date` TEXT, `posting_time` TEXT, `username` TEXT, `amount_value` REAL, `location_code` TEXT, `related_refs_json` TEXT, `transaction_ref` TEXT, `is_reversal` INT
- `accounting_line` — `accounting_record_key` TEXT, `line_no` INTEGER, `account_type` TEXT, `account_no` TEXT, `amount_text` TEXT, `debit_credit_code` TEXT
- `approval_step` — `step_id` TEXT, `workflow_id` TEXT, `step_code` TEXT, `status_code` TEXT, `changed_at` TEXT, `actor_code` TEXT
- `approval_workflow` — `workflow_id` TEXT, `object_type_code` TEXT, `object_ref` TEXT, `opened_at` TEXT, `closed_at` TEXT, `state_code` TEXT
- `archive_cdhdr` — `client` TEXT, `object_class` TEXT, `object_id` TEXT, `change_number` TEXT, `username` TEXT, `change_date` TEXT, `change_time` TEXT, `transaction_code` TEXT, `change_indicator` TEXT, `source_system` TEXT
- `archive_cdpos` — `client` TEXT, `object_class` TEXT, `object_id` TEXT, `change_number` TEXT, `table_name` TEXT, `table_key` TEXT, `field_name` TEXT, `change_indicator` TEXT, `old_value_text` TEXT, `new_value_text` TEXT, `old_unit` TEXT, `new_unit` TEXT, `currency_code` TEXT, `value_type_code` TEXT
- `archive_index` — `archive_id` TEXT, `first_change_number` TEXT, `last_change_number` TEXT, `archived_at` TEXT
- `asn_header` — `asn_number` TEXT, `supplier_no` TEXT, `po_number` TEXT, `received_at` TEXT
- `asn_item` — `asn_number` TEXT, `item_no` INTEGER, `po_number` TEXT, `po_item_no` INTEGER, `quantity_text` TEXT
- `cdhdr` — `client` TEXT, `object_class` TEXT, `object_id` TEXT, `change_number` TEXT, `username` TEXT, `change_date` TEXT, `change_time` TEXT, `transaction_code` TEXT, `change_indicator` TEXT, `source_system` TEXT
- `cdpos` — `client` TEXT, `object_class` TEXT, `object_id` TEXT, `change_number` TEXT, `table_name` TEXT, `table_key` TEXT, `field_name` TEXT, `change_indicator` TEXT, `old_value_text` TEXT, `new_value_text` TEXT, `old_unit` TEXT, `new_unit` TEXT, `currency_code` TEXT, `value_type_code` TEXT
- `cdpos_long_key` — `client` TEXT, `object_class` TEXT, `object_id` TEXT, `change_number` TEXT, `table_name` TEXT, `key_fragment_no` INTEGER, `key_fragment` TEXT
- `change_object_catalog` — `object_class` TEXT, `key_domain` TEXT, `description` TEXT
- `change_object_table` — `object_class` TEXT, `table_name` TEXT, `table_role` TEXT
- `company_code` — `company_code` TEXT, `currency_code` TEXT, `timezone_name` TEXT
- `contract_header` — `contract_no` TEXT, `supplier_no` TEXT, `valid_from` TEXT, `valid_to` TEXT
- `contract_item` — `contract_no` TEXT, `item_no` INTEGER, `material_no` TEXT, `target_quantity_text` TEXT
- `cost_center` — `cost_center_code` TEXT, `company_code` TEXT, `valid_from` TEXT, `valid_to` TEXT
- `document_flow` — `predecessor_id` TEXT, `successor_id` TEXT, `relation_code` TEXT, `created_at` TEXT
- `domain_value` — `domain_name` TEXT, `technical_value` TEXT, `language_code` TEXT, `display_text` TEXT
- `field_catalog` — `table_name` TEXT, `field_name` TEXT, `data_type` TEXT, `domain_name` TEXT, `decimal_scale` INTEGER
- `goods_movement_header` — `record_key` TEXT, `document_ref` TEXT, `document_code` TEXT, `posting_date` TEXT, `posting_time` TEXT, `username` TEXT, `amount_value` REAL, `location_code` TEXT, `related_refs_json` TEXT, `transaction_ref` TEXT, `is_reversal` INT
- `goods_movement_item` — `movement_record_key` TEXT, `item_no` INTEGER, `po_number` TEXT, `po_item_no` INTEGER, `movement_type` TEXT, `quantity_text` TEXT, `reversal_of_item_no` INTEGER
- `inspection_lot` — `record_key` TEXT, `document_ref` TEXT, `document_code` TEXT, `posting_date` TEXT, `posting_time` TEXT, `username` TEXT, `amount_value` REAL, `location_code` TEXT, `related_refs_json` TEXT, `transaction_ref` TEXT, `is_reversal` INT
- `inspection_result` — `inspection_record_key` TEXT, `characteristic_no` INTEGER, `result_code` TEXT, `measured_value_text` TEXT
- `invoice_header` — `record_key` TEXT, `document_ref` TEXT, `document_code` TEXT, `posting_date` TEXT, `posting_time` TEXT, `username` TEXT, `amount_value` REAL, `location_code` TEXT, `related_refs_json` TEXT, `transaction_ref` TEXT, `is_reversal` INT
- `invoice_item` — `invoice_no` TEXT, `item_no` INTEGER, `po_number` TEXT, `po_item_no` INTEGER, `amount_text` TEXT
- `material` — `material_no` TEXT, `base_unit` TEXT, `material_group` TEXT
- `payment_item` — `payment_run_id` TEXT, `item_no` INTEGER, `accounting_document_no` TEXT, `amount_text` TEXT
- `payment_run` — `record_key` TEXT, `document_ref` TEXT, `document_code` TEXT, `posting_date` TEXT, `posting_time` TEXT, `username` TEXT, `amount_value` REAL, `location_code` TEXT, `related_refs_json` TEXT, `transaction_ref` TEXT, `is_reversal` INT
- `plant` — `plant_code` TEXT, `company_code` TEXT, `timezone_name` TEXT
- `po_header` — `po_number` TEXT, `company_code` TEXT, `supplier_no` TEXT, `release_indicator` TEXT
- `po_history` — `po_number` TEXT, `item_number` INTEGER, `follow_on_type` TEXT, `follow_on_number` TEXT, `quantity_text` TEXT
- `po_item` — `po_number` TEXT, `item_number` INTEGER, `material_no` TEXT, `quantity_text` TEXT, `price_text` TEXT, `deletion_indicator` TEXT
- `po_schedule` — `po_number` TEXT, `item_number` INTEGER, `schedule_no` INTEGER, `delivery_date_text` TEXT
- `req_header` — `record_key` TEXT, `document_ref` TEXT, `document_code` TEXT, `posting_date` TEXT, `posting_time` TEXT, `username` TEXT, `amount_value` REAL, `location_code` TEXT, `related_refs_json` TEXT, `transaction_ref` TEXT, `is_reversal` INTEGER
- `req_item` — `requisition_no` TEXT, `item_no` INTEGER, `material_no` TEXT, `quantity_text` TEXT, `deletion_indicator` TEXT
- `rfq_header` — `rfq_no` TEXT, `created_day` TEXT, `send_code` TEXT
- `rfq_item` — `rfq_no` TEXT, `item_no` INTEGER, `requisition_no` TEXT, `requisition_item_no` INTEGER, `material_no` TEXT
- `supplier` — `supplier_no` TEXT, `block_indicator` TEXT, `country_code` TEXT
- `supplier_quotation` — `quotation_no` TEXT, `supplier_no` TEXT, `revision_no` INTEGER
- `supplier_quotation_item` — `quotation_no` TEXT, `item_no` INTEGER, `rfq_no` TEXT, `rfq_item_no` INTEGER, `price_text` TEXT, `currency_code` TEXT
- `tabkey_layout` — `table_name` TEXT, `component_no` INTEGER, `field_name` TEXT, `start_pos` INTEGER, `field_length` INTEGER, `data_type` TEXT
- `transaction_code_catalog` — `transaction_code` TEXT, `functional_area` TEXT, `description` TEXT

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
