import { Suspense } from 'react';
import Breadcrumbs from '@/components/layout/Breadcrumbs';
import SessionsView from './SessionsView';

export const metadata = {
  title: 'Session Timeline | Valliance Graph',
  description: 'Explore sessions on a chronological timeline.',
};

export default function SessionsPage() {
  return (
    <div className="flex flex-1 flex-col min-h-0">
      <Breadcrumbs items={[{ label: 'Home', href: '/' }, { label: 'Sessions' }]} />
      <h2 className="mb-4 text-2xl font-bold text-slate-900">Session Timeline</h2>
      <Suspense fallback={<p className="text-sm text-slate-500">Loading...</p>}>
        <SessionsView />
      </Suspense>
    </div>
  );
}
