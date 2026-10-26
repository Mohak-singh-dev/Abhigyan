/**
 * Abhigyan Frontend Complaints API Module
 * Provides contract functions for complaint classification preview, submission, and querying.
 */

import { apiClient } from './client'
import type { AIClassificationResult, AIClassifyPayload, Complaint } from '../types'

/**
 * Preview AI-based complaint classification without creating or modifying any database records.
 */
export async function classifyComplaintPreview(
  payload: AIClassifyPayload
): Promise<AIClassificationResult> {
  return apiClient.post<AIClassificationResult>('/complaints/classify', payload)
}

export interface ComplaintCreatePayload {
  title: string
  description: string
  bureau: string
  category: string
  priority: string
  institutionId: string
  institutionPermanentId?: string
  complainantType?: string
  complainantName?: string
  complainantEmail?: string
  complainantPhone?: string
  remarks?: string
}

/**
 * Create a new complaint via backend API with server-side AI advisory recording.
 */
export async function createComplaintApi(
  payload: ComplaintCreatePayload
): Promise<Complaint> {
  return apiClient.post<Complaint>('/complaints', payload)
}

/**
 * Retrieve paginated list of complaints from the backend.
 */
export async function listComplaintsApi(params?: Record<string, string | number>): Promise<{
  items: Complaint[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}> {
  const query = params
    ? '?' +
      Object.entries(params)
        .filter(([_, v]) => v !== undefined && v !== null && v !== '')
        .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`)
        .join('&')
    : ''
  return apiClient.get(`/complaints${query}`)
}

/**
 * Retrieve a single complaint by its Case ID.
 */
export async function getComplaintApi(id: string): Promise<Complaint> {
  return apiClient.get<Complaint>(`/complaints/${encodeURIComponent(id)}`)
}
