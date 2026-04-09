import { apiGet } from '@/lib/api-client';
import type { Argument } from '@/types/entities';
import ArgumentMap from '@/components/graph/ArgumentMap';
import Breadcrumbs from '@/components/layout/Breadcrumbs';

interface PositionDetail {
  id: string;
  text: string;
  status: string;
  arguments: Argument[];
}

interface PositionPageProps {
  params: { positionId: string };
}

export async function generateMetadata({ params }: PositionPageProps) {
  return {
    title: `Position ${params.positionId} | Valliance Graph`,
    description: 'Argument map for a position showing supporting and challenging arguments.',
  };
}

export default async function PositionArgumentMapPage({ params }: PositionPageProps) {
  const position = await apiGet<PositionDetail>(`/positions/${params.positionId}/arguments`);

  return (
    <div className="flex flex-1 flex-col min-h-0">
      <Breadcrumbs
        items={[
          { label: 'Home', href: '/' },
          { label: 'Positions' },
          { label: position.text.length > 40 ? `${position.text.slice(0, 37)}...` : position.text },
        ]}
      />
      <h2 className="mb-2 text-2xl font-bold text-slate-900">Argument Map</h2>
      <p className="mb-2 text-base text-slate-700">{position.text}</p>
      <p className="mb-6 text-sm text-slate-500">
        {position.arguments.length} arguments mapped. Green nodes support the position; red nodes
        challenge it. Drag to rearrange. Scroll to zoom.
      </p>
      <div className="flex-1 min-h-0">
        <ArgumentMap
          positionId={position.id}
          positionText={position.text}
          arguments={position.arguments}
        />
      </div>
    </div>
  );
}
