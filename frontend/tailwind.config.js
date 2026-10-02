/** Colours come from CSS variables in src/index.css so light (white/blue/black)
 *  and dark (black/green) themes swap with a single class on <html>. */
const v = (name) => `rgb(var(--${name}) / <alpha-value>)`;

module.exports = {
  content: ["./app/**/*.{js,jsx}", "./components/**/*.{js,jsx}", "./views/**/*.{js,jsx}"],
  darkMode: "class",
  theme: {
    extend: {
      // big desktop monitors (the root font size also steps up here - see globals.css)
      screens: { "3xl": "1920px", "4xl": "2400px" },
      colors: {
        bg: v("bg"),
        surface: v("surface"),
        raised: v("raised"),
        line: v("line"),
        ink: v("ink"),
        muted: v("muted"),
        primary: v("primary"),
        "primary-strong": v("primary-strong"),
        "on-primary": v("on-primary"),
        ok: v("ok"),
        "ok-strong": v("ok-strong"),
        bad: v("bad"),
        "bad-strong": v("bad-strong"),
        gold: v("gold"),
        flame: v("flame"),
      },
      fontFamily: {
        sans: ["var(--font-nunito)", "ui-rounded", '"Segoe UI"', "system-ui", "sans-serif"],
        mono: ["ui-monospace", '"JetBrains Mono"', "SFMono-Regular", "Menlo", "Consolas", "monospace"],
      },
      keyframes: {
        pop: { "0%": { transform: "scale(.9)", opacity: 0 }, "100%": { transform: "scale(1)", opacity: 1 } },
        rise: { "0%": { transform: "translateY(100%)" }, "100%": { transform: "translateY(0)" } },
        shake: { "0%,100%": { transform: "translateX(0)" }, "25%": { transform: "translateX(-6px)" }, "75%": { transform: "translateX(6px)" } },
        bob: { "0%,100%": { transform: "translateY(0)" }, "50%": { transform: "translateY(-6px)" } },
      },
      animation: {
        pop: "pop .25s ease-out",
        rise: "rise .25s ease-out",
        shake: "shake .3s ease-in-out",
        bob: "bob 2.4s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
