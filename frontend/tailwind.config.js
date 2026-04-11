// tailwind.config.js — cores da Âncora Contabilidade
module.exports = {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        ancora: {
          // Usa CSS variables com suporte a modificadores de opacidade (/20, /50, etc.)
          gold:  'rgb(var(--ancora-gold) / <alpha-value>)',
          black: 'rgb(var(--ancora-black) / <alpha-value>)',
          white: 'rgb(var(--ancora-white) / <alpha-value>)',
          navy:  'rgb(var(--ancora-navy) / <alpha-value>)',
        }
      },
      fontFamily: {
        display: ['"Cinzel"', '"Cormorant Garamond"', 'serif'],
        body:    ['"Montserrat"', 'sans-serif'],
      }
    }
  },
  plugins: [],
}
