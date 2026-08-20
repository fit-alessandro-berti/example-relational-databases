"""Business-semantic generation rules for the six benchmark scenarios.

This module intentionally contains the domain decisions that were previously
implicit in catalogue positions.  It is dependency-free so the rules can be
audited without opening an OCEL or source database.
"""

from __future__ import annotations

import re
from typing import Any


CASE_TYPES = {
    "forgeflow": "SalesOrder",
    "trialversion": "Participant",
    "procurechange": "PurchaseRequisition",
    "claimstream": "Claim",
    "permitflow": "PermitApplication",
    "batteryvault": "BatteryPack",
}

SECONDARY_CASE_TYPES = {
    "forgeflow": "Shipment",
    "trialversion": "Sample",
    "procurechange": "Invoice",
    "claimstream": "Exposure",
    "permitflow": "Inspection",
    "batteryvault": "ServiceOrder",
}

# Only genuine master/shared objects are pooled. Every unlisted object type is
# transaction-local and receives an identity unique to the primary process.
SHARED_POOL_SIZES = {
    "forgeflow": {"Customer": 750, "Material": 400, "Supplier": 150},
    "trialversion": {"Study": 100, "Protocol": 150, "Site": 120, "Investigator": 300},
    "procurechange": {"Supplier": 150, "Material": 500, "Contract": 250, "CostCenter": 120},
    "claimstream": {"Policy": 1500, "InsuredParty": 1500, "CatastropheEvent": 60, "ServiceProvider": 240},
    "permitflow": {"Applicant": 1500, "Parcel": 1200, "Property": 1200, "Agency": 80, "Contractor": 500},
    "batteryvault": {"CellBatch": 500, "Owner": 1000, "FirmwareCampaign": 40, "RecallCampaign": 24, "Warehouse": 60, "MaterialBatch": 500, "Certificate": 500},
}


def _step(activity: str, *, exception: bool = False, reason: str | None = None) -> dict[str, Any]:
    return {"activity": activity, "is_exception": exception, "exception_reason": reason}


