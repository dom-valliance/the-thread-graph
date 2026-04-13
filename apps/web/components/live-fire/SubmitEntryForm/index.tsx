'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { createLiveFireEntry } from '@/lib/api-client';

const OUTCOME_OPTIONS = [
  { value: 'used_successfully', label: 'Used Successfully' },
  { value: 'used_and_failed', label: 'Used and Failed' },
  { value: 'not_used', label: 'Not Used' },
] as const;

export default function SubmitEntryForm() {
  const queryClient = useQueryClient();
  const [isOpen, setIsOpen] = useState(false);
  const [positionId, setPositionId] = useState('');
  const [outcome, setOutcome] = useState('');
  const [context, setContext] = useState('');
  const [reporterEmail, setReporterEmail] = useState('');
  const [date, setDate] = useState(new Date().toISOString().slice(0, 10));

  const mutation = useMutation({
    mutationFn: () =>
      createLiveFireEntry({
        position_id: positionId,
        outcome,
        context,
        date,
        reporter_email: reporterEmail,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['live-fire'] });
      setIsOpen(false);
      setPositionId('');
      setOutcome('');
      setContext('');
    },
  });

  if (!isOpen) {
    return (
      <button
        className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        onClick={() => setIsOpen(true)}
      >
        Submit Live Fire Entry
      </button>
    );
  }

  const canSubmit = positionId && outcome && context && reporterEmail && date;

  return (
    <form
      onSubmit={(e) => { e.preventDefault(); mutation.mutate(); }}
      className="rounded-lg border border-slate-200 bg-white p-6 space-y-4"
    >
      <h3 className="text-lg font-semibold text-slate-900">New Live Fire Entry</h3>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label className="block text-xs font-medium text-slate-500 mb-1">Position ID</label>
          <input
            type="text"
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            placeholder="Position UUID"
            value={positionId}
            onChange={(e) => setPositionId(e.target.value)}
            required
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-500 mb-1">Outcome</label>
          <select
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            value={outcome}
            onChange={(e) => setOutcome(e.target.value)}
            required
          >
            <option value="">Select outcome...</option>
            {OUTCOME_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-500 mb-1">Reporter Email</label>
          <input
            type="email"
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            placeholder="you@valliance.com"
            value={reporterEmail}
            onChange={(e) => setReporterEmail(e.target.value)}
            required
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-500 mb-1">Date</label>
          <input
            type="date"
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            required
          />
        </div>
      </div>

      <div>
        <label className="block text-xs font-medium text-slate-500 mb-1">Context</label>
        <textarea
          className="w-full rounded-md border border-slate-300 p-3 text-sm"
          rows={3}
          placeholder="Anonymised client/prospect note..."
          value={context}
          onChange={(e) => setContext(e.target.value)}
          required
        />
      </div>

      <div className="flex gap-3">
        <button
          type="submit"
          disabled={!canSubmit || mutation.isPending}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {mutation.isPending ? 'Submitting...' : 'Submit'}
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
