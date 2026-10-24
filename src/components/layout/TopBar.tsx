import { useState } from 'react'
import {
  Bell,
  CheckCircle2,
  ChevronDown,
  HelpCircle,
  LogOut,
  Menu,
  Search,
  Settings,
  Shield,
  User,
  X,
  AlertTriangle,
  Info,
  Clock,
} from 'lucide-react'
import type { AppNotification, Page, Role, UserProfile } from '../../types'
import { Badge } from '../ui'

interface TopBarProps {
  activePage: Page
  onNavigate: (page: Page) => void
  onToggleMobileMenu: () => void
  notifications: AppNotification[]
  onMarkNotificationAsRead: (id: string) => void
  onMarkAllNotificationsRead: () => void
  currentUser: UserProfile
  currentRole: Role
  onToggleRole: () => void
  onSelectCase?: (caseId: string) => void
}

const PAGE_META: Record<Page, { title: string; subtitle: string }> = {
  dashboard: {
    title: 'Executive Dashboard',
    subtitle: 'Consolidated AICTE complaint monitoring, SLA surveillance & bureau distribution',
  },
  complaints: {
    title: 'All Complaints Directory',
    subtitle: 'Search, filter, track and update cases across AICTE bureaus (RB, PGRC, Approval)',
  },
  details: {
    title: 'Case File Details',
    subtitle: 'Comprehensive audit trail, institution profile, evidence and timeline',
  },
  institutions: {
    title: 'Institutions Roster & Risk Profiles',
    subtitle: 'Accredited technical institutes, colleges and their historic complaint density',
  },
  overlaps: {
    title: 'Cross-Bureau Overlap Detection',
    subtitle: 'Algorithmic duplication check flagging parallel complaints filed with RB & PGRC',
  },
  tracking: {
    title: 'Live Case Tracking & SLA Tracker',
    subtitle: 'Timeline lifecycle progression, milestone checks, and statutory resolution compliance',
  },
  reports: {
    title: 'Reports, Trends & Data Analytics',
    subtitle: 'Visual analytics, bureau resolution metrics and statutory compliance reporting',
  },
  notifications: {
    title: 'System Notifications & Alerts',
    subtitle: 'Urgent SLA breaches, high-confidence overlaps, and bureau escalations',
  },
  users: {
    title: 'AICTE Personnel & Bureau Officers',
    subtitle: 'Officer registry, active assignments, bureau allocation and workload capacity',
  },
  settings: {
    title: 'System & Bureau Settings',
    subtitle: 'Configure SLA thresholds, overlap similarity tolerance, and AICTE compliance rules',
  },
}

