import { apiClient } from './client'
import type { Institution } from '../types'

export function fetchInstitutionsApi(): Promise<Institution[]> {
  return apiClient.get<Institution[]>('institutions')
}
