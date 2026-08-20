# OCEL Quality and Process-Mining Usability Report

Assessment date: 2026-08-20  
Format: OCEL 2.0 JSON, written and read back with PM4Py 2.7.23.6

## Executive summary

The six exports are structurally strong OCELs and are suitable for exploratory object-centric process mining. Every file round-trips through PM4Py without losing events, objects, relations, activity types, or object types. Across all files there are 579,194 events, 238,419 objects, and 2,062,653 event-to-object relations. There are no missing event timestamps, duplicate event/object identifiers, orphan events or objects, dangling relations, or duplicate event-object pairs.

The main limitation is semantic rather than structural: most source systems expose coded activities without authoritative business labels. The generated activity names are therefore evidence-based contextual labels derived from the source table and stable connected object types. They are useful for navigation and discovery, but should not be treated as an official business glossary. ProcureChange is the partial exception: `PC001`–`PC027` use explicit resulting-state values stored in the source database.

| OCEL | Grade | Overall verdict | Best process-mining perspective |
|---|---:|---|---|
| BatteryVault | **8.4 / 10.0** | Very good | Battery-pack lifecycle, service, recall, second-life, and recycling |
| ClaimStream | **8.0 / 10.0** | Good to very good | Claim/exposure lifecycle, reserves, repair, payment, recovery |
| ForgeFlow | **7.8 / 10.0** | Good | Sales-order-centered commercial, engineering, supply, and fulfilment flow |
| PermitFlow | **7.9 / 10.0** | Good | Permit-application workflow performance and routing |
| ProcureChange | **8.5 / 10.0** | Very good | Purchase-requisition-to-payment flow and change/rework analysis |
| TrialVersion | **8.1 / 10.0** | Very good | Participant-centered clinical operations and sample/lab flow |

These grades assess analysis readiness, not the realism or business value of the underlying data. The highly regular population sizes, sequential code systems, and repeated lifecycle patterns suggest synthetic or benchmark-oriented data. The logs are excellent for technical experimentation and comparative process-mining work, but conclusions about real organizational performance would require validation against source owners.

## Grading method

Each grade considers five equally important areas:

1. **Structural integrity:** unique identifiers, valid event-object relations, no orphans, valid OCEL round trip.
2. **Activity semantics:** comprehensibility, code traceability, and confidence that the label describes the stored event.
3. **Object model and connectivity:** useful object types, multi-object events, lifecycle depth, and risks from high-degree shared objects.
4. **Temporal quality:** complete timestamps, meaningful lifecycle spans, ordering quality, and availability of recording timestamps.
5. **Analysis readiness:** useful attributes, balanced activity support, deduplication decisions, and the amount of analyst preprocessing still required.

A score near 10 would require authoritative business activity names, explicit object-object semantics, complete provenance attributes, confirmed real-world data meaning, and documented timestamp semantics. None of the databases provides all of these.

## Cross-log quality findings

### Structural integrity

All six logs have:

- zero duplicate event IDs;
- zero duplicate object IDs;
- zero duplicate event-object pairs;
- zero orphan events and zero orphan objects;
- zero relations pointing to missing events or objects;
- zero missing event timestamps;
- a valid PM4Py OCEL 2.0 JSON round trip;
- one contextual activity label and preserved original activity code for every event.

Events are genuinely object-centric: the median event references three or four objects in every log. This is sufficient for object-centric directly-follows graphs, object interaction analysis, and root-object flattening.

### Activity naming

All 340 activity types have a contextual label ending in the original code, such as `Update battery pack status — Firmware campaign [BV027]`. Every event also carries:

- `activity_code`: the stable source code;
- `activity_context`: the connected object-type context used in the label;
- `activity_label_source`: whether the label came from source-table/object context or an explicit state transition.

For algorithms, `activity_code` is the safest stable key. The longer `ocel:activity` value is preferable for visualization and analyst-facing tables. Labels based on a source table describe the kind of record operation, not necessarily the full business intent. For example, “Record finance posting” is justified by the source table, but the database does not disclose an authoritative business name for each `FF…` code.

### Temporal quality

All logs cover approximately 676–698 calendar days, while the median lifecycle of the recommended root object is roughly 34–46 days. This supports throughput-time, waiting-time, cohort, and temporal-variant analysis. No root object has multiple linked events at the exact same effective timestamp, so deterministic ordering is not being created from timestamp ties.

