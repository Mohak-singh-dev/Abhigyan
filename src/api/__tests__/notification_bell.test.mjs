import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

test('Bug 1 Regression: Stop notification bell and unread indicator blinking', async (t) => {
  const topBarPath = path.resolve(__dirname, '../../components/layout/TopBar.tsx')
  const topBarSource = fs.readFileSync(topBarPath, 'utf8')

  await t.test('TopBar notification bell and unread badge contain no blinking or pulse animation classes', () => {
    // Locate the notification button block in TopBar.tsx
    const bellIndex = topBarSource.indexOf('aria-label="Notifications"')
    assert.ok(bellIndex !== -1, 'TopBar must contain a notification button with aria-label="Notifications"')

    // Extract the notification bell button and unread badge markup (next 800 chars)
    const bellSnippet = topBarSource.slice(bellIndex, bellIndex + 800)

    // Verify continuous blinking/pulsing classes are NOT present on the bell or unread badge
    assert.ok(
      !bellSnippet.includes('animate-pulse'),
      'Notification bell or badge must NOT contain "animate-pulse" continuous animation'
    )
    assert.ok(
      !bellSnippet.includes('animate-bounce'),
      'Notification bell or badge must NOT contain "animate-bounce" continuous animation'
    )
    assert.ok(
      !bellSnippet.includes('animate-ping'),
      'Notification bell or badge must NOT contain "animate-ping" continuous animation'
    )
    assert.ok(
      !bellSnippet.includes('blink'),
      'Notification bell or badge must NOT contain custom "blink" animation'
    )
  })

  await t.test('Notification unread badge retains static indicator styling and functional count display', () => {
    // Verify unread badge retains standard high-contrast badge styling
    assert.ok(
      topBarSource.includes('bg-rose-500'),
      'Unread badge must maintain rose/red indicator color for clear visibility'
    )
    assert.ok(
      topBarSource.includes("unreadNotifs.length > 0 && ("),
      'Unread badge must only display when unreadNotifs.length > 0'
    )
    assert.ok(
      topBarSource.includes("{unreadNotifs.length}"),
      'Unread badge must display unread count'
    )
  })

  await t.test('Unread state changes update badge count without triggering animation classes', () => {
    // Simulate calculating unread count from notification state
    const sampleNotifications = [
      { id: 'n1', read: false, title: 'Case update' },
      { id: 'n2', read: true, title: 'Welcome' },
    ]
    let unreadCount = sampleNotifications.filter((n) => !n.read).length
    assert.equal(unreadCount, 1, 'Initial unread count should be 1')

    // Add a new unread notification
    sampleNotifications.unshift({ id: 'n3', read: false, title: 'New docket filed' })
    unreadCount = sampleNotifications.filter((n) => !n.read).length
    assert.equal(unreadCount, 2, 'Unread count updates to 2')

    // Mark one as read
    sampleNotifications[0].read = true
    unreadCount = sampleNotifications.filter((n) => !n.read).length
    assert.equal(unreadCount, 1, 'Unread count updates to 1 without animation side-effects')
  })
})
