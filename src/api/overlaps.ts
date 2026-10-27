/**
 * Overlaps API Service
 * Interacts with FastAPI backend endpoints:
 * - GET /api/overlaps
 * - GET /api/overlaps/{id}
 * - PATCH /api/overlaps/{id}/decision
 * - GET /api/overlaps/linked/{complaint_id}
 */

import { apiClient } from './client'
import type { Overlap, LinkedDocket, Bureau } from '../types'

export interface OverlapDecisionPayload {
  state: 'linked' | 'dismissed' | 'deferred' | 'open' | 'reset'
  justification?: string
}

interface BackendOverlapRead {
  id: string
  complaint_a_id: string
  complaint_b_id: string
  a: string
  b: string
  similarity: number
  reasons: string[]
  status: string
  decision_state?: string
  justification?: string
  reviewed_by?: string
  reviewed_by_user_id?: string
  reviewed_at?: string
  created_at: string
  updated_at: string
}

interface BackendLinkedDocketRead {
  overlap_id: string
  case_id: string
  bureau: string
  title: string
  similarity: number
  justification?: string
  confirmed_by?: string
  confirmed_at?: string
}

function mapBackendOverlap(item: BackendOverlapRead): Overlap {
  return {
    id: item.id,
    a: item.a || item.complaint_a_id,
    b: item.b || item.complaint_b_id,
    similarity: item.similarity,
    reasons: item.reasons || [],
    status: (item.status as Overlap['status']) || 'open',
    decisionNote: item.justification,
    justification: item.justification,
    reviewedBy: item.reviewed_by,
    reviewedDate: item.reviewed_at ? item.reviewed_at.slice(0, 10) : undefined,
    notes: item.justification,
  }
}

export async function getOverlapsApi(params?: {
  bureau?: string
  status?: string
  minSimilarity?: number
  includeBelowThreshold?: boolean
}): Promise<Overlap[]> {
  const query = new URLSearchParams()
  if (params?.bureau && params.bureau !== 'All') {
    query.set('bureau', params.bureau)
  }
  if (params?.status && params.status !== 'All') {
    query.set('status', params.status)
  }
  if (params?.minSimilarity !== undefined) {
    query.set('min_similarity', String(params.minSimilarity))
  }
  if (params?.includeBelowThreshold !== undefined) {
    query.set('include_below_threshold', String(params.includeBelowThreshold))
  }
  const queryString = query.toString() ? `?${query.toString()}` : ''
  const data = await apiClient.get<BackendOverlapRead[]>(`/overlaps${queryString}`)
  return (data || []).map(mapBackendOverlap)
}

export async function getOverlapByIdApi(id: string): Promise<Overlap> {
  const data = await apiClient.get<BackendOverlapRead>(`/overlaps/${encodeURIComponent(id)}`)
  return mapBackendOverlap(data)
}

export async function updateOverlapDecisionApi(
  id: string,
  payload: OverlapDecisionPayload
): Promise<Overlap> {
  const data = await apiClient.patch<BackendOverlapRead>(
    `/overlaps/${encodeURIComponent(id)}/decision`,
    payload
  )
  return mapBackendOverlap(data)
}

export async function getLinkedDocketsApi(complaintId: string): Promise<LinkedDocket[]> {
  const data = await apiClient.get<BackendLinkedDocketRead[]>(
    `/overlaps/linked/${encodeURIComponent(complaintId)}`
  )
  return (data || []).map((item: BackendLinkedDocketRead) => ({
    overlapId: item.overlap_id,
    caseId: item.case_id,
    bureau: item.bureau as Bureau,
    title: item.title,
    similarity: item.similarity,
    justification: item.justification,
    confirmedBy: item.confirmed_by,
    confirmedAt: item.confirmed_at,
  }))
}
