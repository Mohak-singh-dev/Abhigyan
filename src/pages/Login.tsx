import { useState } from 'react'
import { Landmark, LogIn } from 'lucide-react'
import type { Role } from '../types'

export default function Login({ onLogin }: { onLogin: (r: Role) => void }) {
  const [email, setEmail] = useState('official@aicte-india.org')
  const [password, setPassword] = useState('demo1234')
  const [role, setRole] = useState<Role>('Admin')
  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      <div className="hidden flex-col justify-between bg-navy-900 p-12 text-white lg:flex">
        <div className="flex items-center gap-3 text-lg font-semibold"><Landmark /> Abhigyan • AICTE</div>
        <div>
          <h1 className="text-4xl font-semibold leading-tight">Integrated Complaint<br />Monitoring Dashboard</h1>
          <p className="mt-4 max-w-md text-navy-200">One view of institution complaints across the Regulation Bureau and PGRC. Spot overlaps early, track deadlines and close cases faster.</p>
        </div>
        <p className="text-sm text-navy-200">Smart India Hackathon · Demo build</p>
      </div>
      <div className="flex items-center justify-center p-6">
        <form className="w-full max-w-sm space-y-4" onSubmit={(e) => { e.preventDefault(); onLogin(role) }}>
          <h2 className="text-2xl font-semibold text-navy-900">Sign in</h2>
          <p className="text-sm text-slate-500">Demo login. Any credentials work; choose a role.</p>
          <div><label className="mb-1 block text-sm font-medium">Email</label><input className="input" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required /></div>
          <div><label className="mb-1 block text-sm font-medium">Password</label><input className="input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required /></div>
          <div>
            <label className="mb-1 block text-sm font-medium">Role</label>
            <div className="grid grid-cols-2 gap-2">
              {(['Admin', 'Officer'] as Role[]).map((r) => (
                <button type="button" key={r} onClick={() => setRole(r)} className={`rounded-lg border px-3 py-2 text-sm font-medium ${role === r ? 'border-navy-800 bg-navy-50 text-navy-800' : 'border-slate-300 text-slate-600'}`}>
                  {r === 'Admin' ? 'Admin / Official' : 'Case Officer'}
                </button>
              ))}
            </div>
          </div>
          <button className="btn w-full"><LogIn size={16} /> Sign in as {role}</button>
        </form>
      </div>
    </div>
  )
}
