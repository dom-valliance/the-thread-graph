import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import ArcExplorer from './index';
import type { Arc, ArcBridge } from '@/types/entities';

const MOCK_ARCS: Arc[] = [
  {
    name: 'Test Theme Alpha',
    bookmark_count: 3,
    session_count: 1,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
  {
    name: 'Test Theme Beta',
    bookmark_count: 5,
    session_count: 2,
    created_at: '2026-01-02T00:00:00Z',
    updated_at: '2026-01-02T00:00:00Z',
  },
];

const MOCK_BRIDGES: ArcBridge[] = [
  {
    source_arc_name: 'Test Theme Alpha',
    target_arc_name: 'Test Theme Beta',
    shared_topics: 2,
  },
];

describe('ArcExplorer', () => {
  it('renders an SVG element', () => {
    const { container } = render(<ArcExplorer arcs={MOCK_ARCS} bridges={MOCK_BRIDGES} />);
    const svg = container.querySelector('svg');
    expect(svg).toBeTruthy();
  });

  it('renders without crashing when given empty data', () => {
    const { container } = render(<ArcExplorer arcs={[]} bridges={[]} />);
    const svg = container.querySelector('svg');
    expect(svg).toBeTruthy();
  });

  it('sets the aria label for accessibility', () => {
    const { container } = render(<ArcExplorer arcs={MOCK_ARCS} bridges={MOCK_BRIDGES} />);
    const svg = container.querySelector('svg');
    expect(svg?.getAttribute('aria-label')).toBe('Arc explorer force-directed graph');
  });
});
