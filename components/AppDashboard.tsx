"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { apiFetch, type User } from "@/lib/api";
import { baseLanguage, type TranslationKey } from "@/lib/i18n";

import { useI18n } from "./LocaleProvider";

export default function AppDashboard() {
  const { t, locale, setLocale } = useI18n();
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let active = true;
    apiFetch<User>("/me")
      .then((data) => {
        if (!active) return;
        if (!data.onboarding_completed) {
          router.push("/onboarding");
          return;
        }
        setUser(data);
        if (data.ui_language !== locale) void setLocale(data.ui_language);
      })
      .catch(() => {
        if (active) setFailed(true);
      });
    return () => {
      active = false;
    };
  }, [locale, router, setLocale]);

  if (failed) {
    return (
      <section className="card p-8 text-center">
        <p className="text-sm text-red-700">{t("common.genericError")}</p>
        <button
          type="button"
          onClick={() => router.push("/login?next=/app")}
          className="mt-4 rounded-pill bg-tangerine px-5 py-2 text-sm font-semibold text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tangerine"
        >
          {t("login.submit")}
        </button>
      </section>
    );
  }

  if (!user) {
    return <p className="text-sm text-body">{t("common.loading")}</p>;
  }

  const monolingual =
    user.target_language !== null &&
    baseLanguage(user.ui_language) === baseLanguage(user.target_language);
  const level =
    typeof user.settings.level === "string" ? user.settings.level : t("app.notSet");
  const goal = Number(user.settings.daily_goal_minutes ?? 0);

  const rows: Array<{ label: string; value: string }> = [
    {
      label: t("app.interfaceLanguage"),
      value: t(`locale.${user.ui_language}` as TranslationKey).startsWith("locale.")
        ? user.ui_language
        : t(`locale.${user.ui_language}` as TranslationKey),
    },
    { label: t("app.targetLanguage"), value: user.target_language ?? t("app.notSet") },
    {
      label: t("app.mode"),
      value: t(monolingual ? "app.monolingual" : "app.bilingual"),
    },
    { label: t("app.level"), value: level },
    {
      label: t("app.dailyGoal"),
      value: goal > 0 ? `${goal} ${t("app.minutes")}` : t("app.notSet"),
    },
  ];

  async function logout() {
    try {
      await apiFetch("/auth/logout", { method: "POST" });
    } finally {
      router.push("/login");
    }
  }

  return (
    <>
      <p className="eyebrow">Tangerine Talk</p>
      <h1 className="h2 mt-2">{t("app.title")}</h1>
      <p className="mt-3 text-sm text-body">{t("app.subtitle")}</p>

      <section className="card mt-8 p-6 sm:p-8">
        <h2 className="text-lg font-semibold text-ink">{t("app.profile")}</h2>
        <dl className="mt-5 grid gap-4 sm:grid-cols-2">
          {rows.map((row) => (
            <div key={row.label} className="rounded-2xl bg-mist px-4 py-3">
              <dt className="text-xs font-medium uppercase tracking-wide text-body">
                {row.label}
              </dt>
              <dd className="mt-1 text-sm font-semibold text-ink">{row.value}</dd>
            </div>
          ))}
        </dl>
      </section>

      <p className="mt-8 rounded-2xl border border-dashed border-line px-5 py-6 text-center text-sm text-body">
        {t("app.comingSoon")}
      </p>

      <div className="mt-8 flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={() => router.push("/curriculum")}
          className="rounded-pill bg-tangerine px-5 py-2 text-sm font-semibold text-white transition hover:bg-tangerine-dark focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tangerine focus-visible:ring-offset-2"
        >
          {t("curriculum.title")}
        </button>
        <button
          type="button"
          onClick={() => router.push("/onboarding")}
          className="rounded-pill border border-line px-5 py-2 text-sm font-medium text-body transition hover:border-tangerine focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tangerine"
        >
          {t("app.completeOnboarding")}
        </button>
        <button
          type="button"
          onClick={() => router.push("/providers")}
          className="rounded-pill border border-line px-5 py-2 text-sm font-medium text-body transition hover:border-tangerine focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tangerine"
        >
          {t("app.providersLink")}
        </button>
        <button
          type="button"
          onClick={() => void logout()}
          className="rounded-pill bg-ink px-5 py-2 text-sm font-semibold text-white transition hover:bg-black focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tangerine focus-visible:ring-offset-2"
        >
          {t("app.logout")}
        </button>
      </div>
    </>
  );
}
