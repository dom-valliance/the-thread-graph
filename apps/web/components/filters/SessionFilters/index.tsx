'use client';

import { useCallback } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

export default function SessionFilters() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const currentArc = searchParams.get('arc') ?? '';
  const currentPerson = searchParams.get('person') ?? '';
  const currentDateFrom = searchParams.get('date_from') ?? '';
  const currentDateTo = searchParams.get('date_to') ?? '';

  const updateParam = useCallback(
    (key: string, value: string) => {
      const params = new URLSearchParams(searchParams.toString());
      if (value) {
        params.set(key, value);
      } else {
        params.delete(key);
      }
      router.push(`?${params.toString()}`);
    },
    [router, searchParams],
  );

  const clearAll = useCallback(() => {
    router.push('?');
  }, [router]);

  const hasFilters = currentArc || currentPerson || currentDateFrom || currentDateTo;

  return (
    <div className="mb-6 flex flex-wrap items-end gap-4 rounded-lg border border-slate-200 bg-white p-4">
      <div className="flex flex-col gap-1">
        <label htmlFor="filter-arc" className="text-xs font-medium text-slate-600">
          Arc
        </label>
        <input
          id="filter-arc"
          type="text"
          placeholder="Filter by arc..."
          value={currentArc}
          onChange={(e) => updateParam('arc', e.target.value)}
          className="rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-900 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      </div>

      <div className="flex flex-col gap-1">
        <label htmlFor="filter-person" className="text-xs font-medium text-slate-600">
          Person
        </label>
        <input
          id="filter-person"
          type="text"
          placeholder="Filter by person..."
          value={currentPerson}
          onChange={(e) => updateParam('person', e.target.value)}
          className="rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-900 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      </div>

      <div className="flex flex-col gap-1">
        <label htmlFor="filter-date-from" className="text-xs font-medium text-slate-600">
          From
        </label>
        <input
          id="filter-date-from"
          type="date"
          value={currentDateFrom}
          onChange={(e) => updateParam('date_from', e.target.value)}
          className="rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      </div>

      <div className="flex flex-col gap-1">
        <label htmlFor="filter-date-to" className="text-xs font-medium text-slate-600">
          To
        </label>
        <input
          id="filter-date-to"
          type="date"
          value={currentDateTo}
          onChange={(e) => updateParam('date_to', e.target.value)}
          className="rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      </div>

      {hasFilters && (
        <button
          type="button"
          onClick={clearAll}
          className="rounded bg-slate-100 px-3 py-1.5 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-200"
        >
          Clear filters
        </button>
      )}
    </div>
  );
}
