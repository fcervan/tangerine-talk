"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { apiFetch, jsonBody, type OnboardingResult } from "@/lib/api";
import {
  AVAILABLE_LOCALES,
  baseLanguage,
  isValidLocale,
  normalizeLocale,
  type TranslationKey,
} from "@/lib/i18n";

import { useI18n } from "./LocaleProvider";

const LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"] as const;
const TARGET_SUGGESTIONS = ["ja-JP", "es-ES", "fr-FR", "de-DE", "ko-KR", "ar-SA"] as const;
const TOTAL_STEPS = 3;

const inputClass =
  "mt-1.5 w-full rounded-xl border border-line bg-white px-4 py-3 text-sm text-ink placeholder:text-body/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tangerine";

export default function OnboardingWizard() {
  const { t, locale, setLocale } = useI18n();
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [uiLanguage, setUiLanguage] = useState(() => normalizeLocale(locale));
  const [customUi, setCustomUi] = useState("");
  const [targetLanguage, setTargetLanguage] = useState("");
  const [level, setLevel] = useState<(typeof LEVELS)[number]>("A1");
  const [goal, setGoal] = useState(15);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const effectiveUi = customUi.trim() ? normalizeLocale(customUi) : uiLanguage;
  const monolingual =
    isValidLocale(targetLanguage) &&
    baseLanguage(effectiveUi) === baseLanguage(normalizeLocale(targetLanguage));

  function advance() {
    setError(null);
    if (step === 1 && !isValidLocale(targetLanguage)) {
      setError(t("onboarding.targetRequired"));
      return;
    }
    if (step === 0 && customUi.trim() && !isValidLocale(customUi)) {
      setError(t("onboarding.invalidLocale"));
      return;
    }
    setStep((current) => Math.min(current + 1, TOTAL_STEPS - 1));
  }

  async function finish() {
    setBusy(true);
    setError(null);
    try {
      const target = normalizeLocale(targetLanguage);
      await apiFetch<OnboardingResult>("/me/onboarding", {
        method: "POST",
        body: jsonBody({
          ui_language: effectiveUi,
          target_language: target,
          level,
          daily_goal_minutes: goal,
        }),
      });
      await setLocale(effectiveUi);
      router.push("/app");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : t("common.genericError"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="card w-full max-w-xl p-7 sm:p-9">
      <p className="eyebrow">Tangerine Talk</p>
      <h1 className="mt-2 text-3xl font-bold tracking-tight text-ink">
        {t("onboarding.title")}
      </h1>
      <p className="mt-2 text-sm text-body">{t("onboarding.subtitle")}</p>

      <div className="mt-6 flex items-center justify-between text-xs font-medium text-body">
        <span>{t("onboarding.step", { current: step + 1, total: TOTAL_STEPS })}</span>
        <span>{Math.round(((step + 1) / TOTAL_STEPS) * 100)}%</span>
      </div>
      <div
        className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-mist"
        role="progressbar"
        aria-valuenow={step + 1}
        aria-valuemin={1}
        aria-valuemax={TOTAL_STEPS}
      >
        <div
          className="h-full rounded-full bg-tangerine"
          style={{ width: `${((step + 1) / TOTAL_STEPS) * 100}%` }}
        />
      </div>

      {step === 0 ? (
        <div className="mt-7">
          <h2 className="text-lg font-semibold text-ink">{t("onboarding.interfaceTitle")}</h2>
          <p className="mt-1 text-sm text-body">{t("onboarding.interfaceHelp")}</p>
          <div className="mt-4 flex flex-wrap gap-2">
            {AVAILABLE_LOCALES.map((code) => (
              <button
                key={code}
                type="button"
                aria-pressed={!customUi.trim() && uiLanguage === code}
                onClick={() => {
                  setUiLanguage(code);
                  setCustomUi("");
                }}
                className={`rounded-pill border px-4 py-2 text-sm font-medium transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tangerine ${
                  !customUi.trim() && uiLanguage === code
                    ? "border-tangerine bg-tangerine-tint text-tangerine-dark"
                    : "border-line bg-white text-body hover:border-tangerine"
                }`}
              >
                {t(`locale.${code}` as TranslationKey)}
              </button>
            ))}
          </div>
          <label htmlFor="custom-ui" className="mt-5 block text-sm font-medium text-ink">
            {t("onboarding.otherLocale")}
          </label>
          <input
            id="custom-ui"
            value={customUi}
            onChange={(event) => setCustomUi(event.target.value)}
            placeholder={t("onboarding.otherLocaleHelp")}
            className={inputClass}
          />
        </div>
      ) : null}

      {step === 1 ? (
        <div className="mt-7">
          <h2 className="text-lg font-semibold text-ink">{t("onboarding.targetTitle")}</h2>
          <p className="mt-1 text-sm text-body">{t("onboarding.targetHelp")}</p>
          <label htmlFor="target-language" className="mt-4 block text-sm font-medium text-ink">
            {t("onboarding.targetLabel")}
          </label>
          <input
            id="target-language"
            list="target-suggestions"
            value={targetLanguage}
            onChange={(event) => setTargetLanguage(event.target.value)}
            placeholder="ja-JP"
            className={inputClass}
          />
          <datalist id="target-suggestions">
            {TARGET_SUGGESTIONS.map((code) => (
              <option key={code} value={code} />
            ))}
          </datalist>
          <p className="mt-1.5 text-xs text-body">{t("onboarding.targetHelpCode")}</p>
        </div>
      ) : null}

      {step === 2 ? (
        <div className="mt-7 space-y-5">
          <div>
            <label htmlFor="level" className="text-sm font-medium text-ink">
              {t("onboarding.levelTitle")}
            </label>
            <select
              id="level"
              value={level}
              onChange={(event) =>
                setLevel(event.target.value as (typeof LEVELS)[number])
              }
              className={inputClass}
            >
              {LEVELS.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="goal" className="text-sm font-medium text-ink">
              {t("onboarding.goalTitle")}
            </label>
            <input
              id="goal"
              type="number"
              min={5}
              max={180}
              value={goal}
              onChange={(event) => setGoal(Number(event.target.value))}
              className={inputClass}
            />
            <p className="mt-1.5 text-xs text-body">{t("onboarding.goalHelp")}</p>
          </div>
          <div className="rounded-2xl bg-tangerine-soft p-4">
            <p className="text-sm font-semibold text-ink">{t("onboarding.modeTitle")}</p>
            <p className="mt-1 text-sm text-body">
              {t(monolingual ? "onboarding.modeMonolingual" : "onboarding.modeBilingual")}
            </p>
          </div>
        </div>
      ) : null}

      {error ? (
        <p role="alert" className="mt-5 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </p>
      ) : null}

      <div className="mt-8 flex items-center justify-between gap-3">
        <button
          type="button"
          onClick={() => {
            setError(null);
            setStep((current) => Math.max(current - 1, 0));
          }}
          disabled={step === 0 || busy}
          className="rounded-pill border border-line px-5 py-2.5 text-sm font-medium text-body transition hover:border-tangerine disabled:opacity-40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tangerine"
        >
          {t("common.back")}
        </button>
        {step < TOTAL_STEPS - 1 ? (
          <button
            type="button"
            onClick={advance}
            className="rounded-pill bg-tangerine px-6 py-2.5 text-sm font-semibold text-white shadow-cta transition hover:bg-tangerine-dark focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tangerine focus-visible:ring-offset-2"
          >
            {t("common.next")}
          </button>
        ) : (
          <button
            type="button"
            onClick={() => void finish()}
            disabled={busy}
            className="rounded-pill bg-tangerine px-6 py-2.5 text-sm font-semibold text-white shadow-cta transition hover:bg-tangerine-dark disabled:opacity-60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tangerine focus-visible:ring-offset-2"
          >
            {busy ? t("onboarding.saving") : t("onboarding.finish")}
          </button>
        )}
      </div>
    </section>
  );
}
