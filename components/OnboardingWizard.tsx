"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { apiFetch, jsonBody, type OnboardingResult } from "@/lib/api";
import type { TranslationKey } from "@/lib/i18n";

import { useI18n } from "./LocaleProvider";

const UI_LOCALES = ["pt-BR", "en-US"] as const;
const STUDY_LANGUAGES = [
  "en-US",
  "zh-CN",
  "es-ES",
  "it-IT",
  "fr-FR",
  "de-DE",
  "ko-KR",
  "ja-JP",
  "pt-BR",
] as const;
const TOPICS = [
  "travel",
  "family",
  "work",
  "health",
  "shopping",
  "food",
  "school",
  "technology",
  "leisure",
  "emergencies",
] as const;
const LEVEL_BANDS = ["A1_A2", "B1_B2", "C1_C2", "NONE"] as const;
const TOTAL_STEPS = 5;

const inputClass =
  "mt-1.5 w-full rounded-xl border border-line bg-white px-4 py-3 text-sm text-ink placeholder:text-body/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tangerine";

const chipClass = (active: boolean) =>
  `rounded-pill border px-4 py-2 text-sm font-medium transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tangerine ${
    active
      ? "border-tangerine bg-tangerine-tint text-tangerine-dark"
      : "border-line bg-white text-body hover:border-tangerine"
  }`;

