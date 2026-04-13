'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getThreadPrep, generateThreadPrep, regenerateThreadPrep } from '@/lib/api-client';
import type { ThreadPrepBrief } from '@/types/entities';

export default function ThreadPrepBriefView({ sessionId }: { sessionId: string }) {
  const queryClient = useQueryClient();
  const [generating, setGenerating] = useState(false);

  const { data: brief, isLoading, error } = useQuery({
    queryKey: ['thread-prep', sessionId],
    queryFn: () => getThreadPrep(sessionId),
    retry: false,
  });

  const generateMutation = useMutation({
    mutationFn: () => generateThreadPrep(sessionId),
    onMutate: () => setGenerating(true),
    onSettled: () => setGenerating(false),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['thread-prep', sessionId] });
    },
  });

  const regenerateMutation = useMutation({
    mutationFn: () => regenerateThreadPrep(sessionId),
    onMutate: () => setGenerating(true),
    onSettled: () => setGenerating(false),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['thread-prep', sessionId] });
    },
  });

  const isGenerating = generating || generateMutation.isPending || regenerateMutation.isPending;

  // No brief yet -- show generate button
  if (!brief && !isLoading) {
    return (
      <div className="rounded-lg border border-dashed border-slate-300 bg-slate-50 p-6 text-center">
        <p className="mb-3 text-sm text-slate-600">
          No AI-generated prep brief yet. Generate one from the synced bookmarks.
        </p>
        <button
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
          onClick={() => generateMutation.mutate()}
          disabled={isGenerating}
        >
          {isGenerating ? 'Generating... (30-60s)' : 'Generate Thread Prep Brief'}
        </button>
        {generateMutation.isError && (
          <p className="mt-2 text-sm text-red-600">
            {(generateMutation.error as Error).message}
          </p>
        )}
      </div>
    );
  }

  if (isLoading) {
    return <p className="text-sm text-slate-400">Loading thread prep brief...</p>;
  }

  if (!brief) return null;

  const isWeek1 = brief.week_type === 'problem_landscape';

  return (
    <div className="space-y-6">
      {/* Header + regenerate */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">Thread Prep Brief</h3>
          <p className="text-xs text-slate-400">
            Generated {brief.created_at} from {brief.bookmark_count} bookmark{brief.bookmark_count === 1 ? '' : 's'}
          </p>
        </div>
        <button
          className="rounded-md border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-50 disabled:opacity-50"
          onClick={() => regenerateMutation.mutate()}
          disabled={isGenerating}
        >
          {isGenerating ? 'Regenerating...' : 'Regenerate'}
        </button>
      </div>

      {isWeek1 ? <Week1View brief={brief} /> : <Week2View brief={brief} />}

      {/* Common sections */}
      <BookmarkMappingTable mapping={brief.bookmark_anchor_mapping} />
      <ReadingAssignments assignments={brief.reading_assignments} />
      {brief.adjacent_bookmarks.length > 0 && (
        <AdjacentBookmarksSection bookmarks={brief.adjacent_bookmarks} />
      )}
      {brief.flash_checks.length > 0 && (
        <FlashChecksSection checks={brief.flash_checks} />
      )}
    </div>
  );
}

