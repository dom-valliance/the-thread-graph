'use client';

import { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import type { EvidenceTrailBookmark, EvidenceTrailItem } from '@/types/entities';
import type { GraphNode } from '@/types/graph';
import { useContainerSize } from '@/lib/hooks/use-container-size';
import { useEvidenceTrail, useCreateEvidence } from '@/lib/hooks/use-evidence-trail';

const EDGE_COLOUR = '#3b82f6';
const FOUNDATIONAL_COLOUR = '#10b981';
const DEFAULT_BOOKMARK_COLOUR = '#94a3b8';
const EVIDENCE_COLOUR = '#64748b';
const POSITION_COLOUR = '#8b5cf6';
const BRIDGE_RING_COLOUR = '#f59e0b';
const LINK_COLOUR = '#cbd5e1';

const BOOKMARK_RADIUS = 18;
const EVIDENCE_RADIUS = 12;
const POSITION_RADIUS = 24;

interface EvidenceTrailProps {
  positionId: string;
}

interface TrailNode extends GraphNode {
  column: 'bookmark' | 'evidence' | 'position';
  url?: string | null;
  isBridge?: boolean;
  isUnsourced?: boolean;
}

interface TrailLink extends d3.SimulationLinkDatum<TrailNode> {
  label: string | null;
  strength: number;
}

function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return `${text.slice(0, maxLength - 1)}\u2026`;
}

function bookmarkColour(edgeOrFoundational: string | null): string {
  if (edgeOrFoundational?.toLowerCase() === 'edge') return EDGE_COLOUR;
  if (edgeOrFoundational?.toLowerCase() === 'foundational') return FOUNDATIONAL_COLOUR;
  return DEFAULT_BOOKMARK_COLOUR;
}

function buildNodes(
  positionId: string,
  positionText: string,
  evidence: EvidenceTrailItem[],
): TrailNode[] {
  const nodes: TrailNode[] = [];
  const seenBookmarks = new Set<string>();

  for (const item of evidence) {
    if (item.source_bookmark && !seenBookmarks.has(item.source_bookmark.notion_id)) {
      seenBookmarks.add(item.source_bookmark.notion_id);
      const bk = item.source_bookmark;
      nodes.push({
        id: `bk-${bk.notion_id}`,
        label: truncate(bk.title, 20),
        size: BOOKMARK_RADIUS,
        colour: bookmarkColour(bk.edge_or_foundational),
        data: bk,
        column: 'bookmark',
        url: bk.url,
        isBridge: bk.arc_names.length > 1,
      });
    }

    nodes.push({
      id: `ev-${item.id}`,
      label: truncate(item.text, 25),
      size: EVIDENCE_RADIUS,
      colour: EVIDENCE_COLOUR,
      data: item,
      column: 'evidence',
      isUnsourced: item.source_bookmark === null,
    });
  }

  nodes.push({
    id: `pos-${positionId}`,
    label: truncate(positionText, 30),
    size: POSITION_RADIUS,
    colour: POSITION_COLOUR,
    data: null,
    column: 'position',
  });

  return nodes;
}

function buildLinks(evidence: EvidenceTrailItem[], positionId: string): TrailLink[] {
  const links: TrailLink[] = [];

  for (const item of evidence) {
    if (item.source_bookmark) {
      links.push({
        source: `bk-${item.source_bookmark.notion_id}`,
        target: `ev-${item.id}`,
        label: null,
        strength: 1,
      });
    }

    links.push({
      source: `ev-${item.id}`,
      target: `pos-${positionId}`,
      label: null,
      strength: 1,
    });
  }

  return links;
}

