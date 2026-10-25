import math
import random
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.complaint import Complaint
from app.models.institution import Institution
from app.models.user import User
from app.models.timeline import ComplaintTimeline
from app.schemas.complaint import (
    ComplaintCreate,
    ComplaintRead,
    ComplaintListResponse,
    ComplaintStatusUpdate,
    ComplaintAssignmentUpdate,
)
from app.schemas.timeline import TimelineEventRead
from app.auth import get_current_user, check_case_access

router = APIRouter(prefix="/complaints", tags=["Complaints"])

# Permitted status transitions per workflow rules (AICTE Complaint Lifecycle)
PERMITTED_STATUS_TRANSITIONS = {
    "Pending": ["In Progress"],
    "In Progress": ["Escalated", "Resolved"],
    "Escalated": ["In Progress", "Resolved"],
    "Resolved": [],
}

def get_sla_days(priority: str) -> int:
    p = priority.lower()
    if p == "critical":
        return 3
    elif p == "high":
        return 7
    elif p == "medium":
        return 14
    elif p == "low":
        return 21
    return 14

def get_default_officer(bureau: str) -> str:
    b = bureau.upper()
    if b == "RB":
        return "Anita Verma"
    elif b in ("APPROVAL", "SB"):
        return "Suresh Patel"
    elif b == "ACADEMIC":
        return "Meera Iyer"
    return "Rajesh Kumar"

def get_default_next_action(status_val: str, bureau: str) -> str:
    s = status_val.lower()
    if s == "pending":
        return f"Jurisdiction verification and preliminary scrutiny by {bureau} Cell"
    elif s == "in progress":
        return "Examine institution counter-affidavit and verify official registers"
    elif s == "escalated":
        return "Convene expedited joint hearing with institution management"
    elif s == "resolved":
        return "Final compliance order signed and archived"
    return f"Routine administrative review by {bureau} Cell"

def map_complaint_to_read(c: Complaint) -> ComplaintRead:
    timeline_items = [
        TimelineEventRead(
            id=t.id,
            complaintId=t.complaint_id,
            label=t.label,
            date=t.date,
            by=t.by,
            role=t.role,
            note=t.note,
            userId=t.user_id,
            createdAt=t.created_at,
        )
        for t in getattr(c, "timeline_events", [])
    ]
    return ComplaintRead(
        id=c.id,
        institutionId=c.institution_id,
        institutionPermanentId=c.institution_permanent_id,
        bureau=c.bureau,
        category=c.category,
        priority=c.priority,
        status=c.status,
        officer=c.officer,
        assignedUserId=c.assigned_user_id,
        date=c.date,
        due=c.due,
        title=c.title,
        description=c.description,
        complainantType=c.complainant_type,
        complainantName=c.complainant_name,
        complainantEmail=c.complainant_email,
        complainantPhone=c.complainant_phone,
        remarks=c.remarks,
        nextAction=c.next_action,
        lastActionDate=c.last_action_date,
        institutionName=c.institution.name if c.institution else None,
        createdAt=c.created_at,
        updatedAt=c.updated_at,
        timeline=timeline_items,
    )

