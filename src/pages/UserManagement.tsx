import { useState } from 'react'
import {
  AlertCircle,
  Building2,
  CheckCircle2,
  Mail,
  Phone,
  Search,
  Shield,
  ShieldCheck,
  UserCheck,
  UserPlus,
  Users,
  X,
} from 'lucide-react'
import type { Bureau, Role, UserProfile } from '../types'
import { BUREAUS, USER_STORAGE_KEY, userProfiles as initialProfiles } from '../data'
import { Badge, Button, Card, Modal, PageTitle, SearchBox } from '../components/ui'

export { USER_STORAGE_KEY }

export function getStoredUsers(): UserProfile[] {
  try {
    const stored = localStorage.getItem(USER_STORAGE_KEY)
    if (stored) {
      const parsed = JSON.parse(stored)
      if (Array.isArray(parsed) && parsed.length > 0) {
        return parsed
      }
    }
  } catch {
    // fallback
  }
  return initialProfiles
}

export interface UserManagementProps {
  currentRole?: Role
  currentUser?: UserProfile
  users?: UserProfile[]
  onUpdateUsers?: React.Dispatch<React.SetStateAction<UserProfile[]>>
}

export default function UserManagement({
  currentRole = 'Admin',
  currentUser,
  users: externalUsers,
  onUpdateUsers,
}: UserManagementProps) {
  const [internalUsers, setInternalUsers] = useState<UserProfile[]>(() => getStoredUsers())
  const users = externalUsers ?? internalUsers

  const updateUsers = (updater: (prev: UserProfile[]) => UserProfile[]) => {
    if (onUpdateUsers) {
      onUpdateUsers((prev) => {
        const next = updater(prev)
        try {
          localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(next))
        } catch {
          // ignore
        }
        return next
      })
    } else {
      setInternalUsers((prev) => {
        const next = updater(prev)
        try {
          localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(next))
        } catch {
          // ignore
        }
        return next
      })
    }
  }

  const [search, setSearch] = useState('')
  const [bureauFilter, setBureauFilter] = useState<string>('All')
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)
  const [noticeBanner, setNoticeBanner] = useState<string | null>(null)
  const [errorBanner, setErrorBanner] = useState<string | null>(null)

  // New Officer State
  const [newName, setNewName] = useState('')
  const [newEmail, setNewEmail] = useState('')
  const [newDesignation, setNewDesignation] = useState('')
  const [newBureau, setNewBureau] = useState<Bureau>('PGRC')
  const [newRole, setNewRole] = useState<Role>('Officer')
  const [newPhone, setNewPhone] = useState('')

  const isAdmin = currentRole === 'Admin'

  const filtered = users.filter((u) => {
    const text = `${u.name} ${u.email} ${u.designation} ${u.bureau}`.toLowerCase()
    const matchesSearch = !search.trim() || text.includes(search.toLowerCase().trim())
    const matchesBureau = bureauFilter === 'All' || u.bureau === bureauFilter
    return matchesSearch && matchesBureau
  })

  const handleAddOfficer = (e: React.FormEvent) => {
    e.preventDefault()
    setNoticeBanner(null)
    setErrorBanner(null)

    if (!isAdmin) {
      setErrorBanner('Unauthorized: Only System Administrators can provision new bureau officers.')
      return
    }

    if (!newName.trim() || !newEmail.trim()) {
      setErrorBanner('Please provide both the official name and email address.')
      return
    }

    const emailCandidate = newEmail.trim().toLowerCase()
    const isDuplicate = users.some((u) => u.email.toLowerCase() === emailCandidate)
    if (isDuplicate) {
      setErrorBanner(`An officer with official email "${newEmail.trim()}" is already registered in the directory.`)
      return
    }

    const initials = newName
      .trim()
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)

    const created: UserProfile = {
      id: `u-${Date.now()}`,
      name: newName.trim(),
      email: newEmail.trim(),
      designation: newDesignation.trim() || 'Grievance Officer',
      bureau: newBureau,
      role: newRole,
      avatarText: initials || 'OF',
      phone: newPhone.trim() || '+91 11 2958 0000',
      activeCasesCount: 0,
      status: 'Active',
    }

    updateUsers((prev) => [...prev, created])
    setNewName('')
    setNewEmail('')
    setNewDesignation('')
    setNewPhone('')
    setIsAddModalOpen(false)
    setNoticeBanner(
      `Officer "${created.name}" (${created.bureau} Bureau) successfully provisioned and persisted to ${USER_STORAGE_KEY}.`
    )
  }

  const toggleStatus = (id: string) => {
    setNoticeBanner(null)
    setErrorBanner(null)

    if (!isAdmin) {
      setErrorBanner('Unauthorized: Only System Administrators can alter officer duty status.')
      return
    }

    const target = users.find((u) => u.id === id)
    if (!target) return

    const nextStatus = target.status === 'Active' ? 'On Leave' : 'Active'
    updateUsers((prev) =>
      prev.map((u) => (u.id === id ? { ...u, status: nextStatus } : u))
    )
    setNoticeBanner(`Duty status for "${target.name}" changed to ${nextStatus} and saved to ${USER_STORAGE_KEY}.`)
  }

  return (
    <div className="space-y-6">
      <PageTitle
        title="AICTE Personnel & Bureau Officers"
        sub="Authorised grievance investigators, bureau directors, and case handling officers"
        action={
          <Button
            variant="primary"
            size="sm"
            onClick={() => {
              if (!isAdmin) {
                setErrorBanner('Unauthorized: Only System Administrators can provision new bureau officers.')
                return
              }
              setIsAddModalOpen(true)
            }}
            className="text-xs"
          >
            <UserPlus size={14} />
            <span>Add Bureau Officer</span>
          </Button>
        }
      />

      {/* Non-blocking Notice Banner */}
      {noticeBanner && (
        <div className="flex items-start justify-between gap-3 rounded-lg border border-emerald-300 bg-emerald-50 p-4 text-xs font-medium text-emerald-900 shadow-2xs">
          <div className="flex items-center gap-2">
            <CheckCircle2 size={16} className="text-emerald-700 shrink-0" />
            <span>{noticeBanner}</span>
          </div>
          <button
            type="button"
            onClick={() => setNoticeBanner(null)}
            className="text-emerald-700 hover:text-emerald-900"
          >
            <X size={14} />
          </button>
        </div>
      )}

      {/* Non-blocking Error Banner */}
      {errorBanner && (
        <div className="flex items-start justify-between gap-3 rounded-lg border border-red-300 bg-red-50 p-4 text-xs font-medium text-red-900 shadow-2xs">
          <div className="flex items-center gap-2">
            <AlertCircle size={16} className="text-red-700 shrink-0" />
            <span>{errorBanner}</span>
          </div>
          <button
            type="button"
            onClick={() => setErrorBanner(null)}
            className="text-red-700 hover:text-red-900"
          >
            <X size={14} />
          </button>
        </div>
      )}

      {/* Summary KPI Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="flex items-center gap-3">
          <div className="rounded-xl bg-navy-50 p-3 text-navy-800">
            <Users size={22} />
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-900">{users.length}</div>
            <div className="text-xs text-slate-500">Total Authorised Officers</div>
          </div>
        </Card>

        <Card className="flex items-center gap-3">
          <div className="rounded-xl bg-teal-50 p-3 text-teal-700">
            <UserCheck size={22} />
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-900">
              {users.filter((u) => u.status === 'Active').length}
            </div>
            <div className="text-xs text-slate-500">Active on Duty</div>
          </div>
        </Card>

        <Card className="flex items-center gap-3">
          <div className="rounded-xl bg-indigo-50 p-3 text-indigo-700">
            <ShieldCheck size={22} />
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-900">
              {users.filter((u) => u.bureau === 'RB').length}
            </div>
            <div className="text-xs text-slate-500">Regulation Bureau Staff</div>
          </div>
        </Card>

        <Card className="flex items-center gap-3">
          <div className="rounded-xl bg-sky-50 p-3 text-sky-700">
            <Building2 size={22} />
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-900">
              {users.filter((u) => u.bureau === 'PGRC').length}
            </div>
            <div className="text-xs text-slate-500">PGRC Cell Officers</div>
          </div>
        </Card>
      </div>

      {/* Filter and Search */}
      <Card padding="p-4">
        <div className="flex flex-wrap items-center gap-3">
          <SearchBox
            value={search}
            onChange={setSearch}
            placeholder="Search by officer name, email, designation..."
            className="flex-1 min-w-[240px]"
          />

          <select
            value={bureauFilter}
            onChange={(e) => setBureauFilter(e.target.value)}
            className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs font-medium text-slate-700 focus:outline-none"
          >
            <option value="All">All Bureaus</option>
            {BUREAUS.map((b) => (
              <option key={b} value={b}>
                Bureau: {b}
              </option>
            ))}
          </select>
        </div>
      </Card>

      {/* Officers Grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {filtered.map((user) => (
          <Card key={user.id} className="space-y-4">
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-center gap-3">
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-[#0b2250] text-sm font-bold text-white shadow-2xs">
                  {user.avatarText}
                </div>
                <div>
                  <h4 className="text-sm font-bold text-slate-900 leading-snug">{user.name}</h4>
                  <p className="text-xs text-slate-500">{user.designation}</p>
                </div>
              </div>

              <span
                className={`rounded px-2 py-0.5 text-[10px] font-bold ${
                  user.status === 'Active'
                    ? 'bg-emerald-100 text-emerald-800'
                    : 'bg-amber-100 text-amber-800'
                }`}
              >
                {user.status}
              </span>
            </div>

            <div className="space-y-2 rounded-lg bg-slate-50 p-3 text-xs border border-slate-100 text-slate-600">
              <div className="flex items-center justify-between">
                <span>Bureau:</span>
                <Badge v={user.bureau} />
              </div>
              <div className="flex items-center justify-between">
                <span>System Role:</span>
                <Badge v={user.role} />
              </div>
              <div className="flex items-center justify-between">
                <span>Active Assigned Cases:</span>
                <span className="font-bold text-navy-800">{user.activeCasesCount} Active</span>
              </div>
            </div>

            <div className="space-y-1 text-xs text-slate-500">
              <div className="flex items-center gap-2">
                <Mail size={13} className="text-slate-400" />
                <span className="truncate">{user.email}</span>
              </div>
              <div className="flex items-center gap-2">
                <Phone size={13} className="text-slate-400" />
                <span>{user.phone}</span>
              </div>
            </div>

            <div className="border-t border-slate-100 pt-3 flex items-center justify-between">
              <button
                onClick={() => toggleStatus(user.id)}
                disabled={!isAdmin}
                title={!isAdmin ? 'Only System Administrators can change duty status' : undefined}
                className={`text-xs font-medium ${
                  isAdmin
                    ? 'text-slate-500 hover:text-navy-800 cursor-pointer'
                    : 'text-slate-400 cursor-not-allowed opacity-60'
                }`}
              >
                Toggle Status ({user.status === 'Active' ? 'Set On Leave' : 'Set Active'})
              </button>
              <span className="text-[10px] text-slate-400 font-mono">ID: {user.id}</span>
            </div>
          </Card>
        ))}
      </div>

      {/* Add Officer Modal */}
      <Modal
        open={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        title="Add AICTE Bureau Officer"
        subtitle="Provision an authorised case investigator into Abhigyan"
      >
        <form onSubmit={handleAddOfficer} className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Full Official Name *
              </label>
              <input
                type="text"
                required
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                placeholder="e.g. Dr. Ramesh Chander"
                className="w-full rounded-lg border border-slate-300 p-2 text-xs font-medium text-slate-800 focus:border-navy-600 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Official AICTE Email *
              </label>
              <input
                type="email"
                required
                value={newEmail}
                onChange={(e) => setNewEmail(e.target.value)}
                placeholder="e.g. ramesh.chander@aicte-india.org"
                className="w-full rounded-lg border border-slate-300 p-2 text-xs font-medium text-slate-800 focus:border-navy-600 focus:outline-none"
              />
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-3">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Primary Bureau *
              </label>
              <select
                value={newBureau}
                onChange={(e) => setNewBureau(e.target.value as Bureau)}
                className="w-full rounded-lg border border-slate-300 p-2 text-xs font-medium text-slate-800 focus:border-navy-600 focus:outline-none"
              >
                {BUREAUS.map((b) => (
                  <option key={b} value={b}>
                    {b}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Access Role *
              </label>
              <select
                value={newRole}
                onChange={(e) => setNewRole(e.target.value as Role)}
                className="w-full rounded-lg border border-slate-300 p-2 text-xs font-medium text-slate-800 focus:border-navy-600 focus:outline-none"
              >
                <option value="Officer">Case Officer</option>
                <option value="Admin">Bureau Administrator</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Phone</label>
              <input
                type="text"
                value={newPhone}
                onChange={(e) => setNewPhone(e.target.value)}
                placeholder="+91 11 2958 1000"
                className="w-full rounded-lg border border-slate-300 p-2 text-xs font-medium text-slate-800 focus:border-navy-600 focus:outline-none"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Designation Title
            </label>
            <input
              type="text"
              value={newDesignation}
              onChange={(e) => setNewDesignation(e.target.value)}
              placeholder="e.g. Scrutiny Officer, Fee Monitoring Cell"
              className="w-full rounded-lg border border-slate-300 p-2 text-xs font-medium text-slate-800 focus:border-navy-600 focus:outline-none"
            />
          </div>

          <div className="flex items-center justify-end gap-2 border-t border-slate-100 pt-3">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setIsAddModalOpen(false)}
            >
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="sm">
              <UserCheck size={14} />
              <span>Confirm &amp; Add Officer</span>
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