def build_route(slug: str, case_no: int) -> list[dict[str, Any]]:
    """Return one coherent, deterministic process route.

    Optional branches use prime/modular cohorts so all catalogue activities
    remain frequent while outcomes stay mutually consistent.
    """

    out: list[dict[str, Any]] = []

    def add(*activities: str, exception: bool = False, reason: str | None = None) -> None:
        out.extend(_step(a, exception=exception, reason=reason) for a in activities)

    if slug == "forgeflow":
        add("RFQ Created", "RFQ Line Added", "Quote Prepared")
        if case_no % 4 == 0:
            add("Quote Revised")
        add("Quote Approved", "Quote Sent", "Quote Accepted", "Sales Order Created", "Order Line Added", "Configuration Frozen")
        if case_no % 10 == 0:
            add("Credit Check Failed", exception=True, reason="CREDIT_LIMIT")
        add("Credit Check Passed", "Order Released")
        if case_no % 7 == 0:
            add("Engineering Change Requested", "Engineering Change Approved", "Engineering Change Implemented")
        add("BOM Revision Released", "Work Order Created", "Work Order Released", "Material Reserved")
        if case_no % 5 == 0:
            add("Material Shortage Detected", exception=True, reason="INSUFFICIENT_STOCK")
            add("Purchase Requisition Created", "Purchase Order Issued", "Supplier Confirmation Received", "Goods Receipt Posted", "Incoming Inspection Started")
            if case_no % 10 == 0:
                add("Incoming Inspection Failed", exception=True, reason="INBOUND_DEFECT")
            else:
                add("Incoming Inspection Passed")
        add("Material Issued to Work Order", "Operation Started")
        if case_no % 8 == 0:
            add("Production Paused", exception=True, reason="EQUIPMENT_HOLD")
            add("Production Resumed")
        add("Operation Completed")
        if case_no % 5 == 0:
            add("Final Inspection Failed", exception=True, reason="QUALITY_DEFECT")
            add("Nonconformance Raised", "Rework Ordered", "Rework Completed", "Operation Started", "Operation Completed", "Final Inspection Passed")
        else:
            add("Final Inspection Passed")
        add("Serial Number Assigned", "Finished Goods Received", "Shipment Planned", "Package Sealed", "Shipment Dispatched", "Delivery Confirmed", "Invoice Issued", "Payment Received", "Warranty Registered", "Order Closed")

    elif slug == "trialversion":
        if case_no <= 100:
            add("Study Created", "Protocol Published")
        if case_no % 30 == 0:
            add("Protocol Amended")
        if case_no <= 120:
            add("Site Initiated")
        if case_no % 25 == 0:
            add("Site Suspended", exception=True, reason="SITE_COMPLIANCE_HOLD")
            add("Site Reactivated")
        add("Participant Screened")
        if case_no % 10 == 0:
            add("Screening Failed", "Participant Discontinued", exception=True, reason="INCLUSION_CRITERIA")
        else:
            add("Consent Signed")
            if case_no % 19 == 0:
                add("Participant Reconsented")
            add("Participant Enrolled", "Participant Randomized", "Visit Scheduled")
            if case_no % 5 == 0:
                add("Visit Rescheduled")
            if case_no % 11 == 0:
                add("Visit Canceled", exception=True, reason="PARTICIPANT_REQUEST")
            elif case_no % 7 == 0:
                add("Visit Missed", exception=True, reason="NO_SHOW")
            else:
                add("Visit Started", "Visit Completed")
            add("Drug Kit Assigned", "Drug Kit Dispensed")
            if case_no % 13 == 0:
                add("Dose Held", exception=True, reason="SAFETY_HOLD")
            else:
                add("Dose Administered")
            add("Drug Kit Returned", "Sample Collection Ordered")
            if case_no % 17 == 0:
                add("Sample Collection Canceled", exception=True, reason="COLLECTION_NOT_POSSIBLE")
            else:
                add("Sample Collected", "Sample Accessioned", "Aliquot Created", "Sample Frozen")
                if case_no % 19 == 0:
                    add("Sample Thawed")
                add("Sample Shipment Created", "Sample Shipment Packed", "Sample Shipment Dispatched", "Sample Shipment Received", "Lab Test Ordered", "Lab Test Started", "Lab Test Completed")
                if case_no % 12 == 0:
                    add("Lab Test Repeated", exception=True, reason="QC_REPEAT")
                    add("Lab Test Started", "Lab Test Completed")
                add("Result Entered", "Result Validated")
                if case_no % 19 == 0:
                    add("Result Amended", exception=True, reason="LAB_REASSESSMENT")
                if case_no % 23 == 0:
                    add("Sample Destroyed")
            if case_no % 5 == 0:
                add("Adverse Event Opened", "Adverse Event Graded")
                if case_no % 15 == 0:
                    add("Adverse Event Escalated", exception=True, reason="GRADE_INCREASE")
                add("Adverse Event Resolved")
            if case_no % 7 == 0:
                add("Protocol Deviation Raised", exception=True, reason="PROTOCOL_VARIANCE")
                if case_no % 14 == 0:
                    add("Protocol Deviation Waived")
                add("Protocol Deviation Closed")
            if case_no % 4 == 0:
                add("Data Query Opened", "Data Query Answered", "Data Query Closed")
            if case_no % 17 == 0:
                add("Consent Withdrawn", "Participant Discontinued", exception=True, reason="CONSENT_WITHDRAWAL")
            else:
                add("Participant Completed")
        if case_no > 2880:
            add("Site Closed")

    elif slug == "procurechange":
        add("Purchase Requisition Created", "Requisition Item Added")
        if case_no % 6 == 0:
            add("Requisition Item Changed")
        add("Requisition Submitted")
        if case_no % 11 == 0:
            add("Requisition Rejected", exception=True, reason="BUDGET_REJECTED")
            add("Requisition Item Changed", "Requisition Submitted")
        add("Requisition Released", "RFQ Created", "RFQ Sent", "Supplier Quotation Received")
        if case_no % 7 == 0:
            add("Quotation Revised")
        add("Quotation Evaluated", "Source Selected")
        if case_no % 3 == 0:
            add("Contract Referenced")
        add("Requisition Converted to PO", "Purchase Order Created", "PO Item Added")
        if case_no % 5 == 0:
            add("PO Quantity Changed")
        if case_no % 7 == 0:
            add("PO Price Changed")
        if case_no % 9 == 0:
            add("Delivery Date Changed")
        add("PO Submitted for Approval")
        if case_no % 13 == 0:
            add("PO Rejected", exception=True, reason="APPROVAL_REJECTED")
            add("PO Submitted for Approval")
        add("PO Released", "PO Sent to Supplier", "Supplier Confirmation Received")
        if case_no % 8 == 0:
            add("Supplier Confirmation Changed")
        add("Advance Shipping Notice Received")
        if case_no % 29 == 0:
            add("PO Item Deleted", exception=True, reason="LINE_CANCELED")
        if case_no % 4 == 0:
            add("Partial Receipt Posted")
        add("Goods Receipt Posted")
        if case_no % 17 == 0:
            add("Goods Receipt Reversed", exception=True, reason="POSTING_ERROR")
            add("Goods Receipt Posted")
        add("Quality Inspection Started")
        if case_no % 5 == 0:
            add("Quality Inspection Failed", "Stock Placed in Blocked Stock", exception=True, reason="QUALITY_HOLD")
            if case_no % 10 == 0:
                add("Return to Supplier Posted")
            else:
                add("Stock Released from Blocked Stock")
        else:
            add("Quality Inspection Passed")
        add("PO Item Delivery Completed", "Invoice Received")
        if case_no % 6 == 0:
            add("Invoice Parked")
        add("Invoice Posted")
        if case_no % 8 == 0:
            add("Invoice Changed")
        if case_no % 5 == 0:
            add("Three-Way Match Failed", "Invoice Blocked", exception=True, reason="MATCH_VARIANCE")
            add("Invoice Unblocked", "Three-Way Match Passed")
        else:
            add("Three-Way Match Passed")
        if case_no % 23 == 0:
            add("Credit Memo Posted")
        add("Accounting Document Created", "Payment Proposal Created", "Payment Proposal Approved", "Payment Executed")
        if case_no % 31 == 0:
            add("Payment Reversed", exception=True, reason="BANK_RETURN")
            add("Payment Executed")
        add("PO Item Final-Invoiced", "Purchase Order Closed")
        if case_no % 37 == 0:
            add("Supplier Blocked", exception=True, reason="MASTER_DATA_HOLD")
            add("Supplier Unblocked")

    elif slug == "claimstream":
        add("Claim Reported", "Incident Registered", "Claim Acknowledged", "Policy Located", "Coverage Check Started")
        if case_no % 11 == 0:
            add("Coverage Denied", exception=True, reason="POLICY_EXCLUSION")
            add("Customer Contacted", "Complaint Opened", "Complaint Resolved", "Claim Closed", "Claim Archived")
        else:
            add("Coverage Confirmed", "Exposure Opened", "Exposure Classified")
            if case_no % 5 == 0:
                add("Exposure Reclassified")
            add("Adjuster Assigned")
            if case_no % 7 == 0:
                add("Adjuster Reassigned")
            add("Inspection Scheduled")
            if case_no % 6 == 0:
                add("Inspection Rescheduled")
            add("Inspection Completed", "Damage Item Added")
            if case_no % 5 == 0:
                add("Damage Item Updated")
            add("Evidence Requested", "Evidence Received")
            if case_no % 7 == 0:
                add("Evidence Rejected", exception=True, reason="INVALID_EVIDENCE")
                add("Evidence Requested", "Evidence Received")
            add("Evidence Validated", "Estimate Requested", "Estimate Received")
            if case_no % 4 == 0:
                add("Estimate Revised")
            add("Estimate Approved", "Reserve Established")
            if case_no % 3 == 0:
                add("Reserve Increased")
            if case_no % 5 == 0:
                add("Reserve Decreased")
            add("Fraud Score Calculated")
            if case_no % 8 == 0:
                add("Fraud Investigation Opened")
                if case_no % 24 == 0:
                    add("Fraud Case Referred", exception=True, reason="FRAUD_THRESHOLD")
                else:
                    add("Fraud Investigation Cleared")
            if case_no % 13 == 0:
                add("Liability Denied", exception=True, reason="NO_LIABILITY")
                add("Litigation Opened", "Hearing Scheduled")
            else:
                if case_no % 7 == 0:
                    add("Liability Partially Accepted")
                else:
                    add("Liability Accepted")
                add("Repair Authorized", "Repair Started", "Repair Completed")
                if case_no % 6 == 0:
                    add("Repair Reopened", exception=True, reason="REPAIR_DEFECT")
                    add("Repair Started", "Repair Completed")
                add("Payment Proposed")
                if case_no % 29 == 0:
                    add("Payment Canceled", exception=True, reason="PAYEE_CANCELED")
                else:
                    add("Payment Approved")
                    if case_no % 10 == 0:
                        add("Payment Failed", exception=True, reason="BANK_REJECTED")
                        add("Payment Reissued", "Payment Issued")
                    else:
                        add("Payment Issued")
            if case_no % 9 == 0:
                add("Recovery Identified", "Recovery Demand Sent", "Recovery Received")
            add("Claim Settled", "Reserve Released", "Customer Contacted")
            if case_no % 8 == 0:
                add("Complaint Opened", "Complaint Resolved")
            add("Claim Closed")
            if case_no % 5 == 0:
                add("Claim Reopened", exception=True, reason="NEW_INFORMATION")
                add("Claim Closed")
            add("Claim Archived")

    elif slug == "permitflow":
        add("Pre-Application Opened", "Applicant Identity Verified", "Parcel Linked", "Application Drafted", "Application Submitted")
        if case_no % 29 == 0:
            add("Submission Withdrawn", exception=True, reason="APPLICANT_WITHDRAWAL")
            add("Application Reopened", "Application Submitted")
        add("Fee Calculated", "Fee Invoice Issued", "Fee Paid", "Completeness Review Started")
        if case_no % 5 == 0:
            add("Completeness Rejected", "Additional Information Requested", exception=True, reason="INCOMPLETE_APPLICATION")
            add("Additional Documents Submitted", "Completeness Review Started")
        add("Completeness Accepted", "Zoning Review Started")
        if case_no % 17 == 0:
            add("Zoning Denied", "Plan Revision Requested", exception=True, reason="ZONING_CONFLICT")
            add("Plan Revision Submitted", "Plan Revision Accepted", "Zoning Review Started")
        add("Zoning Approved", "Heritage Review Requested")
        if case_no % 7 == 0:
            add("Heritage Conditions Imposed")
        else:
            add("Heritage Approved")
        add("Environmental Review Started")
        if case_no % 19 == 0:
            add("Environmental Review Failed", "Plan Revision Requested", exception=True, reason="ENVIRONMENTAL_IMPACT")
            add("Plan Revision Submitted", "Plan Revision Accepted", "Environmental Review Started")
        add("Environmental Review Passed", "Public Notice Published", "Consultation Opened")
        if case_no % 5 == 0:
            add("Objection Filed")
            if case_no % 10 == 0:
                add("Objection Withdrawn")
        if case_no % 11 == 0:
            add("Hearing Scheduled", "Hearing Held")
        add("Consultation Closed", "Fire Safety Review Started")
        if case_no % 13 == 0:
            add("Fire Safety Failed", "Plan Revision Requested", exception=True, reason="FIRE_SAFETY_DEFECT")
            add("Plan Revision Submitted", "Plan Revision Accepted", "Fire Safety Review Started")
        add("Fire Safety Passed", "Structural Review Started")
        if case_no % 17 == 0:
            add("Structural Review Failed", "Plan Revision Requested", exception=True, reason="STRUCTURAL_DEFECT")
            add("Plan Revision Submitted", "Plan Revision Accepted", "Structural Review Started")
        add("Structural Review Passed", "Permit Drafted", "Permit Approved", "Permit Issued")
        if case_no % 19 == 0:
            add("Permit Suspended", exception=True, reason="CONDITION_BREACH")
            add("Permit Amended")
        elif case_no % 11 == 0:
            add("Permit Amended")
        if case_no % 29 == 0:
            add("Permit Revoked", "Appeal Filed", "Appeal Hearing Held", exception=True, reason="REVOCATION")
            if case_no % 58 == 0:
                add("Appeal Dismissed")
            else:
                add("Appeal Allowed", "Permit Amended")
        add("Contractor Registered", "Work Commencement Notified", "Inspection Requested", "Inspection Scheduled", "Inspection Performed")
        if case_no % 5 == 0:
            add("Inspection Failed", "Reinspection Requested", "Violation Opened", exception=True, reason="INSPECTION_DEFECT")
            add("Violation Remediated", "Inspection Requested", "Inspection Scheduled", "Inspection Performed")
        add("Inspection Passed", "Completion Certificate Requested", "Completion Certificate Issued", "Case Archived")

    elif slug == "batteryvault":
        add("Cell Batch Produced", "Cell Batch Released", "Module Assembled", "Module Tested")
        if case_no % 10 == 0:
            add("Module Failed Test", exception=True, reason="MODULE_TEST_FAILURE")
            add("Module Tested")
        add("Battery Pack Assembled", "Battery Pack Tested")
        if case_no % 11 == 0:
            add("Battery Pack Failed Test", exception=True, reason="PACK_TEST_FAILURE")
            add("Battery Pack Tested")
        add("Battery Pack Passed Test", "Battery Passport Issued")
        if case_no % 17 == 0:
            add("Battery Passport Corrected")
        add("Battery Installed in Vehicle", "Vehicle Delivered", "Ownership Transferred")
        if case_no % 2 == 0:
            add("Lease Started", "Lease Ended")
        add("Battery Removed from Vehicle")
        if case_no % 4 == 0:
            add("Telemetry Anomaly Detected", "Diagnostic Scheduled", "Diagnostic Run", "State of Health Assessed", "Service Order Opened", "Service Started")
            if case_no % 8 == 0:
                add("Module Replacement Ordered", "Module Replaced")
            add("Service Completed")
        if case_no % 3 == 0:
            add("Firmware Campaign Assigned", "Firmware Downloaded")
            if case_no % 13 == 0:
                add("Firmware Installation Failed", "Firmware Rolled Back", exception=True, reason="INSTALLATION_ERROR")
                add("Firmware Downloaded")
            add("Firmware Installed")
        if case_no % 7 == 0:
            add("Warranty Claim Opened")
            if case_no % 14 == 0:
                add("Warranty Claim Denied", exception=True, reason="WARRANTY_EXCLUSION")
            else:
                add("Warranty Claim Approved")
        if case_no % 30 == 0:
            add("Recall Campaign Announced", "Battery Matched to Recall", "Recall Notification Sent", "Recall Notification Acknowledged", "Recall Service Completed")
        add("Transport Booked", "Shipment Dispatched", "Shipment Received")
        if case_no % 10 == 0:
            add("Battery Quarantined", exception=True, reason="TRANSPORT_DAMAGE")
            add("Battery Released from Quarantine")
        add("Second-Life Assessment Started")
        if case_no % 5 == 0:
            add("Second-Life Assessment Failed", exception=True, reason="LOW_STATE_OF_HEALTH")
        else:
            add("Second-Life Assessment Passed", "Battery Reconfigured", "Second-Life System Commissioned")
            if case_no % 2 == 0:
                add("Second-Life System Decommissioned")
        add("Recycling Order Created", "Battery Dismantled", "Material Batch Recovered", "Material Batch Certified")
        if case_no % 19 == 0:
            add("Compliance Certificate Revoked", exception=True, reason="AUDIT_FINDING")
            add("Compliance Certificate Reissued")
        if case_no % 17 == 0:
            add("Incident Reported", "Incident Investigation Started", exception=True, reason="SAFETY_INCIDENT")
            add("Incident Closed")
        add("Lifecycle Closed")
    else:
        raise KeyError(slug)

    return out


