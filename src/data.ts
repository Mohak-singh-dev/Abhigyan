import type {
  Complaint,
  Institution,
  Overlap,
  Bureau,
  Priority,
  Status,
  AppNotification,
  UserProfile,
} from './types'

export const TODAY = '2026-10-25'
export const OFFICERS = ['Anita Verma', 'Rajesh Kumar', 'Meera Iyer', 'Suresh Patel', 'Dr. Arun Sharma']
export const CURRENT_OFFICER = 'Rajesh Kumar'
export const STATUSES: Status[] = ['Pending', 'In Progress', 'Escalated', 'Resolved']
export const BUREAUS: Bureau[] = ['RB', 'PGRC', 'Approval', 'Academic', 'SB', 'EO']

export const BUREAU_INFO: Record<Bureau, { name: string; desc: string; badgeClass: string }> = {
  RB: {
    name: 'Regulation Bureau (RB)',
    desc: 'Ensures compliance with AICTE regulatory norms, fee structures, and intake limits.',
    badgeClass: 'bg-indigo-50 text-indigo-700 border-indigo-200',
  },
  PGRC: {
    name: 'Public Grievance Redressal Cell (PGRC)',
    desc: 'Handles student, parent, and faculty complaints, mistreatment, and fee grievances.',
    badgeClass: 'bg-teal-50 text-teal-700 border-teal-200',
  },
  Approval: {
    name: 'Approval Bureau',
    desc: 'Manages institution approvals, extension of approvals (EoA), and infrastructure criteria.',
    badgeClass: 'bg-sky-50 text-sky-700 border-sky-200',
  },
  Academic: {
    name: 'Academic Bureau',
    desc: 'Oversees model curricula, faculty standards, academic calendar, and syllabus.',
    badgeClass: 'bg-purple-50 text-purple-700 border-purple-200',
  },
  SB: {
    name: 'Skill Bureau (SB)',
    desc: 'Coordinates vocational training, apprenticeships, and skill accreditation.',
    badgeClass: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  },
  EO: {
    name: 'Executive Office (EO)',
    desc: 'Deals with high-priority statutory oversight, legal inquiries, and ministry references.',
    badgeClass: 'bg-rose-50 text-rose-700 border-rose-200',
  },
}

export const institutions: Institution[] = [
  {
    id: 'i1',
    name: 'Sunrise Institute of Technology',
    city: 'Pune',
    state: 'Maharashtra',
    type: 'Engineering',
    aicteId: '1-4821039',
    approved: '2009',
    contactEmail: 'principal@sunrise-tech.edu.in',
    contactPhone: '+91 20 2748 9901',
    totalComplaints: 6,
    activeComplaints: 3,
    riskLevel: 'High',
  },
  {
    id: 'i2',
    name: 'Bharat College of Engineering',
    city: 'Lucknow',
    state: 'Uttar Pradesh',
    type: 'Engineering',
    aicteId: '1-3390412',
    approved: '2004',
    contactEmail: 'director@bharatengg.ac.in',
    contactPhone: '+91 522 289 1102',
    totalComplaints: 5,
    activeComplaints: 2,
    riskLevel: 'Moderate',
  },
  {
    id: 'i3',
    name: 'Vidya Polytechnic Institute',
    city: 'Jaipur',
    state: 'Rajasthan',
    type: 'Polytechnic',
    aicteId: '1-5120987',
    approved: '2012',
    contactEmail: 'admin@vidyapoly.edu.in',
    contactPhone: '+91 141 298 3341',
    totalComplaints: 4,
    activeComplaints: 1,
    riskLevel: 'Moderate',
  },
  {
    id: 'i4',
    name: 'National Institute of Management Studies',
    city: 'Bengaluru',
    state: 'Karnataka',
    type: 'Management',
    aicteId: '1-2784561',
    approved: '2001',
    contactEmail: 'registrar@nims-blr.ac.in',
    contactPhone: '+91 80 4123 7789',
    totalComplaints: 5,
    activeComplaints: 2,
    riskLevel: 'High',
  },
  {
    id: 'i5',
    name: 'Gyan Jyoti Institute of Pharmacy',
    city: 'Ghaziabad',
    state: 'Uttar Pradesh',
    type: 'Pharmacy',
    aicteId: '1-6045123',
    approved: '2015',
    contactEmail: 'info@gyanjyotipharma.org',
    contactPhone: '+91 120 488 2011',
    totalComplaints: 3,
    activeComplaints: 0,
    riskLevel: 'Low',
  },
  {
    id: 'i6',
    name: 'Himalaya Technical University',
    city: 'Dehradun',
    state: 'Uttarakhand',
    type: 'University',
    aicteId: '1-7210045',
    approved: '2018',
    contactEmail: 'vc-office@himalayatech.ac.in',
    contactPhone: '+91 135 277 8890',
    totalComplaints: 4,
    activeComplaints: 2,
    riskLevel: 'High',
  },
  {
    id: 'i7',
    name: 'Kalinga School of Architecture',
    city: 'Bhubaneswar',
    state: 'Odisha',
    type: 'Architecture',
    aicteId: '1-8930124',
    approved: '2011',
    contactEmail: 'dean@kalinga-arch.edu.in',
    contactPhone: '+91 674 233 4455',
    totalComplaints: 2,
    activeComplaints: 1,
    riskLevel: 'Low',
  },
]

