import { useState } from 'react'
import {
  AlertCircle,
  Building2,
  CheckCircle2,
  Info,
  KeyRound,
  Landmark,
  Loader2,
  LogIn,
  Mail,
  Shield,
  User,
  UserCheck,
} from 'lucide-react'
import type { Role, UserProfile } from '../types'
import { loginApi, demoLoginApi } from '../api/auth'

interface LoginProps {
  onLogin: (user: UserProfile, token: string) => void
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

const IS_DEMO_AUTH_ENABLED = Boolean(import.meta.env.DEV || import.meta.env.VITE_DEMO_AUTH === 'true')

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
  const [password, setPassword] = useState('AicteDemo@2026')
  const [isLoading, setIsLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const handleSelectRole = (r: DemoRoleConfig) => {
    setSelectedRole(r.role)
    setEmail(r.email)
    setPassword('AicteDemo@2026')
    setErrorMessage(null)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setErrorMessage(null)

    try {
      // Primary path: authenticate credentials against POST /api/auth/login
      const res = await loginApi({ email: email.trim(), password })
      onLogin(res.user, res.accessToken)
    } catch (err: unknown) {
      // Invalid credentials must remain invalid credentials. Never fall back to demo login.
      const msg =
        err instanceof Error
          ? err.message
          : 'Authentication failed. Please verify credentials or server connectivity.'
      setErrorMessage(msg)
    } finally {
      setIsLoading(false)
    }
  }

  const handleQuickLogin = async (r: DemoRoleConfig) => {
    setSelectedRole(r.role)
    setEmail(r.email)
    setPassword('AicteDemo@2026')
    setIsLoading(true)
    setErrorMessage(null)

    try {
      // Use demoLoginApi for rapid 1-click role testing
      const res = await demoLoginApi({ role: r.role, email: r.email })
      onLogin(res.user, res.accessToken)
    } catch {
      // Fallback to standard login
      try {
        const res = await loginApi({ email: r.email, password: 'AicteDemo@2026' })
        onLogin(res.user, res.accessToken)
      } catch (err: unknown) {
        const msg =
          err instanceof Error
            ? err.message
            : `Failed to authenticate as ${r.title}.`
        setErrorMessage(msg)
      }
    } finally {
      setIsLoading(false)
    }
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
          <span>FastAPI + PostgreSQL Integrated</span>
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
              Select one of the verified demo perspectives or enter your AICTE credentials.
            </p>
          </div>

          {/* Backend Authentication Notice */}
          <div className="rounded-xl border border-sky-200 bg-sky-50/70 p-3.5 text-xs text-sky-900 flex items-start gap-2.5">
            <Info size={17} className="text-sky-700 flex-shrink-0 mt-0.5" />
            <div className="leading-relaxed">
              <strong className="font-semibold">FastAPI Backend Authentication:</strong> Credentials and role tokens are validated directly against PostgreSQL. Permissions are strictly derived from the server response.
            </div>
          </div>

          {/* Error Banner */}
          {errorMessage && (
            <div className="rounded-xl border border-rose-200 bg-rose-50 p-3.5 text-xs text-rose-800 flex items-start gap-2.5">
              <AlertCircle size={17} className="text-rose-600 flex-shrink-0 mt-0.5" />
              <div className="leading-relaxed">
                <strong className="font-semibold">Authentication Error:</strong> {errorMessage}
              </div>
            </div>
          )}

          {/* Step 1: Select Demo Role Cards */}
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
              Step 1: Choose Role Perspective
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              {DEMO_ROLES.map((r) => {
                const Icon = r.icon
                const isSelected = selectedRole === r.role
                return (
                  <button
                    key={r.role}
                    type="button"
                    disabled={isLoading}
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
                Account Email
              </label>
              <div className="relative">
                <input
                  type="email"
                  value={email}
                  disabled={isLoading}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full rounded-lg border border-slate-300 pl-9 pr-3 py-2 text-xs font-medium text-slate-800 focus:border-navy-700 focus:outline-none disabled:bg-slate-50 disabled:text-slate-500"
                />
                <Mail size={15} className="absolute left-3 top-2.5 text-slate-400" />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Password
              </label>
              <div className="relative">
                <input
                  type="password"
                  value={password}
                  disabled={isLoading}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full rounded-lg border border-slate-300 pl-9 pr-3 py-2 text-xs font-mono text-slate-800 focus:border-navy-700 focus:outline-none disabled:bg-slate-50 disabled:text-slate-500"
                />
                <KeyRound size={15} className="absolute left-3 top-2.5 text-slate-400" />
              </div>
              <p className="text-[10px] text-slate-400 mt-1">
                Default seed accounts password: <span className="font-mono text-slate-600">AicteDemo@2026</span>
              </p>
            </div>

            <div className="pt-2">
              <button
                type="submit"
                disabled={isLoading}
                className="w-full flex items-center justify-center gap-2 rounded-lg bg-navy-800 hover:bg-navy-900 disabled:opacity-60 disabled:cursor-not-allowed px-4 py-2.5 text-xs font-bold text-white transition shadow-xs"
              >
                {isLoading ? (
                  <>
                    <Loader2 size={15} className="animate-spin" />
                    <span>Authenticating with FastAPI...</span>
                  </>
                ) : (
                  <>
                    <LogIn size={15} />
                    <span>Sign in as {activeRoleConfig.title}</span>
                  </>
                )}
              </button>
            </div>

            {/* Quick 1-click login pills (development / demo mode only) */}
            {IS_DEMO_AUTH_ENABLED && (
              <div className="pt-3 border-t border-slate-100">
                <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">
                  Quick 1-Click Role Access (Dev/Demo):
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {DEMO_ROLES.map((r) => (
                    <button
                      key={r.role}
                      type="button"
                      disabled={isLoading}
                      onClick={() => handleQuickLogin(r)}
                      className="rounded-md border border-slate-200 bg-slate-50 hover:bg-slate-100 disabled:opacity-50 px-2.5 py-1 text-[11px] font-medium text-slate-700 transition"
                    >
                      {r.title}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </form>

          {/* Footer Metadata */}
          <div className="text-center text-[11px] text-slate-400">
            AICTE Official Complaint Surveillance &amp; SLA Management System • 2026
          </div>
        </div>
      </div>
    </div>
  )
}
