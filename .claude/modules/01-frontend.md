# Module: Frontend (apps/web)

Next.js 14 App Router application providing the visualisation layer for the Valliance Graph.

---

## Technology

- Next.js 14 (App Router, server components by default)
- React 18
- TypeScript 5.x (strict mode)
- D3.js v7 for graph visualisation
- TanStack Query v5 for client-side data fetching
- Tailwind CSS v3
- pnpm as package manager

## Responsibilities

- Render four primary views: Arc Explorer, Topic Galaxy, Session Timeline, Argument Map.
- Fetch all data from FastAPI middleware via typed API client. No direct Neo4j access.
- Provide search and filtering across all views.
- Handle Azure AD authentication (MSAL.js) and pass JWT to API layer.

## Directory Structure

```
apps/web/
├── app/
│   ├── layout.tsx              # Root layout with auth provider, query provider
│   ├── page.tsx                # Dashboard / landing (redirect to arc explorer)
│   ├── arcs/
│   │   ├── page.tsx            # Arc Explorer view
│   │   └── [arcId]/
│   │       └── page.tsx        # Arc detail: positions, evidence chains
│   ├── topics/
│   │   └── page.tsx            # Topic Galaxy view
│   ├── sessions/
│   │   └── page.tsx            # Session Timeline view
│   ├── positions/
│   │   └── [positionId]/
│   │       └── page.tsx        # Argument Map for a specific position
│   └── api/                    # Next.js API routes (BFF proxy if needed)
├── components/
│   ├── ui/                     # Buttons, cards, modals, search bar
│   ├── graph/
│   │   ├── ArcExplorer/        # D3 force-directed arc network
│   │   ├── TopicGalaxy/        # D3 scatter/cluster of topics
│   │   ├── SessionTimeline/    # D3 horizontal timeline
│   │   └── ArgumentMap/        # D3 for/against layout
│   ├── layout/                 # Navigation, sidebar, breadcrumbs
│   └── filters/                # Filter controls (arc, person, topic, date range)
├── lib/
│   ├── api-client.ts           # Typed HTTP client wrapping fetch to FastAPI
│   ├── auth.ts                 # MSAL.js Azure AD integration
│   ├── hooks/                  # Custom React hooks (useGraph, useFilters, etc.)
│   └── utils.ts                # Formatting, date helpers
├── types/
│   ├── api.ts                  # Response types mirroring API envelope
│   ├── graph.ts                # D3 node/link types
│   └── entities.ts             # Domain entities (Bookmark, Position, Arc, etc.)
├── public/                     # Static assets
├── tailwind.config.ts
├── tsconfig.json
├── vitest.config.ts
└── playwright.config.ts
```

## Key Design Decisions

### D3 in React

Every D3 visualisation is a React component that follows this pattern:

1. Component receives data as props (typed).
2. `useRef` creates a container ref for the SVG.
3. `useEffect` initialises the D3 simulation/rendering on mount, updates on data change.
4. Cleanup function in `useEffect` stops simulations and removes event listeners.
5. React handles the outer shell (loading states, error boundaries, filters). D3 handles the SVG internals.

No `dangerouslySetInnerHTML`. No jQuery. D3 selections operate only within the ref'd container.

### Server vs Client Components

- Page-level components are server components. They fetch initial data server-side.
- Graph visualisation components are client components (`'use client'`).
- Filters and interactive controls are client components.
- Layout and navigation are server components.

### API Client

Single typed client in `lib/api-client.ts`. Every endpoint returns typed responses matching the API envelope. Error handling is centralised: 401 triggers re-auth, 4xx/5xx throw typed errors caught by React Query error boundaries.

```typescript
// Pattern
export async function getArcs(): Promise<ApiResponse<Arc[]>> {
  return apiGet<Arc[]>('/arcs');
}

export async function getPositionArguments(positionId: string): Promise<ApiResponse<ArgumentMap>> {
  return apiGet<ArgumentMap>(`/positions/${positionId}/arguments`);
}
```

## Views Specification

### Arc Explorer

- Force-directed graph. Each arc is a large node. CrossArcBridges are edges with labels.
- Node size proportional to number of locked positions.
- Edge thickness proportional to bridge strength (Core > Supporting > Tangential).
- Click arc node to navigate to arc detail page.
- Filter: toggle P1 (People First) vs V1 (Value First) positions.
- Colour: by proposition mapping.

### Topic Galaxy

- Scatter plot with force simulation. Each topic is a circle.
- Size: co-occurrence frequency (how many bookmarks share this topic with others).
- Proximity: topics that co-occur cluster together.
- Colour: by theme.
- Click topic to show panel with associated bookmarks and positions.
- Search bar filters visible topics.

### Session Timeline

- Horizontal timeline. X-axis is date.
- Each session is a vertical column with argument nodes stacked.
- Arguments colour-coded: green (supports), red (challenges), grey (neutral).
- Click argument to see source session, speaker, and linked position.
- Filter: by arc, by person, show/hide resolved action items.

### Argument Map

- For a given position: two-zone layout.
- Left zone (green): supporting arguments and evidence.
- Right zone (red): challenging arguments and steelman arguments.
- Centre: the position statement.
- Node size proportional to strength assessment.
- ObjectionResponsePairs shown as linked pairs between zones.
- Click node to see source (session, person, bookmark).

## Testing

- **Unit tests**: Vitest + React Testing Library. Test component rendering, filter logic, API client.
- **D3 tests**: Snapshot tests for SVG output given fixed data. Verify node counts, relationship rendering.
- **Integration**: MSW to mock API responses. Test full page render with mocked data.
- **E2E**: Playwright. Navigate between views, apply filters, verify data loads.
- **Visual regression**: Playwright screenshots of each view with known test data.

Test files co-located: `ArcExplorer/index.tsx` and `ArcExplorer/ArcExplorer.test.tsx`.

## Dependencies (expected)

```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "d3": "^7.0.0",
    "@tanstack/react-query": "^5.0.0",
    "@azure/msal-browser": "^3.0.0",
    "@azure/msal-react": "^2.0.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "vitest": "^1.0.0",
    "@testing-library/react": "^14.0.0",
    "msw": "^2.0.0",
    "@playwright/test": "^1.40.0",
    "tailwindcss": "^3.0.0",
    "eslint": "^8.0.0",
    "prettier": "^3.0.0"
  }
}
```

## Build and Dev

```bash
# Development
pnpm --filter web dev          # Next.js dev server on :3000

# Build
pnpm --filter web build        # Production build

# Test
pnpm --filter web test         # Vitest unit tests
pnpm --filter web test:e2e     # Playwright E2E

# Lint
pnpm --filter web lint         # ESLint
pnpm --filter web typecheck    # tsc --noEmit
```
