"use client";

import { useParams } from "next/navigation";

import LessonPlayer from "@/components/LessonPlayer";
import LocaleSwitcher from "@/components/LocaleSwitcher";

export default function LessonPage() {
  const params = useParams<{ id: string }>();
  const id = params?.id ?? "";
  return (
    <main className="min-h-screen bg-mist">
      <header className="border-b border-line bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-5 py-4 sm:px-8">
          <a href="/curriculum" className="text-sm font-bold tracking-tight text-ink">
            Tangerine Talk
          </a>
          <LocaleSwitcher />
        </div>
      </header>
      <div className="mx-auto max-w-3xl px-5 py-10 sm:px-8">
        <LessonPlayer lessonId={id} />
      </div>
    </main>
  );
}
