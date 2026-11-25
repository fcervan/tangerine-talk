import Logo from "./Logo";

export default function Footer() {
  const year = new Date().getFullYear();
  return (
    <footer className="border-t border-line bg-white">
      <div className="mx-auto flex max-w-[1200px] flex-col items-start justify-between gap-6 px-5 py-10 sm:flex-row sm:items-center">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:gap-6 w-full">
          <Logo size={34} />
          <nav className="flex flex-wrap items-center gap-4 text-[13px] text-body">
            <a href="/login" className="hover:text-tangerine">Entrar</a>
            <a href="/terms" className="hover:text-tangerine">Termos</a>
            <a href="/privacy" className="hover:text-tangerine">Privacidade</a>
            <a href="https://github.com/fcervan/tangerine-talk" target="_blank" rel="noopener noreferrer" className="hover:text-tangerine">GitHub</a>
          </nav>
        </div>
        <p className="text-[13px] text-body">© {year} Tangerine Talk. Fale livremente.</p>
      </div>
    </footer>
  );
}
