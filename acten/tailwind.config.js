/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        acten: {
          green: "#173D32",
          burgundy: "#7B263A",
          gold: "#C8A45D",
          ivory: "#F7F5EF",
          charcoal: "#242824",
        },
      },
    },
  },
  plugins: [],
};
