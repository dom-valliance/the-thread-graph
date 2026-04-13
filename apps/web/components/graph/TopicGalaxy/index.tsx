'use client';

import { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import type { Topic, TopicCoOccurrence } from '@/types/entities';
import type { GraphNode } from '@/types/graph';
import { useContainerSize } from '@/lib/hooks/use-container-size';
import { ARC_PALETTE, LABEL_COLOUR, MUTED_NODE_COLOUR, TOOLTIP_BG, TOOLTIP_FG } from '@/lib/graph-colours';

interface TopicNode extends GraphNode {
  data: Topic;
}

interface TopicLink extends d3.SimulationLinkDatum<TopicNode> {
  strength: number;
}

interface TopicGalaxyProps {
  topics: Topic[];
  coOccurrences?: TopicCoOccurrence[];
  onTopicSelect?: (topic: Topic) => void;
}

function arcColour(arc: string | null | undefined, index: number): string {
  if (!arc) return ARC_PALETTE[index % ARC_PALETTE.length];
  let hash = 0;
  for (let i = 0; i < arc.length; i++) {
    hash = arc.charCodeAt(i) + ((hash << 5) - hash);
  }
  return ARC_PALETTE[Math.abs(hash) % ARC_PALETTE.length];
}

function nodeRadius(topic: Topic): number {
  const count = topic.bookmark_count ?? 1;
  return Math.max(8, Math.min(40, 6 + Math.sqrt(count) * 4));
}

function buildNodes(topics: Topic[]): TopicNode[] {
  return topics.map((topic, index) => ({
    id: topic.name,
    label: topic.name,
    size: nodeRadius(topic),
    colour: arcColour(topic.primary_arc, index),
    data: topic,
  }));
}

function buildLinks(
  coOccurrences: TopicCoOccurrence[],
  nodeNames: Set<string>,
): TopicLink[] {
  const maxCount = Math.max(1, ...coOccurrences.map((c) => c.count));
  return coOccurrences
    .filter((c) => nodeNames.has(c.name) && nodeNames.has(c.co_occurring_topic))
    .map((c) => ({
      source: c.name,
      target: c.co_occurring_topic,
      strength: Math.max(1, (c.count / maxCount) * 4),
    }));
}

export default function TopicGalaxy({ topics, coOccurrences = [], onTopicSelect }: TopicGalaxyProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [containerRef, { width, height }] = useContainerSize();

  useEffect(() => {
    const svgElement = svgRef.current;
    if (!svgElement || width === 0 || height === 0) return;

    const svg = d3.select(svgElement);
    svg.selectAll('*').remove();

    if (topics.length === 0) return;

    const nodes = buildNodes(topics);
    const nodeNames = new Set(nodes.map((n) => n.id));
    const links = buildLinks(coOccurrences, nodeNames);

    const simulation = d3
      .forceSimulation<TopicNode>(nodes)
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('charge', d3.forceManyBody().strength(-250))
      .force('collision', d3.forceCollide<TopicNode>().radius((d) => d.size + 20))
      .force('x', d3.forceX(width / 2).strength(0.04))
      .force('y', d3.forceY(height / 2).strength(0.04));

    if (links.length > 0) {
      simulation.force(
        'link',
        d3
          .forceLink<TopicNode, TopicLink>(links)
          .id((d) => d.id)
          .distance(200),
      );
    }

    const container = svg.append('g');

    const zoom = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.3, 3])
      .on('zoom', (event: d3.D3ZoomEvent<SVGSVGElement, unknown>) => {
        container.attr('transform', event.transform.toString());
      });

    svg.call(zoom);

    const tooltip = d3
      .select('body')
      .append('div')
      .attr('class', 'topic-galaxy-tooltip')
      .style('position', 'absolute')
      .style('padding', '6px 10px')
      .style('background', TOOLTIP_BG)
      .style('color', TOOLTIP_FG)
      .style('border-radius', '6px')
      .style('font-size', '12px')
      .style('pointer-events', 'none')
      .style('opacity', 0);

    const linkElements = container
      .append('g')
      .attr('class', 'links')
      .selectAll('line')
      .data(links)
      .join('line')
      .attr('stroke', MUTED_NODE_COLOUR)
      .attr('stroke-width', (d) => d.strength)
      .attr('stroke-opacity', 0.5);

    const nodeGroup = container
      .append('g')
      .attr('class', 'nodes')
      .selectAll<SVGGElement, TopicNode>('g')
      .data(nodes)
      .join('g')
      .style('cursor', onTopicSelect ? 'pointer' : 'default')
      .on('click', (_event, d) => {
        onTopicSelect?.(d.data);
      })
      .on('mouseenter', (event, d) => {
        const bookmarks = d.data.bookmark_count ?? 0;
        const arc = d.data.primary_arc ?? 'No arc';
        tooltip
          .html(`<strong>${d.label}</strong><br/>Arc: ${arc}<br/>${bookmarks} bookmark${bookmarks === 1 ? '' : 's'}`)
          .style('left', `${event.pageX + 12}px`)
          .style('top', `${event.pageY - 10}px`)
          .transition()
          .duration(150)
          .style('opacity', 1);
      })
      .on('mouseleave', () => {
        tooltip.transition().duration(150).style('opacity', 0);
      })
      .call(
        d3
          .drag<SVGGElement, TopicNode>()
          .on('start', (event: d3.D3DragEvent<SVGGElement, TopicNode, TopicNode>) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
          })
          .on('drag', (event: d3.D3DragEvent<SVGGElement, TopicNode, TopicNode>) => {
            event.subject.fx = event.x;
            event.subject.fy = event.y;
          })
          .on('end', (event: d3.D3DragEvent<SVGGElement, TopicNode, TopicNode>) => {
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

    const LABEL_THRESHOLD = 16;
    nodeGroup
      .filter((d) => d.size >= LABEL_THRESHOLD)
      .append('text')
      .text((d) => d.label)
      .attr('text-anchor', 'middle')
      .attr('dy', (d) => d.size + 14)
      .style('font-size', '11px')
      .style('fill', LABEL_COLOUR)
      .style('pointer-events', 'none');

    simulation.on('tick', () => {
      linkElements
        .attr('x1', (d) => (d.source as TopicNode).x ?? 0)
        .attr('y1', (d) => (d.source as TopicNode).y ?? 0)
        .attr('x2', (d) => (d.target as TopicNode).x ?? 0)
        .attr('y2', (d) => (d.target as TopicNode).y ?? 0);

      nodeGroup.attr('transform', (d) => `translate(${d.x ?? 0},${d.y ?? 0})`);
    });

    return () => {
      simulation.stop();
      tooltip.remove();
      svg.on('.zoom', null);
      svg.selectAll('*').remove();
    };
  }, [topics, coOccurrences, width, height, onTopicSelect]);

  return (
    <div ref={containerRef} className="h-full w-full min-h-0">
      <svg
        ref={svgRef}
        width={width}
        height={height}
        className="rounded-lg border border-slate-200 bg-slate-50"
        aria-label="Topic galaxy cluster visualisation"
      />
    </div>
  );
}