def _camel_words(value: str) -> str:
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", value)


SUBJECT_KEYWORDS: dict[str, tuple[tuple[str, str], ...]] = {
    "forgeflow": (
        ("rfq line", "RFQLine"), ("rework ", "ReworkOrder"),
        ("material issued", "MaterialLot"), ("material shortage", "Material"), ("material reserved", "Material"),
        ("incoming inspection", "QualityInspection"), ("final inspection", "QualityInspection"),
        ("finished goods", "MaterialLot"), ("credit check", "SalesOrder"), ("order released", "SalesOrder"), ("order closed", "SalesOrder"),
        ("production paused", "WorkOrder"), ("production resumed", "WorkOrder"), ("delivery confirmed", "Shipment"),
        ("quote prepared", "Quote"), ("quote revised", "QuoteRevision"), ("quote approved", "QuoteRevision"),
        ("quote sent", "QuoteRevision"), ("quote accepted", "QuoteRevision"),
    ),
    "trialversion": (
        ("result ", "LabResult"), ("sample collection", "Sample"), ("sample accessioned", "Sample"),
        ("sample frozen", "Sample"), ("sample thawed", "Sample"), ("sample destroyed", "Sample"),
        ("screening failed", "Participant"), ("drug kit assigned", "Dispensation"),
    ),
    "procurechange": (
        ("requisition item", "RequisitionItem"), ("purchase requisition", "PurchaseRequisition"),
        ("requisition ", "PurchaseRequisition"), ("supplier confirmation", "PurchaseOrder"),
        ("quotation ", "SupplierQuotation"), ("source selected", "SupplierQuotation"),
        ("delivery date", "ScheduleLine"), ("po item", "PurchaseOrderItem"), ("po ", "PurchaseOrder"),
        ("partial receipt", "GoodsReceipt"), ("quality inspection", "InspectionLot"),
        ("stock ", "GoodsMovement"), ("return to supplier", "GoodsMovement"), ("three-way match", "Invoice"),
        ("credit memo", "Invoice"),
    ),
    "claimstream": (
        ("adjuster ", "AdjusterAssignment"), ("evidence ", "EvidenceDocument"), ("repair ", "RepairOrder"),
        ("coverage ", "Claim"), ("fraud score", "Claim"), ("liability ", "Exposure"),
        ("customer contacted", "Communication"), ("hearing scheduled", "LitigationCase"),
        ("claim settled", "Settlement"),
    ),
    "permitflow": (
        ("pre-application", "PermitApplication"), ("application ", "PermitApplication"),
        ("submission ", "PermitApplication"), ("completeness ", "PermitApplication"),
        ("additional information", "PermitApplication"), ("additional documents", "Document"),
        ("zoning ", "Review"), ("heritage ", "Review"), ("environmental ", "Review"),
        ("fire safety", "Review"), ("structural ", "Review"), ("public notice", "Document"),
        ("consultation ", "PermitApplication"), ("hearing ", "PermitApplication"),
        ("fee paid", "Payment"), ("work commencement", "Permit"), ("completion certificate", "Permit"),
        ("case archived", "PermitApplication"),
    ),
    "batteryvault": (
        ("ownership transferred", "BatteryPack"), ("lease ", "BatteryPack"),
        ("battery installed", "BatteryPack"), ("battery removed", "BatteryPack"),
        ("telemetry ", "BatteryPack"), ("state of health", "DiagnosticTest"),
        ("service started", "ServiceOrder"), ("service completed", "ServiceOrder"),
        ("module replacement", "Module"), ("firmware downloaded", "FirmwareCampaign"),
        ("firmware installed", "FirmwareCampaign"), ("firmware installation", "FirmwareCampaign"),
        ("firmware rolled", "FirmwareCampaign"), ("recall notification", "RecallCampaign"),
        ("recall service", "RecallCampaign"), ("battery matched", "RecallCampaign"),
        ("transport booked", "Shipment"), ("battery quarantined", "BatteryPack"),
        ("battery released", "BatteryPack"), ("battery dismantled", "RecyclingOrder"),
        ("second-life", "SecondLifeSystem"),
        ("lifecycle closed", "BatteryPack"),
    ),
}


