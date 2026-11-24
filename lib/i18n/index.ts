import enUS from "./locales/en-US";
import ptBR, { type Dictionary } from "./locales/pt-BR";

/**
 * Dois eixos independentes: `ui_language` escolhe os textos aqui;
 * `target_language` escolhe a frase estudada. Nunca misturar.
 */
export const DEFAULT_LOCALE = "pt-BR";

/** Locales com dicionário. Novos idiomas entram aqui e em `locales/`. */
export const AVAILABLE_LOCALES = ["pt-BR", "en-US"] as const;

export type Locale = string;

const dictionaries: Record<string, Dictionary> = {
  "pt-BR": ptBR,
  "en-US": enUS,
};

type Paths<T, Prefix extends string = ""> = T extends string
  ? Prefix
  : {
      [K in keyof T & string]: Paths<T[K], Prefix extends "" ? K : `${Prefix}.${K}`>;
    }[keyof T & string];

export type TranslationKey = Paths<Dictionary>;

const LOCALE_RE = /^[a-zA-Z]{2,3}(?:-[a-zA-Z]{4,8})?(?:-[a-zA-Z]{2}|-[0-9]{3})?$/;

export function isValidLocale(value: string): boolean {
  return LOCALE_RE.test(value.trim());
}

/** Aceita BCP-47 simples e devolve a forma canônica; inválido cai no padrão. */
export function normalizeLocale(value: string | null | undefined): string {
  const trimmed = (value ?? "").trim();
  if (!LOCALE_RE.test(trimmed)) return DEFAULT_LOCALE;

  const parts = trimmed.split("-");
  parts[0] = parts[0].toLowerCase();
  for (let index = 1; index < parts.length; index += 1) {
    const part = parts[index];
    if (/^\d{3}$/.test(part)) continue;
    parts[index] =
      part.length === 2
        ? part.toUpperCase()
        : part.charAt(0).toUpperCase() + part.slice(1).toLowerCase();
  }
  return parts.join("-");
}

export function baseLanguage(locale: string): string {
  return normalizeLocale(locale).split("-", 1)[0].toLowerCase();
}

/** Dicionário efetivo: exato → mesma base → pt-BR. Nunca cai para o inglês. */
export function resolveDictionaryLocale(locale: string): string {
  const normalized = normalizeLocale(locale);
  if (dictionaries[normalized]) return normalized;
  const base = baseLanguage(normalized);
  const sameBase = Object.keys(dictionaries).find((key) => baseLanguage(key) === base);
  return sameBase ?? DEFAULT_LOCALE;
}

export function translate(
  locale: string,
  key: TranslationKey,
  params?: Record<string, string | number>,
): string {
  const dictionary = dictionaries[resolveDictionaryLocale(locale)] ?? ptBR;
  const raw = key.split(".").reduce<unknown>((current, part) => {
    if (current && typeof current === "object" && part in current) {
      return (current as Record<string, unknown>)[part];
    }
    return undefined;
  }, dictionary);

  let text = typeof raw === "string" ? raw : key;
  if (params) {
    text = text.replace(/\{(\w+)\}/g, (_, name: string) => String(params[name] ?? ""));
  }
  return text;
}
