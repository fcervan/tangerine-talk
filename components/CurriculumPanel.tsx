"use client";

import { useEffect, useState } from "react";

import {
  ApiError,
  apiFetch,
  jsonBody,
  type CompleteResult,
  type Curriculum,
  type CurriculumLessonDetail,
  type Deck,
  type DeckList,
  type User,
} from "@/lib/api";
import type { TranslationKey } from "@/lib/i18n";

import { useI18n } from "./LocaleProvider";

interface Notice {
  text: string;
  ok: boolean;
}

const STATUS_KEY: Record<string, TranslationKey> = {
  locked: "curriculum.locked",
  available: "curriculum.available",
  completed: "curriculum.completed",
};

export default function CurriculumPanel() {
  const { t } = useI18n();
  const [languages, setLanguages] = useState<string[]>([]);
  const [selected, setSelected] = useState("");
  const [curriculum, setCurriculum] = useState<Curriculum | null>(null);
  const [decks, setDecks] = useState<DeckList | null>(null);
  const [lesson, setLesson] = useState<CurriculumLessonDetail | null>(null);
  const [openDeck, setOpenDeck] = useState<Deck | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(false);
  const [notice, setNotice] = useState<Notice | null>(null);

  async function load(target: string) {
    setError(false);
    try {
      const [nextCurriculum, nextDecks] = await Promise.all([
        apiFetch<Curriculum>(`/curriculum?target_language=${encodeURIComponent(target)}`),
        apiFetch<DeckList>(`/decks?target_language=${encodeURIComponent(target)}`),
      ]);
      setCurriculum(nextCurriculum);
      setDecks(nextDecks);
    } catch {
      setError(true);
    }
  }

  useEffect(() => {
    let active = true;
    Promise.all([
      apiFetch<{ languages: string[] }>("/curriculum/languages"),
      apiFetch<User>("/me"),
    ])
      .then(([available, user]) => {
        if (!active) return;
        setLanguages(available.languages);
        const preferred = user.target_language ?? "";
        const initial = available.languages.includes(preferred)
          ? preferred
          : (available.languages[0] ?? "");
        setSelected(initial);
        if (initial) void load(initial);
        else {
          setCurriculum({ target_language: "", level: null, locale: "", units: [] });
          setDecks({ target_language: "", decks: [] });
        }
      })
      .catch(() => {
        if (active) setError(true);
      });
    return () => {
      active = false;
    };
  }, []);

  function choose(target: string) {
    setSelected(target);
    setLesson(null);
    setOpenDeck(null);
    setNotice(null);
    void load(target);
  }

  async function openLesson(id: string) {
    setNotice(null);
    setError(false);
    try {
      setLesson(await apiFetch<CurriculumLessonDetail>(`/curriculum/lessons/${id}`));
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) {
        setNotice({ text: t("curriculum.blocked"), ok: false });
      } else {
        setError(true);
      }
    }
  }

  async function complete() {
    if (lesson === null) return;
    setBusy(true);
    setError(false);
    try {
      const result = await apiFetch<CompleteResult>(
        `/curriculum/lessons/${lesson.id}/complete`,
        { method: "POST", body: jsonBody({}) },
      );
      setNotice({
        text:
          result.status === "completed"
            ? t("curriculum.completedNotice", { xp: result.xp_earned })
            : t("curriculum.alreadyCompleted"),
        ok: true,
      });
      setLesson({ ...lesson, status: "completed" });
      await load(selected);
    } catch {
      setError(true);
    } finally {
      setBusy(false);
    }
  }

  async function showDeck(deck: Deck) {
    setNotice(null);
    if (openDeck?.id === deck.id) {
      setOpenDeck(null);
      return;
    }
    setError(false);
    try {
      setOpenDeck(await apiFetch<Deck>(`/decks/${deck.id}`));
    } catch {
      setError(true);
    }
  }

  const buttonClass =
    "rounded-pill border border-line px-4 py-2 text-xs font-medium text-body transition hover:border-tangerine focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tangerine disabled:opacity-60";

  return (
    <>
      <p className="eyebrow">Tangerine Talk</p>
      <h1 className="h2 mt-2">{t("curriculum.title")}</h1>
      <p className="mt-3 text-sm text-body">{t("curriculum.subtitle")}</p>

      {languages.length > 0 && (
        <div className="mt-6 flex flex-wrap items-center gap-2">
          <span className="mr-1 text-xs font-medium text-body">
            {t("curriculum.languages")}:
          </span>
          {languages.map((language) => (
            <button
              key={language}
              type="button"
              onClick={() => choose(language)}
              className={`rounded-pill px-4 py-1.5 text-xs font-semibold transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tangerine ${
                language === selected
                  ? "bg-tangerine text-white"
                  : "border border-line bg-white text-body hover:border-tangerine"
              }`}
            >
              {language}
            </button>
          ))}
        </div>
      )}

      {error && (
        <p role="alert" className="mt-5 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">
          {t("curriculum.error")}
        </p>
      )}
      {notice && (
        <p
          aria-live="polite"
          className={`mt-5 rounded-xl px-4 py-3 text-sm ${notice.ok ? "bg-emerald-50 text-emerald-700" : "bg-red-50 text-red-700"}`}
        >
          {notice.text}
        </p>
      )}

      {curriculum === null ? (
        <p className="mt-8 text-sm text-body">{t("common.loading")}</p>
      ) : (
        <>
          {curriculum.units.length === 0 ? (
            <p className="mt-8 rounded-2xl border border-dashed border-line px-5 py-6 text-center text-sm text-body">
              {t("curriculum.noContent")}
            </p>
          ) : (
            <section className="mt-8 grid gap-4">
              {curriculum.units.map((unit) => (
                <article key={unit.id} className="card p-5 sm:p-6">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-wide text-tangerine-dark">
                        {unit.level} · {t("curriculum.lessons")}
                      </p>
                      <h2 className="mt-1 text-lg font-semibold text-ink">{unit.title}</h2>
                      {unit.description && (
                        <p className="mt-1 text-xs text-body">{unit.description}</p>
                      )}
                    </div>
                    <span className="rounded-pill bg-mist px-3 py-1 text-[11px] font-medium text-body">
                      {t(STATUS_KEY[unit.status])}
                    </span>
                  </div>

                  <ul className="mt-4 grid gap-2">
                    {unit.lessons.map((item) => (
                      <li
                        key={item.id}
                        className="flex flex-wrap items-center justify-between gap-3 rounded-2xl bg-mist px-4 py-3"
                      >
                        <div>
                          <p className="text-sm font-medium text-ink">{item.title}</p>
                          <p className="mt-0.5 text-xs text-body">
                            {item.exercise_count} {t("curriculum.exercises")} ·{" "}
                            {item.xp_reward} XP · {t(STATUS_KEY[item.status])}
                          </p>
                        </div>
                        <button
                          type="button"
                          onClick={() => void openLesson(item.id)}
                          disabled={item.status === "locked"}
                          className={buttonClass}
                        >
                          {t("curriculum.open")}
                        </button>
                      </li>
                    ))}
                  </ul>
                </article>
              ))}
            </section>
          )}

          {lesson && (
            <section className="card mt-6 p-5 sm:p-6" aria-live="polite">
              <h2 className="text-lg font-semibold text-ink">{lesson.title}</h2>
              <p className="mt-1 text-xs text-body">{t("curriculum.preview")}</p>

              <h3 className="mt-5 text-xs font-semibold uppercase tracking-wide text-body">
                {t("curriculum.items")}
              </h3>
              <ul className="mt-2 grid gap-2 sm:grid-cols-2">
                {lesson.items.map((item) => (
                  <li key={item.id} className="rounded-2xl bg-mist px-4 py-3">
                    <p className="text-sm font-medium text-ink">{item.front_text}</p>
                    <p className="mt-0.5 text-xs text-body">
                      {item.gloss} · {item.gloss_locale}
                    </p>
                  </li>
                ))}
              </ul>

              <h3 className="mt-5 text-xs font-semibold uppercase tracking-wide text-body">
                {t("curriculum.lessons")}
              </h3>
              <ol className="mt-2 grid gap-2">
                {lesson.exercises.map((exercise) => (
                  <li key={exercise.id} className="rounded-2xl border border-line px-4 py-3">
                    <p className="text-[11px] font-medium uppercase tracking-wide text-tangerine-dark">
                      {exercise.type}
                    </p>
                    <p className="mt-1 text-sm text-ink">{exercise.prompt}</p>
                    <p className="mt-0.5 text-xs text-body">
                      {exercise.answer}
                      {exercise.options && ` · ${exercise.options.join(" / ")}`}
                    </p>
                  </li>
                ))}
              </ol>

              <div className="mt-5 flex flex-wrap gap-2">
                <a
                  href={`/lesson/${lesson.id}`}
                  className="rounded-pill bg-tangerine px-5 py-2 text-sm font-semibold text-white transition hover:bg-tangerine-dark focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tangerine"
                >
                  Iniciar lição
                </a>
                <button
                  type="button"
                  onClick={() => void complete()}
                  disabled={busy || lesson.status === "completed"}
                  className={buttonClass}
                >
                  {busy ? t("curriculum.completing") : t("curriculum.complete")}
                </button>
                <button
                  type="button"
                  onClick={() => setLesson(null)}
                  className={buttonClass}
                >
                  {t("curriculum.close")}
                </button>
              </div>
            </section>
          )}

          <section className="mt-10">
            <h2 className="text-lg font-semibold text-ink">{t("curriculum.decks")}</h2>
            {decks === null || decks.decks.length === 0 ? (
              <p className="mt-4 text-sm text-body">{t("curriculum.noDecks")}</p>
            ) : (
              <div className="mt-4 grid gap-4 sm:grid-cols-2">
                {decks.decks.map((deck) => (
                  <article key={deck.id} className="card p-5">
                    <p className="text-xs font-semibold uppercase tracking-wide text-tangerine-dark">
                      {deck.level} · {deck.item_count} {t("curriculum.cards")}
                    </p>
                    <h3 className="mt-1 font-semibold text-ink">{deck.title}</h3>
                    {deck.description && (
                      <p className="mt-1 text-xs text-body">{deck.description}</p>
                    )}
                    <button
                      type="button"
                      onClick={() => void showDeck(deck)}
                      className={`mt-4 ${buttonClass}`}
                    >
                      {openDeck?.id === deck.id
                        ? t("curriculum.hideCards")
                        : t("curriculum.showCards")}
                    </button>
                    {openDeck?.id === deck.id && (
                      <ul className="mt-4 grid gap-2">
                        {(openDeck.items ?? []).map((item) => (
                          <li
                            key={item.id}
                            className="flex flex-wrap justify-between gap-2 rounded-2xl bg-mist px-4 py-2 text-sm"
                          >
                            <span className="text-ink">{item.front_text}</span>
                            <span className="text-body">{item.gloss}</span>
                          </li>
                        ))}
                      </ul>
                    )}
                  </article>
                ))}
              </div>
            )}
          </section>
        </>
      )}
    </>
  );
}
