import LocaleSwitcher from "@/components/LocaleSwitcher";
import ProvidersPanel from "@/components/ProvidersPanel";

export default function ProvidersPage() {
  return (
    <main className="min-h-screen bg-mist">
      <header className="border-b border-line bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-5 py-4 sm:px-8">
          <a href="/app" className="text-sm font-bold tracking-tight text-ink">
            Tangerine Talk
          </a>
          <LocaleSwitcher />
        </div>
      </header>
      <div className="mx-auto max-w-5xl px-5 py-10 sm:px-8">
        <ProvidersPanel />
      </div>
    </main>
  );
}
