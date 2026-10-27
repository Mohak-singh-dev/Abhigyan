import logging
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func

from app.database import get_db
from app.models.complaint import Complaint
from app.models.overlap import ComplaintOverlap
from app.models.setting import SystemSetting
from app.models.user import User
from app.auth import get_current_user
from app.routers.complaints import map_complaint_to_read
from app.schemas.analytics import (
    DashboardAnalyticsResponse,
    DashboardKPIs,
    BureauBreakdownItem,
    PriorityDistributionItem,
    ReportsAnalyticsResponse,
    ReportsKPIs,
    CategoryDistributionItem,
    StatusDistributionItem,
    MonthlyTrendItem,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["Analytics"])

STANDARD_BUREAUS = ["RB", "PGRC", "Approval", "Academic", "SB", "EO"]
STATUS_ORDER = ["Pending", "In Progress", "Escalated", "Resolved"]
PRIORITY_COLORS = {
    "Critical": "#dc2626",
    "High": "#ea580c",
    "Medium": "#d97706",
    "Low": "#64748b",
}


def _get_scoped_complaints_query(
    db: Session,
    current_user: User,
    bureau: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    """
    Build an SQLAlchemy query for Complaints with strict role-based scoping and date/bureau filters.
    """
    query = db.query(Complaint)

    # 1. Role-based scoping
    if current_user.role == "Complainant":
        query = query.filter(
            or_(
                Complaint.complainant_user_id == current_user.id,
                Complaint.complainant_email.ilike(current_user.email.strip()),
            )
        )
    elif current_user.role == "BureauAdmin":
        if current_user.bureau != "All":
            if bureau and bureau.strip() and bureau.lower() != "all" and bureau.strip().upper() != current_user.bureau.upper():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Restricted: Bureau Admin jurisdiction is {current_user.bureau}; cannot query {bureau} Bureau.",
                )
            query = query.filter(Complaint.bureau.ilike(current_user.bureau))
    elif current_user.role == "Officer":
        query = query.filter(
            or_(
                Complaint.assigned_user_id == current_user.id,
                and_(
                    Complaint.assigned_user_id.is_(None),
                    Complaint.officer.ilike(current_user.name.strip()),
                ),
            )
        )

    # 2. General bureau filter (for Admin or unconstrained BureauAdmin)
    if bureau and bureau.strip() and bureau.lower() != "all" and current_user.role != "BureauAdmin":
        query = query.filter(Complaint.bureau.ilike(bureau.strip()))

    # 3. Date range filters (based on filing date YYYY-MM-DD)
    if start_date and start_date.strip():
        query = query.filter(func.substr(Complaint.date, 1, 10) >= start_date.strip()[:10])
    if end_date and end_date.strip():
        query = query.filter(func.substr(Complaint.date, 1, 10) <= end_date.strip()[:10])

    return query


def _get_active_threshold(db: Session) -> int:
    try:
        setting = db.query(SystemSetting).filter(SystemSetting.key == "global").first()
        return setting.similarity_threshold if setting else 75
    except Exception:
        return 75


def _calculate_pending_overlaps(db: Session, current_user: User) -> int:
    if current_user.role == "Complainant":
        return 0

    threshold = _get_active_threshold(db)
    query = db.query(ComplaintOverlap).filter(
        or_(ComplaintOverlap.status == "open", ComplaintOverlap.status == "pending"),
        ComplaintOverlap.similarity >= threshold,
    )
    overlaps = query.all()

    if current_user.role == "BureauAdmin" and current_user.bureau != "All":
        user_bureau = current_user.bureau.upper()
        matching = 0
        for ov in overlaps:
            ca = db.query(Complaint).filter(Complaint.id == ov.complaint_a_id).first()
            cb = db.query(Complaint).filter(Complaint.id == ov.complaint_b_id).first()
            if (ca and ca.bureau.upper() == user_bureau) or (cb and cb.bureau.upper() == user_bureau):
                matching += 1
        return matching

    return len(overlaps)


