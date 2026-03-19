/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx}", "./public/index.html"],
  theme: {
    extend: {
      colors: {
        ink: "#172033",
        clay: "#fff6ea",
        peach: "#ffb36a",
        ember: "#f06d3f",
        ocean: "#0f4c5c",
        mist: "#ecf7f7"
      },
      boxShadow: {
        panel: "0 24px 60px rgba(23, 32, 51, 0.12)"
      },
      fontFamily: {
        display: ['"Sora"', "sans-serif"],
        body: ['"Manrope"', "sans-serif"],
        mono: ['"IBM Plex Mono"', "monospace"]
      }
    }
  },
  plugins: []
};
