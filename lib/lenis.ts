import type Lenis from "lenis";

let instance: Lenis | null = null;

export const setLenis = (l: Lenis | null) => {
  instance = l;
};
export const getLenis = () => instance;

export function scrollToId(hash: string) {
  const el = document.querySelector<HTMLElement>(hash);
  if (!el) return;
  if (instance) {
    instance.scrollTo(el, { offset: -72, duration: 1.3, easing: (t) => 1 - Math.pow(1 - t, 4) });
  } else {
    el.scrollIntoView({ behavior: "smooth" });
  }
}
