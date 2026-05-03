/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        mnemo: {
          bg: '#0a0a0b',
          card: '#141417',
          primary: '#3b82f6',
          secondary: '#8b5cf6',
          text: '#f4f4f5'
        }
      }
    },
  },
  plugins: [],
}
