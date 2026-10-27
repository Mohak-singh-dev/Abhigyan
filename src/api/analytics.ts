/**
 * Analytics API Client
 * Interacts with FastAPI backend endpoints:
 * - GET /api/analytics/dashboard
 * - GET /api/analytics/reports
 */

import { apiClient } from './client'
import type { DashboardAnalyticsResponse, ReportsAnalyticsResponse } from '../types'

export interface AnalyticsFilterParams {
  bureau?: string
  startDate?: string
  endDate?: string
  asOfDate?: string
}

function buildQueryString(params?: AnalyticsFilterParams): string {
  if (!params) return ''
  const entries = Object.entries(params).filter(
    ([, v]) => v !== undefined && v !== null && v !== 'All' && v !== ''
  )
  if (entries.length === 0) return ''
  return '?' + entries.map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`).join('&')
}

/**
 * Fetch database-backed aggregate metrics for the dashboard.
 */
export async function fetchDashboardAnalyticsApi(
  params?: AnalyticsFilterParams
): Promise<DashboardAnalyticsResponse> {
  const query = buildQueryString(params)
  return apiClient.get<DashboardAnalyticsResponse>(`analytics/dashboard${query}`)
}

/**
 * Fetch database-backed reports analytics, time series trends, and redressal metrics.
 */
export async function fetchReportsAnalyticsApi(
  params?: AnalyticsFilterParams
): Promise<ReportsAnalyticsResponse> {
  const query = buildQueryString(params)
  return apiClient.get<ReportsAnalyticsResponse>(`analytics/reports${query}`)
}
