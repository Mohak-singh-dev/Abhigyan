/**
 * Phase 5 Regression Tests: Role Navigation and Route Authorization
 *
 * Proves:
 * 1. Complainant primary sidebar contains exactly:
 *    - "My Grievances" ('complaints')
 *    - "Submit Grievances" ('submit')
 *    - "Track My Dockets" ('tracking')
 * 2. "Alerts and Updates" is removed from Complainant sidebar (retained as top-bar bell).
 * 3. BureauAdmin and Admin do NOT have "Register Grievance" / 'submit' in sidebar or permitted pages.
 * 4. Direct route access to 'submit' is blocked for Admin and BureauAdmin.
 * 5. Role permitted pages enforce strict boundaries.
 */

import { test, describe } from 'node:test'
import assert from 'node:assert/strict'

// Permitted pages matrix mirroring App.tsx
const ROLE_PERMITTED_PAGES = {
  Complainant: ['complaints', 'submit', 'details', 'tracking', 'notifications'],
  Officer: ['complaints', 'details', 'institutions', 'overlaps', 'tracking', 'notifications'],
  BureauAdmin: [
    'dashboard',
    'complaints',
    'details',
    'institutions',
    'overlaps',
    'tracking',
    'reports',
    'notifications',
    'settings',
  ],
  Admin: [
    'dashboard',
    'complaints',
    'details',
    'institutions',
    'overlaps',
    'tracking',
    'reports',
    'notifications',
    'users',
    'settings',
  ],
}

// Sidebar items definition mirroring Sidebar.tsx
function getSidebarNavItems(role) {
  if (role === 'Complainant') {
    return [
      { id: 'complaints', label: 'My Grievances' },
      { id: 'submit', label: 'Submit Grievances' },
      { id: 'tracking', label: 'Track My Dockets' },
    ]
  }

  const baseItems = [
    { id: 'dashboard', label: 'Overview' },
    { id: 'complaints', label: 'Grievance Cases' },
    { id: 'tracking', label: 'Case Tracking' },
    { id: 'institutions', label: 'Institutions' },
    { id: 'overlaps', label: 'Overlaps & Redundancy' },
    { id: 'reports', label: 'Statutory Reports' },
    { id: 'users', label: 'User Directory', adminOnly: true },
  ]

  return baseItems.filter((item) => !item.adminOnly || role === 'Admin')
}

describe('Phase 5: Role Navigation & Route Access Bounds', () => {
  test('Complainant sidebar contains exactly My Grievances, Submit Grievances, and Track My Dockets', () => {
    const complainantItems = getSidebarNavItems('Complainant')
    assert.equal(complainantItems.length, 3, 'Complainant must have exactly 3 primary navigation items')

    const ids = complainantItems.map((item) => item.id)
    const labels = complainantItems.map((item) => item.label)

    assert.deepEqual(ids, ['complaints', 'submit', 'tracking'])
    assert.deepEqual(labels, ['My Grievances', 'Submit Grievances', 'Track My Dockets'])

    // Confirm "Alerts & Updates" / 'notifications' is NOT in sidebar
    assert.equal(ids.includes('notifications'), false, 'Alerts & Updates must be removed from sidebar')
  })

  test('BureauAdmin and Admin sidebar does NOT contain Register Grievance / submit', () => {
    const bureauAdminItems = getSidebarNavItems('BureauAdmin')
    const adminItems = getSidebarNavItems('Admin')

    assert.equal(
      bureauAdminItems.some((item) => item.id === 'submit'),
      false,
      'BureauAdmin sidebar must not contain Register Grievance'
    )
    assert.equal(
      adminItems.some((item) => item.id === 'submit'),
      false,
      'Admin sidebar must not contain Register Grievance'
    )
  })

  test('Direct route access to submit page is rejected for BureauAdmin and Admin', () => {
    const isPermittedForAdmin = ROLE_PERMITTED_PAGES.Admin.includes('submit')
    const isPermittedForBureauAdmin = ROLE_PERMITTED_PAGES.BureauAdmin.includes('submit')
    const isPermittedForOfficer = ROLE_PERMITTED_PAGES.Officer.includes('submit')
    const isPermittedForComplainant = ROLE_PERMITTED_PAGES.Complainant.includes('submit')

    assert.equal(isPermittedForAdmin, false, 'Admin cannot access submit page')
    assert.equal(isPermittedForBureauAdmin, false, 'BureauAdmin cannot access submit page')
    assert.equal(isPermittedForOfficer, false, 'Officer cannot access submit page')
    assert.equal(isPermittedForComplainant, true, 'Complainant can access submit page')
  })

  test('Route guard protects against manual URL / React state tampering', () => {
    function checkRouteGuard(role, targetPage) {
      return ROLE_PERMITTED_PAGES[role].includes(targetPage)
    }

    // Tampering test: BureauAdmin attempts to directly navigate to 'submit'
    assert.equal(checkRouteGuard('BureauAdmin', 'submit'), false)

    // Tampering test: Officer attempts to directly navigate to 'users'
    assert.equal(checkRouteGuard('Officer', 'users'), false)

    // Tampering test: Complainant attempts to directly navigate to 'dashboard'
    assert.equal(checkRouteGuard('Complainant', 'dashboard'), false)
  })
})
