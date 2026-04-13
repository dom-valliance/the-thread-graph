import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import EvidenceTrail from './index';

vi.mock('@/lib/hooks/use-evidence-trail', () => ({
  useEvidenceTrail: vi.fn(() => ({
    data: {
      position_text: 'Test position',
      evidence: [],
      unsourced_count: 0,
      bridge_bookmark_count: 0,
    },
    isLoading: false,
    error: null,
  })),
  useCreateEvidence: vi.fn(() => ({ mutate: vi.fn(), isPending: false })),
}));

vi.mock('@/lib/hooks/use-container-size', () => ({
  useContainerSize: vi.fn(() => [{ current: null }, { width: 800, height: 480 }]),
}));

describe('EvidenceTrail', () => {
  it('renders an SVG element', () => {
    const { container } = render(<EvidenceTrail positionId="p-1" />);
    const svg = container.querySelector('svg');
    expect(svg).toBeTruthy();
  });

  it('renders without crashing with empty data', () => {
    const { container } = render(<EvidenceTrail positionId="p-1" />);
    expect(container).toBeTruthy();
  });

  it('has accessible aria-label', () => {
    const { container } = render(<EvidenceTrail positionId="p-1" />);
    const svg = container.querySelector('svg');
    expect(svg?.getAttribute('aria-label')).toBe(
      'Evidence trail visualisation',
    );
  });
});
