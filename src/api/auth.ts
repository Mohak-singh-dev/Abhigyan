/**
 * Authentication API Service
 * Interacts with FastAPI /api/auth endpoints: /login, /demo-login, and /me.
 */

import {
  apiClient,
  clearAuthToken,
  setAuthToken,
  getAuthToken,
  AUTH_USER_KEY,
} from './client'
import type { Role, UserProfile } from '../types'

export interface LoginPayload {
  email: string
  password: string
}

export interface DemoLoginPayload {
  userId?: string
  email?: string
  role?: string
}

export interface RegisterPayload {
  name: string
  email: string
  password: string
  phone?: string
  complainantType?: string
}

export interface TokenResponse {
  accessToken: string
  tokenType: string
  expiresIn: number
  user: UserProfile
}

/**
 * Authenticate with email and password via POST /api/auth/login.
 */
export async function loginApi(payload: LoginPayload): Promise<TokenResponse> {
  const response = await apiClient.post<TokenResponse>('auth/login', payload)
  if (response?.accessToken) {
    setAuthToken(response.accessToken)
    try {
      localStorage.setItem(AUTH_USER_KEY, JSON.stringify(response.user))
    } catch {
      // ignore storage failure
    }
  }
  return response
}

/**
 * Register a new citizen/complainant account via POST /api/auth/register.
 * Always assigns Complainant role and logs in the user immediately upon creation.
 */
export async function registerApi(payload: RegisterPayload): Promise<TokenResponse> {
  const response = await apiClient.post<TokenResponse>('auth/register', payload)
  if (response?.accessToken) {
    setAuthToken(response.accessToken)
    try {
      localStorage.setItem(AUTH_USER_KEY, JSON.stringify(response.user))
    } catch {
      // ignore storage failure
    }
  }
  return response
}

/**
 * Development-only demo authentication via POST /api/auth/demo-login.
 */
export async function demoLoginApi(payload: DemoLoginPayload): Promise<TokenResponse> {
  const response = await apiClient.post<TokenResponse>('auth/demo-login', payload)
  if (response?.accessToken) {
    setAuthToken(response.accessToken)
    try {
      localStorage.setItem(AUTH_USER_KEY, JSON.stringify(response.user))
    } catch {
      // ignore storage failure
    }
  }
  return response
}

/**
 * Fetch profile of currently authenticated user via GET /api/auth/me.
 */
export async function getCurrentUserApi(): Promise<UserProfile> {
  const user = await apiClient.get<UserProfile>('auth/me')
  try {
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user))
  } catch {
    // ignore
  }
  return user
}

/**
 * Sign out user and remove stored credentials.
 */
export function logoutAuth(): void {
  clearAuthToken()
  try {
    localStorage.removeItem(AUTH_USER_KEY)
  } catch {
    // ignore
  }
}

/**
 * Check if a token currently exists in storage.
 */
export function hasStoredToken(): boolean {
  return Boolean(getAuthToken())
}
