# PermitFlow — building-permit approval: source documentation

## Purpose

This is a synthetic **source-system** SQLite database for practicing object-centric extraction. It is not an event log and it does not contain the OCEL exchange tables. The independent oracle is `ground_truth.ocel2.sqlite`.

## Persistence pattern

Technical activity IDs vary by process-definition version. Activities depend on lifecycle/outcome and inherit historical business variables through execution scopes.

Primary evidence families:

- `wf_activity_history`
- `wf_task_history`
- `wf_message_delivery`
- `wf_form_submission`
- `wf_external_task`

### Table families and meanings

- `wf_process_instance/wf_execution` — root, called-subprocess, scope, and concurrency ancestry.
- `wf_activity_history/wf_task_history` — technical lifecycle records whose outcomes determine semantics.
- `wf_variable_history` — revision history of scope-local business references.
- `wf_message_delivery/wf_form_submission/wf_external_task` — non-human-task sources of domain milestones.
- `wf_process_migration/wf_job_log/wf_incident` — technical history excluded unless a domain rule says otherwise.
- `domain tables` — current permit, parcel, review, fee, inspection, objection, and appeal state.

The database deliberately contains mixed business and technical records, late recording times, redundant evidence, shared master/asset references, and historical relationships. Text codes are technical source codes. Current-state fields, update timestamps, retries, and administrative corrections are not automatically business events.

## Tables and fields

The following tables and columns are present in `source.sqlite`:

