# Post-rework quality analysis of the OCELs and case-centric CSVs

Date: 2026-08-20  
Scope: six `ground_truth.ocel2.sqlite` files and 24 CSV files under `*/case_views/`  
Overall quality grade for process-mining analysis: **9.1 / 10.0**

## Executive assessment

The critical semantic and case-view defects identified in the earlier review have been resolved. The benchmark now uses explicit domain rules for event subjects, contexts, object-to-object relations, resources, and coherent process routes. Transactional identities are case-local; only declared master or shared types are pooled. Exception and rework behavior is embedded in the process position where it occurs instead of being appended after closure.

All six generated primary CSVs are exact projections of their canonical events for activity, timestamp, primary case ID, provenance, and complete object-reference set. All 24 CSVs are sorted first by `case_id`, then by `timestamp`; `source_record_id` is used only as a deterministic tie-breaker. Exception and multi-object exports contain complete traces for selected primary cases, while the fourth CSV supplies a genuinely different secondary-object case notion.

The outputs are now suitable for object-centric discovery, case-centric discovery, conformance exercises, organizational analysis, temporal analysis, and source-to-event extraction benchmarks, subject to the normal limitations of deterministic synthetic data.

## Grading method and result

Grades use a 1.0–10.0 scale and the same weights as the original assessment.

| Dimension | Weight | Post-rework score | Main evidence |
|---|---:|---:|---|
| Technical validity and reproducibility | 15% | 10.0 | SQLite integrity, PM4Py OCEL 2.0 output, stable IDs, byte-identical rerun |
| Scale and catalogue coverage | 10% | 9.8 | 74,661–118,084 events; every activity present at least 51 times |
| Behavioral realism | 20% | 8.8 | Explicit stateful routes, exclusive outcomes, in-line reopen/rework/reversal paths |
| Temporal realism | 10% | 8.6 | Irregular waits, human/24x7 calendars, effective versus recorded time |
| Object-centric semantic quality | 25% | 9.2 | Activity-specific subjects and contexts, semantic O2O qualifiers, type-specific sharing |
| Attribute quality | 10% | 8.8 | Role-specialized resources and activity-appropriate monetary/physical attributes |
| Case-view fidelity and usability | 10% | 9.8 | 100% primary fidelity, complete filtered traces, secondary case notion, enforced sorting |
| **Weighted overall** | **100%** | **9.1** | |

| Scenario | Final grade | Primary case | Secondary case |
|---|---:|---|---|
| ForgeFlow | **9.2** | SalesOrder | Shipment |
| TrialVersion | **9.0** | Participant | Sample |
| ProcureChange | **9.1** | PurchaseRequisition | Invoice |
| ClaimStream | **9.2** | Claim | Exposure |
| PermitFlow | **9.1** | PermitApplication | Inspection |
| BatteryVault | **9.0** | BatteryPack | ServiceOrder |

## Measured evidence

The generator validates source extraction against the canonical in-memory oracle using `source_table` plus `source_record_id`. It requires equality of activity, timestamp, primary case ID, and complete object-reference set for every event. It also checks complete activity and object catalogues, semantic subject relations, exact generated route conformance, role specialization, temporal histories, identity sharing, complete selected-case traces, CSV headers, and CSV ordering.

| Scenario | Events | Objects | E2O | O2O | Activities | Min. frequency | Changed object types | Roles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ForgeFlow | 97,884 | 59,036 | 353,436 | 31,200 | 48 | 300 | 22 | 11 |
| TrialVersion | 74,661 | 33,858 | 259,871 | 32,664 | 56 | 100 | 17 | 9 |
| ProcureChange | 100,504 | 46,353 | 416,109 | 33,000 | 55 | 81 | 17 | 9 |
| ClaimStream | 99,715 | 40,610 | 364,017 | 34,258 | 58 | 87 | 18 | 13 |
| PermitFlow | 118,084 | 32,783 | 426,586 | 33,703 | 63 | 51 | 14 | 12 |
| BatteryVault | 88,346 | 25,779 | 242,634 | 30,599 | 60 | 76 | 16 | 15 |

Every scenario has:

- 100% source-to-primary-CSV fidelity;
- zero transactional objects shared across primary cases;
- at least one genuinely shared master-data population;
- 100% conformance to its explicit generated route;
- full declared object-type coverage in E2O relations;
- an object change for every canonical event, distributed over 14–22 object types;
- qualified O2O relations with `valid_from`, `valid_to`, and relation state;
- complete exception and multi-object traces;
- four CSVs ordered by `case_id`, `timestamp`, and deterministic source-record tie-breaker.

## Resolution of the critical findings

