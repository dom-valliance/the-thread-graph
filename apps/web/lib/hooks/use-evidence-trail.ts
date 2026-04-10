'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getEvidenceTrail,
  createEvidence,
  updateEvidence,
  deleteEvidence,
} from '@/lib/api-client';
import type { EvidenceTrailResponse } from '@/types/entities';

export function useEvidenceTrail(positionId: string) {
  return useQuery({
    queryKey: ['evidence-trail', positionId],
    queryFn: () => getEvidenceTrail(positionId),
    enabled: positionId.length > 0,
  });
}

export function useCreateEvidence() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      text: string;
      type: string;
      position_id: string;
      source_bookmark_id?: string | null;
    }) => createEvidence(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['evidence-trail'] });
    },
  });
}

export function useUpdateEvidence() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      evidenceId,
      data,
    }: {
      evidenceId: string;
      data: { text: string; type: string; source_bookmark_id?: string | null };
    }) => updateEvidence(evidenceId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['evidence-trail'] });
    },
  });
}

export function useDeleteEvidence() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (evidenceId: string) => deleteEvidence(evidenceId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['evidence-trail'] });
    },
  });
}
