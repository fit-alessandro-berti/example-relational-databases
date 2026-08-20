PRAGMA foreign_keys=ON;

CREATE TABLE wf_deployment (deployment_id TEXT PRIMARY KEY, deployed_at TEXT, resource_hash TEXT);
CREATE TABLE wf_process_definition (process_definition_id TEXT PRIMARY KEY, definition_key TEXT NOT NULL, version_no INTEGER NOT NULL, deployment_id TEXT NOT NULL);
CREATE TABLE wf_process_instance (
    process_instance_id TEXT PRIMARY KEY, process_definition_id TEXT NOT NULL,
    root_process_instance_id TEXT NOT NULL, super_process_instance_id TEXT,
    start_time TEXT NOT NULL, end_time TEXT, state_code TEXT NOT NULL
);
CREATE TABLE wf_execution (
    execution_id TEXT PRIMARY KEY, parent_execution_id TEXT, process_instance_id TEXT NOT NULL,
    root_process_instance_id TEXT NOT NULL, super_process_instance_id TEXT,
    activity_id TEXT, is_scope INTEGER NOT NULL, is_concurrent INTEGER NOT NULL,
    created_at TEXT NOT NULL, ended_at TEXT, delete_reason TEXT
);
CREATE TABLE wf_definition_metadata (
    process_definition_id TEXT NOT NULL, activity_id TEXT NOT NULL,
    semantic_code TEXT NOT NULL, semantic_role TEXT NOT NULL,
    PRIMARY KEY(process_definition_id,activity_id)
);
CREATE TABLE wf_variable_history (
    variable_id TEXT PRIMARY KEY, execution_id TEXT NOT NULL, process_instance_id TEXT NOT NULL,
    name TEXT NOT NULL, revision_no INTEGER NOT NULL, value_text TEXT,
    value_type TEXT NOT NULL, created_at TEXT NOT NULL, ended_at TEXT
);

CREATE TABLE wf_activity_history (
    history_id TEXT PRIMARY KEY, execution_id TEXT NOT NULL, process_instance_id TEXT NOT NULL,
    process_definition_id TEXT NOT NULL, activity_id TEXT NOT NULL, actor_code TEXT,
    related_refs_json TEXT NOT NULL CHECK(json_valid(related_refs_json)), amount_value REAL,
    location_code TEXT, transaction_ref TEXT, start_time TEXT, end_time TEXT, lifecycle_code TEXT
);
CREATE TABLE wf_task_history (
    task_id TEXT PRIMARY KEY, execution_id TEXT NOT NULL, process_instance_id TEXT NOT NULL,
    process_definition_id TEXT NOT NULL, activity_id TEXT NOT NULL, assignee_code TEXT,
    related_refs_json TEXT NOT NULL CHECK(json_valid(related_refs_json)), amount_value REAL,
    location_code TEXT, transaction_ref TEXT, start_time TEXT, end_time TEXT,
    outcome_code TEXT, delete_reason TEXT
);
CREATE TABLE wf_message_delivery (
    delivery_id TEXT PRIMARY KEY, execution_id TEXT NOT NULL, process_instance_id TEXT NOT NULL,
    process_definition_id TEXT NOT NULL, activity_id TEXT NOT NULL, actor_code TEXT,
    related_refs_json TEXT NOT NULL CHECK(json_valid(related_refs_json)), amount_value REAL,
    location_code TEXT, transaction_ref TEXT, delivered_at TEXT, message_code TEXT, result_code TEXT
);
CREATE TABLE wf_form_submission (
    submission_id TEXT PRIMARY KEY, execution_id TEXT NOT NULL, process_instance_id TEXT NOT NULL,
    process_definition_id TEXT NOT NULL, activity_id TEXT NOT NULL, submitted_by TEXT,
    related_refs_json TEXT NOT NULL CHECK(json_valid(related_refs_json)), amount_value REAL,
    location_code TEXT, transaction_ref TEXT, submitted_at TEXT, form_key TEXT, payload_json TEXT
);
CREATE TABLE wf_external_task (
    external_task_id TEXT PRIMARY KEY, execution_id TEXT NOT NULL, process_instance_id TEXT NOT NULL,
    process_definition_id TEXT NOT NULL, activity_id TEXT NOT NULL, worker_code TEXT,
    related_refs_json TEXT NOT NULL CHECK(json_valid(related_refs_json)), amount_value REAL,
    location_code TEXT, transaction_ref TEXT, completed_at TEXT, state_code TEXT, error_code TEXT
);
CREATE TABLE wf_job_log (job_log_id TEXT PRIMARY KEY, process_instance_id TEXT, job_type TEXT, retry_no INTEGER, created_at TEXT, ended_at TEXT, result_code TEXT);
CREATE TABLE wf_incident (incident_id TEXT PRIMARY KEY, process_instance_id TEXT, execution_id TEXT, incident_type TEXT, created_at TEXT, resolved_at TEXT);
CREATE TABLE wf_process_migration (migration_id TEXT PRIMARY KEY, process_instance_id TEXT, source_definition_id TEXT, target_definition_id TEXT, migrated_at TEXT);
CREATE TABLE wf_activity_migration_map (migration_id TEXT, source_activity_id TEXT, target_activity_id TEXT, PRIMARY KEY(migration_id,source_activity_id));
CREATE TABLE wf_message_subscription (subscription_id TEXT PRIMARY KEY, execution_id TEXT, message_code TEXT, created_at TEXT, ended_at TEXT);
CREATE TABLE wf_identity_link (identity_link_id TEXT PRIMARY KEY, task_id TEXT, user_code TEXT, group_code TEXT, link_type TEXT);

