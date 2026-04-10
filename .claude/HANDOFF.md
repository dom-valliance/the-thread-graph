# Handoff: Thread Operational Features

**Date:** 2026-04-10
**Purpose:** Build the operational layer that turns the Valliance Graph from a knowledge visualisation tool into the system that runs The Thread curriculum.

---

## Context

Read these before starting:

- `.claude/CLAUDE.md` — project conventions, stack, gotchas
- `.claude/modules/Valliance-Thread_Curriculum_v3.md` — the full curriculum spec (this is the requirements document)
- `.claude/notes/` — accumulated learnings from previous sessions

The Thread is a continuous 12-week learning cycle. Six two-week arcs run sequentially. Each arc has a Week 1 (Problem + Landscape) and Week 2 (Position + Pitch). Sessions run every Friday afternoon in a 2.5-hour block: Thread (45 min), Break (15 min), Workshop (60 min), Forge (30 min). The app must support planning, facilitating, capturing, locking, and propagating the outputs of these sessions.

---

## Current State

The app is a three-tier monorepo: Next.js frontend (`apps/web`), FastAPI middleware (`apps/api`), Neo4j graph database, and an NLP pipeline (`apps/nlp`).

### What exists and works

- **10 frontend pages**: arcs, topics, sessions, bookmarks, positions, objections, bridges, plus detail pages
- **6 D3 graph visualisations**: ArcExplorer, TopicGalaxy, SessionTimeline, ArgumentMap, EvidenceTrail, BridgeExplorer
- **14 API routers** with full CRUD, cursor-based pagination, cross-entity search
- **15 Neo4j repositories** with 16 node types and 30+ relationship types
- **NLP pipeline** with Claude-powered extraction: arguments, action items, evidence, entities
- **Notion sync** for bookmarks and sessions with LLM theme classification
- **ObjectionForge** component for managing objection-response pairs

### What is broken (carry forward from previous session)

1. **Bookmarks page groups by topic, not theme.** Most bookmarks have no topics. Fix: change `apps/web/app/bookmarks/page.tsx` to group by `theme_name` instead of `topic_names`.
2. **Notion relation properties not resolved.** "Valliance Topics" and "Valliance Themes" are relation properties returning page IDs, not names. Fix: either add rollup columns in Notion or implement batch page title resolver in `apps/nlp/sync/notion_client.py`.
3. **Bookmarks capped at 100.** Frontend fetches `?limit=100` but does not paginate. API supports cursor-based pagination already.
4. **Session dates still null after full re-sync.** The `date` field fix was applied in the transformer but a full re-sync (`python -m sync.runner --db sessions --full`) has not remedied it.
5. **Diagnostic logging in transformer.** `BookmarkTransformer._logged_types` should be removed or gated behind debug flag.

---

## What to Build

Five workstreams, ordered by dependency. Each workstream is described with: data model, API endpoints, frontend, and acceptance criteria.

---

### Workstream 1: Cycle Engine

**Goal:** The app knows where you are in the 12-week cycle and what happens next.

#### Data Model

New nodes:

```
Cycle {
  id: string (e.g. "cycle-1")
  number: integer
  start_date: date
  end_date: date
  status: string (active | completed | upcoming)
  created_at: datetime
  updated_at: datetime
}

ScheduledSession {
  id: string (e.g. "ss-c1-w1")
  cycle_number: integer
  week_number: integer (1-12)
  arc_number: integer (1-6)
  week_type: string (problem_landscape | position_pitch)
  date: date
  status: string (upcoming | in_progress | completed)
  created_at: datetime
  updated_at: datetime
}
```

New relationships:

```
(ScheduledSession)-[:PART_OF]->(Cycle)
(ScheduledSession)-[:COVERS]->(Arc)
(Person)-[:LEADS]->(ScheduledSession)
(Person)-[:SHADOWS]->(ScheduledSession)
```

#### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/cycles` | List all cycles |
| GET | `/api/v1/cycles/current` | Current cycle with active arc, week type, lead/shadow, days until next session |
| POST | `/api/v1/cycles` | Create a new cycle (generates 12 ScheduledSession nodes, links to arcs) |
| GET | `/api/v1/cycles/{id}/schedule` | Full 12-week schedule with lead/shadow assignments |
| PUT | `/api/v1/cycles/{id}/schedule/{week}` | Update lead/shadow assignment for a specific week |
| GET | `/api/v1/scheduled-sessions/{id}` | Session detail: agenda, assignments, prep status |

#### Frontend

- **Dashboard page** (`/`): Replace the current redirect-to-arcs. Show: current arc name and number, week type badge (Problem+Landscape or Position+Pitch), lead and shadow names, days until next session, prep checklist, recent Live Fire entries, any pending Flashes.
- **Schedule page** (`/schedule`): 12-week grid showing all sessions with lead/shadow, arc, week type. Current week highlighted. Click to edit assignments.
- **Sidebar update**: Add Dashboard and Schedule links. Highlight current section.

#### Acceptance Criteria

- Creating a cycle auto-generates 12 ScheduledSession nodes linked to the correct arcs (Arc 1 for weeks 1-2, Arc 2 for weeks 3-4, etc.)
- `GET /cycles/current` returns the correct session based on today's date
- Dashboard shows the current state without any manual intervention after cycle creation
- Lead/shadow assignments can be updated per week

---

### Workstream 2: Session Capture & Lock Workflow

**Goal:** Sessions produce structured outputs that get locked before anyone leaves the room.

#### Data Model

New node:

```
ProblemLandscapeBrief {
  id: string
  problem_statement: string (2-3 sentences)
  landscape_criteria: string[] (evaluation dimensions)
  steelman_summary: string
  status: string (draft | locked)
  locked_date: datetime | null
  locked_by: string | null (person email)
  created_at: datetime
  updated_at: datetime
}
```

Extended `Position` node (add these fields to the existing node):

```
Position (extended) {
  + version: integer (default 1)
  + status: string (draft | locked | under_revision)
  + locked_date: datetime | null
  + locked_by: string | null
  + anti_position_text: string | null
  + cross_arc_bridge_text: string | null
  + p1_v1_mapping: string | null (P1 | V1 | both)
  + steelman_addressed: string | null (reference to SteelmanArgument id)
}
```

New relationships:

```
(ProblemLandscapeBrief)-[:PRODUCED_IN]->(ScheduledSession)
(ProblemLandscapeBrief)-[:FOR_ARC]->(Arc)
(Position)-[:PRODUCED_IN]->(ScheduledSession)
(Position)-[:SUPERSEDES]->(Position)  // version chain
```

#### Landscape Grid (Week 1 Workshop output)

```
LandscapeGrid {
  id: string
  created_at: datetime
  updated_at: datetime
}

LandscapeGridEntry {
  id: string
  player_name: string
  criterion: string
  rating: string (strong | weak | mixed)
  notes: string
}

(LandscapeGrid)-[:PART_OF]->(ProblemLandscapeBrief)
(LandscapeGridEntry)-[:ENTRY_IN]->(LandscapeGrid)
(LandscapeGridEntry)-[:EVALUATES]->(Player)
```

#### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/briefs` | Create a Problem-Landscape Brief (draft) |
| GET | `/api/v1/briefs/{id}` | Get brief with landscape grid |
| PUT | `/api/v1/briefs/{id}` | Update brief (only when status = draft) |
| POST | `/api/v1/briefs/{id}/lock` | Lock the brief. Sets status, locked_date, locked_by. Rejects if already locked. |
| POST | `/api/v1/positions` | Create a position (draft) with all required fields |
| PUT | `/api/v1/positions/{id}` | Update position (only when status = draft or under_revision) |
| POST | `/api/v1/positions/{id}/lock` | Lock the position. Validates required fields present (anti_position_text, cross_arc_bridge_text, p1_v1_mapping). Sets status, locked_date, locked_by. |
| POST | `/api/v1/positions/{id}/revise` | Move a locked position to under_revision. Creates a new version node linked via SUPERSEDES. Only permitted when triggered by Live Fire or Flash. |
| GET | `/api/v1/positions/{id}/versions` | Version history for a position |

