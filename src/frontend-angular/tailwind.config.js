/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{html,ts}"],
  theme: {
    extend: {
      colors: {
        'tevejo-azul': '#345e9e',
        'tevejo-escuro': '#191a29',
        'tevejo-cinza-texto': '#414141', // Cinza levemente mais escuro
        'tevejo-cinza-suave': '#979797', // Para a descrição
        'tevejo-bg-card': '#ffffff',    // Branco levemente cinza
      },
      backgroundImage: {
        'tevejo-gradiente': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }
    },
  },
  plugins: [],
}