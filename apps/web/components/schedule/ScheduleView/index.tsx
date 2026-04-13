'use client';

import { useCycles } from '@/lib/hooks/use-cycles';
import CreateCycleForm from '@/components/schedule/CreateCycleForm';
import ScheduleGrid from '@/components/schedule/ScheduleGrid';

export default function ScheduleView() {
  const { data: cycles, isLoading } = useCycles();

  if (isLoading) {
    return <p className="text-sm text-slate-400">Loading...</p>;
  }

  const activeCycle = cycles?.find((c) => c.status === 'active') ?? cycles?.[0] ?? null;

  return (
    <div className="space-y-6">
      <CreateCycleForm existingCycles={cycles ?? []} />

      {activeCycle ? (
        <ScheduleGrid cycleId={activeCycle.id} />
      ) : (
        <div className="rounded-lg border border-slate-200 bg-white p-6">
          <p className="text-sm text-slate-500">
            No cycles yet. Use the form above to create one.
          </p>
        </div>
      )}
    </div>
  );
}
