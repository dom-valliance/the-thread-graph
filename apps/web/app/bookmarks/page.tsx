import { apiGet } from '@/lib/api-client';
import type { Bookmark } from '@/types/entities';
import Breadcrumbs from '@/components/layout/Breadcrumbs';
import Link from 'next/link';

export const metadata = {
  title: 'Bookmarks | Valliance Graph',
  description: 'Browse all synced bookmarks grouped by theme.',
};

function groupByTheme(bookmarks: Bookmark[]): Map<string, Bookmark[]> {
  const groups = new Map<string, Bookmark[]>();
  const ungrouped: Bookmark[] = [];

  for (const bookmark of bookmarks) {
    const theme = bookmark.theme_name;
    if (!theme) {
      ungrouped.push(bookmark);
      continue;
    }
    const list = groups.get(theme) ?? [];
    list.push(bookmark);
    groups.set(theme, list);
  }

  const sorted = new Map<string, Bookmark[]>(
    Array.from(groups.entries()).sort(([, a], [, b]) => b.length - a.length),
  );

  if (ungrouped.length > 0) {
    sorted.set('Uncategorised', ungrouped);
  }

  return sorted;
}

function BookmarkCard({ bookmark }: { bookmark: Bookmark }) {
  return (
    <li className="rounded-lg border border-slate-200 bg-white p-4">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <h4 className="text-sm font-semibold text-slate-900">{bookmark.title}</h4>
          {bookmark.source && (
            <p className="mt-1 text-xs text-slate-500">{bookmark.source}</p>
          )}
          {bookmark.ai_summary && (
            <p className="mt-2 text-sm text-slate-600">{bookmark.ai_summary}</p>
          )}
          {bookmark.arc_bucket_names?.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1">
              {bookmark.arc_bucket_names?.map((arc) => (
                <span
                  key={arc}
                  className="rounded-full bg-blue-50 px-2 py-0.5 text-xs font-medium text-blue-700"
                >
                  {arc}
                </span>
              ))}
            </div>
          )}
        </div>
        <div className="flex shrink-0 flex-col items-end gap-1">
          {bookmark.edge_or_foundational && (
            <span className="rounded bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600">
              {bookmark.edge_or_foundational}
            </span>
          )}
          {bookmark.topic_names?.length > 0 && (
            <span className="text-xs text-slate-400">
              {bookmark.topic_names.join(', ')}
            </span>
          )}
        </div>
      </div>
      {bookmark.url && (
        <Link
          href={bookmark.url}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-2 inline-block text-xs text-blue-600 hover:underline"
        >
          {bookmark.url}
        </Link>
      )}
    </li>
  );
}

async function fetchAllBookmarks(): Promise<Bookmark[]> {
  const PAGE_SIZE = 100;
  const all: Bookmark[] = [];
  let cursor: string | undefined;

  while (true) {
    const params = new URLSearchParams({ limit: String(PAGE_SIZE) });
    if (cursor) params.set('cursor', cursor);

    const page = await apiGet<Bookmark[]>(`/bookmarks?${params.toString()}`);
    all.push(...page);

    if (page.length < PAGE_SIZE) break;
    cursor = page[page.length - 1].notion_id;
  }

  return all;
}

export default async function BookmarksPage() {
  const bookmarks = await fetchAllBookmarks();
  const grouped = groupByTheme(bookmarks);

  return (
    <div className="flex flex-1 flex-col min-h-0">
      <Breadcrumbs items={[{ label: 'Home', href: '/' }, { label: 'Bookmarks' }]} />
      <h2 className="mb-4 text-2xl font-bold text-slate-900">Bookmarks</h2>
      <p className="mb-6 text-sm text-slate-500">
        {bookmarks.length} bookmark{bookmarks.length === 1 ? '' : 's'} synced from Notion,
        grouped by theme.
      </p>

      {bookmarks.length === 0 ? (
        <p className="text-sm text-slate-400">No bookmarks found. Run the Notion sync to populate.</p>
      ) : (
        <div className="flex-1 space-y-8 overflow-auto pb-6">
          {Array.from(grouped.entries()).map(([theme, themeBookmarks]) => (
            <section key={theme}>
              <div className="mb-3 flex items-center gap-2">
                <h3 className={`text-lg font-semibold ${theme === 'Uncategorised' ? 'text-slate-400' : 'text-slate-900'}`}>
                  {theme}
                </h3>
                <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-500">
                  {themeBookmarks.length}
                </span>
              </div>
              <ul className="space-y-3">
                {themeBookmarks.map((bookmark) => (
                  <BookmarkCard
                    key={bookmark.id ?? bookmark.notion_id}
                    bookmark={bookmark}
                  />
                ))}
              </ul>
            </section>
          ))}
        </div>
      )}
    </div>
  );
}
