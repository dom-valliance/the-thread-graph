'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import type { Arc, ArcBridge, Bookmark } from '@/types/entities';
import type { GraphNode, GraphLink } from '@/types/graph';
import { useContainerSize } from '@/lib/hooks/use-container-size';
import { useArcBookmarks } from '@/lib/hooks/use-arc-bookmarks';
import BookmarkDetailPanel from './BookmarkDetailPanel';
import {
  ARC_PALETTE,
  GRAPH_COLOURS,
  MUTED_NODE_COLOUR,
  LINK_COLOUR,
  LABEL_COLOUR,
} from '@/lib/graph-colours';

const NODE_COLOURS = ARC_PALETTE.slice(0, 6);
const BOOKMARK_COLOUR = GRAPH_COLOURS.indigo;
const MORE_COLOUR = MUTED_NODE_COLOUR;
const EDGE_COLOUR = GRAPH_COLOURS.warning;

interface ArcExplorerProps {
  arcs: Arc[];
  bridges: ArcBridge[];
}

// ---------------------------------------------------------------------------
// Arc view helpers (unchanged)
// ---------------------------------------------------------------------------

function buildArcNodes(arcs: Arc[]): GraphNode[] {
  return arcs.map((arc, index) => ({
    id: arc.name,
    label: arc.name,
    size: Math.max(20, Math.min(60, 10 + (arc.bookmark_count + arc.session_count) * 3)),
    colour: NODE_COLOURS[index % NODE_COLOURS.length],
    data: arc,
    type: 'arc' as const,
  }));
}

