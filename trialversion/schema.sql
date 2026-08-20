PRAGMA foreign_keys=ON;

CREATE TABLE study_v (
    record_id TEXT PRIMARY KEY,
    logical_id TEXT NOT NULL,
    version_no INTEGER NOT NULL,
    valid_from TEXT NOT NULL,
    valid_to TEXT,
    recorded_at TEXT NOT NULL,
    edit_session_id TEXT NOT NULL,
    supersedes_version_no INTEGER,
    change_kind TEXT NOT NULL CHECK(change_kind IN ('BUSINESS','CORRECTION','IMPORT_REPLAY','SYSTEM_RECALCULATION')),
    change_reason_code TEXT,
    changed_by TEXT,
    is_current INTEGER NOT NULL,
    is_deleted INTEGER NOT NULL,
    row_hash TEXT NOT NULL,
    state_code TEXT NOT NULL,
    related_refs_json TEXT NOT NULL CHECK(json_valid(related_refs_json)),
    actor_code TEXT,
    amount_value REAL,
    location_code TEXT,
    payload_json TEXT NOT NULL CHECK(json_valid(payload_json))
);
CREATE TABLE protocol_v AS SELECT * FROM study_v WHERE 0;
CREATE TABLE site_v AS SELECT * FROM study_v WHERE 0;
CREATE TABLE investigator_v AS SELECT * FROM study_v WHERE 0;
CREATE TABLE participant_v AS SELECT * FROM study_v WHERE 0;
CREATE TABLE consent_v AS SELECT * FROM study_v WHERE 0;
CREATE TABLE visit_v AS SELECT * FROM study_v WHERE 0;
CREATE TABLE drug_kit_v AS SELECT * FROM study_v WHERE 0;
CREATE TABLE dispensation_v AS SELECT * FROM study_v WHERE 0;
CREATE TABLE dose_v AS SELECT * FROM study_v WHERE 0;
CREATE TABLE sample_v AS SELECT * FROM study_v WHERE 0;
CREATE TABLE aliquot_v AS SELECT * FROM study_v WHERE 0;
CREATE TABLE sample_shipment_v AS SELECT * FROM study_v WHERE 0;
CREATE TABLE shipment_item_v AS SELECT * FROM study_v WHERE 0;
CREATE TABLE lab_order_v AS SELECT * FROM study_v WHERE 0;
CREATE TABLE lab_test_v AS SELECT * FROM study_v WHERE 0;
CREATE TABLE lab_result_v AS SELECT * FROM study_v WHERE 0;
CREATE TABLE adverse_event_v AS SELECT * FROM study_v WHERE 0;
CREATE TABLE protocol_deviation_v AS SELECT * FROM study_v WHERE 0;
CREATE TABLE data_query_v AS SELECT * FROM study_v WHERE 0;

CREATE TABLE object_relation_v (
    relation_id TEXT PRIMARY KEY,
    source_type TEXT NOT NULL,
    source_logical_id TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_logical_id TEXT NOT NULL,
    qualifier_code TEXT NOT NULL,
    valid_from TEXT NOT NULL,
    valid_to TEXT,
    recorded_at TEXT NOT NULL,
    edit_session_id TEXT NOT NULL,
    change_kind TEXT NOT NULL
);
CREATE TABLE edit_session (
    edit_session_id TEXT PRIMARY KEY,
    edited_by TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    session_kind TEXT NOT NULL,
    reason_code TEXT
);
CREATE TABLE site_timezone (site_logical_id TEXT, valid_from TEXT, valid_to TEXT, timezone_name TEXT, PRIMARY KEY(site_logical_id,valid_from));
CREATE TABLE code_dictionary (domain_code TEXT, value_code TEXT, language_code TEXT, display_text TEXT, PRIMARY KEY(domain_code,value_code,language_code));

CREATE INDEX idx_tv_study_logical ON study_v(logical_id,version_no);
CREATE INDEX idx_tv_protocol_logical ON protocol_v(logical_id,version_no);
CREATE INDEX idx_tv_site_logical ON site_v(logical_id,version_no);
CREATE INDEX idx_tv_participant_logical ON participant_v(logical_id,version_no);
CREATE INDEX idx_tv_visit_logical ON visit_v(logical_id,version_no);
CREATE INDEX idx_tv_relation_source ON object_relation_v(source_logical_id,valid_from);

