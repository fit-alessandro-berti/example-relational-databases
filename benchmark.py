"""Deterministic builders for the six relational-to-OCEL benchmark scenarios.

The source databases deliberately use six different operational persistence
patterns.  Canonical events exist only in the generated OCEL oracle and in the
case-view extraction SQL; they are never stored as source values.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import sqlite3
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

os.environ.setdefault("MPLCONFIGDIR", "/tmp/example-relational-databases-matplotlib")

import pandas as pd
import pm4py
from pm4py.objects.ocel.obj import OCEL

from domain_rules import (
    CASE_TYPES,
    O2O_EDGES,
    SECONDARY_CASE_TYPES,
    SHARED_POOL_SIZES,
    actor_role,
    build_route,
    context_types,
    subject_type,
)


DEFAULT_SEED = 20260820
DEFAULT_INSTANCES = 3000
MIN_ACTIVITY_FREQUENCY = 50
MIN_SOURCE_ROWS = 100000


@dataclass(frozen=True)
class Scenario:
    slug: str
    folder: str
    title: str
    pattern: str
    prefix: str
    activities: tuple[str, ...]
    object_types: tuple[str, ...]
    evidence_tables: tuple[str, ...]
    loop_activities: tuple[str, ...]
    description: str


def _items(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split(";") if item.strip())


SCENARIOS: dict[str, Scenario] = {
    "forgeflow": Scenario(
        "forgeflow", "forgeflow", "ForgeFlow — engineer-to-order manufacturing",
        "normalized OLTP milestones with heterogeneous timestamps and duplicate evidence", "FF",
        _items("RFQ Created; RFQ Line Added; Quote Prepared; Quote Revised; Quote Approved; Quote Sent; Quote Accepted; Sales Order Created; Order Line Added; Configuration Frozen; Credit Check Failed; Credit Check Passed; Order Released; Engineering Change Requested; Engineering Change Approved; Engineering Change Implemented; BOM Revision Released; Work Order Created; Work Order Released; Material Reserved; Material Shortage Detected; Purchase Requisition Created; Purchase Order Issued; Supplier Confirmation Received; Goods Receipt Posted; Incoming Inspection Started; Incoming Inspection Passed; Incoming Inspection Failed; Material Issued to Work Order; Operation Started; Operation Completed; Production Paused; Production Resumed; Nonconformance Raised; Rework Ordered; Rework Completed; Final Inspection Passed; Final Inspection Failed; Serial Number Assigned; Finished Goods Received; Shipment Planned; Package Sealed; Shipment Dispatched; Delivery Confirmed; Invoice Issued; Payment Received; Warranty Registered; Order Closed"),
        _items("Customer; RFQ; RFQLine; Quote; QuoteRevision; SalesOrder; SalesOrderLine; ProductConfiguration; EngineeringChange; BOMRevision; WorkOrder; Operation; Material; MaterialLot; PurchaseRequisition; PurchaseOrder; PurchaseOrderLine; Supplier; GoodsReceipt; QualityInspection; Nonconformance; ReworkOrder; SerialUnit; Shipment; Package; Invoice; Payment; Warranty"),
        ("commercial_document", "engineering_execution", "supply_posting", "quality_observation", "fulfilment_record", "finance_posting"),
        ("Final Inspection Failed", "Rework Ordered", "Rework Completed", "Final Inspection Passed"),
        "Milestones are spread over commercial, engineering, supply, quality, fulfilment, and finance records. Transaction references fuse redundant outbox evidence.",
    ),
    "trialversion": Scenario(
        "trialversion", "trialversion", "TrialVersion — clinical-trial execution",
        "in-table row versioning with semantic diffs and correction filtering", "TV",
        _items("Study Created; Protocol Published; Protocol Amended; Site Initiated; Site Suspended; Site Reactivated; Site Closed; Participant Screened; Screening Failed; Consent Signed; Consent Withdrawn; Participant Reconsented; Participant Enrolled; Participant Randomized; Participant Discontinued; Participant Completed; Visit Scheduled; Visit Rescheduled; Visit Started; Visit Completed; Visit Missed; Visit Canceled; Drug Kit Assigned; Drug Kit Dispensed; Dose Administered; Dose Held; Drug Kit Returned; Sample Collection Ordered; Sample Collected; Sample Collection Canceled; Sample Accessioned; Aliquot Created; Sample Frozen; Sample Thawed; Sample Destroyed; Sample Shipment Created; Sample Shipment Packed; Sample Shipment Dispatched; Sample Shipment Received; Lab Test Ordered; Lab Test Started; Lab Test Completed; Lab Test Repeated; Result Entered; Result Validated; Result Amended; Adverse Event Opened; Adverse Event Graded; Adverse Event Escalated; Adverse Event Resolved; Protocol Deviation Raised; Protocol Deviation Waived; Protocol Deviation Closed; Data Query Opened; Data Query Answered; Data Query Closed"),
        _items("Study; Protocol; Site; Participant; Consent; Visit; DrugKit; Dispensation; Dose; Sample; Aliquot; SampleShipment; LabOrder; LabTest; LabResult; AdverseEvent; ProtocolDeviation; DataQuery; Investigator"),
        ("study_v", "protocol_v", "site_v", "participant_v", "visit_v", "drug_kit_v", "sample_v", "sample_shipment_v", "lab_test_v", "lab_result_v", "adverse_event_v", "data_query_v"),
        ("Visit Rescheduled", "Visit Missed", "Participant Reconsented"),
        "Successive logical versions must be compared. BUSINESS changes can create activities; CORRECTION, IMPORT_REPLAY, and SYSTEM_RECALCULATION versions cannot do so by insertion alone.",
    ),
    "procurechange": Scenario(
        "procurechange", "procurechange", "ProcureChange — industrial procure-to-pay",
        "SAP-style packed change documents combined with application documents", "PC",
        _items("Purchase Requisition Created; Requisition Item Added; Requisition Item Changed; Requisition Submitted; Requisition Released; Requisition Rejected; RFQ Created; RFQ Sent; Supplier Quotation Received; Quotation Revised; Quotation Evaluated; Source Selected; Contract Referenced; Requisition Converted to PO; Purchase Order Created; PO Item Added; PO Quantity Changed; PO Price Changed; Delivery Date Changed; PO Submitted for Approval; PO Released; PO Rejected; PO Sent to Supplier; Supplier Confirmation Received; Supplier Confirmation Changed; Advance Shipping Notice Received; PO Item Deleted; Goods Receipt Posted; Goods Receipt Reversed; Partial Receipt Posted; Quality Inspection Started; Quality Inspection Passed; Quality Inspection Failed; Stock Placed in Blocked Stock; Stock Released from Blocked Stock; Return to Supplier Posted; PO Item Delivery Completed; Invoice Received; Invoice Parked; Invoice Posted; Invoice Changed; Three-Way Match Passed; Three-Way Match Failed; Invoice Blocked; Invoice Unblocked; Credit Memo Posted; Accounting Document Created; Payment Proposal Created; Payment Proposal Approved; Payment Executed; Payment Reversed; PO Item Final-Invoiced; Purchase Order Closed; Supplier Blocked; Supplier Unblocked"),
        _items("PurchaseRequisition; RequisitionItem; RFQ; SupplierQuotation; Contract; PurchaseOrder; PurchaseOrderItem; ScheduleLine; Supplier; Material; AdvanceShippingNotice; GoodsMovement; GoodsReceipt; InspectionLot; Invoice; InvoiceItem; AccountingDocument; PaymentProposal; Payment; CostCenter"),
        ("cdhdr", "req_header", "goods_movement_header", "inspection_lot", "invoice_header", "accounting_header", "payment_run"),
        ("Requisition Rejected", "PO Rejected", "Goods Receipt Reversed", "Payment Reversed"),
        "Generic CDHDR/CDPOS field sets are decoded with fixed-width key metadata, then fused with application documents and archived changes.",
    ),
    "claimstream": Scenario(
        "claimstream", "claimstream", "ClaimStream — property-insurance claims",
        "event sourcing with upcasting, technical filtering, and cross-stream correlation", "CS",
        _items("Claim Reported; Incident Registered; Claim Acknowledged; Policy Located; Coverage Check Started; Coverage Confirmed; Coverage Denied; Exposure Opened; Exposure Classified; Exposure Reclassified; Adjuster Assigned; Adjuster Reassigned; Inspection Scheduled; Inspection Rescheduled; Inspection Completed; Damage Item Added; Damage Item Updated; Evidence Requested; Evidence Received; Evidence Validated; Evidence Rejected; Estimate Requested; Estimate Received; Estimate Revised; Estimate Approved; Reserve Established; Reserve Increased; Reserve Decreased; Reserve Released; Fraud Score Calculated; Fraud Investigation Opened; Fraud Investigation Cleared; Fraud Case Referred; Liability Accepted; Liability Partially Accepted; Liability Denied; Repair Authorized; Repair Started; Repair Completed; Repair Reopened; Payment Proposed; Payment Approved; Payment Issued; Payment Failed; Payment Reissued; Payment Canceled; Recovery Identified; Recovery Demand Sent; Recovery Received; Litigation Opened; Hearing Scheduled; Claim Settled; Customer Contacted; Complaint Opened; Complaint Resolved; Claim Closed; Claim Reopened; Claim Archived"),
        _items("Policy; InsuredParty; Claim; Incident; Exposure; DamageItem; AdjusterAssignment; Inspection; EvidenceDocument; Estimate; Reserve; FraudCase; RepairOrder; Payment; Recovery; LitigationCase; Complaint; CatastropheEvent; ServiceProvider; Communication; Settlement"),
        ("event_store", "command_result", "inbox_message", "document_index"),
        ("Payment Failed", "Payment Reissued", "Repair Reopened", "Claim Reopened"),
        "Append-only domain events are correlated across streams, payload versions are upcast, and projections/snapshots remain non-authoritative technical artifacts.",
    ),
    "permitflow": Scenario(
        "permitflow", "permitflow", "PermitFlow — building-permit approval",
        "generic workflow history with execution ancestry, variable scope, outcomes, and migrations", "PF",
        _items("Pre-Application Opened; Applicant Identity Verified; Parcel Linked; Application Drafted; Application Submitted; Submission Withdrawn; Application Reopened; Fee Calculated; Fee Invoice Issued; Fee Paid; Completeness Review Started; Additional Information Requested; Additional Documents Submitted; Completeness Accepted; Completeness Rejected; Zoning Review Started; Zoning Approved; Zoning Denied; Heritage Review Requested; Heritage Approved; Heritage Conditions Imposed; Environmental Review Started; Environmental Review Passed; Environmental Review Failed; Public Notice Published; Consultation Opened; Objection Filed; Objection Withdrawn; Consultation Closed; Hearing Scheduled; Hearing Held; Plan Revision Requested; Plan Revision Submitted; Plan Revision Accepted; Fire Safety Review Started; Fire Safety Passed; Fire Safety Failed; Structural Review Started; Structural Review Passed; Structural Review Failed; Permit Drafted; Permit Approved; Permit Issued; Permit Amended; Permit Suspended; Permit Revoked; Contractor Registered; Work Commencement Notified; Inspection Requested; Inspection Scheduled; Inspection Performed; Inspection Passed; Inspection Failed; Reinspection Requested; Violation Opened; Violation Remediated; Completion Certificate Requested; Completion Certificate Issued; Appeal Filed; Appeal Hearing Held; Appeal Allowed; Appeal Dismissed; Case Archived"),
        _items("PermitApplication; Applicant; Parcel; Property; PlanRevision; Document; Review; Agency; FeeInvoice; Payment; Permit; Contractor; Inspection; Violation; Condition; Objection; Appeal"),
        ("wf_activity_history", "wf_task_history", "wf_message_delivery", "wf_form_submission", "wf_external_task"),
        ("Completeness Rejected", "Application Reopened", "Inspection Failed", "Reinspection Requested"),
        "Technical activity IDs vary by process-definition version. Activities depend on lifecycle/outcome and inherit historical business variables through execution scopes.",
    ),
    "batteryvault": Scenario(
        "batteryvault", "batteryvault", "BatteryVault — circular battery lifecycle",
        "bitemporal Data Vault satellites plus balanced custody and ownership ledger", "BV",
        _items("Cell Batch Produced; Cell Batch Released; Module Assembled; Module Tested; Module Failed Test; Battery Pack Assembled; Battery Pack Tested; Battery Pack Passed Test; Battery Pack Failed Test; Battery Passport Issued; Battery Passport Corrected; Battery Installed in Vehicle; Vehicle Delivered; Ownership Transferred; Lease Started; Lease Ended; Battery Removed from Vehicle; Telemetry Anomaly Detected; Diagnostic Scheduled; Diagnostic Run; State of Health Assessed; Service Order Opened; Service Started; Module Replacement Ordered; Module Replaced; Service Completed; Firmware Campaign Assigned; Firmware Downloaded; Firmware Installed; Firmware Installation Failed; Firmware Rolled Back; Warranty Claim Opened; Warranty Claim Approved; Warranty Claim Denied; Recall Campaign Announced; Battery Matched to Recall; Recall Notification Sent; Recall Notification Acknowledged; Recall Service Completed; Transport Booked; Shipment Dispatched; Shipment Received; Battery Quarantined; Battery Released from Quarantine; Second-Life Assessment Started; Second-Life Assessment Passed; Second-Life Assessment Failed; Battery Reconfigured; Second-Life System Commissioned; Second-Life System Decommissioned; Recycling Order Created; Battery Dismantled; Material Batch Recovered; Material Batch Certified; Compliance Certificate Revoked; Compliance Certificate Reissued; Incident Reported; Incident Investigation Started; Incident Closed; Lifecycle Closed"),
        _items("CellBatch; Module; BatteryPack; BatteryPassport; Vehicle; Owner; ServiceOrder; DiagnosticTest; FirmwareCampaign; WarrantyClaim; RecallCampaign; Shipment; Warehouse; SecondLifeSystem; RecyclingOrder; MaterialBatch; Certificate; Incident"),
        ("sat_pack_status", "sat_pack_test", "sat_passport_data", "sat_diagnostic_result", "sat_service_status", "sat_campaign_status", "sat_claim_status", "sat_recall_status", "sat_shipment_status", "sat_second_life_status", "sat_recycling_status", "sat_certificate_status", "sat_incident_status", "asset_journal"),
        ("Battery Pack Failed Test", "Firmware Installation Failed", "Firmware Rolled Back", "Second-Life Assessment Failed"),
        "Effective-time satellite transitions are deduplicated by hashdiff and source precedence; paired ledger entries form one movement despite two postings.",
    ),
}


def _code(s: Scenario, activity_index: int) -> str:
    return f"{s.prefix}{activity_index + 1:03d}"


def _sql(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _mapping_case(s: Scenario, expression: str) -> str:
    clauses = " ".join(
        f"WHEN {_sql(_code(s, i))} THEN {_sql(activity)}"
        for i, activity in enumerate(s.activities)
    )
    return f"CASE {expression} {clauses} END"


def _event_modulus(index: int) -> int:
    if index < 6:
        return 1
    if index < 12:
        return 2
    return (7, 11, 13, 17, 19, 23, 29, 31, 37)[(index - 12) % 9]


def _safe_type(value: str) -> str:
    out = []
    for ch in value:
        if ch.isalnum():
            out.append(ch.upper())
        else:
            out.append("_")
    return "".join(out)


def _object_id(s: Scenario, object_type: str, case_no: int, type_index: int | None = None) -> str:
    pool_size = SHARED_POOL_SIZES[s.slug].get(object_type)
    number = ((case_no - 1) % pool_size) + 1 if pool_size else case_no
    return f"{s.prefix}-{_safe_type(object_type)}-{number:06d}"


def _build_canonical(s: Scenario, instance_count: int) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    events: list[dict[str, Any]] = []
    objects: dict[str, dict[str, Any]] = {}
    relations: list[dict[str, Any]] = []
    o2o: list[dict[str, Any]] = []
    changes: list[dict[str, Any]] = []
    event_seq = 0
    base = datetime(2023, 1, 1, 6, 0, tzinfo=timezone.utc)
    case_type = CASE_TYPES[s.slug]
    subject_by_event: dict[str, str] = {}
    case_objects: dict[int, set[str]] = defaultdict(set)

    def ensure_object(object_type: str, case_no: int) -> str:
        oid = _object_id(s, object_type, case_no)
        if oid not in objects:
            shared = object_type in SHARED_POOL_SIZES[s.slug]
            objects[oid] = {
                "ocel:oid": oid,
                "ocel:type": object_type,
                "business_key": oid.split("-", 1)[1],
                "source_system": f"{s.prefix}_SRC",
                "region": ("DE-N", "DE-S", "EU-W", "EU-C")[case_no % 4],
                "object_category": "SHARED_MASTER" if shared else "TRANSACTIONAL",
                "lifecycle_status": "IDENTIFIED",
            }
        case_objects[case_no].add(oid)
        return oid

    def state_from_activity(activity: str) -> str:
        for suffix in (
            "Reactivated", "Reassigned", "Rescheduled", "Reissued", "Reopened", "Reconfigured",
            "Completed", "Confirmed", "Accepted", "Approved", "Validated", "Released", "Received",
            "Dispatched", "Administered", "Published", "Registered", "Installed", "Commissioned",
            "Decommissioned", "Dismantled", "Recovered", "Certified", "Corrected", "Amended",
            "Failed", "Rejected", "Denied", "Canceled", "Withdrawn", "Suspended", "Revoked",
            "Closed", "Archived", "Issued", "Created", "Opened", "Started", "Passed", "Paid",
            "Assigned", "Returned", "Frozen", "Thawed", "Destroyed", "Raised", "Filed", "Held",
        ):
            if activity.endswith(suffix):
                return suffix.upper().replace(" ", "_")
        return _safe_type(activity)

    def next_time(current: datetime, case_no: int, position: int, activity_index: int, role: str) -> datetime:
        # Deterministic but irregular waiting/service times. Human roles observe
        # a weekday/day-shift calendar; technical roles can run continuously.
        technical = role in {"TELEMETRY", "SOFTWARE", "PROCESS_OWNER"}
        span = 18 * 60 if technical else 42 * 60
        minutes = 25 + ((case_no * 97 + position * 53 + activity_index * 29) % span)
        value = current + timedelta(minutes=minutes)
        if not technical:
            while value.weekday() >= 5:
                value = (value + timedelta(days=1)).replace(hour=8, minute=(case_no + position) % 45)
            if value.hour < 7:
                value = value.replace(hour=7, minute=(case_no + position) % 45)
            elif value.hour >= 19:
                value = (value + timedelta(days=1)).replace(hour=8, minute=(case_no + position) % 45)
                while value.weekday() >= 5:
                    value += timedelta(days=1)
        return value

    def add_event(case_no: int, activity: str, when: datetime, route_step: dict[str, Any], position: int) -> None:
        nonlocal event_seq
        event_seq += 1
        activity_index = s.activities.index(activity)
        subject = subject_type(s.slug, activity, s.object_types)
        case_oid = ensure_object(case_type, case_no)
        subject_oid = ensure_object(subject, case_no)
        related: list[tuple[str, str]] = [(case_oid, "primary")]
        if subject_oid != case_oid:
            related.append((subject_oid, "subject"))
        for context_type in context_types(s.slug, subject):
            context_oid = ensure_object(context_type, case_no)
            if context_oid not in {oid for oid, _ in related}:
                related.append((context_oid, "context"))
        eid = f"{s.prefix}-E-{event_seq:08d}"
        role = actor_role(s.slug, activity)
        actor_pool = 9 + (sum(map(ord, role)) % 13)
        actor = f"{s.prefix}-{role}-{((case_no * 7 + activity_index * 3) % actor_pool) + 1:03d}"
        money_words = ("Payment", "Invoice", "Reserve", "Estimate", "Fee", "Price", "Credit Memo", "Quotation", "Recovery")
        quantity_words = ("Material", "Goods", "Sample", "Dose", "Shipment", "Module", "Battery", "Stock", "Receipt")
        amount = round(125.0 + ((case_no * 43 + activity_index * 71) % 800000) / 100.0, 2) if any(word in activity for word in money_words) else None
        quantity = round(1.0 + ((case_no * 17 + activity_index * 11) % 2500) / 10.0, 1) if any(word in activity for word in quantity_words) else None
        lag_minutes = (case_no * 31 + position * 17 + activity_index * 23) % (72 * 60)
        event = {
            "ocel:eid": eid,
            "ocel:activity": activity,
            "ocel:timestamp": when,
            "case_no": case_no,
            "activity_index": activity_index,
            "technical_code": _code(s, activity_index),
            "actor": actor,
            "actor_role": role,
            "resource_calendar": "24X7" if role in {"TELEMETRY", "SOFTWARE", "PROCESS_OWNER"} else "WEEKDAY_DAY_SHIFT",
            "source_system": f"{s.prefix}_SRC_{activity_index % 3 + 1}",
            "reason": route_step["exception_reason"],
            "amount": amount,
            "currency": "EUR" if amount is not None else None,
            "quantity": quantity,
            "unit": "EA" if quantity is not None else None,
            "location": ("BER", "HAM", "MUC", "CGN", "FRA")[(case_no + activity_index) % 5],
            "changed_field": "lifecycle_status",
            "old_value": None,
            "new_value": state_from_activity(activity),
            "recorded_at": when + timedelta(minutes=lag_minutes),
            "is_exception": bool(route_step["is_exception"]),
            "exception_reason": route_step["exception_reason"],
            "loop_no": 1 if route_step["is_exception"] else 0,
            "object_refs": [oid for oid, _ in related],
        }
        events.append(event)
        subject_by_event[eid] = subject_oid
        for oid, qualifier in related:
            relations.append({
                "ocel:eid": eid,
                "ocel:activity": activity,
                "ocel:timestamp": when,
                "ocel:oid": oid,
                "ocel:type": objects[oid]["ocel:type"],
                "ocel:qualifier": qualifier,
            })

    case_bounds: dict[int, tuple[datetime, datetime]] = {}
    for case_no in range(1, instance_count + 1):
        jitter_hours = (case_no * case_no * 17 + case_no * 41) % 211
        current = base + timedelta(hours=case_no * 5 + jitter_hours, minutes=(case_no * 37) % 60)
        case_start = current
        route = build_route(s.slug, case_no)
        for position, route_step in enumerate(route):
            activity = route_step["activity"]
            if activity not in s.activities:
                raise AssertionError(f"Unknown activity in {s.slug} route: {activity}")
            idx = s.activities.index(activity)
            if position:
                current = next_time(current, case_no, position, idx, actor_role(s.slug, activity))
            add_event(case_no, activity, current, route_step, position)
        case_bounds[case_no] = (case_start, current)

    # Business-semantic object relations with explicit validity intervals.
    seen_o2o: set[tuple[str, str, str, str]] = set()
    for case_no, (case_start, case_end) in case_bounds.items():
        used = case_objects[case_no]
        for source_type, target_type, qualifier in O2O_EDGES[s.slug]:
            source = _object_id(s, source_type, case_no)
            target = _object_id(s, target_type, case_no)
            if source not in used or target not in used:
                continue
            key = (source, target, qualifier, _iso(case_start))
            if key in seen_o2o:
                continue
            seen_o2o.add(key)
            o2o.append({
                "ocel:oid": source,
                "ocel:oid_2": target,
                "ocel:qualifier": qualifier,
                "valid_from": case_start,
                "valid_to": case_end,
                "relation_state": "ACTIVE",
            })

    events.sort(key=lambda e: (e["ocel:timestamp"], e["ocel:eid"]))
    # Re-number after chronological ordering so IDs are stable and ordered.
    remap: dict[str, str] = {}
    for i, event in enumerate(events, 1):
        old = event["ocel:eid"]
        new = f"{s.prefix}-E-{i:08d}"
        remap[old] = new
        event["ocel:eid"] = new
    for relation in relations:
        relation["ocel:eid"] = remap[relation["ocel:eid"]]
    subject_by_event = {remap[eid]: oid for eid, oid in subject_by_event.items()}
    relations.sort(key=lambda r: (r["ocel:eid"], r["ocel:oid"], r["ocel:qualifier"]))
    # Derive semantically ordered old/new status values and temporal object
    # attributes after global timestamp ordering (important for shared objects).
    state_by_object: dict[str, str] = {}
    for event in events:
        subject_oid = subject_by_event[event["ocel:eid"]]
        prior = state_by_object.get(subject_oid, "IDENTIFIED")
        event["old_value"] = prior
        state_by_object[subject_oid] = event["new_value"]
        objects[subject_oid]["lifecycle_status"] = event["new_value"]
        changes.append({
            "ocel:oid": subject_oid,
            "ocel:type": objects[subject_oid]["ocel:type"],
            "ocel:timestamp": event["ocel:timestamp"],
            "ocel:field": "lifecycle_status",
            "lifecycle_status": event["new_value"],
        })
    return events, objects, relations, o2o, changes


def _connect_source(folder: Path) -> sqlite3.Connection:
    path = folder / "source.sqlite"
    if path.exists():
        path.unlink()
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA journal_mode=DELETE")
    conn.execute("PRAGMA synchronous=FULL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript((folder / "schema.sql").read_text(encoding="utf-8"))
    return conn


def _source_scope(s: Scenario, event: dict[str, Any], source_table: str) -> str:
    return f"{s.prefix}-S-{event['case_no']:06d}-{s.evidence_tables.index(source_table):02d}"


def _set_provenance(event: dict[str, Any], table: str, record_id: str) -> None:
    event["source_table"] = table
    event["source_record_id"] = record_id


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _insert_forgeflow(conn: sqlite3.Connection, s: Scenario, events: list[dict[str, Any]], instance_count: int) -> str:
    bridge: set[tuple[str, str]] = set()
    duplicate_rows = []
    rows: dict[str, list[tuple[Any, ...]]] = defaultdict(list)
    for n, event in enumerate(events, 1):
        table = s.evidence_tables[event["activity_index"] % len(s.evidence_tables)]
        scope = _source_scope(s, event, table)
        case_key = _object_id(s, CASE_TYPES[s.slug], event["case_no"])
        bridge.add((case_key, scope))
        rid = f"{s.prefix}-R-{n:08d}"
        when = event["ocel:timestamp"]
        refs = json.dumps(event["object_refs"], separators=(",", ":"))
        common = (rid, scope, refs, event["technical_code"], event["actor"], event["amount"], event["location"], f"TX-{n:08d}")
        if table == "commercial_document":
            rows[table].append(common + (when.strftime("%Y-%m-%d"), when.strftime("%H:%M:%S")))
        elif table == "engineering_execution":
            rows[table].append(common + (_iso(when), _iso(event["recorded_at"])))
        elif table == "supply_posting":
            rows[table].append(common + (when.strftime("%Y%m%d"), when.hour * 3600 + when.minute * 60 + when.second))
        elif table == "quality_observation":
            rows[table].append(common + (int(when.timestamp() * 1000), event["reason"]))
        elif table == "fulfilment_record":
            rows[table].append(common + (int(when.timestamp()), "UTC"))
        else:
            rows[table].append(common + (when.strftime("%Y-%m-%d"), when.strftime("%H%M%S")))
        if n % 4 == 0:
            duplicate_rows.append((f"MSG-{n:08d}", scope, f"TOPIC-{event['activity_index'] % 9:02d}", f"TX-{n:08d}", _iso(when + timedelta(seconds=3)), refs, 0))
        _set_provenance(event, table, rid)

    conn.executemany("INSERT INTO document_conversion(predecessor_key,successor_key,conversion_code,valid_from) VALUES(?,?, 'ROOT', '2020-01-01')", sorted(bridge))
    for table in s.evidence_tables:
        if table == "commercial_document":
            sql = f"INSERT INTO {table}(record_key,document_ref,related_refs_json,state_code,operator_code,amount_value,location_code,transaction_ref,created_day,created_clock) VALUES(?,?,?,?,?,?,?,?,?,?)"
        elif table == "engineering_execution":
            sql = f"INSERT INTO {table}(record_key,job_ref,related_refs_json,phase_code,operator_code,amount_value,location_code,transaction_ref,effective_at,recorded_at) VALUES(?,?,?,?,?,?,?,?,?,?)"
        elif table == "supply_posting":
            sql = f"INSERT INTO {table}(record_key,supply_ref,related_refs_json,movement_code,operator_code,amount_value,location_code,transaction_ref,posting_day,posting_seconds) VALUES(?,?,?,?,?,?,?,?,?,?)"
        elif table == "quality_observation":
            sql = f"INSERT INTO {table}(record_key,inspection_ref,related_refs_json,result_code,operator_code,amount_value,location_code,transaction_ref,observed_epoch_ms,reason_code) VALUES(?,?,?,?,?,?,?,?,?,?)"
        elif table == "fulfilment_record":
            sql = f"INSERT INTO {table}(record_key,fulfilment_ref,related_refs_json,milestone_code,operator_code,amount_value,location_code,transaction_ref,milestone_epoch,timezone_code) VALUES(?,?,?,?,?,?,?,?,?,?)"
        else:
            sql = f"INSERT INTO {table}(record_key,posting_ref,related_refs_json,posting_code,operator_code,amount_value,location_code,transaction_ref,effective_day,effective_clock) VALUES(?,?,?,?,?,?,?,?,?,?)"
        conn.executemany(sql, rows[table])
    conn.executemany("INSERT INTO integration_outbox(message_id,aggregate_ref,topic_code,transaction_ref,queued_at,payload_json,published_flag) VALUES(?,?,?,?,?,?,?)", duplicate_rows)

    current = _row_count(conn)
    padding = []
    for i in range(current + 1, MIN_SOURCE_ROWS + 1):
        padding.append((f"TECH-{i:08d}", f"SYS-{i % 31:02d}", f"KEEPALIVE-{i % 7}", f"TX-T-{i:08d}", "2024-01-01T00:00:00Z", "{}", 1))
    conn.executemany("INSERT INTO integration_outbox(message_id,aggregate_ref,topic_code,transaction_ref,queued_at,payload_json,published_flag) VALUES(?,?,?,?,?,?,?)", padding)
    return _forge_query(s)


VERSION_TABLES = (
    "study_v", "protocol_v", "site_v", "investigator_v", "participant_v", "consent_v", "visit_v", "drug_kit_v", "dispensation_v", "dose_v", "sample_v", "aliquot_v", "sample_shipment_v", "shipment_item_v", "lab_order_v", "lab_test_v", "lab_result_v", "adverse_event_v", "protocol_deviation_v", "data_query_v",
)


def _insert_trialversion(conn: sqlite3.Connection, s: Scenario, events: list[dict[str, Any]], instance_count: int) -> str:
    versions: dict[tuple[str, str], int] = defaultdict(int)
    last_record: dict[tuple[str, str], str] = {}
    rows: dict[str, list[tuple[Any, ...]]] = defaultdict(list)
    relation_rows: dict[tuple[str, str], tuple[Any, ...]] = {}
    sessions = []
    for n, event in enumerate(events, 1):
        table = s.evidence_tables[event["activity_index"] % len(s.evidence_tables)]
        logical_id = _source_scope(s, event, table)
        key = (table, logical_id)
        versions[key] += 1
        version_no = versions[key]
        if version_no == 1:
            baseline_id = f"{logical_id}:V000"
            rows[table].append((baseline_id, logical_id, 0, "2022-01-01T00:00:00Z", _iso(event["ocel:timestamp"]), "2022-01-01T00:00:01Z", f"ES-B-{n:08d}", None, "IMPORT_REPLAY", "MIG", "SYSTEM", 0, 0, f"H-B-{n:08d}", "B000", json.dumps(event["object_refs"]), event["actor"], event["amount"], event["location"], "{}"))
            last_record[key] = baseline_id
        rid = f"{logical_id}:V{version_no:03d}"
        when = event["ocel:timestamp"]
        sessions.append((f"ES-{n:08d}", event["actor"], _iso(event["recorded_at"]), "SAVE", event["reason"]))
        rows[table].append((rid, logical_id, version_no, _iso(when), None, _iso(event["recorded_at"]), f"ES-{n:08d}", version_no - 1, "BUSINESS", event["reason"], event["actor"], 1, 0, f"H-{n:08d}", event["technical_code"], json.dumps(event["object_refs"]), event["actor"], event["amount"], event["location"], json.dumps({"effectiveAt": _iso(when)}, separators=(",", ":"))))
        last_record[key] = rid
        case_key = _object_id(s, CASE_TYPES[s.slug], event["case_no"])
        relation_rows[(logical_id, case_key)] = (f"REL-{logical_id}", "VersionedRecord", logical_id, CASE_TYPES[s.slug], case_key, "SCOPE", "2022-01-01T00:00:00Z", None, "2022-01-01T00:00:01Z", "ES-REL", "BUSINESS")
        if n % 3 == 0:
            versions[key] += 1
            correction_no = versions[key]
            correction_id = f"{logical_id}:V{correction_no:03d}"
            rows[table].append((correction_id, logical_id, correction_no, _iso(when), None, _iso(event["recorded_at"] + timedelta(days=1)), f"ES-C-{n:08d}", correction_no - 1, "CORRECTION", "TYPO", event["actor"], 1, 0, f"H-C-{n:08d}", event["technical_code"], json.dumps(event["object_refs"]), event["actor"], event["amount"], event["location"], "{\"corrected\":true}"))
        _set_provenance(event, table, rid)

    insert_sql = "(record_id,logical_id,version_no,valid_from,valid_to,recorded_at,edit_session_id,supersedes_version_no,change_kind,change_reason_code,changed_by,is_current,is_deleted,row_hash,state_code,related_refs_json,actor_code,amount_value,location_code,payload_json) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
    for table, table_rows in rows.items():
        conn.executemany(f"INSERT INTO {table}{insert_sql}", table_rows)
    conn.executemany("INSERT OR IGNORE INTO edit_session(edit_session_id,edited_by,recorded_at,session_kind,reason_code) VALUES(?,?,?,?,?)", sessions)
    conn.executemany("INSERT INTO object_relation_v(relation_id,source_type,source_logical_id,target_type,target_logical_id,qualifier_code,valid_from,valid_to,recorded_at,edit_session_id,change_kind) VALUES(?,?,?,?,?,?,?,?,?,?,?)", relation_rows.values())
    _pad_simple(conn, "edit_session", "INSERT INTO edit_session(edit_session_id,edited_by,recorded_at,session_kind,reason_code) VALUES(?,?,?,?,?)", lambda i: (f"ES-T-{i:08d}", "SYSTEM", "2024-01-01T00:00:00Z", "SYSTEM_RECALCULATION", f"N{i % 9}"))
    return _trial_query(s)


APP_TABLES = ("req_header", "goods_movement_header", "inspection_lot", "invoice_header", "accounting_header", "payment_run")


def _insert_procurechange(conn: sqlite3.Connection, s: Scenario, events: list[dict[str, Any]], instance_count: int) -> str:
    cdhdr = []
    cdpos = []
    archive_h = []
    archive_p = []
    app_rows: dict[str, list[tuple[Any, ...]]] = defaultdict(list)
    flow: set[tuple[str, str, str]] = set()
    for n, event in enumerate(events, 1):
        use_change = event["activity_index"] < len(s.activities) // 2
        scope = f"{s.prefix}-DOC-{n:010d}"
        case_key = _object_id(s, CASE_TYPES[s.slug], event["case_no"])
        flow.add((case_key, scope, "FOLLOW_ON"))
        for object_ref in event["object_refs"]:
            flow.add((scope, object_ref, "OBJECT_SCOPE"))
        when = event["ocel:timestamp"]
        refs = json.dumps(event["object_refs"], separators=(",", ":"))
        if use_change:
            table = "cdhdr"
            change_no = f"CHG{n:010d}"
            target_h = archive_h if n % 7 == 0 else cdhdr
            target_p = archive_p if n % 7 == 0 else cdpos
            target_h.append(("100", "PROC_DOC", scope, change_no, event["actor"], when.strftime("%Y%m%d"), when.strftime("%H%M%S"), f"T{event['activity_index'] % 23:03d}", "U", event["source_system"]))
            packed = "100" + f"{event['case_no']:010d}" + f"{event['activity_index'] + 1:05d}"
            target_p.append(("100", "PROC_DOC", scope, change_no, "PO_ITEM", packed, event["technical_code"], "U", event["old_value"], event["new_value"], "EA", "EA", "EUR", "CHAR"))
            target_p.append(("100", "PROC_DOC", scope, change_no, "PO_ITEM", packed, f"AUX{event['activity_index'] % 8}", "U", "0", "1", None, None, None, "NUM"))
            if n % 29 == 0 and n % 7 == 0:
                cdhdr.append(target_h[-1])
                cdpos.extend(target_p[-2:])
            rid = change_no
        else:
            table = APP_TABLES[event["activity_index"] % len(APP_TABLES)]
            rid = f"APP-{n:010d}"
            app_rows[table].append((rid, scope, event["technical_code"], when.strftime("%Y%m%d"), when.strftime("%H%M%S"), event["actor"], event["amount"], event["location"], refs, f"TX-{n:08d}", 0))
        _set_provenance(event, table, rid)
    conn.executemany("INSERT INTO cdhdr(client,object_class,object_id,change_number,username,change_date,change_time,transaction_code,change_indicator,source_system) VALUES(?,?,?,?,?,?,?,?,?,?)", cdhdr)
    conn.executemany("INSERT INTO cdpos(client,object_class,object_id,change_number,table_name,table_key,field_name,change_indicator,old_value_text,new_value_text,old_unit,new_unit,currency_code,value_type_code) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", cdpos)
    conn.executemany("INSERT INTO archive_cdhdr(client,object_class,object_id,change_number,username,change_date,change_time,transaction_code,change_indicator,source_system) VALUES(?,?,?,?,?,?,?,?,?,?)", archive_h)
    conn.executemany("INSERT INTO archive_cdpos(client,object_class,object_id,change_number,table_name,table_key,field_name,change_indicator,old_value_text,new_value_text,old_unit,new_unit,currency_code,value_type_code) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", archive_p)
    conn.executemany("INSERT INTO document_flow(predecessor_id,successor_id,relation_code,created_at) VALUES(?,?,?,'2022-01-01T00:00:00Z')", sorted(flow))
    for table, table_rows in app_rows.items():
        conn.executemany(f"INSERT INTO {table}(record_key,document_ref,document_code,posting_date,posting_time,username,amount_value,location_code,related_refs_json,transaction_ref,is_reversal) VALUES(?,?,?,?,?,?,?,?,?,?,?)", table_rows)
    conn.execute("INSERT INTO tabkey_layout(table_name,component_no,field_name,start_pos,field_length,data_type) VALUES('PO_ITEM',1,'CLIENT',1,3,'CHAR'),('PO_ITEM',2,'DOCNO',4,10,'NUMC'),('PO_ITEM',3,'ITEMNO',14,5,'NUMC')")
    conn.executemany("INSERT INTO field_catalog(table_name,field_name,data_type,domain_name,decimal_scale) VALUES('PO_ITEM',?,'CHAR','TECH_STATE',0)", [( _code(s, i),) for i in range(len(s.activities))])
    _pad_simple(conn, "approval_step", "INSERT INTO approval_step(step_id,workflow_id,step_code,status_code,changed_at,actor_code) VALUES(?,?,?,?,?,?)", lambda i: (f"STEP-T-{i:08d}", f"WF-{i % 9000:06d}", f"S{i % 17:02d}", "RECALC", "2024-01-01T00:00:00Z", "SYSTEM"))
    return _procure_query(s)


def _claim_payload(event: dict[str, Any], version: int) -> str:
    effective = _iso(event["ocel:timestamp"])
    base = {"claimRef": event["object_refs"][0], "objectRefs": event["object_refs"], "effectiveAt": effective}
    if event["amount"] is not None:
        if version == 1:
            base.update({"amount": int(round(event["amount"] * 100)), "currency": "EUR_CENTS"})
        elif version == 2:
            base.update({"amount": event["amount"], "currency": "EUR"})
        else:
            base.update({"money": {"value": f"{event['amount']:.2f}", "currency": "EUR"}})
    return json.dumps(base, separators=(",", ":"), sort_keys=True)


def _insert_claimstream(conn: sqlite3.Connection, s: Scenario, events: list[dict[str, Any]], instance_count: int) -> str:
    aliases = []
    for idx in range(len(s.activities)):
        aliases.append((f"Mutation{idx + 1:03d}CommittedV1", 1, _code(s, idx)))
        aliases.append((f"Mutation{idx + 1:03d}CommittedV2", 2, _code(s, idx)))
        aliases.append((f"Mutation{idx + 1:03d}CommittedV3", 3, _code(s, idx)))
    conn.executemany("INSERT INTO event_type_alias(event_type,schema_version,semantic_code) VALUES(?,?,?)", aliases)
    store = []
    commands = []
    inbox = []
    documents = []
    global_pos = 0
    stream_versions: Counter[str] = Counter()
    for n, event in enumerate(events, 1):
        idx = event["activity_index"]
        source_slot = idx % 4
        version = idx % 3 + 1
        event_type = f"Mutation{idx + 1:03d}CommittedV{version}"
        correlation = f"COR-{n:010d}"
        payload = _claim_payload(event, version)
        recorded = _iso(event["recorded_at"])
        when = _iso(event["ocel:timestamp"])
        if idx < len(s.activities) // 2:
            table = "event_store"
            global_pos += 1
            stream_id = f"claim-{event['case_no']:06d}" if idx % 2 == 0 else f"exposure-{event['case_no']:06d}-{idx % 5}"
            stream_versions[stream_id] += 1
            store.append((global_pos, stream_id, "CLAIM" if idx % 2 == 0 else "EXPOSURE", stream_versions[stream_id], event_type, version, when, recorded, payload, json.dumps({"actor": event["actor"], "location": event["location"]}, separators=(",", ":")), correlation, f"CAUSE-{n:08d}", "TENANT-DE", 0))
            rid = str(global_pos)
            if n % 4 == 0:
                global_pos += 1
                stream_versions[stream_id] += 1
                store.append((global_pos, stream_id, "CLAIM", stream_versions[stream_id], event_type, version, when, recorded, payload, "{\"retry\":true}", correlation, f"CAUSE-{n:08d}", "TENANT-DE", 0))
        elif source_slot == 2:
            table = "command_result"
            rid = f"CMD-{n:010d}"
            commands.append((rid, f"claim-{event['case_no']:06d}", event_type, _code(s, idx), "APPLIED", when, recorded, payload, correlation, event["actor"]))
        else:
            if idx % 8 == 3:
                table = "inbox_message"
                rid = f"IN-{n:010d}"
                inbox.append((rid, f"provider-{n % 31}", event_type, _code(s, idx), when, recorded, payload, correlation, 1))
            else:
                table = "document_index"
                rid = f"DOC-{n:010d}"
                documents.append((rid, f"claim-{event['case_no']:06d}", event_type, _code(s, idx), when, recorded, payload, correlation, "ACTIVE"))
        _set_provenance(event, table, rid)
    conn.executemany("INSERT INTO event_store(global_position,stream_id,stream_type,stream_version,event_type,schema_version,occurred_at,recorded_at,payload_json,metadata_json,correlation_id,causation_id,tenant_id,is_redacted) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", store)
    conn.executemany("INSERT INTO command_result(result_id,stream_id,event_type,semantic_code,result_code,occurred_at,recorded_at,payload_json,correlation_id,actor_code) VALUES(?,?,?,?,?,?,?,?,?,?)", commands)
    conn.executemany("INSERT INTO inbox_message(message_id,sender_ref,event_type,semantic_code,occurred_at,recorded_at,payload_json,correlation_id,processed_flag) VALUES(?,?,?,?,?,?,?,?,?)", inbox)
    conn.executemany("INSERT INTO document_index(document_id,stream_id,event_type,semantic_code,effective_at,indexed_at,payload_json,correlation_id,index_status) VALUES(?,?,?,?,?,?,?,?,?)", documents)
    technical_types = ("ProjectionRebuildStarted", "SnapshotWritten", "CommandAccepted", "OutboxMessageQueued", "SagaCheckpointStored", "ReadModelRepaired", "PayloadRedacted")
    while _row_count(conn) < MIN_SOURCE_ROWS:
        batch = []
        start = _row_count(conn)
        for j in range(min(10000, MIN_SOURCE_ROWS - start)):
            i = start + j + 1
            global_pos += 1
            stream_id = f"technical-{i % 997:04d}"
            stream_versions[stream_id] += 1
            batch.append((global_pos, stream_id, "TECHNICAL", stream_versions[stream_id], technical_types[i % len(technical_types)], 1, "2024-01-01T00:00:00Z", "2024-01-01T00:00:01Z", "{}", "{\"technical\":true}", f"TECH-COR-{i:08d}", None, "TENANT-DE", 0))
        conn.executemany("INSERT INTO event_store(global_position,stream_id,stream_type,stream_version,event_type,schema_version,occurred_at,recorded_at,payload_json,metadata_json,correlation_id,causation_id,tenant_id,is_redacted) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", batch)
    return _claim_query(s)


def _insert_permitflow(conn: sqlite3.Connection, s: Scenario, events: list[dict[str, Any]], instance_count: int) -> str:
    definitions = [(f"DEF-{v}", "permit_process", v, f"DEP-{v}") for v in range(1, 4)]
    conn.executemany("INSERT INTO wf_process_definition(process_definition_id,definition_key,version_no,deployment_id) VALUES(?,?,?,?)", definitions)
    metadata = []
    for version in range(1, 4):
        for idx in range(len(s.activities)):
            technical = f"{('Task','Activity','Node')[version - 1]}_{idx + 1:04x}"
            metadata.append((f"DEF-{version}", technical, _code(s, idx), f"ROLE_{idx + 1:03d}"))
    conn.executemany("INSERT INTO wf_definition_metadata(process_definition_id,activity_id,semantic_code,semantic_role) VALUES(?,?,?,?)", metadata)
    instances = []
    executions = []
    variables = []
    event_bounds: dict[int, tuple[datetime, datetime]] = {}
    by_case: dict[int, list[datetime]] = defaultdict(list)
    for event in events:
        by_case[event["case_no"]].append(event["ocel:timestamp"])
    for case_no, timestamps in by_case.items():
        event_bounds[case_no] = (min(timestamps) - timedelta(hours=1), max(timestamps))
    for case_no in range(1, instance_count + 1):
        version = case_no % 3 + 1
        pi = f"PI-{case_no:06d}"
        ex = f"EX-{case_no:06d}"
        root = _object_id(s, CASE_TYPES[s.slug], case_no)
        started, ended = event_bounds[case_no]
        started_text = _iso(started)
        instances.append((pi, f"DEF-{version}", pi, None, started_text, _iso(ended), "COMPLETED"))
        executions.append((ex, None, pi, pi, None, "ROOT", 1, 0, started_text, _iso(ended), None))
        variables.append((f"VAR-{case_no:06d}-1", ex, pi, "application_ref", 1, root, "TEXT", started_text, None))
        variables.append((f"VAR-{case_no:06d}-2", ex, pi, "plan_revision_ref", 1, f"PLAN-{case_no:06d}-1", "TEXT", started_text, None))
    conn.executemany("INSERT INTO wf_process_instance(process_instance_id,process_definition_id,root_process_instance_id,super_process_instance_id,start_time,end_time,state_code) VALUES(?,?,?,?,?,?,?)", instances)
    conn.executemany("INSERT INTO wf_execution(execution_id,parent_execution_id,process_instance_id,root_process_instance_id,super_process_instance_id,activity_id,is_scope,is_concurrent,created_at,ended_at,delete_reason) VALUES(?,?,?,?,?,?,?,?,?,?,?)", executions)
    conn.executemany("INSERT INTO wf_variable_history(variable_id,execution_id,process_instance_id,name,revision_no,value_text,value_type,created_at,ended_at) VALUES(?,?,?,?,?,?,?,?,?)", variables)

    # Current domain projection duplicates the workflow submission evidence for
    # this one milestone. Extraction must fuse/choose the workflow transaction,
    # not emit a second event from the projection update.
    submissions = {}
    for event in events:
        if event["ocel:activity"] == "Application Submitted":
            app_ref = _object_id(s, CASE_TYPES[s.slug], event["case_no"])
            submissions[app_ref] = (app_ref, "SUBMITTED", _iso(event["ocel:timestamp"]), _iso(event["recorded_at"]))
    conn.executemany("INSERT INTO permit_application(application_ref,current_state_code,submitted_at,updated_at) VALUES(?,?,?,?)", submissions.values())

    rows: dict[str, list[tuple[Any, ...]]] = defaultdict(list)
    for n, event in enumerate(events, 1):
        table = s.evidence_tables[event["activity_index"] % len(s.evidence_tables)]
        version = event["case_no"] % 3 + 1
        technical = f"{('Task','Activity','Node')[version - 1]}_{event['activity_index'] + 1:04x}"
        pi = f"PI-{event['case_no']:06d}"
        ex = f"EX-{event['case_no']:06d}"
        rid = f"WF-{n:010d}"
        when = _iso(event["ocel:timestamp"])
        refs = json.dumps(event["object_refs"], separators=(",", ":"))
        base = (rid, ex, pi, f"DEF-{version}", technical, event["actor"], refs, event["amount"], event["location"], f"TX-{n:08d}")
        if table == "wf_activity_history":
            rows[table].append(base + (when, when, "COMPLETE"))
        elif table == "wf_task_history":
            rows[table].append(base + (_iso(event["ocel:timestamp"] - timedelta(minutes=15)), when, "OK", None))
        elif table == "wf_message_delivery":
            rows[table].append(base + (when, f"MSG-{event['activity_index'] % 13:02d}", "CORRELATED"))
        elif table == "wf_form_submission":
            rows[table].append(base + (when, f"FORM-{event['activity_index'] % 17:02d}", "{}"))
        else:
            rows[table].append(base + (when, "COMPLETED", None))
        _set_provenance(event, table, rid)
    conn.executemany("INSERT INTO wf_activity_history(history_id,execution_id,process_instance_id,process_definition_id,activity_id,actor_code,related_refs_json,amount_value,location_code,transaction_ref,start_time,end_time,lifecycle_code) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", rows["wf_activity_history"])
    conn.executemany("INSERT INTO wf_task_history(task_id,execution_id,process_instance_id,process_definition_id,activity_id,assignee_code,related_refs_json,amount_value,location_code,transaction_ref,start_time,end_time,outcome_code,delete_reason) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rows["wf_task_history"])
    conn.executemany("INSERT INTO wf_message_delivery(delivery_id,execution_id,process_instance_id,process_definition_id,activity_id,actor_code,related_refs_json,amount_value,location_code,transaction_ref,delivered_at,message_code,result_code) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", rows["wf_message_delivery"])
    conn.executemany("INSERT INTO wf_form_submission(submission_id,execution_id,process_instance_id,process_definition_id,activity_id,submitted_by,related_refs_json,amount_value,location_code,transaction_ref,submitted_at,form_key,payload_json) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", rows["wf_form_submission"])
    conn.executemany("INSERT INTO wf_external_task(external_task_id,execution_id,process_instance_id,process_definition_id,activity_id,worker_code,related_refs_json,amount_value,location_code,transaction_ref,completed_at,state_code,error_code) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", rows["wf_external_task"])
    _pad_simple(conn, "wf_job_log", "INSERT INTO wf_job_log(job_log_id,process_instance_id,job_type,retry_no,created_at,ended_at,result_code) VALUES(?,?,?,?,?,?,?)", lambda i: (f"JOB-{i:09d}", f"PI-{i % instance_count + 1:06d}", f"TIMER-{i % 19:02d}", i % 4, "2024-01-01T00:00:00Z", "2024-01-01T00:00:01Z", "TECHNICAL"))
    return _permit_query(s)


SATELLITE_TABLES = (
    "sat_cell_batch_status", "sat_module_status", "sat_pack_status", "sat_pack_specification", "sat_pack_test", "sat_passport_data", "sat_vehicle_status", "sat_ownership_role", "sat_telemetry_summary", "sat_diagnostic_result", "sat_service_status", "sat_campaign_status", "sat_claim_status", "sat_recall_status", "sat_shipment_status", "sat_second_life_status", "sat_recycling_status", "sat_certificate_status", "sat_incident_status",
)

HUBS = {
    "CellBatch": "hub_cell_batch", "Module": "hub_module", "BatteryPack": "hub_battery_pack", "BatteryPassport": "hub_passport", "Vehicle": "hub_vehicle", "Owner": "hub_party", "ServiceOrder": "hub_service_order", "DiagnosticTest": "hub_diagnostic", "FirmwareCampaign": "hub_firmware_campaign", "WarrantyClaim": "hub_warranty_claim", "RecallCampaign": "hub_recall_campaign", "Shipment": "hub_shipment", "Warehouse": "hub_warehouse", "SecondLifeSystem": "hub_second_life_system", "RecyclingOrder": "hub_recycling_order", "MaterialBatch": "hub_material_batch", "Certificate": "hub_certificate", "Incident": "hub_incident",
}


def _insert_batteryvault(conn: sqlite3.Connection, s: Scenario, events: list[dict[str, Any]], objects: dict[str, dict[str, Any]], instance_count: int) -> str:
    hub_rows: dict[str, list[tuple[Any, ...]]] = defaultdict(list)
    for obj in objects.values():
        table = HUBS[obj["ocel:type"]]
        hub_rows[table].append((obj["ocel:oid"], obj["business_key"], "2023-01-01T00:00:00Z", f"{s.prefix}_MASTER"))
    for table, rows in hub_rows.items():
        conn.executemany(f"INSERT INTO {table}(hub_key,business_key,load_dts,record_source) VALUES(?,?,?,?)", rows)

    ledger_activities = {"Ownership Transferred", "Lease Started", "Lease Ended", "Shipment Dispatched", "Shipment Received", "Battery Removed from Vehicle"}
    sat_rows: dict[str, list[tuple[Any, ...]]] = defaultdict(list)
    versions: Counter[tuple[str, str]] = Counter()
    journals = []
    entries = []
    for n, event in enumerate(events, 1):
        # The operational root and canonical case is the BatteryPack hub.
        parent_key = event["object_refs"][0]
        when = event["ocel:timestamp"]
        refs = json.dumps(event["object_refs"], separators=(",", ":"))
        if event["ocel:activity"] in ledger_activities:
            table = "asset_journal"
            rid = f"JRN-{n:010d}"
            journals.append((rid, event["technical_code"], _iso(when), _iso(event["recorded_at"]), event["source_system"], "POSTED", refs, event["actor"], event["location"], event["amount"]))
            entries.append((f"LE-{n:010d}-C", rid, "WAREHOUSE", f"WH-{event['case_no'] % 31:03d}", objects[parent_key]["ocel:type"], parent_key, "CREDIT", 1.0, _iso(when), _iso(event["recorded_at"]), None, event["source_system"]))
            entries.append((f"LE-{n:010d}-D", rid, "CUSTODY", f"AC-{event['case_no'] % 47:03d}", objects[parent_key]["ocel:type"], parent_key, "DEBIT", 1.0, _iso(when), _iso(event["recorded_at"]), None, event["source_system"]))
        else:
            table = s.evidence_tables[event["activity_index"] % (len(s.evidence_tables) - 1)]
            versions[(table, parent_key)] += 1
            seq = versions[(table, parent_key)]
            rid = f"{table}:{parent_key}:{seq:04d}"
            sat_rows[table].append((rid, parent_key, _iso(event["recorded_at"]), _iso(when), None, f"HD-{event['technical_code']}-{n}", event["source_system"], seq, 0, event["technical_code"], refs, event["actor"], event["amount"], event["location"]))
            if n % 5 == 0:
                sat_rows[table].append((f"{rid}:REPLAY", parent_key, _iso(event["recorded_at"] + timedelta(days=1)), _iso(when), None, f"HD-{event['technical_code']}-{n}", f"{s.prefix}_REPLAY", seq + 100000, 1, event["technical_code"], refs, event["actor"], event["amount"], event["location"]))
        _set_provenance(event, table, rid)
    sat_sql = "(satellite_id,parent_key,load_dts,effective_from,effective_to,hashdiff,record_source,source_sequence,is_correction,state_code,related_refs_json,actor_code,amount_value,location_code) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
    for table, rows in sat_rows.items():
        conn.executemany(f"INSERT INTO {table}{sat_sql}", rows)
    conn.executemany("INSERT INTO asset_journal(journal_id,movement_code,effective_at,posted_at,source_system,status_code,related_refs_json,actor_code,location_code,amount_value) VALUES(?,?,?,?,?,?,?,?,?,?)", journals)
    conn.executemany("INSERT INTO asset_ledger_entry(entry_id,journal_id,account_type,account_id,asset_type,asset_hub_key,direction,quantity,effective_at,posted_at,reversal_of_entry_id,source_system) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", entries)
    _pad_simple(conn, "sat_telemetry_summary", "INSERT INTO sat_telemetry_summary(satellite_id,parent_key,load_dts,effective_from,effective_to,hashdiff,record_source,source_sequence,is_correction,state_code,related_refs_json,actor_code,amount_value,location_code) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", lambda i: (f"TEL-{i:09d}", _object_id(s, CASE_TYPES[s.slug], i % instance_count + 1), "2024-01-01T01:00:00Z", "2024-01-01T00:00:00Z", None, f"TEL-HD-{i % 997}", "TELEMETRY", i, 0, "NORMAL", "[]", "SENSOR", float(i % 100), f"Z{i % 9}"))
    return _battery_query(s)


def _row_count(conn: sqlite3.Connection) -> int:
    total = 0
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
    for table in tables:
        total += conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
    return total


def _pad_simple(conn: sqlite3.Connection, table: str, sql: str, factory: Any) -> None:
    current = _row_count(conn)
    needed = max(0, MIN_SOURCE_ROWS - current)
    for start in range(0, needed, 10000):
        stop = min(needed, start + 10000)
        conn.executemany(sql, [factory(i + 1) for i in range(start, stop)])


def _forge_query(s: Scenario) -> str:
    mapping = _mapping_case(s, "technical_code")
    unions = [
        "SELECT record_key source_record_id, document_ref scope_key, state_code technical_code, created_day||'T'||created_clock||'Z' timestamp, operator_code actor, related_refs_json object_refs, 'commercial_document' source_table FROM commercial_document",
        "SELECT record_key, job_ref, phase_code, effective_at, operator_code, related_refs_json, 'engineering_execution' FROM engineering_execution",
        "SELECT record_key, supply_ref, movement_code, substr(posting_day,1,4)||'-'||substr(posting_day,5,2)||'-'||substr(posting_day,7,2)||'T'||printf('%02d:%02d:%02d',posting_seconds/3600,(posting_seconds/60)%60,posting_seconds%60)||'Z', operator_code, related_refs_json, 'supply_posting' FROM supply_posting",
        "SELECT record_key, inspection_ref, result_code, strftime('%Y-%m-%dT%H:%M:%SZ',observed_epoch_ms/1000,'unixepoch'), operator_code, related_refs_json, 'quality_observation' FROM quality_observation",
        "SELECT record_key, fulfilment_ref, milestone_code, strftime('%Y-%m-%dT%H:%M:%SZ',milestone_epoch,'unixepoch'), operator_code, related_refs_json, 'fulfilment_record' FROM fulfilment_record",
        "SELECT record_key, posting_ref, posting_code, substr(effective_day,1,10)||'T'||substr(effective_clock,1,2)||':'||substr(effective_clock,3,2)||':'||substr(effective_clock,5,2)||'Z', operator_code, related_refs_json, 'finance_posting' FROM finance_posting",
    ]
    return f"WITH raw(source_record_id,scope_key,technical_code,timestamp,actor,object_refs,source_table) AS ({' UNION ALL '.join(unions)}), mapped AS (SELECT *, {mapping} activity FROM raw) SELECT dc.predecessor_key case_id, activity, timestamp, source_table, source_record_id, actor, object_refs FROM mapped JOIN document_conversion dc ON dc.successor_key=mapped.scope_key WHERE activity IS NOT NULL ORDER BY case_id, timestamp, source_record_id"


def _trial_query(s: Scenario) -> str:
    mapping = _mapping_case(s, "state_code")
    unions = [f"SELECT record_id, logical_id, version_no, valid_from, recorded_at, change_kind, state_code, changed_by, related_refs_json, '{table}' source_table, LAG(state_code) OVER(PARTITION BY logical_id ORDER BY version_no) prev_state FROM {table}" for table in s.evidence_tables]
    return f"WITH versions AS ({' UNION ALL '.join(unions)}), business AS (SELECT *, {mapping} activity FROM versions WHERE change_kind='BUSINESS') SELECT r.target_logical_id case_id, business.activity, business.valid_from timestamp, business.source_table, business.record_id source_record_id, business.changed_by actor, business.related_refs_json object_refs FROM business JOIN object_relation_v r ON r.source_logical_id=business.logical_id AND r.change_kind='BUSINESS' WHERE business.activity IS NOT NULL ORDER BY case_id, timestamp, source_record_id"


def _procure_query(s: Scenario) -> str:
    mapping_change = _mapping_case(s, "technical_code")
    mapping_app = _mapping_case(s, "document_code")
    app_union = " UNION ALL ".join(f"SELECT record_key source_record_id, document_ref scope_key, document_code, substr(posting_date,1,4)||'-'||substr(posting_date,5,2)||'-'||substr(posting_date,7,2)||'T'||substr(posting_time,1,2)||':'||substr(posting_time,3,2)||':'||substr(posting_time,5,2)||'Z' timestamp, username actor, related_refs_json object_refs, '{table}' source_table FROM {table}" for table in APP_TABLES)
    return f"WITH all_h AS (SELECT *,0 archived FROM cdhdr UNION ALL SELECT *,1 FROM archive_cdhdr), dedup_h AS (SELECT * FROM (SELECT *,ROW_NUMBER() OVER(PARTITION BY change_number ORDER BY archived) rn FROM all_h) WHERE rn=1), all_p AS (SELECT * FROM cdpos UNION ALL SELECT * FROM archive_cdpos), scope_refs AS (SELECT predecessor_id scope_key,json_group_array(successor_id) object_refs FROM document_flow WHERE relation_code='OBJECT_SCOPE' GROUP BY predecessor_id), changes AS (SELECT h.change_number source_record_id,h.object_id scope_key,MAX(CASE WHEN p.field_name LIKE '{s.prefix}%' THEN p.field_name END) technical_code,substr(h.change_date,1,4)||'-'||substr(h.change_date,5,2)||'-'||substr(h.change_date,7,2)||'T'||substr(h.change_time,1,2)||':'||substr(h.change_time,3,2)||':'||substr(h.change_time,5,2)||'Z' timestamp,h.username actor,sr.object_refs,'cdhdr' source_table FROM dedup_h h JOIN all_p p USING(client,object_class,object_id,change_number) JOIN scope_refs sr ON sr.scope_key=h.object_id GROUP BY h.change_number,h.object_id,h.change_date,h.change_time,h.username,sr.object_refs), mapped_changes AS (SELECT *,{mapping_change} activity FROM changes), apps AS ({app_union}), mapped_apps AS (SELECT *,{mapping_app} activity FROM apps), all_events AS (SELECT * FROM mapped_changes UNION ALL SELECT source_record_id,scope_key,document_code,timestamp,actor,object_refs,source_table,activity FROM mapped_apps) SELECT f.predecessor_id case_id,e.activity,e.timestamp,e.source_table,e.source_record_id,e.actor,e.object_refs FROM all_events e JOIN document_flow f ON f.successor_id=e.scope_key AND f.relation_code='FOLLOW_ON' WHERE activity IS NOT NULL ORDER BY case_id,timestamp,source_record_id"


def _claim_query(s: Scenario) -> str:
    mapping = _mapping_case(s, "semantic_code")
    return f"WITH raw AS (SELECT CAST(e.global_position AS TEXT) source_record_id,a.semantic_code,json_extract(e.payload_json,'$.claimRef') case_id,json_extract(e.payload_json,'$.effectiveAt') timestamp,json_extract(e.metadata_json,'$.actor') actor,json_extract(e.payload_json,'$.objectRefs') object_refs,'event_store' source_table,e.correlation_id FROM event_store e JOIN event_type_alias a USING(event_type,schema_version) WHERE e.stream_type<>'TECHNICAL' UNION ALL SELECT result_id,semantic_code,json_extract(payload_json,'$.claimRef'),json_extract(payload_json,'$.effectiveAt'),actor_code,json_extract(payload_json,'$.objectRefs'),'command_result',correlation_id FROM command_result WHERE result_code='APPLIED' UNION ALL SELECT message_id,semantic_code,json_extract(payload_json,'$.claimRef'),json_extract(payload_json,'$.effectiveAt'),'EXTERNAL',json_extract(payload_json,'$.objectRefs'),'inbox_message',correlation_id FROM inbox_message WHERE processed_flag=1 UNION ALL SELECT document_id,semantic_code,json_extract(payload_json,'$.claimRef'),json_extract(payload_json,'$.effectiveAt'),'INDEXER',json_extract(payload_json,'$.objectRefs'),'document_index',correlation_id FROM document_index WHERE index_status='ACTIVE'), fused AS (SELECT *,ROW_NUMBER() OVER(PARTITION BY correlation_id,semantic_code ORDER BY CASE source_table WHEN 'event_store' THEN 1 ELSE 2 END,CASE WHEN source_table='event_store' THEN printf('%020d',CAST(source_record_id AS INTEGER)) ELSE source_record_id END) rn FROM raw), mapped AS (SELECT *,{mapping} activity FROM fused WHERE rn=1) SELECT case_id,activity,timestamp,source_table,source_record_id,actor,object_refs FROM mapped WHERE activity IS NOT NULL ORDER BY case_id,timestamp,source_record_id"


def _permit_query(s: Scenario) -> str:
    mapping = _mapping_case(s, "semantic_code")
    unions = [
        "SELECT history_id source_record_id,execution_id,process_definition_id,activity_id,start_time timestamp,actor_code actor,related_refs_json object_refs,'wf_activity_history' source_table FROM wf_activity_history WHERE lifecycle_code='COMPLETE'",
        "SELECT task_id,execution_id,process_definition_id,activity_id,end_time,assignee_code,related_refs_json,'wf_task_history' FROM wf_task_history WHERE delete_reason IS NULL AND outcome_code IS NOT NULL",
        "SELECT delivery_id,execution_id,process_definition_id,activity_id,delivered_at,actor_code,related_refs_json,'wf_message_delivery' FROM wf_message_delivery WHERE result_code='CORRELATED'",
        "SELECT submission_id,execution_id,process_definition_id,activity_id,submitted_at,submitted_by,related_refs_json,'wf_form_submission' FROM wf_form_submission",
        "SELECT external_task_id,execution_id,process_definition_id,activity_id,completed_at,worker_code,related_refs_json,'wf_external_task' FROM wf_external_task WHERE state_code='COMPLETED' AND error_code IS NULL",
    ]
    return f"WITH raw AS ({' UNION ALL '.join(unions)}), scoped AS (SELECT raw.*,m.semantic_code,(SELECT v.value_text FROM wf_variable_history v WHERE v.execution_id=raw.execution_id AND v.name='application_ref' AND v.created_at<=raw.timestamp ORDER BY v.revision_no DESC LIMIT 1) case_id FROM raw JOIN wf_definition_metadata m USING(process_definition_id,activity_id)), mapped AS (SELECT *,{mapping} activity FROM scoped) SELECT case_id,activity,timestamp,source_table,source_record_id,actor,object_refs FROM mapped WHERE activity IS NOT NULL ORDER BY case_id,timestamp,source_record_id"


def _battery_query(s: Scenario) -> str:
    mapping = _mapping_case(s, "state_code")
    satellites = [table for table in s.evidence_tables if table != "asset_journal"]
    union = " UNION ALL ".join(f"SELECT satellite_id source_record_id,parent_key,load_dts,effective_from,state_code,related_refs_json object_refs,actor_code actor,'{table}' source_table,is_correction,hashdiff,ROW_NUMBER() OVER(PARTITION BY parent_key,hashdiff ORDER BY is_correction,load_dts) duplicate_no FROM {table}" for table in satellites)
    return f"WITH sat AS ({union}), sat_mapped AS (SELECT source_record_id,parent_key,effective_from timestamp,state_code,object_refs,actor,source_table,{mapping} activity FROM sat WHERE is_correction=0 AND duplicate_no=1), ledger AS (SELECT j.journal_id source_record_id,e.asset_hub_key parent_key,j.effective_at timestamp,j.movement_code state_code,j.related_refs_json object_refs,j.actor_code actor,'asset_journal' source_table,{_mapping_case(s, 'j.movement_code')} activity FROM asset_journal j JOIN asset_ledger_entry e ON e.journal_id=j.journal_id GROUP BY j.journal_id HAVING SUM(CASE e.direction WHEN 'DEBIT' THEN e.quantity ELSE -e.quantity END)=0), all_events AS (SELECT * FROM sat_mapped UNION ALL SELECT * FROM ledger) SELECT h.hub_key case_id,activity,timestamp,source_table,source_record_id,actor,object_refs FROM all_events e JOIN hub_battery_pack h ON h.hub_key=e.parent_key WHERE activity IS NOT NULL ORDER BY case_id,timestamp,source_record_id"


def _write_case_views(conn: sqlite3.Connection, folder: Path, base_query: str, s: Scenario, events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    views = folder / "case_views"
    views.mkdir(exist_ok=True)
    exception_activities = sorted({event["ocel:activity"] for event in events if event["is_exception"]})
    exception_sql = ",".join(_sql(activity) for activity in exception_activities)
    exception_flag = f"CASE WHEN activity IN ({exception_sql}) THEN 1 ELSE 0 END"
    secondary_prefix = f"{s.prefix}-{_safe_type(SECONDARY_CASE_TYPES[s.slug])}-*"
    specs = [
        (
            "primary_cases",
            f"SELECT base.*,{exception_flag} is_exception_event FROM ({base_query}) base "
            "ORDER BY case_id,timestamp,source_record_id",
        ),
        (
            "exception_cases",
            f"WITH base AS ({base_query}), selected AS (SELECT DISTINCT case_id FROM base WHERE activity IN ({exception_sql})) "
            f"SELECT base.*,{exception_flag} is_exception_event FROM base JOIN selected USING(case_id) "
            "ORDER BY case_id,timestamp,source_record_id",
        ),
        (
            "multi_object_cases",
            f"WITH base AS ({base_query}), selected AS (SELECT DISTINCT case_id FROM base WHERE json_array_length(object_refs)>=3) "
            "SELECT base.*,CASE WHEN json_array_length(object_refs)>=3 THEN 1 ELSE 0 END is_multi_object_event "
            "FROM base JOIN selected USING(case_id) ORDER BY case_id,timestamp,source_record_id",
        ),
        (
            "secondary_object_cases",
            f"WITH base AS ({base_query}), expanded AS (SELECT j.value case_id,base.activity,base.timestamp,base.source_table,"
            "base.source_record_id,base.actor,base.object_refs,base.case_id primary_case_id "
            f"FROM base,json_each(base.object_refs) j WHERE j.value GLOB {_sql(secondary_prefix)}) "
            "SELECT * FROM expanded ORDER BY case_id,timestamp,source_record_id",
        ),
    ]
    reports = []
    for name, query in specs:
        sql_path = views / f"{name}.sql"
        csv_path = views / f"{name}.csv"
        sql_path.write_text(query.rstrip() + ";\n", encoding="utf-8")
        cur = conn.execute(query)
        header = [col[0] for col in cur.description]
        count = 0
        case_idx = header.index("case_id")
        timestamp_idx = header.index("timestamp")
        source_idx = header.index("source_record_id")
        previous_sort_key: tuple[str, str, str] | None = None
        with csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(header)
            while True:
                rows = cur.fetchmany(10000)
                if not rows:
                    break
                for row in rows:
                    sort_key = (str(row[case_idx]), str(row[timestamp_idx]), str(row[source_idx]))
                    if previous_sort_key is not None and sort_key < previous_sort_key:
                        raise AssertionError(f"{s.slug}/{name} is not sorted by case_id, timestamp, source_record_id")
                    previous_sort_key = sort_key
                writer.writerows(rows)
                count += len(rows)
        reports.append({
            "name": name,
            "case_type": CASE_TYPES[s.slug] if name != "secondary_object_cases" else SECONDARY_CASE_TYPES[s.slug],
            "sql": f"case_views/{name}.sql",
            "csv": f"case_views/{name}.csv",
            "rows": count,
            "sort_order": ["case_id", "timestamp", "source_record_id"],
        })
    return reports


def _write_ocel(folder: Path, events: list[dict[str, Any]], objects: dict[str, dict[str, Any]], relations: list[dict[str, Any]], o2o: list[dict[str, Any]], changes: list[dict[str, Any]]) -> None:
    event_columns = [
        "ocel:eid", "ocel:activity", "ocel:timestamp", "actor", "actor_role", "resource_calendar",
        "source_system", "reason", "amount", "currency", "quantity", "unit", "location",
        "changed_field", "old_value", "new_value", "is_exception", "exception_reason",
        "source_table", "source_record_id", "recorded_at",
    ]
    event_df = pd.DataFrame([{key: event[key] for key in event_columns} for event in events])
    object_df = pd.DataFrame(list(objects.values()))
    relation_df = pd.DataFrame(relations)
    o2o_df = pd.DataFrame(o2o).drop_duplicates().reset_index(drop=True)
    changes_df = pd.DataFrame(changes)
    ocel = OCEL(events=event_df, objects=object_df, relations=relation_df, o2o=o2o_df, object_changes=changes_df)
    path = folder / "ground_truth.ocel2.sqlite"
    if path.exists():
        path.unlink()
    pm4py.write_ocel2_sqlite(ocel, str(path))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _source_contains_activity(conn: sqlite3.Connection, activities: Iterable[str]) -> bool:
    needles = tuple(activity.casefold() for activity in activities)
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
    for table in tables:
        columns = [r[1] for r in conn.execute(f'PRAGMA table_info("{table}")') if str(r[2]).upper() in {"TEXT", "", "JSON"}]
        if not columns:
            continue
        query = "SELECT " + ",".join(f'"{c}"' for c in columns) + f' FROM "{table}"'
        for row in conn.execute(query):
            for value in row:
                if value is None:
                    continue
                folded = str(value).casefold()
                if any(needle == folded for needle in needles):
                    return True
    return False


def _validate(s: Scenario, folder: Path, conn: sqlite3.Connection, events: list[dict[str, Any]], objects: dict[str, dict[str, Any]], relations: list[dict[str, Any]], o2o: list[dict[str, Any]], changes: list[dict[str, Any]], instance_count: int, views: list[dict[str, Any]]) -> dict[str, Any]:
    frequency = Counter(e["ocel:activity"] for e in events)
    rel_by_event: dict[str, set[str]] = defaultdict(set)
    for relation in relations:
        rel_by_event[relation["ocel:eid"]].add(relation["ocel:type"])
    event_case = {event["ocel:eid"]: event["case_no"] for event in events}
    object_cases: dict[str, set[int]] = defaultdict(set)
    for relation in relations:
        object_cases[relation["ocel:oid"]].add(event_case[relation["ocel:eid"]])
    shared_object_fraction = sum(len(case_ids) > 1 for case_ids in object_cases.values()) / len(object_cases)
    transactional_sharing_violations = sum(
        len(object_cases[oid]) > 1
        for oid, obj in objects.items()
        if obj["object_category"] == "TRANSACTIONAL"
    )
    shared_master_objects = [
        oid for oid, obj in objects.items()
        if obj["object_category"] == "SHARED_MASTER" and len(object_cases[oid]) > 1
    ]
    activity_sources: dict[str, set[str]] = defaultdict(set)
    for event in events:
        activity_sources[event["source_table"]].add(event["ocel:activity"])
    max_source_catalogue_fraction = max(map(len, activity_sources.values())) / len(s.activities)
    duplicate_queries = {
        "forgeflow": "SELECT EXISTS(SELECT 1 FROM integration_outbox o JOIN commercial_document d USING(transaction_ref) LIMIT 1)",
        "trialversion": "SELECT EXISTS(SELECT 1 FROM study_v WHERE change_kind='CORRECTION' UNION ALL SELECT 1 FROM protocol_v WHERE change_kind='CORRECTION' LIMIT 1)",
        "procurechange": "SELECT EXISTS(SELECT 1 FROM cdhdr l JOIN archive_cdhdr a USING(client,object_class,object_id,change_number) LIMIT 1)",
        "claimstream": "SELECT EXISTS(SELECT 1 FROM event_store GROUP BY correlation_id,event_type HAVING COUNT(*)>1 LIMIT 1)",
        "permitflow": "SELECT EXISTS(SELECT 1 FROM permit_application WHERE submitted_at IS NOT NULL LIMIT 1)",
        "batteryvault": "SELECT EXISTS(SELECT 1 FROM sat_pack_status WHERE is_correction=1 UNION ALL SELECT 1 FROM sat_pack_test WHERE is_correction=1 LIMIT 1)",
    }
    duplicate_evidence_present = bool(conn.execute(duplicate_queries[s.slug]).fetchone()[0])
    multi_count = sum(1 for event in events if len(rel_by_event[event["ocel:eid"]]) >= 3)
    loop_case_ids = {event["case_no"] for event in events if event["loop_no"] > 0}
    loop_cases = len(loop_case_ids)
    object_ids = set(objects)
    referenced_types = {relation["ocel:type"] for relation in relations}
    change_types = {change["ocel:type"] for change in changes}

    case_traces: dict[int, list[str]] = defaultdict(list)
    for event in events:
        case_traces[event["case_no"]].append(event["ocel:activity"])
    coherent_route_count = sum(
        case_traces[case_no] == [step["activity"] for step in build_route(s.slug, case_no)]
        for case_no in range(1, instance_count + 1)
    )

    actor_roles: dict[str, set[str]] = defaultdict(set)
    for event in events:
        actor_roles[event["actor"]].add(event["actor_role"])
    role_count = len({event["actor_role"] for event in events})
    role_specialization = all(len(roles) == 1 for roles in actor_roles.values()) and all(
        f"-{event['actor_role']}-" in event["actor"]
        and event["resource_calendar"] == (
            "24X7" if event["actor_role"] in {"TELEMETRY", "SOFTWARE", "PROCESS_OWNER"}
            else "WEEKDAY_DAY_SHIFT"
        )
        for event in events
    )

    money_words = ("Payment", "Invoice", "Reserve", "Estimate", "Fee", "Price", "Credit Memo", "Quotation", "Recovery")
    quantity_words = ("Material", "Goods", "Sample", "Dose", "Shipment", "Module", "Battery", "Stock", "Receipt")
    attributes_are_typed = all(
        (event["amount"] is not None) == any(word in event["ocel:activity"] for word in money_words)
        and (event["currency"] == "EUR") == (event["amount"] is not None)
        and (event["quantity"] is not None) == any(word in event["ocel:activity"] for word in quantity_words)
        and (event["unit"] == "EA") == (event["quantity"] is not None)
        for event in events
    )

    expected_by_source = {
        (event["source_table"], str(event["source_record_id"])): event
        for event in events
    }
    csv_stats: dict[str, dict[str, Any]] = {}
    primary_by_source: dict[tuple[str, str], dict[str, str]] = {}
    for view in views:
        counts: Counter[str] = Counter()
        sorted_ok = True
        row_count = 0
        previous: tuple[str, str, str] | None = None
        with (folder / view["csv"]).open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            header_ok = (reader.fieldnames or [])[:3] == ["case_id", "activity", "timestamp"]
            for row in reader:
                row_count += 1
                counts[row["case_id"]] += 1
                key = (row["case_id"], row["timestamp"], row["source_record_id"])
                if previous is not None and key < previous:
                    sorted_ok = False
                previous = key
                if view["name"] == "primary_cases":
                    primary_by_source[(row["source_table"], row["source_record_id"])] = row
        csv_stats[view["name"]] = {
            "rows": row_count,
            "case_counts": counts,
            "sorted": sorted_ok,
            "header": header_ok,
        }

    fidelity_match_count = 0
    for source_key, expected in expected_by_source.items():
        actual = primary_by_source.get(source_key)
        if actual is None:
            continue
        try:
            actual_refs = set(json.loads(actual["object_refs"]))
        except (TypeError, json.JSONDecodeError):
            continue
        if (
            actual["case_id"] == _object_id(s, CASE_TYPES[s.slug], expected["case_no"])
            and actual["activity"] == expected["ocel:activity"]
            and actual["timestamp"] == _iso(expected["ocel:timestamp"])
            and actual_refs == set(expected["object_refs"])
        ):
            fidelity_match_count += 1
    csv_fidelity_fraction = fidelity_match_count / len(events)

    primary_counts = csv_stats["primary_cases"]["case_counts"]
    exception_counts = csv_stats["exception_cases"]["case_counts"]
    multi_counts = csv_stats["multi_object_cases"]["case_counts"]
    exception_trace_complete = bool(exception_counts) and all(
        count == primary_counts[case_id] for case_id, count in exception_counts.items()
    )
    multi_trace_complete = bool(multi_counts) and all(
        count == primary_counts[case_id] for case_id, count in multi_counts.items()
    )
    secondary_stats = csv_stats["secondary_object_cases"]
    checks = {
        "activity_diversity": set(frequency) == set(s.activities) and min(frequency.values()) >= MIN_ACTIVITY_FREQUENCY,
        "object_catalogue_coverage": referenced_types == set(s.object_types),
        "semantic_event_object_rulebook": all(
            subject_type(s.slug, event["ocel:activity"], s.object_types) in rel_by_event[event["ocel:eid"]]
            for event in events
        ),
        "coherent_stateful_routes": coherent_route_count == instance_count,
        "no_source_activity_leakage": not _source_contains_activity(conn, s.activities),
        "multi_object_events": multi_count / len(events) >= 0.15,
        "activity_appropriate_attributes": attributes_are_typed,
        "role_specific_resources": role_specialization and role_count >= 4,
        "temporal_object_attributes": len(change_types) >= 6 and len(changes) == len(events),
        "effective_dated_object_relations": bool(o2o) and all(
            relation.get("ocel:qualifier")
            and relation.get("valid_from") is not None
            and relation.get("valid_to") is not None
            for relation in o2o
        ),
        "loops_and_reversals": loop_cases / instance_count >= 0.20,
        "stable_identifiers": len({e["ocel:eid"] for e in events}) == len(events),
        "provenance": all(e.get("source_table") and e.get("source_record_id") for e in events),
        "referential_validity": all(r["ocel:oid"] in object_ids for r in relations) and all(r["ocel:oid"] in object_ids and r["ocel:oid_2"] in object_ids for r in o2o),
        "event_fusion": duplicate_evidence_present and csv_stats["primary_cases"]["rows"] == len(events),
        "csv_oracle_fidelity": len(primary_by_source) == len(events) and csv_fidelity_fraction == 1.0,
        "csv_sort_order": all(stat["sorted"] and stat["header"] for stat in csv_stats.values()),
        "extraction_difficulty": max_source_catalogue_fraction <= 0.50,
        "type_specific_identity_sharing": transactional_sharing_violations == 0 and bool(shared_master_objects),
        "source_scale": _row_count(conn) >= MIN_SOURCE_ROWS,
        "oracle_scale": 25000 <= len(events) <= 200000,
        "complete_exception_and_multi_views": exception_trace_complete and multi_trace_complete,
        "multiple_case_notions": secondary_stats["rows"] > 0 and len(secondary_stats["case_counts"]) >= 50,
        "case_views": len(views) == 4 and views[0]["rows"] == len(events),
        "oracle_separate_from_source": not conn.execute("SELECT 1 FROM sqlite_master WHERE name LIKE 'event_%' AND name LIKE '%object%' LIMIT 1").fetchone(),
    }
    report = {
        "scenario": s.slug,
        "status": "PASS" if all(checks.values()) else "FAIL",
        "seed": DEFAULT_SEED,
        "instance_count": instance_count,
        "source_row_count": _row_count(conn),
        "oracle_event_count": len(events),
        "oracle_object_count": len(objects),
        "oracle_relation_count": len(relations),
        "object_object_relation_count": len(o2o),
        "object_change_count": len(changes),
        "object_change_type_count": len(change_types),
        "activity_count": len(frequency),
        "minimum_activity_frequency": min(frequency.values()),
        "multi_object_event_fraction": round(multi_count / len(events), 6),
        "loop_instance_fraction": round(loop_cases / instance_count, 6),
        "shared_object_fraction": round(shared_object_fraction, 6),
        "shared_master_object_count": len(shared_master_objects),
        "transactional_sharing_violations": transactional_sharing_violations,
        "role_count": role_count,
        "coherent_route_fraction": round(coherent_route_count / instance_count, 6),
        "csv_oracle_fidelity_fraction": round(csv_fidelity_fraction, 6),
        "largest_source_catalogue_fraction": round(max_source_catalogue_fraction, 6),
        "activity_frequencies": dict(sorted(frequency.items())),
        "case_views": views,
        "checks": checks,
    }
    report["source_sha256"] = _sha256(folder / "source.sqlite")
    report["oracle_sha256"] = _sha256(folder / "ground_truth.ocel2.sqlite")
    return report


def _source_table_fields(folder: Path) -> list[tuple[str, list[tuple[str, str]]]]:
    """Read table names and declared column types from source.sqlite."""
    conn = sqlite3.connect(f"file:{folder / 'source.sqlite'}?mode=ro", uri=True)
    try:
        tables = [
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
        ]
        schema: list[tuple[str, list[tuple[str, str]]]] = []
        for table in tables:
            columns = [
                (row[1], row[2] or "")
                for row in conn.execute(f'PRAGMA table_info("{table}")')
            ]
            schema.append((table, columns))
        return schema
    finally:
        conn.close()


def _source_table_fields_markdown(folder: Path) -> str:
    lines = [
        "## Tables and fields",
        "",
        "The following tables and columns are present in `source.sqlite`:",
        "",
    ]
    for table, columns in _source_table_fields(folder):
        fields = ", ".join(
            f"`{name}` {declared}" if declared else f"`{name}`"
            for name, declared in columns
        )
        lines.append(f"- `{table}` — {fields}")
    return "\n".join(lines)


def _write_docs(s: Scenario, folder: Path, instance_count: int, views: list[dict[str, Any]]) -> None:
    rulebooks = {
        "forgeflow": [
            "Normalize each table's native time representation before ordering.",
            "Fuse outbox/package/movement evidence only when transaction reference and business scope agree.",
            "Treat current status and updated-at fields as state, not standalone events.",
        ],
        "trialversion": [
            "Order versions by version_no for recording precedence and use valid_from for business time.",
            "Only BUSINESS versions with a classified semantic state can produce events; corrections update attributes.",
            "Resolve versioned relations at the event's valid time, never from a stale is_current flag.",
        ],
        "procurechange": [
            "Decode packed keys using tabkey_layout before joining application rows.",
            "Union archive and live change documents and retain the live copy during overlap.",
            "Classify the complete field-change set per change number and deduplicate application evidence.",
        ],
        "claimstream": [
            "Exclude technical stream types and technical event aliases before business classification.",
            "Upcast money and identifier fields according to schema version before correlation.",
            "Fuse retries and cross-stream echoes by correlation ID plus semantic code; use payload effectiveAt as business time.",
        ],
        "permitflow": [
            "Interpret lifecycle and outcome together; canceled or migrated task end times are not completions.",
            "Resolve semantic role by process-definition version and activity migration metadata.",
            "Walk execution scope and select the latest variable revision visible at the activity time.",
        ],
        "batteryvault": [
            "Order satellite facts by effective_from, then source precedence and load_dts; ignore hashdiff replays.",
            "Corrections with the same effective interval change attributes without adding an activity.",
            "Balance debit and credit entries by journal and asset before emitting one custody or ownership movement.",
        ],
    }
    table_guides = {
        "forgeflow": {
            "commercial_document": "commercial lifecycle evidence with split local date/time",
            "engineering_execution": "engineering and operation attempts with separate effective and recording times",
            "supply_posting": "procurement/inventory postings using compact dates and seconds since midnight",
            "quality_observation": "inspection and nonconformance facts stored as epoch milliseconds",
            "fulfilment_record": "package/shipment milestones stored as epoch seconds",
            "finance_posting": "invoice/payment postings with compact clocks",
            "document_conversion": "predecessor/successor scope bridge across heterogeneous documents",
            "integration_outbox": "redundant integration and technical messages; not an activity log",
        },
        "trialversion": {
            "*_v": "coexisting logical row versions with valid time, recording time, edit session, and change kind",
            "object_relation_v": "historized participant, sample, shipment, investigator, and study scope relations",
            "edit_session": "one user or system save that can touch multiple versioned objects",
            "site_timezone": "effective-dated site time-zone rules",
            "code_dictionary": "technical domain values and language-dependent display text",
        },
        "procurechange": {
            "cdhdr/cdpos": "change header plus field-level string changes with packed application keys",
            "archive_cdhdr/archive_cdpos": "older change documents with deliberate live/archive overlap",
            "tabkey_layout/field_catalog": "metadata needed to decode keys and typed old/new values",
            "document_flow/po_history": "many-to-many item-level predecessor and follow-on document relations",
            "application header/item tables": "authoritative material, receipt, invoice, accounting, and payment documents",
            "approval_workflow/approval_step": "approval state and technical workflow history",
        },
        "claimstream": {
            "event_store": "append-only aggregate streams with schema-versioned JSON payloads",
            "command_result/inbox_message": "accepted commands and external facts that can supply business evidence",
            "snapshot_store/projections": "stale-capable query optimizations, never authoritative history",
            "event_type_alias/schema_upcaster_rule": "technical type normalization and old-payload conversion metadata",
            "stream_alias": "effective-dated external-to-canonical stream identity",
            "saga_state/outbox_message": "technical orchestration and integration artifacts",
        },
        "permitflow": {
            "wf_process_instance/wf_execution": "root, called-subprocess, scope, and concurrency ancestry",
            "wf_activity_history/wf_task_history": "technical lifecycle records whose outcomes determine semantics",
            "wf_variable_history": "revision history of scope-local business references",
            "wf_message_delivery/wf_form_submission/wf_external_task": "non-human-task sources of domain milestones",
            "wf_process_migration/wf_job_log/wf_incident": "technical history excluded unless a domain rule says otherwise",
            "domain tables": "current permit, parcel, review, fee, inspection, objection, and appeal state",
        },
        "batteryvault": {
            "hub_*": "stable hashed/business identities loaded from contributing systems",
            "link_* and link_effectivity": "historized assembly, ownership, shipment, service, and genealogy relations",
            "sat_*": "bitemporal status and attribute histories with replay/correction controls",
            "asset_journal/asset_ledger_entry": "balanced ownership or custody movements",
            "business_key_crosswalk/retired_identifier": "effective-dated identity resolution across source identifiers",
            "source_precedence": "attribute-domain-specific trust order for contradictory facts",
        },
    }
    manifest = {
        "scenario": s.slug,
        "title": s.title,
        "source_pattern": s.pattern,
        "seed": DEFAULT_SEED,
        "generator": {"primary_instances": instance_count, "minimum_activity_frequency": MIN_ACTIVITY_FREQUENCY, "minimum_source_rows": MIN_SOURCE_ROWS},
        "activities": list(s.activities),
        "activity_catalogue": list(s.activities),
        "object_types": list(s.object_types),
        "object_type_catalogue": list(s.object_types),
        "activity_count": len(s.activities),
        "object_type_count": len(s.object_types),
        "primary_case_type": CASE_TYPES[s.slug],
        "secondary_case_type": SECONDARY_CASE_TYPES[s.slug],
        "oracle_writer": "pm4py.write_ocel2_sqlite",
        "case_views": views,
        "case_view_ordering": ["case_id", "timestamp", "source_record_id"],
        "deterministic_rules": [
            "Technical codes are classified by the scenario-specific SQL mapping.",
            "Administrative correction, replay, retry, migration, and recalculation records are excluded.",
            "Business effective time takes precedence over recording/load time.",
            "Shared transaction or correlation identifiers are fused before case-view output.",
            "Only declared master-data types share identities across primary cases; transactional identities remain case-local.",
            "Every CSV is sorted by case_id, timestamp, then source_record_id as a deterministic tie-breaker.",
            "The configured seed and explicit process routes contain no nondeterministic input.",
        ] + rulebooks[s.slug],
    }
    (folder / "challenge_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tables = "\n".join(f"- `{name}`" for name in s.evidence_tables)
    table_guide = "\n".join(f"- `{name}` — {meaning}." for name, meaning in table_guides[s.slug].items())
    ambiguity_rules = "\n".join(f"- {rule}" for rule in rulebooks[s.slug])
    source_schema = _source_table_fields_markdown(folder)
    documentation = f"""# {s.title}: source documentation

