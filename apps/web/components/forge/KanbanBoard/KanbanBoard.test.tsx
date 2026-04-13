import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import KanbanBoard from './index';
import type { ForgeAssignment } from '@/types/entities';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

function wrapper({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}

function makeAssignment(
  overrides: Partial<ForgeAssignment>,
): ForgeAssignment {
  return {
    id: 'a-1',
    artefact_type: 'blog_post',
    status: 'assigned',
    deadline: '2026-12-31',
    storyboard_notes: null,
    published_url: null,
    editor_notes: null,
    assigned_to_name: 'Dom',
    assigned_to_email: null,
    editor_name: null,
    editor_email: null,
    session_id: null,
    arc_name: null,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    ...overrides,
  };
}

describe('KanbanBoard', () => {
  it('renders all 5 column headers', () => {
    render(<KanbanBoard assignments={[]} />, { wrapper });

    expect(screen.getByText('Assigned')).toBeTruthy();
    expect(screen.getByText('Storyboarded')).toBeTruthy();
    expect(screen.getByText('In Production')).toBeTruthy();
    expect(screen.getByText('Editor Review')).toBeTruthy();
    expect(screen.getByText('Published')).toBeTruthy();
  });

  it('groups assignments into correct columns', () => {
    const assignments = [
      makeAssignment({ id: 'a-1', status: 'assigned' }),
      makeAssignment({ id: 'a-2', status: 'assigned' }),
      makeAssignment({ id: 'a-3', status: 'in_production' }),
    ];

    render(<KanbanBoard assignments={assignments} />, { wrapper });

    expect(screen.getByText('(2)')).toBeTruthy();
    expect(screen.getByText('(1)')).toBeTruthy();
  });

  it('shows "No items" for empty columns', () => {
    render(<KanbanBoard assignments={[]} />, { wrapper });

    const emptyLabels = screen.getAllByText('No items');
    expect(emptyLabels).toHaveLength(5);
  });

  it('renders assignment artefact type text', () => {
    const assignments = [
      makeAssignment({ artefact_type: 'blog_post' }),
    ];

    render(<KanbanBoard assignments={assignments} />, { wrapper });

    expect(screen.getByText('blog post')).toBeTruthy();
  });

  it('shows overdue styling when deadline is past and status is not published', () => {
    const assignments = [
      makeAssignment({
        id: 'overdue-1',
        status: 'assigned',
        deadline: '2020-01-01',
      }),
    ];

    const { container } = render(
      <KanbanBoard assignments={assignments} />,
      { wrapper },
    );

    const card = container.querySelector('.border-red-300');
    expect(card).toBeTruthy();
  });
});
