'use client';

import { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import type { Arc, ThemeBridge } from '@/types/entities';
import type { GraphNode, GraphLink } from '@/types/graph';
import { useContainerSize } from '@/lib/hooks/use-container-size';

const NODE_COLOURS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

interface ArcExplorerProps {
  arcs: Arc[];
  bridges: ThemeBridge[];
}

function buildNodes(arcs: Arc[]): GraphNode[] {
  return arcs.map((arc, index) => ({
    id: arc.name,
    label: arc.name,
    size: Math.max(20, Math.min(60, 10 + (arc.bookmark_count + arc.session_count) * 3)),
    colour: NODE_COLOURS[index % NODE_COLOURS.length],
    data: arc,
  }));
}

function buildLinks(bridges: ThemeBridge[], nodeNames: Set<string>): GraphLink[] {
  const maxShared = Math.max(1, ...bridges.map((b) => b.shared_topics));
  return bridges
    .filter((b) => nodeNames.has(b.source_theme_name) && nodeNames.has(b.target_theme_name))
    .map((bridge) => ({
      source: bridge.source_theme_name,
      target: bridge.target_theme_name,
      label: `${bridge.shared_topics} shared topic${bridge.shared_topics === 1 ? '' : 's'}`,
      strength: Math.max(1, (bridge.shared_topics / maxShared) * 4),
    }));
}

export default function ArcExplorer({ arcs, bridges }: ArcExplorerProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [containerRef, { width, height }] = useContainerSize();

  useEffect(() => {
    const svgElement = svgRef.current;
    if (!svgElement || width === 0 || height === 0) {
      return;
    }

    const svg = d3.select(svgElement);
    svg.selectAll('*').remove();

    if (arcs.length === 0) {
      return;
    }

    const nodes = buildNodes(arcs);
    const nodeNames = new Set(nodes.map((n) => n.id));
    const links = buildLinks(bridges, nodeNames);

    const simulation = d3
      .forceSimulation<GraphNode>(nodes)
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('charge', d3.forceManyBody().strength(-300))
      .force(
        'link',
        d3
          .forceLink<GraphNode, GraphLink>(links)
          .id((d) => d.id)
          .distance(150),
      )
      .force('collision', d3.forceCollide<GraphNode>().radius((d) => d.size + 10));

    const container = svg.append('g');

    const zoom = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.3, 3])
      .on('zoom', (event: d3.D3ZoomEvent<SVGSVGElement, unknown>) => {
        container.attr('transform', event.transform.toString());
      });

    svg.call(zoom);

    const linkElements = container
      .append('g')
      .attr('class', 'links')
      .selectAll('line')
      .data(links)
      .join('line')
      .attr('stroke', '#94a3b8')
      .attr('stroke-width', (d) => d.strength)
      .attr('stroke-opacity', 0.6);

    const nodeGroup = container
      .append('g')
      .attr('class', 'nodes')
      .selectAll<SVGGElement, GraphNode>('g')
      .data(nodes)
      .join('g')
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
      linkElements
        .attr('x1', (d) => (d.source as GraphNode).x ?? 0)
        .attr('y1', (d) => (d.source as GraphNode).y ?? 0)
        .attr('x2', (d) => (d.target as GraphNode).x ?? 0)
        .attr('y2', (d) => (d.target as GraphNode).y ?? 0);

      nodeGroup.attr('transform', (d) => `translate(${d.x ?? 0},${d.y ?? 0})`);
    });

    return () => {
      simulation.stop();
      svg.on('.zoom', null);
      svg.selectAll('*').remove();
    };
  }, [arcs, bridges, width, height]);

  return (
    <div ref={containerRef} className="h-full w-full min-h-0">
      <svg
        ref={svgRef}
        width={width}
        height={height}
        className="rounded-lg border border-slate-200 bg-slate-50"
        aria-label="Theme explorer force-directed graph"
      />
    </div>
  );
}