## Purpose

This is a synthetic **source-system** SQLite database for practicing object-centric extraction. It is not an event log and it does not contain the OCEL exchange tables. The independent oracle is `ground_truth.ocel2.sqlite`.

## Persistence pattern

{s.description}

Primary evidence families:

{tables}

### Table families and meanings

{table_guide}

The database deliberately contains mixed business and technical records, late recording times, redundant evidence, shared master/asset references, and historical relationships. Text codes are technical source codes. Current-state fields, update timestamps, retries, and administrative corrections are not automatically business events.

{source_schema}

## Deterministic ambiguity rules

{ambiguity_rules}

## Time and identity

Business timestamps are normalized to UTC only by the extraction views. Source timestamps intentionally use ISO strings, split dates/times, epoch seconds, or effective/load pairs as appropriate. Canonical identities use the technical relationships or workflow scopes; no universal source event table exists.

## Case views

The primary case notion is `{CASE_TYPES[s.slug]}`. The secondary-object view uses `{SECONDARY_CASE_TYPES[s.slug]}` as an independent case notion. Exception and multi-object views retain complete primary-case traces and add explicit event flags. Every CSV is ordered first by `case_id`, then by `timestamp`, with `source_record_id` used only to break ties deterministically.

## Reproduction

Run `python generate_data.py`. Generation is deterministic with seed {DEFAULT_SEED} and {instance_count:,} primary instances. The script recreates the source database, OCEL oracle, validation report, and all case-view CSV files.

