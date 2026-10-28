import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), 'VITE_')
  const configuredApiUrl = env.VITE_API_URL?.trim()
  if (mode === 'production' && configuredApiUrl) {
    let apiUrl: URL
    try {
      apiUrl = new URL(configuredApiUrl)
    } catch {
      throw new Error('Production VITE_API_URL must be an absolute HTTPS API URL ending in /api.')
    }
    if (
      apiUrl.protocol !== 'https:' ||
      /^(localhost|127\.0\.0\.1|0\.0\.0\.0)$/i.test(apiUrl.hostname) ||
      apiUrl.username || apiUrl.password ||
      !apiUrl.pathname.replace(/\/$/, '').endsWith('/api')
    ) {
      throw new Error('Production VITE_API_URL must use HTTPS, a public backend hostname, and end in /api.')
    }
  }
  return { plugins: [react()] }
})
