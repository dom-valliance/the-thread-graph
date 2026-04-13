'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { createForgeAssignment } from '@/lib/api-client';

const ARTEFACT_TYPES = [
  'briefing',
  'comparison_framework',
  'market_map',
  'viewpoint_article',
  'credentials_section',
  'pitch_script',
  'one_pager',
  'objection_cards',
] as const;

export default function CreateAssignmentForm() {
  const queryClient = useQueryClient();
  const [isOpen, setIsOpen] = useState(false);
  const [artefactType, setArtefactType] = useState('');
  const [deadline, setDeadline] = useState('');
  const [assignedToEmail, setAssignedToEmail] = useState('');
  const [sessionId, setSessionId] = useState('');
  const [arcName, setArcName] = useState('');

  const mutation = useMutation({
    mutationFn: () =>
      createForgeAssignment({
        artefact_type: artefactType,
        deadline,
        assigned_to_email: assignedToEmail,
        session_id: sessionId,
        arc_name: arcName,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['forge'] });
      setIsOpen(false);
      setArtefactType('');
      setDeadline('');
      setAssignedToEmail('');
      setSessionId('');
      setArcName('');
    },
  });

  if (!isOpen) {
    return (
      <button
        className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        onClick={() => setIsOpen(true)}
      >
        New Assignment
      </button>
    );
  }

  const canSubmit = artefactType && deadline && assignedToEmail && sessionId && arcName;

  return (
    <form
      onSubmit={(e) => { e.preventDefault(); mutation.mutate(); }}
      className="rounded-lg border border-slate-200 bg-white p-6 space-y-4"
    >
      <h3 className="text-lg font-semibold text-slate-900">New Forge Assignment</h3>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label className="block text-xs font-medium text-slate-500 mb-1">Artefact Type</label>
          <select
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            value={artefactType}
            onChange={(e) => setArtefactType(e.target.value)}
            required
          >
            <option value="">Select type...</option>
            {ARTEFACT_TYPES.map((t) => (
              <option key={t} value={t}>{t.replace(/_/g, ' ')}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-500 mb-1">Deadline</label>
          <input
            type="date"
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            value={deadline}
            onChange={(e) => setDeadline(e.target.value)}
            required
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-500 mb-1">Assigned To (email)</label>
          <input
            type="email"
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            placeholder="person@valliance.com"
            value={assignedToEmail}
            onChange={(e) => setAssignedToEmail(e.target.value)}
            required
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-500 mb-1">Arc Name</label>
          <input
            type="text"
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            placeholder="e.g. Agentic AI"
            value={arcName}
            onChange={(e) => setArcName(e.target.value)}
            required
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-500 mb-1">Session ID</label>
          <input
            type="text"
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            placeholder="e.g. ss-c1-w1"
            value={sessionId}
            onChange={(e) => setSessionId(e.target.value)}
            required
          />
        </div>
      </div>

      <div className="flex gap-3">
        <button
          type="submit"
          disabled={!canSubmit || mutation.isPending}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {mutation.isPending ? 'Creating...' : 'Create'}
        </button>
        <button
          type="button"
          className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
          onClick={() => setIsOpen(false)}
        >
          Cancel
        </button>
      </div>

      {mutation.isError && (
        <p className="text-sm text-red-600">{(mutation.error as Error).message}</p>
      )}
    </form>
  );
}
