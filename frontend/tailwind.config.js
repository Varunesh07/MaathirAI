/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        medic: {
          primary: '#0474ea',
          accent: '#74bcf4',
          deep: '#024082',
          chatbg: '#f5f9ff',
          card: '#ffffff',
          border: '#e0ecfa',
          severe: '#E24B4A',
          moderate: '#EF9F27',
          safe: '#1D9E75'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
