import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import MetricsTable from './index';
import type { LiveFirePositionMetric } from '@/types/entities';

function makeMetric(
  overrides: Partial<LiveFirePositionMetric>,
): LiveFirePositionMetric {
  return {
    position_id: 'p-1',
    position_text: 'Default position',
    total_uses: 10,
    successes: 7,
    failures: 3,
    success_rate: 0.7,
    last_used: '2026-03-15',
    never_used: false,
    ...overrides,
  };
}

describe('MetricsTable', () => {
  it('renders table headers', () => {
    render(<MetricsTable metrics={[]} />);

    expect(screen.getByText('Position')).toBeTruthy();
    expect(screen.getByText('Uses')).toBeTruthy();
    expect(screen.getByText('Successes')).toBeTruthy();
    expect(screen.getByText('Failures')).toBeTruthy();
    expect(screen.getByText('Success Rate')).toBeTruthy();
    expect(screen.getByText('Last Used')).toBeTruthy();
  });

  it('renders position text for each metric', () => {
    const metrics = [
      makeMetric({ position_id: 'p-1', position_text: 'AI will replace jobs' }),
      makeMetric({ position_id: 'p-2', position_text: 'Remote work is better' }),
    ];

    render(<MetricsTable metrics={metrics} />);

    expect(screen.getByText('AI will replace jobs')).toBeTruthy();
    expect(screen.getByText('Remote work is better')).toBeTruthy();
  });

  it('formats success rate as percentage', () => {
    const metrics = [makeMetric({ success_rate: 0.75 })];

    render(<MetricsTable metrics={metrics} />);

    expect(screen.getByText('75%')).toBeTruthy();
  });

  it('shows dash when success_rate is null', () => {
    const metrics = [makeMetric({ success_rate: null })];

    render(<MetricsTable metrics={metrics} />);

    expect(screen.getByText('\u2014')).toBeTruthy();
  });

  it('shows "Never" when last_used is null', () => {
    const metrics = [makeMetric({ last_used: null })];

    render(<MetricsTable metrics={metrics} />);

    expect(screen.getByText('Never')).toBeTruthy();
  });

  it('applies bg-red-50 class for high failure rate', () => {
    const metrics = [makeMetric({ position_id: 'fail-1', success_rate: 0.3 })];

    const { container } = render(<MetricsTable metrics={metrics} />);

    const row = container.querySelector('tr.bg-red-50');
    expect(row).toBeTruthy();
  });

  it('applies bg-amber-50 class for never-used positions', () => {
    const metrics = [
      makeMetric({
        position_id: 'unused-1',
        never_used: true,
        success_rate: null,
        total_uses: 0,
        successes: 0,
        failures: 0,
      }),
    ];

    const { container } = render(<MetricsTable metrics={metrics} />);

    const row = container.querySelector('tr.bg-amber-50');
    expect(row).toBeTruthy();
  });
});