const addDays = (d: string, n: number) => {
  const x = new Date(d)
  x.setDate(x.getDate() + n)
  return x.toISOString().slice(0, 10)
}

type RowData = [
  string, // id
  string, // instId
  Bureau, // bureau
  string, // category
  Priority, // priority
  string, // officer
  Status, // status
  string, // date
  string, // due
  string, // title
  string, // description
  'Student' | 'Faculty' | 'Parent' | 'Whistleblower' | 'General Public', // complainantType
]

const rawRows: RowData[] = [
  [
    'RB-2026-0141',
    'i1',
    'RB',
    'Fee Regulation',
    'Critical',
    'Anita Verma',
    'Pending',
    '2026-09-28',
    '2026-10-12',
    'Excess tuition fee collected above approved regulatory cap',
    'Parents allege the institute collects tuition roughly 40% above the fee approved by the state Fee Regulatory Committee, with no formal receipts issued for the additional amount.',
    'Parent',
  ],
  [
    'PGRC-2026-0873',
    'i1',
    'PGRC',
    'Fee Regulation',
    'High',
    'Rajesh Kumar',
    'In Progress',
    '2026-10-02',
    '2026-10-30',
    'Students report compulsory "development charges" exceeding fee norm',
    'A group of third-year B.Tech students submitted a formal grievance stating the 2026-27 fee notice exceeds the approved schedule by Rs 35,000 under mandatory development charges.',
    'Student',
  ],
  [
    'RB-2026-0152',
    'i2',
    'RB',
    'Faculty Norms',
    'High',
    'Meera Iyer',
    'In Progress',
    '2026-10-01',
    '2026-10-25',
    'Severe faculty shortage in Computer Science Department',
    'Whistleblower complaint with staff roster stating the CSE department operates at only 42% of required cadre ratio; ghost faculty signatures observed in biometric submissions.',
    'Whistleblower',
  ],
  [
    'PGRC-2026-0890',
    'i2',
    'PGRC',
    'Faculty Norms',
    'Medium',
    'Rajesh Kumar',
    'Pending',
    '2026-10-05',
    '2026-11-02',
    'Core subjects skipped due to unavailability of qualified faculty',
    'CSE 5th semester students petition that AI and Cloud Computing lab sessions have been stalled for over 6 weeks due to resignations not filled by the management.',
    'Student',
  ],
  [
    'AB-2026-0310',
    'i3',
    'Approval',
    'Infrastructure',
    'Medium',
    'Suresh Patel',
    'Resolved',
    '2026-08-14',
    '2026-09-14',
    'Laboratory machinery and licensed software shortfall',
    'Scrutiny committee found deficiencies in CAD software licenses and CNC machines versus declared figures. Institute has procured licenses and submitted compliance evidence.',
    'General Public',
  ],
  [
    'RB-2026-0166',
    'i3',
    'RB',
    'Infrastructure',
    'Critical',
    'Anita Verma',
    'Escalated',
    '2026-10-08',
    '2026-10-20',
    'Hostel fire safety non-compliance and overcrowding',
    'Municipal fire clearance was revoked in August 2026. The boys hostel houses 180 students beyond structural design limit with obstructed fire escape staircases.',
    'Whistleblower',
  ],
  [
    'PGRC-2026-0902',
    'i4',
    'PGRC',
    'Admission Irregularity',
    'High',
    'Rajesh Kumar',
    'Pending',
    '2026-10-10',
    '2026-11-05',
    'Direct MBA admissions bypassing centralised state counselling',
    'Candidate claims management demanded Rs 2.5 Lakh cash donation for an MBA seat outside the designated CAT/CMAT institutional round.',
    'Student',
  ],
  [
    'RB-2026-0171',
    'i4',
    'RB',
    'Admission Irregularity',
    'High',
    'Meera Iyer',
    'Pending',
    '2026-10-11',
    '2026-10-22',
    'Management quota seat intake exceeded sanctioned threshold',
    'Investigation referral that total sanctioned intake of 120 seats was breached, with 148 candidates enrolled in the 2026 MBA batch.',
    'Whistleblower',
  ],
  [
    'PGRC-2026-0915',
    'i5',
    'PGRC',
    'Certificate Delay',
    'Low',
    'Suresh Patel',
    'Resolved',
    '2026-09-20',
    '2026-10-10',
    'Withholding of B.Pharm provisional degree and migration documents',
    'Graduate was denied clearance certificates citing pending alumni association contribution. Notice served; institute has released all credentials.',
    'Student',
  ],
  [
    'ACD-2026-0044',
    'i5',
    'Academic',
    'Curriculum',
    'Low',
    'Meera Iyer',
    'Resolved',
    '2026-09-02',
    '2026-10-02',
    'Failure to implement AICTE Model Curriculum 2024 revision',
    'Faculty complaint that college continues teaching outdated 2019 syllabus ignoring PCI and AICTE revised elective modules. Syllabus alignment verified.',
    'Faculty',
  ],
  [
    'RB-2026-0180',
    'i6',
    'RB',
    'Unapproved Courses',
    'Critical',
    'Anita Verma',
    'In Progress',
    '2026-10-15',
    '2026-10-28',
    'Operating unapproved M.Tech in Data Science & Cyber Security',
    'Admissions enrolled 45 candidates for an M.Tech program without obtaining approval in the current approval process handbook cycle.',
    'Whistleblower',
  ],
  [
    'PGRC-2026-0921',
    'i6',
    'PGRC',
    'Unapproved Courses',
    'High',
    'Rajesh Kumar',
    'In Progress',
    '2026-10-16',
    '2026-11-08',
    'Enrolled students demand refund and transfer for unapproved degree',
    'Students discovered their course is not listed on the AICTE portal and petitioned PGRC for immediate refund of first semester tuition and migration assistance.',
    'Student',
  ],
  [
    'PGRC-2026-0930',
    'i2',
    'PGRC',
    'Harassment & Ragging',
    'Critical',
    'Dr. Arun Sharma',
    'Escalated',
    '2026-10-18',
    '2026-10-23',
    'Failure of Institutional Anti-Ragging Committee to respond to complaint',
    'First-year student submitted police report extract alleging systemic harassment in hostel block 3 without action by the college anti-ragging squad.',
    'Student',
  ],
  [
    'AB-2026-0322',
    'i1',
    'Approval',
    'Infrastructure',
    'Low',
    'Rajesh Kumar',
    'Pending',
    '2026-10-19',
    '2026-11-12',
    'Library digital access and volume count below mandatory norm',
    'Complaint notes e-journal subscriptions expired in June and reading hall area does not meet 400 sq. meter requirement.',
    'Faculty',
  ],
  [
    'SB-2026-0051',
    'i7',
    'SB',
    'Skill Certification',
    'Medium',
    'Anita Verma',
    'In Progress',
    '2026-10-14',
    '2026-11-04',
    'B.Des interior design apprenticeship stipend deduction grievance',
    'Trainees under the NEAT initiative report unauthorized deduction of 30% from the mandated monthly government stipend.',
    'Student',
  ],
]