function AddEvidenceForm({
  positionId,
  onClose,
}: {
  positionId: string;
  onClose: () => void;
}) {
  const [text, setText] = useState('');
  const [type, setType] = useState('external');
  const [sourceBookmarkId, setSourceBookmarkId] = useState('');
  const createMutation = useCreateEvidence();

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!text.trim()) return;

    createMutation.mutate(
      {
        text: text.trim(),
        type,
        position_id: positionId,
        source_bookmark_id: sourceBookmarkId.trim() || null,
      },
      { onSuccess: () => onClose() },
    );
  }

  return (
    <form onSubmit={handleSubmit} className="mt-4 rounded-lg border border-slate-200 bg-white p-4">
      <div className="mb-3">
        <label htmlFor="evidence-text" className="mb-1 block text-sm font-medium text-slate-700">
          Evidence text
        </label>
        <textarea
          id="evidence-text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          className="w-full rounded border border-slate-300 px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-slate-500 focus:outline-none"
          rows={3}
          placeholder="Describe the evidence..."
          required
        />
      </div>
      <div className="mb-3 flex gap-4">
        <div className="flex-1">
          <label htmlFor="evidence-type" className="mb-1 block text-sm font-medium text-slate-700">
            Type
          </label>
          <select
            id="evidence-type"
            value={type}
            onChange={(e) => setType(e.target.value)}
            className="w-full rounded border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-slate-500 focus:outline-none"
          >
            <option value="external">External</option>
            <option value="internal">Internal</option>
            <option value="anecdotal">Anecdotal</option>
          </select>
        </div>
        <div className="flex-1">
          <label
            htmlFor="source-bookmark-id"
            className="mb-1 block text-sm font-medium text-slate-700"
          >
            Source bookmark ID (optional)
          </label>
          <input
            id="source-bookmark-id"
            type="text"
            value={sourceBookmarkId}
            onChange={(e) => setSourceBookmarkId(e.target.value)}
            className="w-full rounded border border-slate-300 px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-slate-500 focus:outline-none"
            placeholder="Notion ID"
          />
        </div>
      </div>
      <div className="flex gap-2">
        <button
          type="submit"
          disabled={createMutation.isPending}
          className="rounded bg-slate-800 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700 disabled:opacity-50"
        >
          {createMutation.isPending ? 'Saving...' : 'Save'}
        </button>
        <button
          type="button"
          onClick={onClose}
          className="rounded border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}

export default function EvidenceTrail({ positionId }: EvidenceTrailProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [containerRef, { width, height }] = useContainerSize();
  const [showForm, setShowForm] = useState(false);
  const { data, isLoading, error } = useEvidenceTrail(positionId);

  useEffect(() => {
    const svgElement = svgRef.current;
    if (!svgElement || width === 0 || height === 0 || !data) return;

    const svg = d3.select(svgElement);
    svg.selectAll('*').remove();

    const nodes = buildNodes(positionId, data.position_text, data.evidence);
    const links = buildLinks(data.evidence, positionId);

    if (nodes.length === 0) return;

    const colX = {
      bookmark: width * 0.15,
      evidence: width * 0.5,
      position: width * 0.85,
    };
    const centreY = height / 2;

    const simulation = d3
      .forceSimulation<TrailNode>(nodes)
      .force(
        'x',
        d3.forceX<TrailNode>().x((d) => colX[d.column]).strength(0.8),
      )
      .force('y', d3.forceY<TrailNode>(centreY).strength(0.15))
      .force('collision', d3.forceCollide<TrailNode>().radius((d) => d.size + 10))
      .force(
        'link',
        d3
          .forceLink<TrailNode, TrailLink>(links)
          .id((d) => d.id)
          .strength(0),
      );

    const container = svg.append('g');

    const zoom = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.3, 3])
      .on('zoom', (event: d3.D3ZoomEvent<SVGSVGElement, unknown>) => {
        container.attr('transform', event.transform.toString());
      });

    svg.call(zoom);

    // Column labels
    const columnLabels = container.append('g').attr('class', 'column-labels');

    columnLabels
      .append('text')
      .text('Bookmarks')
      .attr('x', colX.bookmark)
      .attr('y', 24)
      .attr('text-anchor', 'middle')
      .style('font-size', '13px')
      .style('font-weight', '600')
      .style('fill', '#64748b')
      .style('opacity', 0.6);

    columnLabels
      .append('text')
      .text('Evidence')
      .attr('x', colX.evidence)
      .attr('y', 24)
      .attr('text-anchor', 'middle')
      .style('font-size', '13px')
      .style('font-weight', '600')
      .style('fill', '#64748b')
      .style('opacity', 0.6);

    columnLabels
      .append('text')
      .text('Position')
      .attr('x', colX.position)
      .attr('y', 24)
      .attr('text-anchor', 'middle')
      .style('font-size', '13px')
      .style('font-weight', '600')
      .style('fill', '#64748b')
      .style('opacity', 0.6);

    // Links
    container
      .append('g')
      .attr('class', 'links')
      .selectAll('line')
      .data(links)
      .join('line')
      .attr('stroke', LINK_COLOUR)
      .attr('stroke-width', 1.5)
      .attr('stroke-opacity', 0.5);

    // Node groups
    const nodeGroup = container
      .append('g')
      .attr('class', 'nodes')
      .selectAll<SVGGElement, TrailNode>('g')
      .data(nodes)
      .join('g')
      .style('cursor', (d) => (d.column === 'bookmark' && d.url ? 'pointer' : 'default'))
      .on('click', (_event, d) => {
        if (d.column === 'bookmark' && d.url) {
          window.open(d.url, '_blank', 'noopener,noreferrer');
        }
      })
      .call(
        d3
          .drag<SVGGElement, TrailNode>()
          .on('start', (event: d3.D3DragEvent<SVGGElement, TrailNode, TrailNode>) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
          })
          .on('drag', (event: d3.D3DragEvent<SVGGElement, TrailNode, TrailNode>) => {
            event.subject.fx = event.x;
            event.subject.fy = event.y;
          })
          .on('end', (event: d3.D3DragEvent<SVGGElement, TrailNode, TrailNode>) => {
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
          }),
      );

    // Bridge ring (gold ring for bookmarks spanning multiple arcs)
    nodeGroup
      .filter((d) => d.column === 'bookmark' && !!d.isBridge)
      .append('circle')
      .attr('r', (d) => d.size + 3)
      .attr('fill', 'none')
      .attr('stroke', BRIDGE_RING_COLOUR)
      .attr('stroke-width', 3);

    // Main circle
    nodeGroup
      .append('circle')
      .attr('r', (d) => d.size)
      .attr('fill', (d) => d.colour)
      .attr('stroke', (d) => (d.isUnsourced ? EVIDENCE_COLOUR : '#fff'))
      .attr('stroke-width', 2)
      .attr('stroke-dasharray', (d) => (d.isUnsourced ? '4 2' : 'none'))
      .attr('opacity', 0.85);

    // Labels below each node
    nodeGroup
      .append('text')
      .text((d) => d.label)
      .attr('text-anchor', 'middle')
      .attr('dy', (d) => d.size + 14)
      .style('font-size', '10px')
      .style('fill', '#475569')
      .style('pointer-events', 'none');

    // Tick handler
    const linkElements = container.selectAll<SVGLineElement, TrailLink>('line');

    simulation.on('tick', () => {
      linkElements
        .attr('x1', (d) => (d.source as TrailNode).x ?? 0)
        .attr('y1', (d) => (d.source as TrailNode).y ?? 0)
        .attr('x2', (d) => (d.target as TrailNode).x ?? 0)
        .attr('y2', (d) => (d.target as TrailNode).y ?? 0);

      nodeGroup.attr('transform', (d) => `translate(${d.x ?? 0},${d.y ?? 0})`);
    });

    return () => {
      simulation.stop();
      svg.on('.zoom', null);
      svg.selectAll('*').remove();
    };
  }, [positionId, data, width, height]);

  if (isLoading) {
    return <p className="py-4 text-sm text-slate-500">Loading evidence trail...</p>;
  }

  if (error) {
    return (
      <p className="py-4 text-sm text-red-600">
        Failed to load evidence trail: {(error as Error).message}
      </p>
    );
  }

  if (!data) return null;

  const sourcedCount = data.evidence.length - data.unsourced_count;

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center gap-4 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm text-slate-600">
        <span>
          <strong className="text-slate-900">{data.evidence.length}</strong> evidence items
        </span>
        <span>
          <strong className="text-slate-900">{sourcedCount}</strong> sourced from bookmarks
        </span>
        <span>
          <strong className="text-slate-900">{data.bridge_bookmark_count}</strong> bridge bookmarks
        </span>
      </div>

      <div ref={containerRef} className="h-[480px] w-full min-h-0">
        <svg
          ref={svgRef}
          width={width}
          height={height}
          className="rounded-lg border border-slate-200 bg-slate-50"
          aria-label="Evidence trail visualisation"
        />
      </div>

      {showForm ? (
        <AddEvidenceForm positionId={positionId} onClose={() => setShowForm(false)} />
      ) : (
        <button
          type="button"
          onClick={() => setShowForm(true)}
          className="self-start rounded border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
        >
          Add evidence
        </button>
      )}
    </div>
  );
}
