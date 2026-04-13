import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import TopicGalaxy from './index';
import type { Topic } from '@/types/entities';

const MOCK_TOPICS: (Topic & { bookmark_count?: number })[] = [
  {
    name: 'Machine Learning',
    bookmark_count: 12,
    primary_arc: null,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
  {
    name: 'Graph Theory',
    bookmark_count: 5,
    primary_arc: null,
    created_at: '2026-01-02T00:00:00Z',
    updated_at: '2026-01-02T00:00:00Z',
  },
];

describe('TopicGalaxy', () => {
  it('renders an SVG element', () => {
    const { container } = render(<TopicGalaxy topics={MOCK_TOPICS} />);
    const svg = container.querySelector('svg');
    expect(svg).toBeTruthy();
  });

  it('renders without crashing when given empty data', () => {
    const { container } = render(<TopicGalaxy topics={[]} />);
    const svg = container.querySelector('svg');
    expect(svg).toBeTruthy();
  });

  it('sets the aria label for accessibility', () => {
    const { container } = render(<TopicGalaxy topics={MOCK_TOPICS} />);
    const svg = container.querySelector('svg');
    expect(svg?.getAttribute('aria-label')).toBe('Topic galaxy cluster visualisation');
  });
});