function buildArcLinks(bridges: ArcBridge[], nodeNames: Set<string>): GraphLink[] {
  const maxShared = Math.max(1, ...bridges.map((b) => b.shared_topics));
  return bridges
    .filter((b) => nodeNames.has(b.source_arc_name) && nodeNames.has(b.target_arc_name))
    .map((bridge) => ({
      source: bridge.source_arc_name,
      target: bridge.target_arc_name,
      label: `${bridge.shared_topics} shared topic${bridge.shared_topics === 1 ? '' : 's'}`,
      strength: Math.max(1, (bridge.shared_topics / maxShared) * 4),
    }));
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function ArcExplorer({ arcs, bridges }: ArcExplorerProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [containerRef, { width, height }] = useContainerSize();

  const [viewMode, setViewMode] = useState<'arcs' | 'drilldown'>('arcs');
  const [selectedArcName, setSelectedArcName] = useState<string | null>(null);
  const [selectedBookmark, setSelectedBookmark] = useState<Bookmark | null>(null);

  const { bookmarks, edges, hasMore, isLoading, loadMore, reset } =
    useArcBookmarks(selectedArcName);

  // Find the Arc object for colour lookup
  const selectedArc = arcs.find((a) => a.name === selectedArcName);
  const selectedArcIndex = arcs.findIndex((a) => a.name === selectedArcName);
  const selectedArcColour = NODE_COLOURS[selectedArcIndex % NODE_COLOURS.length] ?? NODE_COLOURS[0];

  // Handlers
  const handleArcClick = useCallback((arcName: string) => {
    setSelectedArcName(arcName);
    setViewMode('drilldown');
    setSelectedBookmark(null);
  }, []);

  const handleBackToArcs = useCallback(() => {
    setViewMode('arcs');
    setSelectedArcName(null);
    setSelectedBookmark(null);
    reset();
  }, [reset]);

  const handleBookmarkClick = useCallback((bookmark: Bookmark) => {
    setSelectedBookmark(bookmark);
  }, []);

  const handleClosePanel = useCallback(() => {
    setSelectedBookmark(null);
  }, []);

  // Escape key
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key !== 'Escape') return;
      if (selectedBookmark) {
        setSelectedBookmark(null);
      } else if (viewMode === 'drilldown') {
        handleBackToArcs();
      }
    }
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [selectedBookmark, viewMode, handleBackToArcs]);

  // ---------------------------------------------------------------------------
  // Arc view rendering
  // ---------------------------------------------------------------------------

  useEffect(() => {
    if (viewMode !== 'arcs') return;
    const svgElement = svgRef.current;
    if (!svgElement || width === 0 || height === 0) return;

    const svg = d3.select(svgElement);
    svg.selectAll('*').remove();

    if (arcs.length === 0) return;

    const nodes = buildArcNodes(arcs);
    const nodeNames = new Set(nodes.map((n) => n.id));
    const links = buildArcLinks(bridges, nodeNames);

    const simulation = d3
      .forceSimulation<GraphNode>(nodes)
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('charge', d3.forceManyBody().strength(-600))
      .force(
        'link',
        d3
          .forceLink<GraphNode, GraphLink>(links)
          .id((d) => d.id)
          .distance(250),
      )
      .force('collision', d3.forceCollide<GraphNode>().radius((d) => d.size + 30));

    const container = svg.append('g');

    const zoom = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.3, 3])
      .on('zoom', (event: d3.D3ZoomEvent<SVGSVGElement, unknown>) => {
        container.attr('transform', event.transform.toString());
      });

    svg.call(zoom);

    // Assign a curve offset to each link so parallel edges fan out
    const linkOffsets = new Map<string, number>();
    const pairCounts = new Map<string, number>();
    links.forEach((link) => {
      const srcId = typeof link.source === 'string' ? link.source : (link.source as GraphNode).id;
      const tgtId = typeof link.target === 'string' ? link.target : (link.target as GraphNode).id;
      const pairKey = [srcId, tgtId].sort().join('::');
      const idx = pairCounts.get(pairKey) ?? 0;
      pairCounts.set(pairKey, idx + 1);
      linkOffsets.set(`${srcId}->${tgtId}`, (idx + 1) * 40);
    });

    const linkElements = container
      .append('g')
      .attr('class', 'links')
      .selectAll('path')
      .data(links)
      .join('path')
      .attr('fill', 'none')
      .attr('stroke', MUTED_NODE_COLOUR)
      .attr('stroke-width', (d) => d.strength)
      .attr('stroke-opacity', 0.6);

    const nodeGroup = container
      .append('g')
      .attr('class', 'nodes')
      .selectAll<SVGGElement, GraphNode>('g')
      .data(nodes)
      .join('g')
      .style('cursor', 'pointer')
      .on('click', (_event, d) => {
        handleArcClick(d.id);
      })
      .call(
        d3
          .drag<SVGGElement, GraphNode>()
          .on('start', (event: d3.D3DragEvent<SVGGElement, GraphNode, GraphNode>) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
          })
          .on('drag', (event: d3.D3DragEvent<SVGGElement, GraphNode, GraphNode>) => {
            event.subject.fx = event.x;
            event.subject.fy = event.y;
          })
          .on('end', (event: d3.D3DragEvent<SVGGElement, GraphNode, GraphNode>) => {
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
          }),
      );

    nodeGroup
      .append('circle')
      .attr('r', (d) => d.size)
      .attr('fill', (d) => d.colour)
      .attr('stroke', '#fff')
      .attr('stroke-width', 2);

    nodeGroup
      .append('text')
      .text((d) => d.label)
      .attr('text-anchor', 'middle')
      .attr('dy', (d) => d.size + 16)
      .attr('class', 'text-xs fill-slate-700')
      .style('font-size', '12px')
      .style('pointer-events', 'none');

    simulation.on('tick', () => {
      linkElements.attr('d', (d) => {
        const src = d.source as GraphNode;
        const tgt = d.target as GraphNode;
        const sx = src.x ?? 0;
        const sy = src.y ?? 0;
        const tx = tgt.x ?? 0;
        const ty = tgt.y ?? 0;

        // Perpendicular offset for the control point
        const dx = tx - sx;
        const dy = ty - sy;
        const len = Math.sqrt(dx * dx + dy * dy) || 1;
        const srcId = src.id;
        const tgtId = tgt.id;
        const offset = linkOffsets.get(`${srcId}->${tgtId}`) ?? 40;
        // Normal vector perpendicular to the link
        const nx = -dy / len;
        const ny = dx / len;
        const cx = (sx + tx) / 2 + nx * offset;
        const cy = (sy + ty) / 2 + ny * offset;

        return `M ${sx},${sy} Q ${cx},${cy} ${tx},${ty}`;
      });

      nodeGroup.attr('transform', (d) => `translate(${d.x ?? 0},${d.y ?? 0})`);
    });

    return () => {
      simulation.stop();
      svg.on('.zoom', null);
      svg.selectAll('*').remove();
    };
  }, [arcs, bridges, width, height, viewMode, handleArcClick]);

  // ---------------------------------------------------------------------------
  // Drill-down view rendering
  // ---------------------------------------------------------------------------

  useEffect(() => {
    if (viewMode !== 'drilldown') return;
    const svgElement = svgRef.current;
    if (!svgElement || width === 0 || height === 0) return;
    if (!selectedArcName || bookmarks.length === 0) return;

    const svg = d3.select(svgElement);
    svg.selectAll('*').remove();

    // Build nodes
    const allNodes: GraphNode[] = [];
    const allLinks: GraphLink[] = [];

    // Centre arc node
    const arcNode: GraphNode = {
      id: selectedArcName,
      label: selectedArcName,
      size: 40,
      colour: selectedArcColour,
      data: selectedArc,
      type: 'arc',
      fx: width / 2,
      fy: height / 2,
    };
    allNodes.push(arcNode);

    // Bookmark nodes
    bookmarks.forEach((bm) => {
      const nodeId = `bm:${bm.notion_id ?? bm.id}`;
      allNodes.push({
        id: nodeId,
        label: bm.title.length > 30 ? bm.title.slice(0, 27) + '...' : bm.title,
        size: Math.max(12, Math.min(28, 8 + bm.topic_names.length * 4)),
        colour: BOOKMARK_COLOUR,
        data: bm,
        type: 'bookmark',
      });

      // Link bookmark to centre arc
      allLinks.push({
        source: selectedArcName,
        target: nodeId,
        label: null,
        strength: 1,
      });
    });

    // "More..." node
    if (hasMore) {
      allNodes.push({
        id: 'more',
        label: 'more...',
        size: 16,
        colour: MORE_COLOUR,
        data: null,
        type: 'more',
      });
      allLinks.push({
        source: selectedArcName,
        target: 'more',
        label: null,
        strength: 0.5,
      });
    }

    // Bookmark-to-bookmark edges
    const maxShared = Math.max(1, ...edges.map((e) => e.shared_topics));
    edges.forEach((edge) => {
      allLinks.push({
        source: `bm:${edge.source_notion_id}`,
        target: `bm:${edge.target_notion_id}`,
        label: edge.shared_topic_names.join(', '),
        strength: Math.max(1, (edge.shared_topics / maxShared) * 3),
      });
    });

    const simulation = d3
      .forceSimulation<GraphNode>(allNodes)
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('charge', d3.forceManyBody().strength(-150))
      .force(
        'link',
        d3
          .forceLink<GraphNode, GraphLink>(allLinks)
          .id((d) => d.id)
          .distance(100),
      )
      .force('collision', d3.forceCollide<GraphNode>().radius((d) => d.size + 8))
      .force(
        'radial',
        d3
          .forceRadial<GraphNode>(
            (d) => (d.type === 'arc' ? 0 : 150),
            width / 2,
            height / 2,
          )
          .strength((d) => (d.type === 'arc' ? 0 : 0.3)),
      );

    const container = svg.append('g');

    const zoom = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.3, 3])
      .on('zoom', (event: d3.D3ZoomEvent<SVGSVGElement, unknown>) => {
        container.attr('transform', event.transform.toString());
      });

    svg.call(zoom);

    // Assign curve offsets for the drill-down links
    const ddLinkOffsets = new Map<string, number>();
    const ddPairCounts = new Map<string, number>();
    allLinks.forEach((link) => {
      const srcId = typeof link.source === 'string' ? link.source : (link.source as GraphNode).id;
      const tgtId = typeof link.target === 'string' ? link.target : (link.target as GraphNode).id;
      const pairKey = [srcId, tgtId].sort().join('::');
      const idx = ddPairCounts.get(pairKey) ?? 0;
      ddPairCounts.set(pairKey, idx + 1);
      ddLinkOffsets.set(`${srcId}->${tgtId}`, (idx + 1) * 30);
    });

    // Links
    const linkElements = container
      .append('g')
      .attr('class', 'links')
      .selectAll('path')
      .data(allLinks)
      .join('path')
      .attr('fill', 'none')
      .attr('stroke', (d) => {
        const sourceId = typeof d.source === 'string' ? d.source : (d.source as GraphNode).id;
        const targetId = typeof d.target === 'string' ? d.target : (d.target as GraphNode).id;
        // Bookmark-to-bookmark edges are amber
        if (sourceId.startsWith('bm:') && targetId.startsWith('bm:')) return EDGE_COLOUR;
        return LINK_COLOUR;
      })
      .attr('stroke-width', (d) => d.strength)
      .attr('stroke-opacity', 0.5);

    // Nodes
    const nodeGroup = container
      .append('g')
      .attr('class', 'nodes')
      .selectAll<SVGGElement, GraphNode>('g')
      .data(allNodes)
      .join('g')
      .style('cursor', (d) => (d.type === 'more' || d.type === 'bookmark' ? 'pointer' : 'default'))
      .on('click', (_event, d) => {
        if (d.type === 'more') {
          loadMore();
        } else if (d.type === 'bookmark') {
          handleBookmarkClick(d.data as Bookmark);
        }
      })
      .call(
        d3
          .drag<SVGGElement, GraphNode>()
          .on('start', (event: d3.D3DragEvent<SVGGElement, GraphNode, GraphNode>) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
          })
          .on('drag', (event: d3.D3DragEvent<SVGGElement, GraphNode, GraphNode>) => {
            event.subject.fx = event.x;
            event.subject.fy = event.y;
          })
          .on('end', (event: d3.D3DragEvent<SVGGElement, GraphNode, GraphNode>) => {
            if (!event.active) simulation.alphaTarget(0);
            // Keep arc pinned at centre
            if (event.subject.type === 'arc') {
              event.subject.fx = width / 2;
              event.subject.fy = height / 2;
            } else {
              event.subject.fx = null;
              event.subject.fy = null;
            }
          }),
      );

    // Circle rendering
    nodeGroup
      .append('circle')
      .attr('r', (d) => d.size)
      .attr('fill', (d) => d.colour)
      .attr('stroke', (d) => (d.type === 'more' ? MORE_COLOUR : '#fff'))
      .attr('stroke-width', (d) => (d.type === 'more' ? 1 : 2))
      .attr('stroke-dasharray', (d) => (d.type === 'more' ? '4 2' : 'none'))
      .attr('fill-opacity', (d) => (d.type === 'more' ? 0.3 : 1));

    // Labels
    nodeGroup
      .append('text')
      .text((d) => d.label)
      .attr('text-anchor', 'middle')
      .attr('dy', (d) => d.size + 14)
      .style('font-size', (d) => (d.type === 'arc' ? '13px' : '10px'))
      .style('font-weight', (d) => (d.type === 'arc' ? '600' : '400'))
      .style('fill', LABEL_COLOUR)
      .style('pointer-events', 'none');

    simulation.on('tick', () => {
      linkElements.attr('d', (d) => {
        const src = d.source as GraphNode;
        const tgt = d.target as GraphNode;
        const sx = src.x ?? 0;
        const sy = src.y ?? 0;
        const tx = tgt.x ?? 0;
        const ty = tgt.y ?? 0;

        const dx = tx - sx;
        const dy = ty - sy;
        const len = Math.sqrt(dx * dx + dy * dy) || 1;
        const offset = ddLinkOffsets.get(`${src.id}->${tgt.id}`) ?? 30;
        const nx = -dy / len;
        const ny = dx / len;
        const cx = (sx + tx) / 2 + nx * offset;
        const cy = (sy + ty) / 2 + ny * offset;

        return `M ${sx},${sy} Q ${cx},${cy} ${tx},${ty}`;
      });

      nodeGroup.attr('transform', (d) => `translate(${d.x ?? 0},${d.y ?? 0})`);
    });

    return () => {
      simulation.stop();
      svg.on('.zoom', null);
      svg.selectAll('*').remove();
    };
  }, [
    viewMode,
    selectedArcName,
    selectedArcColour,
    selectedArc,
    bookmarks,
    edges,
    hasMore,
    width,
    height,
    loadMore,
    handleBookmarkClick,
  ]);

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------

  return (
    <div ref={containerRef} className="relative h-full w-full min-h-0">
      {/* Back button in drill-down mode */}
      {viewMode === 'drilldown' && (
        <button
          onClick={handleBackToArcs}
          className="absolute left-3 top-3 z-10 flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50"
        >
          <svg
            className="h-4 w-4"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={2}
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
          Back to arcs
        </button>
      )}

      {/* Loading indicator */}
      {viewMode === 'drilldown' && isLoading && (
        <div className="absolute left-1/2 top-3 z-10 -translate-x-1/2 rounded-full bg-slate-800 px-3 py-1 text-xs text-white">
          Loading bookmarks...
        </div>
      )}

      {/* Empty state for drill-down */}
      {viewMode === 'drilldown' && !isLoading && bookmarks.length === 0 && selectedArcName && (
        <div className="absolute left-1/2 top-1/2 z-10 -translate-x-1/2 -translate-y-1/2 text-center">
          <p className="text-sm text-slate-500">No bookmarks in this arc yet.</p>
          <button
            onClick={handleBackToArcs}
            className="mt-2 text-sm font-medium text-blue-600 hover:text-blue-700"
          >
            Back to arcs
          </button>
        </div>
      )}

      <svg
        ref={svgRef}
        width={width}
        height={height}
        className="rounded-lg border border-slate-200 bg-slate-50"
        aria-label={
          viewMode === 'arcs'
            ? 'Arc explorer force-directed graph'
            : `Bookmarks for ${selectedArcName}`
        }
      />

      {/* Bookmark detail panel */}
      <BookmarkDetailPanel bookmark={selectedBookmark} onClose={handleClosePanel} />
    </div>
  );
}
