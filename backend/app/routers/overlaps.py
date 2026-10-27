from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.complaint import Complaint
from app.models.timeline import ComplaintTimeline
from app.models.user import User
from app.models.overlap import ComplaintOverlap, ComplaintOverlapHistory
from app.schemas.overlap import (
    OverlapDecisionUpdate,
    OverlapCreate,
    OverlapRead,
    OverlapHistoryRead,
    LinkedDocketRead,
)
from app.auth import get_current_user

router = APIRouter(prefix="/overlaps", tags=["Overlaps"])


def _format_overlap_read(overlap: ComplaintOverlap) -> OverlapRead:
    reasons_list = overlap.reasons if isinstance(overlap.reasons, list) else []
    history_list = [
        OverlapHistoryRead(
            id=h.id,
            overlap_id=h.overlap_id,
            decision_state=h.decision_state,
            justification=h.justification,
            actor_name=h.actor_name,
            actor_user_id=h.actor_user_id,
            actor_role=h.actor_role,
            created_at=h.created_at,
        )
        for h in getattr(overlap, "history", [])
    ]
    return OverlapRead(
        id=overlap.id,
        complaint_a_id=overlap.complaint_a_id,
        complaint_b_id=overlap.complaint_b_id,
        a=overlap.complaint_a_id,
        b=overlap.complaint_b_id,
        similarity=overlap.similarity,
        reasons=reasons_list,
        status=overlap.status,
        decision_state=overlap.decision_state,
        justification=overlap.justification,
        reviewed_by=overlap.reviewed_by,
        reviewed_by_user_id=overlap.reviewed_by_user_id,
        reviewed_at=overlap.reviewed_at,
        created_at=overlap.created_at,
        updated_at=overlap.updated_at,
        history=history_list,
    )