BatteryVault, ClaimStream, and TrialVersion have parseable recording timestamps for every event. Their median recording delay is approximately 35.9, 35.9, and 43.9 hours respectively, with no negative delays. ForgeFlow exposes a comparable recording timestamp for only 14.3% of events. PermitFlow and ProcureChange do not provide one uniform recording timestamp across their event sources. Consequently, ingestion-latency analysis is strong for the first three, partial for ForgeFlow, and not supported consistently for the latter two.

### Activity balance

Normalized activity entropy ranges from 0.888 to 0.941, and the largest activity accounts for only 3.05%–4.02% of events. This is unusually balanced and favorable for discovery because no single activity dominates the log. Only eight activity types across all logs have fewer than 100 events. Rare-branch conclusions should still use confidence intervals or minimum-support filters.

### Shared-object risk

Several object types are shared master or organizational entities rather than case-like objects. Examples include firmware campaigns, warehouses, catastrophe events, service providers, agencies, suppliers, sites, and studies. Some of these objects link hundreds of events across otherwise unrelated root-object lifecycles. If such objects are used as case notions or are included indiscriminately in an object-centric directly-follows graph, they can create misleading long-range connections.

Recommended controls:

- use the root object type listed for each OCEL as the primary case perspective;
- analyze shared/master objects in a separate interaction view;
- apply degree thresholds before flattening on shared objects;
- do not interpret event co-occurrence through a supplier, agency, site, or campaign as evidence of a direct operational handoff.

The exports contain no surviving explicit object-to-object (`o2o`) relations. Relationships are expressed through shared events. This is sufficient for most OCEL discovery methods, but it limits analyses that require persistent structural relationships independently of events.

## Per-OCEL assessment

### 1. BatteryVault — 8.4 / 10.0

#### Evidence

| Metric | Value |
|---|---:|
| Events | 88,346 |
| Objects | 25,779 |
| Event-object relations | 242,634 |
| Activities | 60 |
| Object types | 18 |
| Objects per event, median / mean | 3 / 2.75 |
| Battery packs | 3,000 |
| Events per battery pack, median | 27 |
| Battery-pack lifecycle span, median | 34.07 days |
| Activity entropy | 0.901 |
| Smallest activity support | 76 events |
| Actor / location completeness | 100% / 100% |
| Median recording delay | 35.9 hours |

#### Strengths

- Every event is connected to a battery pack, giving a clear and complete root perspective.
- Battery packs have deep lifecycles: the median has 27 events, and none is a single-event object.
- The log connects manufacturing components, passport records, diagnostics, service orders, recalls, shipments, second-life systems, recycling orders, and material batches.
- Actor, location, source, and recording timestamps are complete.
- Corrections were removed as duplicate technical versions rather than counted as repeated business activities.
- Activity frequencies are well balanced; only two activities have fewer than 100 events.

#### Limitations and risks

- Most `BV…` meanings are inferred from satellite table names and related object types. The labels identify the record family and context, but not an authoritative status transition.
- `VEHICLE` objects have only one linked event each, so vehicle lifecycle discovery is not useful from this log alone.
- Firmware campaigns, recall campaigns, and warehouses are high-degree shared objects. A warehouse has 150 events on average, and each recall campaign has 100. These can introduce cross-pack shortcuts.
- The 30,000 double-entry ledger rows were not modeled as separate activities because they are accounting representations of 15,000 journal movements. This avoids duplication but means account-level debit/credit analysis must return to the source database.
- 14,666 correction/replay satellite rows were collapsed. The log represents effective business history, not correction-audit history.

#### Recommended use

Use `BATTERYPACK` as the principal case notion. The log is particularly suitable for lifecycle discovery, conformance between service/recall/recycling pathways, throughput analysis, and comparing paths by actor or location. Treat warehouse and campaign objects as context rather than cases.

### 2. ClaimStream — 8.0 / 10.0

#### Evidence

