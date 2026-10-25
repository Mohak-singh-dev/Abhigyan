/**
 * Abhigyan Frontend Authentication Integration Tests
 * Validates frontend API client contracts against live FastAPI backend.
 */

import { test, describe, before } from 'node:test'
import assert from 'node:assert/strict'

const BASE_URL = process.env.VITE_API_URL || 'http://localhost:8000/api'

describe('Abhigyan Frontend Authentication Client Integration', () => {
  before(async () => {
    // Verify health before running integration tests
    const res = await fetch(`${BASE_URL}/health`)
    assert.equal(res.status, 200, 'Backend /health should be available')
    const health = await res.json()
    assert.equal(health.status, 'healthy')
  })

  test('POST /api/auth/login succeeds with valid seed credentials', async () => {
    const res = await fetch(`${BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: 'member-sec@aicte-india.org',
        password: 'AicteDemo@2026',
      }),
    })

    assert.equal(res.status, 200)
    const data = await res.json()
    assert.ok(data.accessToken, 'Should return accessToken')
    assert.equal(data.tokenType, 'bearer')
    assert.equal(data.user.email, 'member-sec@aicte-india.org')
    assert.equal(data.user.role, 'Admin')
    assert.equal(data.user.name, 'Dr. S. Mehta')
  })

  test('POST /api/auth/login returns 401 on incorrect password', async () => {
    const res = await fetch(`${BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: 'member-sec@aicte-india.org',
        password: 'IncorrectPassword',
      }),
    })

    assert.equal(res.status, 401)
    const data = await res.json()
    assert.equal(data.detail, 'Invalid email or password.')
  })

  test('POST /api/auth/login returns 401 on non-existent account', async () => {
    const res = await fetch(`${BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: 'nonexistent.user@aicte-india.org',
        password: 'AicteDemo@2026',
      }),
    })

    assert.equal(res.status, 401)
    const data = await res.json()
    assert.equal(data.detail, 'Invalid email or password.')
  })

  test('POST /api/auth/demo-login authenticates each supported role perspective', async () => {
    const rolesToTest = [
      { role: 'Admin', expectedName: 'Dr. S. Mehta', expectedRole: 'Admin' },
      { role: 'BureauAdmin', expectedName: 'Dr. Priya Nair', expectedRole: 'BureauAdmin' },
      { role: 'Officer', expectedName: 'Rajesh Kumar', expectedRole: 'Officer' },
      { role: 'Complainant', expectedName: 'Rohit Sharma', expectedRole: 'Complainant' },
    ]

    for (const target of rolesToTest) {
      const res = await fetch(`${BASE_URL}/auth/demo-login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role: target.role }),
      })

      assert.equal(res.status, 200, `Demo login for ${target.role} should succeed`)
      const data = await res.json()
      assert.ok(data.accessToken, `Token returned for ${target.role}`)
      assert.equal(data.user.role, target.expectedRole)
      assert.equal(data.user.name, target.expectedName)
    }
  })

  test('GET /api/auth/me returns authenticated user with valid Bearer token', async () => {
    // 1. Log in to get token
    const loginRes = await fetch(`${BASE_URL}/auth/demo-login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ role: 'Officer' }),
    })
    const { accessToken, user } = await loginRes.json()

    // 2. Fetch /api/auth/me with Authorization Bearer header
    const meRes = await fetch(`${BASE_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    })

    assert.equal(meRes.status, 200)
    const profile = await meRes.json()
    assert.equal(profile.id, user.id)
    assert.equal(profile.email, user.email)
    assert.equal(profile.role, 'Officer')
    assert.equal(profile.name, 'Rajesh Kumar')
    assert.equal(typeof profile.activeCasesCount, 'number')
  })

  test('GET /api/auth/me returns 401 when token is missing or malformed', async () => {
    const resNoToken = await fetch(`${BASE_URL}/auth/me`)
    assert.equal(resNoToken.status, 401)

    const resInvalidToken = await fetch(`${BASE_URL}/auth/me`, {
      headers: { Authorization: 'Bearer invalid-garbage-token-12345' },
    })
    assert.equal(resInvalidToken.status, 401)
  })
})
