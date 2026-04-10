'use client';

import { useMemo, useState } from 'react';
import Link from 'next/link';
import type { ObjectionPairWithContext } from '@/types/entities';
import {
  useObjectionPairs,
  useCreateObjectionPair,
  useUpdateObjectionPair,
  useDeleteObjectionPair,
} from '@/lib/hooks/use-objections';

interface ObjectionForgeProps {
  initialPairs: ObjectionPairWithContext[];
}

function ORPCard({
  pair,
  onEdit,
  onDelete,
}: {
  pair: ObjectionPairWithContext;
  onEdit: (pair: ObjectionPairWithContext) => void;
  onDelete: (pairId: string) => void;
}) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <p className="font-bold text-slate-900">{pair.objection_text}</p>
      <p className="mt-2 text-sm text-slate-600">{pair.response_text}</p>

      <div className="mt-3 flex flex-wrap items-center gap-2">
        <span className="rounded-full bg-blue-50 px-2 py-0.5 text-xs font-medium text-blue-700">
          {pair.arc_name}
        </span>
        <Link
          href={`/positions/${pair.position_id}`}
          className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600 hover:bg-slate-200"
        >
          {pair.position_text}
        </Link>
      </div>

      <div className="mt-3 flex gap-2">
        <button
          onClick={() => onEdit(pair)}
          className="rounded border border-slate-200 px-2 py-1 text-xs font-medium text-slate-600 hover:bg-slate-50"
        >
          Edit
        </button>
        <button
          onClick={() => onDelete(pair.id)}
          className="rounded border border-red-200 px-2 py-1 text-xs font-medium text-red-600 hover:bg-red-50"
        >
          Delete
        </button>
      </div>
    </div>
  );
}

function InlineEditForm({
  pair,
  onSave,
  onCancel,
  isSaving,
}: {
  pair: ObjectionPairWithContext;
  onSave: (data: { objection_text: string; response_text: string }) => void;
  onCancel: () => void;
  isSaving: boolean;
}) {
  const [objectionText, setObjectionText] = useState(pair.objection_text);
  const [responseText, setResponseText] = useState(pair.response_text);

  return (
    <div className="rounded-lg border border-blue-200 bg-blue-50/30 p-4">
      <label className="block text-xs font-medium text-slate-700">Objection</label>
      <textarea
        value={objectionText}
        onChange={(e) => setObjectionText(e.target.value)}
        rows={3}
        className="mt-1 w-full rounded border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
      />

      <label className="mt-3 block text-xs font-medium text-slate-700">Response</label>
      <textarea
        value={responseText}
        onChange={(e) => setResponseText(e.target.value)}
        rows={3}
        className="mt-1 w-full rounded border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
      />

      <div className="mt-3 flex gap-2">
        <button
          onClick={() =>
            onSave({ objection_text: objectionText, response_text: responseText })
          }
          disabled={isSaving || !objectionText.trim() || !responseText.trim()}
          className="rounded bg-blue-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {isSaving ? 'Saving...' : 'Save'}
        </button>
        <button
          onClick={onCancel}
          disabled={isSaving}
          className="rounded border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-50 disabled:opacity-50"
        >
          Cancel
        </button>
      </div>
    </div>
  );
}

function AddORPForm({
  onSubmit,
  onCancel,
  isSubmitting,
}: {
  onSubmit: (data: {
    objection_text: string;
    response_text: string;
    position_id: string;
  }) => void;
  onCancel: () => void;
  isSubmitting: boolean;
}) {
  const [objectionText, setObjectionText] = useState('');
  const [responseText, setResponseText] = useState('');
  const [positionId, setPositionId] = useState('');

  function handleSubmit() {
    onSubmit({
      objection_text: objectionText,
      response_text: responseText,
      position_id: positionId,
    });
  }

  const isValid = objectionText.trim() && responseText.trim() && positionId.trim();

  return (
    <div className="rounded-lg border border-green-200 bg-green-50/30 p-4">
      <h3 className="mb-3 text-sm font-semibold text-slate-900">New Objection-Response Pair</h3>

      <label className="block text-xs font-medium text-slate-700">Objection</label>
      <textarea
        value={objectionText}
        onChange={(e) => setObjectionText(e.target.value)}
        rows={3}
        placeholder="State the objection..."
        className="mt-1 w-full rounded border border-slate-300 px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
      />

      <label className="mt-3 block text-xs font-medium text-slate-700">Response</label>
      <textarea
        value={responseText}
        onChange={(e) => setResponseText(e.target.value)}
        rows={3}
        placeholder="Provide the response..."
        className="mt-1 w-full rounded border border-slate-300 px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
      />

      <label className="mt-3 block text-xs font-medium text-slate-700">Position ID</label>
      <input
        type="text"
        value={positionId}
        onChange={(e) => setPositionId(e.target.value)}
        placeholder="e.g. pos-abc123"
        className="mt-1 w-full rounded border border-slate-300 px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
      />

      <div className="mt-3 flex gap-2">
        <button
          onClick={handleSubmit}
          disabled={isSubmitting || !isValid}
          className="rounded bg-green-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-green-700 disabled:opacity-50"
        >
          {isSubmitting ? 'Creating...' : 'Create ORP'}
        </button>
        <button
          onClick={onCancel}
          disabled={isSubmitting}
          className="rounded border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-50 disabled:opacity-50"
        >
          Cancel
        </button>
      </div>
    </div>
  );
}

