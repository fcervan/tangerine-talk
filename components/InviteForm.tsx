"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";

import { ApiError, apiFetch, jsonBody, type InvitePreview, type User } from "@/lib/api";
import { resolveDictionaryLocale } from "@/lib/i18n";

import { useI18n } from "./LocaleProvider";

const fieldClass =
  "mt-1.5 w-full rounded-xl border border-line bg-white px-4 py-3 text-sm text-ink placeholder:text-body/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tangerine";

export default function InviteForm({ token }: { token: string }) {
  const { t, locale, setLocale } = useI18n();
  const router = useRouter();
  const [preview, setPreview] = useState<InvitePreview | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    let active = true;
    apiFetch<InvitePreview>(`/auth/invite/${encodeURIComponent(token)}`)
      .then((data) => {
        if (active) setPreview(data);
      })
      .catch((cause: unknown) => {
        if (!active) return;
        if (cause instanceof ApiError && cause.status === 404) {
          setLoadError(t("invite.invalid"));
        } else {
          setLoadError(cause instanceof Error ? cause.message : t("common.genericError"));
        }
      });
    return () => {
      active = false;
    };
  }, [token, t]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const user = await apiFetch<User>("/auth/register", {
        method: "POST",
        body: jsonBody({ token, name, password }),
      });
      await setLocale(user.ui_language);
      router.push("/onboarding");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : t("common.genericError"));
    } finally {
      setBusy(false);
    }
  }

  if (loadError) {
    return (
      <section className="card w-full max-w-md p-7 text-center sm:p-9">
        <h1 className="text-2xl font-bold text-ink">{t("invite.title")}</h1>
        <p role="alert" className="mt-4 text-sm text-red-700">
          {loadError}
        </p>
      </section>
    );
  }

  if (!preview) {
    return (
      <section className="card w-full max-w-md p-9 text-center text-sm text-body">
        {t("common.loading")}
      </section>
    );
  }

  return (
    <section className="card w-full max-w-md p-7 sm:p-9">
      <p className="eyebrow">{t("invite.invitedFor")}</p>
      <h1 className="mt-2 text-3xl font-bold tracking-tight text-ink">
        {preview.email}
      </h1>
      <p className="mt-2 text-sm text-body">
        {t("invite.expires")}:{" "}
        {new Intl.DateTimeFormat(resolveDictionaryLocale(locale), {
          dateStyle: "medium",
          timeStyle: "short",
        }).format(new Date(preview.expires_at))}
      </p>

      <form onSubmit={submit} className="mt-7 space-y-5">
        <div>
          <label htmlFor="name" className="text-sm font-medium text-ink">
            {t("invite.name")}
          </label>
          <input
            id="name"
            required
            maxLength={120}
            value={name}
            onChange={(event) => setName(event.target.value)}
            className={fieldClass}
          />
        </div>
        <div>
          <label htmlFor="new-password" className="text-sm font-medium text-ink">
            {t("invite.password")}
          </label>
          <input
            id="new-password"
            type="password"
            autoComplete="new-password"
            required
            minLength={12}
            maxLength={128}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className={fieldClass}
          />
          <p className="mt-1.5 text-xs text-body">{t("invite.passwordHint")}</p>
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
          {busy ? t("invite.submitting") : t("invite.submit")}
        </button>
      </form>
    </section>
  );
}
