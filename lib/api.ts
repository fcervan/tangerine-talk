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

/** Nenhum destes tipos contém a chave cadastrada — só `key_hint`. */
export interface ProviderCatalogItem {
  slug: string;
  label: string;
  capabilities: string[];
  needs_key: boolean;
  cloud: boolean;
  default_model: string;
  key_url: string;
}

export interface ProviderCredential {
  id: string;
  provider: string;
  label: string;
  key_hint: string | null;
  base_url: string;
  model: string;
  capabilities: string[];
  is_active: boolean;
  last_tested_at: string | null;
  last_used_at: string | null;
  last_error: string | null;
  created_at: string;
}

export interface ProviderList {
  items: ProviderCredential[];
  catalog: ProviderCatalogItem[];
  fallback_order: string[];
  offline_mode: boolean;
}

export interface ProviderTestResult {
  provider: string;
  ok: boolean;
  status: "ok" | "invalid_key" | "quota" | "provider_error" | "network";
  message: string;
  latency_ms: number | null;
}

export type LessonStatus = "locked" | "available" | "completed";

export interface CurriculumItem {
  id: string;
  kind: string;
  front_text: string;
  example: string | null;
  gloss: string;
  gloss_locale: string;
}

export interface CurriculumExercise {
  id: string;
  type: string;
  prompt: string;
  answer: string;
  options: string[] | null;
  order_index: number;
}

export interface CurriculumLesson {
  id: string;
  slug: string;
  title: string;
  order_index: number;
  kind: string;
  xp_reward: number;
  status: LessonStatus;
  exercise_count: number;
}

export interface CurriculumLessonDetail extends CurriculumLesson {
  items: CurriculumItem[];
  exercises: CurriculumExercise[];
}

export interface CurriculumUnit {
  id: string;
  target_language: string;
  level: string;
  slug: string;
  title: string;
  description: string | null;
  order_index: number;
  status: LessonStatus;
  lessons: CurriculumLesson[];
  items?: CurriculumItem[];
}

export interface Curriculum {
  target_language: string;
  level: string | null;
  locale: string;
  units: CurriculumUnit[];
}

export interface Deck {
  id: string;
  slug: string;
  title: string;
  description: string | null;
  level: string;
  item_count: number;
  items?: CurriculumItem[];
}

export interface DeckList {
  target_language: string;
  decks: Deck[];
}

export interface CompleteResult {
  lesson_id: string;
  status: "completed" | "already_completed";
  xp_earned: number;
  completed_at: string;
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
