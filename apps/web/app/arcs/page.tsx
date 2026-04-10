import { getArcs, getArcBridges } from '@/lib/api-client';
import ArcExplorer from '@/components/graph/ArcExplorer';
import Breadcrumbs from '@/components/layout/Breadcrumbs';

export const metadata = {
  title: 'Arc Explorer | Valliance Graph',
  description: 'Explore arcs and their connections in a force-directed graph.',
};

export default async function ArcsPage() {
  const [arcs, bridges] = await Promise.all([getArcs(), getArcBridges()]);

  return (
    <div className="flex flex-1 flex-col min-h-0">
      <Breadcrumbs items={[{ label: 'Home', href: '/' }, { label: 'Arcs' }]} />
      <h2 className="mb-4 text-2xl font-bold text-slate-900">Arc Explorer</h2>
      <p className="mb-6 text-sm text-slate-500">
        Visualising {arcs.length} arcs and their connections. Drag nodes to rearrange. Scroll
        to zoom.
      </p>
      <div className="flex-1 min-h-0">
        <ArcExplorer arcs={arcs} bridges={bridges} />
      </div>
    </div>
  );
}
