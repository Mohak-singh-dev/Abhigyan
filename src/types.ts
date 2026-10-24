export type Status = 'Pending' | 'In Progress' | 'Resolved' | 'Escalated'
export type Priority = 'Critical' | 'High' | 'Medium' | 'Low'
export type Bureau = 'RB' | 'PGRC' | 'Approval' | 'Academic' | 'SB' | 'EO'
export type Role = 'Admin' | 'Officer'

export type Page =
  | 'dashboard'
  | 'complaints'
  | 'details'
  | 'institutions'
  | 'overlaps'
  | 'tracking'
  | 'reports'
  | 'notifications'
  | 'users'
  | 'settings'

export interface TimelineEvent {
  label: string
  date: string
  by?: string
  note?: string
}

export interface Assignment {
  officer: string
  date: string
  by: string
}

export interface Complaint {
  id: string
  institutionId: string
  bureau: Bureau
  category: string
  priority: Priority
  officer: string
  status: Status
  date: string
  due: string
  title: string
  description: string
  timeline: TimelineEvent[]
  assignments: Assignment[]
  complainantType?: 'Student' | 'Faculty' | 'Parent' | 'Whistleblower' | 'General Public'
  attachmentsCount?: number
  remarks?: string
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
  status?: 'pending' | 'linked' | 'dismissed'
  notes?: string
}

export interface AppNotification {
  id: string
  type: 'alert' | 'warning' | 'info' | 'success'
  title: string
  message: string
  timestamp: string
  caseId?: string
  read: boolean
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
}
