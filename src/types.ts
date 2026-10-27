export type Status = 'Pending' | 'In Progress' | 'Resolved' | 'Escalated'
export type Priority = 'Critical' | 'High' | 'Medium' | 'Low'
export type Bureau = 'RB' | 'PGRC' | 'Approval' | 'Academic' | 'SB' | 'EO'
export type Role = 'Complainant' | 'BureauAdmin' | 'Officer' | 'Admin'

export type Page =
  | 'dashboard'
  | 'complaints'
  | 'submit'
  | 'details'
  | 'institutions'
  | 'overlaps'
  | 'tracking'
  | 'reports'
  | 'notifications'
  | 'users'
  | 'settings'

export interface CaseDocument {
  id: string
  name: string
  size: string
  uploadDate: string
  uploadedBy: string
  uploaderRole: Role
  visibility: 'Public' | 'Internal'
  fileType?: string
  dataUrl?: string
}

export interface TimelineEvent {
  label: string
  date: string
  by?: string
  role?: Role
  note?: string
}

export interface Assignment {
  officer: string
  date: string
  by: string
  byRole?: Role
  previousOfficer?: string
  reason?: string
  bureau?: Bureau
  previousBureau?: Bureau
  type?: 'initial' | 'reassignment' | 'transfer'
}

export interface ReassignmentRequest {
  id: string
  requestedBy: string
  requestedByRole: Role
  requestDate: string
  type: 'officer' | 'bureau'
  currentOfficer: string
  proposedOfficer?: string
  currentBureau: Bureau
  proposedBureau?: Bureau
  reason: string
  status: 'Pending' | 'Approved' | 'Rejected'
  reviewedBy?: string
  reviewedByRole?: Role
  reviewDate?: string
  reviewNote?: string
}

export interface Complaint {
  id: string
  institutionId: string
  institutionPermanentId?: string
  bureau: Bureau
  category: string
  priority: Priority
  officer: string
  assignedUserId?: string
  status: Status
  date: string
  due: string
  title: string
  description: string
  timeline: TimelineEvent[]
  assignments: Assignment[]
  reassignmentRequests?: ReassignmentRequest[]
  complainantType?: 'Student' | 'Faculty' | 'Parent' | 'Whistleblower' | 'General Public'
  complainantName?: string
  complainantEmail?: string
  complainantPhone?: string
  attachmentsCount?: number
  documents?: CaseDocument[]
  remarks?: string
  nextAction?: string
  lastActionDate?: string

  // AI Classification Advisory Metadata
  aiPredictedCategory?: string
  aiPredictedBureau?: Bureau
  aiPredictedPriority?: Priority
  aiConfidence?: number
  aiNeedsManualReview?: boolean
  aiModelVersion?: string
  aiClassificationRun?: boolean
}

export interface AIClassificationResult {
  category: string | null
  bureau: Bureau | null
  priority: Priority | null
  confidence: number | null
  priorityConfidence?: number | null
  needsManualReview: boolean
  modelVersion: string | null
  advisoryNotice: string
  status: 'success' | 'unavailable' | 'invalid_input' | 'error'
  reviewReasons: string[]
}

export interface AIClassifyPayload {
  title: string
  description: string
  confidenceThreshold?: number
}

export interface Institution {
  id: string
  name: string
  city: string
  state: string
  type: string
  aicteId: string
  approved: string
  contactEmail?: string
  contactPhone?: string
  totalComplaints?: number
  activeComplaints?: number
  riskLevel?: 'Low' | 'Moderate' | 'High'
}

export interface Overlap {
  id: string
  a: string
  b: string
  similarity: number
  reasons: string[]
  status?: 'pending' | 'linked' | 'dismissed' | 'deferred' | 'open'
  notes?: string
  reviewedBy?: string
  reviewedDate?: string
  decisionNote?: string
  justification?: string
}

export interface LinkedDocket {
  overlapId: string
  caseId: string
  bureau: Bureau
  title: string
  similarity: number
  justification?: string
  confirmedBy?: string
  confirmedAt?: string
}

export interface AppNotification {
  id: string
  type: 'alert' | 'warning' | 'info' | 'success'
  title: string
  message: string
  timestamp: string
  caseId?: string
  read: boolean
  targetRole?: Role | 'All'
  recipientUserId?: string
  recipientEmail?: string
  bureau?: Bureau | 'All'
}

export interface UserProfile {
  id: string
  name: string
  email: string
  role: Role
  designation: string
  bureau: Bureau | 'All'
  avatarText: string
  phone: string
  activeCasesCount: number
  status: 'Active' | 'On Leave' | 'Inactive'
  department?: string
}

export interface AppSettings {
  similarityThreshold: number
  slaCritical: number
  slaHigh: number
  slaMedium: number
  autoEscalate: boolean
  emailAlerts: boolean
  updatedAt?: string
  updatedBy?: string
}
