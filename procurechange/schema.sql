PRAGMA foreign_keys=ON;

CREATE TABLE cdhdr (
    client TEXT NOT NULL, object_class TEXT NOT NULL, object_id TEXT NOT NULL,
    change_number TEXT NOT NULL, username TEXT, change_date TEXT NOT NULL,
    change_time TEXT NOT NULL, transaction_code TEXT, change_indicator TEXT,
    source_system TEXT, PRIMARY KEY(client,object_class,object_id,change_number)
);
CREATE TABLE cdpos (
    client TEXT NOT NULL, object_class TEXT NOT NULL, object_id TEXT NOT NULL,
    change_number TEXT NOT NULL, table_name TEXT NOT NULL, table_key TEXT NOT NULL,
    field_name TEXT NOT NULL, change_indicator TEXT, old_value_text TEXT,
    new_value_text TEXT, old_unit TEXT, new_unit TEXT, currency_code TEXT,
    value_type_code TEXT,
    PRIMARY KEY(client,object_class,object_id,change_number,table_name,table_key,field_name)
);
CREATE TABLE archive_cdhdr AS SELECT * FROM cdhdr WHERE 0;
CREATE TABLE archive_cdpos AS SELECT * FROM cdpos WHERE 0;
CREATE TABLE cdpos_long_key (
    client TEXT NOT NULL, object_class TEXT NOT NULL, object_id TEXT NOT NULL,
    change_number TEXT NOT NULL, table_name TEXT NOT NULL, key_fragment_no INTEGER NOT NULL,
    key_fragment TEXT NOT NULL,
    PRIMARY KEY(client,object_class,object_id,change_number,table_name,key_fragment_no)
);
CREATE TABLE archive_index (archive_id TEXT PRIMARY KEY, first_change_number TEXT, last_change_number TEXT, archived_at TEXT);
CREATE TABLE tabkey_layout (table_name TEXT, component_no INTEGER, field_name TEXT, start_pos INTEGER, field_length INTEGER, data_type TEXT, PRIMARY KEY(table_name,component_no));
CREATE TABLE field_catalog (table_name TEXT, field_name TEXT, data_type TEXT, domain_name TEXT, decimal_scale INTEGER, PRIMARY KEY(table_name,field_name));
CREATE TABLE domain_value (domain_name TEXT, technical_value TEXT, language_code TEXT, display_text TEXT, PRIMARY KEY(domain_name,technical_value,language_code));
CREATE TABLE transaction_code_catalog (transaction_code TEXT PRIMARY KEY, functional_area TEXT, description TEXT);

CREATE TABLE req_header (
    record_key TEXT PRIMARY KEY, document_ref TEXT NOT NULL, document_code TEXT NOT NULL,
    posting_date TEXT NOT NULL, posting_time TEXT NOT NULL, username TEXT,
    amount_value REAL, location_code TEXT, related_refs_json TEXT NOT NULL CHECK(json_valid(related_refs_json)),
    transaction_ref TEXT, is_reversal INTEGER NOT NULL
);
CREATE TABLE goods_movement_header AS SELECT * FROM req_header WHERE 0;
CREATE TABLE inspection_lot AS SELECT * FROM req_header WHERE 0;
CREATE TABLE invoice_header AS SELECT * FROM req_header WHERE 0;
CREATE TABLE accounting_header AS SELECT * FROM req_header WHERE 0;
CREATE TABLE payment_run AS SELECT * FROM req_header WHERE 0;

CREATE TABLE document_flow (
    predecessor_id TEXT NOT NULL, successor_id TEXT NOT NULL, relation_code TEXT NOT NULL,
    created_at TEXT NOT NULL, PRIMARY KEY(predecessor_id,successor_id,relation_code)
);
CREATE TABLE approval_step (
    step_id TEXT PRIMARY KEY, workflow_id TEXT NOT NULL, step_code TEXT NOT NULL,
    status_code TEXT NOT NULL, changed_at TEXT NOT NULL, actor_code TEXT
);

