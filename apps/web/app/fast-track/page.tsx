import { apiGet } from '@/lib/api-client';
import Breadcrumbs from '@/components/layout/Breadcrumbs';

export const metadata = {
  title: 'Fast Track | Valliance Graph',
  description: 'Essential Thread digest for onboarding.',
};

interface LockedPosition {
  id: string;
  text: string;
  arc_number: number;
  proposition: string | null;
  anti_position_text: string | null;
  status: string;
}

export default async function FastTrackPage() {
  let positions: LockedPosition[] = [];
  try {
    positions = await apiGet<LockedPosition[]>('/positions?status=locked&limit=100');
  } catch {
    positions = [];
  }

  return (
    <div className="flex flex-1 flex-col min-h-0">
      <Breadcrumbs items={[{ label: 'Home', href: '/' }, { label: 'Fast Track' }]} />
      <h2 className="mb-4 text-2xl font-bold text-slate-900">Fast Track</h2>
      <p className="mb-6 text-sm text-slate-500">
        Essential Thread digest: {positions.length} locked position{positions.length === 1 ? '' : 's'}.
      </p>

      {positions.length === 0 ? (
        <p className="text-sm text-slate-400">
          No locked positions yet. Complete at least one cycle to populate the Fast Track.
        </p>
      ) : (
        <div className="flex-1 space-y-6 overflow-auto pb-6">
          {positions.map((p) => (
            <div key={p.id} className="rounded-lg border border-slate-200 bg-white p-6">
              <div className="flex items-center gap-2 mb-2">
                <span className="rounded-full bg-blue-50 px-2 py-0.5 text-xs font-medium text-blue-700">
                  Arc {p.arc_number}
                </span>
                {p.proposition && (
                  <span className="rounded-full bg-purple-50 px-2 py-0.5 text-xs font-medium text-purple-700">
                    {p.proposition}
                  </span>
                )}
              </div>

              <div className="mb-3">
                <p className="text-xs font-medium text-slate-500">Position</p>
                <p className="mt-1 text-sm text-slate-900">{p.text}</p>
              </div>

              {p.anti_position_text && (
                <div>
                  <p className="text-xs font-medium text-slate-500">Anti-Position</p>
                  <p className="mt-1 text-sm text-slate-600">{p.anti_position_text}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
