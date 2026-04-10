import { getCrossArcBridges, getUnconnectedPositions } from '@/lib/api-client';
import BridgeExplorer from '@/components/graph/BridgeExplorer';
import Breadcrumbs from '@/components/layout/Breadcrumbs';

export const metadata = {
  title: 'Cross-Arc Bridges | Valliance Graph',
  description: 'Explore position-to-position bridges across arcs.',
};

export default async function BridgesPage() {
  const [bridges, gaps] = await Promise.all([
    getCrossArcBridges(),
    getUnconnectedPositions(),
  ]);

  return (
    <div className="flex flex-1 flex-col min-h-0">
      <Breadcrumbs items={[{ label: 'Home', href: '/' }, { label: 'Bridges' }]} />
      <h2 className="mb-4 text-2xl font-bold text-slate-900">Cross-Arc Bridge Explorer</h2>
      <p className="mb-6 text-sm text-slate-500">
        {bridges.length} bridge{bridges.length === 1 ? '' : 's'} connecting positions across arcs.
        {gaps.length > 0 && ` ${gaps.length} unconnected position${gaps.length === 1 ? '' : 's'}.`}
      </p>
      <div className="flex-1 min-h-0">
        <BridgeExplorer bridges={bridges} gaps={gaps} />
      </div>
    </div>
  );
}
