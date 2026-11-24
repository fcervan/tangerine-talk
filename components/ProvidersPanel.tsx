"use client";

import { useEffect, useMemo, useState, type FormEvent } from "react";

import {
  ApiError,
  apiFetch,
  jsonBody,
  type ProviderCatalogItem,
  type ProviderCredential,
  type ProviderList,
  type ProviderTestResult,
} from "@/lib/api";
import type { TranslationKey } from "@/lib/i18n";

import { useI18n } from "./LocaleProvider";

function errorKey(err: unknown): TranslationKey {
  if (err instanceof ApiError) {
    if (err.status === 409) return "providers.errors.duplicate";
    if (err.status === 404) return "providers.errors.notFound";
    if (err.status === 422) return "providers.errors.invalid";
  }
  return "providers.errors.generic";
}

export default function ProvidersPanel() {
  const { t, locale } = useI18n();
  const [data, setData] = useState<ProviderList | null>(null);
  const [selected, setSelected] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [model, setModel] = useState("");
  const [baseUrl, setBaseUrl] = useState("");
  const [busy, setBusy] = useState(false);
  const [testing, setTesting] = useState("");
  const [error, setError] = useState<TranslationKey | null>(null);
  const [results, setResults] = useState<Record<string, ProviderTestResult>>({});

  const available = useMemo<ProviderCatalogItem[]>(
    () =>
      data?.catalog.filter(
        (item) => !data.items.some((row) => row.provider === item.slug),
      ) ?? [],
    [data],
  );
  const selectedSpec = available.find((item) => item.slug === selected) ?? null;

  useEffect(() => {
    let active = true;
    apiFetch<ProviderList>("/me/providers")
      .then((value) => {
        if (active) setData(value);
      })
      .catch((err: unknown) => {
        if (active) setError(errorKey(err));
      });
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    if (available.length === 0) {
      setSelected("");
    } else if (!available.some((item) => item.slug === selected)) {
      setSelected(available[0].slug);
    }
  }, [available, selected]);

  async function reload() {
    setData(await apiFetch<ProviderList>("/me/providers"));
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedSpec) return;
    setBusy(true);
    setError(null);
    try {
      await apiFetch("/me/providers", {
        method: "POST",
        body: jsonBody({
          provider: selectedSpec.slug,
          api_key: apiKey || undefined,
          model: model || undefined,
          base_url: baseUrl || undefined,
        }),
      });
      setApiKey("");
      setModel("");
      setBaseUrl("");
      await reload();
    } catch (err) {
      setError(errorKey(err));
    } finally {
      setBusy(false);
    }
  }

  async function testCredential(provider: string) {
    setTesting(provider);
    setError(null);
    try {
      const result = await apiFetch<ProviderTestResult>(
        `/me/providers/${provider}/test`,
        { method: "POST" },
      );
      setResults((current) => ({ ...current, [provider]: result }));
    } catch (err) {
      setError(errorKey(err));
    } finally {
      setTesting("");
    }
  }

  async function toggle(row: ProviderCredential) {
    setError(null);
    try {
      await apiFetch(`/me/providers/${row.provider}`, {
        method: "PATCH",
        body: jsonBody({ is_active: !row.is_active }),
      });
      await reload();
    } catch (err) {
      setError(errorKey(err));
    }
  }

  async function remove(provider: string) {
    setError(null);
    try {
      await apiFetch(`/me/providers/${provider}`, { method: "DELETE" });
      setResults((current) => {
        const next = { ...current };
        delete next[provider];
        return next;
      });
      await reload();
    } catch (err) {
      setError(errorKey(err));
    }
  }

  const fieldClass =
    "mt-1 w-full rounded-xl border border-line bg-white px-4 py-2 text-sm text-ink " +
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-tangerine";
  const buttonClass =
    "rounded-pill bg-tangerine px-5 py-2 text-sm font-semibold text-white transition " +
    "hover:bg-tangerine-dark focus-visible:outline-none focus-visible:ring-2 " +
    "focus-visible:ring-tangerine focus-visible:ring-offset-2 disabled:opacity-60";
  const secondaryClass =
    "rounded-pill border border-line px-4 py-2 text-xs font-medium text-body transition " +
    "hover:border-tangerine focus-visible:outline-none focus-visible:ring-2 " +
    "focus-visible:ring-tangerine";

  return (
    <>
      <p className="eyebrow">Tangerine Talk</p>
      <h1 className="h2 mt-2">{t("providers.title")}</h1>
      <p className="mt-3 text-sm text-body">{t("providers.subtitle")}</p>
      <p className="mt-1 text-xs text-body">{t("providers.privacy")}</p>

      {error && (
        <p role="alert" className="mt-5 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">
          {t(error)}
        </p>
      )}

      {data === null ? (
        <p className="mt-8 text-sm text-body">{t("common.loading")}</p>
      ) : (
        <>
          {data.offline_mode && (
            <p className="mt-5 rounded-xl bg-tangerine-soft px-4 py-3 text-sm text-ink">
              {t("providers.offline")}
            </p>
          )}

          <section className="card mt-8 p-6 sm:p-8">
            <h2 className="text-lg font-semibold text-ink">{t("providers.catalogTitle")}</h2>
            {available.length === 0 ? (
              <p className="mt-4 text-sm text-body">{t("providers.allConfigured")}</p>
            ) : (
              <form onSubmit={(event) => void submit(event)} className="mt-5 grid gap-4">
                <div>
                  <label htmlFor="provider-slug" className="text-xs font-medium text-body">
                    {t("providers.selectProvider")}
                  </label>
                  <select
                    id="provider-slug"
                    value={selected}
                    onChange={(event) => setSelected(event.target.value)}
                    className={fieldClass}
                  >
                    {available.map((item) => (
                      <option key={item.slug} value={item.slug}>
                        {item.label}
                      </option>
                    ))}
                  </select>
                </div>

                {selectedSpec?.needs_key && (
                  <div>
                    <label htmlFor="provider-key" className="text-xs font-medium text-body">
                      {t("providers.key")}
                    </label>
                    <input
                      id="provider-key"
                      type="password"
                      autoComplete="off"
                      required
                      maxLength={512}
                      value={apiKey}
                      onChange={(event) => setApiKey(event.target.value)}
                      className={fieldClass}
                    />
                    <p className="mt-1 text-xs text-body">{t("providers.keyHelp")}</p>
                    {selectedSpec.key_url && (
                      <a
                        href={selectedSpec.key_url}
                        target="_blank"
                        rel="noreferrer"
                        className="mt-1 inline-block text-xs font-medium text-tangerine-dark underline"
                      >
                        {t("providers.getKey")}
                      </a>
                    )}
                  </div>
                )}

                {selectedSpec && !selectedSpec.needs_key && (
                  <p className="text-xs text-body">{t("providers.localHint")}</p>
                )}

                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <label htmlFor="provider-model" className="text-xs font-medium text-body">
                      {t("providers.model")}
                    </label>
                    <input
                      id="provider-model"
                      maxLength={120}
                      placeholder={selectedSpec?.default_model ?? ""}
                      value={model}
                      onChange={(event) => setModel(event.target.value)}
                      className={fieldClass}
                    />
                  </div>
                  <div>
                    <label htmlFor="provider-url" className="text-xs font-medium text-body">
                      {t("providers.baseUrl")}
                    </label>
                    <input
                      id="provider-url"
                      placeholder={selectedSpec?.cloud ? undefined : "http://127.0.0.1:11434/v1"}
                      value={baseUrl}
                      onChange={(event) => setBaseUrl(event.target.value)}
                      className={fieldClass}
                    />
                  </div>
                </div>

                <div>
                  <button type="submit" disabled={busy || !selectedSpec} className={buttonClass}>
                    {busy ? t("providers.saving") : t("providers.save")}
                  </button>
                </div>
              </form>
            )}
          </section>

          <section className="mt-8">
            <h2 className="text-lg font-semibold text-ink">{t("providers.configuredTitle")}</h2>
            {data.items.length === 0 ? (
              <p className="mt-4 text-sm text-body">{t("providers.empty")}</p>
            ) : (
              <ul className="mt-4 grid gap-4">
                {data.items.map((row) => {
                  const result = results[row.provider];
                  return (
                    <li key={row.id} className="card p-5 sm:p-6">
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <div>
                          <p className="font-semibold text-ink">
                            {row.label}
                            <span
                              className={`ml-2 rounded-pill px-2 py-0.5 text-[11px] font-medium ${
                                row.is_active
                                  ? "bg-emerald-50 text-emerald-700"
                                  : "bg-mist text-body"
                              }`}
                            >
                              {t(row.is_active ? "providers.active" : "providers.inactive")}
                            </span>
                          </p>
                          <p className="mt-1 text-xs text-body">
                            {row.key_hint ?? `${t("providers.baseUrl")}: ${row.base_url}`} ·{" "}
                            {row.model}
                          </p>
                          <p className="mt-1 text-xs text-body">
                            {t("providers.lastTested")}:{" "}
                            {row.last_tested_at
                              ? new Intl.DateTimeFormat(locale).format(new Date(row.last_tested_at))
                              : t("providers.neverTested")}
                          </p>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          <button
                            type="button"
                            onClick={() => void testCredential(row.provider)}
                            disabled={testing === row.provider}
                            className={secondaryClass}
                          >
                            {testing === row.provider
                              ? t("providers.testing")
                              : t("providers.test")}
                          </button>
                          <button
                            type="button"
                            onClick={() => void toggle(row)}
                            className={secondaryClass}
                          >
                            {t(row.is_active ? "providers.deactivate" : "providers.activate")}
                          </button>
                          <button
                            type="button"
                            onClick={() => void remove(row.provider)}
                            className={secondaryClass}
                          >
                            {t("providers.remove")}
                          </button>
                        </div>
                      </div>
                      {result && (
                        <p
                          aria-live="polite"
                          className={`mt-3 text-xs ${result.ok ? "text-emerald-700" : "text-red-700"}`}
                        >
                          {t(`providers.status.${result.status}` as TranslationKey)}
                        </p>
                      )}
                    </li>
                  );
                })}
              </ul>
            )}
          </section>

          <section className="mt-8 rounded-2xl border border-line bg-white px-5 py-5">
            <h2 className="text-sm font-semibold text-ink">{t("providers.fallbackTitle")}</h2>
            <p className="mt-1 text-xs text-body">{t("providers.fallbackHelp")}</p>
            <ol className="mt-3 flex flex-wrap gap-2 text-xs text-body">
              {data.fallback_order
                .filter((slug) => data.items.some((row) => row.provider === slug))
                .map((slug, index) => (
                  <li key={slug} className="rounded-pill bg-mist px-3 py-1">
                    {index + 1}. {slug}
                  </li>
                ))}
            </ol>
          </section>
        </>
      )}
    </>
  );
}
