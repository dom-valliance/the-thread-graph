# Module: Neo4j Data Layer

Neo4j 5.x graph database storing the Valliance knowledge graph. This module defines the schema, constraints, indexes, seed data strategy, and query patterns.

---

## Technology

- Neo4j 5.x (Community Edition for dev, Enterprise for production)
- Cypher query language
- APOC plugin (for batch operations and utility functions)
- Neo4j Browser for ad hoc queries during development

## Schema

### Node Labels

All labels are PascalCase singular. Every node carries `created_at` (datetime) and `updated_at` (datetime) managed by the repository layer.

| Label | Primary Key | Source |
|-------|------------|--------|
| Bookmark | notion_id (string) | Notion Bookmarks DB |
| Session | notion_id (string) | Notion Learning Sessions DB |
| Arc | number (integer, 1-6) | Manual |
| Position | id (string) | Manual, locked in sessions |
| AntiPosition | id (string) | Manual |
| Person | email (string) | Manual |
| Topic | name (string) | Notion Bookmarks DB multi-select |
| Theme | name (string) | Notion Bookmarks DB select |
| Argument | id (string) | NLP extraction + manual review |
| ActionItem | id (string) | NLP extraction + manual review |
| ObjectionResponsePair | id (string) | Manual, post-engagement |
| CrossArcBridge | id (string) | Manual |
| SteelmanArgument | id (string) | Manual |
| Evidence | id (string) | Manual + NLP |
| Player | name (string) | Manual |
| Proposition | name (string, enum) | Manual (P1 or V1) |

### Relationship Types

All relationship types are UPPER_SNAKE_CASE. Defined in the architecture brief Section 2.

```
Bookmark relationships:
  (Bookmark)-[:TAGGED_WITH]->(Topic)
  (Bookmark)-[:HAS_THEME]->(Theme)
  (Bookmark)-[:DISCUSSED_IN]->(Session)
  (Bookmark)-[:EVIDENCES]->(Position)
  (Bookmark)-[:RELATES_TO]->(Bookmark)
  (Bookmark)-[:AUTHORED_BY]->(Person)
  (Bookmark)-[:COVERS_PLAYER]->(Player)
  (Bookmark)-[:PUBLISHED_BY]->(Player)

Session relationships:
  (Session)-[:COVERS]->(Arc)
  (Session)-[:PRODUCED]->(Position)
  (Session)-[:GENERATED]->(ActionItem)
  (Session)-[:REFERENCED]->(Bookmark)
  (Session)-[:CONTAINED]->(Argument)

Person relationships:
  (Person)-[:PRESENTED_IN]->(Session)
  (Person)-[:RAISED]->(Argument)
  (Person)-[:ASSIGNED]->(ActionItem)
  (Person)-[:PROMOTED]->(Bookmark)
  (Person)-[:LOCKED]->(Position)
  (Person)-[:OWNS]->(Arc)

Argument relationships:
  (Argument)-[:SUPPORTS]->(Position)
  (Argument)-[:CHALLENGES]->(Position)
  (Argument)-[:REFERENCES]->(Bookmark)
  (Argument)-[:MADE_IN]->(Session)
  (Argument)-[:COUNTERED_BY]->(Argument)
  (Argument)-[:RELATES_TO]->(Argument)

Position relationships:
  (Position)-[:LOCKED_IN]->(Arc)
  (Position)-[:HAS_ANTI_POSITION]->(AntiPosition)
  (Position)-[:BRIDGES_TO]->(Position) [via CrossArcBridge]
  (Position)-[:MAPS_TO]->(Proposition)
  (Position)-[:TESTED_BY]->(ObjectionResponsePair)
  (Position)-[:REPLACED_BY]->(Position)

Arc relationships:
  (Arc)-[:FOLLOWS]->(Arc)
  (Arc)-[:HAS_STEELMAN]->(SteelmanArgument)
  (Arc)-[:HAS_POSITION]->(Position)

Topic relationships:
  (Topic)-[:CO_OCCURS_WITH]->(Topic)

Evidence relationships:
  (Evidence)-[:SUPPORTS]->(Position)
  (Evidence)-[:SOURCED_FROM]->(Bookmark)
  (Evidence)-[:GENERATED_IN]->(Session)
```

## Constraints and Indexes

Run on database initialisation:

