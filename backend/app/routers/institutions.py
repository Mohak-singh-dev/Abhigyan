from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.institution import Institution
from app.schemas.institution import InstitutionRead

router = APIRouter(prefix="/institutions", tags=["Institutions"])

@router.get("", response_model=List[InstitutionRead])
def list_institutions(
    search: Optional[str] = Query(None, description="Search term for name, city, state, or AICTE ID"),
    state: Optional[str] = Query(None, description="Filter by state (or 'All')"),
    type: Optional[str] = Query(None, description="Filter by institution type (or 'All')"),
    db: Session = Depends(get_db)
):
    """
    List registered technical institutions.
    Supports search query matching across name, city, state, and AICTE permanent ID.
    """
    query = db.query(Institution)

    if state and state.lower() != "all":
        query = query.filter(Institution.state.ilike(state))

    if type and type.lower() != "all":
        query = query.filter(Institution.type.ilike(type))

    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Institution.name.ilike(term),
                Institution.city.ilike(term),
                Institution.state.ilike(term),
                Institution.aicte_id.ilike(term),
                Institution.type.ilike(term)
            )
        )

    institutions = query.order_by(Institution.name.asc()).all()

    # Map model attributes to response schema
    results: List[InstitutionRead] = []
    for inst in institutions:
        results.append(
            InstitutionRead(
                id=inst.id,
                aicteId=inst.aicte_id,
                name=inst.name,
                city=inst.city,
                state=inst.state,
                type=inst.type,
                approved=inst.approved,
                contactEmail=inst.contact_email,
                contactPhone=inst.contact_phone,
                riskLevel=inst.risk_level or "Low",
                totalComplaints=0,
                activeComplaints=0
            )
        )
    return results

@router.get("/{institution_id}", response_model=InstitutionRead)
def get_institution(institution_id: str, db: Session = Depends(get_db)):
    """
    Retrieve single technical institution by ID or AICTE permanent ID.
    """
    inst = db.query(Institution).filter(
        or_(
            Institution.id == institution_id,
            Institution.aicte_id == institution_id
        )
    ).first()

    if not inst:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Institution with ID '{institution_id}' was not found in AICTE registry."
        )

    return InstitutionRead(
        id=inst.id,
        aicteId=inst.aicte_id,
        name=inst.name,
        city=inst.city,
        state=inst.state,
        type=inst.type,
        approved=inst.approved,
        contactEmail=inst.contact_email,
        contactPhone=inst.contact_phone,
        riskLevel=inst.risk_level or "Low",
        totalComplaints=0,
        activeComplaints=0
    )