export default function ObjectionForge({ initialPairs }: ObjectionForgeProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeArc, setActiveArc] = useState<string | null>(null);
  const [editingPairId, setEditingPairId] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);

  const { data: pairs = [] } = useObjectionPairs(undefined, initialPairs);
  const createMutation = useCreateObjectionPair();
  const updateMutation = useUpdateObjectionPair();
  const deleteMutation = useDeleteObjectionPair();

  const arcNames = useMemo(() => {
    const names = new Set(pairs.map((p) => p.arc_name));
    return Array.from(names).sort();
  }, [pairs]);

  const filteredPairs = useMemo(() => {
    let result = pairs;

    if (activeArc) {
      result = result.filter((p) => p.arc_name === activeArc);
    }

    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      result = result.filter((p) =>
        p.objection_text.toLowerCase().includes(query),
      );
    }

    return result;
  }, [pairs, activeArc, searchQuery]);

  function handleDelete(pairId: string) {
    if (!window.confirm('Delete this objection-response pair?')) return;
    deleteMutation.mutate(pairId);
  }

  function handleUpdate(
    pairId: string,
    data: { objection_text: string; response_text: string },
  ) {
    updateMutation.mutate(
      { pairId, data },
      { onSuccess: () => setEditingPairId(null) },
    );
  }

  function handleCreate(data: {
    objection_text: string;
    response_text: string;
    position_id: string;
  }) {
    createMutation.mutate(data, {
      onSuccess: () => setShowAddForm(false),
    });
  }

  return (
    <div className="space-y-4">
      {/* Search */}
      <input
        type="text"
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        placeholder="Search objections..."
        className="w-full rounded-lg border border-slate-300 px-4 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
      />

      {/* Arc filter tabs */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setActiveArc(null)}
          className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
            activeArc === null
              ? 'bg-slate-900 text-white'
              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
          }`}
        >
          All
        </button>
        {arcNames.map((name) => (
          <button
            key={name}
            onClick={() => setActiveArc(name)}
            className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
              activeArc === name
                ? 'bg-slate-900 text-white'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            {name}
          </button>
        ))}
      </div>

      {/* Add ORP button / form */}
      {showAddForm ? (
        <AddORPForm
          onSubmit={handleCreate}
          onCancel={() => setShowAddForm(false)}
          isSubmitting={createMutation.isPending}
        />
      ) : (
        <button
          onClick={() => setShowAddForm(true)}
          className="rounded-lg border border-dashed border-slate-300 px-4 py-2 text-sm font-medium text-slate-600 hover:border-slate-400 hover:bg-slate-50"
        >
          + Add ORP
        </button>
      )}

      {/* ORP cards */}
      {filteredPairs.length === 0 ? (
        <p className="py-8 text-center text-sm text-slate-400">
          No objection-response pairs found.
        </p>
      ) : (
        <div className="space-y-3">
          {filteredPairs.map((pair) =>
            editingPairId === pair.id ? (
              <InlineEditForm
                key={pair.id}
                pair={pair}
                onSave={(data) => handleUpdate(pair.id, data)}
                onCancel={() => setEditingPairId(null)}
                isSaving={updateMutation.isPending}
              />
            ) : (
              <ORPCard
                key={pair.id}
                pair={pair}
                onEdit={(p) => setEditingPairId(p.id)}
                onDelete={handleDelete}
              />
            ),
          )}
        </div>
      )}
    </div>
  );
}
