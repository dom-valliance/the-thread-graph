'use client';

import { useQuery } from '@tanstack/react-query';
import { apiGet } from '@/lib/api-client';
import type { Session } from '@/types/entities';

export interface SessionFilters {
  theme?: string;
  person?: string;
  dateFrom?: string;
  dateTo?: string;
}

function buildQueryString(filters?: SessionFilters): string {
  if (!filters) return '';

  const params = new URLSearchParams();
  if (filters.theme) params.set('arc', filters.theme);
  if (filters.person) params.set('person', filters.person);
  if (filters.dateFrom) params.set('date_from', filters.dateFrom);
  if (filters.dateTo) params.set('date_to', filters.dateTo);

  const qs = params.toString();
  return qs ? `?${qs}` : '';
}

export function useSessions(filters?: SessionFilters) {
  return useQuery({
    queryKey: ['sessions', filters],
    queryFn: () => apiGet<Session[]>(`/sessions${buildQueryString(filters)}`),
  });
}
