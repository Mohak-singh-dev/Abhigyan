import { useState } from 'react'
import type { AppNotification, Complaint, Page, Role, Status, UserProfile } from './types'
import {
  CURRENT_OFFICER,
  TODAY,
  initialComplaints,
  initialNotifications,
  overlaps,
  userProfiles,
} from './data'
import AppLayout from './components/layout/AppLayout'
import Dashboard from './pages/Dashboard'
import { ComplaintsPage, DetailsPage } from './pages/Complaints'
import Institutions from './pages/Institutions'
import Overlaps from './pages/Overlaps'
import CaseTracking from './pages/CaseTracking'
import Reports from './pages/Reports'
import NotificationsPage from './pages/Notifications'
import UserManagement from './pages/UserManagement'
import Settings from './pages/Settings'

export default function App() {
  const [currentRole, setCurrentRole] = useState<Role>('Admin')
  const [activePage, setActivePage] = useState<Page>('dashboard')
  const [selectedCaseId, setSelectedCaseId] = useState<string | undefined>()
  const [complaints, setComplaints] = useState<Complaint[]>(initialComplaints)
  const [notifications, setNotifications] = useState<AppNotification[]>(initialNotifications)

  // Current active profile
  const adminUser = userProfiles.find((u) => u.role === 'Admin') || userProfiles[0]
  const officerUser = userProfiles.find((u) => u.name === CURRENT_OFFICER) || userProfiles[1]
  const currentUser: UserProfile = currentRole === 'Admin' ? adminUser : officerUser

  // Handlers
  const handleOpenCase = (id: string) => {
    setSelectedCaseId(id)
    setActivePage('details')
  }

  const handleStatusChange = (id: string, newStatus: Status) => {
    setComplaints((prev) =>
      prev.map((c) => {
        if (c.id === id && c.status !== newStatus) {
          const actionText =
            newStatus === 'Resolved'
              ? 'Case investigation completed & Marked Resolved'
              : `Status updated to ${newStatus}`

          return {
            ...c,
            status: newStatus,
            timeline: [
              ...c.timeline,
              {
                label: actionText,
                date: TODAY,
                by: `${currentUser.name} (${currentUser.designation})`,
              },
            ],
          }
        }
        return c
      })
    )
  }

  const handleAssignOfficer = (id: string, newOfficer: string) => {
    setComplaints((prev) =>
      prev.map((c) => {
        if (c.id === id && c.officer !== newOfficer) {
          return {
            ...c,
            officer: newOfficer,
            assignments: [
              ...c.assignments,
              {
                officer: newOfficer,
                date: TODAY,
                by: `${currentUser.name} (${currentRole})`,
              },
            ],
            timeline: [
              ...c.timeline,
              {
                label: `Reassigned investigating officer to ${newOfficer}`,
                date: TODAY,
                by: currentUser.name,
              },
            ],
          }
        }
        return c
      })
    )
  }

  const handleAddTimelineNote = (id: string, noteText: string) => {
    setComplaints((prev) =>
      prev.map((c) => {
        if (c.id === id) {
          return {
            ...c,
            timeline: [
              ...c.timeline,
              {
                label: 'Investigation Action & Hearing Note Logged',
                date: TODAY,
                by: currentUser.name,
                note: noteText,
              },
            ],
          }
        }
        return c
      })
    )
  }

  const handleAddComplaint = (newComplaint: Complaint) => {
    setComplaints((prev) => [newComplaint, ...prev])
    // Also push a system notification
    const newNotif: AppNotification = {
      id: `notif-${Date.now()}`,
      type: 'info',
      title: `New Case Registered: ${newComplaint.id}`,
      message: `A new complaint has been filed against ${newComplaint.institutionId} under ${newComplaint.bureau} bureau.`,
      timestamp: `${TODAY} 10:00`,
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

  const handleToggleRole = () => {
    setCurrentRole((prev) => (prev === 'Admin' ? 'Officer' : 'Admin'))
  }

  const selectedComplaint = complaints.find((c) => c.id === selectedCaseId)
  const pendingOverlapsCount = overlaps.filter((o) => o.similarity >= 80).length

  return (
    <AppLayout
      activePage={activePage}
      onNavigate={setActivePage}
      notifications={notifications}
      onMarkNotificationAsRead={handleMarkNotificationRead}
      onMarkAllNotificationsRead={handleMarkAllNotificationsRead}
      currentUser={currentUser}
      currentRole={currentRole}
      onToggleRole={handleToggleRole}
      pendingOverlapsCount={pendingOverlapsCount}
      onSelectCase={handleOpenCase}
    >
      {/* Dynamic Page Router */}
      {activePage === 'dashboard' && (
        <Dashboard
          complaints={complaints}
          onOpen={handleOpenCase}
          onStatus={handleStatusChange}
          onNavigate={setActivePage}
          currentRole={currentRole}
        />
      )}

      {activePage === 'complaints' && (
        <ComplaintsPage
          complaints={complaints}
          onOpen={handleOpenCase}
          onStatus={handleStatusChange}
          onAddComplaint={handleAddComplaint}
        />
      )}

      {activePage === 'details' && (
        <DetailsPage
          complaint={selectedComplaint}
          onBack={() => setActivePage('complaints')}
          onStatus={handleStatusChange}
          onAssign={handleAssignOfficer}
          onAddNote={handleAddTimelineNote}
          onNavigateToInstitution={(instId) => {
            setActivePage('institutions')
          }}
        />
      )}

      {activePage === 'institutions' && (
        <Institutions complaints={complaints} onOpen={handleOpenCase} />
      )}

      {activePage === 'overlaps' && (
        <Overlaps complaints={complaints} onOpen={handleOpenCase} />
      )}

      {activePage === 'tracking' && (
        <CaseTracking
          complaints={complaints}
          onOpen={handleOpenCase}
          onStatus={handleStatusChange}
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
    </AppLayout>
  )
}
