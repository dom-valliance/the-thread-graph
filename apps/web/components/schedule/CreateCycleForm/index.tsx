'use client';

import { useState } from 'react';
import { useCreateCycle } from '@/lib/hooks/use-cycles';
import type { Cycle } from '@/types/entities';

export default function CreateCycleForm({
  existingCycles,
}: {
  existingCycles: Cycle[];
}) {
  const nextNumber = existingCycles.length > 0
    ? Math.max(...existingCycles.map((c) => c.number)) + 1
    : 1;

  const [number, setNumber] = useState(nextNumber);
  const [startDate, setStartDate] = useState('');
  const [status, setStatus] = useState('active');
  const [isOpen, setIsOpen] = useState(false);

  const createMutation = useCreateCycle();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!startDate) return;
    createMutation.mutate(
      { number, start_date: startDate, status },
      { onSuccess: () => setIsOpen(false) },
    );
  };

  if (!isOpen) {
    return (
      <button
        className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        onClick={() => setIsOpen(true)}
      >
        Create New Cycle
      </button>
    );
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="rounded-lg border border-slate-200 bg-white p-6 space-y-4"
    >
      <h3 className="text-lg font-semibold text-slate-900">New Cycle</h3>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div>
          <label className="block text-xs font-medium text-slate-500 mb-1">
            Cycle Number
          </label>
          <input
            type="number"
            min={1}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            value={number}
            onChange={(e) => setNumber(parseInt(e.target.value, 10))}
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-500 mb-1">
            Start Date (first Friday)
          </label>
          <input
            type="date"
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            required
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-500 mb-1">
            Status
          </label>
          <select
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            value={status}
            onChange={(e) => setStatus(e.target.value)}
          >
            <option value="active">Active</option>
            <option value="upcoming">Upcoming</option>
          </select>
        </div>
      </div>

      <div className="flex gap-3">
        <button
          type="submit"
          disabled={createMutation.isPending || !startDate}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {createMutation.isPending ? 'Creating...' : 'Create Cycle'}
        </button>
        <button
          type="button"
          className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
          onClick={() => setIsOpen(false)}
        >
          Cancel
        </button>
      </div>

      {createMutation.isError && (
        <p className="text-sm text-red-600">
          {(createMutation.error as Error).message}
        </p>
      )}
    </form>
  );
}
