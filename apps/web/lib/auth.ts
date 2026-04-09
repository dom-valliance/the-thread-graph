/**
 * Stub authentication module for local development.
 * Returns a hardcoded dev token. Replace with Azure AD
 * integration before deploying to staging or production.
 */
export function getDevToken(): string {
  return 'dev-token-placeholder';
}

export function getAuthHeaders(): Record<string, string> {
  return {
    Authorization: `Bearer ${getDevToken()}`,
  };
}
