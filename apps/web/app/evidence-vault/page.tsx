import { getVaultEvidence } from '@/lib/api-client';
import Breadcrumbs from '@/components/layout/Breadcrumbs';
import VaultFilters from '@/components/evidence-vault/VaultFilters';

export const metadata = {
  title: 'Evidence Vault | Valliance Graph',
  description: 'Browse evidence entries tagged by arc, proposition, and type.',
};

export default async function EvidenceVaultPage() {
  let evidence: Awaited<ReturnType<typeof getVaultEvidence>> = [];
  try {
    evidence = await getVaultEvidence();
  } catch {
    evidence = [];
  }

  return (
    <div className="flex flex-1 flex-col min-h-0">
      <Breadcrumbs items={[{ label: 'Home', href: '/' }, { label: 'Evidence Vault' }]} />
      <h2 className="mb-4 text-2xl font-bold text-slate-900">Evidence Vault</h2>
      <p className="mb-6 text-sm text-slate-500">
        {evidence.length} evidence entr{evidence.length === 1 ? 'y' : 'ies'} across all arcs.
      </p>

      <div className="flex-1 overflow-auto pb-6">
        <VaultFilters initialEvidence={evidence} />
      </div>
    </div>
  );
}
