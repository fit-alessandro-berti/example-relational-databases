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

## Tables and fields

The following tables and columns are present in `source.sqlite`:

- `bom_component` — `bom_no` TEXT, `revision_no` INTEGER, `component_no` INTEGER, `material_no` TEXT, `quantity` REAL
- `bom_header` — `bom_no` TEXT, `configuration_no` TEXT, `current_revision_no` INTEGER
- `bom_revision` — `bom_no` TEXT, `revision_no` INTEGER, `effective_from` TEXT, `effective_to` TEXT, `release_code` TEXT
- `commercial_document` — `record_key` TEXT, `document_ref` TEXT, `related_refs_json` TEXT, `state_code` TEXT, `operator_code` TEXT, `amount_value` REAL, `location_code` TEXT, `transaction_ref` TEXT, `created_day` TEXT, `created_clock` TEXT
- `credit_assessment` — `assessment_no` TEXT, `order_no` TEXT, `result_code` TEXT, `assessed_at` TEXT, `limit_amount` REAL
- `customer` — `customer_no` TEXT, `account_group` TEXT, `created_on` TEXT
- `delivery_confirmation` — `confirmation_no` TEXT, `shipment_no` TEXT, `confirmed_at` TEXT, `recipient_code` TEXT
- `document_conversion` — `predecessor_key` TEXT, `successor_key` TEXT, `conversion_code` TEXT, `valid_from` TEXT
- `engineering_change` — `change_no` TEXT, `requested_at` TEXT, `approved_at` TEXT, `implemented_at` TEXT, `state_code` TEXT
- `engineering_change_target` — `change_no` TEXT, `target_type_code` TEXT, `target_ref` TEXT
- `engineering_execution` — `record_key` TEXT, `job_ref` TEXT, `related_refs_json` TEXT, `phase_code` TEXT, `operator_code` TEXT, `amount_value` REAL, `location_code` TEXT, `transaction_ref` TEXT, `effective_at` TEXT, `recorded_at` TEXT
- `finance_posting` — `record_key` TEXT, `posting_ref` TEXT, `related_refs_json` TEXT, `posting_code` TEXT, `operator_code` TEXT, `amount_value` REAL, `location_code` TEXT, `transaction_ref` TEXT, `effective_day` TEXT, `effective_clock` TEXT
- `fulfilment_record` — `record_key` TEXT, `fulfilment_ref` TEXT, `related_refs_json` TEXT, `milestone_code` TEXT, `operator_code` TEXT, `amount_value` REAL, `location_code` TEXT, `transaction_ref` TEXT, `milestone_epoch` INTEGER, `timezone_code` TEXT
- `goods_receipt` — `receipt_no` TEXT, `purchase_order_no` TEXT, `posting_day` TEXT
- `goods_receipt_line` — `receipt_no` TEXT, `line_no` INTEGER, `purchase_order_no` TEXT, `purchase_order_line_no` INTEGER, `lot_no` TEXT, `quantity` REAL
- `inspection` — `inspection_no` TEXT, `receipt_line_ref` TEXT, `status_code` TEXT
- `inspection_result` — `result_no` TEXT, `sample_no` TEXT, `characteristic_code` TEXT, `measured_value` TEXT, `result_code` TEXT, `recorded_at` TEXT
- `inspection_sample` — `sample_no` TEXT, `inspection_no` TEXT, `lot_no` TEXT, `sample_quantity` REAL
- `integration_outbox` — `message_id` TEXT, `aggregate_ref` TEXT, `topic_code` TEXT, `transaction_ref` TEXT, `queued_at` TEXT, `payload_json` TEXT, `published_flag` INTEGER
- `inventory_movement` — `movement_no` TEXT, `lot_no` TEXT, `work_order_no` TEXT, `movement_code` TEXT, `quantity` REAL, `transaction_ref` TEXT
- `invoice` — `invoice_no` TEXT, `issue_day` TEXT, `currency_code` TEXT, `gross_amount` REAL
- `invoice_line` — `invoice_no` TEXT, `line_no` INTEGER, `source_type_code` TEXT, `source_ref` TEXT, `amount` REAL
- `lot_genealogy` — `input_lot_no` TEXT, `output_lot_no` TEXT, `relation_code` TEXT, `quantity` REAL, `unit_code` TEXT
- `material_lot` — `lot_no` TEXT, `material_no` TEXT, `quantity` REAL, `unit_code` TEXT
- `material_reservation` — `reservation_no` TEXT, `work_order_no` TEXT, `material_no` TEXT, `requested_quantity` REAL, `confirmed_quantity` REAL, `state_code` TEXT
- `nonconformance` — `nonconformance_no` TEXT, `inspection_no` TEXT, `state_code` TEXT
- `nonconformance_subject` — `nonconformance_no` TEXT, `subject_type_code` TEXT, `subject_ref` TEXT
- `operation_execution` — `execution_no` TEXT, `work_order_no` TEXT, `operation_no` INTEGER, `attempt_no` INTEGER, `start_at` TEXT, `completion_at` TEXT, `result_code` TEXT, `superseded_flag` INTEGER
- `package` — `package_no` TEXT, `shipment_no` TEXT, `sealed_at` TEXT
- `package_content` — `package_no` TEXT, `content_type_code` TEXT, `content_ref` TEXT, `quantity` REAL
- `package_scan` — `scan_no` TEXT, `package_no` TEXT, `scan_code` TEXT, `scan_at` TEXT, `transaction_ref` TEXT
- `payment` — `payment_no` TEXT, `value_day` TEXT, `amount` REAL, `currency_code` TEXT
- `payment_application` — `payment_no` TEXT, `invoice_no` TEXT, `applied_amount` REAL, `applied_at` TEXT
- `product_configuration` — `configuration_no` TEXT, `product_code` TEXT, `frozen_at` TEXT, `state_code` TEXT
- `production_receipt` — `receipt_no` TEXT, `work_order_no` TEXT, `lot_no` TEXT, `quantity` REAL, `posting_at` TEXT, `transaction_ref` TEXT
- `purchase_order` — `purchase_order_no` TEXT, `supplier_no` TEXT, `issued_at` TEXT, `state_code` TEXT
- `purchase_order_line` — `purchase_order_no` TEXT, `line_no` INTEGER, `requisition_no` TEXT, `requisition_line_no` INTEGER, `material_no` TEXT, `quantity` REAL
- `purchase_requisition` — `requisition_no` TEXT, `created_at` TEXT, `requester_code` TEXT, `state_code` TEXT
- `purchase_requisition_line` — `requisition_no` TEXT, `line_no` INTEGER, `material_no` TEXT, `quantity` REAL, `work_order_no` TEXT
- `quality_observation` — `record_key` TEXT, `inspection_ref` TEXT, `related_refs_json` TEXT, `result_code` TEXT, `operator_code` TEXT, `amount_value` REAL, `location_code` TEXT, `transaction_ref` TEXT, `observed_epoch_ms` INTEGER, `reason_code` TEXT
- `quote_approval` — `approval_no` TEXT, `quote_no` TEXT, `revision_no` INTEGER, `decision_code` TEXT, `decided_at` TEXT, `approver_code` TEXT
- `quote_header` — `quote_no` TEXT, `active_revision_no` INTEGER, `status_code` TEXT
- `quote_line` — `quote_no` TEXT, `revision_no` INTEGER, `line_no` INTEGER, `rfq_no` TEXT, `rfq_line_no` INTEGER, `quantity` REAL
- `quote_revision` — `quote_no` TEXT, `revision_no` INTEGER, `valid_from` TEXT, `status_code` TEXT
- `rework_order` — `rework_no` TEXT, `nonconformance_no` TEXT, `state_code` TEXT
- `rfq_header` — `rfq_no` TEXT, `customer_no` TEXT, `created_day` TEXT, `status_code` TEXT
- `rfq_line` — `rfq_no` TEXT, `line_no` INTEGER, `material_no` TEXT, `quantity` REAL
- `sales_order` — `order_no` TEXT, `customer_no` TEXT, `created_at` TEXT, `released_at` TEXT, `closed_at` TEXT, `status_code` TEXT
- `sales_order_line` — `order_no` TEXT, `line_no` INTEGER, `configuration_no` TEXT, `quantity` REAL
- `serial_assignment` — `assignment_no` TEXT, `serial_no` TEXT, `work_order_no` TEXT, `lot_no` TEXT, `assigned_at` TEXT
- `shipment` — `shipment_no` TEXT, `planned_departure_at` TEXT, `actual_departure_at` TEXT, `transaction_ref` TEXT
- `shipment_allocation` — `shipment_no` TEXT, `order_no` TEXT, `order_line_no` INTEGER, `allocated_quantity` REAL
- `supplier` — `supplier_no` TEXT, `supplier_group` TEXT, `country_code` TEXT
- `supplier_confirmation` — `confirmation_no` TEXT, `purchase_order_no` TEXT, `confirmed_at` TEXT, `confirmation_code` TEXT
- `supply_posting` — `record_key` TEXT, `supply_ref` TEXT, `related_refs_json` TEXT, `movement_code` TEXT, `operator_code` TEXT, `amount_value` REAL, `location_code` TEXT, `transaction_ref` TEXT, `posting_day` TEXT, `posting_seconds` INTEGER
- `warranty_registration` — `warranty_no` TEXT, `serial_no` TEXT, `registered_at` TEXT, `coverage_code` TEXT
- `work_order` — `work_order_no` TEXT, `order_no` TEXT, `release_code` TEXT
- `work_order_operation` — `work_order_no` TEXT, `operation_no` INTEGER, `current_state` TEXT

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