-- Domain projections are updated by workflow transactions but are not used as
-- a complete activity history.
CREATE TABLE permit_application (application_ref TEXT PRIMARY KEY, current_state_code TEXT, submitted_at TEXT, updated_at TEXT);
CREATE TABLE applicant (applicant_ref TEXT PRIMARY KEY, identity_token TEXT, party_kind TEXT);
CREATE TABLE application_party (application_ref TEXT, applicant_ref TEXT, role_code TEXT, valid_from TEXT, valid_to TEXT);
CREATE TABLE parcel (parcel_ref TEXT PRIMARY KEY, cadastral_code TEXT, municipality_code TEXT);
CREATE TABLE property (property_ref TEXT PRIMARY KEY, parcel_ref TEXT, use_code TEXT);
CREATE TABLE application_parcel (application_ref TEXT, parcel_ref TEXT, valid_from TEXT, valid_to TEXT);
CREATE TABLE plan_revision (plan_revision_ref TEXT PRIMARY KEY, application_ref TEXT, revision_no INTEGER, current_state_code TEXT);
CREATE TABLE document (document_ref TEXT PRIMARY KEY, content_hash TEXT, document_type_code TEXT);
CREATE TABLE document_link (document_ref TEXT, subject_type_code TEXT, subject_ref TEXT, valid_from TEXT, valid_to TEXT, PRIMARY KEY(document_ref,subject_type_code,subject_ref,valid_from));
CREATE TABLE review (review_ref TEXT PRIMARY KEY, application_ref TEXT, review_type_code TEXT, current_state_code TEXT);
CREATE TABLE review_assignment (review_ref TEXT, agency_ref TEXT, reviewer_code TEXT, valid_from TEXT, valid_to TEXT, PRIMARY KEY(review_ref,agency_ref,valid_from));
CREATE TABLE agency (agency_ref TEXT PRIMARY KEY, agency_type_code TEXT);
CREATE TABLE fee_invoice (fee_invoice_ref TEXT PRIMARY KEY, application_ref TEXT, amount_value REAL, state_code TEXT);
CREATE TABLE payment (payment_ref TEXT PRIMARY KEY, fee_invoice_ref TEXT, amount_value REAL, state_code TEXT);
CREATE TABLE permit (permit_ref TEXT PRIMARY KEY, application_ref TEXT, state_code TEXT);
CREATE TABLE permit_condition (condition_ref TEXT PRIMARY KEY, permit_ref TEXT, condition_code TEXT, state_code TEXT);
CREATE TABLE contractor (contractor_ref TEXT PRIMARY KEY, registration_code TEXT);
CREATE TABLE inspection (inspection_ref TEXT PRIMARY KEY, permit_ref TEXT, state_code TEXT);
CREATE TABLE violation (violation_ref TEXT PRIMARY KEY, inspection_ref TEXT, state_code TEXT);
CREATE TABLE objection (objection_ref TEXT PRIMARY KEY, application_ref TEXT, state_code TEXT);
CREATE TABLE appeal (appeal_ref TEXT PRIMARY KEY, application_ref TEXT, state_code TEXT);

CREATE INDEX idx_pf_variable_scope ON wf_variable_history(execution_id,name,created_at);
CREATE INDEX idx_pf_metadata ON wf_definition_metadata(process_definition_id,activity_id);
