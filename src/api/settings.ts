/**
 * Settings API Client
 * Interacts with FastAPI backend endpoints:
 * - GET /api/settings
 * - PUT /api/settings
 * - POST /api/settings/reset
 */

import { apiClient } from './client'
import type { AppSettings } from '../types'

export interface BackendSettingRead {
  key?: string
  similarity_threshold: number
  sla_critical: number
  sla_high: number
  sla_medium: number
  auto_escalate: boolean
  email_alerts: boolean
  similarityThreshold?: number
  slaCritical?: number
  slaHigh?: number
  slaMedium?: number
  autoEscalate?: boolean
  emailAlerts?: boolean
  updated_at?: string
  updatedAt?: string
  updated_by?: string
  updatedBy?: string
}

export function mapBackendSettings(res: BackendSettingRead): AppSettings {
  return {
    similarityThreshold: res.similarityThreshold ?? res.similarity_threshold ?? 75,
    slaCritical: res.slaCritical ?? res.sla_critical ?? 3,
    slaHigh: res.slaHigh ?? res.sla_high ?? 7,
    slaMedium: res.slaMedium ?? res.sla_medium ?? 14,
    autoEscalate: res.autoEscalate ?? res.auto_escalate ?? true,
    emailAlerts: res.emailAlerts ?? res.email_alerts ?? true,
    updatedAt: res.updatedAt ?? res.updated_at,
    updatedBy: res.updatedBy ?? res.updated_by,
  }
}

export async function getSettingsApi(): Promise<AppSettings> {
  const data = await apiClient.get<BackendSettingRead>('/settings')
  return mapBackendSettings(data)
}

export async function updateSettingsApi(settings: Partial<AppSettings>): Promise<AppSettings> {
  const payload = {
    similarityThreshold: settings.similarityThreshold,
    slaCritical: settings.slaCritical,
    slaHigh: settings.slaHigh,
    slaMedium: settings.slaMedium,
    autoEscalate: settings.autoEscalate,
    emailAlerts: settings.emailAlerts,
  }
  const data = await apiClient.put<BackendSettingRead>('/settings', payload)
  return mapBackendSettings(data)
}

export async function resetSettingsApi(): Promise<AppSettings> {
  const data = await apiClient.post<BackendSettingRead>('/settings/reset', {})
  return mapBackendSettings(data)
}