def subject_type(slug: str, activity: str, object_types: tuple[str, ...]) -> str:
    low = activity.lower()
    for keyword, object_type in SUBJECT_KEYWORDS[slug]:
        if keyword in low:
            return object_type
    matches = []
    for object_type in object_types:
        phrase = _camel_words(object_type).lower()
        if re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", low):
            matches.append((len(phrase), object_type))
    if matches:
        return max(matches)[1]
    return CASE_TYPES[slug]


CONTEXT_BY_SUBJECT: dict[str, dict[str, tuple[str, ...]]] = {
    "forgeflow": {
        "RFQ": ("Customer",), "RFQLine": ("RFQ", "Material"), "Quote": ("RFQ", "Customer"),
        "QuoteRevision": ("Quote", "RFQ"), "SalesOrder": ("Customer", "QuoteRevision"),
        "SalesOrderLine": ("SalesOrder", "ProductConfiguration"), "ProductConfiguration": ("SalesOrderLine",),
        "EngineeringChange": ("ProductConfiguration", "BOMRevision"), "BOMRevision": ("ProductConfiguration",),
        "WorkOrder": ("SalesOrderLine", "BOMRevision"), "Operation": ("WorkOrder",),
        "Material": ("WorkOrder", "MaterialLot"), "MaterialLot": ("Material", "WorkOrder"),
        "PurchaseRequisition": ("WorkOrder", "Material"), "PurchaseOrder": ("PurchaseRequisition", "PurchaseOrderLine", "Supplier"),
        "Supplier": ("PurchaseOrder",), "GoodsReceipt": ("PurchaseOrder", "MaterialLot", "Supplier"),
        "QualityInspection": ("GoodsReceipt", "MaterialLot", "WorkOrder"), "Nonconformance": ("QualityInspection", "WorkOrder"),
        "ReworkOrder": ("Nonconformance", "WorkOrder"), "SerialUnit": ("WorkOrder", "MaterialLot"),
        "Shipment": ("SalesOrder", "SerialUnit", "Package"), "Package": ("Shipment", "SerialUnit"),
        "Invoice": ("SalesOrder", "Shipment"), "Payment": ("Invoice",), "Warranty": ("SerialUnit", "Customer"),
    },
    "trialversion": {
        "Study": ("Protocol",), "Protocol": ("Study",), "Site": ("Study", "Investigator"),
        "Participant": ("Study", "Site", "Investigator"), "Consent": ("Participant", "Protocol"),
        "Visit": ("Participant", "Site"), "DrugKit": ("Participant", "Site"), "Dispensation": ("Participant", "DrugKit"),
        "Dose": ("Participant", "Dispensation"), "Sample": ("Participant", "Visit"), "Aliquot": ("Sample",),
        "SampleShipment": ("Sample", "Site"), "LabOrder": ("Sample",), "LabTest": ("LabOrder", "Sample"),
        "LabResult": ("LabTest", "Sample"), "AdverseEvent": ("Participant", "Dose"),
        "ProtocolDeviation": ("Participant", "Protocol"), "DataQuery": ("Participant", "Visit"),
    },
    "procurechange": {
        "PurchaseRequisition": ("RequisitionItem", "CostCenter"), "RequisitionItem": ("PurchaseRequisition", "Material"),
        "RFQ": ("RequisitionItem", "Supplier"), "SupplierQuotation": ("RFQ", "Supplier"), "Contract": ("Supplier", "Material"),
        "PurchaseOrder": ("PurchaseRequisition", "Supplier", "Contract"), "PurchaseOrderItem": ("PurchaseOrder", "Material"),
        "ScheduleLine": ("PurchaseOrderItem",), "AdvanceShippingNotice": ("PurchaseOrder", "Supplier"),
        "GoodsMovement": ("PurchaseOrderItem", "Material"), "GoodsReceipt": ("PurchaseOrder", "GoodsMovement", "Material"),
        "InspectionLot": ("GoodsReceipt", "Material"), "Invoice": ("PurchaseOrder", "GoodsReceipt", "InvoiceItem", "Supplier"),
        "InvoiceItem": ("Invoice", "PurchaseOrderItem"), "AccountingDocument": ("Invoice", "CostCenter"),
        "PaymentProposal": ("AccountingDocument", "Invoice"), "Payment": ("PaymentProposal", "Supplier", "Invoice"),
        "Supplier": ("PurchaseOrder",),
    },
    "claimstream": {
        "Policy": ("InsuredParty",), "Claim": ("Policy", "InsuredParty", "Incident", "CatastropheEvent"), "Incident": ("Claim",),
        "Exposure": ("Claim", "DamageItem"), "AdjusterAssignment": ("Claim", "Exposure"),
        "Inspection": ("Claim", "Exposure", "ServiceProvider"), "DamageItem": ("Exposure", "Claim"),
        "EvidenceDocument": ("Claim", "Exposure"), "Estimate": ("DamageItem", "Claim"), "Reserve": ("Exposure", "Claim"),
        "FraudCase": ("Claim", "Exposure"), "RepairOrder": ("DamageItem", "Claim", "ServiceProvider"),
        "Payment": ("Claim", "Exposure", "Reserve"), "Recovery": ("Claim", "Payment"),
        "LitigationCase": ("Claim", "Exposure"), "Complaint": ("Claim", "InsuredParty"),
        "Communication": ("Claim", "InsuredParty"), "Settlement": ("Claim", "Payment"),
    },
    "permitflow": {
        "PermitApplication": ("Applicant", "Parcel", "Property"), "Applicant": ("PermitApplication",),
        "Parcel": ("PermitApplication", "Property"), "PlanRevision": ("PermitApplication", "Document"),
        "Document": ("PermitApplication", "PlanRevision"), "Review": ("PermitApplication", "PlanRevision", "Agency"),
        "FeeInvoice": ("PermitApplication",), "Payment": ("FeeInvoice", "PermitApplication"),
        "Objection": ("PermitApplication", "Applicant", "PlanRevision"), "Permit": ("PermitApplication", "Condition"),
        "Contractor": ("Permit",), "Inspection": ("Permit", "Contractor"), "Violation": ("Inspection", "Permit"),
        "Appeal": ("PermitApplication", "Permit"),
    },
    "batteryvault": {
        "CellBatch": ("Module",), "Module": ("CellBatch", "BatteryPack"), "BatteryPack": ("Module", "BatteryPassport"),
        "BatteryPassport": ("BatteryPack",), "Vehicle": ("BatteryPack", "Owner"), "Owner": ("BatteryPack", "Vehicle"),
        "DiagnosticTest": ("BatteryPack", "ServiceOrder"), "ServiceOrder": ("BatteryPack", "DiagnosticTest"),
        "FirmwareCampaign": ("BatteryPack",), "WarrantyClaim": ("BatteryPack", "ServiceOrder"),
        "RecallCampaign": ("BatteryPack",), "Shipment": ("BatteryPack", "Warehouse"),
        "SecondLifeSystem": ("BatteryPack",), "RecyclingOrder": ("BatteryPack",),
        "MaterialBatch": ("RecyclingOrder", "BatteryPack"), "Certificate": ("MaterialBatch",),
        "Incident": ("BatteryPack", "Shipment"),
    },
}


