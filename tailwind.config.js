/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: { extend: { colors: { navy: { 50: '#eef3fb', 100: '#dbe6f6', 200: '#b9cdec', 600: '#1d4a94', 700: '#14397a', 800: '#0f2d63', 900: '#0b2250' } } } },
  plugins: [],
}
