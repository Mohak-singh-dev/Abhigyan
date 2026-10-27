/**
 * Users Management API Client (Phase 2)
 * Connects with FastAPI backend /api/users endpoints:
 * - GET /api/users (query personnel directory)
 * - GET /api/users/:id (lookup specific profile)
 * - POST /api/users (provision official user)
 * - PATCH /api/users/:id (update officer details and roles)
 * - PATCH /api/users/:id/status (toggle duty status)
 */

import { apiClient } from './client'
import type { Bureau, Role, UserProfile } from '../types'

export interface UserCreatePayload {
  name: string
  email: string
  role: Role
  bureau?: Bureau | 'All'
  designation?: string
  phone?: string
  status?: 'Active' | 'On Leave' | 'Inactive'
  department?: string
  password: string
}

export interface UserUpdatePayload {
  name?: string
  email?: string
  role?: Role
  bureau?: Bureau | 'All'
  designation?: string
  phone?: string
  status?: 'Active' | 'On Leave' | 'Inactive'
  department?: string
  password?: string
}

export interface UserQueryFilters {
  role?: string
  bureau?: string
  status?: string
  search?: string
}

export async function fetchUsersApi(filters?: UserQueryFilters): Promise<UserProfile[]> {
  const queryParams = new URLSearchParams()
  if (filters?.role && filters.role !== 'All') queryParams.append('role', filters.role)
  if (filters?.bureau && filters.bureau !== 'All') queryParams.append('bureau', filters.bureau)
  if (filters?.status && filters.status !== 'All') queryParams.append('status', filters.status)
  if (filters?.search && filters.search.trim()) queryParams.append('search', filters.search.trim())

  const queryString = queryParams.toString()
  const path = queryString ? `users?${queryString}` : 'users'
  return await apiClient.get<UserProfile[]>(path)
}

export async function getUserByIdApi(id: string): Promise<UserProfile> {
  return await apiClient.get<UserProfile>(`users/${encodeURIComponent(id)}`)
}

export async function createUserApi(payload: UserCreatePayload): Promise<UserProfile> {
  return await apiClient.post<UserProfile>('users', payload)
}

export async function updateUserApi(id: string, payload: UserUpdatePayload): Promise<UserProfile> {
  return await apiClient.patch<UserProfile>(`users/${encodeURIComponent(id)}`, payload)
}

export async function updateUserStatusApi(
  id: string,
  status: 'Active' | 'On Leave' | 'Inactive'
): Promise<UserProfile> {
  return await apiClient.patch<UserProfile>(`users/${encodeURIComponent(id)}/status`, { status })
}
