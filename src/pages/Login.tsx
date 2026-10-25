import { useState } from 'react'
import {
  Building2,
  CheckCircle2,
  Info,
  KeyRound,
  Landmark,
  LogIn,
  Mail,
  Shield,
  ShieldAlert,
  User,
  UserCheck,
} from 'lucide-react'
import type { Role } from '../types'

interface LoginProps {
  onLogin: (role: Role, userEmail?: string) => void
  initialRole?: Role
}

interface DemoRoleConfig {
  role: Role
  label: string
  title: string
  user: string
  email: string
  scope: string
  icon: typeof Shield
  accent: string
}

const DEMO_ROLES: DemoRoleConfig[] = [
  {
    role: 'Complainant',
    label: 'Citizen / Student',
    title: 'Complainant / User',
    user: 'Rohit Sharma',
    email: 'rohit.sharma@student.edu.in',
    scope: 'Submit grievances, track personal docket timeline, upload supporting evidence',
    icon: User,
    accent: 'border-emerald-500 bg-emerald-50/50 text-emerald-900',
  },
  {
    role: 'BureauAdmin',
    label: 'Bureau Head',
    title: 'Bureau / Cell Admin',
    user: 'Dr. Priya Nair',
    email: 'priya.nair@aicte-india.org',
    scope: 'Manage PGRC/RB dockets, assign officers, review bureau workload and SLA queues',
    icon: Building2,
    accent: 'border-sky-500 bg-sky-50/50 text-sky-900',
  },
  {
    role: 'Officer',
    label: 'Case Officer',
    title: 'Handling Officer',
    user: 'Rajesh Kumar',
    email: 'rajesh.kumar@aicte-india.org',
    scope: 'Investigate assigned cases, record inquiry notes, update status, review overlaps',
    icon: UserCheck,
    accent: 'border-teal-500 bg-teal-50/50 text-teal-900',
  },
  {
    role: 'Admin',
    label: 'System Admin',
    title: 'System Admin',
    user: 'Dr. S. Mehta',
    email: 'member-sec@aicte-india.org',
    scope: 'All bureaus oversight, user directory, institution master data, SLA thresholds',
    icon: Shield,
    accent: 'border-navy-800 bg-navy-50/50 text-navy-900',
  },
]

