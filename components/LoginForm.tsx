"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

import { apiFetch, jsonBody, type User } from "@/lib/api";

import { useI18n } from "./LocaleProvider";

const fieldClass =
  "mt-1.5 w-full rounded-xl border border-line bg-white px-4 py-3 text-sm text-ink placeholder:text-body/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tangerine";

export default function LoginForm({ next }: { next?: string }) {
  const { t, setLocale } = useI18n();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const user = await apiFetch<User>("/auth/login", {
        method: "POST",
        body: jsonBody({ email, password }),
      });
      await setLocale(user.ui_language);
      const destination =
        next && next.startsWith("/") && !next.startsWith("//") ? next : "/app";
      router.push(user.onboarding_completed ? destination : "/onboarding");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : t("common.genericError"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="card w-full max-w-md p-7 sm:p-9">
      <p className="eyebrow">Tangerine Talk</p>
      <h1 className="mt-2 text-3xl font-bold tracking-tight text-ink">{t("login.title")}</h1>
      <p className="mt-2 text-sm text-body">{t("login.subtitle")}</p>

      <form onSubmit={submit} className="mt-7 space-y-5">
        <div>
          <label htmlFor="email" className="text-sm font-medium text-ink">
            {t("login.email")}
          </label>
          <input
            id="email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className={fieldClass}
          />
        </div>
        <div>
          <label htmlFor="password" className="text-sm font-medium text-ink">
            {t("login.password")}
          </label>
          <input
            id="password"
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className={fieldClass}
          />
        </div>

        {error ? (
          <p role="alert" className="rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </p>
        ) : null}

        <button
          type="submit"
          disabled={busy}
          className="w-full rounded-pill bg-tangerine px-6 py-3 text-sm font-semibold text-white shadow-cta transition hover:bg-tangerine-dark disabled:opacity-60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tangerine focus-visible:ring-offset-2"
        >
          {busy ? t("login.submitting") : t("login.submit")}
        </button>
      </form>

      <p className="mt-6 text-center text-xs text-body">
        {t("register.noAccount")}{" "}
        <a href="/cadastro" className="font-medium text-tangerine hover:underline">
          {t("register.registerLink")}
        </a>
      </p>
      <p className="mt-2 text-center text-xs text-body">{t("login.restricted")}</p>
    </section>
  );
}
