import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.database import get_db
from app.models.user import User
from app.models.complaint import Complaint
from app.schemas.user import UserProfileRead, UserCreate, UserUpdate, UserStatusUpdate
from app.auth import get_current_user, hash_password
from app.routers.auth import get_user_profile_read

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=List[UserProfileRead])
def list_users(
    role: Optional[str] = Query(None, description="Filter by system role (e.g. Officer, BureauAdmin, Admin, Complainant)"),
    bureau: Optional[str] = Query(None, description="Filter by assigned Bureau (e.g. PGRC, RB, All)"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (Active, On Leave, Inactive)"),
    search: Optional[str] = Query(None, description="Search term matching name, email, designation, or bureau"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List personnel and users in the AICTE directory.
    Enforces authorization: Complainants are rejected with 403 Forbidden.
    System Admin and official staff (BureauAdmin, Officer) can query the directory.
    """
    if current_user.role == "Complainant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Complainants are not permitted to access personnel directory.",
        )

    query = db.query(User)

    if role and role.strip() and role.lower() != "all":
        query = query.filter(User.role.ilike(role.strip()))

    if bureau and bureau.strip() and bureau.lower() != "all":
        query = query.filter(User.bureau.ilike(bureau.strip()))

    if status_filter and status_filter.strip() and status_filter.lower() != "all":
        query = query.filter(User.status.ilike(status_filter.strip()))

    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                User.name.ilike(term),
                User.email.ilike(term),
                User.designation.ilike(term),
                User.bureau.ilike(term),
            )
        )

    users = query.order_by(User.id.asc()).all()
    return [get_user_profile_read(u, db) for u in users]


@router.get("/{id}", response_model=UserProfileRead)
def get_user_by_id(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve user profile and active cases count by user ID.
    Enforces authorization: Complainants are rejected with 403 Forbidden.
    """
    if current_user.role == "Complainant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Complainants are not permitted to access personnel directory.",
        )

    user = db.query(User).filter(User.id == id.strip()).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{id}' was not found in AICTE directory.",
        )

    return get_user_profile_read(user, db)


@router.post("", response_model=UserProfileRead, status_code=status.HTTP_201_CREATED)
def create_official_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Provision an official user account and assign privileges/bureau jurisdiction.
    Enforces authorization: Only System Administrator (Admin) holds provisioning authority.
    Validates email uniqueness, hashes passwords securely, and assigns stable unique ID.
    """
    if current_user.role != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Only System Administrators can provision official accounts and assign roles.",
        )

    clean_email = payload.email.strip().lower()
    existing = db.query(User).filter(func.lower(User.email) == clean_email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An officer with official email '{clean_email}' is already registered in the directory.",
        )

    # Compute avatar initials from name
    parts = payload.name.strip().split()
    if len(parts) >= 2:
        avatar_text = (parts[0][0] + parts[-1][0]).upper()
    elif len(parts) == 1 and len(parts[0]) >= 2:
        avatar_text = parts[0][:2].upper()
    else:
        avatar_text = "OF"

    user_id = f"u-{uuid.uuid4().hex[:8]}"
    password_hash = hash_password(payload.password.strip())

    default_designation = (
        payload.designation.strip()
        if payload.designation and payload.designation.strip()
        else ("Grievance Officer" if payload.role == "Officer" else f"{payload.role} Officer")
    )

    new_user = User(
        id=user_id,
        name=payload.name.strip(),
        email=clean_email,
        role=payload.role,
        designation=default_designation,
        bureau=payload.bureau,
        avatar_text=avatar_text,
        phone=payload.phone.strip() if payload.phone else "",
        status=payload.status or "Active",
        department=payload.department.strip() if payload.department and payload.department.strip() else f"{payload.bureau} Bureau",
        password_hash=password_hash,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return get_user_profile_read(new_user, db)


@router.patch("/{id}", response_model=UserProfileRead)
@router.put("/{id}", response_model=UserProfileRead)
def update_user(
    id: str,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update user profile attributes, bureau jurisdiction, or reassign system roles.
    Enforces authorization: Only System Administrator (Admin) holds update authority.
    Guards email uniqueness and hashes new password if supplied.
    """
    if current_user.role != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Only System Administrators can modify user accounts and roles.",
        )

    user = db.query(User).filter(User.id == id.strip()).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{id}' was not found in AICTE directory.",
        )

    if user.id == current_user.id and payload.role is not None and payload.role != "Admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="System Administrator cannot revoke their own administrative privileges.",
        )

    if payload.email is not None:
        clean_email = payload.email.strip().lower()
        if clean_email != user.email.lower():
            dup = db.query(User).filter(func.lower(User.email) == clean_email, User.id != user.id).first()
            if dup:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"An account with email '{clean_email}' already exists in the directory.",
                )
            user.email = clean_email

    if payload.name is not None and payload.name.strip():
        user.name = payload.name.strip()
        parts = user.name.split()
        if len(parts) >= 2:
            user.avatar_text = (parts[0][0] + parts[-1][0]).upper()
        elif len(parts) == 1 and len(parts[0]) >= 2:
            user.avatar_text = parts[0][:2].upper()

    if payload.role is not None:
        user.role = payload.role

    if payload.bureau is not None:
        user.bureau = payload.bureau

    if payload.designation is not None:
        user.designation = payload.designation.strip()

    if payload.phone is not None:
        user.phone = payload.phone.strip()

    if payload.department is not None:
        user.department = payload.department.strip()

    if payload.status is not None:
        user.status = payload.status

    if payload.password is not None and payload.password.strip():
        user.password_hash = hash_password(payload.password)

    db.commit()
    db.refresh(user)

    return get_user_profile_read(user, db)


@router.patch("/{id}/status", response_model=UserProfileRead)
def update_user_status(
    id: str,
    payload: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Activate, deactivate, or toggle official duty status for a bureau officer.
    Enforces authorization: Only System Administrator (Admin) holds status modification authority.
    """
    if current_user.role != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Only System Administrators can alter officer duty status.",
        )

    user = db.query(User).filter(User.id == id.strip()).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{id}' was not found in AICTE directory.",
        )

    if user.id == current_user.id and payload.status != "Active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="System Administrator cannot deactivate their own active session account.",
        )

    user.status = payload.status
    db.commit()
    db.refresh(user)

    return get_user_profile_read(user, db)
