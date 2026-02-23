// tailwind.config.js — cores da Âncora Contabilidade
module.exports = {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        ancora: {
          gold:    '#C6A348',  // Dourado Institucional
          black:   '#111111',  // Preto Institucional
          white:   '#FFFFFF',  // Branco Oficial
          navy:    '#0F1E3A',  // Azul Marinho
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
