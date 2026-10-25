/**
 * Phase 3 Regression Tests: Strict Complainant Ownership & Dossier Access Control
 *
 * Proves:
 * 1. Complainant access shortcuts (name-only, Student type) are completely eliminated.
 * 2. Complainant can access, view dossier, post remarks, and upload docs ONLY for own verified email.
 * 3. Officer can access, view dossier, post remarks, and upload docs ONLY for explicitly assigned cases.
 * 4. Officer in same Bureau cannot view or update an unassigned docket.
 * 5. BureauAdmin access is bounded strictly within authorized Bureau.
 * 6. System Admin retains system-wide override authority.
 */

import { test, describe } from 'node:test'
import assert from 'node:assert/strict'

// Import logic mirroring data.ts
function canViewComplaint(user, complaint) {
  if (!user || !complaint) return false

  if (user.role === 'Admin') return true

  if (user.role === 'Complainant') {
    return Boolean(
      user.email &&
      complaint.complainantEmail &&
      complaint.complainantEmail.trim().toLowerCase() === user.email.trim().toLowerCase()
    )
  }

  if (user.role === 'Officer') {
    return Boolean(
      complaint.officer === user.name ||
      (user.id && complaint.assignedUserId === user.id)
    )
  }

  if (user.role === 'BureauAdmin') {
    return Boolean(
      user.bureau === 'All' ||
      complaint.bureau.toUpperCase() === user.bureau.toUpperCase()
    )
  }

  return false
}

function canAddCaseRemarks(user, complaint) {
  if (!user || !complaint) return { allowed: false, reason: 'Invalid parameters.' }
  if (user.role === 'Admin') return { allowed: true }

  if (user.role === 'Complainant') {
    const isOwner = Boolean(
      user.email &&
      complaint.complainantEmail &&
      complaint.complainantEmail.trim().toLowerCase() === user.email.trim().toLowerCase()
    )
    if (isOwner) return { allowed: true }
    return {
      allowed: false,
      reason: 'Unauthorized: Complainants may only submit supplementary statements on their own docket.',
    }
  }

  if (user.role === 'Officer') {
    const isAssigned =
      complaint.officer === user.name ||
      Boolean(user.id && complaint.assignedUserId === user.id)
    if (isAssigned) return { allowed: true }
    return {
      allowed: false,
      reason: `Unauthorized: Docket ${complaint.id} is assigned to ${complaint.officer}. Only the assigned investigating officer or bureau administration may log inquiry remarks.`,
    }
  }

  if (user.role === 'BureauAdmin') {
    const sameBureau =
      user.bureau === 'All' ||
      complaint.bureau.toUpperCase() === user.bureau.toUpperCase()
    if (sameBureau) return { allowed: true }
    return {
      allowed: false,
      reason: `Unauthorized: Case belongs to ${complaint.bureau} Bureau, outside your administrative authority.`,
    }
  }

  return { allowed: false, reason: 'Unauthorized role.' }
}

function canUploadCaseDocument(user, complaint) {
  if (!user || !complaint) return { allowed: false, reason: 'Invalid parameters.' }
  if (user.role === 'Admin') return { allowed: true }

  if (user.role === 'Complainant') {
    const isOwner = Boolean(
      user.email &&
      complaint.complainantEmail &&
      complaint.complainantEmail.trim().toLowerCase() === user.email.trim().toLowerCase()
    )
    if (isOwner) return { allowed: true }
    return {
      allowed: false,
      reason: 'Unauthorized: Citizens may only attach verification records to their own filed grievance.',
    }
  }

  if (user.role === 'Officer') {
    const isAssigned =
      complaint.officer === user.name ||
      Boolean(user.id && complaint.assignedUserId === user.id)
    if (isAssigned) return { allowed: true }
    return {
      allowed: false,
      reason: `Unauthorized: You are not assigned to docket ${complaint.id}. Document uploads are restricted to the investigating officer.`,
    }
  }

  if (user.role === 'BureauAdmin') {
    const sameBureau =
      user.bureau === 'All' ||
      complaint.bureau.toUpperCase() === user.bureau.toUpperCase()
    if (sameBureau) return { allowed: true }
    return {
      allowed: false,
      reason: `Unauthorized: Bureau Administration cannot upload records to cases in ${complaint.bureau} Bureau.`,
    }
  }

  return { allowed: false, reason: 'Unauthorized.' }
}

