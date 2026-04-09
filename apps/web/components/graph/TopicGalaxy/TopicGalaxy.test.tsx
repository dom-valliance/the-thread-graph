import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import TopicGalaxy from './index';
import type { Topic } from '@/types/entities';

const MOCK_TOPICS: (Topic & { bookmark_count?: number })[] = [
  {
    id: 'topic-1',
    name: 'Machine Learning',
    description: 'ML techniques and applications',
    bookmark_count: 12,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
  {
    id: 'topic-2',
    name: 'Graph Theory',
    description: null,
    bookmark_count: 5,
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