| Metric | Value |
|---|---:|
| Events | 99,715 |
| Objects | 40,610 |
| Event-object relations | 364,017 |
| Activities | 58 |
| Object types | 21 |
| Objects per event, median / mean | 3 / 3.65 |
| Claims | 3,000 |
| Events per claim, median | 33 |
| Claim lifecycle span, median | 42.27 days |
| Activity entropy | 0.925 |
| Smallest activity support | 87 events |
| Actor completeness | 68.83% |
| Location completeness | 61.61% |
| Median recording delay | 35.9 hours |

#### Strengths

- Every event links to a claim, and claims have a substantial median lifecycle of 33 events.
- The object model covers incident, exposure, damage item, adjuster assignment, inspection, evidence, estimate, reserve, repair order, payment, recovery, settlement, fraud, litigation, communication, and complaint perspectives.
- Event cardinality is consistently multi-object, making the log well suited to object interaction and synchronization analysis.
- Event-store retries were explicitly identified and removed: 15,359 exact retry duplicates do not inflate paths or activity counts.
- All 58 versioned technical event types were normalized to stable semantic codes before contextual naming.
- Recording timestamps are complete and temporally consistent.

#### Limitations and risks

- Activity labels remain contextual because `event_type_alias` maps technical names such as `Mutation…CommittedV…` only to opaque `CS…` codes, not to business descriptions.
- Actor is absent for 31.17% of events and location for 38.39%, mainly because some secondary source tables do not store these attributes.
- Communication, fraud case, litigation case, and settlement objects are single-event milestones, not lifecycle-bearing case notions.
- Catastrophe events and service providers are very high-degree shared objects. A catastrophe event has a median of 350 linked events; flattening on this type would merge many claims.
- Amount is present for 24.71% of events. Financial analyses must treat absence as “not applicable or unavailable,” not as zero.

#### Recommended use

Use `CLAIM` as the main case notion and `EXPOSURE` or `DAMAGEITEM` for subprocess views. The log is strong for claims-path discovery, reserve/payment timing, repair coordination, and outcome-path comparison. Exclude catastrophe and service-provider edges when discovering claim-local control flow, then add them back for workload or network analysis.

### 3. ForgeFlow — 7.8 / 10.0

#### Evidence

| Metric | Value |
|---|---:|
| Events | 97,884 |
| Objects | 59,036 |
| Event-object relations | 353,436 |
| Activities | 48 |
| Object types | 28 |
| Objects per event, median / mean | 4 / 3.61 |
| Sales orders | 3,000 |
| Events per sales order, median | 29 |
| Sales-order lifecycle span, median | 34.10 days |
| Activity entropy | 0.941 |
| Smallest activity support | 300 events |
| Actor / location completeness | 100% / 100% |
| Comparable recording timestamp | 14.31% of events |

#### Strengths

- ForgeFlow has the broadest object model: 28 types spanning commercial documents, RFQs, quotes, engineering, materials, work orders, quality, procurement, fulfilment, shipment, invoice, payment, and warranty.
- Every event relates to a sales order; the median sales order has 29 events over 34.1 days.
- Median event cardinality is four objects, providing rich synchronization and interaction structure.
- Actor and location are complete.
- Activity support is excellent: no activity has fewer than 300 events, and normalized entropy is the highest of the six logs.
- Timestamps encoded as ISO strings, date/clock pairs, epochs, epoch milliseconds, and day/seconds pairs were normalized consistently to UTC.

#### Limitations and risks

- No populated catalog explains the `FF…` codes. Names therefore describe the source operation family and connected objects, not an authoritative business transition.
- Only the engineering-execution table provides a comparable recording timestamp, limiting cross-family ingestion-delay analysis.
- Several types are mainly milestones: payment, warranty, RFQ line, purchase-order line, and many sales-order-line objects have one event.
- Customer, supplier, and material objects have long, high-degree histories across orders. They are dimensions or shared resources, not good case notions.
- The 24,471 integration-outbox rows were excluded as technical messages, and 18,000 document-conversion rows were used as technical linkage context rather than events. Integration reliability analysis is therefore outside this OCEL's intended scope.

#### Recommended use

Use `SALESORDER` for end-to-end discovery and `WORKORDER`, `SHIPMENT`, or `QUOTEREVISION` for focused subprocesses. The log is useful for cross-functional interaction and synchronization analysis. Apply type filtering before discovery so shared customer/material/supplier histories do not create cross-order directly-follows edges.

### 4. PermitFlow — 7.9 / 10.0

