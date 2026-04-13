import type { ApiResponse, PaginatedResponse } from '@/types/api';
import type {
  Arc,
  ArcBridge,
  ArcDetail,
  Bookmark,
  BookmarkEdge,
  CrossArcBridge,
  Cycle,
  CycleCurrentResponse,
  CycleSchedule,
  Evidence,
  EvidenceTrailResponse,
  ForgeAssignment,
  ForgeTracker,
  ObjectionPairWithContext,
  PositionVersion,
  ProblemLandscapeBrief,
  ScheduledSession,
  Flash,
  LiveFireEntry,
  LiveFireMetrics,
  PrepBrief,
  ReadingAssignment,
  ThreadPrepBrief,
  UnconnectedPosition,
  WorkshopAssignment,
} from '@/types/entities';

// Server components run inside Docker where localhost does not reach the API container.
// API_URL is the internal (server-side) address; NEXT_PUBLIC_API_URL is the browser-facing one.
const API_BASE_URL =
  process.env.API_URL ??
  process.env.NEXT_PUBLIC_API_URL ??
  'http://localhost:8000/api/v1';

class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
    message: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${path}`;
  const response = await fetch(url, {
    ...init,
    cache: 'no-store',
    headers: {
      'Content-Type': 'application/json',
      ...init?.headers,
    },
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const code = body?.error?.code ?? 'UNKNOWN_ERROR';
    const message = body?.error?.message ?? `Request failed with status ${response.status}`;
    throw new ApiError(response.status, code, message);
  }

  const envelope: ApiResponse<T> = await response.json();
  return envelope.data;
}

export async function apiGet<T>(path: string): Promise<T> {
  return apiFetch<T>(path, { method: 'GET' });
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  return apiFetch<T>(path, {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

export async function getArcs(): Promise<Arc[]> {
  return apiGet<Arc[]>('/arcs');
}

export async function getArcDetail(arcName: string): Promise<ArcDetail> {
  return apiGet<ArcDetail>(`/arcs/${encodeURIComponent(arcName)}`);
}

export async function getArcBridges(): Promise<ArcBridge[]> {
  return apiGet<ArcBridge[]>('/arcs/bridges');
}

// Paginated fetch that preserves the meta envelope

async function apiFetchPaginated<T>(
  path: string,
  init?: RequestInit,
): Promise<PaginatedResponse<T>> {
  const url = `${API_BASE_URL}${path}`;
  const response = await fetch(url, {
    ...init,
    cache: 'no-store',
    headers: {
      'Content-Type': 'application/json',
      ...init?.headers,
    },
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const code = body?.error?.code ?? 'UNKNOWN_ERROR';
    const message = body?.error?.message ?? `Request failed with status ${response.status}`;
    throw new ApiError(response.status, code, message);
  }

  return response.json();
}

// Arc drill-down

export async function getArcBookmarks(
  arcName: string,
  offset: number = 0,
  limit: number = 10,
): Promise<PaginatedResponse<Bookmark>> {
  return apiFetchPaginated<Bookmark>(
    `/arcs/${encodeURIComponent(arcName)}/bookmarks?offset=${offset}&limit=${limit}`,
  );
}

export async function getArcBookmarkEdges(
  arcName: string,
  notionIds: string[],
): Promise<BookmarkEdge[]> {
  return apiPost<BookmarkEdge[]>(
    `/arcs/${encodeURIComponent(arcName)}/bookmarks/edges`,
    { notion_ids: notionIds },
  );
}

// Objection Forge CRUD

export async function getObjectionPairs(
  arcName?: string,
): Promise<ObjectionPairWithContext[]> {
  const params = arcName ? `?arc_name=${encodeURIComponent(arcName)}` : '';
  return apiGet<ObjectionPairWithContext[]>(`/objections${params}`);
}

export async function createObjectionPair(data: {
  objection_text: string;
  response_text: string;
  position_id: string;
}): Promise<ObjectionPairWithContext> {
  return apiPost<ObjectionPairWithContext>('/objections', data);
}

export async function updateObjectionPair(
  pairId: string,
  data: { objection_text: string; response_text: string },
): Promise<ObjectionPairWithContext> {
  return apiFetch<ObjectionPairWithContext>(`/objections/${encodeURIComponent(pairId)}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function deleteObjectionPair(pairId: string): Promise<void> {
  const url = `${API_BASE_URL}/objections/${encodeURIComponent(pairId)}`;
  const response = await fetch(url, { method: 'DELETE', cache: 'no-store' });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new ApiError(
      response.status,
      body?.error?.code ?? 'UNKNOWN_ERROR',
      body?.error?.message ?? `Delete failed with status ${response.status}`,
    );
  }
}