export default function Login({ onLogin, initialRole = 'Admin' }: LoginProps) {
  const defaultRoleConfig = DEMO_ROLES.find((r) => r.role === initialRole) || DEMO_ROLES[3]
  const [selectedRole, setSelectedRole] = useState<Role>(initialRole)
  const [email, setEmail] = useState(defaultRoleConfig.email)
  const [password, setPassword] = useState('demo-access-2026')

  const handleSelectRole = (r: DemoRoleConfig) => {
    setSelectedRole(r.role)
    setEmail(r.email)
    setPassword('demo-access-2026')
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onLogin(selectedRole, email)
  }

  const activeRoleConfig = DEMO_ROLES.find((r) => r.role === selectedRole) || DEMO_ROLES[3]

  return (
    <div className="grid min-h-screen lg:grid-cols-12 bg-slate-100 font-sans">
      {/* Left Branding & Context Panel */}
      <div className="hidden lg:flex lg:col-span-5 flex-col justify-between bg-[#0b2250] p-10 text-white relative overflow-hidden">
        <div className="relative z-10 space-y-6">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-xl bg-teal-500/20 text-teal-300 border border-teal-400/30 flex items-center justify-center">
              <Landmark size={24} />
            </div>
            <div>
              <div className="font-bold text-base tracking-wide uppercase">All India Council for Technical Education</div>
              <div className="text-xs text-navy-200">Ministry of Education, Government of India</div>
            </div>
          </div>

          <div className="pt-8">
            <span className="inline-block px-2.5 py-1 rounded bg-teal-500/20 text-teal-200 text-xs font-semibold uppercase tracking-wider border border-teal-400/30 mb-3">
              Abhigyan Platform
            </span>
            <h1 className="text-3xl font-bold leading-tight text-white">
              Integrated Complaint Monitoring &amp; Cross-Bureau Redressal System
            </h1>
            <p className="mt-4 text-sm text-slate-300 leading-relaxed">
              Unified surveillance and dispute resolution across the Regulation Bureau (RB), Public Grievance Redressal Cell (PGRC), and Approval Bureau. Detect duplicate dockets early, enforce statutory SLA windows, and streamline inter-bureau coordination.
            </p>
          </div>

          {/* 4 Roles Overview */}
          <div className="pt-4 space-y-2.5">
            <div className="text-xs font-bold uppercase tracking-wider text-teal-300">
              Role-Based Access Matrix
            </div>
            <div className="grid gap-2 text-xs">
              <div className="rounded-lg bg-white/5 p-2.5 border border-white/10">
                <span className="font-semibold text-white">Complainant / Citizen:</span>
                <span className="text-slate-300 ml-1.5">Direct grievance filing and secure tracking of personal dockets.</span>
              </div>
              <div className="rounded-lg bg-white/5 p-2.5 border border-white/10">
                <span className="font-semibold text-white">Bureau / Cell Admin:</span>
                <span className="text-slate-300 ml-1.5">Workload distribution, docket assignment, and SLA enforcement.</span>
              </div>
              <div className="rounded-lg bg-white/5 p-2.5 border border-white/10">
                <span className="font-semibold text-white">Handling Officer:</span>
                <span className="text-slate-300 ml-1.5">Field inquiry hearings, action notes, and overlap validation.</span>
              </div>
              <div className="rounded-lg bg-white/5 p-2.5 border border-white/10">
                <span className="font-semibold text-white">System Admin:</span>
                <span className="text-slate-300 ml-1.5">Cross-bureau governance, master data, and institutional registry.</span>
              </div>
            </div>
          </div>
        </div>

        <div className="relative z-10 pt-6 border-t border-white/10 flex items-center justify-between text-xs text-slate-400">
          <span>AICTE Prototype Build</span>
          <span>FastAPI + PostgreSQL Ready</span>
        </div>
      </div>

      {/* Right Login / Demo Role Selection Form */}
      <div className="lg:col-span-7 flex flex-col justify-center px-6 py-10 sm:px-12 lg:px-16 max-w-2xl mx-auto w-full">
        {/* Mobile Header */}
        <div className="lg:hidden flex items-center gap-3 mb-6 p-4 rounded-xl bg-[#0b2250] text-white">
          <Landmark size={24} className="text-teal-300" />
          <div>
            <div className="font-bold text-sm">Abhigyan • AICTE</div>
            <div className="text-[11px] text-slate-300">Complaint Monitoring Portal</div>
          </div>
        </div>

        <div className="space-y-6">
          <div>
            <h2 className="text-2xl font-bold text-slate-900">Sign In to Abhigyan</h2>
            <p className="text-xs text-slate-500 mt-1">
              Select one of the four demo perspectives below for simulated role-based access.
            </p>
          </div>

          {/* Prototype Notice Banner */}
          <div className="rounded-xl border border-sky-200 bg-sky-50/70 p-3.5 text-xs text-sky-900 flex items-start gap-2.5">
            <Info size={17} className="text-sky-700 flex-shrink-0 mt-0.5" />
            <div className="leading-relaxed">
              <strong className="font-semibold">Simulated Prototype Access:</strong> No real credentials or passwords are collected. Real token-based authentication will be enforced by the FastAPI backend.
            </div>
          </div>

          {/* Step 1: Select Demo Role Cards */}
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
              Step 1: Choose Demo Role Perspective
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              {DEMO_ROLES.map((r) => {
                const Icon = r.icon
                const isSelected = selectedRole === r.role
                return (
                  <button
                    key={r.role}
                    type="button"
                    onClick={() => handleSelectRole(r)}
                    className={`text-left p-3.5 rounded-xl border-2 transition-all relative ${
                      isSelected
                        ? `${r.accent} shadow-xs ring-1 ring-slate-400/20`
                        : 'border-slate-200 bg-white hover:border-slate-300 text-slate-700'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <Icon size={16} />
                        <span className="font-bold text-xs">{r.title}</span>
                      </div>
                      {isSelected && (
                        <CheckCircle2 size={15} className="text-current" />
                      )}
                    </div>
                    <div className="text-[11px] font-semibold text-slate-700 mt-1.5 truncate">
                      {r.user}
                    </div>
                    <div className="text-[10px] text-slate-500 line-clamp-2 mt-0.5 leading-tight">
                      {r.scope}
                    </div>
                  </button>
                )
              })}
            </div>
          </div>

          {/* Step 2: Form & Sign In */}
          <form onSubmit={handleSubmit} className="space-y-4 bg-white p-5 rounded-xl border border-slate-200 shadow-2xs">
            <div className="flex items-center justify-between border-b border-slate-100 pb-2.5">
              <span className="text-xs font-bold text-slate-800">
                Step 2: Sign In as <span className="text-teal-700 font-extrabold">{activeRoleConfig.title}</span>
              </span>
              <span className="text-[11px] font-mono text-slate-400">
                {activeRoleConfig.label}
              </span>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Demo User Account Email
              </label>
              <div className="relative">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full rounded-lg border border-slate-300 pl-9 pr-3 py-2 text-xs font-medium text-slate-800 focus:border-navy-700 focus:outline-none"
                />
                <Mail size={15} className="absolute left-3 top-2.5 text-slate-400" />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Simulated Password (Pre-filled)
              </label>
              <div className="relative">
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full rounded-lg border border-slate-300 pl-9 pr-3 py-2 text-xs font-mono text-slate-800 focus:border-navy-700 focus:outline-none"
                />
                <KeyRound size={15} className="absolute left-3 top-2.5 text-slate-400" />
              </div>
              <p className="text-[10px] text-slate-400 mt-1">
                Prototype authentication token will be passed to FastAPI backend session.
              </p>
            </div>

            <div className="pt-2">
              <button
                type="submit"
                className="w-full flex items-center justify-center gap-2 rounded-lg bg-navy-800 hover:bg-navy-900 px-4 py-2.5 text-xs font-bold text-white transition shadow-xs"
              >
                <LogIn size={15} />
                <span>Sign in as {activeRoleConfig.title}</span>
              </button>
            </div>

            {/* Quick 1-click login pills */}
            <div className="pt-3 border-t border-slate-100">
              <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">
                Quick 1-Click Access:
              </div>
              <div className="flex flex-wrap gap-1.5">
                {DEMO_ROLES.map((r) => (
                  <button
                    key={r.role}
                    type="button"
                    onClick={() => {
                      setSelectedRole(r.role)
                      onLogin(r.role, r.email)
                    }}
                    className="rounded-md border border-slate-200 bg-slate-50 hover:bg-slate-100 px-2.5 py-1 text-[11px] font-medium text-slate-700 transition"
                  >
                    {r.title}
                  </button>
                ))}
              </div>
            </div>
          </form>

          {/* Footer Metadata */}
          <div className="text-center text-[11px] text-slate-400">
            AICTE Official Complaint Surveillance &amp; SLA Management Prototype • 2026
          </div>
        </div>
      </div>
    </div>
  )
}
