import { useEffect, useState } from 'react'
import { ShieldAlert } from 'lucide-react'
import type { AppNotification, Bureau, CaseDocument, Complaint, Page, ReassignmentRequest, Role, Status, UserProfile } from './types'
import {
  canAddCaseRemarks,
  canAssignCase,
  canReviewReassignmentRequest,
  canTransferBureau,
  canUpdateCaseStatus,
  canUploadCaseDocument,
  getOfficersForBureau,
  CURRENT_OFFICER,
  TODAY,
  initialComplaints,
  initialNotifications,
  overlaps,
  userProfiles,
} from './data'
import AppLayout from './components/layout/AppLayout'
import Dashboard from './pages/Dashboard'
import { ComplaintsPage, DetailsPage, SubmitComplaint } from './pages/Complaints'
import Institutions from './pages/Institutions'
import Overlaps from './pages/Overlaps'
import CaseTracking from './pages/CaseTracking'
import Reports from './pages/Reports'
import NotificationsPage from './pages/Notifications'
import UserManagement from './pages/UserManagement'
import Settings from './pages/Settings'
import Login from './pages/Login'
import { Button, Card } from './components/ui'

// Permitted pages matrix per role
const ROLE_PERMITTED_PAGES: Record<Role, Page[]> = {
  Complainant: ['complaints', 'submit', 'details', 'tracking', 'notifications'],
  Officer: ['complaints', 'details', 'institutions', 'overlaps', 'tracking', 'notifications'],
  BureauAdmin: [
    'dashboard',
    'complaints',
    'submit',
    'details',
    'institutions',
    'overlaps',
    'tracking',
    'reports',
    'users',
    'notifications',
  ],
  Admin: [
    'dashboard',
    'complaints',
    'submit',
    'details',
    'institutions',
    'overlaps',
    'tracking',
    'reports',
    'notifications',
    'users',
    'settings',
  ],
}

export const getDefaultLandingPage = (role: Role): Page => {
  return role === 'Complainant' || role === 'Officer' ? 'complaints' : 'dashboard'
}

