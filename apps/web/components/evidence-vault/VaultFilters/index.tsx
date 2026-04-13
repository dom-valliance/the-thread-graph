'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getVaultEvidence } from '@/lib/api-client';
import type { Evidence } from '@/types/entities';

const VAULT_TYPES = [
  'live_fire',
  'problem_week_anecdote',
  'market_data',
  'client_story',
  'flash',
] as const;

const PROPOSITIONS = ['P1', 'V1', 'both'] as const;

export default function VaultFilters({
  initialEvidence,
}: {
  initialEvidence: Evidence[];
}) {
  const [arc, setArc] = useState('');
  const [proposition, setProposition] = useState('');
  const [vaultType, setVaultType] = useState('');
  const hasFilters = arc || proposition || vaultType;

  const { data: filtered, isLoading } = useQuery({
    queryKey: ['evidence-vault', arc, proposition, vaultType],
    queryFn: () =>
      getVaultEvidence({
        arc: arc || undefined,
        proposition: proposition || undefined,
        vault_type: vaultType || undefined,
      }),
    enabled: !!hasFilters,
  });

  const evidence = hasFilters ? (filtered ?? []) : initialEvidence;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-3">
        <div>
          <label className="block text-xs font-medium text-slate-500 mb-1">Arc</label>
          <input
            type="text"
            className="rounded-md border border-slate-300 px-3 py-1.5 text-sm"
            placeholder="Filter by arc..."
            value={arc}
            onChange={(e) => setArc(e.target.value)}
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-500 mb-1">Proposition</label>
          <select
            className="rounded-md border border-slate-300 px-3 py-1.5 text-sm"
            value={proposition}
            onChange={(e) => setProposition(e.target.value)}
          >
            <option value="">All</option>
            {PROPOSITIONS.map((p) => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-500 mb-1">Type</label>
          <select
            className="rounded-md border border-slate-300 px-3 py-1.5 text-sm"
            value={vaultType}
            onChange={(e) => setVaultType(e.target.value)}
          >
            <option value="">All</option>
            {VAULT_TYPES.map((t) => (
              <option key={t} value={t}>{t.replace(/_/g, ' ')}</option>
            ))}
          </select>
        </div>

        {hasFilters && (
          <div className="flex items-end">
            <button
              className="rounded-md border border-slate-300 px-3 py-1.5 text-xs text-slate-600 hover:bg-slate-50"
              onClick={() => { setArc(''); setProposition(''); setVaultType(''); }}
            >
              Clear filters
            </button>
          </div>
        )}
      </div>

      {isLoading && hasFilters ? (
        <p className="text-sm text-slate-400">Filtering...</p>
      ) : (
        <>
          <p className="text-xs text-slate-400">
            {evidence.length} result{evidence.length === 1 ? '' : 's'}
          </p>
          <ul className="space-y-3">
            {evidence.map((item) => (
              <li
                key={item.id}
                className="rounded-lg border border-slate-200 bg-white p-4"
              >
                <p className="text-sm text-slate-900">{item.text}</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-600">
                    {item.type}
                  </span>
                  {item.vault_type && (
                    <span className="rounded-full bg-blue-50 px-2 py-0.5 text-xs text-blue-700">
                      {item.vault_type}
                    </span>
                  )}
                  {item.proposition_mapping && (
                    <span className="rounded-full bg-purple-50 px-2 py-0.5 text-xs text-purple-700">
                      {item.proposition_mapping}
                    </span>
                  )}
                </div>
                {item.source_title && (
                  <p className="mt-1 text-xs text-slate-400">Source: {item.source_title}</p>
                )}
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