O2O_EDGES: dict[str, tuple[tuple[str, str, str], ...]] = {
    "forgeflow": (("SalesOrder", "Customer", "placed-by"), ("SalesOrder", "RFQ", "converted-from"), ("QuoteRevision", "Quote", "revision-of"), ("WorkOrder", "SalesOrderLine", "fulfills"), ("WorkOrder", "BOMRevision", "uses"), ("PurchaseOrder", "Supplier", "ordered-from"), ("GoodsReceipt", "PurchaseOrder", "receives"), ("QualityInspection", "GoodsReceipt", "inspects"), ("Shipment", "SalesOrder", "delivers"), ("Invoice", "SalesOrder", "bills"), ("Payment", "Invoice", "settles"), ("Warranty", "SerialUnit", "covers")),
    "trialversion": (("Participant", "Study", "enrolled-in"), ("Participant", "Site", "managed-at"), ("Consent", "Participant", "signed-by"), ("Consent", "Protocol", "under-protocol"), ("Visit", "Participant", "visit-of"), ("Dispensation", "DrugKit", "dispenses"), ("Dose", "Participant", "administered-to"), ("Sample", "Participant", "collected-from"), ("Aliquot", "Sample", "derived-from"), ("SampleShipment", "Sample", "contains"), ("LabTest", "Sample", "tests"), ("LabResult", "LabTest", "result-of"), ("AdverseEvent", "Participant", "affects")),
    "procurechange": (("RequisitionItem", "PurchaseRequisition", "item-of"), ("RFQ", "PurchaseRequisition", "sources"), ("SupplierQuotation", "RFQ", "responds-to"), ("PurchaseOrder", "PurchaseRequisition", "converts"), ("PurchaseOrder", "Supplier", "ordered-from"), ("PurchaseOrderItem", "Material", "orders"), ("GoodsReceipt", "PurchaseOrder", "receives"), ("InspectionLot", "GoodsReceipt", "inspects"), ("Invoice", "PurchaseOrder", "bills"), ("AccountingDocument", "Invoice", "posts"), ("Payment", "Invoice", "settles")),
    "claimstream": (("Claim", "Policy", "under-policy"), ("Claim", "InsuredParty", "reported-by"), ("Incident", "Claim", "incident-of"), ("Exposure", "Claim", "exposure-of"), ("DamageItem", "Exposure", "damage-of"), ("AdjusterAssignment", "Claim", "assigned-to"), ("Inspection", "Exposure", "inspects"), ("Estimate", "DamageItem", "estimates"), ("Reserve", "Exposure", "reserved-for"), ("RepairOrder", "DamageItem", "repairs"), ("Payment", "Claim", "pays"), ("Payment", "Exposure", "covers"), ("Recovery", "Payment", "recovers"), ("Complaint", "Claim", "complaint-about")),
    "permitflow": (("PermitApplication", "Applicant", "submitted-by"), ("PermitApplication", "Parcel", "covers"), ("Parcel", "Property", "identifies"), ("PlanRevision", "PermitApplication", "revision-of"), ("Document", "PlanRevision", "documents"), ("Review", "PlanRevision", "reviews"), ("Review", "Agency", "performed-by"), ("Payment", "FeeInvoice", "settles"), ("Permit", "PermitApplication", "issued-for"), ("Condition", "Permit", "condition-of"), ("Inspection", "Permit", "inspects"), ("Violation", "Inspection", "raised-by"), ("Appeal", "PermitApplication", "appeals")),
    "batteryvault": (("Module", "CellBatch", "assembled-from"), ("BatteryPack", "Module", "contains"), ("BatteryPassport", "BatteryPack", "passport-of"), ("Vehicle", "BatteryPack", "installed-with"), ("BatteryPack", "Owner", "owned-by"), ("ServiceOrder", "BatteryPack", "services"), ("DiagnosticTest", "BatteryPack", "diagnoses"), ("FirmwareCampaign", "BatteryPack", "targets"), ("WarrantyClaim", "BatteryPack", "claims-for"), ("RecallCampaign", "BatteryPack", "recalls"), ("Shipment", "BatteryPack", "transports"), ("SecondLifeSystem", "BatteryPack", "uses"), ("RecyclingOrder", "BatteryPack", "recycles"), ("MaterialBatch", "RecyclingOrder", "recovered-by"), ("Certificate", "MaterialBatch", "certifies")),
}


