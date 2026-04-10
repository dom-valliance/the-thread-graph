import type * as d3 from 'd3';

export interface GraphNode extends d3.SimulationNodeDatum {
  id: string;
  label: string;
  size: number;
  colour: string;
  data: unknown;
  type?: 'arc' | 'bookmark' | 'more' | 'position' | 'evidence';
}

export interface GraphLink extends d3.SimulationLinkDatum<GraphNode> {
  label: string | null;
  strength: number;
}
