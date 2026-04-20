import type { Config } from "tailwindcss";

// ARIA Design System — tailwind.config.ts
// All tokens sourced from design-tokens.md
const config: Config = {
  darkMode: ["class"],
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      // ─── Brand Colors ────────────────────────────────────────────────────────
      colors: {
        brand: {
          primary: "#4F46E5",
          "primary-hover": "#4338CA",
          "primary-light": "#EEF2FF",
          accent: "#6366F1",
        },

        // ─── Evaluation Outcome Colors ─────────────────────────────────────────
        outcome: {
          pass: "#10B981",
          "pass-light": "#D1FAE5",
          fail: "#F43F5E",
          "fail-light": "#FFE4E6",
          warn: "#F59E0B",
          "warn-light": "#FEF3C7",
          pause: "#8B5CF6",
          "pause-light": "#EDE9FE",
        },

        // ─── Pipeline Status Colors ────────────────────────────────────────────
        status: {
          queued: "#6B7280",
          "queued-bg": "#F3F4F6",
          running: "#3B82F6",
          "running-bg": "#DBEAFE",
          complete: "#10B981",
          "complete-bg": "#D1FAE5",
          failed: "#EF4444",
          "failed-bg": "#FEE2E2",
          conditional: "#F59E0B",
          "conditional-bg": "#FEF3C7",
        },

        // ─── LLM Brand Colors ──────────────────────────────────────────────────
        llm: {
          claude: "#D97706",
          "claude-bg": "#FEF3C7",
          openai: "#10B981",
          "openai-bg": "#D1FAE5",
          gemini: "#3B82F6",
          "gemini-bg": "#DBEAFE",
        },

        // ─── Surface / Background ──────────────────────────────────────────────
        surface: {
          DEFAULT: "#FFFFFF",
          raised: "#F3F4F6",
          page: "#F9FAFB",
        },

        // ─── Neutral Scale ─────────────────────────────────────────────────────
        neutral: {
          50: "#F9FAFB",
          100: "#F3F4F6",
          200: "#E5E7EB",
          300: "#D1D5DB",
          400: "#9CA3AF",
          500: "#6B7280",
          600: "#4B5563",
          700: "#374151",
          800: "#1F2937",
          900: "#111827",
        },
      },

      // ─── Font Families ────────────────────────────────────────────────────────
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["Geist Mono", "ui-monospace", "monospace"],
      },

      // ─── Font Sizes (type scale from design-tokens.md) ────────────────────────
      fontSize: {
        caption: ["0.75rem", { lineHeight: "1.4", fontWeight: "400" }],
        "body-sm": ["0.875rem", { lineHeight: "1.5", fontWeight: "400" }],
        body: ["1rem", { lineHeight: "1.6", fontWeight: "400" }],
        "body-lg": ["1.125rem", { lineHeight: "1.6", fontWeight: "400" }],
        h4: ["1.25rem", { lineHeight: "1.4", fontWeight: "600" }],
        h3: ["1.5rem", { lineHeight: "1.3", fontWeight: "600" }],
        h2: ["1.875rem", { lineHeight: "1.25", fontWeight: "700" }],
        h1: ["2.25rem", { lineHeight: "1.2", fontWeight: "700" }],
        "score-sm": ["1.25rem", { lineHeight: "1", fontWeight: "600" }],
        score: ["2rem", { lineHeight: "1", fontWeight: "700" }],
      },

      // ─── Spacing Scale ─────────────────────────────────────────────────────────
      // Extends Tailwind's default 4px base (0.25rem = 1 unit)
      spacing: {
        "4.5": "1.125rem", // 18px — occasional gap between standard steps
        "13": "3.25rem",   // 52px
        "15": "3.75rem",   // 60px
        "18": "4.5rem",    // 72px
        "22": "5.5rem",    // 88px
        "26": "6.5rem",    // 104px
        "30": "7.5rem",    // 120px
      },

      // ─── Border Radius ─────────────────────────────────────────────────────────
      borderRadius: {
        sm: "4px",
        md: "8px",
        lg: "12px",
        xl: "16px",
        "2xl": "24px",
        full: "9999px",
      },

      // ─── Box Shadows ───────────────────────────────────────────────────────────
      boxShadow: {
        sm: "0 1px 2px rgba(0,0,0,0.05)",
        md: "0 4px 6px rgba(0,0,0,0.07)",
        lg: "0 10px 15px rgba(0,0,0,0.10)",
        xl: "0 20px 25px rgba(0,0,0,0.12)",
      },

      // ─── Animations ────────────────────────────────────────────────────────────
      keyframes: {
        // Running-state pulse for agent cards and status icons
        "status-pulse": {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.4" },
        },
        // Spinner for Loader2 icon
        spin: {
          from: { transform: "rotate(0deg)" },
          to: { transform: "rotate(360deg)" },
        },
        // Slide-in for drawer
        "slide-in-right": {
          from: { transform: "translateX(100%)" },
          to: { transform: "translateX(0)" },
        },
        // Fade in for modals
        "fade-in": {
          from: { opacity: "0" },
          to: { opacity: "1" },
        },
        // Score ring draw animation
        "ring-fill": {
          from: { strokeDashoffset: "var(--ring-circumference)" },
          to: { strokeDashoffset: "var(--ring-offset)" },
        },
      },
      animation: {
        "status-pulse": "status-pulse 2s ease-in-out infinite",
        "slide-in-right": "slide-in-right 0.25s ease-out",
        "fade-in": "fade-in 0.2s ease-out",
        "ring-fill": "ring-fill 0.8s ease-out forwards",
      },

      // ─── Max Widths ─────────────────────────────────────────────────────────────
      maxWidth: {
        "8xl": "88rem",   // 1408px — wide report layouts
        "9xl": "96rem",   // 1536px — ultra-wide screens
      },

      // ─── Z-Index Scale ──────────────────────────────────────────────────────────
      zIndex: {
        sidebar: "40",
        topbar: "50",
        drawer: "60",
        modal: "70",
        toast: "80",
        tooltip: "90",
      },
    },
  },
  plugins: [
    // shadcn/ui requires tailwindcss-animate
    // add: require("tailwindcss-animate")
    // Typography plugin for report prose sections
    // add: require("@tailwindcss/typography")
  ],
};

export default config;
