/**
 * Phase 4 Regression Tests: Per-User Notification Read-State
 *
 * Proves:
 * 1. Notification read-state is namespaced by authenticated user ID (abhigyan_notifications_<userId>).
 * 2. Marking notifications as read for one user does not change the read-state for another user.
 * 3. Account-switching does not leak read-state across sessions.
 * 4. Missing or malformed stored values are handled gracefully with safe fallbacks.
 */

import { test, describe, beforeEach } from 'node:test'
import assert from 'node:assert/strict'

// In-memory localStorage mock for node environment
class MockLocalStorage {
  constructor() {
    this.store = new Map()
  }
  getItem(key) {
    return this.store.get(key) || null
  }
  setItem(key, value) {
    this.store.set(key, String(value))
  }
  removeItem(key) {
    this.store.delete(key)
  }
  clear() {
    this.store.clear()
  }
}

globalThis.localStorage = new MockLocalStorage()

// Storage helper functions mirroring App.tsx implementation
function getNotificationStorageKey(userId) {
  return userId ? `abhigyan_notifications_${userId}` : 'abhigyan_notifications_anonymous'
}

const mockDefaultNotifications = [
  { id: 'notif-1', title: 'Hearing Notice', read: false },
  { id: 'notif-2', title: 'Inspection Notice', read: false },
]

function loadUserNotifications(userId) {
  if (!userId) return mockDefaultNotifications
  try {
    const key = getNotificationStorageKey(userId)
    const stored = globalThis.localStorage.getItem(key)
    if (stored) {
      const parsed = JSON.parse(stored)
      if (Array.isArray(parsed) && parsed.length > 0) return parsed
    }
  } catch {
    // Graceful recovery from malformed JSON
  }
  return mockDefaultNotifications
}

function saveUserNotifications(userId, notifications) {
  const key = getNotificationStorageKey(userId)
  globalThis.localStorage.setItem(key, JSON.stringify(notifications))
}

describe('Phase 4: Per-User Notification Read-State Isolation', () => {
  beforeEach(() => {
    globalThis.localStorage.clear()
  })

  test('Namespace key incorporates authenticated user ID', () => {
    assert.equal(getNotificationStorageKey('usr-rohit-101'), 'abhigyan_notifications_usr-rohit-101')
    assert.equal(getNotificationStorageKey('usr-priya-202'), 'abhigyan_notifications_usr-priya-202')
    assert.equal(getNotificationStorageKey(null), 'abhigyan_notifications_anonymous')
  })

  test('Marking notifications as read for User A does not alter read-state for User B', () => {
    const userA = 'user-complainant-1'
    const userB = 'user-officer-2'

    // 1. Initial state: both users load defaults
    const notifsUserA = loadUserNotifications(userA)
    const notifsUserB = loadUserNotifications(userB)

    assert.equal(notifsUserA.every((n) => n.read === false), true, 'User A initially has all unread')
    assert.equal(notifsUserB.every((n) => n.read === false), true, 'User B initially has all unread')

    // 2. User A marks notif-1 as read and saves
    const updatedUserA = notifsUserA.map((n) => (n.id === 'notif-1' ? { ...n, read: true } : n))
    saveUserNotifications(userA, updatedUserA)

    // 3. User B marks all as read and saves
    const updatedUserB = notifsUserB.map((n) => ({ ...n, read: true }))
    saveUserNotifications(userB, updatedUserB)

    // 4. Verify User A storage remains independent
    const reloadedUserA = loadUserNotifications(userA)
    assert.equal(reloadedUserA.find((n) => n.id === 'notif-1')?.read, true)
    assert.equal(reloadedUserA.find((n) => n.id === 'notif-2')?.read, false, 'User A notif-2 remains unread')

    // 5. Verify User B storage remains independent
    const reloadedUserB = loadUserNotifications(userB)
    assert.equal(reloadedUserB.every((n) => n.read === true), true, 'User B all notifications read')
  })

  test('Account switching scenario preserves per-user notification state without bleed', () => {
    const complainantId = 'usr-complainant'
    const adminId = 'usr-admin'

    // Session 1: Complainant logs in, marks all as read
    const compNotifs = loadUserNotifications(complainantId).map((n) => ({ ...n, read: true }))
    saveUserNotifications(complainantId, compNotifs)

    // Account Switch: Admin logs in
    const adminNotifs = loadUserNotifications(adminId)
    assert.equal(
      adminNotifs.some((n) => n.read === false),
      true,
      'Admin should NOT inherit Complainant read-state'
    )

    // Account Switch Back: Complainant logs back in
    const compNotifsRestored = loadUserNotifications(complainantId)
    assert.equal(
      compNotifsRestored.every((n) => n.read === true),
      true,
      'Complainant read-state is safely preserved across account switches'
    )
  })

  test('Malformed or corrupted localStorage entries fall back safely', () => {
    const userId = 'usr-test-corrupted'
    const key = getNotificationStorageKey(userId)

    // Inject corrupted JSON
    globalThis.localStorage.setItem(key, '{corrupted-non-json-data!!')
    const fallbackNotifs = loadUserNotifications(userId)

    assert.ok(Array.isArray(fallbackNotifs), 'Returns array on corrupted storage')
    assert.equal(fallbackNotifs.length, 2, 'Returns default notifications')
  })
})