export default function TopBar({
  activePage,
  onNavigate,
  onToggleMobileMenu,
  notifications,
  onMarkNotificationAsRead,
  onMarkAllNotificationsRead,
  currentUser,
  currentRole,
  onToggleRole,
  onSelectCase,
}: TopBarProps) {
  const [showNotifMenu, setShowNotifMenu] = useState(false)
  const [showProfileMenu, setShowProfileMenu] = useState(false)
  const [quickSearch, setQuickSearch] = useState('')

  const unreadNotifs = notifications.filter((n) => !n.read)
  const pageMeta = PAGE_META[activePage] || PAGE_META.dashboard

  const handleCaseClick = (caseId?: string) => {
    if (caseId && onSelectCase) {
      onSelectCase(caseId)
      setShowNotifMenu(false)
    }
  }

  const getNotifIcon = (type: AppNotification['type']) => {
    switch (type) {
      case 'alert':
        return <AlertTriangle size={15} className="text-rose-600" />
      case 'warning':
        return <Clock size={15} className="text-amber-600" />
      case 'success':
        return <CheckCircle2 size={15} className="text-emerald-600" />
      default:
        return <Info size={15} className="text-sky-600" />
    }
  }

  return (
    <header className="sticky top-0 z-20 flex h-[72px] items-center justify-between border-b border-slate-200/80 bg-white px-4 sm:px-6 shadow-xs">
      {/* Left: Mobile trigger & Page Title */}
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleMobileMenu}
          className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 lg:hidden"
          aria-label="Open mobile menu"
        >
          <Menu size={20} />
        </button>

        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-bold text-slate-900 tracking-tight leading-tight">
              {pageMeta.title}
            </h1>
            <span className="hidden sm:inline-block rounded-md bg-navy-50 text-navy-800 border border-navy-100 text-[10px] font-bold px-2 py-0.5 uppercase">
              Gov of India
            </span>
          </div>
          <p className="text-xs text-slate-500 hidden md:block mt-0.5 truncate max-w-xl">
            {pageMeta.subtitle}
          </p>
        </div>
      </div>

      {/* Right: Quick Search, Notifications, User Profile */}
      <div className="flex items-center gap-3">
        {/* Quick Search */}
        <div className="relative hidden lg:block w-64">
          <Search size={15} className="absolute left-3 top-2.5 text-slate-400" />
          <input
            type="text"
            value={quickSearch}
            onChange={(e) => setQuickSearch(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && quickSearch.trim()) {
                onNavigate('complaints')
              }
            }}
            placeholder="Quick search cases, institutes..."
            className="w-full rounded-lg border border-slate-200 bg-slate-50/70 py-1.5 pl-8 pr-3 text-xs text-slate-800 placeholder-slate-400 outline-none transition focus:border-navy-600 focus:bg-white focus:ring-2 focus:ring-navy-100"
          />
        </div>

        {/* Notifications Popover */}
        <div className="relative">
          <button
            onClick={() => {
              setShowNotifMenu(!showNotifMenu)
              setShowProfileMenu(false)
            }}
            className="relative flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 bg-slate-50/60 text-slate-600 transition hover:bg-slate-100 hover:text-slate-900 focus:outline-none"
            title="Notifications"
            aria-label="View notifications"
          >
            <Bell size={18} />
            {unreadNotifs.length > 0 && (
              <span className="absolute -top-1 -right-1 flex h-4 min-w-[16px] items-center justify-center rounded-full bg-rose-500 px-1 text-[10px] font-bold text-white shadow-xs animate-pulse">
                {unreadNotifs.length}
              </span>
            )}
          </button>

          {showNotifMenu && (
            <>
              <div
                className="fixed inset-0 z-40"
                onClick={() => setShowNotifMenu(false)}
              />
              <div className="absolute right-0 mt-2 w-80 sm:w-96 rounded-xl border border-slate-200 bg-white shadow-xl z-50 overflow-hidden animate-in fade-in slide-in-from-top-1">
                <div className="flex items-center justify-between border-b border-slate-100 px-4 py-3 bg-slate-50/80">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-800">
                      Notifications
                    </span>
                    {unreadNotifs.length > 0 && (
                      <span className="rounded-full bg-rose-100 px-2 py-0.2 text-[10px] font-bold text-rose-700">
                        {unreadNotifs.length} unread
                      </span>
                    )}
                  </div>
                  {unreadNotifs.length > 0 && (
                    <button
                      onClick={onMarkAllNotificationsRead}
                      className="text-[11px] font-semibold text-navy-700 hover:text-navy-900 transition"
                    >
                      Mark all as read
                    </button>
                  )}
                </div>

                <div className="max-h-80 overflow-y-auto divide-y divide-slate-100 scrollbar-thin">
                  {notifications.length === 0 ? (
                    <div className="py-8 text-center text-xs text-slate-400">
                      No notifications available
                    </div>
                  ) : (
                    notifications.map((n) => (
                      <div
                        key={n.id}
                        onClick={() => {
                          onMarkNotificationAsRead(n.id)
                          if (n.caseId) handleCaseClick(n.caseId)
                        }}
                        className={`flex gap-3 p-3.5 transition cursor-pointer hover:bg-slate-50 ${
                          !n.read ? 'bg-sky-50/40' : ''
                        }`}
                      >
                        <div className="flex-shrink-0 mt-0.5 p-1.5 rounded-lg bg-slate-100">
                          {getNotifIcon(n.type)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between gap-1">
                            <h4
                              className={`text-xs font-semibold truncate ${
                                !n.read ? 'text-slate-900 font-bold' : 'text-slate-700'
                              }`}
                            >
                              {n.title}
                            </h4>
                            {!n.read && (
                              <span className="h-2 w-2 rounded-full bg-navy-600 flex-shrink-0" />
                            )}
                          </div>
                          <p className="mt-0.5 text-xs text-slate-500 line-clamp-2 leading-relaxed">
                            {n.message}
                          </p>
                          <div className="mt-1 flex items-center justify-between text-[10px] text-slate-400">
                            <span>{n.timestamp}</span>
                            {n.caseId && (
                              <span className="font-semibold text-navy-700 hover:underline">
                                View {n.caseId} &rarr;
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>

                <div className="border-t border-slate-100 p-2.5 bg-slate-50/50 text-center">
                  <button
                    onClick={() => {
                      setShowNotifMenu(false)
                      onNavigate('notifications')
                    }}
                    className="text-xs font-semibold text-navy-800 hover:text-navy-900"
                  >
                    View All Activity &rarr;
                  </button>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Separator */}
        <div className="h-6 w-px bg-slate-200" />

        {/* User Profile Menu */}
        <div className="relative">
          <button
            onClick={() => {
              setShowProfileMenu(!showProfileMenu)
              setShowNotifMenu(false)
            }}
            className="flex items-center gap-2.5 rounded-lg p-1.5 text-left transition hover:bg-slate-100 focus:outline-none"
            aria-label="User profile menu"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#0b2250] text-xs font-bold text-white shadow-xs">
              {currentUser.avatarText}
            </div>
            <div className="hidden sm:block">
              <div className="flex items-center gap-1.5">
                <span className="text-xs font-bold text-slate-800 leading-none">
                  {currentUser.name}
                </span>
                <span
                  className={`rounded px-1.5 py-0.2 text-[9px] font-bold ${
                    currentRole === 'Admin'
                      ? 'bg-purple-100 text-purple-700'
                      : 'bg-teal-100 text-teal-700'
                  }`}
                >
                  {currentRole}
                </span>
              </div>
              <div className="text-[10px] text-slate-500 truncate max-w-[140px] mt-0.5">
                {currentUser.bureau === 'All'
                  ? 'All Bureaus'
                  : `${currentUser.bureau} Bureau`}
              </div>
            </div>
            <ChevronDown size={14} className="text-slate-400 hidden sm:block" />
          </button>

          {showProfileMenu && (
            <>
              <div
                className="fixed inset-0 z-40"
                onClick={() => setShowProfileMenu(false)}
              />
              <div className="absolute right-0 mt-2 w-64 rounded-xl border border-slate-200 bg-white shadow-xl z-50 overflow-hidden animate-in fade-in slide-in-from-top-1">
                <div className="border-b border-slate-100 bg-slate-50 p-4">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#0b2250] text-sm font-bold text-white shadow-sm">
                      {currentUser.avatarText}
                    </div>
                    <div className="min-w-0">
                      <div className="text-xs font-bold text-slate-900 truncate">
                        {currentUser.name}
                      </div>
                      <div className="text-[11px] text-slate-500 truncate">{currentUser.email}</div>
                      <div className="mt-1 flex items-center gap-1">
                        <Badge v={currentRole} />
                      </div>
                    </div>
                  </div>
                </div>

                <div className="p-1.5 text-xs text-slate-700 divide-y divide-slate-100">
                  <div className="py-1">
                    <button
                      onClick={() => {
                        setShowProfileMenu(false)
                        onNavigate('users')
                      }}
                      className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 hover:bg-slate-100 transition"
                    >
                      <User size={15} className="text-slate-400" />
                      <span>Officer Directory</span>
                    </button>
                    <button
                      onClick={() => {
                        setShowProfileMenu(false)
                        onNavigate('settings')
                      }}
                      className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 hover:bg-slate-100 transition"
                    >
                      <Settings size={15} className="text-slate-400" />
                      <span>System Settings</span>
                    </button>
                  </div>

                  <div className="py-1">
                    <button
                      onClick={() => {
                        onToggleRole()
                        setShowProfileMenu(false)
                      }}
                      className="flex w-full items-center justify-between rounded-lg px-3 py-2 hover:bg-slate-100 text-navy-800 font-medium transition"
                    >
                      <div className="flex items-center gap-2.5">
                        <Shield size={15} className="text-teal-600" />
                        <span>Switch to {currentRole === 'Admin' ? 'Officer View' : 'Admin View'}</span>
                      </div>
                      <span className="text-[10px] bg-slate-200 px-1.5 py-0.5 rounded font-mono">
                        Demo
                      </span>
                    </button>
                  </div>

                  <div className="pt-1">
                    <div className="px-3 py-2 text-[10px] text-slate-400 leading-tight">
                      AICTE CaseTrack SIH Edition • Production Frontend Prototype
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  )
}
