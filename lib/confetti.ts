const COLORS = ["#FF5A0A", "#FF7A33", "#E64A00", "#FFE9DC", "#FFFFFF", "#FFF5EE"];

/** Micro-confetti strictly in orange + white tones, rendered with the Web Animations API. */
export function burst(x: number, y: number, count = 26) {
  if (typeof document === "undefined") return;
  for (let i = 0; i < count; i++) {
    const el = document.createElement("span");
    const size = 5 + Math.random() * 7;
    const color = COLORS[Math.floor(Math.random() * COLORS.length)];
    Object.assign(el.style, {
      position: "fixed",
      left: `${x}px`,
      top: `${y}px`,
      width: `${size}px`,
      height: `${size * (Math.random() > 0.5 ? 1 : 0.5)}px`,
      borderRadius: Math.random() > 0.5 ? "999px" : "2px",
      background: color,
      boxShadow: "0 0 0 1px rgba(255,90,10,0.35)",
      pointerEvents: "none",
      zIndex: "9999",
    } as CSSStyleDeclaration);
    document.body.appendChild(el);
    const angle = Math.random() * Math.PI * 2;
    const dist = 50 + Math.random() * 90;
    const dx = Math.cos(angle) * dist;
    const dy = Math.sin(angle) * dist - 30;
    el.animate(
      [
        { transform: "translate(-50%,-50%) scale(1) rotate(0deg)", opacity: 1 },
        {
          transform: `translate(calc(-50% + ${dx}px), calc(-50% + ${dy + 70}px)) scale(0.6) rotate(${
            Math.random() * 540 - 270
          }deg)`,
          opacity: 0,
        },
      ],
      { duration: 800 + Math.random() * 600, easing: "cubic-bezier(0.22, 1, 0.36, 1)" }
    ).onfinish = () => el.remove();
  }
}

export function burstFrom(el: Element) {
  const r = el.getBoundingClientRect();
  burst(r.left + r.width / 2, r.top + r.height / 2);
}
