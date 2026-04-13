import { getCurrentCycle } from '@/lib/api-client';
import Breadcrumbs from '@/components/layout/Breadcrumbs';
import Link from 'next/link';

export const metadata = {
  title: 'Dashboard | Valliance Graph',
  description: 'Current cycle status and session overview.',
};

const WEEK_TYPE_LABELS: Record<string, string> = {
  problem_landscape: 'Problem + Landscape',
  position_pitch: 'Position + Pitch',
};

export default async function DashboardPage() {
  let cycle;
  try {
    cycle = await getCurrentCycle();
  } catch {
    cycle = null;
  }

  return (
    <div className="flex flex-1 flex-col min-h-0">
      <Breadcrumbs items={[{ label: 'Dashboard' }]} />
      <h2 className="mb-4 text-2xl font-bold text-slate-900">Dashboard</h2>

      {!cycle ? (
        <div className="rounded-lg border border-slate-200 bg-white p-6">
          <p className="text-sm text-slate-500">
            No active cycle found.{' '}
            <Link href="/schedule" className="text-blue-600 hover:underline">
              Create a cycle
            </Link>{' '}
            to get started.
          </p>
        </div>
      ) : (
        <div className="flex-1 space-y-6 overflow-auto pb-6">
          {/* Cycle overview */}
          <div className="rounded-lg border border-slate-200 bg-white p-6">
            <div className="flex items-center gap-3 mb-4">
              <h3 className="text-lg font-semibold text-slate-900">
                Cycle {cycle.number}
              </h3>
              <span className="rounded-full bg-green-50 px-2.5 py-0.5 text-xs font-medium text-green-700">
                Active
              </span>
              <Link
                href="/schedule"
                className="ml-auto text-xs text-blue-600 hover:underline"
              >
                View full schedule
              </Link>
            </div>

            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              <div>
                <p className="text-xs text-slate-500">Start</p>
                <p className="text-sm font-medium text-slate-900">{cycle.start_date}</p>
              </div>
              <div>
                <p className="text-xs text-slate-500">End</p>
                <p className="text-sm font-medium text-slate-900">{cycle.end_date}</p>
              </div>
              {cycle.days_until_next != null && (
                <div>
                  <p className="text-xs text-slate-500">Next session</p>
                  <p className="text-sm font-medium text-slate-900">
                    {cycle.days_until_next === 0
                      ? 'Today'
                      : `${cycle.days_until_next} day${cycle.days_until_next === 1 ? '' : 's'}`}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Current session */}
          {cycle.current_session && (
            <div className="rounded-lg border border-slate-200 bg-white p-6">
              <div className="flex items-center gap-3 mb-4">
                <h3 className="text-lg font-semibold text-slate-900">
                  Week {cycle.current_session.week_number}: {cycle.current_session.arc_name}
                </h3>
                <span className="rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-medium text-blue-700">
                  {WEEK_TYPE_LABELS[cycle.current_session.week_type] ?? cycle.current_session.week_type}
                </span>
                <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-600">
                  Arc {cycle.current_session.arc_number}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                {cycle.current_session.date && (
                  <div>
                    <p className="text-xs text-slate-500">Date</p>
                    <p className="text-sm font-medium text-slate-900">
                      {cycle.current_session.date}
                    </p>
                  </div>
                )}
                <div>
                  <p className="text-xs text-slate-500">Lead</p>
                  <p className="text-sm font-medium text-slate-900">
                    {cycle.current_session.lead_name ?? 'Unassigned'}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-slate-500">Shadow</p>
                  <p className="text-sm font-medium text-slate-900">
                    {cycle.current_session.shadow_name ?? 'Unassigned'}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-slate-500">Status</p>
                  <p className="text-sm font-medium text-slate-900 capitalize">
                    {cycle.current_session.status}
                  </p>
                </div>
              </div>

              {/* Quick actions */}
              <div className="mt-4 flex gap-3 border-t border-slate-100 pt-4">
                <Link
                  href={`/sessions/${cycle.current_session.id}/workspace`}
                  className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                >
                  Open Workspace
                </Link>
                <Link
                  href={`/sessions/${cycle.current_session.id}/prep`}
                  className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
                >
                  View Prep Brief
                </Link>
                <Link
                  href="/live-fire"
                  className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
                >
                  Live Fire
                </Link>
                <Link
                  href="/forge"
                  className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
                >
                  Forge
                </Link>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
