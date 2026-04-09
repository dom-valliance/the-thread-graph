export interface ApiResponse<T> {
  data: T;
  meta?: Record<string, unknown>;
}

export interface PaginatedResponse<T> {
  data: T[];
  meta: {
    count: number;
    cursor: string | null;
    has_more: boolean;
  };
}

export interface ErrorResponse {
  error: {
    code: string;
    message: string;
  };
}
