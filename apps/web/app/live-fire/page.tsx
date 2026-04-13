import { getLiveFireMetrics } from '@/lib/api-client';
import Breadcrumbs from '@/components/layout/Breadcrumbs';
import MetricsTable from '@/components/live-fire/MetricsTable';
import SubmitEntryForm from '@/components/live-fire/SubmitEntryForm';

export const metadata = {
  title: 'Live Fire | Valliance Graph',
  description: 'Track field usage and effectiveness of locked positions.',
};

export default async function LiveFirePage() {
  let metrics;
  try {
    metrics = await getLiveFireMetrics();
  } catch {
    metrics = null;
  }

  return (
    <div className="flex flex-1 flex-col min-h-0">
      <Breadcrumbs items={[{ label: 'Home', href: '/' }, { label: 'Live Fire' }]} />
      <h2 className="mb-4 text-2xl font-bold text-slate-900">Live Fire</h2>
      <p className="mb-6 text-sm text-slate-500">
        Position usage tracking from real conversations.
      </p>

      <div className="flex-1 space-y-6 overflow-auto pb-6">
        <SubmitEntryForm />

        {metrics ? (
          <MetricsTable metrics={metrics.metrics} />
        ) : (
          <p className="text-sm text-slate-400">No metrics available.</p>
        )}
      </div>
    </div>
  );
}
