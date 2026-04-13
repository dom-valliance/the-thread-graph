// =============================================================================
// Neo4j Schema Initialisation: Constraints and Indexes
// Run once against a fresh database, safe to re-run (all use IF NOT EXISTS).
// =============================================================================

// ---------------------------------------------------------------------------
// Uniqueness Constraints (17)
// ---------------------------------------------------------------------------

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

CREATE CONSTRAINT cycle_id IF NOT EXISTS
FOR (c:Cycle) REQUIRE c.id IS UNIQUE;

CREATE CONSTRAINT scheduled_session_id IF NOT EXISTS
FOR (ss:ScheduledSession) REQUIRE ss.id IS UNIQUE;

CREATE CONSTRAINT brief_id IF NOT EXISTS
FOR (b:ProblemLandscapeBrief) REQUIRE b.id IS UNIQUE;

CREATE CONSTRAINT landscape_grid_id IF NOT EXISTS
FOR (lg:LandscapeGrid) REQUIRE lg.id IS UNIQUE;

CREATE CONSTRAINT landscape_grid_entry_id IF NOT EXISTS
FOR (lge:LandscapeGridEntry) REQUIRE lge.id IS UNIQUE;

CREATE CONSTRAINT live_fire_entry_id IF NOT EXISTS
FOR (lf:LiveFireEntry) REQUIRE lf.id IS UNIQUE;

CREATE CONSTRAINT flash_id IF NOT EXISTS
FOR (f:Flash) REQUIRE f.id IS UNIQUE;

CREATE CONSTRAINT forge_assignment_id IF NOT EXISTS
FOR (fa:ForgeAssignment) REQUIRE fa.id IS UNIQUE;

CREATE CONSTRAINT workshop_assignment_id IF NOT EXISTS
FOR (wa:WorkshopAssignment) REQUIRE wa.id IS UNIQUE;

CREATE CONSTRAINT reading_assignment_id IF NOT EXISTS
FOR (ra:ReadingAssignment) REQUIRE ra.id IS UNIQUE;

CREATE CONSTRAINT thread_prep_brief_id IF NOT EXISTS
FOR (tpb:ThreadPrepBrief) REQUIRE tpb.id IS UNIQUE;

// ---------------------------------------------------------------------------
// Performance Indexes (7)
// ---------------------------------------------------------------------------

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

CREATE INDEX cycle_status IF NOT EXISTS
FOR (c:Cycle) ON (c.status);

CREATE INDEX scheduled_session_status IF NOT EXISTS
FOR (ss:ScheduledSession) ON (ss.status);

CREATE INDEX scheduled_session_date IF NOT EXISTS
FOR (ss:ScheduledSession) ON (ss.date);

CREATE INDEX live_fire_date IF NOT EXISTS
FOR (lf:LiveFireEntry) ON (lf.date);

CREATE INDEX flash_status IF NOT EXISTS
FOR (f:Flash) ON (f.status);

CREATE INDEX evidence_vault_type IF NOT EXISTS
FOR (e:Evidence) ON (e.vault_type);

CREATE INDEX evidence_proposition IF NOT EXISTS
FOR (e:Evidence) ON (e.proposition_mapping);

CREATE INDEX forge_status IF NOT EXISTS
FOR (fa:ForgeAssignment) ON (fa.status);

CREATE INDEX forge_deadline IF NOT EXISTS
FOR (fa:ForgeAssignment) ON (fa.deadline);

// ---------------------------------------------------------------------------
// Full-Text Indexes (3)
// ---------------------------------------------------------------------------

CREATE FULLTEXT INDEX bookmark_search IF NOT EXISTS
FOR (b:Bookmark) ON EACH [b.title, b.ai_summary, b.valliance_viewpoint];

CREATE FULLTEXT INDEX position_search IF NOT EXISTS
FOR (p:Position) ON EACH [p.text];

CREATE FULLTEXT INDEX argument_search IF NOT EXISTS
FOR (a:Argument) ON EACH [a.text];
