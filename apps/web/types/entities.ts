export interface Arc {
  name: string;
  bookmark_count: number;
  session_count: number;
  created_at: string;
  updated_at: string;
}

export interface ArcBridge {
  source_arc_name: string;
  target_arc_name: string;
  shared_topics: number;
}

export interface ArcDetail {
  name: string;
  bookmark_count: number;
  session_count: number;
  bookmarks: Bookmark[];
  created_at: string;
  updated_at: string;
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
  source: string | null;
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
