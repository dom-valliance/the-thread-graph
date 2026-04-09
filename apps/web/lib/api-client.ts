import type { ApiResponse } from '@/types/api';
import type { Arc, ArcDetail, ThemeBridge } from '@/types/entities';

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

export async function getArcBridges(): Promise<ThemeBridge[]> {
  return apiGet<ThemeBridge[]>('/arcs/bridges');
}

export { ApiError };
