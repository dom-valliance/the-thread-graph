'use client';

import { useState } from 'react';
import { useCycleSchedule, useUpdateAssignment } from '@/lib/hooks/use-cycles';
import type { ScheduledSession } from '@/types/entities';
import Link from 'next/link';

const WEEK_TYPE_LABELS: Record<string, string> = {
  problem_landscape: 'Problem + Landscape',
  position_pitch: 'Position + Pitch',
};

function AssignmentCell({
  session,
  field,
  cycleId,
}: {
  session: ScheduledSession;
  field: 'lead' | 'shadow';
  cycleId: string;
}) {
  const [isEditing, setIsEditing] = useState(false);
  const [email, setEmail] = useState(
    field === 'lead' ? session.lead_email ?? '' : session.shadow_email ?? '',
  );
  const updateMutation = useUpdateAssignment(cycleId);

  const displayName = field === 'lead' ? session.lead_name : session.shadow_name;

  const handleSave = () => {
    updateMutation.mutate(
      {
        sessionId: session.id,
        ...(field === 'lead'
          ? { lead_email: email || null, shadow_email: session.shadow_email }
          : { lead_email: session.lead_email, shadow_email: email || null }),
      },
      { onSuccess: () => setIsEditing(false) },
    );
  };

  if (isEditing) {
    return (
      <td className="px-3 py-2">
        <div className="flex items-center gap-1">
          <input
            type="email"
            className="w-32 rounded border border-slate-300 px-1.5 py-0.5 text-xs"
            placeholder="email@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleSave();
              if (e.key === 'Escape') setIsEditing(false);
            }}
            autoFocus
          />
          <button
            className="text-xs text-blue-600 hover:underline"
            onClick={handleSave}
            disabled={updateMutation.isPending}
          >
            {updateMutation.isPending ? '...' : 'Save'}
          </button>
        </div>
      </td>
    );
  }

  return (
    <td
      className="px-3 py-2 text-slate-600 cursor-pointer hover:text-blue-600"
      onClick={() => setIsEditing(true)}
      title="Click to assign"
    >
      {displayName ?? <span className="text-slate-300">Click to assign</span>}
    </td>
  );
}

export default function ScheduleGrid({ cycleId }: { cycleId: string }) {
  const { data, isLoading, error } = useCycleSchedule(cycleId);

  if (isLoading) {
    return <p className="text-sm text-slate-400">Loading schedule...</p>;
  }

  if (error || !data) {
    return <p className="text-sm text-red-500">Failed to load schedule.</p>;
  }

  const today = new Date().toISOString().slice(0, 10);

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-200 text-left">
            <th className="px-3 py-2 font-medium text-slate-500">Week</th>
            <th className="px-3 py-2 font-medium text-slate-500">Arc</th>
            <th className="px-3 py-2 font-medium text-slate-500">Type</th>
            <th className="px-3 py-2 font-medium text-slate-500">Date</th>
            <th className="px-3 py-2 font-medium text-slate-500">Lead</th>
            <th className="px-3 py-2 font-medium text-slate-500">Shadow</th>
            <th className="px-3 py-2 font-medium text-slate-500">Status</th>
            <th className="px-3 py-2 font-medium text-slate-500"></th>
          </tr>
        </thead>
        <tbody>
          {data.sessions?.map((session) => {
            const isCurrent = session.date === today;
            return (
              <tr
                key={session.id}
                className={`border-b border-slate-100 ${
                  isCurrent ? 'bg-blue-50' : 'hover:bg-slate-50'
                }`}
              >
                <td className="px-3 py-2 font-medium text-slate-900">
                  {session.week_number}
                  {isCurrent && (
                    <span className="ml-2 rounded-full bg-blue-500 px-1.5 py-0.5 text-[10px] font-medium text-white">
                      NOW
                    </span>
                  )}
                </td>
                <td className="px-3 py-2 text-slate-700">
                  {session.arc_name ?? `Arc ${session.arc_number}`}
                </td>
                <td className="px-3 py-2 text-slate-600">
                  {WEEK_TYPE_LABELS[session.week_type] ?? session.week_type}
                </td>
                <td className="px-3 py-2 text-slate-600">{session.date ?? '—'}</td>
                <AssignmentCell session={session} field="lead" cycleId={cycleId} />
                <AssignmentCell session={session} field="shadow" cycleId={cycleId} />
                <td className="px-3 py-2">
                  <span
                    className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium capitalize ${
                      session.status === 'completed'
                        ? 'bg-green-50 text-green-700'
                        : session.status === 'in_progress'
                          ? 'bg-amber-50 text-amber-700'
                          : 'bg-slate-100 text-slate-600'
                    }`}
                  >
                    {session.status}
                  </span>
                </td>
                <td className="px-3 py-2">
                  <div className="flex gap-2">
                    <Link
                      href={`/sessions/${session.id}/workspace`}
                      className="text-xs text-blue-600 hover:underline"
                    >
                      Workspace
                    </Link>
                    <Link
                      href={`/sessions/${session.id}/prep`}
                      className="text-xs text-blue-600 hover:underline"
                    >
                      Prep
                    </Link>
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
