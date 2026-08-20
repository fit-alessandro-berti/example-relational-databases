PRAGMA foreign_keys=ON;

CREATE TABLE hub_cell_batch (hub_key TEXT PRIMARY KEY, business_key TEXT NOT NULL, load_dts TEXT NOT NULL, record_source TEXT NOT NULL);
CREATE TABLE hub_module AS SELECT * FROM hub_cell_batch WHERE 0;
CREATE TABLE hub_battery_pack AS SELECT * FROM hub_cell_batch WHERE 0;
CREATE TABLE hub_passport AS SELECT * FROM hub_cell_batch WHERE 0;
CREATE TABLE hub_vehicle AS SELECT * FROM hub_cell_batch WHERE 0;
CREATE TABLE hub_party AS SELECT * FROM hub_cell_batch WHERE 0;
CREATE TABLE hub_service_order AS SELECT * FROM hub_cell_batch WHERE 0;
CREATE TABLE hub_diagnostic AS SELECT * FROM hub_cell_batch WHERE 0;
CREATE TABLE hub_firmware_campaign AS SELECT * FROM hub_cell_batch WHERE 0;
CREATE TABLE hub_warranty_claim AS SELECT * FROM hub_cell_batch WHERE 0;
CREATE TABLE hub_recall_campaign AS SELECT * FROM hub_cell_batch WHERE 0;
CREATE TABLE hub_shipment AS SELECT * FROM hub_cell_batch WHERE 0;
CREATE TABLE hub_warehouse AS SELECT * FROM hub_cell_batch WHERE 0;
CREATE TABLE hub_second_life_system AS SELECT * FROM hub_cell_batch WHERE 0;
CREATE TABLE hub_recycling_order AS SELECT * FROM hub_cell_batch WHERE 0;
CREATE TABLE hub_material_batch AS SELECT * FROM hub_cell_batch WHERE 0;
CREATE TABLE hub_certificate AS SELECT * FROM hub_cell_batch WHERE 0;
CREATE TABLE hub_incident AS SELECT * FROM hub_cell_batch WHERE 0;

CREATE TABLE sat_cell_batch_status (
    satellite_id TEXT PRIMARY KEY, parent_key TEXT NOT NULL, load_dts TEXT NOT NULL,
    effective_from TEXT NOT NULL, effective_to TEXT, hashdiff TEXT NOT NULL,
    record_source TEXT NOT NULL, source_sequence INTEGER NOT NULL, is_correction INTEGER NOT NULL,
    state_code TEXT NOT NULL, related_refs_json TEXT NOT NULL CHECK(json_valid(related_refs_json)),
    actor_code TEXT, amount_value REAL, location_code TEXT
);
CREATE TABLE sat_module_status AS SELECT * FROM sat_cell_batch_status WHERE 0;
CREATE TABLE sat_pack_status AS SELECT * FROM sat_cell_batch_status WHERE 0;
CREATE TABLE sat_pack_specification AS SELECT * FROM sat_cell_batch_status WHERE 0;
CREATE TABLE sat_pack_test AS SELECT * FROM sat_cell_batch_status WHERE 0;
CREATE TABLE sat_passport_data AS SELECT * FROM sat_cell_batch_status WHERE 0;
CREATE TABLE sat_vehicle_status AS SELECT * FROM sat_cell_batch_status WHERE 0;
CREATE TABLE sat_ownership_role AS SELECT * FROM sat_cell_batch_status WHERE 0;
CREATE TABLE sat_telemetry_summary AS SELECT * FROM sat_cell_batch_status WHERE 0;
CREATE TABLE sat_diagnostic_result AS SELECT * FROM sat_cell_batch_status WHERE 0;
CREATE TABLE sat_service_status AS SELECT * FROM sat_cell_batch_status WHERE 0;
CREATE TABLE sat_campaign_status AS SELECT * FROM sat_cell_batch_status WHERE 0;
CREATE TABLE sat_claim_status AS SELECT * FROM sat_cell_batch_status WHERE 0;
CREATE TABLE sat_recall_status AS SELECT * FROM sat_cell_batch_status WHERE 0;
CREATE TABLE sat_shipment_status AS SELECT * FROM sat_cell_batch_status WHERE 0;
CREATE TABLE sat_second_life_status AS SELECT * FROM sat_cell_batch_status WHERE 0;
CREATE TABLE sat_recycling_status AS SELECT * FROM sat_cell_batch_status WHERE 0;
CREATE TABLE sat_certificate_status AS SELECT * FROM sat_cell_batch_status WHERE 0;
CREATE TABLE sat_incident_status AS SELECT * FROM sat_cell_batch_status WHERE 0;

