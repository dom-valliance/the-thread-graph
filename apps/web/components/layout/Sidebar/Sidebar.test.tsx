import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';

vi.mock('next/navigation', () => ({ usePathname: vi.fn() }));

import { usePathname } from 'next/navigation';
import Sidebar from './index';

const mockUsePathname = usePathname as ReturnType<typeof vi.fn>;

describe('Sidebar', () => {
  it('renders all 12 navigation items', () => {
    mockUsePathname.mockReturnValue('/');
    render(<Sidebar />);

    const expectedLabels = [
      'Dashboard', 'Schedule', 'Arcs', 'Bridges', 'Objections',
      'Topics', 'Sessions', 'Evidence Vault', 'Live Fire', 'Forge',
      'Bookmarks', 'Fast Track',
    ];

    for (const label of expectedLabels) {
      expect(screen.getByText(label)).toBeDefined();
    }

    const links = screen.getAllByRole('link');
    expect(links).toHaveLength(12);
  });

  it('renders the "Valliance Graph" branding text', () => {
    mockUsePathname.mockReturnValue('/');
    render(<Sidebar />);

    expect(screen.getByText('Valliance Graph')).toBeDefined();
  });

  it('highlights Dashboard link when pathname is "/"', () => {
    mockUsePathname.mockReturnValue('/');
    render(<Sidebar />);

    const dashboardLink = screen.getByText('Dashboard');
    expect(dashboardLink.className).toContain('bg-slate-700');
  });

  it('highlights Arcs link when pathname is "/arcs"', () => {
    mockUsePathname.mockReturnValue('/arcs');
    render(<Sidebar />);

    const arcsLink = screen.getByText('Arcs');
    expect(arcsLink.className).toContain('bg-slate-700');
  });

  it('highlights Arcs link for sub-path "/arcs/some-arc"', () => {
    mockUsePathname.mockReturnValue('/arcs/some-arc');
    render(<Sidebar />);

    const arcsLink = screen.getByText('Arcs');
    expect(arcsLink.className).toContain('bg-slate-700');
  });

  it('does not highlight Dashboard for non-root paths', () => {
    mockUsePathname.mockReturnValue('/arcs');
    render(<Sidebar />);

    const dashboardLink = screen.getByText('Dashboard');
    expect(dashboardLink.className).not.toContain('bg-slate-700');
  });
});