export const initialComplaints: Complaint[] = rawRows.map(
  ([id, institutionId, bureau, category, priority, officer, status, date, due, title, description, complainantType]) => {
    const timeline: import('./types').TimelineEvent[] = [
      { label: 'Complaint registered and verified on AICTE portal', date, by: 'System / Portal' },
      { label: `Assigned to ${officer} (${bureau} Bureau)`, date: addDays(date, 1), by: 'Admin (Dr. S. Mehta)' },
    ]
    if (status !== 'Pending') {
      timeline.push({
        label: status === 'Resolved' ? 'Investigation complete & Marked Resolved' : `Case status updated to ${status}`,
        date: addDays(date, 3),
        by: officer,
        note: status === 'Escalated' ? 'Escalated to Bureau Head due to SLA breach and severity.' : undefined,
      })
    }
    return {
      id,
      institutionId,
      bureau,
      category,
      priority,
      officer,
      status,
      date,
      due,
      title,
      description,
      complainantType,
      attachmentsCount: Math.floor(Math.random() * 3) + 1,
      timeline,
      assignments: [{ officer, date: addDays(date, 1), by: 'Admin (Dr. S. Mehta)' }],
    }
  }
)

export const overlaps: Overlap[] = [
  {
    id: 'o1',
    a: 'RB-2026-0141',
    b: 'PGRC-2026-0873',
    similarity: 94,
    reasons: [
      'Same Institution: Sunrise Institute of Technology (Pune)',
      'Both complaints cite excessive tuition fee demands and unapproved development levies',
      'Both submitted within 4 calendar days of each other',
      'Matching keywords: "tuition fee", "approved fee cap", "development charges"',
    ],
    status: 'pending',
    notes: 'Recommend joint inquiry by RB and PGRC to issue a consolidated show-cause notice.',
  },
  {
    id: 'o2',
    a: 'RB-2026-0152',
    b: 'PGRC-2026-0890',
    similarity: 88,
    reasons: [
      'Same Institution: Bharat College of Engineering (Lucknow)',
      'Shared Department: Computer Science & Engineering (CSE)',
      'RB complaint concerns faculty roster/cadre shortfall; PGRC complaint details stalled lab lectures caused by that exact vacancy',
      'Direct causal link between regulatory non-compliance and student grievance',
    ],
    status: 'linked',
    notes: 'Linked as Case Track #CT-2026-88. Inquiry officer assigned to verify biometric records.',
  },
  {
    id: 'o3',
    a: 'RB-2026-0171',
    b: 'PGRC-2026-0902',
    similarity: 91,
    reasons: [
      'Same Institution: National Institute of Management Studies (Bengaluru)',
      'Shared Category: Admission Irregularities in MBA program',
      'Matching evidence: Unapproved intake extension coincides with direct donation demands',
      'Filed within 24 hours of each other',
    ],
    status: 'pending',
    notes: 'Urgent overlap: Possible unauthorised admissions racket.',
  },
  {
    id: 'o4',
    a: 'RB-2026-0180',
    b: 'PGRC-2026-0921',
    similarity: 92,
    reasons: [
      'Same Institution: Himalaya Technical University (Dehradun)',
      'Identical course: M.Tech in Data Science & Cyber Security',
      'RB filed by staff whistleblower regarding lack of approval; PGRC filed by enrolled students demanding fee refund',
      'Critical risk: Degrees at jeopardy for 45 students',
    ],
    status: 'linked',
    notes: 'Consolidated into single hearing committee scheduled for 28-Oct-2026.',
  },
  {
    id: 'o5',
    a: 'RB-2026-0141',
    b: 'AB-2026-0322',
    similarity: 52,
    reasons: [
      'Same Institution: Sunrise Institute of Technology',
      'Different subject matter: Tuition fee vs library infrastructure criteria',
      'May indicate overall institutional governance stress',
    ],
    status: 'dismissed',
    notes: 'Different bureaus and unrelated topics; kept as separate case files.',
  },
]

