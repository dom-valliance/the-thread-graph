import { apiGet } from '@/lib/api-client';
import type { Topic, TopicCoOccurrence } from '@/types/entities';
import TopicsView from './TopicsView';
import Breadcrumbs from '@/components/layout/Breadcrumbs';

export const metadata = {
  title: 'Topic Galaxy | Valliance Graph',
  description: 'Explore topics as a clustered galaxy visualisation.',
};

export default async function TopicsPage() {
  const [topics, coOccurrences] = await Promise.all([
    apiGet<Topic[]>('/topics'),
    apiGet<TopicCoOccurrence[]>('/topics/co-occurrences'),
  ]);

  return (
    <div className="flex flex-1 flex-col min-h-0">
      <Breadcrumbs items={[{ label: 'Home', href: '/' }, { label: 'Topics' }]} />
      <h2 className="mb-4 text-2xl font-bold text-slate-900">Topic Galaxy</h2>
      <p className="mb-6 text-sm text-slate-500">
        Visualising {topics.length} topics. Larger circles indicate more bookmarks. Click a topic to
        see its bookmarks. Drag nodes to rearrange. Scroll to zoom.
      </p>
      <div className="flex-1 min-h-0">
        <TopicsView topics={topics} coOccurrences={coOccurrences} />
      </div>
    </div>
  );
}
