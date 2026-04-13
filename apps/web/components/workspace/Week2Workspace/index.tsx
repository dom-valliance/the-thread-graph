'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { createPosition, updatePosition, lockPosition } from '@/lib/api-client';

const P1_V1_OPTIONS = ['P1', 'V1', 'both'] as const;

export default function Week2Workspace({
  sessionId,
  arcNumber,
}: {
  sessionId: string;
  arcNumber: number;
}) {
  const queryClient = useQueryClient();
  const [positionId, setPositionId] = useState<string | null>(null);
  const [isLocked, setIsLocked] = useState(false);
  const [text, setText] = useState('');
  const [antiPositionText, setAntiPositionText] = useState('');
  const [crossArcBridgeText, setCrossArcBridgeText] = useState('');
  const [p1V1Mapping, setP1V1Mapping] = useState('');

  const createMutation = useMutation({
    mutationFn: () =>
      createPosition({
        text,
        arc_number: arcNumber,
        session_id: sessionId,
        anti_position_text: antiPositionText || null,
        cross_arc_bridge_text: crossArcBridgeText || null,
        p1_v1_mapping: p1V1Mapping || null,
      }),
    onSuccess: (data: any) => {
      setPositionId(data.id);
      queryClient.invalidateQueries({ queryKey: ['positions'] });
    },
  });

  const saveMutation = useMutation({
    mutationFn: () =>
      updatePosition(positionId!, {
        text,
        anti_position_text: antiPositionText,
        cross_arc_bridge_text: crossArcBridgeText,
        p1_v1_mapping: p1V1Mapping,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['positions'] });
    },
  });

  const lockMutation = useMutation({
    mutationFn: () => lockPosition(positionId!, { locked_by: 'current-user' }),
    onSuccess: () => {
      setIsLocked(true);
      queryClient.invalidateQueries({ queryKey: ['positions'] });
    },
  });

  const canLock =
    positionId &&
    !isLocked &&
    text.trim() &&
    antiPositionText.trim() &&
    crossArcBridgeText.trim() &&
    p1V1Mapping;

  return (
    <div className="space-y-6">
      {isLocked && (
        <div className="rounded-lg border border-green-200 bg-green-50 px-4 py-2">
          <span className="text-sm font-medium text-green-700">Position locked</span>
        </div>
      )}

      <div className="rounded-lg border border-slate-200 bg-white p-6 space-y-4">
        <h3 className="text-lg font-semibold text-slate-900">Position Statement</h3>
        <textarea
          className="w-full rounded-md border border-slate-300 p-3 text-sm disabled:bg-slate-50"
          rows={6}
          placeholder="Your position on this arc's question..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          disabled={isLocked}
        />
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-6 space-y-4">
        <h3 className="text-lg font-semibold text-slate-900">Anti-Position</h3>
        <textarea
          className="w-full rounded-md border border-slate-300 p-3 text-sm disabled:bg-slate-50"
          rows={4}
          placeholder="The strongest argument against your position..."
          value={antiPositionText}
          onChange={(e) => setAntiPositionText(e.target.value)}
          disabled={isLocked}
        />
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-6 space-y-4">
        <h3 className="text-lg font-semibold text-slate-900">Cross-Arc Bridge</h3>
        <textarea
          className="w-full rounded-md border border-slate-300 p-3 text-sm disabled:bg-slate-50"
          rows={4}
          placeholder="How this position connects to other arcs..."
          value={crossArcBridgeText}
          onChange={(e) => setCrossArcBridgeText(e.target.value)}
          disabled={isLocked}
        />
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-6 space-y-4">
        <h3 className="text-lg font-semibold text-slate-900">P1/V1 Mapping</h3>
        <select
          className="rounded-md border border-slate-300 px-3 py-2 text-sm disabled:bg-slate-50"
          value={p1V1Mapping}
          onChange={(e) => setP1V1Mapping(e.target.value)}
          disabled={isLocked}
        >
          <option value="">Select mapping...</option>
          {P1_V1_OPTIONS.map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
      </div>

      {!isLocked && (
        <div className="flex gap-3">
          {!positionId ? (
            <button
              className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
              onClick={() => createMutation.mutate()}
              disabled={createMutation.isPending || !text.trim()}
            >
              {createMutation.isPending ? 'Creating...' : 'Create Position'}
            </button>
          ) : (
            <button
              className="rounded-md bg-slate-600 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700 disabled:opacity-50"
              onClick={() => saveMutation.mutate()}
              disabled={saveMutation.isPending}
            >
              {saveMutation.isPending ? 'Saving...' : 'Save'}
            </button>
          )}

          <button
            className="rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50"
            onClick={() => lockMutation.mutate()}
            disabled={!canLock || lockMutation.isPending}
          >
            {lockMutation.isPending ? 'Locking...' : 'Lock Position'}
          </button>
        </div>
      )}
    </div>
  );
}