@router.post("", response_model=ComplaintRead, status_code=status.HTTP_201_CREATED)
def create_complaint(
    complaint_in: ComplaintCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create and persist a new grievance complaint in PostgreSQL.
    Requires authentication. If logged in as Complainant, enforces complainant identity.
    Validates institution existence, applies statutory SLA due dates, bureau routing defaults,
    and records the initial creation events in the chronological timeline.
    """
    # 1. Verify that referenced institution exists
    inst = db.query(Institution).filter(Institution.id == complaint_in.institutionId).first()
    if not inst:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Institution with ID '{complaint_in.institutionId}' does not exist in the AICTE registry."
        )

    # 2. Case ID resolution or generation
    case_id = complaint_in.id
    if not case_id or not case_id.strip():
        prefix = "AB" if complaint_in.bureau == "Approval" else ("ACD" if complaint_in.bureau == "Academic" else complaint_in.bureau)
        for _ in range(100):
            candidate = f"{prefix}-2026-{random.randint(1000, 9999)}"
            if not db.query(Complaint).filter(Complaint.id == candidate).first():
                case_id = candidate
                break
        if not case_id:
            case_id = f"{prefix}-2026-{int(datetime.now(timezone.utc).timestamp()) % 10000:04d}"
    else:
        case_id = case_id.strip()
        existing = db.query(Complaint).filter(Complaint.id.ilike(case_id)).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Complaint with Case ID '{case_id}' already exists."
            )

    # 3. Default Officer & User assignment
    officer_name = complaint_in.officer.strip() if complaint_in.officer and complaint_in.officer.strip() else get_default_officer(complaint_in.bureau)
    assigned_user = db.query(User).filter(User.name == officer_name).first()
    assigned_user_id = assigned_user.id if assigned_user else None

    # 4. Complainant identity verification: Never trust client to spoof identity
    if current_user.role == "Complainant":
        complainant_name = current_user.name
        complainant_email = current_user.email
        complainant_phone = complaint_in.complainantPhone.strip() if complaint_in.complainantPhone and complaint_in.complainantPhone.strip() else (current_user.phone or None)
        intake_user_id = current_user.id
    else:
        complainant_name = complaint_in.complainantName.strip() if complaint_in.complainantName and complaint_in.complainantName.strip() else current_user.name
        complainant_email = complaint_in.complainantEmail.strip() if complaint_in.complainantEmail and complaint_in.complainantEmail.strip() else current_user.email
        complainant_phone = complaint_in.complainantPhone.strip() if complaint_in.complainantPhone and complaint_in.complainantPhone.strip() else None
        intake_user_id = None

    # 5. Filing Date & Due Date SLA
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    date_val = complaint_in.date.strip() if complaint_in.date and complaint_in.date.strip() else now_str
    if complaint_in.due and complaint_in.due.strip():
        due_val = complaint_in.due.strip()
    else:
        sla_days = get_sla_days(complaint_in.priority)
        try:
            base_date = datetime.strptime(date_val, "%Y-%m-%d")
        except ValueError:
            base_date = datetime.now(timezone.utc)
        due_val = (base_date + timedelta(days=sla_days)).strftime("%Y-%m-%d")

    # 6. Permanent ID
    perm_id = complaint_in.institutionPermanentId.strip() if complaint_in.institutionPermanentId and complaint_in.institutionPermanentId.strip() else inst.aicte_id

    # 7. Workflow next action & last action date
    status_val = complaint_in.status if complaint_in.status else "Pending"
    next_action_val = complaint_in.nextAction.strip() if complaint_in.nextAction and complaint_in.nextAction.strip() else get_default_next_action(status_val, complaint_in.bureau)
    last_action_date_val = complaint_in.lastActionDate.strip() if complaint_in.lastActionDate and complaint_in.lastActionDate.strip() else date_val

    # 8. Instantiate and save model along with initial timeline events in one transaction
    new_complaint = Complaint(
        id=case_id,
        institution_id=inst.id,
        institution_permanent_id=perm_id,
        bureau=complaint_in.bureau,
        category=complaint_in.category.strip(),
        priority=complaint_in.priority,
        status=status_val,
        officer=officer_name,
        assigned_user_id=assigned_user_id,
        date=date_val,
        due=due_val,
        title=complaint_in.title.strip(),
        description=complaint_in.description.strip(),
        complainant_type=complaint_in.complainantType or "General Public",
        complainant_name=complainant_name,
        complainant_email=complainant_email,
        complainant_phone=complainant_phone,
        remarks=complaint_in.remarks.strip() if complaint_in.remarks else None,
        next_action=next_action_val,
        last_action_date=last_action_date_val,
    )

    try:
        db.add(new_complaint)
        db.flush()

        # Record initial creation events in timeline
        now_hm = datetime.now(timezone.utc).strftime("%H:%M")
        event_intake = ComplaintTimeline(
            complaint_id=new_complaint.id,
            label="Complaint registered and verified on AICTE portal",
            date=f"{date_val} {now_hm}",
            by=f"{complainant_name} ({new_complaint.complainant_type})",
            role="Complainant",
            note="Portal intake verified; acknowledgement issued to complainant.",
            user_id=intake_user_id,
        )
        db.add(event_intake)

        allocation_by = f"{current_user.name} ({current_user.designation})" if current_user.role != "Complainant" else "Central Allocation Engine"
        allocation_role = current_user.role if current_user.role != "Complainant" else "Admin"
        event_allocation = ComplaintTimeline(
            complaint_id=new_complaint.id,
            label=f"Assigned to {officer_name} ({new_complaint.bureau} Bureau)",
            date=f"{date_val} {now_hm}",
            by=allocation_by,
            role=allocation_role,
            note=f"Initial statutory assignment to {new_complaint.bureau} Bureau based on category: {new_complaint.category}.",
            user_id=assigned_user_id,
        )
        db.add(event_allocation)

        db.commit()
        db.refresh(new_complaint)
    except Exception:
        db.rollback()
        raise

    return map_complaint_to_read(new_complaint)

@router.get("", response_model=ComplaintListResponse)
def list_complaints(
    search: Optional[str] = Query(None, description="Search term matching Case ID, title, description, or complainant"),
    bureau: Optional[str] = Query(None, description="Filter by Bureau (e.g. PGRC, RB, Approval)"),
    status: Optional[str] = Query(None, description="Filter by Status (e.g. Pending, In Progress, Resolved, Escalated)"),
    priority: Optional[str] = Query(None, description="Filter by Priority (e.g. Critical, High, Medium, Low)"),
    category: Optional[str] = Query(None, description="Filter by Category"),
    institutionId: Optional[str] = Query(None, alias="institutionId", description="Filter by Institution internal ID"),
    officer: Optional[str] = Query(None, description="Filter by assigned officer name"),
    page: int = Query(1, ge=1, description="Page number"),
    pageSize: int = Query(20, ge=1, le=100, alias="pageSize", description="Page size limit"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List registered grievance complaints with multi-parameter search, filtering and pagination.
    Applies role-based access scoping:
    - Complainant: Only views grievances submitted by themselves.
    - BureauAdmin: Scoped to their authorized Bureau (or all if All).
    - Officer: Scoped to assigned cases or their Bureau cell.
    - Admin: System-wide access across all Bureaus.
    """
    query = db.query(Complaint)

    # 1. Role-based scoping
    if current_user.role == "Complainant":
        query = query.filter(
            or_(
                Complaint.complainant_email.ilike(current_user.email.strip()),
                Complaint.complainant_name.ilike(current_user.name.strip()),
            )
        )
    elif current_user.role == "BureauAdmin":
        if current_user.bureau != "All":
            if bureau and bureau.strip() and bureau.lower() != "all" and bureau.strip().upper() != current_user.bureau.upper():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Restricted: Bureau Admin jurisdiction is {current_user.bureau}; cannot query {bureau} Bureau."
                )
            query = query.filter(Complaint.bureau.ilike(current_user.bureau))
    elif current_user.role == "Officer":
        if current_user.bureau != "All":
            query = query.filter(
                or_(
                    Complaint.officer.ilike(current_user.name.strip()),
                    Complaint.assigned_user_id == current_user.id,
                    Complaint.bureau.ilike(current_user.bureau),
                )
            )

    # 2. General filtering
    if bureau and bureau.strip() and bureau.lower() != "all" and current_user.role != "BureauAdmin":
        query = query.filter(Complaint.bureau.ilike(bureau.strip()))

    if status and status.strip() and status.lower() != "all":
        query = query.filter(Complaint.status.ilike(status.strip()))

    if priority and priority.strip() and priority.lower() != "all":
        query = query.filter(Complaint.priority.ilike(priority.strip()))

    if category and category.strip() and category.lower() != "all":
        query = query.filter(Complaint.category.ilike(f"%{category.strip()}%"))

    if institutionId and institutionId.strip() and institutionId.lower() != "all":
        query = query.filter(Complaint.institution_id == institutionId.strip())

    if officer and officer.strip() and officer.lower() != "all":
        query = query.filter(Complaint.officer.ilike(f"%{officer.strip()}%"))

    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Complaint.id.ilike(term),
                Complaint.title.ilike(term),
                Complaint.description.ilike(term),
                Complaint.complainant_name.ilike(term),
                Complaint.institution_permanent_id.ilike(term),
            )
        )

    total = query.count()
    total_pages = math.ceil(total / pageSize) if total > 0 else 0
    records = query.order_by(Complaint.date.desc(), Complaint.created_at.desc()).offset((page - 1) * pageSize).limit(pageSize).all()

    items = [map_complaint_to_read(c) for c in records]

    return ComplaintListResponse(
        items=items,
        total=total,
        page=page,
        pageSize=pageSize,
        totalPages=total_pages
    )

