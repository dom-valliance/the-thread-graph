import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import SessionTimeline from './index';
import type { Session } from '@/types/entities';

const MOCK_SESSIONS: Session[] = [
  {
    id: 'session-1',
    title: 'Kickoff Meeting',
    date: '2026-01-10',
    summary: 'Initial planning discussion',
    created_at: '2026-01-10T00:00:00Z',
    updated_at: '2026-01-10T00:00:00Z',
  },
  {
    id: 'session-2',
    title: 'Deep Dive: Architecture',
    date: '2026-01-17',
    summary: null,
    created_at: '2026-01-17T00:00:00Z',
    updated_at: '2026-01-17T00:00:00Z',
  },
];

describe('SessionTimeline', () => {
  it('renders an SVG element', () => {
    const { container } = render(<SessionTimeline sessions={MOCK_SESSIONS} />);
    const svg = container.querySelector('svg');
    expect(svg).toBeTruthy();
  });

  it('renders without crashing when given empty data', () => {
    const { container } = render(<SessionTimeline sessions={[]} />);
    const svg = container.querySelector('svg');
    expect(svg).toBeTruthy();
  });

  it('sets the aria label for accessibility', () => {
    const { container } = render(<SessionTimeline sessions={MOCK_SESSIONS} />);
    const svg = container.querySelector('svg');
    expect(svg?.getAttribute('aria-label')).toBe('Session timeline visualisation');
  });
});
