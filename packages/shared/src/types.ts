/** API response envelope for single items. */
export interface ApiResponse<T> {
  data: T;
  meta?: Record<string, unknown>;
}

/** API response envelope for paginated collections. */
export interface PaginatedResponse<T> {
  data: T[];
  meta: PaginationMeta;
}

export interface PaginationMeta {
  count: number;
  cursor: string | null;
  has_more: boolean;
}

/** Error response envelope. */
export interface ErrorResponse {
  error: {
    code: string;
    message: string;
  };
}

/** Arc entity. */
export interface Arc {
  number: number;
  name: string;
  description: string | null;
  position_count: number;
  created_at: string;
  updated_at: string;
}

/** Arc detail with nested relations. */
export interface ArcDetail {
  number: number;
  name: string;
  description: string | null;
  positions: PositionSummary[];
  bridges: CrossArcBridge[];
  steelman_arguments: SteelmanSummary[];
  created_at: string;
  updated_at: string;
}

/** Bookmark entity. */
export interface Bookmark {
  notion_id: string;
  title: string;
  source: string | null;
  url: string | null;
  ai_summary: string | null;
  valliance_viewpoint: string | null;
  edge_or_foundational: string | null;
  focus: string | null;
  time_consumption: string | null;
  date_added: string | null;
  topic_names: string[];
  theme_name: string | null;
  created_at: string;
  updated_at: string;
}

/** Session entity. */
export interface Session {
  notion_id: string;
  title: string;
  date: string | null;
  duration: number | null;
  summary: string | null;
  arc_focus: string | null;
  created_at: string;
  updated_at: string;
}

/** Position summary used in arc detail and argument maps. */
export interface PositionSummary {
  id: string;
  text: string;
  status: string;
  locked_date: string | null;
  proposition: string | null;
}

/** Position entity with full detail. */
export interface Position {
  id: string;
  text: string;
  status: string;
  locked_date: string | null;
  arc_number: number;
  proposition: string | null;
  created_at: string;
  updated_at: string;
}

/** Cross-arc bridge. */
export interface CrossArcBridge {
  id: string;
  label: string | null;
  strength: string;
  source_position_id: string;
  target_position_id: string;
  source_arc_number: number | null;
  target_arc_number: number | null;
  created_at: string;
  updated_at: string;
}

/** Steelman argument summary. */
export interface SteelmanSummary {
  id: string;
  text: string;
}

/** Topic entity. */
export interface Topic {
  name: string;
  co_occurrence_count: number;
  theme: string | null;
  created_at: string;
  updated_at: string;
}

/** Argument entity. */
export interface Argument {
  id: string;
  text: string;
  sentiment: string;
  strength: string | null;
  speaker: string | null;
  session_id: string | null;
  created_at: string;
  updated_at: string;
}

/** Evidence entity. */
export interface Evidence {
  id: string;
  text: string;
  type: string;
  source_id: string | null;
  created_at: string;
  updated_at: string;
}

/** Action item entity. */
export interface ActionItem {
  id: string;
  text: string;
  assignee: string | null;
  due_date: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

/** Player entity. */
export interface Player {
  name: string;
  created_at: string;
  updated_at: string;
}
