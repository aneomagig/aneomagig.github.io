/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './*.html',
    './_layouts/**/*.html',
    './_includes/**/*.html',
    './about/**/*.html',
    './devlog/**/*.html',
    './portfolio/**/*.html',
    './_posts/**/*.{html,md,markdown}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Noto Sans KR"', 'sans-serif'],
        display: ['Poppins', 'sans-serif'],
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
};
