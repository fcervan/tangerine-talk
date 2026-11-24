"use client";

import { useEffect, useRef, useState } from "react";

import {
  ApiError,
  apiFetch,
  jsonBody,
  type CompleteResult,
  type CurriculumLessonDetail,
  type TutorChatResult,
  type TutorCorrectionResult,
} from "@/lib/api";
import { useI18n } from "./LocaleProvider";

interface Props {
  lessonId: string;
}

export default function LessonPlayer({ lessonId }: Props) {
  const { t } = useI18n();
  const [lesson, setLesson] = useState<CurriculumLessonDetail | null>(null);
  const [index, setIndex] = useState(0);
  const [answer, setAnswer] = useState("");
  const [feedback, setFeedback] = useState<string | null>(null);
  const [correct, setCorrect] = useState<boolean | null>(null);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [listening, setListening] = useState(false);
  const [error, setError] = useState(false);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    let active = true;
    apiFetch<CurriculumLessonDetail>(`/curriculum/lessons/${lessonId}`)
      .then((data) => {
        if (active) setLesson(data);
      })
      .catch(() => {
        if (active) setError(true);
      });
    return () => {
      active = false;
    };
  }, [lessonId]);

  const exercise = lesson?.exercises[index] ?? null;
  const total = lesson?.exercises.length ?? 0;
  const isLast = index >= total - 1;

  function speak(text: string) {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.speak(utterance);
  }

  function startListening() {
    const SR =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition;
    if (!SR) {
      setNotice("Reconhecimento de voz não disponível neste navegador.");
      return;
    }
    const recognition = new SR();
    recognition.lang = lesson?.items[0]?.gloss_locale ?? "es-ES";
    recognition.interimResults = false;
    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setAnswer(transcript);
      setListening(false);
    };
    recognition.onerror = () => setListening(false);
    recognition.onend = () => setListening(false);
    recognitionRef.current = recognition;
    setListening(true);
    recognition.start();
  }

  async function check() {
    if (!exercise) return;
    setBusy(true);
    setError(false);
    try {
      if (exercise.type === "multiple_choice") {
        const ok = answer.trim().toLowerCase() === exercise.answer.trim().toLowerCase();
        setCorrect(ok);
        setFeedback(ok ? "Correto!" : `Resposta esperada: ${exercise.answer}`);
      } else {
        const result = await apiFetch<TutorCorrectionResult>("/tutor/correct", {
          method: "POST",
          body: jsonBody({
            expected: exercise.answer,
            answer: answer.trim() || "(vazio)",
            context: exercise.prompt,
          }),
        });
        setCorrect(result.correct);
        setFeedback(result.feedback || (result.correct ? "Correto!" : "Tente de novo."));
        if (!result.ok) setError(true);
      }
    } catch (err) {
      if (err instanceof ApiError) {
        setNotice(err.message);
      } else {
        setError(true);
      }
    } finally {
      setBusy(false);
    }
  }

  async function hint() {
    if (!exercise) return;
    setBusy(true);
    try {
      const result = await apiFetch<TutorChatResult>("/tutor/chat", {
        method: "POST",
        body: jsonBody({
          task: "feedback",
          messages: [
            {
              role: "system",
              content:
                "Você é um tutor de idiomas. Dê uma dica curta, sem revelar a resposta, no idioma da interface.",
            },
            {
              role: "user",
              content: `Exercício: ${exercise.prompt}\nResposta esperada (não revele): ${exercise.answer}`,
            },
          ],
        }),
      });
      setNotice(result.content || result.message);
    } catch {
      setError(true);
    } finally {
      setBusy(false);
    }
  }

  async function finish() {
    if (!lesson) return;
    setBusy(true);
    try {
      const result = await apiFetch<CompleteResult>(
        `/curriculum/lessons/${lesson.id}/complete`,
        { method: "POST", body: jsonBody({}) },
      );
      setNotice(
        result.status === "completed"
          ? `Lição concluída! +${result.xp_earned} XP.`
          : "Esta lição já estava concluída.",
      );
    } catch {
      setError(true);
    } finally {
      setBusy(false);
    }
  }

  function next() {
    setAnswer("");
    setFeedback(null);
    setCorrect(null);
    setIndex((i) => i + 1);
  }

  if (error && !lesson) {
    return <p className="text-sm text-red-700">{t("curriculum.error")}</p>;
  }
  if (!lesson) {
    return <p className="text-sm text-body">{t("common.loading")}</p>;
  }

  return (
    <div className="space-y-6">
      <header>
        <p className="eyebrow">Tangerine Talk</p>
        <h1 className="h2 mt-2">{lesson.title}</h1>
        <p className="mt-2 text-sm text-body">
          Exercício {Math.min(index + 1, total)} de {total}
        </p>
      </header>

      {exercise && (
        <section className="card p-5 sm:p-6">
          <p className="text-[11px] font-semibold uppercase tracking-wide text-tangerine-dark">
            {exercise.type}
          </p>
          <p className="mt-2 text-lg font-medium text-ink">{exercise.prompt}</p>
          {exercise.options && (
            <div className="mt-4 grid gap-2 sm:grid-cols-2">
              {exercise.options.map((opt) => (
                <button
                  key={opt}
                  type="button"
                  onClick={() => setAnswer(opt)}
                  className={`rounded-2xl border px-4 py-3 text-sm transition ${
                    answer === opt
                      ? "border-tangerine bg-tangerine-tint text-ink"
                      : "border-line bg-white text-body hover:border-tangerine"
                  }`}
                >
                  {opt}
                </button>
              ))}
            </div>
          )}
          {!exercise.options && (
            <textarea
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              rows={3}
              className="mt-4 w-full rounded-2xl border border-line bg-white px-4 py-3 text-sm text-ink focus:border-tangerine focus:outline-none"
              placeholder="Sua resposta…"
            />
          )}

          <div className="mt-4 flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => speak(exercise.prompt)}
              className="rounded-pill border border-line px-4 py-2 text-xs font-medium text-body hover:border-tangerine"
            >
              🔊 Ouvir
            </button>
            <button
              type="button"
              onClick={startListening}
              disabled={listening}
              className="rounded-pill border border-line px-4 py-2 text-xs font-medium text-body hover:border-tangerine disabled:opacity-60"
            >
              {listening ? "Ouvindo…" : "🎤 Falar"}
            </button>
            <button
              type="button"
              onClick={() => void check()}
              disabled={busy}
              className="rounded-pill bg-tangerine px-5 py-2 text-sm font-semibold text-white hover:bg-tangerine-dark disabled:opacity-60"
            >
              {busy ? "Verificando…" : "Verificar"}
            </button>
            <button
              type="button"
              onClick={() => void hint()}
              disabled={busy}
              className="rounded-pill border border-line px-4 py-2 text-xs font-medium text-body hover:border-tangerine disabled:opacity-60"
            >
              💡 Dica
            </button>
          </div>

          {feedback && (
            <p
              className={`mt-4 rounded-xl px-4 py-3 text-sm ${
                correct ? "bg-emerald-50 text-emerald-700" : "bg-red-50 text-red-700"
              }`}
            >
              {feedback}
            </p>
          )}
          {notice && (
            <p className="mt-4 rounded-xl bg-mist px-4 py-3 text-sm text-body">{notice}</p>
          )}
        </section>
      )}

      <div className="flex flex-wrap gap-2">
        {!isLast && (
          <button
            type="button"
            onClick={next}
            className="rounded-pill bg-tangerine px-5 py-2 text-sm font-semibold text-white hover:bg-tangerine-dark"
          >
            Próximo
          </button>
        )}
        {isLast && (
          <button
            type="button"
            onClick={() => void finish()}
            disabled={busy}
            className="rounded-pill bg-tangerine px-5 py-2 text-sm font-semibold text-white hover:bg-tangerine-dark disabled:opacity-60"
          >
            {busy ? "Registrando…" : "Concluir lição"}
          </button>
        )}
        <a
          href="/curriculum"
          className="rounded-pill border border-line px-5 py-2 text-sm font-medium text-body hover:border-tangerine"
        >
          Voltar à trilha
        </a>
      </div>
    </div>
  );
}
