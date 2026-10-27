from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.complaint import ComplaintRead

class DashboardKPIs(BaseModel):
    total: int = Field(..., description="Total complaints in scope")
    pending: int = Field(..., description="Pending complaints")
    inProgress: int = Field(..., description="In Progress complaints")
    resolved: int = Field(..., description="Resolved complaints")
    escalated: int = Field(..., description="Escalated complaints")
    underInvestigation: int = Field(..., description="Pending + In Progress complaints")
    overdue: int = Field(..., description="Overdue complaints past SLA due date and not resolved")
    criticalHigh: int = Field(..., description="Critical and High priority complaints")
    resolutionRate: int = Field(..., description="Percentage of resolved complaints (0-100)")
    pendingOverlaps: int = Field(..., description="Pending cross-bureau overlap candidates")
    totalTrend: Optional[str] = Field(None, description="Month-over-month trend percentage string or None if insufficient history")
    totalTrendLabel: str = Field("vs last month", description="Explanation label for totalTrend")
    asOfDate: str = Field(..., description="Reference date used for SLA overdue evaluation (YYYY-MM-DD)")

class BureauBreakdownItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    Resolved: int
    InProgress: int = Field(..., alias="In Progress", serialization_alias="In Progress")
    Pending: int
    Escalated: int
    Total: int

class PriorityDistributionItem(BaseModel):
    name: str
    value: int
    color: str

class DashboardAnalyticsResponse(BaseModel):
    kpis: DashboardKPIs
    bureauBreakdown: List[BureauBreakdownItem]
    priorityDistribution: List[PriorityDistributionItem]
    recentCases: List[ComplaintRead]

class MonthlyTrendItem(BaseModel):
    month: str  # e.g. "Aug 2026", "Sep 2026", "Oct 2026"
    monthKey: str  # "2026-08"
    Filed: int
    Resolved: int

class CategoryDistributionItem(BaseModel):
    name: str
    value: int

class StatusDistributionItem(BaseModel):
    name: str
    value: int

class ReportsKPIs(BaseModel):
    total: int
    resolved: int
    resolutionRate: int
    avgTurnaroundDays: Optional[float] = Field(None, description="Average redressal turnaround in days, or None if no resolved cases")
    turnaroundDaysLabel: str = Field("Avg. Redressal Turnaround", description="Label explaining turnaround")
    redundancyPreventedRate: Optional[int] = Field(None, description="Percentage of overlaps resolved/linked, or None if no overlap data")
    redundancyPreventedLabel: str = Field("Overlap Redundancy Actioned", description="Label explaining redundancy")

class ReportsAnalyticsResponse(BaseModel):
    kpis: ReportsKPIs
    categoryDistribution: List[CategoryDistributionItem]
    statusDistribution: List[StatusDistributionItem]
    bureauBreakdown: List[BureauBreakdownItem]
    monthlyTrends: List[MonthlyTrendItem]
    dataNote: Optional[str] = Field(None, description="Notice if historical range is limited or empty")
