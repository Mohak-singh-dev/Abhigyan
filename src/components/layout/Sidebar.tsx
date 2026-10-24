import {
  BarChart3,
  Bell,
  Building2,
  ChevronLeft,
  ChevronRight,
  FileText,
  FolderGit2,
  GitMerge,
  Landmark,
  LayoutDashboard,
  Settings,
  ShieldCheck,
  UserCheck,
  Users,
} from 'lucide-react'
import type { Page, Role } from '../../types'

interface SidebarProps {
  activePage: Page
  onNavigate: (page: Page) => void
  collapsed: boolean
  onToggleCollapse: () => void
  unreadNotificationsCount: number
  pendingOverlapsCount: number
  currentRole: Role
  onToggleRole: () => void
}

interface NavConfig {
  id: Page
  label: string
  icon: typeof LayoutDashboard
  badge?: number
  badgeColor?: string
}

export default function Sidebar({
  activePage,
  onNavigate,
  collapsed,
  onToggleCollapse,
  unreadNotificationsCount,
  pendingOverlapsCount,
  currentRole,
  onToggleRole,
}: SidebarProps) {
  const navItems: NavConfig[] = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'complaints', label: 'All Complaints', icon: FileText },
    { id: 'institutions', label: 'Institutions', icon: Building2 },
    {
      id: 'overlaps',
      label: 'Overlap Detection',
      icon: GitMerge,
      badge: pendingOverlapsCount > 0 ? pendingOverlapsCount : undefined,
      badgeColor: 'bg-amber-500 text-slate-900',
    },
    { id: 'tracking', label: 'Case Tracking', icon: FolderGit2 },
    { id: 'reports', label: 'Reports & Analytics', icon: BarChart3 },
    {
      id: 'notifications',
      label: 'Notifications',
      icon: Bell,
      badge: unreadNotificationsCount > 0 ? unreadNotificationsCount : undefined,
      badgeColor: 'bg-rose-500 text-white',
    },
    { id: 'users', label: 'User Management', icon: Users },
    { id: 'settings', label: 'Settings', icon: Settings },
  ]

  const bureaus = [
    { code: 'RB', name: 'Regulation Bureau' },
    { code: 'PGRC', name: 'Grievance Cell' },
    { code: 'Approval', name: 'Approval Bureau' },
    { code: 'Academic', name: 'Academic Bureau' },
  ]

  return (
    <aside
      className={`relative flex flex-col bg-[#0b2250] text-white transition-all duration-300 ease-in-out border-r border-white/10 z-30 select-none ${
        collapsed ? 'w-20' : 'w-64'
      }`}
    >
      {/* Brand Header */}
      <div className="flex items-center gap-3 border-b border-white/10 px-4 py-5 min-h-[72px]">
        <div className="flex-shrink-0 flex items-center justify-center w-10 h-10 rounded-xl bg-teal-500/20 text-teal-300 border border-teal-400/30 shadow-inner">
          <Landmark size={22} strokeWidth={2.2} />
        </div>
        {!collapsed && (
          <div className="min-w-0 overflow-hidden">
            <div className="font-bold text-sm tracking-wide text-white leading-tight flex items-center gap-1.5">
              <span>Abhigyan</span>
              <span className="text-[10px] font-semibold uppercase px-1.5 py-0.2 rounded bg-teal-500/30 text-teal-200 border border-teal-400/30">
                SIH
              </span>
            </div>
            <div className="text-[11px] text-navy-200 truncate font-normal mt-0.5">
              AICTE Complaint Monitoring
            </div>
          </div>
        )}
      </div>

      {/* Navigation List */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1 scrollbar-thin">
        {!collapsed && (
          <div className="px-3 pb-2 text-[10px] font-bold uppercase tracking-wider text-navy-200/60">
            Core Modules
          </div>
        )}
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive =
            activePage === item.id || (activePage === 'details' && item.id === 'complaints')

          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              title={collapsed ? item.label : undefined}
              className={`group relative flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all ${
                isActive
                  ? 'bg-white/15 text-white shadow-sm font-semibold'
                  : 'text-navy-100 hover:bg-white/10 hover:text-white'
              } ${collapsed ? 'justify-center px-0' : ''}`}
            >
              <div className="relative flex-shrink-0">
                <Icon
                  size={19}
                  className={`transition-colors ${
                    isActive ? 'text-teal-300' : 'text-navy-200 group-hover:text-white'
                  }`}
                  strokeWidth={isActive ? 2.3 : 1.9}
                />
                {item.badge && collapsed && (
                  <span className="absolute -top-1.5 -right-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-rose-500 text-[9px] font-bold text-white ring-2 ring-[#0b2250]">
                    {item.badge}
                  </span>
                )}
              </div>

              {!collapsed && (
                <>
                  <span className="flex-1 text-left truncate">{item.label}</span>
                  {item.badge && (
                    <span
                      className={`ml-auto flex-shrink-0 rounded-full px-2 py-0.5 text-[11px] font-bold ${
                        item.badgeColor || 'bg-white/20 text-white'
                      }`}
                    >
                      {item.badge}
                    </span>
                  )}
                  {isActive && <div className="h-4 w-1 rounded-full bg-teal-400" />}
                </>
              )}
            </button>
          )
        })}

        {/* Bureau Tags Section */}
        {!collapsed && (
          <div className="pt-5 mt-4 border-t border-white/10">
            <div className="px-3 pb-2 text-[10px] font-bold uppercase tracking-wider text-navy-200/60 flex items-center justify-between">
              <span>Integrated Bureaus</span>
              <ShieldCheck size={13} className="text-teal-400" />
            </div>
            <div className="grid grid-cols-2 gap-1.5 px-1">
              {bureaus.map((b) => (
                <div
                  key={b.code}
                  className="rounded-md bg-white/5 px-2 py-1.5 text-left border border-white/5 hover:bg-white/10 transition cursor-default"
                >
                  <div className="text-[11px] font-bold text-teal-300">{b.code}</div>
                  <div className="text-[9px] text-navy-200 truncate">{b.name}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </nav>

      {/* Role Switcher & Collapse Toggle Footer */}
      <div className="border-t border-white/10 p-3 space-y-2">
        {/* Role toggle badge */}
        {!collapsed ? (
          <div className="flex items-center justify-between rounded-lg bg-white/5 p-2 border border-white/10">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-md bg-teal-500/20 text-teal-300 flex items-center justify-center text-xs font-bold">
                {currentRole === 'Admin' ? 'A' : 'O'}
              </div>
              <div>
                <div className="text-xs font-semibold text-white leading-tight">
                  {currentRole === 'Admin' ? 'Central Admin' : 'Case Officer'}
                </div>
                <div className="text-[10px] text-navy-200">
                  {currentRole === 'Admin' ? 'Full AICTE Oversight' : 'Grievance Redressal'}
                </div>
              </div>
            </div>
            <button
              onClick={onToggleRole}
              title="Switch user perspective for testing"
              className="rounded bg-white/10 hover:bg-white/20 px-2 py-1 text-[10px] font-semibold text-teal-200 transition"
            >
              Switch
            </button>
          </div>
        ) : (
          <button
            onClick={onToggleRole}
            title={`Active role: ${currentRole} (Click to switch)`}
            className="w-full flex justify-center py-2 text-teal-300 hover:bg-white/10 rounded-lg transition"
          >
            <UserCheck size={18} />
          </button>
        )}

        {/* Sidebar Collapse Toggle */}
        <button
          onClick={onToggleCollapse}
          className="flex w-full items-center justify-center gap-2 rounded-lg py-1.5 text-xs text-navy-200 hover:bg-white/10 hover:text-white transition"
          title={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
        >
          {collapsed ? (
            <ChevronRight size={16} />
          ) : (
            <>
              <ChevronLeft size={16} />
              <span className="text-[11px] font-medium">Collapse Menu</span>
            </>
          )}
        </button>
      </div>
    </aside>
  )
}