```cypher
// Uniqueness constraints (also create indexes)
CREATE CONSTRAINT bookmark_notion_id IF NOT EXISTS
  FOR (b:Bookmark) REQUIRE b.notion_id IS UNIQUE;

CREATE CONSTRAINT session_notion_id IF NOT EXISTS
  FOR (s:Session) REQUIRE s.notion_id IS UNIQUE;

CREATE CONSTRAINT arc_number IF NOT EXISTS
  FOR (a:Arc) REQUIRE a.number IS UNIQUE;

CREATE CONSTRAINT position_id IF NOT EXISTS
  FOR (p:Position) REQUIRE p.id IS UNIQUE;

CREATE CONSTRAINT anti_position_id IF NOT EXISTS
  FOR (ap:AntiPosition) REQUIRE ap.id IS UNIQUE;

CREATE CONSTRAINT person_email IF NOT EXISTS
  FOR (p:Person) REQUIRE p.email IS UNIQUE;

CREATE CONSTRAINT topic_name IF NOT EXISTS
  FOR (t:Topic) REQUIRE t.name IS UNIQUE;

CREATE CONSTRAINT theme_name IF NOT EXISTS
  FOR (th:Theme) REQUIRE th.name IS UNIQUE;

CREATE CONSTRAINT argument_id IF NOT EXISTS
  FOR (a:Argument) REQUIRE a.id IS UNIQUE;

CREATE CONSTRAINT action_item_id IF NOT EXISTS
  FOR (ai:ActionItem) REQUIRE ai.id IS UNIQUE;

CREATE CONSTRAINT orp_id IF NOT EXISTS
  FOR (orp:ObjectionResponsePair) REQUIRE orp.id IS UNIQUE;

CREATE CONSTRAINT bridge_id IF NOT EXISTS
  FOR (cab:CrossArcBridge) REQUIRE cab.id IS UNIQUE;

CREATE CONSTRAINT steelman_id IF NOT EXISTS
  FOR (sa:SteelmanArgument) REQUIRE sa.id IS UNIQUE;

CREATE CONSTRAINT evidence_id IF NOT EXISTS
  FOR (e:Evidence) REQUIRE e.id IS UNIQUE;

CREATE CONSTRAINT player_name IF NOT EXISTS
  FOR (pl:Player) REQUIRE pl.name IS UNIQUE;

CREATE CONSTRAINT proposition_name IF NOT EXISTS
  FOR (pr:Proposition) REQUIRE pr.name IS UNIQUE;

// Additional indexes for query performance
CREATE INDEX session_date IF NOT EXISTS
  FOR (s:Session) ON (s.date);

CREATE INDEX bookmark_date_added IF NOT EXISTS
  FOR (b:Bookmark) ON (b.date_added);

CREATE INDEX position_status IF NOT EXISTS
  FOR (p:Position) ON (p.status);

CREATE INDEX position_locked_date IF NOT EXISTS
  FOR (p:Position) ON (p.locked_date);

CREATE INDEX argument_sentiment IF NOT EXISTS
  FOR (a:Argument) ON (a.sentiment);

CREATE INDEX action_item_status IF NOT EXISTS
  FOR (ai:ActionItem) ON (ai.status);

CREATE INDEX evidence_type IF NOT EXISTS
  FOR (e:Evidence) ON (e.type);

// Full-text indexes for search
CREATE FULLTEXT INDEX bookmark_search IF NOT EXISTS
  FOR (b:Bookmark) ON EACH [b.title, b.ai_summary, b.valliance_viewpoint];

CREATE FULLTEXT INDEX position_search IF NOT EXISTS
  FOR (p:Position) ON EACH [p.text];

CREATE FULLTEXT INDEX argument_search IF NOT EXISTS
  FOR (a:Argument) ON EACH [a.text];
```

## Idempotent Write Patterns

All ingestion uses MERGE keyed on the primary key. Properties are set via ON CREATE SET and ON MATCH SET.

### Bookmark upsert

```cypher
MERGE (b:Bookmark {notion_id: $notion_id})
ON CREATE SET
  b.title = $title,
  b.source = $source,
  b.url = $url,
  b.ai_summary = $ai_summary,
  b.valliance_viewpoint = $valliance_viewpoint,
  b.edge_or_foundational = $edge_or_foundational,
  b.focus = $focus,
  b.time_consumption = $time_consumption,
  b.date_added = datetime($date_added),
  b.created_at = datetime(),
  b.updated_at = datetime()
ON MATCH SET
  b.title = $title,
  b.source = $source,
  b.url = $url,
  b.ai_summary = $ai_summary,
  b.valliance_viewpoint = $valliance_viewpoint,
  b.edge_or_foundational = $edge_or_foundational,
  b.focus = $focus,
  b.time_consumption = $time_consumption,
  b.updated_at = datetime()
WITH b
UNWIND $topic_names AS topic_name
MERGE (t:Topic {name: topic_name})
ON CREATE SET t.created_at = datetime(), t.updated_at = datetime()
MERGE (b)-[:TAGGED_WITH]->(t)
WITH b, $theme_name AS theme_name
WHERE theme_name IS NOT NULL
MERGE (th:Theme {name: theme_name})
ON CREATE SET th.created_at = datetime(), th.updated_at = datetime()
MERGE (b)-[:HAS_THEME]->(th)
```

### Relationship upsert pattern

```cypher
MATCH (source:Bookmark {notion_id: $bookmark_id})
MATCH (target:Position {id: $position_id})
MERGE (source)-[:EVIDENCES]->(target)
```

## Seed Data

Phase 1 seed script loads:

1. Six Arc nodes (Agentic AI, Palantir/Ontology, People Enablement, Consulting Craft, Agentic Engineering, Value Realisation) with FOLLOWS relationships.
2. Two Proposition nodes (P1 People First, V1 Value First).
3. All bookmarks from Notion Bookmarks DB via sync service.
4. All Topic and Theme nodes derived from bookmark fields.
5. All sessions from Notion Learning Sessions DB via sync service.
6. Manually authored initial positions, anti-positions, and person nodes.

Seed script is idempotent. Safe to re-run.

## Query Library

The ten use-case queries from the architecture brief Section 3 are implemented as repository methods. Each maps to an API endpoint.

## Development Setup

```bash
# Local Neo4j via Docker
docker compose up neo4j

# Connect via browser
open http://localhost:7474

# Run constraint/index setup
cypher-shell -u neo4j -p <password> -f scripts/init-schema.cypher

# Run seed
python scripts/seed.py
```

## Backup Strategy

- Production: Azure-managed Neo4j backup via AKS persistent volumes.
- Dev: `neo4j-admin database dump` before destructive operations.
- CI: testcontainers provides ephemeral instances per test run.
