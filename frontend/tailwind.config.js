/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // 简约浅色主题配色
        primary: '#1a1a1a',
        secondary: '#666666',
        border: '#e5e5e5',
        background: '#fafafa',
        surface: '#ffffff',
      }
    },
  },
  plugins: [],
}
