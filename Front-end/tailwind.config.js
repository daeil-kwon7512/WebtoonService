/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        "primary": "#3E6F7E",
        "primary-light": "#E0F2F1",
        "accent": "#17cfa1",
        "background-light": "#F7F7F8",
        "text-main": "#333333",
        "text-muted": "#666666",
      },
      fontFamily: {
        "sans": ["Inter", "sans-serif"],
      },
      boxShadow: {
        'soft': '0 4px 20px -2px rgba(0, 0, 0, 0.05)',
      }
    },
  },
  plugins: [],
}

