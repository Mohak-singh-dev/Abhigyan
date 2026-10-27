/**
 * Complaints API Service
 * Interacts with FastAPI backend endpoints:
 * - POST /api/complaints/classify (AI Advisory Preview)
 * - GET /api/complaints
 * - POST /api/complaints
 * - GET /api/complaints/{id}
 * - GET /api/complaints/{id}/timeline
 * - POST /api/complaints/{id}/timeline
 * - PATCH /api/complaints/{id}/status
 * - PATCH /api/complaints/{id}/assign
 */

import { apiClient } from './client'
import type {
  AIClassificationResult,
  AIClassifyPayload,
  Complaint,
  Status,
  TimelineEvent,
} from '../types'

export interface ComplaintStatusUpdatePayload {
  status: Status
  remarks?: string
  note?: string
  overrideReason?: string
}

export interface ComplaintAssignPayload {
  officer?: string
  userId?: string
  bureau?: string
  reason?: string
  preserveBureau?: boolean
}

export interface TimelineNoteCreatePayload {
  note: string
  label?: string
}

export interface ComplaintCreatePayload {
  id?: string
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

export interface ComplaintListResponse {
  items: Complaint[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}

/**
 * Preview AI-based complaint classification without creating or modifying database records.
 */
export async function classifyComplaintPreview(
  payload: AIClassifyPayload
): Promise<AIClassificationResult> {
  return apiClient.post<AIClassificationResult>('/complaints/classify', payload)
}

export async function fetchComplaintsApi(params?: Record<string, string | number>): Promise<ComplaintListResponse> {
  const query = params
    ? '?' +
      Object.entries(params)
        .filter(([, v]) => v !== undefined && v !== null && v !== 'All' && v !== '')
        .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`)
        .join('&')
    : ''
  return apiClient.get<ComplaintListResponse>(`complaints${query}`)
}

export const listComplaintsApi = fetchComplaintsApi

export async function fetchComplaintByIdApi(id: string): Promise<Complaint> {
  return apiClient.get<Complaint>(`complaints/${encodeURIComponent(id)}`)
}

export const getComplaintApi = fetchComplaintByIdApi

export async function createComplaintApi(payload: ComplaintCreatePayload): Promise<Complaint> {
  return apiClient.post<Complaint>('complaints', payload)
}

export async function updateComplaintStatusApi(
  id: string,
  payload: ComplaintStatusUpdatePayload
): Promise<Complaint> {
  return apiClient.patch<Complaint>(`complaints/${encodeURIComponent(id)}/status`, payload)
}

export async function assignComplaintApi(
  id: string,
  payload: ComplaintAssignPayload
): Promise<Complaint> {
  return apiClient.patch<Complaint>(`complaints/${encodeURIComponent(id)}/assign`, payload)
}

export async function addComplaintTimelineNoteApi(
  id: string,
  payload: TimelineNoteCreatePayload
): Promise<TimelineEvent> {
  return apiClient.post<TimelineEvent>(`complaints/${encodeURIComponent(id)}/timeline`, payload)
}
