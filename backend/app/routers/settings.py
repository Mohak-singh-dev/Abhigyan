from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.setting import SystemSetting
from app.models.user import User
from app.schemas.setting import SettingRead, SettingUpdate
from app.auth import get_current_user

router = APIRouter(prefix="/settings", tags=["Settings"])

DEFAULT_SETTING_VALUES = {
    "key": "global",
    "similarity_threshold": 75,
    "sla_critical": 3,
    "sla_high": 7,
    "sla_medium": 14,
    "auto_escalate": True,
    "email_alerts": True,
    "updated_by": "System Initialization",
}


def _get_or_create_global_settings(db: Session) -> SystemSetting:
    setting = db.query(SystemSetting).filter(SystemSetting.key == "global").first()
    if not setting:
        setting = SystemSetting(
            key=DEFAULT_SETTING_VALUES["key"],
            similarity_threshold=DEFAULT_SETTING_VALUES["similarity_threshold"],
            sla_critical=DEFAULT_SETTING_VALUES["sla_critical"],
            sla_high=DEFAULT_SETTING_VALUES["sla_high"],
            sla_medium=DEFAULT_SETTING_VALUES["sla_medium"],
            auto_escalate=DEFAULT_SETTING_VALUES["auto_escalate"],
            email_alerts=DEFAULT_SETTING_VALUES["email_alerts"],
            updated_by=DEFAULT_SETTING_VALUES["updated_by"],
            updated_at=datetime.now(timezone.utc),
        )
        db.add(setting)
        db.commit()
        db.refresh(setting)
    return setting


def _validate_sla_hierarchy(crit: int, high: int, med: int):
    if crit >= high:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SLA Logic Conflict: Critical severity SLA window must be shorter than High priority window.",
        )
    if high >= med:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SLA Logic Conflict: High priority SLA window must be shorter than Standard / Medium window.",
        )


@router.get("", response_model=SettingRead)
def get_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve authoritative system settings.
    Accessible to all authenticated users so client interfaces align on SLA and threshold parameters.
    """
    setting = _get_or_create_global_settings(db)
    return setting


@router.put("", response_model=SettingRead)
@router.patch("", response_model=SettingRead)
def update_settings(
    payload: SettingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update global system settings.
    Enforces authorization: Only System Admin (role 'Admin' and bureau 'All') may modify global configuration.
    """
    if not (current_user.role == "Admin" and current_user.bureau == "All"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only System Administrator can modify global system and SLA configuration.",
        )

    setting = _get_or_create_global_settings(db)

    # Determine proposed values (merge existing with updates)
    new_threshold = (
        payload.similarity_threshold
        if payload.similarity_threshold is not None
        else setting.similarity_threshold
    )
    new_crit = (
        payload.sla_critical
        if payload.sla_critical is not None
        else setting.sla_critical
    )
    new_high = (
        payload.sla_high
        if payload.sla_high is not None
        else setting.sla_high
    )
    new_med = (
        payload.sla_medium
        if payload.sla_medium is not None
        else setting.sla_medium
    )
    new_auto_esc = (
        payload.auto_escalate
        if payload.auto_escalate is not None
        else setting.auto_escalate
    )
    new_email = (
        payload.email_alerts
        if payload.email_alerts is not None
        else setting.email_alerts
    )

    # Validate threshold bounds
    if new_threshold < 50 or new_threshold > 95:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid threshold: Overlap similarity threshold must be an integer between 50% and 95%.",
        )

    # Validate individual SLA bounds
    if new_crit < 1 or new_crit > 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Critical SLA: Must be a positive business duration between 1 and 30 days.",
        )
    if new_high < 1 or new_high > 60:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid High SLA: Must be a positive business duration between 1 and 60 days.",
        )
    if new_med < 1 or new_med > 90:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Standard SLA: Must be a positive business duration between 1 and 90 days.",
        )

    # Validate SLA hierarchy
    _validate_sla_hierarchy(new_crit, new_high, new_med)

    # Apply changes
    setting.similarity_threshold = new_threshold
    setting.sla_critical = new_crit
    setting.sla_high = new_high
    setting.sla_medium = new_med
    setting.auto_escalate = new_auto_esc
    setting.email_alerts = new_email
    setting.updated_at = datetime.now(timezone.utc)
    setting.updated_by = current_user.name

    # Check user in DB for foreign key reference
    db_user = db.query(User).filter(User.id == current_user.id).first()
    setting.updated_by_user_id = db_user.id if db_user else None

    db.commit()
    db.refresh(setting)
    return setting


@router.post("/reset", response_model=SettingRead)
def reset_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Reset settings to demonstration default parameters.
    Only authorized System Admins may reset configuration.
    """
    if not (current_user.role == "Admin" and current_user.bureau == "All"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only System Administrator can reset global system and SLA configuration.",
        )

    setting = _get_or_create_global_settings(db)
    setting.similarity_threshold = DEFAULT_SETTING_VALUES["similarity_threshold"]
    setting.sla_critical = DEFAULT_SETTING_VALUES["sla_critical"]
    setting.sla_high = DEFAULT_SETTING_VALUES["sla_high"]
    setting.sla_medium = DEFAULT_SETTING_VALUES["sla_medium"]
    setting.auto_escalate = DEFAULT_SETTING_VALUES["auto_escalate"]
    setting.email_alerts = DEFAULT_SETTING_VALUES["email_alerts"]
    setting.updated_at = datetime.now(timezone.utc)
    setting.updated_by = f"{current_user.name} (Reset to Defaults)"

    db_user = db.query(User).filter(User.id == current_user.id).first()
    setting.updated_by_user_id = db_user.id if db_user else None

    db.commit()
    db.refresh(setting)
    return setting