function Week1View({ brief }: { brief: ThreadPrepBrief }) {
  return (
    <>
      {brief.sharpened_problem_question && (
        <Section title="Sharpened Problem Question">
          <p className="text-sm font-medium text-slate-900">{brief.sharpened_problem_question}</p>
          {brief.problem_question_rationale && (
            <p className="mt-1 text-sm italic text-slate-600">{brief.problem_question_rationale}</p>
          )}
        </Section>
      )}

      {brief.sharpened_landscape_question && (
        <Section title="Sharpened Landscape Question">
          <p className="text-sm font-medium text-slate-900">{brief.sharpened_landscape_question}</p>
          {brief.landscape_question_rationale && (
            <p className="mt-1 text-sm italic text-slate-600">{brief.landscape_question_rationale}</p>
          )}
        </Section>
      )}

      {brief.steelman_argument && (
        <Section title="Steelman">
          <blockquote className="border-l-4 border-blue-300 pl-3 text-sm italic text-slate-800">
            {brief.steelman_argument}
          </blockquote>
          {brief.steelman_rationale && (
            <p className="mt-1 text-sm text-slate-600">{brief.steelman_rationale}</p>
          )}
        </Section>
      )}

      {brief.workshop_grid_criteria.length > 0 && (
        <Section title="Workshop Grid Criteria">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left">
                <th className="px-3 py-1.5 font-medium text-slate-500">Criterion</th>
                <th className="px-3 py-1.5 font-medium text-slate-500">What it tests</th>
              </tr>
            </thead>
            <tbody>
              {brief.workshop_grid_criteria.map((c, i) => (
                <tr key={i} className="border-b border-slate-100">
                  <td className="px-3 py-1.5 font-medium text-slate-900">{c.criterion}</td>
                  <td className="px-3 py-1.5 text-slate-600">{c.what_it_tests}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Section>
      )}
    </>
  );
}

function Week2View({ brief }: { brief: ThreadPrepBrief }) {
  return (
    <>
      {brief.new_evidence_since_week1 && (
        <Section title="New Evidence Since Week 1">
          <p className="text-sm text-slate-700 whitespace-pre-line">{brief.new_evidence_since_week1}</p>
        </Section>
      )}
      {brief.objection_fuel && (
        <Section title="Objection Fuel">
          <p className="text-sm text-slate-700 whitespace-pre-line">{brief.objection_fuel}</p>
        </Section>
      )}
      {brief.cross_arc_bridge_prompts && (
        <Section title="Cross-Arc Bridge Prompts">
          <p className="text-sm text-slate-700 whitespace-pre-line">{brief.cross_arc_bridge_prompts}</p>
        </Section>
      )}
      {brief.p1_v1_signal && (
        <Section title="P1/V1 Signal">
          <p className="text-sm text-slate-700 whitespace-pre-line">{brief.p1_v1_signal}</p>
        </Section>
      )}
    </>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5">
      <h4 className="mb-2 text-sm font-semibold text-slate-700">{title}</h4>
      {children}
    </div>
  );
}

function BookmarkMappingTable({
  mapping,
}: {
  mapping: ThreadPrepBrief['bookmark_anchor_mapping'];
}) {
  if (!mapping || mapping.length === 0) return null;

  return (
    <Section title="Bookmark-to-Anchor Mapping">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200 text-left">
              <th className="px-3 py-1.5 font-medium text-slate-500">Bookmark</th>
              <th className="px-3 py-1.5 font-medium text-slate-500">PMF Anchor</th>
              <th className="px-3 py-1.5 font-medium text-slate-500">Contribution</th>
            </tr>
          </thead>
          <tbody>
            {mapping.map((m, i) => (
              <tr key={i} className="border-b border-slate-100">
                <td className="px-3 py-1.5 text-slate-900">
                  {m.bookmark_title}
                  {m.bookmark_source && (
                    <span className="ml-1 text-xs text-slate-400">({m.bookmark_source})</span>
                  )}
                </td>
                <td className="px-3 py-1.5 text-slate-600">{m.pmf_anchor}</td>
                <td className="px-3 py-1.5 text-slate-600">{m.contribution}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Section>
  );
}

function ReadingAssignments({
  assignments,
}: {
  assignments: ThreadPrepBrief['reading_assignments'];
}) {
  if (!assignments || assignments.length === 0) return null;

  return (
    <Section title="Reading Assignments">
      <ul className="space-y-1">
        {assignments.map((a, i) => (
          <li key={i} className="text-sm">
            <span className="font-medium text-slate-900">{a.player}:</span>{' '}
            <span className="text-slate-600">{a.bookmark_titles?.join(', ')}</span>
          </li>
        ))}
      </ul>
    </Section>
  );
}

function AdjacentBookmarksSection({
  bookmarks,
}: {
  bookmarks: ThreadPrepBrief['adjacent_bookmarks'];
}) {
  return (
    <Section title="Adjacent Bookmarks (Other Arcs)">
      <ul className="space-y-1">
        {bookmarks.map((b, i) => (
          <li key={i} className="text-sm">
            <span className="font-medium text-slate-900">{b.bookmark_title}</span>
            <span className="ml-1 rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-600">
              {b.relevant_arc}
            </span>
            <span className="ml-1 text-slate-500"> - {b.reason}</span>
          </li>
        ))}
      </ul>
    </Section>
  );
}

function FlashChecksSection({
  checks,
}: {
  checks: ThreadPrepBrief['flash_checks'];
}) {
  return (
    <Section title="Potential Flashes">
      {checks.map((f, i) => (
        <div
          key={i}
          className="mb-2 rounded border border-amber-200 bg-amber-50 p-3 text-sm"
        >
          <p className="font-medium text-amber-800">{f.bookmark_title}</p>
          <p className="text-amber-700">
            Challenges Arc {f.challenged_arc} on: {f.challenged_claim}
          </p>
        </div>
      ))}
    </Section>
  );
}
