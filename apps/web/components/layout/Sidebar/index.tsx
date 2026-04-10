'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { classNames } from '@/lib/utils';

const NAV_ITEMS = [
  { label: 'Arcs', href: '/arcs' },
  { label: 'Bridges', href: '/bridges' },
  { label: 'Objections', href: '/objections' },
  { label: 'Topics', href: '/topics' },
  { label: 'Sessions', href: '/sessions' },
  { label: 'Bookmarks', href: '/bookmarks' },
] as const;

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 flex h-screen w-56 flex-col bg-slate-900 text-slate-100">
      <div className="px-4 py-6">
        <span className="text-lg font-semibold tracking-tight">Valliance Graph</span>
      </div>
      <nav className="flex-1 px-2">
        <ul className="space-y-1">
          {NAV_ITEMS.map((item) => {
            const isActive = pathname.startsWith(item.href);
            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={classNames(
                    'block rounded-md px-3 py-2 text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-slate-700 text-white'
                      : 'text-slate-300 hover:bg-slate-800 hover:text-white',
                  )}
                >
                  {item.label}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
    </aside>
  );
}
