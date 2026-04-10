import { getObjectionPairs } from '@/lib/api-client';
import ObjectionForge from '@/components/ObjectionForge';
import Breadcrumbs from '@/components/layout/Breadcrumbs';

export const metadata = {
  title: 'Objection Forge | Valliance Graph',
  description: 'Browse, create, and manage objection-response pairs.',
};

export default async function ObjectionsPage() {
  const pairs = await getObjectionPairs();

  return (
    <div className="flex flex-1 flex-col min-h-0">
      <Breadcrumbs items={[{ label: 'Home', href: '/' }, { label: 'Objections' }]} />
      <h2 className="mb-4 text-2xl font-bold text-slate-900">Objection Forge</h2>
      <p className="mb-6 text-sm text-slate-500">
        {pairs.length} objection-response pair{pairs.length === 1 ? '' : 's'} across your
        arcs. Search, filter, and refine your positions.
      </p>
      <div className="flex-1 overflow-auto pb-6">
        <ObjectionForge initialPairs={pairs} />
      </div>
    </div>
  );
}
