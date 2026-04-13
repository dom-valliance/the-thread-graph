'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { updateForgeAssignment } from '@/lib/api-client';
import type { ForgeAssignment } from '@/types/entities';

const COLUMNS = [
  { key: 'assigned', label: 'Assigned' },
  { key: 'storyboarded', label: 'Storyboarded' },
  { key: 'in_production', label: 'In Production' },
  { key: 'editor_review', label: 'Editor Review' },
  { key: 'published', label: 'Published' },
] as const;

const NEXT_STATUS: Record<string, string> = {
  assigned: 'storyboarded',
  storyboarded: 'in_production',
  in_production: 'editor_review',
  editor_review: 'published',
};

function isOverdue(assignment: ForgeAssignment): boolean {
  if (assignment.status === 'published') return false;
  const today = new Date().toISOString().slice(0, 10);
  return assignment.deadline < today;
}

function ForgeCard({ item }: { item: ForgeAssignment }) {
  const queryClient = useQueryClient();
  const nextStatus = NEXT_STATUS[item.status];

  const advanceMutation = useMutation({
    mutationFn: () => updateForgeAssignment(item.id, { status: nextStatus }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['forge'] });
    },
  });

  return (
    <div
      className={`rounded-md border bg-white p-3 text-sm ${
        isOverdue(item) ? 'border-red-300 bg-red-50' : 'border-slate-200'
      }`}
    >
      <p className="font-medium text-slate-900">{item.artefact_type.replace(/_/g, ' ')}</p>
      {item.arc_name && (
        <p className="text-xs text-slate-500">{item.arc_name}</p>
      )}
      <div className="mt-1 flex items-center justify-between">
        <span className="text-xs text-slate-400">
          {item.assigned_to_name ?? 'Unassigned'}
        </span>
        <span
          className={`text-xs ${
            isOverdue(item) ? 'font-medium text-red-600' : 'text-slate-400'
          }`}
        >
          {item.deadline}
        </span>
      </div>
      {nextStatus && (
        <button
          className="mt-2 w-full rounded border border-blue-200 bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700 hover:bg-blue-100 disabled:opacity-50"
          onClick={() => advanceMutation.mutate()}
          disabled={advanceMutation.isPending}
        >
          {advanceMutation.isPending
            ? 'Moving...'
            : `Advance to ${nextStatus.replace(/_/g, ' ')}`}
        </button>
      )}
    </div>
  );
}

export default function KanbanBoard({
  assignments,
}: {
  assignments: ForgeAssignment[];
}) {
  const grouped = COLUMNS.map((col) => ({
    ...col,
    items: assignments.filter((a) => a.status === col.key),
  }));

  return (
    <div className="flex gap-4 overflow-x-auto">
      {grouped.map((column) => (
        <div
          key={column.key}
          className="min-w-[220px] flex-1 rounded-lg border border-slate-200 bg-slate-50 p-3"
        >
          <h3 className="mb-3 text-sm font-semibold text-slate-700">
            {column.label}{' '}
            <span className="text-xs font-normal text-slate-400">
              ({column.items.length})
            </span>
          </h3>
          <div className="space-y-2">
            {column.items.map((item) => (
              <ForgeCard key={item.id} item={item} />
            ))}
            {column.items.length === 0 && (
              <p className="text-xs text-slate-400">No items</p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