ROLE_KEYWORDS: dict[str, tuple[tuple[str, str], ...]] = {
    "forgeflow": (("RFQ", "SALES"), ("Quote", "SALES"), ("Sales Order", "SALES"), ("Credit", "CREDIT"), ("Engineering", "ENGINEERING"), ("BOM", "ENGINEERING"), ("Purchase", "BUYER"), ("Supplier", "BUYER"), ("Inspection", "QUALITY"), ("Nonconformance", "QUALITY"), ("Rework", "PRODUCTION"), ("Operation", "PRODUCTION"), ("Production", "PRODUCTION"), ("Material", "WAREHOUSE"), ("Shipment", "LOGISTICS"), ("Package", "LOGISTICS"), ("Delivery", "LOGISTICS"), ("Invoice", "FINANCE"), ("Payment", "FINANCE"), ("Warranty", "SERVICE")),
    "trialversion": (("Study", "STUDY_MGMT"), ("Protocol", "STUDY_MGMT"), ("Site", "SITE_COORD"), ("Participant", "INVESTIGATOR"), ("Consent", "INVESTIGATOR"), ("Visit", "SITE_COORD"), ("Drug", "PHARMACY"), ("Dose", "NURSE"), ("Sample", "LAB"), ("Aliquot", "LAB"), ("Lab", "LAB"), ("Result", "LAB"), ("Adverse", "SAFETY"), ("Deviation", "COMPLIANCE"), ("Data Query", "DATA_MGMT")),
    "procurechange": (("Requisition", "REQUESTER"), ("RFQ", "BUYER"), ("Quotation", "BUYER"), ("Source", "BUYER"), ("Contract", "BUYER"), ("PO Submitted", "APPROVER"), ("PO Released", "APPROVER"), ("PO Rejected", "APPROVER"), ("Purchase Order", "BUYER"), ("PO ", "BUYER"), ("Supplier", "BUYER"), ("Shipping", "LOGISTICS"), ("Receipt", "WAREHOUSE"), ("Stock", "WAREHOUSE"), ("Inspection", "QUALITY"), ("Invoice", "AP"), ("Match", "AP"), ("Accounting", "AP"), ("Payment", "TREASURY")),
    "claimstream": (("Claim Reported", "INTAKE"), ("Incident", "INTAKE"), ("Acknowledged", "INTAKE"), ("Policy", "COVERAGE"), ("Coverage", "COVERAGE"), ("Exposure", "ADJUSTER"), ("Adjuster", "ADJUSTER"), ("Inspection", "INSPECTOR"), ("Damage", "ADJUSTER"), ("Evidence", "ADJUSTER"), ("Estimate", "ESTIMATOR"), ("Reserve", "CLAIMS_MGR"), ("Fraud", "FRAUD"), ("Liability", "CLAIMS_MGR"), ("Repair", "REPAIR_COORD"), ("Payment", "PAYMENTS"), ("Recovery", "RECOVERY"), ("Litigation", "LEGAL"), ("Hearing", "LEGAL"), ("Complaint", "CUSTOMER_CARE"), ("Customer", "CUSTOMER_CARE")),
    "permitflow": (("Applicant", "CASE_OFFICER"), ("Application", "CASE_OFFICER"), ("Parcel", "CASE_OFFICER"), ("Fee", "CASHIER"), ("Completeness", "CASE_OFFICER"), ("Document", "CASE_OFFICER"), ("Zoning", "PLANNER"), ("Heritage", "HERITAGE"), ("Environmental", "ENVIRONMENT"), ("Consultation", "CONSULTATION"), ("Objection", "CONSULTATION"), ("Hearing", "CONSULTATION"), ("Plan Revision", "CASE_OFFICER"), ("Fire", "FIRE_REVIEW"), ("Structural", "STRUCTURAL_REVIEW"), ("Permit", "PERMIT_OFFICER"), ("Contractor", "PERMIT_OFFICER"), ("Inspection", "INSPECTOR"), ("Violation", "INSPECTOR"), ("Appeal", "APPEAL_BOARD")),
    "batteryvault": (("Cell", "MANUFACTURING"), ("Module", "MANUFACTURING"), ("Battery Pack", "TEST_ENGINEER"), ("Passport", "PASSPORT"), ("Vehicle", "DEALER"), ("Ownership", "DEALER"), ("Lease", "DEALER"), ("Telemetry", "TELEMETRY"), ("Diagnostic", "SERVICE"), ("Health", "SERVICE"), ("Service", "SERVICE"), ("Firmware", "SOFTWARE"), ("Warranty", "WARRANTY"), ("Recall", "RECALL"), ("Transport", "LOGISTICS"), ("Shipment", "LOGISTICS"), ("Quarantine", "LOGISTICS"), ("Second-Life", "SECOND_LIFE"), ("Recycl", "RECYCLING"), ("Material", "RECYCLING"), ("Certificate", "COMPLIANCE"), ("Incident", "SAFETY")),
}


def actor_role(slug: str, activity: str) -> str:
    for keyword, role in ROLE_KEYWORDS[slug]:
        if keyword.lower() in activity.lower():
            return role
    return "PROCESS_OWNER"


def context_types(slug: str, subject: str) -> tuple[str, ...]:
    return CONTEXT_BY_SUBJECT[slug].get(subject, ())