CREATE TABLE asset_journal (
    journal_id TEXT PRIMARY KEY, movement_code TEXT NOT NULL, effective_at TEXT NOT NULL,
    posted_at TEXT NOT NULL, source_system TEXT NOT NULL, status_code TEXT NOT NULL,
    related_refs_json TEXT NOT NULL CHECK(json_valid(related_refs_json)), actor_code TEXT,
    location_code TEXT, amount_value REAL
);
CREATE TABLE asset_ledger_entry (
    entry_id TEXT PRIMARY KEY, journal_id TEXT NOT NULL, account_type TEXT NOT NULL,
    account_id TEXT NOT NULL, asset_type TEXT NOT NULL, asset_hub_key TEXT NOT NULL,
    direction TEXT NOT NULL CHECK(direction IN ('DEBIT','CREDIT')), quantity REAL NOT NULL,
    effective_at TEXT NOT NULL, posted_at TEXT NOT NULL, reversal_of_entry_id TEXT,
    source_system TEXT NOT NULL
);
CREATE TABLE ledger_account (account_type TEXT, account_id TEXT, valid_from TEXT, valid_to TEXT, PRIMARY KEY(account_type,account_id,valid_from));
CREATE TABLE ledger_reversal (reversal_journal_id TEXT PRIMARY KEY, original_journal_id TEXT NOT NULL, reason_code TEXT, reversed_at TEXT);

CREATE TABLE link_module_cell_batch (link_key TEXT PRIMARY KEY, module_hub_key TEXT, cell_batch_hub_key TEXT, load_dts TEXT, record_source TEXT);
CREATE TABLE link_pack_module (link_key TEXT PRIMARY KEY, pack_hub_key TEXT, module_hub_key TEXT, load_dts TEXT, record_source TEXT);
CREATE TABLE link_pack_passport (link_key TEXT PRIMARY KEY, pack_hub_key TEXT, passport_hub_key TEXT, load_dts TEXT, record_source TEXT);
CREATE TABLE link_vehicle_pack (link_key TEXT PRIMARY KEY, vehicle_hub_key TEXT, pack_hub_key TEXT, load_dts TEXT, record_source TEXT);
CREATE TABLE link_pack_owner (link_key TEXT PRIMARY KEY, pack_hub_key TEXT, owner_hub_key TEXT, load_dts TEXT, record_source TEXT);
CREATE TABLE link_pack_service (link_key TEXT PRIMARY KEY, pack_hub_key TEXT, service_hub_key TEXT, load_dts TEXT, record_source TEXT);
CREATE TABLE link_pack_diagnostic (link_key TEXT PRIMARY KEY, pack_hub_key TEXT, diagnostic_hub_key TEXT, load_dts TEXT, record_source TEXT);
CREATE TABLE link_pack_firmware_campaign (link_key TEXT PRIMARY KEY, pack_hub_key TEXT, campaign_hub_key TEXT, load_dts TEXT, record_source TEXT);
CREATE TABLE link_pack_warranty_claim (link_key TEXT PRIMARY KEY, pack_hub_key TEXT, claim_hub_key TEXT, load_dts TEXT, record_source TEXT);
CREATE TABLE link_pack_recall (link_key TEXT PRIMARY KEY, pack_hub_key TEXT, recall_hub_key TEXT, load_dts TEXT, record_source TEXT);
CREATE TABLE link_pack_shipment (link_key TEXT PRIMARY KEY, pack_hub_key TEXT, shipment_hub_key TEXT, load_dts TEXT, record_source TEXT);
CREATE TABLE link_shipment_warehouse (link_key TEXT PRIMARY KEY, shipment_hub_key TEXT, warehouse_hub_key TEXT, qualifier_code TEXT, load_dts TEXT, record_source TEXT);
CREATE TABLE link_pack_second_life (link_key TEXT PRIMARY KEY, pack_hub_key TEXT, second_life_hub_key TEXT, load_dts TEXT, record_source TEXT);
CREATE TABLE link_pack_recycling_order (link_key TEXT PRIMARY KEY, pack_hub_key TEXT, recycling_hub_key TEXT, load_dts TEXT, record_source TEXT);
CREATE TABLE link_recycling_material_batch (link_key TEXT PRIMARY KEY, recycling_hub_key TEXT, material_hub_key TEXT, load_dts TEXT, record_source TEXT);
CREATE TABLE link_certificate_subject (link_key TEXT PRIMARY KEY, certificate_hub_key TEXT, subject_hub_key TEXT, subject_type TEXT, load_dts TEXT, record_source TEXT);
CREATE TABLE link_incident_subject (link_key TEXT PRIMARY KEY, incident_hub_key TEXT, subject_hub_key TEXT, subject_type TEXT, load_dts TEXT, record_source TEXT);
CREATE TABLE link_effectivity (link_key TEXT, load_dts TEXT, effective_from TEXT, effective_to TEXT, is_active INTEGER, record_source TEXT, PRIMARY KEY(link_key,load_dts));

CREATE TABLE business_key_crosswalk (source_system TEXT, source_identifier TEXT, canonical_hub_key TEXT, effective_from TEXT, effective_to TEXT, PRIMARY KEY(source_system,source_identifier,effective_from));
CREATE TABLE retired_identifier (identifier TEXT, hub_key TEXT, retired_at TEXT, reason_code TEXT, PRIMARY KEY(identifier,retired_at));
CREATE TABLE source_precedence (attribute_domain TEXT, record_source TEXT, priority_no INTEGER, valid_from TEXT, valid_to TEXT, PRIMARY KEY(attribute_domain,record_source,valid_from));
CREATE TABLE record_source_catalog (record_source TEXT PRIMARY KEY, source_kind TEXT, timezone_name TEXT);

CREATE INDEX idx_bv_sat_pack_effective ON sat_pack_status(parent_key,effective_from,load_dts);
CREATE INDEX idx_bv_ledger_journal ON asset_ledger_entry(journal_id);