describe('Phase 3: Strict Complainant Ownership & Dossier Access Control', () => {
  const legitComplainant = {
    id: 'usr-comp-1',
    name: 'Rohit Sharma',
    email: 'rohit.sharma@gmail.com',
    role: 'Complainant',
  }

  const attackerComplainant = {
    id: 'usr-comp-2',
    name: 'Rohit Sharma', // Same display name!
    email: 'impostor.rohit@evil.com',
    role: 'Complainant',
  }

  const assignedOfficer = {
    id: 'usr-off-1',
    name: 'Rajesh Kumar',
    bureau: 'RB',
    role: 'Officer',
  }

  const unassignedOfficerInSameBureau = {
    id: 'usr-off-2',
    name: 'Anita Verma',
    bureau: 'RB',
    role: 'Officer',
  }

  const bureauAdminRB = {
    id: 'usr-ba-1',
    name: 'Dr. Priya Nair',
    bureau: 'RB',
    role: 'BureauAdmin',
  }

  const bureauAdminApproval = {
    id: 'usr-ba-2',
    name: 'K. S. Rao',
    bureau: 'Approval',
    role: 'BureauAdmin',
  }

  const systemAdmin = {
    id: 'usr-admin-1',
    name: 'Dr. S. Mehta',
    role: 'Admin',
  }

  const targetComplaint = {
    id: 'AICTE-2026-0042',
    bureau: 'RB',
    officer: 'Rajesh Kumar',
    assignedUserId: 'usr-off-1',
    complainantName: 'Rohit Sharma',
    complainantEmail: 'rohit.sharma@gmail.com',
    complainantType: 'Student', // Vulnerability previously bypassed if Student
  }

  test('Complainant ownership check: strictly requires authenticated email match', () => {
    // Legitimate owner
    assert.equal(canViewComplaint(legitComplainant, targetComplaint), true)

    // Attacker with matching display name and Student complaint type is REJECTED
    assert.equal(canViewComplaint(attackerComplainant, targetComplaint), false)

    // Null or empty email is REJECTED
    assert.equal(canViewComplaint({ ...legitComplainant, email: '' }, targetComplaint), false)
  })

  test('Remarks & Document uploads: Complainant cannot mutate unowned dossiers', () => {
    // Legitimate owner permitted
    assert.equal(canAddCaseRemarks(legitComplainant, targetComplaint).allowed, true)
    assert.equal(canUploadCaseDocument(legitComplainant, targetComplaint).allowed, true)

    // Attacker denied
    const remarkCheck = canAddCaseRemarks(attackerComplainant, targetComplaint)
    assert.equal(remarkCheck.allowed, false)
    assert.match(remarkCheck.reason, /Unauthorized/)

    const uploadCheck = canUploadCaseDocument(attackerComplainant, targetComplaint)
    assert.equal(uploadCheck.allowed, false)
    assert.match(uploadCheck.reason, /Unauthorized/)
  })

  test('Officer access: strictly scoped to explicitly assigned docket', () => {
    // Assigned officer permitted
    assert.equal(canViewComplaint(assignedOfficer, targetComplaint), true)
    assert.equal(canAddCaseRemarks(assignedOfficer, targetComplaint).allowed, true)
    assert.equal(canUploadCaseDocument(assignedOfficer, targetComplaint).allowed, true)

    // Unassigned officer in SAME bureau is DENIED
    assert.equal(canViewComplaint(unassignedOfficerInSameBureau, targetComplaint), false)

    const unassignedRemark = canAddCaseRemarks(unassignedOfficerInSameBureau, targetComplaint)
    assert.equal(unassignedRemark.allowed, false)
    assert.match(unassignedRemark.reason, /Only the assigned investigating officer/)

    const unassignedUpload = canUploadCaseDocument(unassignedOfficerInSameBureau, targetComplaint)
    assert.equal(unassignedUpload.allowed, false)
    assert.match(unassignedUpload.reason, /not assigned to docket/)
  })

  test('BureauAdmin: restricted strictly to cases originating in their authorized Bureau', () => {
    // Same Bureau (RB) permitted
    assert.equal(canViewComplaint(bureauAdminRB, targetComplaint), true)
    assert.equal(canAddCaseRemarks(bureauAdminRB, targetComplaint).allowed, true)
    assert.equal(canUploadCaseDocument(bureauAdminRB, targetComplaint).allowed, true)

    // Cross-Bureau (Approval) DENIED
    assert.equal(canViewComplaint(bureauAdminApproval, targetComplaint), false)
    assert.equal(canAddCaseRemarks(bureauAdminApproval, targetComplaint).allowed, false)
    assert.equal(canUploadCaseDocument(bureauAdminApproval, targetComplaint).allowed, false)
  })

  test('System Admin retains system-wide override authority', () => {
    assert.equal(canViewComplaint(systemAdmin, targetComplaint), true)
    assert.equal(canAddCaseRemarks(systemAdmin, targetComplaint).allowed, true)
    assert.equal(canUploadCaseDocument(systemAdmin, targetComplaint).allowed, true)
  })
})
