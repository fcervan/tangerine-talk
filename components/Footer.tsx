import Logo from "./Logo";

export default function Footer() {
  return (
    <footer className="border-t border-line bg-white">
      <div className="mx-auto flex max-w-[1200px] flex-col items-start justify-between gap-6 px-5 py-10 sm:flex-row sm:items-center">
        <Logo size={34} />
        <p className="text-[13px] text-body">© {new Date().getFullYear()} Tangerine Talk. Fale livremente.</p>
      </div>
    </footer>
  );
}
