import { getPrepBrief, getReadingList, getWorkshopAssignments, getScheduledSession } from '@/lib/api-client';
import Breadcrumbs from '@/components/layout/Breadcrumbs';
import ThreadPrepBriefView from '@/components/prep/ThreadPrepBriefView';
import Link from 'next/link';

export const metadata = {
  title: 'Session Prep | Valliance Graph',
  description: 'Preparation brief, reading list, and workshop assignments.',
};

export default async function PrepPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  let session;
  try {
    session = await getScheduledSession(id);
  } catch {
    return (
      <div className="flex flex-1 flex-col min-h-0">
        <Breadcrumbs items={[{ label: 'Home', href: '/' }, { label: 'Prep' }]} />
        <p className="text-sm text-red-500">Session not found.</p>
      </div>
    );
  }

  const [brief, readings, workshops] = await Promise.all([
    getPrepBrief(id).catch(() => null),
    getReadingList(id).catch(() => []),
    getWorkshopAssignments(id).catch(() => []),
  ]);

  const isWeek1 = session.week_type === 'problem_landscape';

  return (
    <div className="flex flex-1 flex-col min-h-0">
      <Breadcrumbs
        items={[
          { label: 'Home', href: '/' },
          { label: 'Schedule', href: '/schedule' },
          { label: `Week ${session.week_number}` },
          { label: 'Prep' },
        ]}
      />
      <h2 className="mb-4 text-2xl font-bold text-slate-900">
        Prep: Week {session.week_number} - {session.arc_name}
      </h2>

      <div className="flex-1 space-y-6 overflow-auto pb-6">
        {/* AI-generated Thread Prep Brief */}
        <ThreadPrepBriefView sessionId={id} />

        {/* Basic Prep Brief (auto-generated from graph data) */}
        {brief && (
          <div className="rounded-lg border border-slate-200 bg-white p-6">
            <h3 className="mb-3 text-lg font-semibold text-slate-900">Prep Brief</h3>
            {brief.arc_name && (
              <p className="text-sm text-slate-600">Arc: {brief.arc_name}</p>
            )}
            {brief.previous_locked_position_text && (
              <div className="mt-3">
                <p className="text-xs font-medium text-slate-500">Previous Locked Position</p>
                <p className="mt-1 text-sm text-slate-700">{brief.previous_locked_position_text}</p>
              </div>
            )}
            <p className="mt-2 text-xs text-slate-400">
              {brief.evidence_count} evidence entr{brief.evidence_count === 1 ? 'y' : 'ies'} for this arc
            </p>

            {brief.recent_bookmarks?.length > 0 && (
              <div className="mt-4">
                <p className="text-xs font-medium text-slate-500">Recent Bookmarks</p>
                <ul className="mt-1 space-y-1">
                  {brief.recent_bookmarks.map((b) => (
                    <li key={b.notion_id} className="text-sm text-slate-700">
                      {b.url ? (
                        <Link href={b.url} target="_blank" className="text-blue-600 hover:underline">
                          {b.title}
                        </Link>
                      ) : (
                        b.title
                      )}
                      {b.date_added && (
                        <span className="ml-2 text-xs text-slate-400">{b.date_added}</span>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Reading List */}
        <div className="rounded-lg border border-slate-200 bg-white p-6">
          <h3 className="mb-3 text-lg font-semibold text-slate-900">Reading List</h3>
          {readings.length === 0 ? (
            <p className="text-sm text-slate-400">No readings assigned yet.</p>
          ) : (
            <ul className="space-y-2">
              {readings.map((r) => (
                <li key={r.id} className="flex items-center gap-2 text-sm">
                  <span
                    className={`inline-block h-4 w-4 rounded border ${
                      r.status === 'read'
                        ? 'border-green-500 bg-green-500'
                        : 'border-slate-300'
                    }`}
                  />
                  <span className="text-slate-700">{r.bookmark_title ?? 'Unknown bookmark'}</span>
                  <span className="text-xs text-slate-400">{r.assigned_to_name ?? ''}</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Workshop Assignments (Week 1 only) */}
        {isWeek1 && (
          <div className="rounded-lg border border-slate-200 bg-white p-6">
            <h3 className="mb-3 text-lg font-semibold text-slate-900">Workshop Assignments</h3>
            {workshops.length === 0 ? (
              <p className="text-sm text-slate-400">No workshop assignments yet.</p>
            ) : (
              <ul className="space-y-2">
                {workshops.map((w) => (
                  <li key={w.id} className="rounded-md border border-slate-100 p-3">
                    <p className="text-sm font-medium text-slate-900">{w.player_or_approach}</p>
                    <p className="text-xs text-slate-500">
                      {w.assigned_to_name ?? 'Unassigned'} - {w.status}
                    </p>
                    {w.analysis_notes && (
                      <p className="mt-1 text-xs text-slate-600">{w.analysis_notes}</p>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
