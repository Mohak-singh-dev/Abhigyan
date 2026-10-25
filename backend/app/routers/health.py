from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db

router = APIRouter(prefix="", tags=["Health"])

@router.get("/health")
def check_health(db: Session = Depends(get_db)):
    """
    Service health check endpoint.
    Verifies that the FastAPI application and PostgreSQL connection are operational.
    """
    try:
        result = db.execute(text("SELECT 1")).scalar()
        if result != 1:
            raise HTTPException(status_code=500, detail="Database ping failed")
        return {
            "status": "healthy",
            "database": "connected",
            "service": "Abhigyan Complaint Monitoring API",
            "phase": "Phase 1: Foundations"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection error: {str(e)}"
        )
