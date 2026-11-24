/** Cliente da API: mesma origem (/api/*), cookies httpOnly e refresh automático. */

export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export interface User {
  id: string;
  email: string;
  name: string;
  role: "owner" | "member";
  ui_language: string;
  target_language: string | null;
  onboarding_completed: boolean;
  settings: Record<string, unknown>;
  created_at: string;
}

export interface OnboardingResult extends User {
  exercise_mode: "monolingual" | "bilingual";
}

export interface InvitePreview {
  email: string;
  role: string;
  expires_at: string;
}

export async function apiFetch<T>(
  path: string,
  init: RequestInit = {},
  allowRefresh = true,
): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body !== undefined && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`/api${path}`, {
    ...init,
    headers,
    credentials: "same-origin",
  });

  if (response.status === 401 && allowRefresh && !path.startsWith("/auth/")) {
    const refreshed = await fetch("/api/auth/refresh", {
      method: "POST",
      credentials: "same-origin",
    });
    if (refreshed.ok) return apiFetch<T>(path, init, false);
  }

  if (!response.ok) {
    let detail = "Erro na requisição.";
    try {
      const body: unknown = await response.json();
      if (
        body &&
        typeof body === "object" &&
        "detail" in body &&
        typeof body.detail === "string"
      ) {
        detail = body.detail;
      }
    } catch {
      // Resposta sem JSON: mantém a mensagem genérica.
    }
    throw new ApiError(response.status, detail);
  }

  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

export function jsonBody(value: unknown): string {
  return JSON.stringify(value);
}
