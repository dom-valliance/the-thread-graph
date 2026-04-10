'use client';

import { useSearchParams } from 'next/navigation';
import { useSessions } from '@/lib/hooks/use-sessions';
import SessionFilters from '@/components/filters/SessionFilters';
import SessionTimeline from '@/components/graph/SessionTimeline';

export default function SessionsView() {
  const searchParams = useSearchParams();

  const arc = searchParams.get('arc') ?? undefined;
  const person = searchParams.get('person') ?? undefined;
  const dateFrom = searchParams.get('date_from') ?? undefined;
  const dateTo = searchParams.get('date_to') ?? undefined;

  const { data: sessions, isLoading } = useSessions({
    arc: arc ?? undefined,
    person,
    dateFrom,
    dateTo,
  });

  return (
    <>
      <SessionFilters />
      {isLoading && (
        <p className="text-sm text-slate-500">Loading sessions...</p>
      )}
      {!isLoading && sessions && sessions.length === 0 && (
        <p className="text-sm text-slate-500">No sessions found matching the current filters.</p>
      )}
      {!isLoading && sessions && sessions.length > 0 && (
        <div className="flex-1 min-h-0">
          <SessionTimeline sessions={sessions} />
        </div>
      )}
    </>
  );
}