@router.get("/dashboard", response_model=DashboardAnalyticsResponse)
def get_dashboard_analytics(
    bureau: Optional[str] = Query(None, description="Filter by Bureau (e.g. RB, PGRC, Approval, Academic, All)"),
    startDate: Optional[str] = Query(None, description="Earliest complaint date (YYYY-MM-DD)"),
    endDate: Optional[str] = Query(None, description="Latest complaint date (YYYY-MM-DD)"),
    asOfDate: Optional[str] = Query(None, description="Evaluation reference date for overdue calculations (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get real database-backed aggregate metrics for the dashboard.
    Enforces role-based scoping:
    - Complainants: Only their permitted complaints.
    - Officers: Only their assigned complaints.
    - BureauAdmins: Cases within their authorized bureau jurisdiction.
    - System Admins: Organization-wide aggregates.
    """
    ref_date = asOfDate.strip() if asOfDate and asOfDate.strip() else datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Fetch all complaints in the authorized scope and filtered window
    query = _get_scoped_complaints_query(
        db=db,
        current_user=current_user,
        bureau=bureau,
        start_date=startDate,
        end_date=endDate,
    )
    complaints: List[Complaint] = query.all()

    total = len(complaints)
    pending = sum(1 for c in complaints if c.status == "Pending")
    in_progress = sum(1 for c in complaints if c.status == "In Progress")
    resolved = sum(1 for c in complaints if c.status == "Resolved")
    escalated = sum(1 for c in complaints if c.status == "Escalated")
    under_investigation = pending + in_progress

    # Overdue: status != 'Resolved' and due < ref_date
    overdue = sum(1 for c in complaints if c.status != "Resolved" and c.due and c.due < ref_date)
    critical_high = sum(1 for c in complaints if c.priority in ("Critical", "High"))
    resolution_rate = round((resolved / total) * 100) if total > 0 else 0

    # Calculate real month-over-month trend for total filed complaints
    # Target month: ref_date's month; previous month: target month - 1 month
    ref_ym = ref_date[:7]
    try:
        ref_year, ref_month = int(ref_date[:4]), int(ref_date[5:7])
        if ref_month == 1:
            prev_ym = f"{ref_year - 1:04d}-12"
        else:
            prev_ym = f"{ref_year:04d}-{ref_month - 1:02d}"
    except Exception:
        prev_ym = ""

    cur_month_count = sum(1 for c in complaints if c.date and c.date.startswith(ref_ym))
    prev_month_count = sum(1 for c in complaints if c.date and c.date.startswith(prev_ym))

    if prev_month_count > 0:
        diff = cur_month_count - prev_month_count
        pct = round((diff / prev_month_count) * 100)
        total_trend = f"+{pct}%" if pct > 0 else f"{pct}%"
        total_trend_label = "vs last month"
    elif cur_month_count > 0:
        total_trend = None
        total_trend_label = "baseline established"
    else:
        total_trend = None
        total_trend_label = "no activity in period"

    pending_overlaps = _calculate_pending_overlaps(db, current_user)

    kpis = DashboardKPIs(
        total=total,
        pending=pending,
        inProgress=in_progress,
        resolved=resolved,
        escalated=escalated,
        underInvestigation=under_investigation,
        overdue=overdue,
        criticalHigh=critical_high,
        resolutionRate=resolution_rate,
        pendingOverlaps=pending_overlaps,
        totalTrend=total_trend,
        totalTrendLabel=total_trend_label,
        asOfDate=ref_date,
    )

    # Bureau breakdown
    bureau_breakdown: List[BureauBreakdownItem] = []
    for b in STANDARD_BUREAUS:
        b_list = [c for c in complaints if c.bureau.upper() == b.upper()]
        b_resolved = sum(1 for c in b_list if c.status == "Resolved")
        b_in_progress = sum(1 for c in b_list if c.status == "In Progress")
        b_pending = sum(1 for c in b_list if c.status == "Pending")
        b_escalated = sum(1 for c in b_list if c.status == "Escalated")
        bureau_breakdown.append(
            BureauBreakdownItem(
                name=b,
                Resolved=b_resolved,
                InProgress=b_in_progress,
                Pending=b_pending,
                Escalated=b_escalated,
                Total=len(b_list),
            )
        )

    # Priority distribution
    priority_distribution: List[PriorityDistributionItem] = []
    for prio, color in PRIORITY_COLORS.items():
        val = sum(1 for c in complaints if c.priority == prio)
        priority_distribution.append(
            PriorityDistributionItem(name=prio, value=val, color=color)
        )

    # Recent cases (top 5 ordered by date desc, created_at desc)
    recent_records = sorted(
        complaints,
        key=lambda c: (c.date or "", getattr(c, "created_at", None) or datetime.min),
        reverse=True,
    )[:5]
    recent_cases = [map_complaint_to_read(c) for c in recent_records]

    return DashboardAnalyticsResponse(
        kpis=kpis,
        bureauBreakdown=bureau_breakdown,
        priorityDistribution=priority_distribution,
        recentCases=recent_cases,
    )


@router.get("/reports", response_model=ReportsAnalyticsResponse)
def get_reports_analytics(
    bureau: Optional[str] = Query(None, description="Filter by Bureau"),
    startDate: Optional[str] = Query(None, description="Earliest complaint date (YYYY-MM-DD)"),
    endDate: Optional[str] = Query(None, description="Latest complaint date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get real historical analytics, trends, category distributions, and redressal metrics.
    Computes time-series trends strictly from historical database records without fake or simulated points.
    """
    query = _get_scoped_complaints_query(
        db=db,
        current_user=current_user,
        bureau=bureau,
        start_date=startDate,
        end_date=endDate,
    )
    complaints: List[Complaint] = query.all()
    total = len(complaints)
    resolved = sum(1 for c in complaints if c.status == "Resolved")
    resolution_rate = round((resolved / total) * 100) if total > 0 else 0

    # Calculate real average turnaround days for resolved cases
    turnaround_days_list: List[int] = []
    for c in complaints:
        if c.status == "Resolved" and c.date:
            res_date_str = c.last_action_date or c.date
            try:
                d_file = datetime.strptime(c.date[:10], "%Y-%m-%d")
                d_res = datetime.strptime(res_date_str[:10], "%Y-%m-%d")
                days = (d_res - d_file).days
                if days >= 0:
                    turnaround_days_list.append(days)
            except Exception:
                pass

    avg_turnaround = (
        round(sum(turnaround_days_list) / len(turnaround_days_list), 1)
        if turnaround_days_list
        else None
    )

    # Calculate real overlap redundancy actioned rate
    redundancy_rate: Optional[int] = None
    if current_user.role != "Complainant":
        try:
            threshold = _get_active_threshold(db)
            all_overlaps = db.query(ComplaintOverlap).filter(ComplaintOverlap.similarity >= threshold).all()
            if current_user.role == "BureauAdmin" and current_user.bureau != "All":
                user_bureau = current_user.bureau.upper()
                relevant = []
                for ov in all_overlaps:
                    ca = db.query(Complaint).filter(Complaint.id == ov.complaint_a_id).first()
                    cb = db.query(Complaint).filter(Complaint.id == ov.complaint_b_id).first()
                    if (ca and ca.bureau.upper() == user_bureau) or (cb and cb.bureau.upper() == user_bureau):
                        relevant.append(ov)
                all_overlaps = relevant

            if all_overlaps:
                actioned = sum(
                    1
                    for ov in all_overlaps
                    if ov.status in ("linked", "dismissed", "deferred")
                    or ov.decision_state in ("linked", "dismissed", "deferred")
                )
                redundancy_rate = round((actioned / len(all_overlaps)) * 100)
        except Exception:
            pass

    kpis = ReportsKPIs(
        total=total,
        resolved=resolved,
        resolutionRate=resolution_rate,
        avgTurnaroundDays=avg_turnaround,
        turnaroundDaysLabel="Avg. Redressal Turnaround",
        redundancyPreventedRate=redundancy_rate,
        redundancyPreventedLabel="Overlap Redundancy Actioned",
    )

    # 1. Category Distribution
    category_counts: dict[str, int] = {}
    for c in complaints:
        cat = c.category or "Uncategorized"
        category_counts[cat] = category_counts.get(cat, 0) + 1

    category_distribution = [
        CategoryDistributionItem(name=k, value=v)
        for k, v in sorted(category_counts.items(), key=lambda item: item[1], reverse=True)
    ]

    # 2. Status Distribution
    status_distribution = [
        StatusDistributionItem(
            name=s,
            value=sum(1 for c in complaints if c.status == s),
        )
        for s in STATUS_ORDER
    ]

    # 3. Bureau Breakdown
    bureau_breakdown: List[BureauBreakdownItem] = []
    for b in STANDARD_BUREAUS:
        b_list = [c for c in complaints if c.bureau.upper() == b.upper()]
        b_resolved = sum(1 for c in b_list if c.status == "Resolved")
        b_in_progress = sum(1 for c in b_list if c.status == "In Progress")
        b_pending = sum(1 for c in b_list if c.status == "Pending")
        b_escalated = sum(1 for c in b_list if c.status == "Escalated")
        bureau_breakdown.append(
            BureauBreakdownItem(
                name=b,
                Resolved=b_resolved,
                InProgress=b_in_progress,
                Pending=b_pending,
                Escalated=b_escalated,
                Total=len(b_list),
            )
        )

    # 4. Monthly Trends (Real Historical Data Only)
    distinct_months = set()
    for c in complaints:
        if c.date and len(c.date) >= 7:
            distinct_months.add(c.date[:7])
        if c.last_action_date and len(c.last_action_date) >= 7:
            distinct_months.add(c.last_action_date[:7])

    sorted_months = sorted(list(distinct_months))
    monthly_trends: List[MonthlyTrendItem] = []
    for ym in sorted_months:
        try:
            dt = datetime.strptime(ym, "%Y-%m")
            month_label = dt.strftime("%b %Y")
        except Exception:
            month_label = ym

        filed_count = sum(1 for c in complaints if c.date and c.date.startswith(ym))
        resolved_count = sum(
            1
            for c in complaints
            if c.status == "Resolved"
            and (
                (c.last_action_date and c.last_action_date.startswith(ym))
                or (not c.last_action_date and c.date and c.date.startswith(ym))
            )
        )

        monthly_trends.append(
            MonthlyTrendItem(
                month=month_label,
                monthKey=ym,
                Filed=filed_count,
                Resolved=resolved_count,
            )
        )

    data_note = None
    if total == 0:
        data_note = "No complaint records match the specified filters and scope."
    elif len(monthly_trends) <= 1:
        data_note = "Historical time series is based on available records; data spans limited calendar months."

    return ReportsAnalyticsResponse(
        kpis=kpis,
        categoryDistribution=category_distribution,
        statusDistribution=status_distribution,
        bureauBreakdown=bureau_breakdown,
        monthlyTrends=monthly_trends,
        dataNote=data_note,
    )
