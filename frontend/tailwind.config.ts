import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{vue,ts}"],
  theme: {
    extend: {
      colors: {
        clinical: {
          bg: "#f6f8fb",
          ink: "#0f172a",
          muted: "#64748b",
          line: "#dbe4ef",
          blue: "#2563eb",
          cyan: "#0ea5e9",
          teal: "#14b8a6",
        },
      },
      boxShadow: {
        soft: "0 18px 45px rgba(15, 23, 42, 0.08)",
        panel: "0 10px 30px rgba(37, 99, 235, 0.10)",
      },
    },
  },
  plugins: [],
} satisfies Config;
