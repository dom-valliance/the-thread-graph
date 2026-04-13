'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getCycles,
  getCurrentCycle,
  getCycleSchedule,
  createCycle,
  updateSessionAssignment,
} from '@/lib/api-client';

export function useCycles() {
  return useQuery({
    queryKey: ['cycles'],
    queryFn: getCycles,
  });
}

export function useCurrentCycle() {
  return useQuery({
    queryKey: ['cycles', 'current'],
    queryFn: getCurrentCycle,
  });
}

export function useCycleSchedule(cycleId: string | undefined) {
  return useQuery({
    queryKey: ['cycles', cycleId, 'schedule'],
    queryFn: () => getCycleSchedule(cycleId!),
    enabled: !!cycleId,
  });
}

export function useCreateCycle() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { number: number; start_date: string; status?: string }) =>
      createCycle(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cycles'] });
    },
  });
}

export function useUpdateAssignment(cycleId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: {
      sessionId: string;
      lead_email?: string | null;
      shadow_email?: string | null;
    }) =>
      updateSessionAssignment(cycleId, data.sessionId, {
        lead_email: data.lead_email,
        shadow_email: data.shadow_email,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cycles', cycleId, 'schedule'] });
      queryClient.invalidateQueries({ queryKey: ['cycles', 'current'] });
    },
  });
}
