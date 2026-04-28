import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#f3f7ff",
          100: "#dfe9ff",
          200: "#bfd2ff",
          500: "#3b82f6",
          600: "#1d4ed8",
          900: "#0b1a37",
        },
      },
    },
  },
  plugins: [],
};

export default config;

