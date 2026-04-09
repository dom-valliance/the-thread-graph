import { apiGet } from '@/lib/api-client';
import type { ArcDetail } from '@/types/entities';
import Breadcrumbs from '@/components/layout/Breadcrumbs';

interface ArcDetailPageProps {
  params: { arcId: string };
}

const STATUS_BADGE: Record<string, string> = {
  locked: 'bg-green-100 text-green-800',
  active: 'bg-blue-100 text-blue-800',
  draft: 'bg-slate-100 text-slate-600',
  archived: 'bg-amber-100 text-amber-800',
};

function badgeClass(status: string): string {
  return STATUS_BADGE[status.toLowerCase()] ?? 'bg-slate-100 text-slate-600';
}

export async function generateMetadata({ params }: ArcDetailPageProps) {
  const arc = await apiGet<ArcDetail>(`/arcs/${params.arcId}`);
  return {
    title: `${arc.name} | Valliance Graph`,
    description: arc.description ?? `Detail page for arc ${arc.name}.`,
  };
}

export default async function ArcDetailPage({ params }: ArcDetailPageProps) {
  const arc = await apiGet<ArcDetail>(`/arcs/${params.arcId}`);

  return (
    <div>
      <Breadcrumbs
        items={[
          { label: 'Home', href: '/' },
          { label: 'Arcs', href: '/arcs' },
          { label: arc.name },
        ]}
      />

      <div className="mb-6">
        <h2 className="mb-1 text-2xl font-bold text-slate-900">{arc.name}</h2>
        {arc.description && <p className="text-sm text-slate-600">{arc.description}</p>}
        <p className="mt-2 text-xs text-slate-400">
          Arc #{arc.number} &middot; Created {new Date(arc.created_at).toLocaleDateString('en-GB')}
        </p>
      </div>

      <section className="mb-8">
        <h3 className="mb-3 text-lg font-semibold text-slate-800">
          Positions ({arc.positions.length})
        </h3>
        {arc.positions.length === 0 ? (
          <p className="text-sm text-slate-500">No positions recorded for this arc.</p>
        ) : (
          <ul className="space-y-3">
            {arc.positions.map((position) => (
              <li
                key={position.id}
                className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-slate-900">{position.text}</p>
                    {position.proposition && (
                      <p className="mt-1 text-xs text-slate-500">{position.proposition}</p>
                    )}
                    {position.locked_date && (
                      <p className="mt-1 text-xs text-slate-400">
                        Locked {new Date(position.locked_date).toLocaleDateString('en-GB')}
                      </p>
                    )}
                  </div>
                  <span
                    className={`inline-flex shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${badgeClass(position.status)}`}
                  >
                    {position.status}
                  </span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      {arc.steelman_arguments.length > 0 && (
        <section className="mb-8">
          <h3 className="mb-3 text-lg font-semibold text-slate-800">
            Steelman Arguments ({arc.steelman_arguments.length})
          </h3>
          <ul className="space-y-2">
            {arc.steelman_arguments.map((arg) => (
              <li
                key={arg.id}
                className="rounded border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700"
              >
                {arg.text}
              </li>
            ))}
          </ul>
        </section>
      )}

      {arc.bridges.length > 0 && (
        <section>
          <h3 className="mb-3 text-lg font-semibold text-slate-800">
            Cross-Arc Bridges ({arc.bridges.length})
          </h3>
          <ul className="space-y-2">
            {arc.bridges.map((bridge) => (
              <li
                key={bridge.id}
                className="flex items-center gap-2 rounded border border-slate-200 bg-white px-4 py-3 text-sm"
              >
                <span className="font-medium text-slate-700">
                  {bridge.label ?? 'Unnamed bridge'}
                </span>
                <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-500">
                  {bridge.strength}
                </span>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
