'use client';

import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { createBrief, getBrief, updateBrief, lockBrief } from '@/lib/api-client';

export default function Week1Workspace({
  sessionId,
  arcName,
}: {
  sessionId: string;
  arcName: string;
}) {
  const queryClient = useQueryClient();
  const [briefId, setBriefId] = useState<string | null>(null);
  const [problemStatement, setProblemStatement] = useState('');
  const [criteria, setCriteria] = useState('');
  const [steelmanSummary, setSteelmanSummary] = useState('');

  const { data: brief } = useQuery({
    queryKey: ['briefs', briefId],
    queryFn: () => getBrief(briefId!),
    enabled: !!briefId,
  });

  const isLocked = brief?.status === 'locked';

  const createMutation = useMutation({
    mutationFn: () =>
      createBrief({
        problem_statement: problemStatement,
        landscape_criteria: criteria.split('\n').filter(Boolean),
        steelman_summary: steelmanSummary,
        session_id: sessionId,
        arc_name: arcName,
      }),
    onSuccess: (data) => {
      setBriefId(data.id);
      queryClient.invalidateQueries({ queryKey: ['briefs'] });
    },
  });

  const saveMutation = useMutation({
    mutationFn: () =>
      updateBrief(briefId!, {
        problem_statement: problemStatement,
        landscape_criteria: criteria.split('\n').filter(Boolean),
        steelman_summary: steelmanSummary,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['briefs', briefId] });
    },
  });

  const lockMutation = useMutation({
    mutationFn: () => lockBrief(briefId!, { locked_by: 'current-user' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['briefs', briefId] });
    },
  });

  const canLock =
    briefId &&
    !isLocked &&
    problemStatement.trim() &&
    criteria.trim() &&
    steelmanSummary.trim();

  return (
    <div className="space-y-6">
      {isLocked && (
        <div className="rounded-lg border border-green-200 bg-green-50 px-4 py-2">
          <span className="text-sm font-medium text-green-700">
            Locked on {brief?.locked_date} by {brief?.locked_by}
          </span>
        </div>
      )}

      <div className="rounded-lg border border-slate-200 bg-white p-6 space-y-4">
        <h3 className="text-lg font-semibold text-slate-900">Problem Statement</h3>
        <textarea
          className="w-full rounded-md border border-slate-300 p-3 text-sm disabled:bg-slate-50"
          rows={4}
          placeholder="2-3 sentences defining the problem..."
          value={problemStatement}
          onChange={(e) => setProblemStatement(e.target.value)}
          disabled={isLocked}
        />
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-6 space-y-4">
        <h3 className="text-lg font-semibold text-slate-900">Landscape Criteria</h3>
        <p className="text-xs text-slate-500">One criterion per line.</p>
        <textarea
          className="w-full rounded-md border border-slate-300 p-3 text-sm disabled:bg-slate-50"
          rows={6}
          placeholder="Evaluation dimensions..."
          value={criteria}
          onChange={(e) => setCriteria(e.target.value)}
          disabled={isLocked}
        />
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-6 space-y-4">
        <h3 className="text-lg font-semibold text-slate-900">Steelman Summary</h3>
        <textarea
          className="w-full rounded-md border border-slate-300 p-3 text-sm disabled:bg-slate-50"
          rows={4}
          placeholder="Best argument for the strongest competitor..."
          value={steelmanSummary}
          onChange={(e) => setSteelmanSummary(e.target.value)}
          disabled={isLocked}
        />
      </div>

      {!isLocked && (
        <div className="flex gap-3">
          {!briefId ? (
            <button
              className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
              onClick={() => createMutation.mutate()}
              disabled={createMutation.isPending || !problemStatement.trim()}
            >
              {createMutation.isPending ? 'Creating...' : 'Create Brief'}
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
            {lockMutation.isPending ? 'Locking...' : 'Lock Brief'}
          </button>
        </div>
      )}
    </div>
  );
}
