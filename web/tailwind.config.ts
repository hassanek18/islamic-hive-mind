import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        'bg-primary': '#0a0e1a',
        'bg-secondary': '#111827',
        'bg-chat': '#1a1f35',
        'accent-gold': '#d4a843',
        'accent-gold-dim': '#b8942f',
        'text-primary': '#f5f0e8',
        'text-secondary': '#9ca3af',
        'text-arabic': '#ffffff',
        'border-subtle': '#1e293b',
      },
      fontFamily: {
        amiri: ['Amiri', 'serif'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      maxWidth: {
        'content': '1200px',
      },
    },
  },
  plugins: [],
};
export default config;
