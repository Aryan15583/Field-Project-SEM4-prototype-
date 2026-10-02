"""HTML & CSS projects - one at the end of each section (added to units 8, 12 and 16)."""
from .dsl import project, run, t
from .htmlcss_adv import PAGE, page, styled

# ------------------------------------------------------------------ Beginner: profile card
CARD_HTML = '''<article class="card">
  <img src="avatar.png" alt="Portrait of Ada" width="96" height="96">
  <h1>Ada Lovelace</h1>
  <p class="role">First programmer</p>
  <ul class="links">
    <li><a href="https://github.com">GitHub</a></li>
    <li><a href="mailto:ada@example.com">Email</a></li>
  </ul>
</article>'''

CARD_CSS = '''body {
  margin: 0;
  font-family: sans-serif;
}
.card {
  width: 300px;
  padding: 24px;
  border-radius: 16px;
  border: 2px solid rgb(29, 111, 242);
  text-align: center;
}
.role {
  color: rgb(85, 85, 85);
}'''

CARD_FLEX = CARD_CSS + '''
.links {
  display: flex;
  justify-content: center;
  gap: 12px;
  padding: 0;
  list-style: none;
}'''

BEGINNER = project(
    "Project: Profile card",
    "Build the kind of profile card you see on every social site:\n\n1. The HTML: a picture, name, role and links.\n2. "
    "Card styling with the box model.\n3. A tidy row of links with flexbox.",
    run("Step 1 - Inside an <article class=\"card\">: an <img> (with alt text and width/height 96), an <h1> with a name, "
        "a <p class=\"role\"> and a <ul class=\"links\"> with two links.", "html",
        [t("img alt", selector=".card img", prop="attr:alt"), t("h1", selector=".card h1", prop="count"),
         t("role", selector=".card p.role", prop="count"), t("links", selector=".card ul.links li a", prop="count"),
         t("img width", selector=".card img", prop="attr:width")],
        ["Portrait of Ada", "1", "1", "2", "96"], page(CARD_HTML), starter=PAGE),
    run("Step 2 - Style it: body margin 0; .card 300px wide with 24px padding, 16px rounded corners, a 2px solid "
        "rgb(29, 111, 242) border and centred text; .role in rgb(85, 85, 85).", "html",
        [t("width", selector=".card", prop="width"), t("padding", selector=".card", prop="padding-top"),
         t("radius", selector=".card", prop="border-top-left-radius"), t("border", selector=".card", prop="border-top-color"),
         t("centred", selector=".card", prop="text-align"), t("role", selector=".role", prop="color")],
        ["300px", "24px", "16px", "rgb(29, 111, 242)", "center", "rgb(85, 85, 85)"],
        styled(CARD_CSS, CARD_HTML), starter=page(CARD_HTML), carry=True),
    run("Step 3 - Lay the links out in a row: .links becomes a flex container, centred, with a 12px gap, no padding and "
        "no bullets.", "html",
        [t("flex", selector=".links", prop="display"), t("centre", selector=".links", prop="justify-content"),
         t("gap", selector=".links", prop="column-gap"), t("bullets", selector=".links", prop="list-style-type"),
         t("padding", selector=".links", prop="padding-left")],
        ["flex", "center", "12px", "none", "0px"], styled(CARD_FLEX, CARD_HTML), starter=styled(CARD_CSS, CARD_HTML), carry=True),
)

# ------------------------------------------------------------------ Intermediate: pricing page
PLANS = '''<main class="plans">
  <section class="plan">
    <h2>Free</h2>
    <p class="price">$0</p>
    <a class="cta" href="#free">Start</a>
  </section>
  <section class="plan featured">
    <h2>Pro</h2>
    <p class="price">$9</p>
    <a class="cta" href="#pro">Upgrade</a>
  </section>
  <section class="plan">
    <h2>Team</h2>
    <p class="price">$29</p>
    <a class="cta" href="#team">Contact us</a>
  </section>
</main>'''

GRID = '''body {
  margin: 0;
}
.plans {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0;
  width: 600px;
}
.plan {
  padding: 16px;
  border: 1px solid rgb(220, 220, 220);
}'''

FEATURED = GRID + '''
.plan.featured {
  border: 3px solid rgb(29, 111, 242);
  transform: scale(1.05);
}
.cta {
  transition: background-color 150ms ease-out;
}
.cta:hover {
  background-color: rgb(29, 111, 242);
}'''

RESPONSIVE = FEATURED.replace('''  width: 600px;
}''', '''  width: 100%;
}
@media (max-width: 640px) {
  .plans {
    grid-template-columns: 1fr;
  }
  .plan.featured {
    order: -1;
  }
}''')

