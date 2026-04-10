'use client';

import { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import type { CrossArcBridge, UnconnectedPosition } from '@/types/entities';
import type { GraphNode, GraphLink } from '@/types/graph';
import { useContainerSize } from '@/lib/hooks/use-container-size';

const NODE_COLOURS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

const STRENGTH_STYLES: Record<string, { width: number; colour: string; dash: string }> = {
  Core: { width: 3, colour: '#1e293b', dash: 'none' },
  Supporting: { width: 2, colour: '#64748b', dash: 'none' },
  Tangential: { width: 1, colour: '#94a3b8', dash: '4 2' },
};

interface BridgeExplorerProps {
  bridges: CrossArcBridge[];
  gaps: UnconnectedPosition[];
}

function truncate(text: string, max: number): string {
  return text.length > max ? text.slice(0, max - 3) + '...' : text;
}

export default function BridgeExplorer({ bridges, gaps }: BridgeExplorerProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [containerRef, { width, height }] = useContainerSize();

  useEffect(() => {
    const svgElement = svgRef.current;
    if (!svgElement || width === 0 || height === 0) return;

    const svg = d3.select(svgElement);
    svg.selectAll('*').remove();

    // Collect unique arcs from bridges
    const arcSet = new Map<number, string>();
    bridges.forEach((b) => {
      arcSet.set(b.source_arc_number, b.source_arc_name);
      arcSet.set(b.target_arc_number, b.target_arc_name);
    });
    gaps.forEach((g) => {
      arcSet.set(g.arc_number, g.arc_name);
    });

    const arcEntries = Array.from(arcSet.entries()).sort((a, b) => a[0] - b[0]);

    if (arcEntries.length === 0) return;

    // Compute hex centres
    const cx = width / 2;
    const cy = height / 2;
    const radius = Math.min(width, height) * 0.3;

    const arcCentres = new Map<number, { x: number; y: number }>();
    arcEntries.forEach(([num], i) => {
      const angle = (i / arcEntries.length) * 2 * Math.PI - Math.PI / 2;
      arcCentres.set(num, {
        x: cx + radius * Math.cos(angle),
        y: cy + radius * Math.sin(angle),
      });
    });

    // Build position nodes from bridges
    const positionMap = new Map<
      string,
      { id: string; text: string; arcNumber: number; arcName: string; connected: boolean }
    >();

    bridges.forEach((b) => {
      if (!positionMap.has(b.source_position_id)) {
        positionMap.set(b.source_position_id, {
          id: b.source_position_id,
          text: b.source_position_text,
          arcNumber: b.source_arc_number,
          arcName: b.source_arc_name,
          connected: true,
        });
      }
      if (!positionMap.has(b.target_position_id)) {
        positionMap.set(b.target_position_id, {
          id: b.target_position_id,
          text: b.target_position_text,
          arcNumber: b.target_arc_number,
          arcName: b.target_arc_name,
          connected: true,
        });
      }
    });

    gaps.forEach((g) => {
      if (!positionMap.has(g.id)) {
        positionMap.set(g.id, {
          id: g.id,
          text: g.text,
          arcNumber: g.arc_number,
          arcName: g.arc_name,
          connected: false,
        });
      }
    });

    // Build graph nodes
    const nodes: GraphNode[] = Array.from(positionMap.values()).map((p) => {
      const centre = arcCentres.get(p.arcNumber) ?? { x: cx, y: cy };
      return {
        id: p.id,
        label: truncate(p.text, 25),
        size: 14,
        colour: NODE_COLOURS[(p.arcNumber - 1) % NODE_COLOURS.length],
        data: p,
        type: 'position' as const,
        x: centre.x + (Math.random() - 0.5) * 60,
        y: centre.y + (Math.random() - 0.5) * 60,
      };
    });

    // Build links
    const links: (GraphLink & { bridgeData: CrossArcBridge })[] = bridges.map((b) => ({
      source: b.source_position_id,
      target: b.target_position_id,
      label: b.label,
      strength: STRENGTH_STYLES[b.strength]?.width ?? 1,
      bridgeData: b,
    }));

    const simulation = d3
      .forceSimulation<GraphNode>(nodes)
      .force('charge', d3.forceManyBody().strength(-80))
      .force('collision', d3.forceCollide<GraphNode>().radius(22))
      .force(
        'link',
        d3
          .forceLink<GraphNode, GraphLink>(links)
          .id((d) => d.id)
          .distance(200)
          .strength(0.1),
      )
      .force(
        'arcX',
        d3.forceX<GraphNode>((d) => {
          const p = d.data as { arcNumber: number };
          return arcCentres.get(p.arcNumber)?.x ?? cx;
        }).strength(0.3),
      )
      .force(
        'arcY',
        d3.forceY<GraphNode>((d) => {
          const p = d.data as { arcNumber: number };
          return arcCentres.get(p.arcNumber)?.y ?? cy;
        }).strength(0.3),
      );

    const container = svg.append('g');

    const zoom = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.3, 3])
      .on('zoom', (event: d3.D3ZoomEvent<SVGSVGElement, unknown>) => {
        container.attr('transform', event.transform.toString());
      });

    svg.call(zoom);

    // Arc labels (background)
    container
      .append('g')
      .attr('class', 'arc-labels')
      .selectAll('text')
      .data(arcEntries)
      .join('text')
      .attr('x', ([num]) => arcCentres.get(num)?.x ?? cx)
      .attr('y', ([num]) => (arcCentres.get(num)?.y ?? cy) - radius * 0.35)
      .attr('text-anchor', 'middle')
      .attr('fill', '#94a3b8')
      .attr('font-size', '14px')
      .attr('font-weight', '600')
      .text(([, name]) => name);

    // Links
    const linkElements = container
      .append('g')
      .attr('class', 'links')
      .selectAll('line')
      .data(links)
      .join('line')
      .attr('stroke', (d) => STRENGTH_STYLES[d.bridgeData.strength]?.colour ?? '#94a3b8')
      .attr('stroke-width', (d) => STRENGTH_STYLES[d.bridgeData.strength]?.width ?? 1)
      .attr('stroke-dasharray', (d) => STRENGTH_STYLES[d.bridgeData.strength]?.dash ?? 'none')
      .attr('stroke-opacity', 0.7);

    // Tooltip
    const tooltip = d3
      .select('body')
      .append('div')
      .attr('class', 'bridge-tooltip')
      .style('position', 'absolute')
      .style('visibility', 'hidden')
      .style('background', 'white')
      .style('border', '1px solid #e2e8f0')
      .style('border-radius', '8px')
      .style('padding', '10px 14px')
      .style('font-size', '12px')
      .style('color', '#334155')
      .style('box-shadow', '0 2px 8px rgba(0,0,0,0.1)')
      .style('max-width', '300px')
      .style('z-index', '50')
      .style('pointer-events', 'none');

    // Nodes
    const nodeGroup = container
      .append('g')
      .attr('class', 'nodes')
      .selectAll<SVGGElement, GraphNode>('g')
      .data(nodes)
      .join('g')
      .style('cursor', 'pointer')
      .on('mouseover', (_event, d) => {
        const p = d.data as { text: string; arcName: string; connected: boolean };
        tooltip
          .html(
            `<strong>${p.arcName}</strong><br/>${p.text}${
              !p.connected ? '<br/><em style="color:#ef4444">No cross-arc bridges</em>' : ''
            }`,
          )
          .style('visibility', 'visible');
      })
      .on('mousemove', (event) => {
        tooltip
          .style('top', event.pageY - 10 + 'px')
          .style('left', event.pageX + 10 + 'px');
      })
      .on('mouseout', () => {
        tooltip.style('visibility', 'hidden');
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
      .attr('stroke', (d) => {
        const p = d.data as { connected: boolean };
        return p.connected ? '#fff' : d.colour;
      })
      .attr('stroke-width', (d) => {
        const p = d.data as { connected: boolean };
        return p.connected ? 2 : 1.5;
      })
      .attr('stroke-dasharray', (d) => {
        const p = d.data as { connected: boolean };
        return p.connected ? 'none' : '3 2';
      })
      .attr('fill-opacity', (d) => {
        const p = d.data as { connected: boolean };
        return p.connected ? 1 : 0.4;
      });

    nodeGroup
      .append('text')
      .text((d) => d.label)
      .attr('text-anchor', 'middle')
      .attr('dy', (d) => d.size + 12)
      .style('font-size', '9px')
      .style('fill', '#64748b')
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
      tooltip.remove();
    };
  }, [bridges, gaps, width, height]);

  return (
    <div className="flex h-full gap-4">
      {/* Main graph area */}
      <div ref={containerRef} className="flex-1 min-h-0 min-w-0">
        <svg
          ref={svgRef}
          width={width}
          height={height}
          className="rounded-lg border border-slate-200 bg-slate-50"
          aria-label="Cross-arc bridge explorer"
        />
      </div>

      {/* Unconnected positions sidebar */}
      {gaps.length > 0 && (
        <div className="w-64 shrink-0 overflow-y-auto rounded-lg border border-slate-200 bg-white p-3">
          <h3 className="mb-2 text-sm font-semibold text-slate-700">
            Unconnected positions ({gaps.length})
          </h3>
          <ul className="space-y-2">
            {gaps.map((g) => (
              <li key={g.id} className="rounded border border-dashed border-slate-300 p-2">
                <span
                  className="mb-1 inline-block rounded-full px-2 py-0.5 text-xs font-medium"
                  style={{
                    backgroundColor: NODE_COLOURS[(g.arc_number - 1) % NODE_COLOURS.length] + '20',
                    color: NODE_COLOURS[(g.arc_number - 1) % NODE_COLOURS.length],
                  }}
                >
                  {g.arc_name}
                </span>
                <p className="text-xs text-slate-600">{truncate(g.text, 80)}</p>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
