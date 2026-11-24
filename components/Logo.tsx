export default function Logo({ size = 40 }: { size?: number }) {
  return (
    <span className="flex items-center gap-2.5">
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src="/mascot.png" alt="" width={size} height={size} style={{ width: size, height: size }} className="object-contain" />
      <span className="text-[22px] font-extrabold leading-none tracking-tight text-ink">
        Tangerine<span className="text-tangerine">Talk</span>
      </span>
    </span>
  );
}
