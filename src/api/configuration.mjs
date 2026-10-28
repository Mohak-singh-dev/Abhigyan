export function resolveApiBaseUrl(rawUrl, isProduction) {
  const configuredUrl = typeof rawUrl === 'string' ? rawUrl.trim().replace(/\/$/, '') : ''
  if (!configuredUrl) return isProduction ? '' : 'http://localhost:8000/api'

  let parsedUrl
  try {
    parsedUrl = new URL(configuredUrl)
  } catch {
    throw new Error('VITE_API_URL must be an absolute http(s) URL.')
  }

  if (!['http:', 'https:'].includes(parsedUrl.protocol)) {
    throw new Error('VITE_API_URL must use http or https.')
  }
  if (isProduction && (
    parsedUrl.protocol !== 'https:' ||
    /^(localhost|127\.0\.0\.1|0\.0\.0\.0)$/i.test(parsedUrl.hostname) ||
    parsedUrl.username || parsedUrl.password ||
    !parsedUrl.pathname.replace(/\/$/, '').endsWith('/api')
  )) {
    throw new Error('Production VITE_API_URL must use HTTPS, a public backend hostname, and end in /api.')
  }

  return configuredUrl
}