const STORAGE_KEYS = {
  IS_LOGGED_IN: 'abhigyan_is_logged_in',
  ROLE: 'abhigyan_role',
  PAGE: 'abhigyan_active_page',
  CASE_ID: 'abhigyan_selected_case_id',
  COMPLAINTS: 'abhigyan_complaints',
  NOTIFICATIONS: 'abhigyan_notifications',
} as const

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEYS.IS_LOGGED_IN)
      return stored !== null ? JSON.parse(stored) : true
    } catch {
      return true
    }
  })

  const [currentRole, setCurrentRole] = useState<Role>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEYS.ROLE)
      if (stored && ['Complainant', 'Officer', 'BureauAdmin', 'Admin'].includes(stored)) {
        return stored as Role
      }
    } catch {
      // fallback
    }
    return 'Admin'
  })

  const [activePage, setActivePage] = useState<Page>(() => {
    try {
      const storedRole = localStorage.getItem(STORAGE_KEYS.ROLE) as Role | null
      const role: Role =
        storedRole && ['Complainant', 'Officer', 'BureauAdmin', 'Admin'].includes(storedRole)
          ? (storedRole as Role)
          : 'Admin'
      const storedPage = localStorage.getItem(STORAGE_KEYS.PAGE) as Page | null
      if (storedPage && ROLE_PERMITTED_PAGES[role].includes(storedPage)) {
        if (storedPage === 'details') {
          const storedCaseId = localStorage.getItem(STORAGE_KEYS.CASE_ID)
          if (!storedCaseId) {
            return getDefaultLandingPage(role)
          }
        }
        return storedPage
      }
      return getDefaultLandingPage(role)
    } catch {
      return 'dashboard'
    }
  })

  const [selectedCaseId, setSelectedCaseId] = useState<string | undefined>(() => {
    try {
      return localStorage.getItem(STORAGE_KEYS.CASE_ID) || undefined
    } catch {
      return undefined
    }
  })

  const [complaints, setComplaints] = useState<Complaint[]>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEYS.COMPLAINTS)
      if (stored) {
        const parsed = JSON.parse(stored)
        if (Array.isArray(parsed) && parsed.length > 0) return parsed
      }
    } catch {
      // fallback
    }
    return initialComplaints
  })

  const [notifications, setNotifications] = useState<AppNotification[]>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEYS.NOTIFICATIONS)
      if (stored) {
        const parsed = JSON.parse(stored)
        if (Array.isArray(parsed) && parsed.length > 0) return parsed
      }
    } catch {
      // fallback
    }
    return initialNotifications
  })

  // Synchronize state changes to localStorage
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.IS_LOGGED_IN, JSON.stringify(isLoggedIn))
    } catch {
      // ignore
    }
  }, [isLoggedIn])

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.ROLE, currentRole)
    } catch {
      // ignore
    }
  }, [currentRole])

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.PAGE, activePage)
    } catch {
      // ignore
    }
  }, [activePage])

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.COMPLAINTS, JSON.stringify(complaints))
    } catch {
      // ignore
    }
  }, [complaints])

  useEffect(() => {
    try {
      if (selectedCaseId) {
        localStorage.setItem(STORAGE_KEYS.CASE_ID, selectedCaseId)
      } else {
        localStorage.removeItem(STORAGE_KEYS.CASE_ID)
      }
    } catch {
      // ignore
    }
  }, [selectedCaseId])

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.NOTIFICATIONS, JSON.stringify(notifications))
    } catch {
      // ignore
    }
  }, [notifications])

  // Current active profile based on role
  const currentUser: UserProfile =
    userProfiles.find((u) => u.role === currentRole) || userProfiles[0]

  // Role switching with automatic landing page redirection
  const handleSelectRole = (newRole: Role) => {
    setCurrentRole(newRole)
    const permitted = ROLE_PERMITTED_PAGES[newRole]
    if (!permitted.includes(activePage)) {
      setActivePage(getDefaultLandingPage(newRole))
    }
  }

  const handleLogin = (role: Role) => {
    setCurrentRole(role)
    setIsLoggedIn(true)
    setActivePage(getDefaultLandingPage(role))
  }

  const handleSignOut = () => {
    setIsLoggedIn(false)
    try {
      localStorage.setItem(STORAGE_KEYS.IS_LOGGED_IN, 'false')
    } catch {
      // ignore
    }
  }

  // Handlers
  const handleOpenCase = (id: string) => {
    setSelectedCaseId(id)
    setActivePage('details')
  }

  const handleStatusChange = (id: string, newStatus: Status, noteText?: string) => {
    const target = complaints.find((c) => c.id === id)
    if (!target) return

    const check = canUpdateCaseStatus(currentUser, target, newStatus)
    if (!check.allowed) {
      const blockedNotif: AppNotification = {
        id: `notif-denied-${Date.now()}`,
        type: 'alert',
        title: 'Status Update Denied (FastAPI 403 Simulation)',
        message: check.reason || 'You do not have permission to execute this status transition.',
        timestamp: `${TODAY} 11:30`,
        caseId: id,
        read: false,
      }
      setNotifications((prev) => [blockedNotif, ...prev])
      return
    }

    setComplaints((prev) =>
      prev.map((c) => {
        if (c.id === id) {
          const actionText =
            newStatus === 'Resolved'
              ? 'Case investigation concluded & Marked Resolved'
              : `Status transitioned to ${newStatus}`

          return {
            ...c,
            status: newStatus,
            lastActionDate: TODAY,
            timeline: [
              ...c.timeline,
              {
                label: actionText,
                date: `${TODAY} 11:30`,
                by: `${currentUser.name} (${currentUser.designation})`,
                role: currentRole,
                note: noteText,
              },
            ],
          }
        }
        return c
      })
    )

    // Push notification for status advance
    const notif: AppNotification = {
      id: `notif-${Date.now()}`,
      type: newStatus === 'Resolved' ? 'success' : newStatus === 'Escalated' ? 'alert' : 'info',
      title: `Docket ${id} Updated: ${newStatus}`,
      message: `Status updated to ${newStatus} by ${currentUser.name} (${currentRole}).`,
      timestamp: `${TODAY} 11:30`,
      caseId: id,
      read: false,
    }
    setNotifications((prev) => [notif, ...prev])
  }

  const handleAssignOfficer = (id: string, newOfficer: string, reason?: string) => {
    const target = complaints.find((c) => c.id === id)
    if (!target) return

    const check = canAssignCase(currentUser, target)
    if (!check.allowed) {
      const blockedNotif: AppNotification = {
        id: `notif-denied-${Date.now()}`,
        type: 'alert',
        title: 'Assignment Blocked (FastAPI 403 Simulation)',
        message: check.reason || 'You do not have authorization to reassign this case.',
        timestamp: `${TODAY} 11:30`,
        caseId: id,
        read: false,
      }
      setNotifications((prev) => [blockedNotif, ...prev])
      return
    }

    if (target.officer === newOfficer) return

    const assignmentReason =
      reason?.trim() ||
      `Administrative officer reassignment within ${target.bureau} Bureau.`

    setComplaints((prev) =>
      prev.map((c) => {
        if (c.id === id) {
          const prevOfficer = c.officer
          return {
            ...c,
            officer: newOfficer,
            assignments: [
              ...c.assignments,
              {
                officer: newOfficer,
                previousOfficer: prevOfficer,
                date: TODAY,
                by: `${currentUser.name} (${currentUser.designation})`,
                byRole: currentRole,
                reason: assignmentReason,
                bureau: c.bureau,
                type: 'reassignment',
              },
            ],
            timeline: [
              ...c.timeline,
              {
                label: `Investigating officer reassigned from ${prevOfficer} to ${newOfficer}`,
                date: `${TODAY} 11:30`,
                by: `${currentUser.name} (${currentRole})`,
                role: currentRole,
                note: `Administrative Justification: ${assignmentReason}`,
              },
            ],
          }
        }
        return c
      })
    )

    const notif: AppNotification = {
      id: `notif-${Date.now()}`,
      type: 'info',
      title: `Docket ${id} Reassigned`,
      message: `Docket ${id} assigned to ${newOfficer} by ${currentUser.name}. Reason: ${assignmentReason}`,
      timestamp: `${TODAY} 11:30`,
      caseId: id,
      read: false,
    }
    setNotifications((prev) => [notif, ...prev])
  }

  const handleCrossBureauTransfer = (
    id: string,
    newBureau: Bureau,
    newOfficer: string,
    reason: string
  ) => {
    const target = complaints.find((c) => c.id === id)
    if (!target) return

    const check = canTransferBureau(currentUser, target)
    if (!check.allowed) {
      const blockedNotif: AppNotification = {
        id: `notif-denied-${Date.now()}`,
        type: 'alert',
        title: 'Cross-Bureau Transfer Denied (FastAPI 403 Simulation)',
        message: check.reason || 'You are not authorized to transfer this case.',
        timestamp: `${TODAY} 11:30`,
        caseId: id,
        read: false,
      }
      setNotifications((prev) => [blockedNotif, ...prev])
      return
    }

    const prevBureau = target.bureau
    const prevOfficer = target.officer

    setComplaints((prev) =>
      prev.map((c) => {
        if (c.id === id) {
          return {
            ...c,
            bureau: newBureau,
            officer: newOfficer,
            lastActionDate: TODAY,
            assignments: [
              ...c.assignments,
              {
                officer: newOfficer,
                previousOfficer: prevOfficer,
                date: TODAY,
                by: `${currentUser.name} (${currentUser.designation})`,
                byRole: currentRole,
                reason,
                bureau: newBureau,
                previousBureau: prevBureau,
                type: 'transfer',
              },
            ],
            timeline: [
              ...c.timeline,
              {
                label: `Cross-Bureau Transfer: Jurisdiction transferred from ${prevBureau} to ${newBureau}`,
                date: `${TODAY} 11:30`,
                by: `${currentUser.name} (${currentRole})`,
                role: currentRole,
                note: `Statutory Transfer Reason: ${reason}. Designated officer: ${newOfficer}.`,
              },
            ],
          }
        }
        return c
      })
    )

    const notif: AppNotification = {
      id: `notif-${Date.now()}`,
      type: 'warning',
      title: `Cross-Bureau Transfer: ${id}`,
      message: `Docket ${id} transferred from ${prevBureau} to ${newBureau} by ${currentUser.name}. Reason: ${reason}`,
      timestamp: `${TODAY} 11:30`,
      caseId: id,
      read: false,
    }
    setNotifications((prev) => [notif, ...prev])
  }

  const handleRequestReassignment = (
    id: string,
    request: Omit<ReassignmentRequest, 'id' | 'requestDate' | 'requestedBy' | 'requestedByRole' | 'status'>
  ) => {
    const target = complaints.find((c) => c.id === id)
    if (!target) return

    const newRequest: ReassignmentRequest = {
      id: `req-${Date.now()}`,
      requestedBy: currentUser.name,
      requestedByRole: currentRole,
      requestDate: `${TODAY} 11:30`,
      status: 'Pending',
      ...request,
    }

    setComplaints((prev) =>
      prev.map((c) => {
        if (c.id === id) {
          const reqTypeLabel =
            request.type === 'bureau'
              ? `Formal Cross-Bureau Transfer Request to ${request.proposedBureau} Bureau`
              : `Formal Officer Reassignment Request to ${request.proposedOfficer || 'another officer'}`

          return {
            ...c,
            reassignmentRequests: [...(c.reassignmentRequests || []), newRequest],
            timeline: [
              ...c.timeline,
              {
                label: `${reqTypeLabel} submitted`,
                date: `${TODAY} 11:30`,
                by: `${currentUser.name} (${currentRole})`,
                role: currentRole,
                note: `Reason: ${request.reason}`,
              },
            ],
          }
        }
        return c
      })
    )

    const notif: AppNotification = {
      id: `notif-${Date.now()}`,
      type: 'info',
      title: `Reassignment Request Submitted: ${id}`,
      message: `${currentUser.name} requested ${
        request.type === 'bureau' ? `cross-bureau transfer to ${request.proposedBureau}` : 'officer reassignment'
      } for docket ${id}.`,
      timestamp: `${TODAY} 11:30`,
      caseId: id,
      read: false,
    }
    setNotifications((prev) => [notif, ...prev])
  }

  const handleReviewReassignmentRequest = (
    id: string,
    requestId: string,
    decision: 'Approved' | 'Rejected',
    reviewNote?: string
  ) => {
    const target = complaints.find((c) => c.id === id)
    if (!target) return

    const check = canReviewReassignmentRequest(currentUser, target)
    if (!check.allowed) {
      const blockedNotif: AppNotification = {
        id: `notif-denied-${Date.now()}`,
        type: 'alert',
        title: 'Review Action Blocked (FastAPI 403 Simulation)',
        message: check.reason || 'You do not have administrative authority to review this request.',
        timestamp: `${TODAY} 11:30`,
        caseId: id,
        read: false,
      }
      setNotifications((prev) => [blockedNotif, ...prev])
      return
    }

    const req = target.reassignmentRequests?.find((r) => r.id === requestId)
    if (!req) return

    setComplaints((prev) =>
      prev.map((c) => {
        if (c.id === id) {
          const updatedRequests = (c.reassignmentRequests || []).map((r) =>
            r.id === requestId
              ? {
                  ...r,
                  status: decision,
                  reviewedBy: currentUser.name,
                  reviewedByRole: currentRole,
                  reviewDate: `${TODAY} 11:30`,
                  reviewNote:
                    reviewNote ||
                    (decision === 'Approved'
                      ? 'Approved upon statutory review'
                      : 'Rejected after administrative review'),
                }
              : r
          )

          let updatedBureau = c.bureau
          let updatedOfficer = c.officer
          const updatedAssignments = [...c.assignments]
          const newTimelineEvents = [...c.timeline]

          if (decision === 'Approved') {
            if (req.type === 'bureau' && req.proposedBureau) {
              const prevBureau = c.bureau
              const prevOfficer = c.officer
              updatedBureau = req.proposedBureau
              updatedOfficer = req.proposedOfficer || getOfficersForBureau(req.proposedBureau)[0]

              updatedAssignments.push({
                officer: updatedOfficer,
                previousOfficer: prevOfficer,
                date: TODAY,
                by: `${currentUser.name} (${currentUser.designation})`,
                byRole: currentRole,
                reason: `Approved transfer request from ${req.requestedBy}: ${req.reason}`,
                bureau: updatedBureau,
                previousBureau: prevBureau,
                type: 'transfer',
              })

              newTimelineEvents.push({
                label: `Cross-Bureau Transfer Approved: Transferred from ${prevBureau} to ${updatedBureau}`,
                date: `${TODAY} 11:30`,
                by: `${currentUser.name} (${currentRole})`,
                role: currentRole,
                note: `Approved Request #${req.id}. Designated officer: ${updatedOfficer}. Note: ${
                  reviewNote || 'Approved.'
                }`,
              })
            } else if (req.type === 'officer' && req.proposedOfficer) {
              const prevOfficer = c.officer
              updatedOfficer = req.proposedOfficer

              updatedAssignments.push({
                officer: updatedOfficer,
                previousOfficer: prevOfficer,
                date: TODAY,
                by: `${currentUser.name} (${currentUser.designation})`,
                byRole: currentRole,
                reason: `Approved reassignment request from ${req.requestedBy}: ${req.reason}`,
                bureau: c.bureau,
                type: 'reassignment',
              })

              newTimelineEvents.push({
                label: `Officer Reassignment Approved: Reassigned from ${prevOfficer} to ${updatedOfficer}`,
                date: `${TODAY} 11:30`,
                by: `${currentUser.name} (${currentRole})`,
                role: currentRole,
                note: `Approved Request #${req.id}. Note: ${reviewNote || 'Approved.'}`,
              })
            }
          } else {
            newTimelineEvents.push({
              label: `Reassignment / Transfer Request Rejected by ${currentUser.name}`,
              date: `${TODAY} 11:30`,
              by: `${currentUser.name} (${currentRole})`,
              role: currentRole,
              note: `Reason for Rejection: ${
                reviewNote || 'Request not aligned with statutory jurisdiction.'
              }`,
            })
          }

          return {
            ...c,
            bureau: updatedBureau,
            officer: updatedOfficer,
            assignments: updatedAssignments,
            reassignmentRequests: updatedRequests,
            timeline: newTimelineEvents,
          }
        }
        return c
      })
    )

    const notif: AppNotification = {
      id: `notif-${Date.now()}`,
      type: decision === 'Approved' ? 'success' : 'warning',
      title: `Reassignment Request ${decision}: ${id}`,
      message: `Request for docket ${id} was ${decision.toLowerCase()} by ${currentUser.name}.`,
      timestamp: `${TODAY} 11:30`,
      caseId: id,
      read: false,
    }
    setNotifications((prev) => [notif, ...prev])
  }

  const handleAddTimelineNote = (id: string, noteText: string) => {
    const target = complaints.find((c) => c.id === id)
    if (!target) return

    const check = canAddCaseRemarks(currentUser, target)
    if (!check.allowed) {
      const blockedNotif: AppNotification = {
        id: `notif-denied-${Date.now()}`,
        type: 'alert',
        title: 'Action Remark Denied (FastAPI 403 Simulation)',
        message: check.reason || 'You do not have permission to post remarks on this docket.',
        timestamp: `${TODAY} 11:30`,
        caseId: id,
        read: false,
      }
      setNotifications((prev) => [blockedNotif, ...prev])
      return
    }

    setComplaints((prev) =>
      prev.map((c) => {
        if (c.id === id) {
          const noteLabel =
            currentRole === 'Complainant'
              ? 'Supplementary Statement / Complainant Update Logged'
              : 'Investigation Action & Inquiry Milestone Logged'

          return {
            ...c,
            lastActionDate: TODAY,
            timeline: [
              ...c.timeline,
              {
                label: noteLabel,
                date: `${TODAY} 11:30`,
                by: `${currentUser.name} (${currentUser.designation})`,
                role: currentRole,
                note: noteText,
              },
            ],
          }
        }
        return c
      })
    )
  }

  const handleAddDocument = (id: string, newDoc: CaseDocument) => {
    const target = complaints.find((c) => c.id === id)
    if (!target) return

    const check = canUploadCaseDocument(currentUser, target)
    if (!check.allowed) {
      const blockedNotif: AppNotification = {
        id: `notif-denied-${Date.now()}`,
        type: 'alert',
        title: 'Document Upload Denied (FastAPI 403 Simulation)',
        message: check.reason || 'You do not have authorization to upload documents to this docket.',
        timestamp: `${TODAY} 11:30`,
        caseId: id,
        read: false,
      }
      setNotifications((prev) => [blockedNotif, ...prev])
      return
    }

    setComplaints((prev) =>
      prev.map((c) => {
        if (c.id === id) {
          const existing = c.documents || []
          return {
            ...c,
            documents: [...existing, newDoc],
            attachmentsCount: existing.length + 1,
            timeline: [
              ...c.timeline,
              {
                label: `Supporting record attached: ${newDoc.name}`,
                date: `${TODAY} 11:30`,
                by: `${currentUser.name} (${currentRole})`,
                role: currentRole,
                note: `Document (${newDoc.size}) uploaded with ${newDoc.visibility} visibility.`,
              },
            ],
          }
        }
        return c
      })
    )

    const notif: AppNotification = {
      id: `notif-${Date.now()}`,
      type: 'info',
      title: `Document Uploaded: ${newDoc.name}`,
      message: `A new verification record has been attached to docket ${id}.`,
      timestamp: `${TODAY} 11:30`,
      caseId: id,
      read: false,
    }
    setNotifications((prev) => [notif, ...prev])
  }

  const handleAddComplaint = (newComplaint: Complaint) => {
    setComplaints((prev) => [newComplaint, ...prev])

    // Push system notification
    const newNotif: AppNotification = {
      id: `notif-${Date.now()}`,
      type: 'info',
      title: `New Case Registered: ${newComplaint.id}`,
      message: `A new complaint has been filed against ${newComplaint.institutionPermanentId || newComplaint.institutionId} under ${newComplaint.bureau} bureau.`,
      timestamp: `${TODAY} 11:00`,
      caseId: newComplaint.id,
      read: false,
    }
    setNotifications((prev) => [newNotif, ...prev])
  }

  const handleMarkNotificationRead = (id: string) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n))
    )
  }

  const handleMarkAllNotificationsRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })))
  }

  // If user is logged out, show the Login screen
  if (!isLoggedIn) {
    return <Login onLogin={handleLogin} initialRole={currentRole} />
  }

  const selectedComplaint = complaints.find((c) => c.id === selectedCaseId)
  const pendingOverlapsCount = overlaps.filter((o) => o.similarity >= 80).length
  const isPagePermitted = ROLE_PERMITTED_PAGES[currentRole].includes(activePage)

  return (
    <AppLayout
      activePage={activePage}
      onNavigate={setActivePage}
      notifications={notifications}
      onMarkNotificationAsRead={handleMarkNotificationRead}
      onMarkAllNotificationsRead={handleMarkAllNotificationsRead}
      currentUser={currentUser}
      currentRole={currentRole}
      onSelectRole={handleSelectRole}
      onSignOut={handleSignOut}
      pendingOverlapsCount={pendingOverlapsCount}
      onSelectCase={handleOpenCase}
    >
      {/* Route Protection: Unauthorized Access Fallback */}
      {!isPagePermitted ? (
        <Card className="border-l-4 border-l-rose-600 p-8 text-center max-w-xl mx-auto my-12">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-rose-100 text-rose-700">
            <ShieldAlert size={28} />
          </div>
          <h3 className="mt-4 text-base font-bold text-slate-900">
            Access Restricted by Demo Role Permissions
          </h3>
          <p className="mt-2 text-xs text-slate-600 leading-relaxed">
            Your current demo role (<strong>{currentRole}</strong>) does not have access permissions for the &quot;{activePage}&quot; module. In production, this policy will be strictly verified and enforced by the FastAPI backend.
          </p>
          <div className="mt-5 flex justify-center gap-2">
            <Button
              variant="primary"
              size="sm"
              onClick={() => setActivePage(getDefaultLandingPage(currentRole))}
            >
              Return to Permitted View
            </Button>
          </div>
        </Card>
      ) : (
        <>
          {/* Dynamic Page Router */}
          {activePage === 'dashboard' && (
            <Dashboard
              complaints={complaints}
              onOpen={handleOpenCase}
              onStatus={handleStatusChange}
              onNavigate={setActivePage}
              currentRole={currentRole}
              currentUser={currentUser}
            />
          )}

          {activePage === 'complaints' && (
            <ComplaintsPage
              complaints={complaints}
              onOpen={handleOpenCase}
              onStatus={handleStatusChange}
              onAddComplaint={handleAddComplaint}
              onNavigateToSubmit={() => setActivePage('submit')}
              currentRole={currentRole}
              currentUser={currentUser}
            />
          )}

          {activePage === 'submit' && (
            <SubmitComplaint
              complaints={complaints}
              onSubmit={handleAddComplaint}
              onCancel={() => setActivePage(getDefaultLandingPage(currentRole))}
              onTrackCase={handleOpenCase}
              currentRole={currentRole}
              currentUser={currentUser}
            />
          )}

          {activePage === 'details' && (
            <DetailsPage
              complaint={selectedComplaint}
              onBack={() => setActivePage('complaints')}
              onStatus={handleStatusChange}
              onAssign={handleAssignOfficer}
              onTransferBureau={handleCrossBureauTransfer}
              onRequestReassignment={handleRequestReassignment}
              onReviewReassignmentRequest={handleReviewReassignmentRequest}
              onAddNote={handleAddTimelineNote}
              onAddDocument={handleAddDocument}
              onNavigateToInstitution={(instId) => {
                setActivePage('institutions')
              }}
              currentRole={currentRole}
              currentUser={currentUser}
            />
          )}

          {activePage === 'institutions' && (
            <Institutions complaints={complaints} onOpen={handleOpenCase} />
          )}

          {activePage === 'overlaps' && (
            <Overlaps
              complaints={complaints}
              onOpen={handleOpenCase}
              currentRole={currentRole}
              currentUser={currentUser}
            />
          )}

          {activePage === 'tracking' && (
            <CaseTracking
              complaints={complaints}
              onOpen={handleOpenCase}
              onStatus={handleStatusChange}
              onAddNote={handleAddTimelineNote}
              currentRole={currentRole}
              currentUser={currentUser}
            />
          )}

          {activePage === 'reports' && <Reports complaints={complaints} />}

          {activePage === 'notifications' && (
            <NotificationsPage
              notifications={notifications}
              onMarkAsRead={handleMarkNotificationRead}
              onMarkAllAsRead={handleMarkAllNotificationsRead}
              onOpenCase={handleOpenCase}
            />
          )}

          {activePage === 'users' && <UserManagement />}

          {activePage === 'settings' && <Settings />}
        </>
      )}
    </AppLayout>
  )
}