export const initialNotifications: AppNotification[] = [
  {
    id: 'notif-1',
    type: 'alert',
    title: 'High-Risk Overlap Flagged (94% Match)',
    message: 'AICTE CaseTrack detected overlapping fee complaints for Sunrise Institute of Technology in RB and PGRC.',
    timestamp: '2026-10-24 16:30',
    caseId: 'RB-2026-0141',
    read: false,
  },
  {
    id: 'notif-2',
    type: 'warning',
    title: 'SLA Alert: Case RB-2026-0141 Overdue',
    message:
      'Case RB-2026-0141 has exceeded the configured 14-day resolution window (demonstration threshold) by 13 days.',
    timestamp: '2026-10-24 11:15',
    caseId: 'RB-2026-0141',
    read: false,
  },
  {
    id: 'notif-3',
    type: 'alert',
    title: 'Escalation: Anti-Ragging Cell Intervention',
    message: 'Case PGRC-2026-0930 at Bharat College of Engineering escalated directly to Bureau Head.',
    timestamp: '2026-10-23 18:45',
    caseId: 'PGRC-2026-0930',
    read: false,
  },
  {
    id: 'notif-4',
    type: 'success',
    title: 'Compliance Verified: Lab shortfalls rectified',
    message: 'Institution Vidya Polytechnic submitted verified receipts and licenses for AB-2026-0310.',
    timestamp: '2026-10-22 14:10',
    caseId: 'AB-2026-0310',
    read: true,
  },
  {
    id: 'notif-5',
    type: 'info',
    title: 'Monthly SIH Bureau Performance Report Generated',
    message: 'October 2026 complaint resolution analytics now compiled across RB, PGRC, Approval, and Academic bureaus.',
    timestamp: '2026-10-21 09:00',
    read: true,
  },
]

