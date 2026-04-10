import type { ApiResponse, PaginatedResponse } from '@/types/api';
import type {
  Arc,
  ArcBridge,
  ArcDetail,
  Bookmark,
  BookmarkEdge,
  CrossArcBridge,
  EvidenceTrailResponse,
  ObjectionPairWithContext,
  UnconnectedPosition,
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

export { ApiError };
