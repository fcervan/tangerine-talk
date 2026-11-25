"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

import { apiFetch, jsonBody, type User } from "@/lib/api";

import { useI18n } from "./LocaleProvider";

const fieldClass =
  "mt-1.5 w-full rounded-xl border border-line bg-white px-4 py-3 text-sm text-ink placeholder:text-body/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tangerine";

const MIN_PASSWORD = 12;

export default function RegisterForm({ next }: { next?: string }) {
  const { t, setLocale } = useI18n();
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    if (password.length < MIN_PASSWORD) {
      setError(t("register.passwordHint"));
      return;
    }
    setBusy(true);
    try {
      const user = await apiFetch<User>("/auth/register-public", {
        method: "POST",
        body: jsonBody({ name, email, password }),
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
      <h1 className="mt-2 text-3xl font-bold tracking-tight text-ink">
        {t("register.title")}
      </h1>
      <p className="mt-2 text-sm text-body">{t("register.subtitle")}</p>

      <form onSubmit={submit} className="mt-7 space-y-5">
        <div>
          <label htmlFor="name" className="text-sm font-medium text-ink">
            {t("register.name")}
          </label>
          <input
            id="name"
            autoComplete="name"
            required
            minLength={2}
            maxLength={120}
            value={name}
            onChange={(event) => setName(event.target.value)}
            className={fieldClass}
          />
        </div>
        <div>
          <label htmlFor="email" className="text-sm font-medium text-ink">
            {t("register.email")}
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
            {t("register.password")}
          </label>
          <input
            id="password"
            type="password"
            autoComplete="new-password"
            required
            minLength={MIN_PASSWORD}
            maxLength={128}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className={fieldClass}
          />
          <p className="mt-1.5 text-xs text-body">{t("register.passwordHint")}</p>
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
          {busy ? t("register.submitting") : t("register.submit")}
        </button>
      </form>

      <p className="mt-6 text-center text-xs text-body">
        {t("register.hasAccount")}{" "}
        <a href="/login" className="font-medium text-tangerine hover:underline">
          {t("register.loginLink")}
        </a>
      </p>
    </section>
  );
}
