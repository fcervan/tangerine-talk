const LANGS = ["Español", "日本語", "Français", "Deutsch", "Italiano", "Português", "한국어", "中文", "Русский", "العربية", "हिन्दी", "Nederlands", "Svenska", "Türkçe", "Polski", "English"];

export default function Languages() {
  const row = [...LANGS, ...LANGS];
  return (
    <section id="languages" className="overflow-hidden bg-white py-20">
      <div className="mx-auto mb-10 max-w-[1200px] px-5">
        <p className="eyebrow mb-3">Idiomas</p>
        <h2 className="h2">50+ idiomas, <span className="hl">um só</span> tutor.</h2>
      </div>
      <div className="[mask-image:linear-gradient(90deg,transparent,#000_10%,#000_90%,transparent)]">
        <div className="marquee flex w-max gap-4">
          {row.map((l, i) => (
            <span key={i} className="rounded-pill bg-tangerine-soft px-6 py-3 text-[16px] font-medium text-ink transition-colors duration-300 hover:bg-tangerine hover:text-white">
              {l}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}
