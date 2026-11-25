import type { Metadata } from "next";
import { cookies } from "next/headers";

import LocaleProvider from "@/components/LocaleProvider";
import {
  DEFAULT_LOCALE,
  normalizeLocale,
  resolveDictionaryLocale,
  translate,
} from "@/lib/i18n";

import "./globals.css";

function currentLocale(): string {
  return resolveDictionaryLocale(
    normalizeLocale(cookies().get("tt_locale")?.value ?? DEFAULT_LOCALE),
  );
}

export function generateMetadata(): Metadata {
  const locale = currentLocale();
  return {
    title: translate(locale, "meta.title"),
    description: translate(locale, "meta.description"),
  };
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const locale = currentLocale();

  return (
    <html lang={locale}>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <LocaleProvider initialLocale={locale}>
          <main id="main-content">{children}</main>
        </LocaleProvider>
      </body>
    </html>
  );
}
