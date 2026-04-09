import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import ArgumentMap from './index';
import type { Argument } from '@/types/entities';

const MOCK_ARGUMENTS: Argument[] = [
  {
    id: 'arg-1',
    text: 'Evidence strongly supports the claim',
    type: 'Supporting',
    strength: 'Strong',
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
  {
    id: 'arg-2',
    text: 'Counter-evidence suggests otherwise',
    type: 'Challenging',
    strength: 'Moderate',
    created_at: '2026-01-02T00:00:00Z',
    updated_at: '2026-01-02T00:00:00Z',
  },
];

describe('ArgumentMap', () => {
  it('renders an SVG element', () => {
    const { container } = render(
      <ArgumentMap
        positionId="pos-1"
        positionText="Climate change requires immediate action"
        arguments={MOCK_ARGUMENTS}
      />,
    );
    const svg = container.querySelector('svg');
    expect(svg).toBeTruthy();
  });

  it('renders without crashing when given empty arguments', () => {
    const { container } = render(
      <ArgumentMap
        positionId="pos-1"
        positionText="An empty position"
        arguments={[]}
      />,
    );
    const svg = container.querySelector('svg');
    expect(svg).toBeTruthy();
  });

  it('sets the aria label for accessibility', () => {
    const { container } = render(
      <ArgumentMap
        positionId="pos-1"
        positionText="Test position"
        arguments={MOCK_ARGUMENTS}
      />,
    );
    const svg = container.querySelector('svg');
    expect(svg?.getAttribute('aria-label')).toBe('Argument map visualisation');
  });
});
