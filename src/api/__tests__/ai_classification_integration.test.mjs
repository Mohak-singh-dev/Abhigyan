/**
 * Abhigyan Frontend AI Classification Integration Tests
 * Validates frontend API client contracts against live FastAPI backend.
 */

import { test, describe, before } from 'node:test'
import assert from 'node:assert/strict'

const BASE_URL = process.env.VITE_API_URL || 'http://localhost:8000/api'

describe('Abhigyan Frontend AI Classification Client Integration', () => {
  let adminToken = ''

  before(async () => {
    // 1. Verify backend health
    const healthRes = await fetch(`${BASE_URL}/health`)
    assert.equal(healthRes.status, 200, 'Backend /health should be available')

    // 2. Obtain an authenticated token for test requests
    const loginRes = await fetch(`${BASE_URL}/auth/demo-login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ role: 'Complainant' }),
    })
    assert.equal(loginRes.status, 200, 'Demo login should succeed')
    const loginData = await loginRes.json()
    adminToken = loginData.accessToken
    assert.ok(adminToken, 'Access token must be present')
  })

  test('POST /api/complaints/classify returns advisory predictions for valid complaint', async () => {
    const payload = {
      title: 'Tuition fee overcharge and withholding caution money',
      description: 'The college has issued a notice demanding an extra fee of Rs 40,000 above the state cap and refuses to return caution deposit.',
    }

    const res = await fetch(`${BASE_URL}/complaints/classify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${adminToken}`,
      },
      body: JSON.stringify(payload),
    })

    assert.equal(res.status, 200)
    const data = await res.json()
    assert.equal(data.status, 'success')
    assert.ok(data.category, 'Predicted category must be present')
    assert.ok(data.bureau, 'Suggested bureau must be present')
    assert.ok(data.priority, 'Suggested priority must be present')
    assert.equal(typeof data.confidence, 'number')
    assert.ok(data.confidence >= 0 && data.confidence <= 1)
    assert.equal(typeof data.needsManualReview, 'boolean')
    assert.ok(data.advisoryNotice.includes('advisory'))
  })

  test('POST /api/complaints/classify safely handles short / empty input', async () => {
    const payload = {
      title: '   ',
      description: '   ',
    }

    const res = await fetch(`${BASE_URL}/complaints/classify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${adminToken}`,
      },
      body: JSON.stringify(payload),
    })

    assert.equal(res.status, 200)
    const data = await res.json()
    assert.equal(data.status, 'invalid_input')
    assert.equal(data.needsManualReview, true)
    assert.equal(data.confidence, 0.0)
  })

  test('POST /api/complaints/classify rejects unauthenticated request with 401', async () => {
    const res = await fetch(`${BASE_URL}/complaints/classify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: 'Valid title here',
        description: 'Valid description with sufficient details.',
      }),
    })

    assert.equal(res.status, 401)
  })

  test('POST /api/complaints records AI advisory fields while honoring user selections', async () => {
    const complaintPayload = {
      title: 'Hostel seniors hazing and extorting junior students',
      description: 'First year students are locked in dorms and beaten by seniors every night.',
      bureau: 'Approval',      // User deliberately picked Approval
      category: 'Curriculum',   // User deliberately picked Curriculum
      priority: 'Low',          // User deliberately picked Low
      institutionId: 'i1',
      complainantType: 'Student',
      complainantName: 'Rohit Sharma',
      complainantEmail: 'rohit.sharma@student.edu.in',
    }

    const res = await fetch(`${BASE_URL}/complaints`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${adminToken}`,
      },
      body: JSON.stringify(complaintPayload),
    })

    assert.equal(res.status, 201)
    const created = await res.json()

    // 1. User choices must be preserved exactly
    assert.equal(created.bureau, 'Approval')
    assert.equal(created.category, 'Curriculum')
    assert.equal(created.priority, 'Low')

    // 2. AI advisory predictions must be recorded
    assert.equal(created.aiClassificationRun, true)
    assert.ok(created.aiPredictedCategory, 'AI predicted category should be present')
    assert.ok(created.aiPredictedBureau, 'AI predicted bureau should be present')
    assert.equal(typeof created.aiConfidence, 'number')
    assert.equal(typeof created.aiNeedsManualReview, 'boolean')
  })
})