// Evidence Trail + CRUD

export async function getEvidenceTrail(
  positionId: string,
): Promise<EvidenceTrailResponse> {
  return apiGet<EvidenceTrailResponse>(
    `/positions/${encodeURIComponent(positionId)}/evidence-trail`,
  );
}

export async function createEvidence(data: {
  text: string;
  type: string;
  position_id: string;
  source_bookmark_id?: string | null;
}): Promise<unknown> {
  return apiPost('/evidence', data);
}

export async function updateEvidence(
  evidenceId: string,
  data: { text: string; type: string; source_bookmark_id?: string | null },
): Promise<unknown> {
  return apiFetch(`/evidence/${encodeURIComponent(evidenceId)}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function deleteEvidence(evidenceId: string): Promise<void> {
  const url = `${API_BASE_URL}/evidence/${encodeURIComponent(evidenceId)}`;
  const response = await fetch(url, { method: 'DELETE', cache: 'no-store' });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new ApiError(
      response.status,
      body?.error?.code ?? 'UNKNOWN_ERROR',
      body?.error?.message ?? `Delete failed with status ${response.status}`,
    );
  }
}

// Cross-Arc Bridge Explorer

export async function getCrossArcBridges(): Promise<CrossArcBridge[]> {
  return apiGet<CrossArcBridge[]>('/bridges');
}

export async function getUnconnectedPositions(): Promise<UnconnectedPosition[]> {
  return apiGet<UnconnectedPosition[]>('/bridges/gaps');
}

// Prep & Onboarding

export async function getWorkshopAssignments(sessionId: string): Promise<WorkshopAssignment[]> {
  return apiGet<WorkshopAssignment[]>(
    `/scheduled-sessions/${encodeURIComponent(sessionId)}/workshop-assignments`,
  );
}

export async function createWorkshopAssignment(
  sessionId: string,
  data: { player_or_approach: string; assigned_to_email: string },
): Promise<WorkshopAssignment> {
  return apiPost<WorkshopAssignment>(
    `/scheduled-sessions/${encodeURIComponent(sessionId)}/workshop-assignments`,
    data,
  );
}

export async function updateWorkshopAssignment(
  assignmentId: string,
  data: { status?: string; analysis_notes?: string },
): Promise<WorkshopAssignment> {
  return apiFetch<WorkshopAssignment>(
    `/workshop-assignments/${encodeURIComponent(assignmentId)}`,
    { method: 'PUT', body: JSON.stringify(data) },
  );
}

export async function getReadingList(sessionId: string): Promise<ReadingAssignment[]> {
  return apiGet<ReadingAssignment[]>(
    `/scheduled-sessions/${encodeURIComponent(sessionId)}/reading-list`,
  );
}

export async function createReadingAssignment(
  sessionId: string,
  data: { bookmark_notion_id: string; assigned_to_email: string },
): Promise<ReadingAssignment> {
  return apiPost<ReadingAssignment>(
    `/scheduled-sessions/${encodeURIComponent(sessionId)}/reading-list`,
    data,
  );
}

export async function updateReadingAssignment(
  assignmentId: string,
  data: { status: string },
): Promise<ReadingAssignment> {
  return apiFetch<ReadingAssignment>(
    `/reading-assignments/${encodeURIComponent(assignmentId)}`,
    { method: 'PUT', body: JSON.stringify(data) },
  );
}

export async function getPrepBrief(sessionId: string): Promise<PrepBrief> {
  return apiGet<PrepBrief>(
    `/scheduled-sessions/${encodeURIComponent(sessionId)}/prep-brief`,
  );
}

export async function getThreadPrep(sessionId: string): Promise<ThreadPrepBrief> {
  return apiGet<ThreadPrepBrief>(
    `/scheduled-sessions/${encodeURIComponent(sessionId)}/thread-prep`,
  );
}

export async function generateThreadPrep(sessionId: string): Promise<ThreadPrepBrief> {
  return apiPost<ThreadPrepBrief>(
    `/scheduled-sessions/${encodeURIComponent(sessionId)}/generate-prep`,
    {},
  );
}

export async function regenerateThreadPrep(sessionId: string): Promise<ThreadPrepBrief> {
  return apiPost<ThreadPrepBrief>(
    `/scheduled-sessions/${encodeURIComponent(sessionId)}/regenerate-prep`,
    {},
  );
}

// Forge

export async function createForgeAssignment(data: {
  artefact_type: string;
  deadline: string;
  assigned_to_email: string;
  session_id: string;
  arc_name: string;
  derived_from_id?: string | null;
  storyboard_notes?: string | null;
}): Promise<ForgeAssignment> {
  return apiPost<ForgeAssignment>('/forge', data);
}

export async function getForgeAssignments(params?: {
  status?: string;
  arc?: string;
  person?: string;
  cycle_id?: string;
}): Promise<ForgeAssignment[]> {
  const qs = params ? '?' + new URLSearchParams(
    Object.entries(params).filter(([, v]) => v != null) as [string, string][]
  ).toString() : '';
  return apiGet<ForgeAssignment[]>(`/forge${qs}`);
}

export async function getForgeAssignment(id: string): Promise<ForgeAssignment> {
  return apiGet<ForgeAssignment>(`/forge/${encodeURIComponent(id)}`);
}

export async function updateForgeAssignment(
  id: string,
  data: { status?: string; storyboard_notes?: string; published_url?: string; editor_notes?: string },
): Promise<ForgeAssignment> {
  return apiFetch<ForgeAssignment>(`/forge/${encodeURIComponent(id)}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function getForgeTracker(cycleId: string): Promise<ForgeTracker> {
  return apiGet<ForgeTracker>(`/forge/tracker?cycle_id=${encodeURIComponent(cycleId)}`);
}

// Briefs (Problem-Landscape)

export async function createBrief(data: {
  problem_statement: string;
  landscape_criteria: string[];
  steelman_summary: string;
  session_id: string;
  arc_name: string;
}): Promise<ProblemLandscapeBrief> {
  return apiPost<ProblemLandscapeBrief>('/briefs', data);
}

export async function getBrief(briefId: string): Promise<ProblemLandscapeBrief> {
  return apiGet<ProblemLandscapeBrief>(`/briefs/${encodeURIComponent(briefId)}`);
}

export async function updateBrief(
  briefId: string,
  data: { problem_statement?: string; landscape_criteria?: string[]; steelman_summary?: string },
): Promise<ProblemLandscapeBrief> {
  return apiFetch<ProblemLandscapeBrief>(`/briefs/${encodeURIComponent(briefId)}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function lockBrief(
  briefId: string,
  data: { locked_by: string },
): Promise<ProblemLandscapeBrief> {
  return apiPost<ProblemLandscapeBrief>(`/briefs/${encodeURIComponent(briefId)}/lock`, data);
}

// Positions (Lock / Revise)

export async function createPosition(data: {
  text: string;
  arc_number: number;
  session_id: string;
  anti_position_text?: string | null;
  cross_arc_bridge_text?: string | null;
  p1_v1_mapping?: string | null;
}): Promise<unknown> {
  return apiPost('/positions', data);
}

export async function updatePosition(
  positionId: string,
  data: {
    text?: string;
    anti_position_text?: string;
    cross_arc_bridge_text?: string;
    p1_v1_mapping?: string;
  },
): Promise<unknown> {
  return apiFetch(`/positions/${encodeURIComponent(positionId)}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function lockPosition(
  positionId: string,
  data: { locked_by: string },
): Promise<unknown> {
  return apiPost(`/positions/${encodeURIComponent(positionId)}/lock`, data);
}

export async function revisePosition(
  positionId: string,
  data: { trigger_type: string; trigger_id: string },
): Promise<unknown> {
  return apiPost(`/positions/${encodeURIComponent(positionId)}/revise`, data);
}

export async function getPositionVersions(positionId: string): Promise<PositionVersion[]> {
  return apiGet<PositionVersion[]>(`/positions/${encodeURIComponent(positionId)}/versions`);
}

// Live Fire

export async function createLiveFireEntry(data: {
  outcome: string;
  context: string;
  date: string;
  position_id: string;
  objection_pair_id?: string | null;
  reporter_email: string;
  session_id?: string | null;
}): Promise<LiveFireEntry> {
  return apiPost<LiveFireEntry>('/live-fire', data);
}

export async function getLiveFireEntries(params?: {
  position_id?: string;
  outcome?: string;
  date_from?: string;
  date_to?: string;
}): Promise<LiveFireEntry[]> {
  const qs = params ? '?' + new URLSearchParams(
    Object.entries(params).filter(([, v]) => v != null) as [string, string][]
  ).toString() : '';
  return apiGet<LiveFireEntry[]>(`/live-fire${qs}`);
}

export async function getLiveFireMetrics(): Promise<LiveFireMetrics> {
  return apiGet<LiveFireMetrics>('/live-fire/metrics');
}

// Flashes

export async function createFlash(data: {
  title: string;
  description: string;
  position_id: string;
  raised_by_email: string;
}): Promise<Flash> {
  return apiPost<Flash>('/flashes', data);
}

export async function getFlashes(params?: {
  status?: string;
  position_id?: string;
}): Promise<Flash[]> {
  const qs = params ? '?' + new URLSearchParams(
    Object.entries(params).filter(([, v]) => v != null) as [string, string][]
  ).toString() : '';
  return apiGet<Flash[]>(`/flashes${qs}`);
}

export async function getPendingFlashes(): Promise<Flash[]> {
  return apiGet<Flash[]>('/flashes/pending');
}

export async function updateFlash(
  flashId: string,
  data: { status?: string; reviewed_date?: string },
): Promise<Flash> {
  return apiFetch<Flash>(`/flashes/${encodeURIComponent(flashId)}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

// Evidence Vault

export async function getVaultEvidence(params?: {
  arc?: string;
  proposition?: string;
  vault_type?: string;
  date_from?: string;
  date_to?: string;
}): Promise<Evidence[]> {
  const qs = params ? '?' + new URLSearchParams(
    Object.entries(params).filter(([, v]) => v != null) as [string, string][]
  ).toString() : '';
  return apiGet<Evidence[]>(`/evidence-vault${qs}`);
}

// Cycle Engine

export async function getCycles(): Promise<Cycle[]> {
  return apiGet<Cycle[]>('/cycles');
}

export async function getCurrentCycle(): Promise<CycleCurrentResponse> {
  return apiGet<CycleCurrentResponse>('/cycles/current');
}

export async function createCycle(data: {
  number: number;
  start_date: string;
  status?: string;
}): Promise<Cycle> {
  return apiPost<Cycle>('/cycles', data);
}

export async function getCycleSchedule(cycleId: string): Promise<CycleSchedule> {
  return apiGet<CycleSchedule>(`/cycles/${encodeURIComponent(cycleId)}/schedule`);
}

export async function updateSessionAssignment(
  cycleId: string,
  sessionId: string,
  data: { lead_email?: string | null; shadow_email?: string | null },
): Promise<ScheduledSession> {
  return apiFetch<ScheduledSession>(
    `/cycles/${encodeURIComponent(cycleId)}/schedule/${encodeURIComponent(sessionId)}`,
    { method: 'PUT', body: JSON.stringify(data) },
  );
}

export async function getScheduledSession(sessionId: string): Promise<ScheduledSession> {
  return apiGet<ScheduledSession>(`/scheduled-sessions/${encodeURIComponent(sessionId)}`);
}

export { ApiError };
