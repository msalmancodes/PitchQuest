module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'peach': '#d4886a',
        'peach-dark': '#c7785a',
        'wood-light': '#a08b7c',
        'wood': '#8b6f5c',
        'wood-dark': '#5a4a42',
        'ivory': '#fbf9f7',
        'sand': '#f0e8e2',
        'cream': '#f5e6db',
      },
      fontFamily: {
        'sans': ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
      },
    },
  },
  plugins: [],
}