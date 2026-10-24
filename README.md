# AICTE CaseTrack
### Integrated Complaint Monitoring & Status Dashboard (SIH Project)

A specialized governance portal engineered for the **All India Council for Technical Education (AICTE)** to monitor, cross-reference, and adjudicate institution-related grievances across AICTE bureaus and cells—specifically highlighting **Regulation Bureau (RB)** and the **Public Grievance Redressal Cell (PGRC)**.

---

## 🏛️ Key Capabilities

- **Cross-Bureau Overlap Detection**: Algorithmically identifies duplicate or related complaints filed simultaneously across RB and PGRC for the same technical institution, displaying matching confidence scores (up to 94%) and corroborating evidence points.
- **Statutory SLA Surveillance**: Automated countdown tracker enforcing the 14-day statutory resolution window under AICTE Grievance Regulations, flagging overdue cases with warning banners.
- **Executive & Case Officer Perspectives**: Seamless role toggle between **Central Admin (Dr. S. Mehta)** and **Grievance Officer (Rajesh Kumar)**.
- **Complete Institutional Audit Trail**: Timestamped chronological timeline recording verification, bureau transfers, hearings, and compliance releases.
- **Institution Directory & Risk Profiles**: Campus registry profiling complaint density, approved intake flags, and affiliation history.
- **Data Analytics & Visual Reporting**: Real-time charts covering bureau distribution, severity categorization, resolution throughput, and monthly trends.

---

## 🚀 Running the Project

### Prerequisites
- Node.js (v18+ recommended)
- npm or yarn

### 1. Installation
```bash
npm install
```

### 2. Start Development Server
```bash
npm run dev
```
The application will launch at: **`http://localhost:5173/`**

### 3. Production Build
```bash
npm run build
```

---

## 📁 Repository Structure

```
AICTE_CASE_TRACK/
├── src/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── AppLayout.tsx      # Core application shell & responsive container
│   │   │   ├── Sidebar.tsx        # Dark navy (#0b2250) navigation with bureau badges & role toggle
│   │   │   └── TopBar.tsx         # Header with global search, notification dropdown, and officer profile
│   │   ├── ComplaintTable.tsx     # Reusable, sortable government-grade complaints table
│   │   └── ui.tsx                 # Design system (Cards, Badges, Stats, Buttons, Modals, Search)
│   ├── pages/
│   │   ├── Dashboard.tsx          # Executive dashboard with KPI metrics & bureau charts
│   │   ├── Complaints.tsx         # All Complaints directory + comprehensive Case File Details view
│   │   ├── Institutions.tsx       # Institutional registry & campus complaint dossier
│   │   ├── Overlaps.tsx           # Cross-bureau duplicate detection with side-by-side comparison
│   │   ├── CaseTracking.tsx       # Live SLA milestone tracker & statutory progress monitor
│   │   ├── Reports.tsx            # Data analytics & visual charts (Recharts)
│   │   ├── Notifications.tsx      # System notification feed & breach alert center
│   │   ├── UserManagement.tsx     # Bureau officer registry, assignment tracker & personnel roster
│   │   └── Settings.tsx           # Overlap similarity threshold & statutory SLA settings
│   ├── types.ts                   # TypeScript interfaces (Complaint, Institution, Overlap, etc.)
│   ├── data.ts                    # Realistic domain-specific demo data for AICTE SIH
│   ├── App.tsx                    # Root component with local state & view router
│   ├── index.css                  # Tailwind styles & custom government scrollbars
│   └── main.tsx                   # React DOM entry point
├── index.html                     # HTML5 shell with Inter typography & government branding
├── package.json                   # Dependencies (React 18, Vite 5, Tailwind CSS 3, Lucide, Recharts)
├── tailwind.config.js             # Navy palette & theme extension
├── tsconfig.json                  # TypeScript bundler compiler configuration
└── vite.config.ts                 # Vite development & build configuration
```

---

## 🎨 Design System Specifications

- **Sidebar**: Dark Navy (`#0b2250`), subtle borders (`border-white/10`), active teal indicator (`#14b8a6`), collapsible toggle.
- **Main Viewport**: Light grey background (`#f8fafc` / `bg-slate-50`), rounded cards (`rounded-xl border border-slate-200/80`), subtle elevations.
- **Typography**: Inter / system-ui clean government type with clear hierarchy.
- **Bureaus Highlighted**:
  - `RB` — Regulation Bureau
  - `PGRC` — Public Grievance Redressal Cell
  - `Approval` — Approval Bureau
  - `Academic` — Academic Bureau
  - `SB` — Skill Bureau
  - `EO` — Executive Office