@router.get("/{id}", response_model=ComplaintRead)
def get_complaint(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve a single grievance complaint by its internal ID or Case ID.
    Enforces role-based and Bureau-scoped access control.
    """
    complaint = db.query(Complaint).filter(Complaint.id.ilike(id.strip())).first()

    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint with ID or Case ID '{id}' was not found."
        )

    check_case_access(current_user, complaint, action="view")

    return map_complaint_to_read(complaint)

@router.get("/{id}/timeline", response_model=List[TimelineEventRead])
def get_complaint_timeline(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve chronological audit history timeline events for a complaint.
    Enforces role-based access control.
    """
    complaint = db.query(Complaint).filter(Complaint.id.ilike(id.strip())).first()
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint with ID or Case ID '{id}' was not found."
        )

    check_case_access(current_user, complaint, action="view")

    events = db.query(ComplaintTimeline).filter(
        ComplaintTimeline.complaint_id == complaint.id
    ).order_by(ComplaintTimeline.id.asc()).all()

    return [
        TimelineEventRead(
            id=t.id,
            complaintId=t.complaint_id,
            label=t.label,
            date=t.date,
            by=t.by,
            role=t.role,
            note=t.note,
            userId=t.user_id,
            createdAt=t.created_at,
        )
        for t in events
    ]

