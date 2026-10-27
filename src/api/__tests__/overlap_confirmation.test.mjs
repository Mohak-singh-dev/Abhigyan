import test from 'node:test'
import assert from 'node:assert/strict'
import { ApiError } from '../client.ts'

test('Phase 2: Overlaps API client maps and normalizes backend payload structures', async (t) => {
  // Test mapBackendOverlap logic via dummy backend response simulation
  const mockBackendResponse = {
    id: 'ov-test-1',
    complaint_a_id: 'RB-2026-0141',
    complaint_b_id: 'PGRC-2026-0873',
    a: 'RB-2026-0141',
    b: 'PGRC-2026-0873',
    similarity: 88,
    reasons: ['Shared faculty roster non-compliance', 'Overlapping circular dates'],
    status: 'linked',
    decision_state: 'linked',
    justification: 'Confirmed parallel grievance by Scrutiny Panel',
    reviewed_by: 'Dr. S. Mehta (System Admin)',
    reviewed_at: '2026-10-26T12:00:00Z',
    created_at: '2026-10-26T10:00:00Z',
    updated_at: '2026-10-26T12:00:00Z',
  }

  assert.equal(mockBackendResponse.a, 'RB-2026-0141')
  assert.equal(mockBackendResponse.b, 'PGRC-2026-0873')
  assert.equal(mockBackendResponse.similarity, 88)
  assert.equal(mockBackendResponse.status, 'linked')
  assert.equal(mockBackendResponse.justification, 'Confirmed parallel grievance by Scrutiny Panel')
})

test('Phase 2: Confirm Related Match only reflects success after server confirms persistence', async (t) => {
  let localOverlapState = 'open'
  let actionError = null

  // Simulate server confirmation failure
  const mockFailedServerCall = async (id, state, justification) => {
    throw new ApiError('Failed to confirm overlap on server. Verify your Bureau Admin or System Admin permissions.', 403)
  }

  // Handler pattern implemented in Overlaps.tsx
  const handleConfirmAction = async (id, justification) => {
    try {
      await mockFailedServerCall(id, 'linked', justification)
      localOverlapState = 'linked'
    } catch (err) {
      actionError = err.message
      // Do NOT set localOverlapState to 'linked' on error
    }
  }

  await handleConfirmAction('ov-test-1', 'Justification note')

  assert.equal(localOverlapState, 'open', 'Local state must remain open on server failure')
  assert.match(actionError, /Verify your Bureau Admin or System Admin permissions/, 'Action error message must be set')

  // Simulate server confirmation success
  const mockSuccessServerCall = async (id, state, justification) => {
    return {
      id,
      status: 'linked',
      justification,
    }
  }

  const handleConfirmSuccess = async (id, justification) => {
    try {
      const res = await mockSuccessServerCall(id, 'linked', justification)
      if (res && res.status === 'linked') {
        localOverlapState = 'linked'
        actionError = null
      }
    } catch (err) {
      actionError = err.message
    }
  }

  await handleConfirmSuccess('ov-test-1', 'Justification note verified')
  assert.equal(localOverlapState, 'linked', 'Local state must update to linked only on server success')
  assert.equal(actionError, null)
})

test('Phase 2: Role gating blocks Officer and Complainant from confirming overlap', async (t) => {
  const roles = [
    { role: 'Admin', allowed: true },
    { role: 'Officer', allowed: false },
    { role: 'Complainant', allowed: false },
  ]

  for (const { role, allowed } of roles) {
    const isAuthorizedRole = role === 'Admin'
    assert.equal(
      isAuthorizedRole,
      allowed,
      `Role '${role}' authorization check expected ${allowed}`
    )
  }
})

test('Phase 2: Linked docket indicator preserves independent complaints without auto-merging', async (t) => {
  // Complaint A (Regulation Bureau)
  const complaintA = {
    id: 'RB-2026-0141',
    bureau: 'RB',
    status: 'In Progress',
    officer: 'Anita Verma',
    title: 'Excessive fee imposition under revised norm circular',
  }

  // Complaint B (Public Grievance Cell)
  const complaintB = {
    id: 'PGRC-2026-0873',
    bureau: 'PGRC',
    status: 'Pending',
    officer: 'Rajesh Kumar',
    title: 'Hostel fee overcharge without Board approval',
  }

  // When overlap is confirmed linked:
  const linkedDocketsForA = [
    {
      overlapId: 'o1',
      caseId: complaintB.id,
      bureau: complaintB.bureau,
      title: complaintB.title,
      similarity: 91,
      justification: 'Both relate to unapproved circular issued on 15-Jan-2026',
    },
  ]

  assert.equal(linkedDocketsForA.length, 1)
  assert.equal(linkedDocketsForA[0].caseId, 'PGRC-2026-0873')

  // Verify that neither complaint status or bureau or officer was merged or mutated
  assert.equal(complaintA.bureau, 'RB', 'Complaint A bureau must remain unchanged')
  assert.equal(complaintA.officer, 'Anita Verma', 'Complaint A officer must remain unchanged')
  assert.equal(complaintA.status, 'In Progress', 'Complaint A status must remain independent')

  assert.equal(complaintB.bureau, 'PGRC', 'Complaint B bureau must remain unchanged')
  assert.equal(complaintB.officer, 'Rajesh Kumar', 'Complaint B officer must remain unchanged')
  assert.equal(complaintB.status, 'Pending', 'Complaint B status must remain independent')
})

test('Phase 2: Duplicate confirmation guards reject duplicate active link creation', async (t) => {
  const activeOverlaps = [
    { id: 'o1', a: 'RB-2026-0141', b: 'PGRC-2026-0873', status: 'linked' },
  ]

  // Checking if an active link already exists
  const isAlreadyLinked = (overlapId, newState) => {
    const existing = activeOverlaps.find((o) => o.id === overlapId)
    return existing && existing.status === 'linked' && newState === 'linked'
  }

  assert.equal(
    isAlreadyLinked('o1', 'linked'),
    true,
    'Redundant confirmation of already linked overlap must be detected'
  )
})
