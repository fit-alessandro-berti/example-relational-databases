PRAGMA foreign_keys=ON;

CREATE TABLE document_conversion (
    predecessor_key TEXT NOT NULL,
    successor_key TEXT NOT NULL,
    conversion_code TEXT NOT NULL,
    valid_from TEXT NOT NULL,
    PRIMARY KEY (predecessor_key, successor_key, conversion_code)
);

CREATE TABLE commercial_document (
    record_key TEXT PRIMARY KEY,
    document_ref TEXT NOT NULL,
    related_refs_json TEXT NOT NULL CHECK(json_valid(related_refs_json)),
    state_code TEXT NOT NULL,
    operator_code TEXT,
    amount_value REAL,
    location_code TEXT,
    transaction_ref TEXT NOT NULL,
    created_day TEXT NOT NULL,
    created_clock TEXT NOT NULL
);

CREATE TABLE engineering_execution (
    record_key TEXT PRIMARY KEY,
    job_ref TEXT NOT NULL,
    related_refs_json TEXT NOT NULL CHECK(json_valid(related_refs_json)),
    phase_code TEXT NOT NULL,
    operator_code TEXT,
    amount_value REAL,
    location_code TEXT,
    transaction_ref TEXT NOT NULL,
    effective_at TEXT NOT NULL,
    recorded_at TEXT NOT NULL
);

CREATE TABLE supply_posting (
    record_key TEXT PRIMARY KEY,
    supply_ref TEXT NOT NULL,
    related_refs_json TEXT NOT NULL CHECK(json_valid(related_refs_json)),
    movement_code TEXT NOT NULL,
    operator_code TEXT,
    amount_value REAL,
    location_code TEXT,
    transaction_ref TEXT NOT NULL,
    posting_day TEXT NOT NULL,
    posting_seconds INTEGER NOT NULL
);

CREATE TABLE quality_observation (
    record_key TEXT PRIMARY KEY,
    inspection_ref TEXT NOT NULL,
    related_refs_json TEXT NOT NULL CHECK(json_valid(related_refs_json)),
    result_code TEXT NOT NULL,
    operator_code TEXT,
    amount_value REAL,
    location_code TEXT,
    transaction_ref TEXT NOT NULL,
    observed_epoch_ms INTEGER NOT NULL,
    reason_code TEXT
);

CREATE TABLE fulfilment_record (
    record_key TEXT PRIMARY KEY,
    fulfilment_ref TEXT NOT NULL,
    related_refs_json TEXT NOT NULL CHECK(json_valid(related_refs_json)),
    milestone_code TEXT NOT NULL,
    operator_code TEXT,
    amount_value REAL,
    location_code TEXT,
    transaction_ref TEXT NOT NULL,
    milestone_epoch INTEGER NOT NULL,
    timezone_code TEXT NOT NULL
);

CREATE TABLE finance_posting (
    record_key TEXT PRIMARY KEY,
    posting_ref TEXT NOT NULL,
    related_refs_json TEXT NOT NULL CHECK(json_valid(related_refs_json)),
    posting_code TEXT NOT NULL,
    operator_code TEXT,
    amount_value REAL,
    location_code TEXT,
    transaction_ref TEXT NOT NULL,
    effective_day TEXT NOT NULL,
    effective_clock TEXT NOT NULL
);

CREATE TABLE integration_outbox (
    message_id TEXT PRIMARY KEY,
    aggregate_ref TEXT NOT NULL,
    topic_code TEXT NOT NULL,
    transaction_ref TEXT NOT NULL,
    queued_at TEXT NOT NULL,
    payload_json TEXT NOT NULL CHECK(json_valid(payload_json)),
    published_flag INTEGER NOT NULL
);