@router.patch("/{id}/status", response_model=ComplaintRead)
@router.post("/{id}/status", response_model=ComplaintRead)
def update_complaint_status(
    id: str,
    payload: ComplaintStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update complaint status, remarks and next action, recording a chronological timeline event
    within the same database transaction.
    Enforces role permissions, Bureau jurisdiction, and permitted workflow status transitions.
    """
    complaint = db.query(Complaint).filter(Complaint.id.ilike(id.strip())).first()
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint with ID or Case ID '{id}' was not found."
        )

    # Enforce case authorization (Complainant -> 403, BureauAdmin cross-bureau -> 403, Officer not assigned/different bureau -> 403)
    check_case_access(current_user, complaint, action="update_status")

    target_status = payload.status
    if complaint.status == "Resolved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Case is Resolved and closed. Status transitions from 'Resolved' are not permitted."
        )

    if complaint.status == target_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Complaint is already in '{target_status}' status."
        )

    permitted = PERMITTED_STATUS_TRANSITIONS.get(complaint.status, [])
    if target_status not in permitted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status transition from '{complaint.status}' to '{target_status}' is not permitted. Permitted transitions: {', '.join(permitted) if permitted else 'None (Case Closed)'}."
        )

    # Actor identity strictly derived from the authenticated user
    actor_user_id = current_user.id
    actor_name = current_user.name
    actor_role = current_user.role

    # Atomic transaction: update complaint and insert timeline event
    try:
        today_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")

        complaint.status = target_status
        complaint.last_action_date = today_date

        if payload.remarks is not None:
            complaint.remarks = payload.remarks.strip()

        if payload.nextAction is not None and payload.nextAction.strip():
            complaint.next_action = payload.nextAction.strip()
        else:
            complaint.next_action = get_default_next_action(target_status, complaint.bureau)

        action_label = (
            "Case investigation concluded & Marked Resolved"
            if target_status == "Resolved"
            else f"Status transitioned to {target_status}"
        )
        note_text = payload.note.strip() if payload.note and payload.note.strip() else (
            payload.remarks.strip() if payload.remarks and payload.remarks.strip() else None
        )

        timeline_event = ComplaintTimeline(
            complaint_id=complaint.id,
            label=action_label,
            date=now_str,
            by=actor_name,
            role=actor_role,
            note=note_text,
            user_id=actor_user_id,
        )
        db.add(timeline_event)
        db.commit()
        db.refresh(complaint)
    except Exception:
        db.rollback()
        raise

    return map_complaint_to_read(complaint)

@router.patch("/{id}/assign", response_model=ComplaintRead)
@router.post("/{id}/assign", response_model=ComplaintRead)
def assign_complaint(
    id: str,
    payload: ComplaintAssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Assign or reassign a complaint to an eligible user/Bureau and record in the timeline
    within the same database transaction.
    Enforces role permissions, Bureau jurisdiction, and authentic timeline actor integrity.
    """
    complaint = db.query(Complaint).filter(Complaint.id.ilike(id.strip())).first()
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint with ID or Case ID '{id}' was not found."
        )

    # Enforce assignment authorization (Complainant -> 403, Officer -> 403, BureauAdmin cross-bureau -> 403, Admin -> OK)
    check_case_access(current_user, complaint, action="assign")

    if not payload.userId and not payload.officer and not payload.bureau:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must specify at least a userId, officer name, or bureau to update assignment."
        )

    target_officer = complaint.officer
    target_user_id = complaint.assigned_user_id
    target_bureau = payload.bureau or complaint.bureau

    # If BureauAdmin, ensure target bureau remains within their authority
    if current_user.role == "BureauAdmin" and current_user.bureau != "All":
        if payload.bureau and payload.bureau.strip().upper() != complaint.bureau.upper():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Restricted: Bureau Admin can only transfer cases originating in their authorized Bureau ({current_user.bureau}).",
            )

    # 1. Resolve user by userId if provided
    resolved_user: Optional[User] = None
    if payload.userId and payload.userId.strip():
        resolved_user = db.query(User).filter(User.id == payload.userId.strip()).first()
        if not resolved_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with ID '{payload.userId}' was not found in AICTE user registry."
            )
        if resolved_user.status.lower() != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User '{resolved_user.name}' is inactive and cannot be assigned cases."
            )
        if resolved_user.role not in ("Officer", "BureauAdmin", "Admin"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User '{resolved_user.name}' has role '{resolved_user.role}' and is not eligible for case assignment."
            )
        if current_user.role == "BureauAdmin" and current_user.bureau != "All":
            if resolved_user.bureau != "All" and resolved_user.bureau.upper() != current_user.bureau.upper():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Restricted: Bureau Admin cannot assign case to officer in {resolved_user.bureau} Bureau.",
                )
        target_officer = resolved_user.name
        target_user_id = resolved_user.id
        if not payload.bureau and resolved_user.bureau != "All":
            target_bureau = resolved_user.bureau

    # 2. Or resolve by officer name if provided
    elif payload.officer and payload.officer.strip():
        resolved_user = db.query(User).filter(User.name.ilike(payload.officer.strip())).first()
        if not resolved_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Officer '{payload.officer}' was not found in AICTE user registry."
            )
        if resolved_user.status.lower() != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Officer '{resolved_user.name}' is inactive and cannot be assigned cases."
            )
        if current_user.role == "BureauAdmin" and current_user.bureau != "All":
            if resolved_user.bureau != "All" and resolved_user.bureau.upper() != current_user.bureau.upper():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Restricted: Bureau Admin cannot assign case to officer in {resolved_user.bureau} Bureau.",
                )
        target_officer = resolved_user.name
        target_user_id = resolved_user.id
        if not payload.bureau and resolved_user.bureau != "All":
            target_bureau = resolved_user.bureau

    prev_officer = complaint.officer
    prev_bureau = complaint.bureau

    # Generate timeline label
    is_officer_changed = (target_officer != prev_officer)
    is_bureau_changed = (target_bureau != prev_bureau)

    if is_officer_changed and is_bureau_changed:
        action_label = f"Case reassigned from {prev_officer} ({prev_bureau} Bureau) to {target_officer} ({target_bureau} Bureau)"
    elif is_officer_changed:
        action_label = f"Investigating officer reassigned from {prev_officer} to {target_officer}"
    elif is_bureau_changed:
        action_label = f"Case transferred from {prev_bureau} Bureau to {target_bureau} Bureau"
    else:
        action_label = f"Case assignment confirmed for {target_officer} ({target_bureau} Bureau)"

    # Atomic transaction: update complaint and insert timeline event
    try:
        today_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")

        complaint.officer = target_officer
        complaint.assigned_user_id = target_user_id
        complaint.bureau = target_bureau
        complaint.last_action_date = today_date

        reason_text = payload.reason.strip() if payload.reason and payload.reason.strip() else f"Administrative case assignment within {target_bureau} Bureau."

        timeline_event = ComplaintTimeline(
            complaint_id=complaint.id,
            label=action_label,
            date=now_str,
            by=current_user.name,
            role=current_user.role,
            note=f"Administrative Justification: {reason_text}",
            user_id=current_user.id,
        )
        db.add(timeline_event)
        db.commit()
        db.refresh(complaint)
    except Exception:
        db.rollback()
        raise

    return map_complaint_to_read(complaint)