#### Frontend

- **Session workspace page** (`/sessions/{id}/workspace`): Live editing surface for the current session's output. Week 1: Problem-Landscape Brief editor with structured fields (problem statement, landscape criteria, steelman summary) plus landscape grid builder. Week 2: Position editor with required fields (position text, anti-position, cross-arc bridge, P1/V1 mapping). Lock button at the bottom, disabled until all required fields are populated. After lock, view switches to read-only with a "Locked" badge.
- **Position detail enhancement**: Show version history, locked status badge, anti-position, cross-arc bridge, and P1/V1 mapping alongside the existing argument map.

#### Acceptance Criteria

- A brief or position in `draft` status can be edited freely
- Locking validates all required fields are present; returns 422 with specific missing fields if not
- A locked brief or position cannot be edited via PUT (returns 409 Conflict)
- `POST /positions/{id}/revise` creates a new version node, copies fields, sets status to draft, links via SUPERSEDES
- Version history shows the full chain with locked dates

---

### Workstream 3: Evidence Vault & Live Fire

**Goal:** Field evidence flows back into positions. The primary success metric is tracked.

#### Data Model

New nodes:

```
LiveFireEntry {
  id: string
  outcome: string (used_successfully | used_and_failed | not_used)
  context: string (anonymised client/prospect note)
  date: date
  created_at: datetime
  updated_at: datetime
}

Flash {
  id: string
  title: string
  description: string
  status: string (pending | reviewed_holds | minor_update | major_rewrite_scheduled)
  reviewed_date: datetime | null
  created_at: datetime
  updated_at: datetime
}
```

Extended `Evidence` node:

```
Evidence (extended) {
  + proposition_mapping: string | null (P1 | V1 | both)
  + vault_type: string | null (live_fire | problem_week_anecdote | market_data | client_story | flash)
}
```

New relationships:

```
(LiveFireEntry)-[:REFERENCES]->(Position)
(LiveFireEntry)-[:REFERENCES]->(ObjectionResponsePair)
(LiveFireEntry)-[:REPORTED_BY]->(Person)
(LiveFireEntry)-[:REPORTED_IN]->(ScheduledSession)
(Flash)-[:AFFECTS]->(Position)
(Flash)-[:RAISED_BY]->(Person)
(Flash)-[:RESOLVED_IN]->(ScheduledSession)
```

#### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/live-fire` | Submit a Live Fire entry |
| GET | `/api/v1/live-fire` | List entries with filters (position_id, outcome, date range) |
| GET | `/api/v1/live-fire/metrics` | Aggregated: per position, times used, times failed, success rate, never-used positions |
| POST | `/api/v1/flashes` | Submit a Flash (any team member) |
| GET | `/api/v1/flashes` | List flashes with filters (status, position_id) |
| GET | `/api/v1/flashes/pending` | Pending flashes for next Live Fire slot |
| PUT | `/api/v1/flashes/{id}` | Update Flash status after review |
| GET | `/api/v1/evidence-vault` | Evidence entries with filters (arc, proposition, vault_type, date range) |

#### Frontend

- **Evidence Vault page** (`/evidence-vault`): Filterable list of all evidence entries tagged by arc, proposition (P1/V1), and type. Submission form for new entries. Search.
- **Live Fire dashboard** (`/live-fire`): Two views. (1) Submission form: select position, select outcome, add context. (2) Metrics view: table of all locked positions with columns for times used, times failed, success rate, last used date. Highlight positions with >50% failure rate in red. Highlight positions never used in amber.
- **Flash panel**: Accessible from the dashboard. Submit a Flash (select affected position, describe the event). Pending Flashes shown on dashboard with a badge count.
- **Arc Pulse view** (embedded in dashboard at Weeks 6 and 12): All six positions with health indicator derived from Live Fire metrics and Evidence Vault tags. Green = no evidence of drift. Amber = evidence accumulating. Red = under strain (high failure rate or Flash pending).

#### Acceptance Criteria

