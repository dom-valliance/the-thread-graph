'use client';

import { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import type { Argument } from '@/types/entities';
import type { GraphNode } from '@/types/graph';
import { useContainerSize } from '@/lib/hooks/use-container-size';

const SUPPORT_COLOUR = '#22c55e';
const CHALLENGE_COLOUR = '#ef4444';
const POSITION_COLOUR = '#3b82f6';

const STRENGTH_RADIUS: Record<string, number> = {
  Strong: 24,
  Moderate: 18,
  Weak: 12,
};

interface ArgumentMapProps {
  positionId: string;
  positionText: string;
  arguments: Argument[];
}

interface ArgumentNode extends GraphNode {
  zone: 'centre' | 'support' | 'challenge';
}

interface ArgumentLink extends d3.SimulationLinkDatum<ArgumentNode> {
  label: string | null;
  strength: number;
}

function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return `${text.slice(0, maxLength - 1)}...`;
}

function buildNodes(positionId: string, positionText: string, args: Argument[]): ArgumentNode[] {
  const centreNode: ArgumentNode = {
    id: positionId,
    label: truncate(positionText, 60),
    size: 36,
    colour: POSITION_COLOUR,
    data: null,
    zone: 'centre',
  };

  const argNodes: ArgumentNode[] = args.map((arg) => {
    const isSupporting = arg.type.toLowerCase() === 'supporting' || arg.type.toLowerCase() === 'support';
    return {
      id: arg.id,
      label: truncate(arg.text, 40),
      size: STRENGTH_RADIUS[arg.strength] ?? 16,
      colour: isSupporting ? SUPPORT_COLOUR : CHALLENGE_COLOUR,
      data: arg,
      zone: isSupporting ? 'support' : 'challenge',
    };
  });

  return [centreNode, ...argNodes];
}

function buildLinks(positionId: string, args: Argument[]): ArgumentLink[] {
  return args.map((arg) => ({
    source: arg.id,
    target: positionId,
    label: null,
    strength: 1,
  }));
}

export default function ArgumentMap({
  positionId,
  positionText,
  arguments: args,
}: ArgumentMapProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [containerRef, { width, height }] = useContainerSize();

  useEffect(() => {
    const svgElement = svgRef.current;
    if (!svgElement || width === 0 || height === 0) return;

    const svg = d3.select(svgElement);
    svg.selectAll('*').remove();

    const nodes = buildNodes(positionId, positionText, args);
    const links = buildLinks(positionId, args);

    if (nodes.length <= 1) return;

    const centreX = width / 2;
    const centreY = height / 2;

    const simulation = d3
      .forceSimulation<ArgumentNode>(nodes)
      .force('center', d3.forceCenter(centreX, centreY))
      .force('charge', d3.forceManyBody().strength(-200))
      .force(
        'link',
        d3
          .forceLink<ArgumentNode, ArgumentLink>(links)
          .id((d) => d.id)
          .distance(120),
      )
      .force('collision', d3.forceCollide<ArgumentNode>().radius((d) => d.size + 8))
      .force(
        'x',
        d3.forceX<ArgumentNode>().x((d) => {
          if (d.zone === 'centre') return centreX;
          if (d.zone === 'support') return centreX - width * 0.25;
          return centreX + width * 0.25;
        }).strength(0.15),
      )
      .force('y', d3.forceY(centreY).strength(0.1));

    const container = svg.append('g');

    const zoom = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.3, 3])
      .on('zoom', (event: d3.D3ZoomEvent<SVGSVGElement, unknown>) => {
        container.attr('transform', event.transform.toString());
      });

    svg.call(zoom);

    const zoneLabels = container.append('g').attr('class', 'zone-labels');

    zoneLabels
      .append('text')
      .text('Supporting')
      .attr('x', centreX - width * 0.25)
      .attr('y', 24)
      .attr('text-anchor', 'middle')
      .style('font-size', '13px')
      .style('font-weight', '600')
      .style('fill', SUPPORT_COLOUR)
      .style('opacity', 0.6);

    zoneLabels
      .append('text')
      .text('Challenging')
      .attr('x', centreX + width * 0.25)
      .attr('y', 24)
      .attr('text-anchor', 'middle')
      .style('font-size', '13px')
      .style('font-weight', '600')
      .style('fill', CHALLENGE_COLOUR)
      .style('opacity', 0.6);

    const linkElements = container
      .append('g')
      .attr('class', 'links')
      .selectAll('line')
      .data(links)
      .join('line')
      .attr('stroke', '#cbd5e1')
      .attr('stroke-width', 1.5)
      .attr('stroke-opacity', 0.5);

    const nodeGroup = container
      .append('g')
      .attr('class', 'nodes')
      .selectAll<SVGGElement, ArgumentNode>('g')
      .data(nodes)
      .join('g')
      .call(
        d3
          .drag<SVGGElement, ArgumentNode>()
          .on('start', (event: d3.D3DragEvent<SVGGElement, ArgumentNode, ArgumentNode>) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
          })
          .on('drag', (event: d3.D3DragEvent<SVGGElement, ArgumentNode, ArgumentNode>) => {
            event.subject.fx = event.x;
            event.subject.fy = event.y;
          })
          .on('end', (event: d3.D3DragEvent<SVGGElement, ArgumentNode, ArgumentNode>) => {
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
      .attr('stroke-width', 2)
      .attr('opacity', 0.85);

    nodeGroup
      .append('text')
      .text((d) => d.label)
      .attr('text-anchor', 'middle')
      .attr('dy', (d) => d.size + 14)
      .style('font-size', (d) => (d.zone === 'centre' ? '12px' : '10px'))
      .style('fill', '#475569')
      .style('pointer-events', 'none');

    simulation.on('tick', () => {
      linkElements
        .attr('x1', (d) => (d.source as ArgumentNode).x ?? 0)
        .attr('y1', (d) => (d.source as ArgumentNode).y ?? 0)
        .attr('x2', (d) => (d.target as ArgumentNode).x ?? 0)
        .attr('y2', (d) => (d.target as ArgumentNode).y ?? 0);

      nodeGroup.attr('transform', (d) => `translate(${d.x ?? 0},${d.y ?? 0})`);
    });

    return () => {
      simulation.stop();
      svg.on('.zoom', null);
      svg.selectAll('*').remove();
    };
  }, [positionId, positionText, args, width, height]);

  return (
    <div ref={containerRef} className="h-full w-full min-h-0">
      <svg
        ref={svgRef}
        width={width}
        height={height}
        className="rounded-lg border border-slate-200 bg-slate-50"
        aria-label="Argument map visualisation"
      />
    </div>
  );
}
