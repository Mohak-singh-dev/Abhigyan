import test from 'node:test'
import assert from 'node:assert/strict'
import {
  canAssignCase,
  canUpdateCaseStatus,
  canViewComplaint,
  resolveOfficerName,
  userProfiles,
  PERMITTED_STATUS_TRANSITIONS,
} from '../../data.ts'

test('Bug 1 Regression: Handling officer reassignment persistence and name resolution', async (t) => {
  const officerRajesh = {
    id: 'u2',
    name: 'Rajesh Kumar',
    email: 'rajesh.kumar@aicte-india.org',
    role: 'Officer',
    designation: 'Senior Grievance Officer, PGRC',
    bureau: 'PGRC',
  }

  const officerAnita = {
    id: 'u3',
    name: 'Anita Verma',
    email: 'anita.verma@aicte-india.org',
    role: 'Officer',
    designation: 'Director & Bureau Chief, RB',
    bureau: 'RB',
  }

  const bureauAdminPriya = {
    id: 'u1b',
    name: 'Dr. Priya Nair',
    email: 'priya.nair@aicte-india.org',
    role: 'BureauAdmin',
    designation: 'Bureau Chief, PGRC',
    bureau: 'PGRC',
  }

  const systemAdminMehta = {
    id: 'u1',
    name: 'Dr. S. Mehta',
    email: 'member-sec@aicte-india.org',
    role: 'Admin',
    designation: 'Member Secretary & System Admin',
    bureau: 'All',
  }

  // Initial complaints list
  let complaints = [
    {
      id: 'PGRC-2026-0873',
      bureau: 'PGRC',
      category: 'Fee Regulation',
      priority: 'High',
      officer: 'Rajesh Kumar',
      assignedUserId: 'u2',
      status: 'In Progress',
      title: 'Compulsory development charges exceeding norm',
      complainantEmail: 'rohit.sharma@student.edu.in',
      timeline: [
        {
          id: 1,
          label: 'Initial assignment to Rajesh Kumar',
          by: 'Dr. S. Mehta (Admin)',
          role: 'Admin',
          note: 'Allocated to PGRC.',
        },
      ],
      assignments: [
        {
          officer: 'Rajesh Kumar',
          by: 'Dr. S. Mehta',
          byRole: 'Admin',
          bureau: 'PGRC',
          type: 'initial',
        },
      ],
    },
    {
      id: 'RB-2026-0141',
      bureau: 'RB',
      category: 'Fee Regulation',
      priority: 'Critical',
      officer: 'Anita Verma',
      assignedUserId: 'u3',
      status: 'Pending',
      title: 'Excess tuition fee collected above approved regulatory cap',
      complainantEmail: 'citizen.grievance@aicte-portal.in',
      timeline: [],
      assignments: [],
    },
  ]

  await t.test('1. Authorization checks enforce that Officers cannot assign cases, while Admin and Bureau Admin can', () => {
    const targetCase = complaints[0]

    // Officer cannot assign
    const officerCheck = canAssignCase(officerRajesh, targetCase)
    assert.equal(officerCheck.allowed, false, 'Officers must NOT be permitted to assign/reassign cases')

    // Bureau Admin for PGRC can assign PGRC case
    const pgrcAdminCheck = canAssignCase(bureauAdminPriya, targetCase)
    assert.equal(pgrcAdminCheck.allowed, true, 'Bureau Admin can assign cases within authorized Bureau')

    // Bureau Admin cannot assign case from another Bureau
    const rbCase = complaints[1]
    const crossBureauCheck = canAssignCase(bureauAdminPriya, rbCase)
    assert.equal(crossBureauCheck.allowed, false, 'Bureau Admin cannot assign cases outside their Bureau')

    // System Admin has system-wide assignment authority
    const adminCheck = canAssignCase(systemAdminMehta, targetCase)
    assert.equal(adminCheck.allowed, true, 'System Admin can assign any case')
    const adminRbCheck = canAssignCase(systemAdminMehta, rbCase)
    assert.equal(adminRbCheck.allowed, true, 'System Admin can assign RB case')
  })

  await t.test('2. Reassigning a case to Anita Verma displays her real name instead of "Reassigned Officer"', async () => {
    const targetCaseId = 'PGRC-2026-0873'
    const newOfficerUser = userProfiles.find((u) => u.name === 'Anita Verma')
    assert.ok(newOfficerUser, 'Anita Verma must exist in AICTE user registry with stable ID')
    assert.equal(newOfficerUser.id, 'u3', 'Anita Verma stable user ID is u3')

    // Simulate backend assignment response from FastAPI
    const backendResponse = {
      id: targetCaseId,
      officer: newOfficerUser.name,
      assignedUserId: newOfficerUser.id,
      bureau: 'PGRC',
      timeline: [
        ...complaints[0].timeline,
        {
          id: 2,
          label: `Investigating officer reassigned from Rajesh Kumar to ${newOfficerUser.name}`,
          by: `${systemAdminMehta.name} (${systemAdminMehta.role})`,
          role: systemAdminMehta.role,
          note: 'Administrative reassignment within AICTE.',
        },
      ],
    }

    // Apply the backend response using resolveOfficerName
    const resolvedName = resolveOfficerName(backendResponse, userProfiles)
    assert.equal(resolvedName, 'Anita Verma', 'Resolved officer name must be Anita Verma')
    assert.notEqual(resolvedName, 'Reassigned Officer', 'Must NOT display generic Reassigned Officer fallback')

    complaints = complaints.map((c) => {
      if (c.id === targetCaseId) {
        return {
          ...c,
          officer: resolvedName,
          assignedUserId: backendResponse.assignedUserId,
          timeline: backendResponse.timeline,
        }
      }
      return c
    })

    const updatedCase = complaints.find((c) => c.id === targetCaseId)
    assert.equal(updatedCase?.officer, 'Anita Verma')
    assert.equal(updatedCase?.assignedUserId, 'u3')

    // Even if local storage or state had "Reassigned Officer", resolveOfficerName recovers "Anita Verma" via assignedUserId
    const corruptedCase = {
      ...updatedCase,
      officer: 'Reassigned Officer',
      assignedUserId: 'u3',
    }
    const recoveredName = resolveOfficerName(corruptedCase, userProfiles)
    assert.equal(recoveredName, 'Anita Verma', 'Must resolve real officer name from authoritative profile using assignedUserId')
  })

  await t.test('3. The old officer loses access and the new officer sees the case after a fresh server sync', () => {
    const targetCaseId = 'PGRC-2026-0873'
    const updatedCase = complaints.find((c) => c.id === targetCaseId)
    assert.ok(updatedCase)

    // Old officer Rajesh Kumar loses access
    const rajeshAccess = canViewComplaint(officerRajesh, updatedCase)
    assert.equal(rajeshAccess.allowed, false, 'Old officer Rajesh Kumar is forbidden from viewing the reassigned case')

    const rajeshWorklist = complaints.filter(
      (c) =>
        c.officer === officerRajesh.name ||
        resolveOfficerName(c) === officerRajesh.name ||
        c.assignedUserId === officerRajesh.id
    )
    assert.equal(
      rajeshWorklist.some((c) => c.id === targetCaseId),
      false,
      'Old officer worklist does not contain the reassigned case'
    )

    // New officer Anita Verma sees the case
    const anitaAccess = canViewComplaint(officerAnita, updatedCase)
    assert.equal(anitaAccess.allowed, true, 'New officer Anita Verma is permitted to view the assigned case')

    const anitaWorklist = complaints.filter(
      (c) =>
        c.officer === officerAnita.name ||
        resolveOfficerName(c) === officerAnita.name ||
        c.assignedUserId === officerAnita.id
    )
    assert.equal(
      anitaWorklist.some((c) => c.id === targetCaseId),
      true,
      'New officer Anita Verma sees the assigned case in her worklist'
    )

    // Simulate fresh server sync for Officer Rajesh Kumar (server only returns his cases)
    const serverItemsForRajesh = [
      {
        id: 'PGRC-2026-9999',
        officer: 'Rajesh Kumar',
        assignedUserId: 'u2',
        bureau: 'PGRC',
      },
    ]

    const staleLocalComplaints = [
      {
        id: 'PGRC-2026-0873',
        officer: 'Rajesh Kumar', // Stale in Rajesh's local storage
        assignedUserId: 'u2',
        bureau: 'PGRC',
      },
      {
        id: 'PGRC-2026-9999',
        officer: 'Rajesh Kumar',
        assignedUserId: 'u2',
        bureau: 'PGRC',
      },
    ]

    const serverIds = new Set(serverItemsForRajesh.map((s) => s.id))
    const syncedComplaints = staleLocalComplaints.map((local) => {
      const remote = serverItemsForRajesh.find((s) => s.id === local.id)
      if (remote) {
        return {
          ...local,
          ...remote,
          officer: resolveOfficerName(remote, userProfiles),
        }
      }
      if (
        officerRajesh.role === 'Officer' &&
        (local.officer === officerRajesh.name || local.assignedUserId === officerRajesh.id) &&
        !serverIds.has(local.id)
      ) {
        return {
          ...local,
          officer: 'Unassigned',
          assignedUserId: undefined,
        }
      }
      return local
    })

    const reassignedAfterSync = syncedComplaints.find((c) => c.id === 'PGRC-2026-0873')
    assert.equal(reassignedAfterSync?.officer, 'Unassigned', 'Old officer local copy marked Unassigned after sync')
    assert.equal(reassignedAfterSync?.assignedUserId, undefined, 'assignedUserId cleared for old officer')
    assert.notEqual(reassignedAfterSync?.officer, 'Reassigned Officer', 'Must NOT use Reassigned Officer')
  })

  await t.test('4. Unknown or missing assigned-user IDs are handled safely', () => {
    // 1. Missing assigned-user ID and missing officer string
    const completelyUnassigned = {
      id: 'TEST-001',
      bureau: 'PGRC',
    }
    assert.equal(
      resolveOfficerName(completelyUnassigned, userProfiles),
      'Unassigned',
      'Missing assigned user ID and officer string resolves to safe neutral fallback "Unassigned"'
    )

    // 2. Unresolved non-existent user ID
    const unknownUserIdCase = {
      id: 'TEST-002',
      assignedUserId: 'u9999_non_existent',
      bureau: 'RB',
    }
    assert.equal(
      resolveOfficerName(unknownUserIdCase, userProfiles),
      'Unknown Officer',
      'Unresolvable assignedUserId resolves to safe neutral fallback "Unknown Officer"'
    )

    // 3. Stale "Reassigned Officer" string with unresolvable assignedUserId
    const corruptedCase = {
      id: 'TEST-003',
      officer: 'Reassigned Officer',
      assignedUserId: 'u_invalid_404',
      bureau: 'Approval',
    }
    assert.equal(
      resolveOfficerName(corruptedCase, userProfiles),
      'Unknown Officer',
      'Corrupted case with invalid user ID resolves to "Unknown Officer", never "Reassigned Officer"'
    )

    // 4. Stale "Reassigned Officer" string with no assignedUserId
    const corruptedWithoutId = {
      id: 'TEST-004',
      officer: 'Reassigned Officer',
      bureau: 'Approval',
    }
    assert.equal(
      resolveOfficerName(corruptedWithoutId, userProfiles),
      'Unassigned',
      'Corrupted case without user ID resolves to safe fallback "Unassigned", never "Reassigned Officer"'
    )

    // 5. Valid assignedUserId matches authoritative user profile
    const validOfficerCase = {
      id: 'TEST-005',
      assignedUserId: 'u2',
      officer: 'Reassigned Officer', // stale string in local storage
    }
    assert.equal(
      resolveOfficerName(validOfficerCase, userProfiles),
      'Rajesh Kumar',
      'Resolves authoritative officer name from user ID even if officer string was corrupted'
    )
  })
})