- Live Fire entries link to specific positions and optionally to specific objection-response pairs
- Metrics endpoint returns correct aggregation (used vs. failed ratio per position)
- Positions with zero Live Fire entries are flagged as "never used"
- Flash submission notifies the next session's lead (stretch: Slack webhook)
- Only one Flash can be active per session (enforced by API)

---

### Workstream 4: Forge & Content Pipeline

**Goal:** Track the 12 external artefacts per cycle from assignment through publication.

#### Data Model

New nodes:

```
ForgeAssignment {
  id: string
  artefact_type: string (briefing | comparison_framework | market_map | viewpoint_article | credentials_section | pitch_script | one_pager | objection_cards)
  status: string (assigned | storyboarded | in_production | editor_review | published | overdue)
  deadline: date (Thursday before the next session)
  storyboard_notes: string | null
  published_url: string | null
  editor_notes: string | null
  created_at: datetime
  updated_at: datetime
}
```

New relationships:

```
(ForgeAssignment)-[:ASSIGNED_TO]->(Person)
(ForgeAssignment)-[:EDITED_BY]->(Person)  // previous week's lead
(ForgeAssignment)-[:FOR_SESSION]->(ScheduledSession)
(ForgeAssignment)-[:FOR_ARC]->(Arc)
(ForgeAssignment)-[:DERIVED_FROM]->(Position)
(ForgeAssignment)-[:DERIVED_FROM]->(ProblemLandscapeBrief)
```

#### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/forge` | Create a Forge assignment |
| GET | `/api/v1/forge` | List assignments with filters (status, arc, person, cycle) |
| GET | `/api/v1/forge/{id}` | Assignment detail |
| PUT | `/api/v1/forge/{id}` | Update assignment (status, storyboard notes, published URL) |
| GET | `/api/v1/forge/tracker` | Cycle-level: artefacts produced vs. target (12), by type breakdown |

#### Frontend

- **Forge board** (`/forge`): Kanban-style board with columns: Assigned, Storyboarded, In Production, Editor Review, Published. Cards show assignee, artefact type, arc, deadline. Overdue items highlighted.
- **Forge tracker** (embedded in dashboard): Progress bar showing artefacts produced this cycle vs. 12 target.

#### Acceptance Criteria

- Creating a Forge assignment auto-sets the editor to the previous week's lead (lookup from rota)
- Status transitions are validated (cannot skip from assigned to published)
- Overdue detection: any assignment past its deadline that is not in published status
- Tracker returns correct count per cycle

---

### Workstream 5: Prep & Onboarding

**Goal:** Reduce preparation burden and get new hires up to speed.

#### Data Model

New nodes:

```
WorkshopAssignment {
  id: string
  player_or_approach: string
  analysis_notes: string | null
  status: string (assigned | prepared | presented)
  created_at: datetime
  updated_at: datetime
}

ReadingAssignment {
  id: string
  status: string (assigned | read)
  created_at: datetime
  updated_at: datetime
}
```

New relationships:

```
(WorkshopAssignment)-[:ASSIGNED_TO]->(Person)
(WorkshopAssignment)-[:FOR_SESSION]->(ScheduledSession)
(WorkshopAssignment)-[:RESEARCHES]->(Player)
(ReadingAssignment)-[:ASSIGNED_TO]->(Person)
(ReadingAssignment)-[:FOR_SESSION]->(ScheduledSession)
(ReadingAssignment)-[:COVERS]->(Bookmark)
```

#### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/scheduled-sessions/{id}/workshop-assignments` | Assign players to people for Week 1 Workshops |
| GET | `/api/v1/scheduled-sessions/{id}/workshop-assignments` | List assignments for a session |
| PUT | `/api/v1/workshop-assignments/{id}` | Update status or notes |
| POST | `/api/v1/scheduled-sessions/{id}/reading-list` | Assign reading (bookmarks) to people |
| GET | `/api/v1/scheduled-sessions/{id}/reading-list` | Reading list with per-person read/unread status |
| PUT | `/api/v1/reading-assignments/{id}` | Mark as read |
| GET | `/api/v1/scheduled-sessions/{id}/prep-brief` | Auto-generated prep brief: arc question, relevant fresh bookmarks, previous cycle's locked position, Evidence Vault entries for this arc |

