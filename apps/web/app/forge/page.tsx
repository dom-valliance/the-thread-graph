import { getForgeAssignments } from '@/lib/api-client';
import Breadcrumbs from '@/components/layout/Breadcrumbs';
import KanbanBoard from '@/components/forge/KanbanBoard';
import CreateAssignmentForm from '@/components/forge/CreateAssignmentForm';

export const metadata = {
  title: 'Forge | Valliance Graph',
  description: 'Track external artefacts through the content pipeline.',
};

export default async function ForgePage() {
  let assignments: Awaited<ReturnType<typeof getForgeAssignments>> = [];
  try {
    assignments = await getForgeAssignments();
  } catch {
    assignments = [];
  }

  return (
    <div className="flex flex-1 flex-col min-h-0">
      <Breadcrumbs items={[{ label: 'Home', href: '/' }, { label: 'Forge' }]} />
      <h2 className="mb-4 text-2xl font-bold text-slate-900">Forge</h2>
      <p className="mb-6 text-sm text-slate-500">
        Content pipeline: {assignments.length} artefact{assignments.length === 1 ? '' : 's'} tracked.
      </p>

      <div className="flex-1 space-y-6 overflow-auto pb-6">
        <CreateAssignmentForm />
        <KanbanBoard assignments={assignments} />
      </div>
    </div>
  );
}