test('Phase 1 Regression: Status transition rules, permitted workflows, and System Admin overrides', async (t) => {
  const adminUser = {
    id: 'u1',
    name: 'Dr. S. Mehta',
    role: 'Admin',
    designation: 'Member Secretary & System Admin',
    bureau: 'All',
  }

  const pgrcAdmin = {
    id: 'u1b',
    name: 'Dr. Priya Nair',
    role: 'BureauAdmin',
    designation: 'Bureau Chief, PGRC',
    bureau: 'PGRC',
  }

  const pgrcOfficer = {
    id: 'u2',
    name: 'Rajesh Kumar',
    role: 'Officer',
    designation: 'Senior Grievance Officer, PGRC',
    bureau: 'PGRC',
  }

  const otherOfficer = {
    id: 'u3',
    name: 'Anita Verma',
    role: 'Officer',
    designation: 'Director, RB',
    bureau: 'RB',
  }

  const complainantUser = {
    id: 'u0',
    name: 'Rohit Sharma',
    role: 'Complainant',
    designation: 'Student',
    bureau: 'PGRC',
  }

  const pendingCase = {
    id: 'PGRC-2026-0001',
    bureau: 'PGRC',
    officer: 'Rajesh Kumar',
    assignedUserId: 'u2',
    status: 'Pending',
    title: 'Pending inquiry test case',
  }

  const inProgressCase = {
    id: 'PGRC-2026-0002',
    bureau: 'PGRC',
    officer: 'Rajesh Kumar',
    assignedUserId: 'u2',
    status: 'In Progress',
    title: 'In Progress inquiry test case',
  }

  const resolvedCase = {
    id: 'PGRC-2026-0003',
    bureau: 'PGRC',
    officer: 'Rajesh Kumar',
    assignedUserId: 'u2',
    status: 'Resolved',
    title: 'Closed case test',
  }

  const rbCase = {
    id: 'RB-2026-0004',
    bureau: 'RB',
    officer: 'Anita Verma',
    assignedUserId: 'u3',
    status: 'Pending',
    title: 'RB Bureau case test',
  }

  await t.test('1. Transitioning to same status is rejected for all roles', () => {
    assert.equal(canUpdateCaseStatus(adminUser, pendingCase, 'Pending').allowed, false)
    assert.equal(canUpdateCaseStatus(pgrcAdmin, pendingCase, 'Pending').allowed, false)
    assert.equal(canUpdateCaseStatus(pgrcOfficer, pendingCase, 'Pending').allowed, false)
  })

  await t.test('2. Complainants cannot modify case status', () => {
    assert.equal(canUpdateCaseStatus(complainantUser, pendingCase, 'In Progress').allowed, false)
  })

  await t.test('3. Officers can only update assigned cases within permitted transitions', () => {
    // Assigned officer advancing Pending -> In Progress (permitted)
    const validOfficerTransition = canUpdateCaseStatus(pgrcOfficer, pendingCase, 'In Progress')
    assert.equal(validOfficerTransition.allowed, true)

    // Assigned officer attempting Pending -> Resolved (illegal skip)
    const invalidSkip = canUpdateCaseStatus(pgrcOfficer, pendingCase, 'Resolved')
    assert.equal(invalidSkip.allowed, false)

    // Unassigned officer attempting to update case
    const unassignedAttempt = canUpdateCaseStatus(otherOfficer, pendingCase, 'In Progress')
    assert.equal(unassignedAttempt.allowed, false)

    // Officer attempting to reopen Resolved case
    const reopenAttempt = canUpdateCaseStatus(pgrcOfficer, resolvedCase, 'In Progress')
    assert.equal(reopenAttempt.allowed, false)
  })

  await t.test('4. Bureau Admin is strictly bound by jurisdiction and normal workflow rules', () => {
    // Permitted transition in jurisdiction
    const validPgrc = canUpdateCaseStatus(pgrcAdmin, inProgressCase, 'Resolved')
    assert.equal(validPgrc.allowed, true)

    // Cross-bureau case rejected
    const crossBureau = canUpdateCaseStatus(pgrcAdmin, rbCase, 'In Progress')
    assert.equal(crossBureau.allowed, false)
    assert.match(crossBureau.reason || '', /jurisdiction/i)

    // Bureau Admin cannot reopen Resolved case
    const adminReopen = canUpdateCaseStatus(pgrcAdmin, resolvedCase, 'In Progress')
    assert.equal(adminReopen.allowed, false)
  })

  await t.test('5. System Admin must follow permitted transitions UNLESS explicit overrideReason is provided', () => {
    // Normal permitted transition without overrideReason succeeds
    const normalAdmin = canUpdateCaseStatus(adminUser, pendingCase, 'In Progress')
    assert.equal(normalAdmin.allowed, true)

    // Non-permitted transition (Pending -> Resolved) WITHOUT overrideReason is rejected
    const unreasonedSkip = canUpdateCaseStatus(adminUser, pendingCase, 'Resolved')
    assert.equal(unreasonedSkip.allowed, false)
    assert.match(unreasonedSkip.reason || '', /override/i)

    // Non-permitted transition WITH blank overrideReason is rejected
    const blankReason = canUpdateCaseStatus(adminUser, pendingCase, 'Resolved', '   ')
    assert.equal(blankReason.allowed, false)

    // Non-permitted transition WITH valid overrideReason succeeds
    const validOverride = canUpdateCaseStatus(
      adminUser,
      pendingCase,
      'Resolved',
      'Special High Court order HC-8820: Case resolved summarily'
    )
    assert.equal(validOverride.allowed, true)

    // Reopening Resolved case WITHOUT overrideReason is rejected
    const unreasonedReopen = canUpdateCaseStatus(adminUser, resolvedCase, 'In Progress')
    assert.equal(unreasonedReopen.allowed, false)

    // Reopening Resolved case WITH valid overrideReason succeeds
    const validReopen = canUpdateCaseStatus(
      adminUser,
      resolvedCase,
      'In Progress',
      'Reopened pursuant to appellate tribunal review'
    )
    assert.equal(validReopen.allowed, true)
  })
})

