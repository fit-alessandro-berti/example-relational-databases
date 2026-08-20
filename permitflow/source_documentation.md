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

## Deterministic ambiguity rules

- Interpret lifecycle and outcome together; canceled or migrated task end times are not completions.
- Resolve semantic role by process-definition version and activity migration metadata.
- Walk execution scope and select the latest variable revision visible at the activity time.

## Time and identity

Business timestamps are normalized to UTC only by the extraction views. Source timestamps intentionally use ISO strings, split dates/times, epoch seconds, or effective/load pairs as appropriate. Canonical identities use the technical relationships or workflow scopes; no universal source event table exists.

## Reproduction

Run `python generate_data.py`. Generation is deterministic with seed 20260820 and 3,000 primary instances. The script recreates the source database, OCEL oracle, validation report, and all case-view CSV files.

The final activity-mapping queries are intentionally absent from this document. They are present only in the case-view SQL exercises.