The final activity-mapping queries are intentionally absent from this document. They are present only in the case-view SQL exercises.
"""
    (folder / "source_documentation.md").write_text(documentation, encoding="utf-8")
    glossary_lines = [f"# {s.title}: business glossary", "", "## Object types", ""]
    for name in s.object_types:
        glossary_lines.append(f"- **{name}** — a process-relevant business object represented or referenced by the operational source.")
    glossary_lines.extend(["", "## Activity catalogue", "", "The oracle uses the following canonical business activities; source values use technical codes.", ""])
    glossary_lines.extend(f"- {activity}" for activity in s.activities)
    (folder / "business_glossary.md").write_text("\n".join(glossary_lines) + "\n", encoding="utf-8")


def build_scenario(slug: str, folder: Path | str | None = None, *, instance_count: int = DEFAULT_INSTANCES) -> dict[str, Any]:
    if slug not in SCENARIOS:
        raise KeyError(f"Unknown scenario: {slug}")
    if instance_count < 2000:
        raise ValueError("instance_count must be at least 2000 to preserve the activity-frequency contract")
    s = SCENARIOS[slug]
    folder = Path(folder) if folder is not None else Path(__file__).resolve().parent / s.folder
    folder.mkdir(parents=True, exist_ok=True)
    events, objects, relations, o2o, changes = _build_canonical(s, instance_count)
    conn = _connect_source(folder)
    try:
        if slug == "forgeflow":
            query = _insert_forgeflow(conn, s, events, instance_count)
        elif slug == "trialversion":
            query = _insert_trialversion(conn, s, events, instance_count)
        elif slug == "procurechange":
            query = _insert_procurechange(conn, s, events, instance_count)
        elif slug == "claimstream":
            query = _insert_claimstream(conn, s, events, instance_count)
        elif slug == "permitflow":
            query = _insert_permitflow(conn, s, events, instance_count)
        elif slug == "batteryvault":
            query = _insert_batteryvault(conn, s, events, objects, instance_count)
        else:
            raise AssertionError(slug)
        conn.commit()
        views = _write_case_views(conn, folder, query, s, events)
        _write_ocel(folder, events, objects, relations, o2o, changes)
        _write_docs(s, folder, instance_count, views)
        report = _validate(s, folder, conn, events, objects, relations, o2o, changes, instance_count, views)
        (folder / "validation_report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if report["status"] != "PASS":
            failed = [name for name, ok in report["checks"].items() if not ok]
            raise RuntimeError(f"Validation failed for {slug}: {', '.join(failed)}")
        return report
    finally:
        conn.close()


def build_all(root: Path | str | None = None, *, instance_count: int = DEFAULT_INSTANCES) -> list[dict[str, Any]]:
    root = Path(root) if root is not None else Path(__file__).resolve().parent
    return [build_scenario(slug, root / scenario.folder, instance_count=instance_count) for slug, scenario in SCENARIOS.items()]
