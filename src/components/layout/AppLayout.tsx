import { useState, type ReactNode } from 'react'
import Sidebar from './Sidebar'
import TopBar from './TopBar'
import type { AppNotification, Page, Role, UserProfile } from '../../types'

interface AppLayoutProps {
  children: ReactNode
  activePage: Page
  onNavigate: (page: Page) => void
  notifications: AppNotification[]
  onMarkNotificationAsRead: (id: string) => void
  onMarkAllNotificationsRead: () => void
  currentUser: UserProfile
  currentRole: Role
  onSelectRole: (role: Role) => void
  onSignOut?: () => void
  pendingOverlapsCount: number
  onSelectCase?: (caseId: string) => void
}

export default function AppLayout({
  children,
  activePage,
  onNavigate,
  notifications,
  onMarkNotificationAsRead,
  onMarkAllNotificationsRead,
  currentUser,
  currentRole,
  onSelectRole,
  onSignOut,
  pendingOverlapsCount,
  onSelectCase,
}: AppLayoutProps) {
  const [collapsed, setCollapsed] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const unreadCount = notifications.filter((n) => !n.read).length

  const handleNavigate = (page: Page) => {
    onNavigate(page)
    setMobileMenuOpen(false)
  }

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-50 font-sans antialiased text-slate-800">
      {/* Desktop Sidebar */}
      <div className="hidden lg:flex lg:flex-shrink-0">
        <Sidebar
          activePage={activePage}
          onNavigate={handleNavigate}
          collapsed={collapsed}
          onToggleCollapse={() => setCollapsed(!collapsed)}
          unreadNotificationsCount={unreadCount}
          pendingOverlapsCount={pendingOverlapsCount}
          currentRole={currentRole}
          onSelectRole={onSelectRole}
          onSignOut={onSignOut}
          currentUser={currentUser}
        />
      </div>

      {/* Mobile Drawer Backdrop */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/60 backdrop-blur-xs lg:hidden transition-opacity"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Mobile Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-50 flex w-72 transform transition-transform duration-300 ease-in-out lg:hidden ${
          mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <Sidebar
          activePage={activePage}
          onNavigate={handleNavigate}
          collapsed={false}
          onToggleCollapse={() => setMobileMenuOpen(false)}
          unreadNotificationsCount={unreadCount}
          pendingOverlapsCount={pendingOverlapsCount}
          currentRole={currentRole}
          onSelectRole={onSelectRole}
          onSignOut={onSignOut}
          currentUser={currentUser}
        />
      </div>

      {/* Main Content Viewport */}
      <div className="flex flex-1 flex-col min-w-0 overflow-hidden">
        <TopBar
          activePage={activePage}
          onNavigate={handleNavigate}
          onToggleMobileMenu={() => setMobileMenuOpen(true)}
          notifications={notifications}
          onMarkNotificationAsRead={onMarkNotificationAsRead}
          onMarkAllNotificationsRead={onMarkAllNotificationsRead}
          currentUser={currentUser}
          currentRole={currentRole}
          onSelectRole={onSelectRole}
          onSignOut={onSignOut}
          onSelectCase={onSelectCase}
        />

        {/* Scrollable Page Body */}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 scrollbar-thin">
          <div className="mx-auto max-w-7xl">{children}</div>
        </main>
      </div>
    </div>
  )
}
