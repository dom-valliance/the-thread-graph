import { apiGet } from '@/lib/api-client';
import type { Bookmark } from '@/types/entities';
import Breadcrumbs from '@/components/layout/Breadcrumbs';
import Link from 'next/link';

interface TopicDetailPageProps {
  params: { name: string };
}

export async function generateMetadata({ params }: TopicDetailPageProps) {
  const name = decodeURIComponent(params.name);
  return {
    title: `${name} | Topics | Valliance Graph`,
    description: `Bookmarks tagged with "${name}".`,
  };
}

export default async function TopicDetailPage({ params }: TopicDetailPageProps) {
  const name = decodeURIComponent(params.name);
  const bookmarks = await apiGet<Bookmark[]>(`/topics/${encodeURIComponent(name)}/bookmarks`);

  return (
    <div className="flex flex-1 flex-col min-h-0">
      <Breadcrumbs
        items={[
          { label: 'Home', href: '/' },
          { label: 'Topics', href: '/topics' },
          { label: name },
        ]}
      />
      <h2 className="mb-2 text-2xl font-bold text-slate-900">{name}</h2>
      <p className="mb-6 text-sm text-slate-500">
        {bookmarks.length} bookmark{bookmarks.length === 1 ? '' : 's'} tagged with this topic.
      </p>

      {bookmarks.length === 0 ? (
        <p className="text-sm text-slate-400">No bookmarks found for this topic.</p>
      ) : (
        <ul className="space-y-3">
          {bookmarks.map((bookmark) => (
            <li
              key={bookmark.id}
              className="rounded-lg border border-slate-200 bg-white p-4"
            >
              <h3 className="text-sm font-semibold text-slate-900">{bookmark.title}</h3>
              {bookmark.source && (
                <p className="mt-1 text-xs text-slate-500">{bookmark.source}</p>
              )}
              {bookmark.url && (
                <Link
                  href={bookmark.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-1 inline-block text-xs text-blue-600 hover:underline"
                >
                  {bookmark.url}
                </Link>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
