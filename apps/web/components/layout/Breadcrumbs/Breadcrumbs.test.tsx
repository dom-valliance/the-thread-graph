import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import Breadcrumbs from './index';

describe('Breadcrumbs', () => {
  it('renders all breadcrumb labels', () => {
    render(
      <Breadcrumbs items={[
        { label: 'Home', href: '/' },
        { label: 'Arcs', href: '/arcs' },
        { label: 'Current Arc' },
      ]} />,
    );

    expect(screen.getByText('Home')).toBeDefined();
    expect(screen.getByText('Arcs')).toBeDefined();
    expect(screen.getByText('Current Arc')).toBeDefined();
  });

  it('renders separators between items but not before the first', () => {
    render(
      <Breadcrumbs items={[
        { label: 'Home', href: '/' },
        { label: 'Arcs', href: '/arcs' },
        { label: 'Detail' },
      ]} />,
    );

    const separators = screen.getAllByText('/');
    expect(separators).toHaveLength(2);
  });

  it('renders the last item as a span with font-medium class', () => {
    render(
      <Breadcrumbs items={[
        { label: 'Home', href: '/' },
        { label: 'Last Item' },
      ]} />,
    );

    const lastItem = screen.getByText('Last Item');
    expect(lastItem.tagName).toBe('SPAN');
    expect(lastItem.className).toContain('font-medium');
  });

  it('renders middle items with href as links', () => {
    render(
      <Breadcrumbs items={[
        { label: 'Home', href: '/' },
        { label: 'Arcs', href: '/arcs' },
        { label: 'Detail' },
      ]} />,
    );

    const homeLink = screen.getByText('Home');
    expect(homeLink.tagName).toBe('A');

    const arcsLink = screen.getByText('Arcs');
    expect(arcsLink.tagName).toBe('A');
  });

  it('renders a single item without any separator', () => {
    render(
      <Breadcrumbs items={[{ label: 'Home' }]} />,
    );

    expect(screen.getByText('Home')).toBeDefined();
    expect(screen.queryAllByText('/')).toHaveLength(0);
  });
});
