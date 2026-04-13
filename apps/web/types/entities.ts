export interface Arc {
  name: string;
  bookmark_count: number;
  session_count: number;
  created_at: string;
  updated_at: string;
}

export interface ArcBridge {
  id: string;
  source_arc_name: string;
  target_arc_name: string;
  shared_topics: number;
  strength: string;
  label: string | null;
}

export interface Position {
  proposition: string;
  locked_date: string | null;
  id: string;
  text: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface SteelmanArgument {
  id: string;
  text: string;
  created_at: string;
  updated_at: string;
}

export interface ArcDetail {
  name: string;
  description: string | null;
  bookmark_count: number;
  session_count: number;
  bookmarks: Bookmark[];
  created_at: string;
  updated_at: string;
  positions: Position[];
  number: number;
  steelman_arguments: SteelmanArgument[];
  bridges: ArcBridge[];
}

export interface Bookmark {
  id: string;
  notion_id?: string;
  title: string;
  url: string | null;
  source: string | null;
  ai_summary: string | null;
  valliance_viewpoint: string | null;
  edge_or_foundational: string | null;
  focus: string | null;
  topic_names: string[];
  theme_name: string | null;
  arc_bucket_names: string[];
  date_added: string | null;
  created_at: string;
  updated_at: string;
}

export interface Session {
  notion_id: string;
  title: string;
  date: string;
  duration: number | null;
  summary: string | null;
  theme_name: string | null;
  enrichment_status: string | null;
  created_at: string;
  updated_at: string;
}

export interface Topic {
  name: string;
  bookmark_count: number;
  primary_arc: string | null;
  created_at: string;
  updated_at: string;
}

export interface TopicCoOccurrence {
  name: string;
  co_occurring_topic: string;
  count: number;
}

export interface Argument {
  id: string;
  text: string;
  type: string;
  strength: string;
  created_at: string;
  updated_at: string;
}

export interface Evidence {
  id: string;
  text: string;
  type: string;
  source: string | null;
  source_title: string | null;
  vault_type: string | null;
  proposition_mapping: string | null;
  created_at: string;
  updated_at: string;
}

// Arc drill-down: bookmark-to-bookmark edges

export interface BookmarkEdge {
  source_notion_id: string;
  target_notion_id: string;
  shared_topics: number;
  shared_topic_names: string[];
}

// Objection Forge: ORPs with position and arc context

export interface ObjectionPairWithContext {
  id: string;
  objection_text: string;
  response_text: string;
  position_id: string;
  position_text: string;
  arc_name: string;
  arc_number: number;
  created_at: string;
  updated_at: string;
}

// Evidence Trail: provenance chain from bookmarks to positions

export interface EvidenceTrailBookmark {
  notion_id: string;
  title: string;
  url: string | null;
  source: string | null;
  edge_or_foundational: string | null;
  ai_summary: string | null;
  arc_names: string[];
}

export interface EvidenceTrailItem {
  id: string;
  text: string;
  type: string;
  source_bookmark: EvidenceTrailBookmark | null;
}

export interface EvidenceTrailResponse {
  position_id: string;
  position_text: string;
  evidence: EvidenceTrailItem[];
  unsourced_count: number;
  bridge_bookmark_count: number;
}

// Cross-Arc Bridge Explorer

export interface CrossArcBridge {
  strength: string;
  label: string | null;
  source_position_id: string;
  source_position_text: string;
  source_arc_name: string;
  source_arc_number: number;
  target_position_id: string;
  target_position_text: string;
  target_arc_name: string;
  target_arc_number: number;
}

export interface UnconnectedPosition {
  id: string;
  text: string;
  arc_name: string;
  arc_number: number;
}

// Cycle Engine

export interface Cycle {
  id: string;
  number: number;
  start_date: string;
  end_date: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ScheduledSession {
  id: string;
  cycle_number: number;
  week_number: number;
  arc_number: number;
  arc_name: string;
  week_type: string;
  date: string | null;
  status: string;
  lead_name: string | null;
  lead_email: string | null;
  shadow_name: string | null;
  shadow_email: string | null;
  created_at: string;
  updated_at: string;
}

export interface CycleCurrentResponse {
  id: string;
  number: number;
  start_date: string;
  end_date: string;
  status: string;
  created_at: string;
  updated_at: string;
  current_session: ScheduledSession | null;
  days_until_next: number | null;
}

export interface CycleSchedule {
  cycle: Cycle;
  sessions: ScheduledSession[];
}

// Session Capture & Lock Workflow

export interface LandscapeGridEntry {
  id: string;
  player_name: string;
  criterion: string;
  rating: string;
  notes: string;
}

export interface LandscapeGrid {
  id: string;
  entries: LandscapeGridEntry[];
}

export interface ProblemLandscapeBrief {
  id: string;
  problem_statement: string;
  landscape_criteria: string[];
  steelman_summary: string;
  status: string;
  locked_date: string | null;
  locked_by: string | null;
  session_id: string | null;
  arc_name: string | null;
  landscape_grid: LandscapeGrid | null;
  created_at: string;
  updated_at: string;
}

// Evidence Vault & Live Fire

export interface LiveFireEntry {
  id: string;
  outcome: string;
  context: string;
  date: string;
  position_id: string | null;
  position_text: string | null;
  reporter_name: string | null;
  reporter_email: string | null;
  created_at: string;
  updated_at: string;
}

export interface LiveFirePositionMetric {
  position_id: string;
  position_text: string;
  total_uses: number;
  successes: number;
  failures: number;
  success_rate: number | null;
  last_used: string | null;
  never_used: boolean;
}

export interface LiveFireMetrics {
  metrics: LiveFirePositionMetric[];
}

export interface Flash {
  id: string;
  title: string;
  description: string;
  status: string;
  reviewed_date: string | null;
  position_id: string | null;
  position_text: string | null;
  raised_by_name: string | null;
  raised_by_email: string | null;
  created_at: string;
  updated_at: string;
}

// Forge & Content Pipeline

export interface ForgeAssignment {
  id: string;
  artefact_type: string;
  status: string;
  deadline: string;
  storyboard_notes: string | null;
  published_url: string | null;
  editor_notes: string | null;
  assigned_to_name: string | null;
  assigned_to_email: string | null;
  editor_name: string | null;
  editor_email: string | null;
  session_id: string | null;
  arc_name: string | null;
  created_at: string;
  updated_at: string;
}

export interface ForgeTracker {
  cycle_id: string;
  total_target: number;
  produced: number;
  by_type: Record<string, number>;
}

// Prep & Onboarding

export interface WorkshopAssignment {
  id: string;
  player_or_approach: string;
  analysis_notes: string | null;
  status: string;
  assigned_to_name: string | null;
  assigned_to_email: string | null;
  player_name: string | null;
  created_at: string;
  updated_at: string;
}

export interface ReadingAssignment {
  id: string;
  status: string;
  assigned_to_name: string | null;
  assigned_to_email: string | null;
  bookmark_title: string | null;
  bookmark_notion_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface PrepBrief {
  session_id: string;
  arc_name: string | null;
  recent_bookmarks: { notion_id: string; title: string; url: string | null; date_added: string | null }[];
  previous_locked_position_text: string | null;
  evidence_count: number;
}

// Thread Prep Brief (LLM-generated)

export interface BookmarkAnchorMapping {
  bookmark_title: string;
  bookmark_source: string | null;
  pmf_anchor: string;
  contribution: string;
}

export interface WorkshopCriterion {
  criterion: string;
  what_it_tests: string;
}

export interface ThreadPrepReadingAssignment {
  player: string;
  bookmark_titles: string[];
}

export interface AdjacentBookmark {
  bookmark_title: string;
  relevant_arc: string;
  reason: string;
}

export interface FlashCheck {
  bookmark_title: string;
  challenged_arc: string;
  challenged_claim: string;
}

export interface ThreadPrepBrief {
  id: string;
  session_id: string;
  week_type: string;
  arc_number: number;
  arc_name: string;
  sharpened_problem_question: string | null;
  problem_question_rationale: string | null;
  sharpened_landscape_question: string | null;
  landscape_question_rationale: string | null;
  steelman_argument: string | null;
  steelman_rationale: string | null;
  workshop_grid_criteria: WorkshopCriterion[];
  new_evidence_since_week1: string | null;
  objection_fuel: string | null;
  cross_arc_bridge_prompts: string | null;
  p1_v1_signal: string | null;
  bookmark_anchor_mapping: BookmarkAnchorMapping[];
  reading_assignments: ThreadPrepReadingAssignment[];
  adjacent_bookmarks: AdjacentBookmark[];
  flash_checks: FlashCheck[];
  bookmark_count: number;
  raw_markdown: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface PositionVersion {
  id: string;
  text: string;
  version: number;
  status: string;
  locked_date: string | null;
  locked_by: string | null;
  created_at: string;
  updated_at: string;
}