INTERMEDIATE = project(
    "Project: Pricing page",
    "Build a SaaS pricing section:\n\n1. Three plan cards in a grid.\n2. Highlight the featured plan and animate the "
    "buttons.\n3. Make it responsive: one column on small screens, featured plan first.\n\n(The preview is 600px wide - "
    "a 'small screen' in step 3.)",
    run("Step 1 - Three <section class=\"plan\"> elements (Free, Pro with class featured, Team) inside <main "
        "class=\"plans\">. Make .plans a 3-column grid 600px wide with no gap (body margin 0).", "html",
        [t("plans", selector=".plans .plan", prop="count"), t("featured", selector=".plan.featured h2", prop="text"),
         t("columns", selector=".plans", prop="grid-template-columns")],
        ["3", "Pro", "200px 200px 200px"], styled(GRID, PLANS), starter=PAGE),
    run("Step 2 - .plan.featured gets a 3px solid rgb(29, 111, 242) border and transform: scale(1.05). The .cta links "
        "get a 150ms ease-out background-color transition and turn rgb(29, 111, 242) on hover.", "html",
        [t("border", selector=".featured", prop="border-top-width"), t("scale", selector=".featured", prop="transform"),
         t("transition", selector=".cta", prop="transition-duration"), t("timing", selector=".cta", prop="transition-timing-function")],
        ["3px", "matrix(1.05, 0, 0, 1.05, 0, 0)", "0.15s", "ease-out"], styled(FEATURED, PLANS), starter=styled(GRID, PLANS),
        carry=True, require=[r":hover"]),
    run("Step 3 - Make .plans width: 100%, and in a @media (max-width: 640px) query switch to a single column and move "
        "the featured plan first with order: -1.", "html",
        [t("one column", selector=".plans", prop="grid-template-columns"), t("featured first", selector=".featured", prop="order"),
         t("first card on top", selector=".featured", prop="top")],
        ["600px", "-1", "auto"], styled(RESPONSIVE, PLANS), starter=styled(FEATURED, PLANS), carry=True,
        require=[r"@media\s*\(\s*max-width"]),
)

# ------------------------------------------------------------------ Advanced: accessible landing page
LANDING = '''<a class="skip" href="#main">Skip to content</a>
<header>
  <nav aria-label="Main">
    <button class="menu" aria-expanded="false" aria-controls="menu">Menu</button>
    <ul id="menu">
      <li><a href="/" aria-current="page">Home</a></li>
      <li><a href="/learn">Learn</a></li>
    </ul>
  </nav>
</header>
<main id="main">
  <h1>Learn to code</h1>
  <button class="icon" aria-label="Play intro video"><span aria-hidden="true">▶</span></button>
</main>
<footer>
  <p>Made with care</p>
</footer>'''

THEME = ''':root {
  --bg: rgb(255, 255, 255);
  --text: rgb(17, 17, 17);
  --brand: rgb(29, 111, 242);
}
[data-theme="dark"] {
  --bg: rgb(0, 0, 0);
  --text: rgb(229, 231, 235);
  --brand: rgb(34, 197, 94);
}
body {
  margin: 0;
  background-color: var(--bg);
  color: var(--text);
}
h1 {
  color: var(--brand);
}'''

A11Y = THEME + '''
.skip {
  position: absolute;
  left: -9999px;
}
.skip:focus {
  left: 8px;
}
:focus-visible {
  outline: 3px solid var(--brand);
  outline-offset: 2px;
}
@media (prefers-reduced-motion: reduce) {
  * {
    animation: none;
    transition: none;
  }
}'''

ADVANCED = project(
    "Project: Accessible landing page",
    "Build a landing page that works for everyone:\n\n1. Semantic landmarks, a skip link and an accessible menu "
    "button.\n2. A light/dark theme with CSS custom properties.\n3. Keyboard focus styles, a hidden-until-focused "
    "skip link and reduced-motion support.",
    run("Step 1 - Markup: a skip link to #main first; a <header> with <nav aria-label=\"Main\"> holding a menu button "
        "(aria-expanded=\"false\", aria-controls=\"menu\") and a list whose Home link has aria-current=\"page\"; <main "
        "id=\"main\"> with an <h1> and an icon-only button with an aria-label; a <footer>.", "html",
        [t("skip", selector="body > a:first-child", prop="attr:href"), t("landmarks", selector="header, nav, main, footer", prop="count"),
         t("menu button", selector="button[aria-controls=menu]", prop="attr:aria-expanded"),
         t("current", selector="a[aria-current=page]", prop="text"), t("icon label", selector="main button", prop="attr:aria-label")],
        ["#main", "4", "false", "Home", "Play intro video"], page(LANDING), starter=PAGE),
    run("Step 2 - Theme: on :root define --bg rgb(255, 255, 255), --text rgb(17, 17, 17), --brand rgb(29, 111, 242); in "
        "[data-theme=\"dark\"] override them to rgb(0, 0, 0), rgb(229, 231, 235), rgb(34, 197, 94). body uses --bg / --text "
        "(margin 0) and h1 uses --brand.", "html",
        [t("light bg", selector="body", prop="background-color"), t("brand", selector="html", prop="--brand"),
         t("dark brand", selector="[data-theme=dark] h1", prop="color")],
        ["rgb(255, 255, 255)", "rgb(29, 111, 242)", "rgb(34, 197, 94)"],
        styled(THEME, LANDING.replace('<main id="main">', '<main id="main" data-theme="dark">')),
        starter=page(LANDING.replace('<main id="main">', '<main id="main" data-theme="dark">')), carry=True,
        require=[r"var\(\s*--brand"]),
    run("Step 3 - Accessibility polish: .skip is position absolute and off-screen (left: -9999px) until :focus (left: "
        "8px); :focus-visible gets a 3px solid outline in var(--brand) with a 2px offset; and a prefers-reduced-motion "
        "query turns off animations and transitions.", "html",
        [t("skip hidden", selector=".skip", prop="left"), t("skip position", selector=".skip", prop="position"),
         t("dark brand still works", selector="[data-theme=dark] h1", prop="color")],
        ["-9999px", "absolute", "rgb(34, 197, 94)"],
        styled(A11Y, LANDING.replace('<main id="main">', '<main id="main" data-theme="dark">')),
        starter=styled(THEME, LANDING.replace('<main id="main">', '<main id="main" data-theme="dark">')), carry=True,
        require=[r":focus-visible", r"prefers-reduced-motion", r"\.skip:focus"]),
)

PROJECTS = {8: BEGINNER, 12: INTERMEDIATE, 16: ADVANCED}