- `agency` — `agency_ref` TEXT, `agency_type_code` TEXT
- `appeal` — `appeal_ref` TEXT, `application_ref` TEXT, `state_code` TEXT
- `applicant` — `applicant_ref` TEXT, `identity_token` TEXT, `party_kind` TEXT
- `application_parcel` — `application_ref` TEXT, `parcel_ref` TEXT, `valid_from` TEXT, `valid_to` TEXT
- `application_party` — `application_ref` TEXT, `applicant_ref` TEXT, `role_code` TEXT, `valid_from` TEXT, `valid_to` TEXT
- `contractor` — `contractor_ref` TEXT, `registration_code` TEXT
- `document` — `document_ref` TEXT, `content_hash` TEXT, `document_type_code` TEXT
- `document_link` — `document_ref` TEXT, `subject_type_code` TEXT, `subject_ref` TEXT, `valid_from` TEXT, `valid_to` TEXT
- `fee_invoice` — `fee_invoice_ref` TEXT, `application_ref` TEXT, `amount_value` REAL, `state_code` TEXT
- `inspection` — `inspection_ref` TEXT, `permit_ref` TEXT, `state_code` TEXT
- `objection` — `objection_ref` TEXT, `application_ref` TEXT, `state_code` TEXT
- `parcel` — `parcel_ref` TEXT, `cadastral_code` TEXT, `municipality_code` TEXT
- `payment` — `payment_ref` TEXT, `fee_invoice_ref` TEXT, `amount_value` REAL, `state_code` TEXT
- `permit` — `permit_ref` TEXT, `application_ref` TEXT, `state_code` TEXT
- `permit_application` — `application_ref` TEXT, `current_state_code` TEXT, `submitted_at` TEXT, `updated_at` TEXT
- `permit_condition` — `condition_ref` TEXT, `permit_ref` TEXT, `condition_code` TEXT, `state_code` TEXT
- `plan_revision` — `plan_revision_ref` TEXT, `application_ref` TEXT, `revision_no` INTEGER, `current_state_code` TEXT
- `property` — `property_ref` TEXT, `parcel_ref` TEXT, `use_code` TEXT
- `review` — `review_ref` TEXT, `application_ref` TEXT, `review_type_code` TEXT, `current_state_code` TEXT
- `review_assignment` — `review_ref` TEXT, `agency_ref` TEXT, `reviewer_code` TEXT, `valid_from` TEXT, `valid_to` TEXT
- `violation` — `violation_ref` TEXT, `inspection_ref` TEXT, `state_code` TEXT
- `wf_activity_history` — `history_id` TEXT, `execution_id` TEXT, `process_instance_id` TEXT, `process_definition_id` TEXT, `activity_id` TEXT, `actor_code` TEXT, `related_refs_json` TEXT, `amount_value` REAL, `location_code` TEXT, `transaction_ref` TEXT, `start_time` TEXT, `end_time` TEXT, `lifecycle_code` TEXT
- `wf_activity_migration_map` — `migration_id` TEXT, `source_activity_id` TEXT, `target_activity_id` TEXT
- `wf_definition_metadata` — `process_definition_id` TEXT, `activity_id` TEXT, `semantic_code` TEXT, `semantic_role` TEXT
- `wf_deployment` — `deployment_id` TEXT, `deployed_at` TEXT, `resource_hash` TEXT
- `wf_execution` — `execution_id` TEXT, `parent_execution_id` TEXT, `process_instance_id` TEXT, `root_process_instance_id` TEXT, `super_process_instance_id` TEXT, `activity_id` TEXT, `is_scope` INTEGER, `is_concurrent` INTEGER, `created_at` TEXT, `ended_at` TEXT, `delete_reason` TEXT
- `wf_external_task` — `external_task_id` TEXT, `execution_id` TEXT, `process_instance_id` TEXT, `process_definition_id` TEXT, `activity_id` TEXT, `worker_code` TEXT, `related_refs_json` TEXT, `amount_value` REAL, `location_code` TEXT, `transaction_ref` TEXT, `completed_at` TEXT, `state_code` TEXT, `error_code` TEXT
- `wf_form_submission` — `submission_id` TEXT, `execution_id` TEXT, `process_instance_id` TEXT, `process_definition_id` TEXT, `activity_id` TEXT, `submitted_by` TEXT, `related_refs_json` TEXT, `amount_value` REAL, `location_code` TEXT, `transaction_ref` TEXT, `submitted_at` TEXT, `form_key` TEXT, `payload_json` TEXT
- `wf_identity_link` — `identity_link_id` TEXT, `task_id` TEXT, `user_code` TEXT, `group_code` TEXT, `link_type` TEXT
- `wf_incident` — `incident_id` TEXT, `process_instance_id` TEXT, `execution_id` TEXT, `incident_type` TEXT, `created_at` TEXT, `resolved_at` TEXT
- `wf_job_log` — `job_log_id` TEXT, `process_instance_id` TEXT, `job_type` TEXT, `retry_no` INTEGER, `created_at` TEXT, `ended_at` TEXT, `result_code` TEXT
- `wf_message_delivery` — `delivery_id` TEXT, `execution_id` TEXT, `process_instance_id` TEXT, `process_definition_id` TEXT, `activity_id` TEXT, `actor_code` TEXT, `related_refs_json` TEXT, `amount_value` REAL, `location_code` TEXT, `transaction_ref` TEXT, `delivered_at` TEXT, `message_code` TEXT, `result_code` TEXT
- `wf_message_subscription` — `subscription_id` TEXT, `execution_id` TEXT, `message_code` TEXT, `created_at` TEXT, `ended_at` TEXT
- `wf_process_definition` — `process_definition_id` TEXT, `definition_key` TEXT, `version_no` INTEGER, `deployment_id` TEXT
- `wf_process_instance` — `process_instance_id` TEXT, `process_definition_id` TEXT, `root_process_instance_id` TEXT, `super_process_instance_id` TEXT, `start_time` TEXT, `end_time` TEXT, `state_code` TEXT
- `wf_process_migration` — `migration_id` TEXT, `process_instance_id` TEXT, `source_definition_id` TEXT, `target_definition_id` TEXT, `migrated_at` TEXT
- `wf_task_history` — `task_id` TEXT, `execution_id` TEXT, `process_instance_id` TEXT, `process_definition_id` TEXT, `activity_id` TEXT, `assignee_code` TEXT, `related_refs_json` TEXT, `amount_value` REAL, `location_code` TEXT, `transaction_ref` TEXT, `start_time` TEXT, `end_time` TEXT, `outcome_code` TEXT, `delete_reason` TEXT
- `wf_variable_history` — `variable_id` TEXT, `execution_id` TEXT, `process_instance_id` TEXT, `name` TEXT, `revision_no` INTEGER, `value_text` TEXT, `value_type` TEXT, `created_at` TEXT, `ended_at` TEXT

## Deterministic ambiguity rules

- Interpret lifecycle and outcome together; canceled or migrated task end times are not completions.
- Resolve semantic role by process-definition version and activity migration metadata.
- Walk execution scope and select the latest variable revision visible at the activity time.

## Time and identity

Business timestamps are normalized to UTC only by the extraction views. Source timestamps intentionally use ISO strings, split dates/times, epoch seconds, or effective/load pairs as appropriate. Canonical identities use the technical relationships or workflow scopes; no universal source event table exists.

## Case views

The primary case notion is `PermitApplication`. The secondary-object view uses `Inspection` as an independent case notion. Exception and multi-object views retain complete primary-case traces and add explicit event flags. Every CSV is ordered first by `case_id`, then by `timestamp`, with `source_record_id` used only to break ties deterministically.

## Reproduction

Run `python generate_data.py`. Generation is deterministic with seed 20260820 and 3,000 primary instances. The script recreates the source database, OCEL oracle, validation report, and all case-view CSV files.

The final activity-mapping queries are intentionally absent from this document. They are present only in the case-view SQL exercises.
