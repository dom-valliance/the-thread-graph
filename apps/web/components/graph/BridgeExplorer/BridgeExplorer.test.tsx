import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import BridgeExplorer from './index';

describe('BridgeExplorer', () => {
  it('renders an SVG element', () => {
    const { container } = render(
      <BridgeExplorer bridges={[]} gaps={[]} />,
    );
    const svg = container.querySelector('svg');
    expect(svg).toBeTruthy();
  });

  it('renders without crashing with empty data', () => {
    const { container } = render(
      <BridgeExplorer bridges={[]} gaps={[]} />,
    );
    expect(container).toBeTruthy();
  });

  it('has accessible aria-label', () => {
    const { container } = render(
      <BridgeExplorer bridges={[]} gaps={[]} />,
    );
    const svg = container.querySelector('svg');
    expect(svg?.getAttribute('aria-label')).toBe(
      'Cross-arc bridge explorer',
    );
  });
});
