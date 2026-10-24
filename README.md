# Abhigyan

**Integrated Complaint Monitoring and Status Dashboard**
SIH (Smart India Hackathon) Project — AICTE

A governance portal prototype for the All India Council for Technical Education (AICTE) to monitor, cross-reference, and adjudicate institution-related grievances across AICTE bureaus — specifically the Regulation Bureau (RB) and the Public Grievance Redressal Cell (PGRC).

> **Demonstration Notice:** All data, match scores, SLA thresholds, and resolution metrics in this prototype are simulated and do not represent verified AICTE policy, live records, or official government data.

---

## Key Capabilities

- **Cross-Bureau Overlap Detection:** Rule-based cross-referencing to identify duplicate or related complaints filed simultaneously across RB and PGRC for the same institution. Match scores are computed from keyword overlap, institution ID, and category intersection on simulated demo data.
- **Configurable SLA Surveillance:** Countdown tracker enforcing a configurable resolution window (default: 14 days in Settings). Overdue cases are highlighted with warning banners. The 14-day default is a demonstration value and not a verified statutory deadline.
- **Role Toggle (Admin / Officer):** Simulate different user perspectives between Central Admin (Dr. S. Mehta) and Case Officer (Rajesh Kumar) for demonstration purposes.
- **Complete Audit Trail:** Timestamped chronological timeline recording verification, bureau assignments, hearings, and officer notes for each case.
- **Institution Directory and Risk Profiles:** Campus registry showing complaint density, active case counts, and risk levels per institution.
- **Data Analytics and Visual Reporting:** Charts covering bureau distribution, priority severity, resolution status, and illustrative monthly trends (Recharts).

---

## Tech Stack

| Layer      | Technology                                |
|------------|-------------------------------------------|
| Framework  | React 18 (Vite 5)                         |
| Language   | TypeScript                                |
| Styling    | Tailwind CSS 3 (custom navy palette)      |
| Icons      | Lucide React                              |
| Charts     | Recharts                                  |
| Backend    | Planned — FastAPI + PostgreSQL (not yet implemented) |

---

## Running the Project

### Prerequisites

- Node.js v18 or later
- npm

### 1. Install dependencies

```bash
npm install
```

### 2. Start development server

```bash
npm run dev
```

The application will be available at `http://localhost:5173/`

### 3. Production build

```bash
npm run build
```

Output is placed in the `dist/` directory.

### 4. Preview production build

```bash
npm run preview
```

---

## Repository Structure

```
Abhigyan/
├── src/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── AppLayout.tsx      # Application shell and responsive layout
│   │   │   ├── Sidebar.tsx        # Navy sidebar with navigation and role toggle
│   │   │   └── TopBar.tsx         # Top bar with notifications and global search
│   │   ├── ComplaintTable.tsx     # Reusable sortable complaints table
│   │   └── ui.tsx                 # Shared design system (Card, Badge, Button, Modal, etc.)
│   ├── pages/
│   │   ├── Dashboard.tsx          # Executive dashboard with KPI metrics and charts
│   │   ├── Complaints.tsx         # All Complaints directory and Case Details view
│   │   ├── Institutions.tsx       # Institution registry and per-campus complaint history
│   │   ├── Overlaps.tsx           # Cross-bureau overlap detection and officer review
│   │   ├── CaseTracking.tsx       # Case lifecycle stepper and SLA countdown
│   │   ├── Reports.tsx            # Analytics and illustrative chart reports
│   │   ├── Notifications.tsx      # System notification feed
│   │   ├── UserManagement.tsx     # Officer roster and case assignment overview
│   │   └── Settings.tsx           # Configurable SLA thresholds and overlap sensitivity
│   ├── types.ts                   # Shared TypeScript interfaces (Complaint, Institution, Overlap, etc.)
│   ├── data.ts                    # Simulated demo data and helper functions
│   ├── App.tsx                    # Root component with state management and view router
│   ├── index.css                  # Tailwind base styles
│   └── main.tsx                   # React DOM entry point
├── index.html                     # HTML shell with Inter font
├── package.json                   # Project metadata and dependencies
├── tailwind.config.js             # Tailwind CSS theme extension (navy palette)
├── tsconfig.json                  # TypeScript configuration
└── vite.config.ts                 # Vite build configuration
```

---

## Core Workflow

The prototype demonstrates this officer workflow:

1. **Institution Directory** — Browse registered institutions, filter by state or type, and select a campus to view its full complaint history.
2. **Institution Profile** — See risk level, active vs resolved complaint counts, and the complaint dossier for the selected institution.
3. **Complaint Details** — Open a case file to read the full narrative, view the chronological audit trail, reassign the officer, change case status, and log investigation notes.
4. **Potential Overlap Review** — Navigate to the Overlap Detection page to review flagged complaint pairs, read the matching reasons, and decide to link cases or keep them as separate files. Officers must make this decision; no automatic merging or case closure occurs.
5. **Officer Decision** — All status changes, assignments, and overlap decisions are officer-initiated actions logged to the case timeline.
6. **Chronological Action History** — The full audit trail is visible in Case Details and the Case Tracking page.

---

## Design System

- **Sidebar:** Dark navy (`#0b2250`), active teal indicator (`#14b8a6`), collapsible
- **Main viewport:** Light grey (`bg-slate-50`), rounded white cards
- **Typography:** Inter (via system-ui fallback)
- **Bureaus:**
  - `RB` — Regulation Bureau
  - `PGRC` — Public Grievance Redressal Cell
  - `Approval` — Approval Bureau
  - `Academic` — Academic Bureau
  - `SB` — Skill Bureau
  - `EO` — Executive Office

---

## Planned Next Steps

- FastAPI backend with PostgreSQL for persistent case storage
- JWT-based authentication with role enforcement
- Real complaint intake form with file attachment support
- Officer workload assignment engine
