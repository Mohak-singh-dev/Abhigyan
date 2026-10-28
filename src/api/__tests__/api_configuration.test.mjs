import assert from 'node:assert/strict'
import test from 'node:test'
import { resolveApiBaseUrl } from '../configuration.mjs'

test('development keeps the localhost API default', () => {
  assert.equal(resolveApiBaseUrl(undefined, false), 'http://localhost:8000/api')
})

test('production without an API URL is unconfigured instead of using localhost', () => {
  assert.equal(resolveApiBaseUrl(undefined, true), '')
})

test('configured API URL is preserved without a trailing slash', () => {
  assert.equal(resolveApiBaseUrl('https://api.example.com/api/', true), 'https://api.example.com/api')
})

test('production rejects insecure and localhost API URLs', () => {
  assert.throws(() => resolveApiBaseUrl('http://api.example.com/api', true), /HTTPS/)
  assert.throws(() => resolveApiBaseUrl('https://localhost:8000/api', true), /public backend/)
  assert.throws(() => resolveApiBaseUrl('https://api.example.com', true), /end in \/api/)
})

test('malformed API URLs are rejected', () => {
  assert.throws(() => resolveApiBaseUrl('/api', true), /absolute http\(s\) URL/)
})