#### Evidence

| Metric | Value |
|---|---:|
| Events | 118,084 |
| Objects | 32,783 |
| Event-object relations | 426,586 |
| Activities | 63 |
| Object types | 17 |
| Objects per event, median / mean | 4 / 3.61 |
| Permit applications | 3,000 |
| Events per application, median | 35 |
| Application lifecycle span, median | 45.92 days |
| Activity entropy | 0.919 |
| Smallest activity support | 51 events |
| Actor / location completeness | 100% / 100% |

#### Strengths

- This is the largest event log and has the deepest median root lifecycle: 35 events per permit application.
- Every event connects to a permit application, and no application is single-event.
- The log captures applicant/property/parcel intake, plans, reviews, agencies, fees, payments, documents, inspections, contractors, conditions, objections, violations, appeals, and permits.
- Five workflow persistence mechanisms contain disjoint semantic-code sets, so combining them provides all 63 activities without duplicating the same code across tables.
- Actor and location are complete, and exact root-level timestamp ties are absent.
- The multi-object cardinality supports analysis of handoffs among plans, reviews, agencies, inspections, and permit outcomes.

#### Limitations and risks

- The source metadata maps engine IDs to `PF…` codes and `ROLE…` values, but neither target has a human description. Generated labels therefore describe technical actions such as task completion, form submission, or message delivery plus object context.
- The business purpose of two activities with similar source/object context can remain unclear; the preserved `PF…` code is essential for distinguishing them.
- There is no uniform recorded-at timestamp, so workflow execution time can be analyzed but ingestion latency cannot.
- Agencies are extremely high-degree shared objects (median 394 events), while applicant, parcel, property, and contractor objects can also bridge many applications.
- Payment is a single-event milestone. Document objects are also shallow: 65.93% have one event.

#### Recommended use

Use `PERMITAPPLICATION` as the principal case notion. The log is well suited to workflow throughput, branch/rework discovery, task-form-message interaction, and comparing inspection/appeal/violation paths. Do not flatten on `AGENCY`; use agency as a resource or organizational dimension.

### 5. ProcureChange — 8.5 / 10.0

#### Evidence

| Metric | Value |
|---|---:|
| Events | 100,504 |
| Objects | 46,353 |
| Event-object relations | 416,109 |
| Activities | 55 |
| Object types | 20 |
| Objects per event, median / mean | 4 / 4.14 |
| Purchase requisitions | 3,000 |
| Events per requisition, median | 33 |
| Requisition lifecycle span, median | 44.54 days |
| Activity entropy | 0.922 |
| Smallest activity support | 81 events |
| Actor completeness | 100% |
| Location completeness | 44.24% |

#### Strengths

- ProcureChange has the highest mean object cardinality and a strong end-to-end root perspective: every event links to a purchase requisition.
- `PC001`–`PC027` use explicit `new_value_text` transitions such as requisition submission, quotation evaluation, PO approval, PO change, and supplier confirmation change. These are the most semantically trustworthy activity names in the six exports.
- The object model covers requisition/item, RFQ, supplier quotation, contract, purchase order/item, schedule line, ASN, goods receipt/movement, inspection, invoice/item, accounting document, payment proposal, and payment.
- Change-document object scope was recovered from 416,109 `OBJECT_SCOPE` links rather than guessing from technical change keys.
- Live and archive change headers were merged with 299 overlaps removed.
- Actor is complete, making organizational and segregation-of-duties analysis feasible.

#### Limitations and risks

- `PC028`–`PC055` have no populated description catalog; their labels use the source document family and connected objects.
- Location is available for only 44.24% of events and should not be used as a universal slicing dimension.
- There is no uniform recording timestamp separate from business posting time.
- Supplier, cost center, contract, and material are very high-degree shared objects. Supplier objects average 363 events and can connect many requisitions.
- Payment and ASN are mostly one-event milestones; schedule lines have exactly one event.
- The log combines state-change events with document-posting events. Discovery should preserve `source_table` so analysts can distinguish change history from follow-on business documents.

#### Recommended use

Use `PURCHASEREQUISITION` as the primary case perspective and `PURCHASEORDER` for the purchasing subprocess. This is the strongest log for change/rework analysis because it retains previous/resulting state attributes for source change documents. It is also suitable for approval-loop detection, compliance, document-flow timing, and supplier interaction, provided shared suppliers/contracts are excluded from case-level directly-follows construction.

