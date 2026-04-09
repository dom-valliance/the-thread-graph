'use client';

import { useQuery } from '@tanstack/react-query';
import { apiGet } from '@/lib/api-client';
import type { Argument } from '@/types/entities';

export interface PositionWithArguments {
  id: string;
  text: string;
  status: string;
  arguments: Argument[];
}

export function usePositionArguments(positionId: string) {
  return useQuery({
    queryKey: ['positions', positionId, 'arguments'],
    queryFn: () => apiGet<PositionWithArguments>(`/positions/${positionId}/arguments`),
    enabled: positionId.length > 0,
  });
}