@router.get("", response_model=List[OverlapRead])
def list_overlaps(
    bureau: Optional[str] = Query(None, description="Filter by Bureau of either complaint"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by decision status (open, linked, dismissed, deferred)"),
    min_similarity: Optional[int] = Query(None, description="Filter candidates by minimum similarity threshold"),
    include_below_threshold: bool = Query(False, description="Include open candidates below the threshold"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List cross-bureau complaint overlaps.
    Enforces authorization: Complainants are rejected with 403 Forbidden.
    Applies authoritative similarity threshold to open candidates while preserving historical decisions intact.
    """
    if current_user.role == "Complainant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Complainants are not permitted to access cross-bureau overlap intelligence.",
        )

    from app.models.setting import SystemSetting
    setting = db.query(SystemSetting).filter(SystemSetting.key == "global").first()
    effective_threshold = (
        min_similarity
        if min_similarity is not None
        else (setting.similarity_threshold if setting else 75)
    )

    query = db.query(ComplaintOverlap)

    if status_filter and status_filter.lower() != "all":
        norm_status = "open" if status_filter.lower() == "pending" else status_filter.lower()
        if norm_status == "open":
            query = query.filter(or_(ComplaintOverlap.status == "open", ComplaintOverlap.status == "pending"))
            if not include_below_threshold:
                query = query.filter(ComplaintOverlap.similarity >= effective_threshold)
        else:
            query = query.filter(ComplaintOverlap.status == norm_status)
    elif not include_below_threshold:
        # All statuses: preserve all historical decisions (linked/dismissed/deferred),
        # but filter unreviewed open candidates below the active threshold
        query = query.filter(
            or_(
                ComplaintOverlap.status.notin_(["open", "pending"]),
                ComplaintOverlap.similarity >= effective_threshold,
            )
        )

    overlaps = query.order_by(ComplaintOverlap.similarity.desc()).all()

    # Filter by bureau jurisdiction if specified or if user is BureauAdmin
    filtered = []
    for ov in overlaps:
        comp_a = db.query(Complaint).filter(Complaint.id == ov.complaint_a_id).first()
        comp_b = db.query(Complaint).filter(Complaint.id == ov.complaint_b_id).first()

        # Bureau query filter
        if bureau and bureau.lower() != "all":
            a_match = comp_a and comp_a.bureau.lower() == bureau.lower()
            b_match = comp_b and comp_b.bureau.lower() == bureau.lower()
            if not (a_match or b_match):
                continue

        filtered.append(_format_overlap_read(ov))

    return filtered


@router.get("/{overlap_id}", response_model=OverlapRead)
def get_overlap(
    overlap_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get single overlap pair with decision history."""
    if current_user.role == "Complainant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Complainants are not permitted to access cross-bureau overlap intelligence.",
        )

    overlap = db.query(ComplaintOverlap).filter(ComplaintOverlap.id == overlap_id).first()
    if not overlap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Overlap record with ID '{overlap_id}' was not found.",
        )

    return _format_overlap_read(overlap)


@router.post("", response_model=OverlapRead, status_code=status.HTTP_201_CREATED)
def create_overlap(
    payload: OverlapCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Register a new cross-bureau overlap candidate pair."""
    if current_user.role not in ["Admin", "BureauAdmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only System Admins and Bureau Admins can register overlap candidate relationships.",
        )

    if payload.complaint_a_id == payload.complaint_b_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create an overlap link from a complaint to itself.",
        )

    comp_a = db.query(Complaint).filter(Complaint.id == payload.complaint_a_id).first()
    if not comp_a:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint with ID or Case ID '{payload.complaint_a_id}' was not found.",
        )

    comp_b = db.query(Complaint).filter(Complaint.id == payload.complaint_b_id).first()
    if not comp_b:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint with ID or Case ID '{payload.complaint_b_id}' was not found.",
        )

    # Check for existing overlap
    existing = db.query(ComplaintOverlap).filter(
        or_(
            (ComplaintOverlap.complaint_a_id == payload.complaint_a_id) & (ComplaintOverlap.complaint_b_id == payload.complaint_b_id),
            (ComplaintOverlap.complaint_a_id == payload.complaint_b_id) & (ComplaintOverlap.complaint_b_id == payload.complaint_a_id),
        )
    ).first()

    if existing:
        return _format_overlap_read(existing)

    overlap_id = payload.id or f"o{int(datetime.now(timezone.utc).timestamp())}"
    new_overlap = ComplaintOverlap(
        id=overlap_id,
        complaint_a_id=payload.complaint_a_id,
        complaint_b_id=payload.complaint_b_id,
        similarity=payload.similarity,
        reasons=payload.reasons or [],
        status="open",
    )
    db.add(new_overlap)
    db.commit()
    db.refresh(new_overlap)
    return _format_overlap_read(new_overlap)


@router.patch("/{overlap_id}/decision", response_model=OverlapRead)
def update_overlap_decision(
    overlap_id: str,
    payload: OverlapDecisionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Review, confirm, defer, or dismiss an overlap decision.
    - Transactional: persists relationship and timeline events atomically.
    - RBAC: Strictly requires Admin or BureauAdmin.
    - Scope: BureauAdmin restricted to dockets in their Bureau.
    - Auditable: writes to complaint_overlap_history and both complaint_timelines.
    - Independent: Complaints are NOT merged, reallocated, or altered in status.
    """
    if current_user.role not in ["Admin", "BureauAdmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only System Admins and Bureau Admins can review or confirm overlap relationships.",
        )

    overlap = db.query(ComplaintOverlap).filter(ComplaintOverlap.id == overlap_id).first()
    if not overlap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Overlap record with ID '{overlap_id}' was not found.",
        )

    # Validate that both complaints exist and are distinct
    if overlap.complaint_a_id == overlap.complaint_b_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot link a complaint to itself.",
        )

    comp_a = db.query(Complaint).filter(Complaint.id == overlap.complaint_a_id).first()
    if not comp_a:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint with ID or Case ID '{overlap.complaint_a_id}' was not found.",
        )

    comp_b = db.query(Complaint).filter(Complaint.id == overlap.complaint_b_id).first()
    if not comp_b:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint with ID or Case ID '{overlap.complaint_b_id}' was not found.",
        )

    # Enforce Bureau scope for Bureau Admins
    is_bureau_admin = current_user.role == "BureauAdmin" or (
        current_user.role == "Admin" and current_user.bureau and current_user.bureau != "All"
    )
    if is_bureau_admin:
        user_bureau = (current_user.bureau or "").strip()
        if user_bureau not in [comp_a.bureau, comp_b.bureau]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Bureau Admin jurisdiction restricted: neither docket ({comp_a.id} in {comp_a.bureau}, {comp_b.id} in {comp_b.bureau}) belongs to your authorized Bureau ('{user_bureau}').",
            )

    decision_target = "open" if payload.state in ["open", "reset"] else payload.state
    justification_text = (payload.justification or "").strip()

    # Prevent duplicate active relationships
    if decision_target == "linked":
        if overlap.status == "linked":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Overlap #{overlap.id} between {comp_a.id} and {comp_b.id} is already active.",
            )
        # Check if another overlap between this pair is already linked
        duplicate_active = db.query(ComplaintOverlap).filter(
            or_(
                (ComplaintOverlap.complaint_a_id == comp_a.id) & (ComplaintOverlap.complaint_b_id == comp_b.id),
                (ComplaintOverlap.complaint_a_id == comp_b.id) & (ComplaintOverlap.complaint_b_id == comp_a.id),
            ),
            ComplaintOverlap.id != overlap.id,
            ComplaintOverlap.status == "linked"
        ).first()
        if duplicate_active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"An active confirmed relationship already exists between docket {comp_a.id} and {comp_b.id} under Overlap #{duplicate_active.id}.",
            )

    was_already_linked = (overlap.status == "linked")

    try:
        user_in_db = db.query(User).filter(User.id == current_user.id).first() if current_user.id else None
        actor_id_val = user_in_db.id if user_in_db else None

        overlap.status = decision_target
        overlap.decision_state = decision_target if decision_target != "open" else None
        overlap.justification = justification_text or None
        designation = getattr(current_user, "designation", None) or current_user.role
        overlap.reviewed_by = f"{current_user.name} ({designation})"
        overlap.reviewed_by_user_id = actor_id_val
        overlap.reviewed_at = datetime.now(timezone.utc)

        # 1. Auditable decision history record
        history_entry = ComplaintOverlapHistory(
            overlap_id=overlap.id,
            decision_state=decision_target,
            justification=justification_text or None,
            actor_name=current_user.name,
            actor_user_id=actor_id_val,
            actor_role=current_user.role,
        )
        db.add(history_entry)

        # 2. If decision is confirmed 'linked' and wasn't already linked, add coordination event to both complaints
        if decision_target == "linked" and not was_already_linked:
            now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
            today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

            reason_suffix = f" Justification: {justification_text}" if justification_text else ""

            timeline_a = ComplaintTimeline(
                complaint_id=comp_a.id,
                label=f"Cross-Bureau Overlap Confirmed: Linked with Docket {comp_b.id}",
                date=now_str,
                by=f"{current_user.name} ({designation})",
                role=current_user.role,
                note=f"Cross-bureau inquiry coordination established with docket {comp_b.id} ({comp_b.bureau} Bureau).{reason_suffix}",
                user_id=actor_id_val,
            )
            timeline_b = ComplaintTimeline(
                complaint_id=comp_b.id,
                label=f"Cross-Bureau Overlap Confirmed: Linked with Docket {comp_a.id}",
                date=now_str,
                by=f"{current_user.name} ({designation})",
                role=current_user.role,
                note=f"Cross-bureau inquiry coordination established with docket {comp_a.id} ({comp_a.bureau} Bureau).{reason_suffix}",
                user_id=actor_id_val,
            )
            db.add(timeline_a)
            db.add(timeline_b)

            comp_a.last_action_date = today_str
            comp_b.last_action_date = today_str

        db.commit()
        db.refresh(overlap)
        return _format_overlap_read(overlap)
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to persist overlap decision transaction: {str(e)}",
        )


