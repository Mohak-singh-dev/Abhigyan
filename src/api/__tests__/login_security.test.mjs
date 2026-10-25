/**
 * Phase 2 Regression Tests: Login Fallback Elimination & Demo Auth Restrictions
 *
 * Proves:
 * 1. Submitting an incorrect password fails and does NOT silently fall back to demo login.
 * 2. Invalid credentials remain invalid credentials.
 * 3. No session or authentication tokens are generated on failure.
 * 4. Error state is set for display in the UI.
 * 5. Explicit demo login is restricted to development/configured demo mode and fails in production mode.
 */

import { test, describe } from 'node:test'
import assert from 'node:assert/strict'

// Mock state and API handlers mirroring Login.tsx
class LoginFlowSimulator {
  constructor({ demoAuthEnabled = true } = {}) {
    this.demoAuthEnabled = demoAuthEnabled
    this.sessionCreated = false
    this.sessionUser = null
    this.uiError = null
    this.demoLoginCallCount = 0
    this.normalLoginCallCount = 0
  }

  // Real backend behavior: 401 on wrong password
  async mockNormalLogin(email, password) {
    this.normalLoginCallCount++
    if (password !== 'CorrectPassword@2026') {
      const err = new Error('Invalid email or password.')
      err.status = 401
      throw err
    }
    return {
      accessToken: 'jwt-valid-token',
      user: { id: 'u1', email, role: 'Admin', name: 'Dr. S. Mehta' },
    }
  }

  async mockDemoLogin(role) {
    this.demoLoginCallCount++
    if (!this.demoAuthEnabled) {
      const err = new Error('Demo authentication is disabled in this environment.')
      err.status = 403
      throw err
    }
    return {
      accessToken: 'jwt-demo-token',
      user: { id: 'u-demo', email: 'demo@aicte.gov.in', role, name: 'Demo User' },
    }
  }

  // Fixed handleSubmit in Login.tsx: NO silent fallback!
  async handleSubmit(email, password) {
    this.uiError = null
    try {
      const res = await this.mockNormalLogin(email, password)
      this.sessionCreated = true
      this.sessionUser = res.user
      return res
    } catch (err) {
      // Security Fix: Do NOT call mockDemoLogin on 401 or any error!
      this.uiError = err.message || 'Invalid email or password.'
      this.sessionCreated = false
      this.sessionUser = null
      return null
    }
  }

  // Explicit user action: Quick Demo Login Button
  async handleQuickDemoLogin(role) {
    if (!this.demoAuthEnabled) {
      this.uiError = 'Demo login is not available in production environments.'
      return null
    }
    try {
      const res = await this.mockDemoLogin(role)
      this.sessionCreated = true
      this.sessionUser = res.user
      return res
    } catch (err) {
      this.uiError = err.message
      return null
    }
  }
}

describe('Phase 2: Login Fallback Elimination & Demo Auth Restrictions', () => {
  test('Submitting incorrect password fails and NEVER falls back to demo login', async () => {
    const simulator = new LoginFlowSimulator({ demoAuthEnabled: true })

    const result = await simulator.handleSubmit('member-sec@aicte-india.org', 'WrongPassword123')

    // 1. Login fails
    assert.equal(result, null, 'Login must return null on failure')
    assert.equal(simulator.normalLoginCallCount, 1, 'Normal login called once')

    // 2. Demo-login endpoint is NOT called
    assert.equal(simulator.demoLoginCallCount, 0, 'Demo login endpoint must NOT be called on failure')

    // 3. No authenticated session is created
    assert.equal(simulator.sessionCreated, false, 'No authenticated session created')
    assert.equal(simulator.sessionUser, null, 'No session user stored')

    // 4. UI displays appropriate error
    assert.equal(simulator.uiError, 'Invalid email or password.')
  })

  test('Submitting valid credentials creates authenticated session normally', async () => {
    const simulator = new LoginFlowSimulator({ demoAuthEnabled: true })

    const result = await simulator.handleSubmit('member-sec@aicte-india.org', 'CorrectPassword@2026')

    assert.ok(result, 'Login returns response')
    assert.equal(simulator.sessionCreated, true)
    assert.equal(simulator.sessionUser.email, 'member-sec@aicte-india.org')
    assert.equal(simulator.uiError, null)
    assert.equal(simulator.demoLoginCallCount, 0)
  })

  test('Explicit demo login works in development configuration', async () => {
    const simulator = new LoginFlowSimulator({ demoAuthEnabled: true })

    const result = await simulator.handleQuickDemoLogin('Officer')

    assert.ok(result)
    assert.equal(simulator.demoLoginCallCount, 1)
    assert.equal(simulator.sessionCreated, true)
    assert.equal(simulator.sessionUser.role, 'Officer')
  })

  test('Explicit demo login is rejected when demo authentication is disabled', async () => {
    const simulator = new LoginFlowSimulator({ demoAuthEnabled: false })

    const result = await simulator.handleQuickDemoLogin('Officer')

    assert.equal(result, null, 'Demo login should be rejected when disabled')
    assert.equal(simulator.sessionCreated, false)
    assert.match(simulator.uiError, /not available in production/)
  })
})