-- Additional application-state tables retain current operational values.
CREATE TABLE req_item (requisition_no TEXT, item_no INTEGER, material_no TEXT, quantity_text TEXT, deletion_indicator TEXT, PRIMARY KEY(requisition_no,item_no));
CREATE TABLE rfq_header (rfq_no TEXT PRIMARY KEY, created_day TEXT, send_code TEXT);
CREATE TABLE rfq_item (rfq_no TEXT, item_no INTEGER, requisition_no TEXT, requisition_item_no INTEGER, material_no TEXT, PRIMARY KEY(rfq_no,item_no));
CREATE TABLE supplier_quotation (quotation_no TEXT PRIMARY KEY, supplier_no TEXT, revision_no INTEGER);
CREATE TABLE supplier_quotation_item (quotation_no TEXT, item_no INTEGER, rfq_no TEXT, rfq_item_no INTEGER, price_text TEXT, currency_code TEXT, PRIMARY KEY(quotation_no,item_no));
CREATE TABLE contract_header (contract_no TEXT PRIMARY KEY, supplier_no TEXT, valid_from TEXT, valid_to TEXT);
CREATE TABLE contract_item (contract_no TEXT, item_no INTEGER, material_no TEXT, target_quantity_text TEXT, PRIMARY KEY(contract_no,item_no));
CREATE TABLE po_header (po_number TEXT PRIMARY KEY, company_code TEXT, supplier_no TEXT, release_indicator TEXT);
CREATE TABLE po_item (po_number TEXT, item_number INTEGER, material_no TEXT, quantity_text TEXT, price_text TEXT, deletion_indicator TEXT, PRIMARY KEY(po_number,item_number));
CREATE TABLE po_schedule (po_number TEXT, item_number INTEGER, schedule_no INTEGER, delivery_date_text TEXT, PRIMARY KEY(po_number,item_number,schedule_no));
CREATE TABLE supplier (supplier_no TEXT PRIMARY KEY, block_indicator TEXT, country_code TEXT);
CREATE TABLE material (material_no TEXT PRIMARY KEY, base_unit TEXT, material_group TEXT);
CREATE TABLE asn_header (asn_number TEXT PRIMARY KEY, supplier_no TEXT, po_number TEXT, received_at TEXT);
CREATE TABLE asn_item (asn_number TEXT, item_no INTEGER, po_number TEXT, po_item_no INTEGER, quantity_text TEXT, PRIMARY KEY(asn_number,item_no));
CREATE TABLE goods_movement_item (movement_record_key TEXT, item_no INTEGER, po_number TEXT, po_item_no INTEGER, movement_type TEXT, quantity_text TEXT, reversal_of_item_no INTEGER, PRIMARY KEY(movement_record_key,item_no));
CREATE TABLE po_history (po_number TEXT, item_number INTEGER, follow_on_type TEXT, follow_on_number TEXT, quantity_text TEXT);
CREATE TABLE inspection_result (inspection_record_key TEXT, characteristic_no INTEGER, result_code TEXT, measured_value_text TEXT, PRIMARY KEY(inspection_record_key,characteristic_no));
CREATE TABLE invoice_item (invoice_no TEXT, item_no INTEGER, po_number TEXT, po_item_no INTEGER, amount_text TEXT, PRIMARY KEY(invoice_no,item_no));
CREATE TABLE accounting_line (accounting_record_key TEXT, line_no INTEGER, account_type TEXT, account_no TEXT, amount_text TEXT, debit_credit_code TEXT, PRIMARY KEY(accounting_record_key,line_no));
CREATE TABLE payment_item (payment_run_id TEXT, item_no INTEGER, accounting_document_no TEXT, amount_text TEXT, PRIMARY KEY(payment_run_id,item_no));
CREATE TABLE approval_workflow (workflow_id TEXT PRIMARY KEY, object_type_code TEXT, object_ref TEXT, opened_at TEXT, closed_at TEXT, state_code TEXT);
CREATE TABLE company_code (company_code TEXT PRIMARY KEY, currency_code TEXT, timezone_name TEXT);
CREATE TABLE plant (plant_code TEXT PRIMARY KEY, company_code TEXT, timezone_name TEXT);
CREATE TABLE cost_center (cost_center_code TEXT PRIMARY KEY, company_code TEXT, valid_from TEXT, valid_to TEXT);
CREATE TABLE change_object_catalog (object_class TEXT PRIMARY KEY, key_domain TEXT, description TEXT);
CREATE TABLE change_object_table (object_class TEXT, table_name TEXT, table_role TEXT, PRIMARY KEY(object_class,table_name));

CREATE INDEX idx_pc_cdpos_change ON cdpos(change_number);
CREATE INDEX idx_pc_archive_cdpos_change ON archive_cdpos(change_number);
CREATE INDEX idx_pc_flow_successor ON document_flow(successor_id);
