export interface Arc {
  name: string;
  bookmark_count: number;
  session_count: number;
  created_at: string;
  updated_at: string;
}

export interface ThemeBridge {
  source_theme_name: string;
  target_theme_name: string;
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
  arc_names: string[];
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
  primary_theme: string | null;
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