export default function OnboardingWizard() {
  const { t, setLocale } = useI18n();
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [uiLanguage, setUiLanguage] = useState("pt-BR");
  const [studyLanguages, setStudyLanguages] = useState<string[]>([]);
  const [programSource, setProgramSource] = useState<"curriculum" | "topics">("topics");
  const [topics, setTopics] = useState<string[]>([]);
  const [levelBand, setLevelBand] = useState("NONE");
  const [goal, setGoal] = useState(15);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  function toggle(list: string[], value: string, setter: (v: string[]) => void) {
    setter(list.includes(value) ? list.filter((x) => x !== value) : [...list, value]);
  }

  function advance() {
    setError(null);
    if (step === 1 && studyLanguages.length === 0) {
      setError(t("onboarding.studyRequired"));
      return;
    }
    if (step === 2 && programSource === "topics" && topics.length === 0) {
      setError(t("onboarding.topicsRequired"));
      return;
    }
    setStep((c) => Math.min(c + 1, TOTAL_STEPS - 1));
  }

  async function finish() {
    setBusy(true);
    setError(null);
    try {
      await apiFetch<OnboardingResult>("/me/onboarding", {
        method: "POST",
        body: jsonBody({
          ui_language: uiLanguage,
          study_languages: studyLanguages,
          level_band: levelBand,
          program_source: programSource,
          program_topics: topics,
          daily_goal_minutes: goal,
        }),
      });
      await setLocale(uiLanguage);
      router.push("/app");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : t("common.genericError"));
    } finally {
      setBusy(false);
    }
  }

  const levelLabel = (band: string) =>
    band === "NONE" ? t("onboarding.levelNone") : band.replace("_", "/");

  return (
    <section className="card w-full max-w-2xl p-7 sm:p-9">
      <p className="eyebrow">Tangerine Talk</p>
      <h1 className="mt-2 text-3xl font-bold tracking-tight text-ink">
        {t("onboarding.title")}
      </h1>
      <p className="mt-2 text-sm text-body">{t("onboarding.subtitle")}</p>

      <div className="mt-6 flex items-center justify-between text-xs font-medium text-body">
        <span>{t("onboarding.stepLabel", { current: step + 1, total: TOTAL_STEPS })}</span>
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

      {step === 0 && (
        <div className="mt-7">
          <h2 className="text-lg font-semibold text-ink">{t("onboarding.interfaceTitle")}</h2>
          <p className="mt-1 text-sm text-body">{t("onboarding.interfaceHelp")}</p>
          <div className="mt-4 flex flex-wrap gap-2">
            {UI_LOCALES.map((code) => (
              <button
                key={code}
                type="button"
                aria-pressed={uiLanguage === code}
                onClick={() => setUiLanguage(code)}
                className={chipClass(uiLanguage === code)}
              >
                {code === "pt-BR"
                  ? t("onboarding.interfaceOptionBr")
                  : t("onboarding.interfaceOptionEn")}
              </button>
            ))}
          </div>
        </div>
      )}

      {step === 1 && (
        <div className="mt-7">
          <h2 className="text-lg font-semibold text-ink">{t("onboarding.studyTitle")}</h2>
          <p className="mt-1 text-sm text-body">{t("onboarding.studyHelp")}</p>
          <div className="mt-4 flex flex-wrap gap-2">
            {STUDY_LANGUAGES.map((code) => (
              <button
                key={code}
                type="button"
                aria-pressed={studyLanguages.includes(code)}
                onClick={() => toggle(studyLanguages, code, setStudyLanguages)}
                className={chipClass(studyLanguages.includes(code))}
              >
                {t(`language.${code}` as TranslationKey)}
              </button>
            ))}
          </div>
        </div>
      )}

      {step === 2 && (
        <div className="mt-7 space-y-5">
          <div>
            <h2 className="text-lg font-semibold text-ink">{t("onboarding.programTitle")}</h2>
            <p className="mt-1 text-sm text-body">{t("onboarding.programHelp")}</p>
            <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
              <button
                type="button"
                onClick={() => setProgramSource("topics")}
                className={`card p-4 text-left transition ${
                  programSource === "topics" ? "ring-2 ring-tangerine" : ""
                }`}
              >
                <p className="font-semibold text-ink">{t("onboarding.programTopics")}</p>
                <p className="mt-1 text-xs text-body">{t("onboarding.programTopicsHelp")}</p>
              </button>
              <button
                type="button"
                onClick={() => setProgramSource("curriculum")}
                className={`card p-4 text-left transition ${
                  programSource === "curriculum" ? "ring-2 ring-tangerine" : ""
                }`}
              >
                <p className="font-semibold text-ink">{t("onboarding.programCurriculum")}</p>
                <p className="mt-1 text-xs text-body">{t("onboarding.programCurriculumHelp")}</p>
              </button>
            </div>
          </div>
          {programSource === "topics" && (
            <div>
              <p className="text-sm font-medium text-ink">{t("onboarding.topicsLabel")}</p>
              <div className="mt-2 flex flex-wrap gap-2">
                {TOPICS.map((topic) => (
                  <button
                    key={topic}
                    type="button"
                    aria-pressed={topics.includes(topic)}
                    onClick={() => toggle(topics, topic, setTopics)}
                    className={chipClass(topics.includes(topic))}
                  >
                    {t(`topic.${topic}` as TranslationKey)}
                  </button>
                ))}
              </div>
            </div>
          )}
          {programSource === "curriculum" && (
            <div className="rounded-2xl bg-tangerine-soft p-4 text-sm text-body">
              {t("onboarding.curriculumSoon")}
            </div>
          )}
        </div>
      )}

      {step === 3 && (
        <div className="mt-7">
          <h2 className="text-lg font-semibold text-ink">{t("onboarding.levelTitle")}</h2>
          <div className="mt-4 flex flex-wrap gap-2">
            {LEVEL_BANDS.map((band) => (
              <button
                key={band}
                type="button"
                aria-pressed={levelBand === band}
                onClick={() => setLevelBand(band)}
                className={chipClass(levelBand === band)}
              >
                {levelLabel(band)}
              </button>
            ))}
          </div>
        </div>
      )}

      {step === 4 && (
        <div className="mt-7 space-y-5">
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
            <p className="text-sm font-semibold text-ink">{t("onboarding.summaryTitle")}</p>
            <p className="mt-1 text-sm text-body">
              {t("onboarding.summary", {
                ui: uiLanguage,
                languages: studyLanguages
                  .map((code) => t(`language.${code}` as TranslationKey))
                  .join(", "),
                level: levelLabel(levelBand),
                source:
                  programSource === "topics"
                    ? t("onboarding.sourceTopics")
                    : t("onboarding.sourceCurriculum"),
              })}
            </p>
          </div>
        </div>
      )}

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
            setStep((c) => Math.max(c - 1, 0));
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