| Earlier finding | Resolution | Validation |
|---|---|---|
| Event-object relations followed catalogue position | `domain_rules.py` now selects an activity-specific subject and semantic context objects | `semantic_event_object_rulebook`, `object_catalogue_coverage` |
| Transactional objects were pooled across unrelated cases | Pools are limited to explicit master/shared types; every transactional type uses the primary case number | `type_specific_identity_sharing`; zero violations in all scenarios |
| Routes mixed exclusive outcomes and appended loops after closure | Each domain has a coherent route builder with conditional outcomes and in-line retry, rework, reopen, or reversal | `coherent_stateful_routes`, `loops_and_reversals` |
| Amounts and generic values appeared on every event | Monetary and physical attributes are emitted only for activity families where they are meaningful | `activity_appropriate_attributes` |
| Actors were interchangeable | Actor IDs encode domain roles and use role-appropriate weekday or 24x7 calendars | `role_specific_resources` |
| Temporal changes covered only one primary type | Lifecycle changes now follow each event's semantic subject across 14–22 types per scenario | `temporal_object_attributes` |
| O2O relations used generic repeated qualifiers without validity | Relations now use domain qualifiers such as `settles`, `inspects`, `derived-from`, and `recycles`, with validity bounds | `effective_dated_object_relations` |
| Exception and multi-object files were incomplete event filters | They now select qualifying case IDs and retain the complete primary trace, with explicit event flags | `complete_exception_and_multi_views` |
| No independent case notion existed | Each scenario now includes `secondary_object_cases.csv` for Shipment, Sample, Invoice, Exposure, Inspection, or ServiceOrder | `multiple_case_notions` |
| CSV quality was not protected against future regressions | Generation performs row-level oracle fidelity and order checks; `validate_all.py` independently rechecks artifacts and ordering | `csv_oracle_fidelity`, `csv_sort_order` |

## Resolution of the four known CSV defects

| Scenario | Previous defect | Post-rework result |
|---|---|---|
| ProcureChange | Exact object-set match was 16.85% | Change-document scope reconstructs the full event object set; **100% exact match** |
| ClaimStream | Two retries were selected because numeric positions were ordered lexically | Event-store positions use numeric precedence; **100% provenance and row fidelity** |
| PermitFlow | 1,044 empty case IDs and 8,435 timestamps shifted by 15 minutes | Variables are visible before the first event and task completion time matches the oracle; **100% case/time fidelity** |
| BatteryVault | CSV case IDs omitted the canonical `BV-` prefix and used the wrong hub | The BatteryPack hub key is the case ID; **100% canonical case-ID fidelity** |

## Case-view design

Each scenario emits four views:

1. `primary_cases.csv` contains the full primary-object trace and an `is_exception_event` flag.
2. `exception_cases.csv` contains every event for cases with at least one exception, preserving the original trace and flagging the exceptional event.
3. `multi_object_cases.csv` contains every event for cases with at least one event related to three or more object types, with `is_multi_object_event`.
4. `secondary_object_cases.csv` changes the case notion to the configured secondary object and retains the original primary case in `primary_case_id`.

Row counts are:

| Scenario | Primary | Exception cases | Multi-object cases | Secondary-object cases |
|---|---:|---:|---:|---:|
| ForgeFlow | 97,884 | 35,784 | 97,884 | 15,000 |
| TrialVersion | 74,661 | 33,769 | 74,661 | 36,832 |
| ProcureChange | 100,504 | 45,895 | 100,504 | 23,997 |
| ClaimStream | 99,715 | 53,859 | 99,715 | 45,574 |
| PermitFlow | 118,084 | 50,721 | 118,084 | 15,600 |
| BatteryVault | 88,346 | 38,342 | 88,346 | 3,956 |

The multi-object selection equals the primary population in ForgeFlow, TrialVersion, and ProcureChange because every case contains at least one genuinely multi-object event. It remains a labelled complete-trace view, but it is not a smaller cohort in those three scenarios.

## Remaining limitations

The benchmark is deliberately synthetic and should not be treated as empirical evidence about real organizations.

- Optional branches use deterministic modular cohorts. They are coherent, but sufficiently deep analysis can identify the synthetic schedule.
- Most transactional types have one object instance per primary case. Real orders, claims, trials, and batteries often contain multiple items, visits, payments, inspections, or service orders.
- O2O validity bounds are meaningful and machine-readable, but most relations last for the generated case interval rather than changing repeatedly mid-case.
- Lifecycle `old_value`/`new_value` fields are more appropriate than before but remain normalized status summaries, not a complete domain data model.
- Secondary-object views include the events explicitly related to that object. They are valid object-lifecycle case notions, but they intentionally do not reproduce the full primary trace.
- Source-system noise and extraction patterns are realistic benchmark constructions, not calibrated samples from production systems.

These limitations reduce realism modestly, but they no longer invalidate object-centric relations, primary case fidelity, control-flow interpretation, or CSV usability.

## Verification record

The final verification run completed successfully with:

- `python generate_all.py` — all six scenarios PASS;
- `python validate_all.py` — all six generated artifact sets PASS;
- `python -m py_compile benchmark.py domain_rules.py generate_all.py validate_all.py` — PASS;
- `git diff --check` — PASS;
- a second full generation producing byte-identical source and OCEL SHA-256 values for every scenario.
