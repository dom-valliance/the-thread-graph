import Breadcrumbs from '@/components/layout/Breadcrumbs';
import ScheduleView from '@/components/schedule/ScheduleView';

export const metadata = {
  title: 'Schedule | Valliance Graph',
  description: 'View and manage the 12-week cycle schedule.',
};

export default function SchedulePage() {
  return (
    <div className="flex flex-1 flex-col min-h-0">
      <Breadcrumbs items={[{ label: 'Home', href: '/' }, { label: 'Schedule' }]} />
      <h2 className="mb-4 text-2xl font-bold text-slate-900">Schedule</h2>
      <p className="mb-6 text-sm text-slate-500">
        12-week cycle schedule with lead and shadow assignments.
      </p>
      <div className="flex-1 overflow-auto pb-6">
        <ScheduleView />
      </div>
    </div>
  );
}
