import { getScheduledSession } from '@/lib/api-client';
import Breadcrumbs from '@/components/layout/Breadcrumbs';
import Week1Workspace from '@/components/workspace/Week1Workspace';
import Week2Workspace from '@/components/workspace/Week2Workspace';

export const metadata = {
  title: 'Session Workspace | Valliance Graph',
  description: 'Live editing surface for session outputs.',
};

export default async function WorkspacePage({
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
        <Breadcrumbs
          items={[
            { label: 'Home', href: '/' },
            { label: 'Sessions', href: '/sessions' },
            { label: 'Workspace' },
          ]}
        />
        <p className="text-sm text-red-500">Session not found.</p>
      </div>
    );
  }

  const isWeek1 = session.week_type === 'problem_landscape';

  return (
    <div className="flex flex-1 flex-col min-h-0">
      <Breadcrumbs
        items={[
          { label: 'Home', href: '/' },
          { label: 'Schedule', href: '/schedule' },
          { label: `Week ${session.week_number}` },
          { label: 'Workspace' },
        ]}
      />
      <div className="mb-4 flex items-center gap-3">
        <h2 className="text-2xl font-bold text-slate-900">
          Week {session.week_number}: {session.arc_name}
        </h2>
        <span className="rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-medium text-blue-700">
          {isWeek1 ? 'Problem + Landscape' : 'Position + Pitch'}
        </span>
      </div>

      <div className="flex-1 overflow-auto pb-6">
        {isWeek1 ? (
          <Week1Workspace sessionId={id} arcName={session.arc_name} />
        ) : (
          <Week2Workspace sessionId={id} arcNumber={session.arc_number} />
        )}
      </div>
    </div>
  );
}