export const userProfiles: UserProfile[] = [
  {
    id: 'u1',
    name: 'Dr. S. Mehta',
    email: 'member-sec@aicte-india.org',
    role: 'Admin',
    designation: 'Member Secretary & Central Admin',
    bureau: 'All',
    avatarText: 'SM',
    phone: '+91 11 2958 1000',
    activeCasesCount: 15,
    status: 'Active',
  },
  {
    id: 'u2',
    name: 'Rajesh Kumar',
    email: 'rajesh.kumar@aicte-india.org',
    role: 'Officer',
    designation: 'Senior Grievance Officer, PGRC',
    bureau: 'PGRC',
    avatarText: 'RK',
    phone: '+91 11 2958 1042',
    activeCasesCount: 5,
    status: 'Active',
  },
  {
    id: 'u3',
    name: 'Anita Verma',
    email: 'anita.verma@aicte-india.org',
    role: 'Officer',
    designation: 'Director & Bureau Chief, RB',
    bureau: 'RB',
    avatarText: 'AV',
    phone: '+91 11 2958 1077',
    activeCasesCount: 4,
    status: 'Active',
  },
  {
    id: 'u4',
    name: 'Meera Iyer',
    email: 'meera.iyer@aicte-india.org',
    role: 'Officer',
    designation: 'Legal Counsel & Officer, RB / Academic',
    bureau: 'RB',
    avatarText: 'MI',
    phone: '+91 11 2958 1091',
    activeCasesCount: 3,
    status: 'Active',
  },
  {
    id: 'u5',
    name: 'Suresh Patel',
    email: 'suresh.patel@aicte-india.org',
    role: 'Officer',
    designation: 'Scrutiny Officer, Approval Bureau',
    bureau: 'Approval',
    avatarText: 'SP',
    phone: '+91 11 2958 1115',
    activeCasesCount: 2,
    status: 'Active',
  },
  {
    id: 'u6',
    name: 'Dr. Arun Sharma',
    email: 'arun.sharma@aicte-india.org',
    role: 'Officer',
    designation: 'Special Inquiries Officer, PGRC',
    bureau: 'PGRC',
    avatarText: 'AS',
    phone: '+91 11 2958 1130',
    activeCasesCount: 1,
    status: 'Active',
  },
]

// Helper functions
export const fmt = (d: string) => {
  try {
    const parts = d.split('-')
    if (parts.length === 3) {
      const year = parts[0]
      const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
      const month = monthNames[parseInt(parts[1], 10) - 1] || parts[1]
      const day = parts[2]
      return `${day} ${month} ${year}`
    }
    return d
  } catch {
    return d
  }
}

export const instName = (id: string) => institutions.find((i) => i.id === id)?.name ?? 'Unknown Institute'
export const getInstitution = (id: string) => institutions.find((i) => i.id === id)

export const isOverdue = (c: Complaint) => {
  if (c.status === 'Resolved') return false
  return c.due < TODAY
}

export const getDaysRemaining = (due: string) => {
  const target = new Date(due).getTime()
  const current = new Date(TODAY).getTime()
  const diffDays = Math.round((target - current) / (1000 * 3600 * 24))
  return diffDays
}
