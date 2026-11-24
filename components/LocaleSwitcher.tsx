"use client";

import { AVAILABLE_LOCALES, type TranslationKey } from "@/lib/i18n";

import { useI18n } from "./LocaleProvider";

export default function LocaleSwitcher() {
  const { dictionaryLocale, setLocale, t } = useI18n();
  const available = AVAILABLE_LOCALES as readonly string[];
  const value = available.includes(dictionaryLocale) ? dictionaryLocale : AVAILABLE_LOCALES[0];

  return (
    <div className="flex items-center gap-2">
      <label htmlFor="locale-switcher" className="text-xs font-medium text-body">
        {t("locale.label")}
      </label>
      <select
        id="locale-switcher"
        value={value}
        onChange={(event) => void setLocale(event.target.value)}
        className="rounded-pill border border-line bg-white px-3 py-1.5 text-sm text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tangerine"
      >
        {AVAILABLE_LOCALES.map((code) => (
          <option key={code} value={code}>
            {t(`locale.${code}` as TranslationKey)}
          </option>
        ))}
      </select>
    </div>
  );
}
