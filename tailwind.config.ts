import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        tangerine: {
          DEFAULT: "#FF5A0A",
          light: "#FF7A33",
          dark: "#E64A00",
          tint: "#FFE9DC",
          soft: "#FFF5EE",
        },
        ink: "#111111",
        body: "#5C5C5C",
        mist: "#F7F7F8",
        line: "#EDEDED",
      },
      fontFamily: { sans: ["Poppins", "system-ui", "sans-serif"] },
      boxShadow: {
        card: "0 10px 30px rgba(17, 17, 17, 0.06)",
        lift: "0 18px 40px rgba(17, 17, 17, 0.10)",
        cta: "0 12px 28px rgba(255, 90, 10, 0.35)",
      },
      borderRadius: { pill: "999px" },
      transitionTimingFunction: { brand: "cubic-bezier(0.22, 1, 0.36, 1)" },
    },
  },
  plugins: [],
};

export default config;
