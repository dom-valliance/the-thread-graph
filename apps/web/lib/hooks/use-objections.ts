'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getObjectionPairs,
  createObjectionPair,
  updateObjectionPair,
  deleteObjectionPair,
} from '@/lib/api-client';
import type { ObjectionPairWithContext } from '@/types/entities';

export function useObjectionPairs(
  arcName?: string,
  initialData?: ObjectionPairWithContext[],
) {
  return useQuery({
    queryKey: ['objections', arcName],
    queryFn: () => getObjectionPairs(arcName),
    initialData,
  });
}

export function useCreateObjectionPair() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      objection_text: string;
      response_text: string;
      position_id: string;
    }) => createObjectionPair(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['objections'] });
    },
  });
}

export function useUpdateObjectionPair() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      pairId,
      data,
    }: {
      pairId: string;
      data: { objection_text: string; response_text: string };
    }) => updateObjectionPair(pairId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['objections'] });
    },
  });
}

export function useDeleteObjectionPair() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (pairId: string) => deleteObjectionPair(pairId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['objections'] });
    },
  });
}