@router.get("/linked/{complaint_id}", response_model=List[LinkedDocketRead])
def get_linked_dockets_for_complaint(
    complaint_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all confirmed linked dockets for a specific complaint.
    Returns linked docket Case ID, Bureau, similarity, and confirmation rationale.
    """
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Complaint with ID or Case ID '{complaint_id}' was not found.",
        )

    # Check access to the complaint
    if current_user.role == "Complainant" and complaint.complainant_email != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to access docket information for this complaint.",
        )

    overlaps = db.query(ComplaintOverlap).filter(
        or_(
            ComplaintOverlap.complaint_a_id == complaint.id,
            ComplaintOverlap.complaint_b_id == complaint.id,
        ),
        ComplaintOverlap.status == "linked",
    ).all()

    linked: List[LinkedDocketRead] = []
    for ov in overlaps:
        other_id = ov.complaint_b_id if ov.complaint_a_id == complaint.id else ov.complaint_a_id
        other_comp = db.query(Complaint).filter(Complaint.id == other_id).first()
        if other_comp:
            linked.append(
                LinkedDocketRead(
                    overlap_id=ov.id,
                    case_id=other_comp.id,
                    bureau=other_comp.bureau,
                    title=other_comp.title,
                    similarity=ov.similarity,
                    justification=ov.justification,
                    confirmed_by=ov.reviewed_by,
                    confirmed_at=ov.reviewed_at,
                )
            )

    return linked
