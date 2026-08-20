PRAGMA foreign_keys=ON;

CREATE TABLE event_store (
    global_position INTEGER PRIMARY KEY,
    stream_id TEXT NOT NULL,
    stream_type TEXT NOT NULL,
    stream_version INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    schema_version INTEGER NOT NULL,
    occurred_at TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    payload_json TEXT NOT NULL CHECK(json_valid(payload_json)),
    metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)),
    correlation_id TEXT,
    causation_id TEXT,
    tenant_id TEXT NOT NULL,
    is_redacted INTEGER NOT NULL,
    UNIQUE(stream_id,stream_version)
);
CREATE TABLE event_type_alias (
    event_type TEXT NOT NULL,
    schema_version INTEGER NOT NULL,
    semantic_code TEXT NOT NULL,
    PRIMARY KEY(event_type,schema_version)
);
CREATE TABLE schema_upcaster_rule (
    event_type TEXT, from_version INTEGER, to_version INTEGER,
    rule_json TEXT NOT NULL CHECK(json_valid(rule_json)),
    PRIMARY KEY(event_type,from_version,to_version)
);
CREATE TABLE command_result (
    result_id TEXT PRIMARY KEY, stream_id TEXT NOT NULL, event_type TEXT NOT NULL,
    semantic_code TEXT NOT NULL, result_code TEXT NOT NULL, occurred_at TEXT NOT NULL,
    recorded_at TEXT NOT NULL, payload_json TEXT NOT NULL CHECK(json_valid(payload_json)),
    correlation_id TEXT, actor_code TEXT
);
CREATE TABLE inbox_message (
    message_id TEXT PRIMARY KEY, sender_ref TEXT, event_type TEXT NOT NULL,
    semantic_code TEXT NOT NULL, occurred_at TEXT NOT NULL, recorded_at TEXT NOT NULL,
    payload_json TEXT NOT NULL CHECK(json_valid(payload_json)), correlation_id TEXT,
    processed_flag INTEGER NOT NULL
);
CREATE TABLE document_index (
    document_id TEXT PRIMARY KEY, stream_id TEXT NOT NULL, event_type TEXT NOT NULL,
    semantic_code TEXT NOT NULL, effective_at TEXT NOT NULL, indexed_at TEXT NOT NULL,
    payload_json TEXT NOT NULL CHECK(json_valid(payload_json)), correlation_id TEXT,
    index_status TEXT NOT NULL
);
CREATE TABLE snapshot_store (stream_id TEXT, stream_version INTEGER, snapshot_type TEXT, snapshot_json TEXT, written_at TEXT, PRIMARY KEY(stream_id,stream_version));
CREATE TABLE command_log (command_id TEXT PRIMARY KEY, stream_id TEXT, command_type TEXT, accepted_at TEXT, payload_json TEXT);
CREATE TABLE outbox_message (message_id TEXT PRIMARY KEY, correlation_id TEXT, topic_code TEXT, payload_json TEXT, queued_at TEXT, sent_at TEXT);
CREATE TABLE projection_checkpoint (projection_name TEXT PRIMARY KEY, global_position INTEGER, updated_at TEXT);
CREATE TABLE claim_projection (claim_ref TEXT PRIMARY KEY, current_state_code TEXT, last_global_position INTEGER, projection_json TEXT);
CREATE TABLE exposure_projection (exposure_ref TEXT PRIMARY KEY, claim_ref TEXT, current_state_code TEXT, last_global_position INTEGER);
CREATE TABLE payment_projection (payment_ref TEXT PRIMARY KEY, claim_ref TEXT, current_state_code TEXT, amount_value REAL);
CREATE TABLE repair_projection (repair_ref TEXT PRIMARY KEY, claim_ref TEXT, current_state_code TEXT);
CREATE TABLE party_projection (party_ref TEXT PRIMARY KEY, masked_identity TEXT, current_role_code TEXT);
CREATE TABLE saga_state (saga_id TEXT PRIMARY KEY, correlation_id TEXT, state_code TEXT, payload_json TEXT, checkpoint_at TEXT);
CREATE TABLE stream_alias (alias_id TEXT, canonical_stream_id TEXT, valid_from TEXT, valid_to TEXT, PRIMARY KEY(alias_id,valid_from));
CREATE TABLE redacted_identity_map (redacted_ref TEXT PRIMARY KEY, stable_party_ref TEXT NOT NULL, redacted_at TEXT NOT NULL);

CREATE INDEX idx_cs_event_corr ON event_store(correlation_id,event_type);
CREATE INDEX idx_cs_event_stream ON event_store(stream_id,stream_version);

