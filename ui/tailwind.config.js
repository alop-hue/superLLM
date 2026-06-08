/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#fff6ed',
          100: '#ffebd4',
          200: '#ffd4a8',
          300: '#ffb875',
          400: '#ff9642',
          500: '#ff7a1a',
          600: '#f8600a',
          700: '#cc4a05',
          800: '#a23b0a',
          900: '#82330c',
        },
      },
    },
  },
  plugins: [],
}