### 6. TrialVersion — 8.1 / 10.0

#### Evidence

| Metric | Value |
|---|---:|
| Events | 74,661 |
| Objects | 33,858 |
| Event-object relations | 259,871 |
| Activities | 56 |
| Object types | 19 |
| Objects per event, median / mean | 3 / 3.48 |
| Participants | 3,000 |
| Events per participant, median | 26 |
| Participant lifecycle span, median | 35.75 days |
| Activity entropy | 0.888 |
| Smallest activity support | 100 events |
| Actor / location completeness | 100% / 100% |
| Median recording delay | 43.88 hours |

#### Strengths

- Every event relates to a participant, with a useful median lifecycle of 26 events.
- The object model connects studies, protocols, sites, investigators, visits, consent, drug kits, dispensation/dose, samples/aliquots/shipments, lab orders/tests/results, adverse events, protocol deviations, and data queries.
- Actor, location, source table, and recording timestamp are complete.
- Recording timestamps are always later than effective timestamps, supporting delay and late-entry analysis.
- The version model was collapsed onto effective business events while retaining whether a correction was applied.
- No activity has fewer than 100 events.

#### Limitations and risks

- The populated version tables expose only `TV…` state codes. The `code_dictionary` table exists but is empty, so activity names are based on the version-table family and object context.
- The source design distributes code families across version tables; “update study record” describes the physical record family and should not be interpreted as an authoritative clinical verb.
- 33,300 import-replay baseline versions were excluded, and 24,887 correction versions were collapsed into their effective business events. This is appropriate for process discovery but unsuitable for reconstructing the edit/audit process itself.
- Aliquot objects are single-event, consent is 94.11% single-event, and dose is 88.89% single-event. They are milestones rather than independent lifecycles.
- Site, study, protocol, and investigator objects are long-lived shared entities. A site has a median of 318 events and a study 126, so they can connect many participants.

#### Recommended use

Use `PARTICIPANT` as the primary case notion and `SAMPLE`, `LABTEST`, or `VISIT` for focused subprocesses. The log is suitable for clinical-operational flow, sample/lab turnaround, adverse-event pathways, and data-query interactions. For data-entry correction analysis, create a separate audit OCEL that keeps correction versions as explicit events.

## Practical recommendations before analysis

1. **Use the original code as the analytical key.** Keep `activity_code` for grouping and model reproducibility; use `ocel:activity` for display.
2. **Start with root-object perspectives.** Recommended roots are `BATTERYPACK`, `CLAIM`, `SALESORDER`, `PERMITAPPLICATION`, `PURCHASEREQUISITION`, and `PARTICIPANT`.
3. **Control shared-object degrees.** Exclude or separately model campaign, warehouse, catastrophe, provider, customer, supplier, agency, site, study, and similar master-data objects during local control-flow discovery.
4. **Keep `source_table` visible.** This is necessary to distinguish business state changes from workflow-engine representations and document postings.
5. **Treat missing attributes as unavailable, not zero.** This applies particularly to amounts, ClaimStream actor/location, ProcureChange location, and recording timestamps.
6. **Apply minimum support to rare branches.** Activities with fewer than 100 events exist in BatteryVault, ClaimStream, PermitFlow, and ProcureChange.
7. **Validate semantics with domain owners before conformance checking.** Contextual labels are adequate for exploration but not a substitute for an official activity dictionary.
8. **Do not use these logs alone for correction/audit-process mining.** The main exports intentionally collapse retries and corrections to effective business events.

## Final conclusion

All six OCELs are technically sound and immediately usable for object-centric discovery, lifecycle statistics, performance analysis, and controlled flattening. ProcureChange receives the highest grade because a substantial part of its activity semantics comes directly from stored transition values and its object scope is especially rich. BatteryVault follows closely due to complete attributes and deep pack lifecycles. The remaining logs are structurally excellent but lose points for contextual rather than authoritative activity semantics, shared-object hub effects, or incomplete provenance attributes.

The most important analytical safeguard is to separate root-case objects from shared contextual objects. With that control—and with `activity_code` retained as the stable identifier—the exports provide a strong foundation for process-mining analysis.
