"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { apiFetch, jsonBody } from "@/lib/api";
import {
  normalizeLocale,
  resolveDictionaryLocale,
  translate,
  type TranslationKey,
} from "@/lib/i18n";

interface I18nValue {
  /** Preferência do usuário — pode ser um locale sem dicionário ainda. */
  locale: string;
  /** Locale cujo dicionário está sendo usado de fato. */
  dictionaryLocale: string;
  setLocale: (next: string) => Promise<void>;
  t: (key: TranslationKey, params?: Record<string, string | number>) => string;
}

const I18nContext = createContext<I18nValue | null>(null);

export default function LocaleProvider({
  initialLocale,
  children,
}: {
  initialLocale: string;
  children: ReactNode;
}) {
  const [locale, setLocaleState] = useState(() => normalizeLocale(initialLocale));

  useEffect(() => {
    // Com sessão ativa, o backend é a fonte da verdade. Sem sessão, a landing
    // usa a última escolha local.
    if (document.cookie.includes("tt_access=")) return;
    const saved = window.localStorage.getItem("tt_locale");
    if (saved) setLocaleState(normalizeLocale(saved));
  }, []);

  const setLocale = useCallback(async (next: string) => {
    const normalized = normalizeLocale(next);
    setLocaleState(normalized);
    window.localStorage.setItem("tt_locale", normalized);
    document.cookie = `tt_locale=${normalized}; path=/; max-age=31536000; samesite=lax`;
    try {
      await apiFetch("/me", {
        method: "PATCH",
        body: jsonBody({ ui_language: normalized }),
      });
    } catch {
      // Preferência local já aplicada; sincroniza no próximo login.
    }
  }, []);

  useEffect(() => {
    document.documentElement.lang = resolveDictionaryLocale(locale);
  }, [locale]);

  const value = useMemo<I18nValue>(
    () => ({
      locale,
      dictionaryLocale: resolveDictionaryLocale(locale),
      setLocale,
      t: (key, params) => translate(locale, key, params),
    }),
    [locale, setLocale],
  );

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n(): I18nValue {
  const context = useContext(I18nContext);
  if (!context) throw new Error("useI18n precisa estar dentro de LocaleProvider.");
  return context;
}
