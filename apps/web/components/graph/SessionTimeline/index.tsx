'use client';

import { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import type { Session } from '@/types/entities';
import { useContainerSize } from '@/lib/hooks/use-container-size';

const ARC_COLOURS: Record<string, string> = {
  default: '#94a3b8',
};

const COLOUR_PALETTE = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

interface SessionTimelineProps {
  sessions: Session[];
  onSessionSelect?: (session: Session) => void;
}

function arcColour(arcName: string | undefined, colourMap: Map<string, string>): string {
  if (!arcName) return ARC_COLOURS.default;
  if (colourMap.has(arcName)) return colourMap.get(arcName)!;
  const index = colourMap.size % COLOUR_PALETTE.length;
  colourMap.set(arcName, COLOUR_PALETTE[index]);
  return COLOUR_PALETTE[index];
}

export default function SessionTimeline({ sessions, onSessionSelect }: SessionTimelineProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [containerRef, { width, height }] = useContainerSize();

  useEffect(() => {
    const svgElement = svgRef.current;
    if (!svgElement || width === 0 || height === 0) return;

    const svg = d3.select(svgElement);
    svg.selectAll('*').remove();

    if (sessions.length === 0) return;

    const margin = { top: 30, right: 30, bottom: 40, left: 30 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const dates = sessions.map((s) => new Date(s.date));
    const extent = d3.extent(dates) as [Date, Date];

    const padding = 24 * 60 * 60 * 1000;
    const xScale = d3
      .scaleTime()
      .domain([new Date(extent[0].getTime() - padding), new Date(extent[1].getTime() + padding)])
      .range([0, innerWidth]);

    const container = svg
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const xAxis = d3.axisBottom(xScale).ticks(d3.timeWeek.every(1)).tickFormat(d3.timeFormat('%d %b') as (domainValue: Date | d3.NumberValue, index: number) => string);
    container
      .append('g')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(xAxis)
      .selectAll('text')
      .style('font-size', '10px')
      .attr('fill', '#64748b');

    container
      .append('line')
      .attr('x1', 0)
      .attr('x2', innerWidth)
      .attr('y1', innerHeight / 2)
      .attr('y2', innerHeight / 2)
      .attr('stroke', '#e2e8f0')
      .attr('stroke-width', 2);

    const colourMap = new Map<string, string>();

    const tooltip = d3
      .select('body')
      .append('div')
      .attr('class', 'session-timeline-tooltip')
      .style('position', 'absolute')
      .style('padding', '8px 12px')
      .style('background', '#1e293b')
      .style('color', '#f8fafc')
      .style('border-radius', '6px')
      .style('font-size', '12px')
      .style('pointer-events', 'none')
      .style('max-width', '250px')
      .style('opacity', 0);

    const markers = container
      .selectAll<SVGGElement, Session>('g.session-marker')
      .data(sessions)
      .join('g')
      .attr('class', 'session-marker')
      .style('cursor', onSessionSelect ? 'pointer' : 'default');

    markers
      .append('line')
      .attr('x1', (d) => xScale(new Date(d.date)))
      .attr('x2', (d) => xScale(new Date(d.date)))
      .attr('y1', innerHeight / 2 - 20)
      .attr('y2', innerHeight / 2 + 20)
      .attr('stroke', (d) => arcColour(d.theme_name, colourMap))
      .attr('stroke-width', 2)
      .attr('stroke-opacity', 0.7);

    markers
      .append('circle')
      .attr('cx', (d) => xScale(new Date(d.date)))
      .attr('cy', innerHeight / 2)
      .attr('r', 6)
      .attr('fill', (d) => arcColour(d.theme_name, colourMap))
      .attr('stroke', '#fff')
      .attr('stroke-width', 2);

    markers
      .on('mouseenter', (event, d) => {
        const summaryText = d.summary ? `<br/><em>${d.summary}</em>` : '';
        tooltip
          .html(`<strong>${d.title}</strong><br/>${d.date}${summaryText}`)
          .style('left', `${event.pageX + 12}px`)
          .style('top', `${event.pageY - 10}px`)
          .transition()
          .duration(150)
          .style('opacity', 1);
      })
      .on('mouseleave', () => {
        tooltip.transition().duration(150).style('opacity', 0);
      })
      .on('click', (_event, d) => {
        onSessionSelect?.(d);
      });

    return () => {
      tooltip.remove();
      svg.selectAll('*').remove();
    };
  }, [sessions, width, height, onSessionSelect]);

  return (
    <div ref={containerRef} className="h-full w-full min-h-0">
      <svg
        ref={svgRef}
        width={width}
        height={height}
        className="rounded-lg border border-slate-200 bg-slate-50"
        aria-label="Session timeline visualisation"
      />
    </div>
  );
}
