import test from 'node:test'
import assert from 'node:assert/strict'
import {
  isNotificationAuthorized,
  canViewComplaint,
  getNotificationStorageKey,
  loadUserNotifications,
  saveUserNotifications,
} from '../../data.ts'

test('Bug 2 Regression: Hide unauthorized notifications before displaying them', async (t) => {
  // Mock users
  const complainantRohit = {
    id: 'u0',
    name: 'Rohit Sharma',
    email: 'rohit.sharma@gmail.com',
    role: 'Complainant',
    bureau: 'PGRC',
  }

  const complainantOther = {
    id: 'u0b',
    name: 'S. Sundaram',
    email: 'citizen.grievance@aicte-portal.in',
    role: 'Complainant',
    bureau: 'RB',
  }

  const officerRajesh = {
    id: 'u2',
    name: 'Rajesh Kumar',
    email: 'rajesh.kumar@aicte-india.org',
    role: 'Officer',
    bureau: 'PGRC',
  }

  const officerAnita = {
    id: 'u3',
    name: 'Anita Verma',
    email: 'anita.verma@aicte-india.org',
    role: 'Officer',
    bureau: 'RB',
  }

  const bureauAdminPriya = {
    id: 'u1b',
    name: 'Dr. Priya Nair',
    email: 'priya.nair@aicte-india.org',
    role: 'BureauAdmin',
    bureau: 'PGRC',
  }

  const systemAdminMehta = {
    id: 'u1',
    name: 'Dr. S. Mehta',
    email: 'member-sec@aicte-india.org',
    role: 'Admin',
    bureau: 'All',
  }

  // Mock complaints
  const mockComplaints = [
    {
      id: 'PGRC-2026-0930',
      title: 'Fee anomaly at Sunrise Institute',
      bureau: 'PGRC',
      officer: 'Rajesh Kumar',
      assignedUserId: 'u2',
      complainantEmail: 'rohit.sharma@gmail.com',
      complainantName: 'Rohit Sharma',
    },
    {
      id: 'RB-2026-0141',
      title: 'Tuition fee regulatory violation',
      bureau: 'RB',
      officer: 'Anita Verma',
      assignedUserId: 'u3',
      complainantEmail: 'citizen.grievance@aicte-portal.in',
      complainantName: 'S. Sundaram',
    },
    {
      id: 'AB-2026-0310',
      title: 'CAD Software licenses shortfall',
      bureau: 'Approval',
      officer: 'Suresh Patel',
      assignedUserId: 'u5',
      complainantEmail: 'other.student@college.edu.in',
      complainantName: 'Other Student',
    },
  ]

  // Mock notifications
  const notifRohitCase = {
    id: 'n-rohit',
    type: 'info',
    title: 'Docket PGRC-2026-0930 Updated',
    message: 'Scrutiny remark added to your grievance.',
    caseId: 'PGRC-2026-0930',
    read: false,
  }

  const notifOtherCase = {
    id: 'n-other',
    type: 'alert',
    title: 'Docket RB-2026-0141 Escalated',
    message: 'Sensitive regulatory non-compliance circular issued.',
    caseId: 'RB-2026-0141',
    read: false,
  }

  const notifApprovalCase = {
    id: 'n-approval',
    type: 'warning',
    title: 'Docket AB-2026-0310 Inspection Scheduled',
    message: 'Inspection committee deputed to campus.',
    caseId: 'AB-2026-0310',
    read: false,
  }

  const notifDirectToRohit = {
    id: 'n-rohit-direct',
    type: 'info',
    title: 'Acknowledgement: Grievance Received',
    message: 'Your submitted grievance has been queued for verification.',
    recipientEmail: 'rohit.sharma@gmail.com',
    recipientUserId: 'u0',
    read: false,
  }

  const notifSystemBroadcast = {
    id: 'n-broadcast',
    type: 'info',
    title: 'System Wide Monthly Report',
    message: 'Consolidated report generated for central administration.',
    read: false,
  }

  const notifPgrcInternalReport = {
    id: 'n-pgrc-report',
    type: 'info',
    title: 'PGRC Bureau Monthly Metrics Published',
    message: 'Internal bureau audit report available for review.',
    bureau: 'PGRC',
    read: false,
  }

  await t.test('1. Complainant only sees notifications addressed to their authenticated user ID/email or linked to an authorized complaint', () => {
    // Rohit sees own case notification
    assert.equal(
      isNotificationAuthorized(complainantRohit, notifRohitCase, mockComplaints),
      true,
      'Rohit should see notifications for his own filed grievance'
    )

    // Rohit sees notification explicitly addressed to his user ID/email
    assert.equal(
      isNotificationAuthorized(complainantRohit, notifDirectToRohit, mockComplaints),
      true,
      'Rohit should see notifications explicitly addressed to his email/user ID'
    )

    // Other complainant does NOT see notification addressed to Rohit
    assert.equal(
      isNotificationAuthorized(complainantOther, notifDirectToRohit, mockComplaints),
      false,
      'Other complainant must NEVER see notifications addressed to Rohit'
    )

    // Rohit NEVER sees Sundaram\'s or Approval case notifications
    assert.equal(
      isNotificationAuthorized(complainantRohit, notifOtherCase, mockComplaints),
      false,
      'Rohit must NEVER see notifications for Sundaram\'s case (RB-2026-0141)'
    )
    assert.equal(
      isNotificationAuthorized(complainantRohit, notifApprovalCase, mockComplaints),
      false,
      'Rohit must NEVER see notifications for unowned case (AB-2026-0310)'
    )

    // Rohit does NOT see internal Bureau report notifications
    assert.equal(
      isNotificationAuthorized(complainantRohit, notifPgrcInternalReport, mockComplaints),
      false,
      'Complainant must NEVER see internal bureau audit reports'
    )

    // Rohit does NOT see general unaddressed system reports
    assert.equal(
      isNotificationAuthorized(complainantRohit, notifSystemBroadcast, mockComplaints),
      false,
      'Complainant must not see unaddressed general system admin reports'
    )
  })

  await t.test('2. Unauthorized notifications are absent from the bell dropdown, unread count, and Notifications page', () => {
    const allNotifications = [
      notifRohitCase, // unread, authorized for Rohit
      notifDirectToRohit, // unread, authorized for Rohit
      notifOtherCase, // unread, UNAUTHORIZED for Rohit
      notifApprovalCase, // unread, UNAUTHORIZED for Rohit
      notifPgrcInternalReport, // unread, UNAUTHORIZED for Rohit
    ]

    // Pre-filtering applied before bell dropdown, unread count, and Notifications page
    const visibleForRohit = allNotifications.filter((n) =>
      isNotificationAuthorized(complainantRohit, n, mockComplaints)
    )

    // Exactly 2 authorized notifications visible
    assert.equal(visibleForRohit.length, 2, 'Exactly 2 notifications should be visible to Rohit')
    const visibleIds = visibleForRohit.map((n) => n.id)
    assert.ok(visibleIds.includes('n-rohit'), 'n-rohit must be visible')
    assert.ok(visibleIds.includes('n-rohit-direct'), 'n-rohit-direct must be visible')
    assert.ok(!visibleIds.includes('n-other'), 'n-other must NOT be visible')
    assert.ok(!visibleIds.includes('n-approval'), 'n-approval must NOT be visible')
    assert.ok(!visibleIds.includes('n-pgrc-report'), 'n-pgrc-report must NOT be visible')

    // Unread count strictly reflects only visible authorized notifications
    const visibleUnreadCount = visibleForRohit.filter((n) => !n.read).length
    assert.equal(visibleUnreadCount, 2, 'Unread count must be 2, ignoring all unauthorized notifications')

    // Mark-all-read operates only on visible notifications without touching unauthorized ones
    const visibleIdSet = new Set(visibleForRohit.map((n) => n.id))
    const updatedNotifications = allNotifications.map((n) =>
      visibleIdSet.has(n.id) ? { ...n, read: true } : n
    )

    const markedRohit = updatedNotifications.find((n) => n.id === 'n-rohit')
    const markedDirect = updatedNotifications.find((n) => n.id === 'n-rohit-direct')
    const untouchedOther = updatedNotifications.find((n) => n.id === 'n-other')
    const untouchedApproval = updatedNotifications.find((n) => n.id === 'n-approval')

    assert.equal(markedRohit?.read, true, 'Authorized notification marked as read')
    assert.equal(markedDirect?.read, true, 'Authorized notification marked as read')
    assert.equal(untouchedOther?.read, false, 'Unauthorized notification read-state untouched')
    assert.equal(untouchedApproval?.read, false, 'Unauthorized notification read-state untouched')
  })

  await t.test('3. Clicking an authorized notification opens the permitted case; unauthorized case IDs cannot be exposed', () => {
    // 1. Authorized case access check
    const rohitDocket = mockComplaints.find((c) => c.id === notifRohitCase.caseId)
    const rohitAccess = canViewComplaint(complainantRohit, rohitDocket)
    assert.equal(rohitAccess.allowed, true, 'Complainant can open permitted case linked to authorized notification')

    // 2. Unauthorized case access check
    const otherDocket = mockComplaints.find((c) => c.id === notifOtherCase.caseId)
    const otherAccess = canViewComplaint(complainantRohit, otherDocket)
    assert.equal(otherAccess.allowed, false, 'Complainant cannot access unowned case')
    assert.ok(otherAccess.reason?.includes('submitted by'), 'Access denied with appropriate security reason')

    // 3. Ensure unauthorized caseId is filtered before rendering so it cannot be clicked
    const visibleToRohit = [notifRohitCase, notifOtherCase].filter((n) =>
      isNotificationAuthorized(complainantRohit, n, mockComplaints)
    )
    assert.equal(visibleToRohit.length, 1)
    assert.equal(visibleToRohit[0].caseId, 'PGRC-2026-0930', 'Only authorized docket ID is exposed to the user')
  })

  await t.test('4. Officer and Bureau Admin notification scoping follows actual authorization rules', () => {
    // Officer Rajesh Kumar (PGRC):
    // 1. Sees case assigned to him (PGRC-2026-0930)
    assert.equal(
      isNotificationAuthorized(officerRajesh, notifRohitCase, mockComplaints),
      true,
      'Officer Rajesh sees notifications for his assigned case'
    )
    // 2. Does NOT see RB-2026-0141 (assigned to Anita Verma in RB)
    assert.equal(
      isNotificationAuthorized(officerRajesh, notifOtherCase, mockComplaints),
      false,
      'Officer Rajesh does NOT see notifications for cases assigned to Anita Verma'
    )
    // 3. Sees PGRC internal report
    assert.equal(
      isNotificationAuthorized(officerRajesh, notifPgrcInternalReport, mockComplaints),
      true,
      'Officer Rajesh sees internal notifications for his bureau (PGRC)'
    )

    // Officer Anita Verma (RB):
    // 1. Sees case assigned to her (RB-2026-0141)
    assert.equal(
      isNotificationAuthorized(officerAnita, notifOtherCase, mockComplaints),
      true,
      'Officer Anita sees notifications for her assigned case'
    )
    // 2. Does NOT see PGRC-2026-0930 (assigned to Rajesh)
    assert.equal(
      isNotificationAuthorized(officerAnita, notifRohitCase, mockComplaints),
      false,
      'Officer Anita does NOT see notifications for cases assigned to Rajesh Kumar'
    )

    // Bureau Admin Dr. Priya Nair (PGRC):
    // 1. Sees notifications for PGRC cases
    assert.equal(
      isNotificationAuthorized(bureauAdminPriya, notifRohitCase, mockComplaints),
      true,
      'Bureau Admin Priya sees notifications for cases in PGRC Bureau'
    )
    // 2. Does NOT see notifications for RB cases
    assert.equal(
      isNotificationAuthorized(bureauAdminPriya, notifOtherCase, mockComplaints),
      false,
      'Bureau Admin Priya does NOT see notifications for RB Bureau cases'
    )
    // 3. Sees PGRC internal bureau report
    assert.equal(
      isNotificationAuthorized(bureauAdminPriya, notifPgrcInternalReport, mockComplaints),
      true,
      'Bureau Admin Priya sees PGRC bureau reports'
    )

    // System Admin Dr. S. Mehta:
    // Sees notifications system-wide
    assert.equal(
      isNotificationAuthorized(systemAdminMehta, notifRohitCase, mockComplaints),
      true,
      'System Admin sees PGRC notifications'
    )
    assert.equal(
      isNotificationAuthorized(systemAdminMehta, notifOtherCase, mockComplaints),
      true,
      'System Admin sees RB notifications'
    )
    assert.equal(
      isNotificationAuthorized(systemAdminMehta, notifApprovalCase, mockComplaints),
      true,
      'System Admin sees Approval notifications'
    )
    assert.equal(
      isNotificationAuthorized(systemAdminMehta, notifPgrcInternalReport, mockComplaints),
      true,
      'System Admin sees bureau reports'
    )
    assert.equal(
      isNotificationAuthorized(systemAdminMehta, notifSystemBroadcast, mockComplaints),
      true,
      'System Admin sees general system broadcasts'
    )
  })

  await t.test('5. Switching users does not leak notification content or read-state', () => {
    const localStorageMock = {}
    global.localStorage = {
      getItem: (key) => localStorageMock[key] || null,
      setItem: (key, val) => {
        localStorageMock[key] = String(val)
      },
      removeItem: (key) => {
        delete localStorageMock[key]
      },
    }

    const keyUserA = getNotificationStorageKey('u0')
    const keyUserB = getNotificationStorageKey('u0b')
    assert.notEqual(keyUserA, keyUserB, 'Storage keys must be strictly isolated per user ID')

    // Save notifications for User A
    const notifsUserA = [
      { id: 'n1', title: 'User A notification', read: false },
      { id: 'n2', title: 'User A notification 2', read: false },
    ]
    saveUserNotifications('u0', notifsUserA)

    // User A marks n1 read
    notifsUserA[0].read = true
    saveUserNotifications('u0', notifsUserA)

    // Save notifications for User B
    const notifsUserB = [
      { id: 'n1', title: 'User B notification with same ID', read: false },
    ]
    saveUserNotifications('u0b', notifsUserB)

    // Verify User A state has n1 read
    const loadedA = loadUserNotifications('u0')
    assert.equal(loadedA.find((n) => n.id === 'n1')?.read, true)

    // Verify User B state has n1 unread
    const loadedB = loadUserNotifications('u0b')
    assert.equal(loadedB.find((n) => n.id === 'n1')?.read, false)
    assert.equal(loadedB[0].title, 'User B notification with same ID')

    // Clean up
    delete global.localStorage
  })
})
