'use client';

import { useQuery } from '@tanstack/react-query';
import { getArcs, getArcDetail } from '@/lib/api-client';

export function useArcs() {
  return useQuery({
    queryKey: ['arcs'],
    queryFn: getArcs,
  });
}

export function useArcDetail(arcName: string) {
  return useQuery({
    queryKey: ['arcs', arcName],
    queryFn: () => getArcDetail(arcName),
    enabled: arcName.length > 0,
  });
}