#### Frontend

- **Session prep page** (`/sessions/{id}/prep`): Shows the prep brief, reading list with checkboxes, Workshop assignments (Week 1 only). Lead can assign readings and Workshop players from this page.
- **Fast-Track page** (`/fast-track`): After Cycle 1 completes, shows the Essential Thread digest. Six position summaries, six anti-positions, unified thesis, key disagreements. Generated from locked positions and session summaries. Versioned per cycle.

#### Acceptance Criteria

- Prep brief auto-pulls bookmarks tagged to the current arc that were added since the last session
- Reading list shows per-person completion status
- Workshop assignments link to Player nodes (reuse existing Player infrastructure)

---

## Suggested Build Order

```
Workstream 1: Cycle Engine
  ├── 1a. Cycle + ScheduledSession nodes, constraints, seed script
  ├── 1b. Cycle API (CRUD, /current)
  ├── 1c. Rota API (lead/shadow assignment)
  ├── 1d. Dashboard page
  └── 1e. Schedule page

Workstream 2: Lock Workflow
  ├── 2a. Extend Position model (version, status, anti-position, etc.)
  ├── 2b. ProblemLandscapeBrief + LandscapeGrid nodes
  ├── 2c. Lock/revise API endpoints
  ├── 2d. Session workspace page (Week 1 brief editor)
  └── 2e. Session workspace page (Week 2 position editor)

Workstream 3: Evidence Vault & Live Fire
  ├── 3a. LiveFireEntry + Flash nodes
  ├── 3b. Live Fire API (CRUD, metrics)
  ├── 3c. Flash API (CRUD, pending)
  ├── 3d. Evidence Vault page
  ├── 3e. Live Fire dashboard
  └── 3f. Arc Pulse view

Workstream 4: Forge Pipeline
  ├── 4a. ForgeAssignment node
  ├── 4b. Forge API (CRUD, tracker)
  ├── 4c. Forge board page
  └── 4d. Dashboard tracker widget

Workstream 5: Prep & Onboarding
  ├── 5a. WorkshopAssignment + ReadingAssignment nodes
  ├── 5b. Prep API endpoints
  ├── 5c. Session prep page
  └── 5d. Fast-Track page
```

Start with 1a-1e. Everything else keys off knowing where you are in the cycle.

---

## Conventions Reminder

- **API**: REST, `/api/v1/` prefix, response envelope `{ "data": ..., "meta": { "count": n } }`, cursor-based pagination
- **Neo4j**: Parameterised Cypher only. MERGE with ON CREATE SET / ON MATCH SET. Node labels PascalCase singular. Relationships UPPER_SNAKE_CASE. All queries in repositories, never in routers or services.
- **Frontend**: Server components for pages, client components for interactivity. TanStack Query for client-side fetching. Tailwind CSS. D3 in React via useEffect with cleanup.
- **Python**: Type hints everywhere. Async in FastAPI. Pydantic v2 for all API boundaries. Dependencies via `Depends()`.
- **Testing**: Test alongside source. Behaviour-named tests. Mock at boundaries.

---

## Files to Read First

When starting a workstream, read these files to understand the patterns:

| Purpose | File |
|---------|------|
| Router pattern | `apps/api/routers/arcs.py` |
| Service pattern | `apps/api/services/arc_service.py` |
| Repository pattern | `apps/api/repositories/arc_repository.py` |
| Model pattern | `apps/api/models/arc.py` |
| Response envelope | `apps/api/models/common.py` |
| Neo4j driver setup | `apps/api/core/database.py` |
| Dependency injection | `apps/api/core/dependencies.py` |
| Frontend page pattern | `apps/web/app/arcs/page.tsx` |
| API client pattern | `apps/web/lib/api-client.ts` |
| Hook pattern | `apps/web/lib/hooks/use-sessions.ts` |
| Type definitions | `apps/web/types/entities.ts` |
| D3 component pattern | `apps/web/components/graph/ArcExplorer/index.tsx` |
| Schema init script | `scripts/init-schema.cypher` |
