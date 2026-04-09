'use client';

import { useQuery } from '@tanstack/react-query';
import { apiGet } from '@/lib/api-client';
import type { Topic } from '@/types/entities';

export function useTopics() {
  return useQuery({
    queryKey: ['topics'],
    queryFn: () => apiGet<Topic[]>('/topics'),
  });
}