test('Phase 1 Regression: Bureau preservation during ordinary reassignment vs cross-bureau transfer', async (t) => {
  const originalCase = {
    id: 'PGRC-2026-0873',
    bureau: 'PGRC',
    officer: 'Rajesh Kumar',
    assignedUserId: 'u2',
    status: 'In Progress',
    assignments: [
      {
        officer: 'Rajesh Kumar',
        bureau: 'PGRC',
        type: 'initial',
      },
    ],
    timeline: [],
  }

  await t.test('1. Ordinary reassignment preserves the complaint bureau regardless of target officer home bureau', () => {
    // Officer Anita Verma has home bureau RB, but complaint is PGRC
    const targetOfficer = {
      id: 'u3',
      name: 'Anita Verma',
      bureau: 'RB',
    }

    // When preserveBureau is active (ordinary reassignment)
    const ordinaryReassignment = {
      ...originalCase,
      officer: targetOfficer.name,
      assignedUserId: targetOfficer.id,
      bureau: originalCase.bureau, // Kept as PGRC!
      assignments: [
        ...originalCase.assignments,
        {
          officer: targetOfficer.name,
          previousOfficer: originalCase.officer,
          bureau: originalCase.bureau, // Stays PGRC
          type: 'reassignment',
        },
      ],
    }

    assert.equal(ordinaryReassignment.bureau, 'PGRC', 'Bureau MUST remain PGRC during ordinary officer reassignment')
    assert.equal(ordinaryReassignment.officer, 'Anita Verma')
    assert.equal(ordinaryReassignment.assignedUserId, 'u3')
    assert.equal(ordinaryReassignment.assignments[1].bureau, 'PGRC')
    assert.equal(ordinaryReassignment.assignments[1].type, 'reassignment')
  })

  await t.test('2. Cross-bureau transfer explicitly mutates bureau and records transfer audit entry', () => {
    const crossBureauTransfer = {
      ...originalCase,
      bureau: 'RB',
      officer: 'Anita Verma',
      assignedUserId: 'u3',
      assignments: [
        ...originalCase.assignments,
        {
          officer: 'Anita Verma',
          previousOfficer: originalCase.officer,
          bureau: 'RB',
          previousBureau: originalCase.bureau,
          type: 'transfer',
          reason: 'Subject matter pertains to Regulation Bureau statutory remit',
        },
      ],
      timeline: [
        {
          label: `Cross-Bureau Transfer: Jurisdiction transferred from PGRC to RB`,
          by: 'Dr. S. Mehta (Admin)',
          role: 'Admin',
          note: 'Statutory Transfer Reason: Subject matter pertains to Regulation Bureau statutory remit. Designated officer: Anita Verma.',
        },
      ],
    }

    assert.equal(crossBureauTransfer.bureau, 'RB', 'Bureau changes to RB on explicit transfer')
    assert.equal(crossBureauTransfer.assignments[1].type, 'transfer')
    assert.equal(crossBureauTransfer.assignments[1].previousBureau, 'PGRC')
    assert.match(crossBureauTransfer.timeline[0].label, /Cross-Bureau Transfer/i)
  })
})