-- Representative normalized master and relation tables. These hold current
-- operational state only and are intentionally not a universal history log.
CREATE TABLE customer (customer_no TEXT PRIMARY KEY, account_group TEXT, created_on TEXT);
CREATE TABLE rfq_header (rfq_no TEXT PRIMARY KEY, customer_no TEXT, created_day TEXT, status_code TEXT);
CREATE TABLE rfq_line (rfq_no TEXT, line_no INTEGER, material_no TEXT, quantity REAL, PRIMARY KEY(rfq_no,line_no));
CREATE TABLE quote_header (quote_no TEXT PRIMARY KEY, active_revision_no INTEGER, status_code TEXT);
CREATE TABLE quote_revision (quote_no TEXT, revision_no INTEGER, valid_from TEXT, status_code TEXT, PRIMARY KEY(quote_no,revision_no));
CREATE TABLE quote_line (quote_no TEXT, revision_no INTEGER, line_no INTEGER, rfq_no TEXT, rfq_line_no INTEGER, quantity REAL, PRIMARY KEY(quote_no,revision_no,line_no));
CREATE TABLE quote_approval (approval_no TEXT PRIMARY KEY, quote_no TEXT, revision_no INTEGER, decision_code TEXT, decided_at TEXT, approver_code TEXT);
CREATE TABLE sales_order (order_no TEXT PRIMARY KEY, customer_no TEXT, created_at TEXT, released_at TEXT, closed_at TEXT, status_code TEXT);
CREATE TABLE sales_order_line (order_no TEXT, line_no INTEGER, configuration_no TEXT, quantity REAL, PRIMARY KEY(order_no,line_no));
CREATE TABLE credit_assessment (assessment_no TEXT PRIMARY KEY, order_no TEXT, result_code TEXT, assessed_at TEXT, limit_amount REAL);
CREATE TABLE product_configuration (configuration_no TEXT PRIMARY KEY, product_code TEXT, frozen_at TEXT, state_code TEXT);
CREATE TABLE engineering_change (change_no TEXT PRIMARY KEY, requested_at TEXT, approved_at TEXT, implemented_at TEXT, state_code TEXT);
CREATE TABLE engineering_change_target (change_no TEXT, target_type_code TEXT, target_ref TEXT, PRIMARY KEY(change_no,target_type_code,target_ref));
CREATE TABLE bom_header (bom_no TEXT PRIMARY KEY, configuration_no TEXT, current_revision_no INTEGER);
CREATE TABLE bom_revision (bom_no TEXT, revision_no INTEGER, effective_from TEXT, effective_to TEXT, release_code TEXT, PRIMARY KEY(bom_no,revision_no));
CREATE TABLE bom_component (bom_no TEXT, revision_no INTEGER, component_no INTEGER, material_no TEXT, quantity REAL, PRIMARY KEY(bom_no,revision_no,component_no));
CREATE TABLE work_order (work_order_no TEXT PRIMARY KEY, order_no TEXT, release_code TEXT);
CREATE TABLE work_order_operation (work_order_no TEXT, operation_no INTEGER, current_state TEXT, PRIMARY KEY(work_order_no,operation_no));
CREATE TABLE operation_execution (execution_no TEXT PRIMARY KEY, work_order_no TEXT, operation_no INTEGER, attempt_no INTEGER, start_at TEXT, completion_at TEXT, result_code TEXT, superseded_flag INTEGER);
CREATE TABLE material_reservation (reservation_no TEXT PRIMARY KEY, work_order_no TEXT, material_no TEXT, requested_quantity REAL, confirmed_quantity REAL, state_code TEXT);
CREATE TABLE material_lot (lot_no TEXT PRIMARY KEY, material_no TEXT, quantity REAL, unit_code TEXT);
CREATE TABLE lot_genealogy (input_lot_no TEXT, output_lot_no TEXT, relation_code TEXT, quantity REAL, unit_code TEXT, PRIMARY KEY(input_lot_no,output_lot_no,relation_code));
CREATE TABLE inventory_movement (movement_no TEXT PRIMARY KEY, lot_no TEXT, work_order_no TEXT, movement_code TEXT, quantity REAL, transaction_ref TEXT);
CREATE TABLE production_receipt (receipt_no TEXT PRIMARY KEY, work_order_no TEXT, lot_no TEXT, quantity REAL, posting_at TEXT, transaction_ref TEXT);
CREATE TABLE serial_assignment (assignment_no TEXT PRIMARY KEY, serial_no TEXT, work_order_no TEXT, lot_no TEXT, assigned_at TEXT);
CREATE TABLE purchase_requisition (requisition_no TEXT PRIMARY KEY, created_at TEXT, requester_code TEXT, state_code TEXT);
CREATE TABLE purchase_requisition_line (requisition_no TEXT, line_no INTEGER, material_no TEXT, quantity REAL, work_order_no TEXT, PRIMARY KEY(requisition_no,line_no));
CREATE TABLE purchase_order (purchase_order_no TEXT PRIMARY KEY, supplier_no TEXT, issued_at TEXT, state_code TEXT);
CREATE TABLE purchase_order_line (purchase_order_no TEXT, line_no INTEGER, requisition_no TEXT, requisition_line_no INTEGER, material_no TEXT, quantity REAL, PRIMARY KEY(purchase_order_no,line_no));
CREATE TABLE supplier_confirmation (confirmation_no TEXT PRIMARY KEY, purchase_order_no TEXT, confirmed_at TEXT, confirmation_code TEXT);
CREATE TABLE goods_receipt (receipt_no TEXT PRIMARY KEY, purchase_order_no TEXT, posting_day TEXT);
CREATE TABLE goods_receipt_line (receipt_no TEXT, line_no INTEGER, purchase_order_no TEXT, purchase_order_line_no INTEGER, lot_no TEXT, quantity REAL, PRIMARY KEY(receipt_no,line_no));
CREATE TABLE inspection (inspection_no TEXT PRIMARY KEY, receipt_line_ref TEXT, status_code TEXT);
CREATE TABLE inspection_sample (sample_no TEXT PRIMARY KEY, inspection_no TEXT, lot_no TEXT, sample_quantity REAL);
CREATE TABLE inspection_result (result_no TEXT PRIMARY KEY, sample_no TEXT, characteristic_code TEXT, measured_value TEXT, result_code TEXT, recorded_at TEXT);
CREATE TABLE nonconformance (nonconformance_no TEXT PRIMARY KEY, inspection_no TEXT, state_code TEXT);
CREATE TABLE nonconformance_subject (nonconformance_no TEXT, subject_type_code TEXT, subject_ref TEXT, PRIMARY KEY(nonconformance_no,subject_type_code,subject_ref));
CREATE TABLE rework_order (rework_no TEXT PRIMARY KEY, nonconformance_no TEXT, state_code TEXT);
CREATE TABLE shipment (shipment_no TEXT PRIMARY KEY, planned_departure_at TEXT, actual_departure_at TEXT, transaction_ref TEXT);
CREATE TABLE shipment_allocation (shipment_no TEXT, order_no TEXT, order_line_no INTEGER, allocated_quantity REAL, PRIMARY KEY(shipment_no,order_no,order_line_no));
CREATE TABLE package (package_no TEXT PRIMARY KEY, shipment_no TEXT, sealed_at TEXT);
CREATE TABLE package_content (package_no TEXT, content_type_code TEXT, content_ref TEXT, quantity REAL, PRIMARY KEY(package_no,content_type_code,content_ref));
CREATE TABLE package_scan (scan_no TEXT PRIMARY KEY, package_no TEXT, scan_code TEXT, scan_at TEXT, transaction_ref TEXT);
CREATE TABLE delivery_confirmation (confirmation_no TEXT PRIMARY KEY, shipment_no TEXT, confirmed_at TEXT, recipient_code TEXT);
CREATE TABLE invoice (invoice_no TEXT PRIMARY KEY, issue_day TEXT, currency_code TEXT, gross_amount REAL);
CREATE TABLE invoice_line (invoice_no TEXT, line_no INTEGER, source_type_code TEXT, source_ref TEXT, amount REAL, PRIMARY KEY(invoice_no,line_no));
CREATE TABLE payment (payment_no TEXT PRIMARY KEY, value_day TEXT, amount REAL, currency_code TEXT);
CREATE TABLE payment_application (payment_no TEXT, invoice_no TEXT, applied_amount REAL, applied_at TEXT, PRIMARY KEY(payment_no,invoice_no));
CREATE TABLE warranty_registration (warranty_no TEXT PRIMARY KEY, serial_no TEXT, registered_at TEXT, coverage_code TEXT);
CREATE TABLE supplier (supplier_no TEXT PRIMARY KEY, supplier_group TEXT, country_code TEXT);

CREATE INDEX idx_document_conversion_successor ON document_conversion(successor_key);
CREATE INDEX idx_ff_commercial_state ON commercial_document(state_code);
CREATE INDEX idx_ff_engineering_phase ON engineering_execution(phase_code);
CREATE INDEX idx_ff_supply_movement ON supply_posting(movement_code);
