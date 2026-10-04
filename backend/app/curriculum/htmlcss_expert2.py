"""HTML & CSS - Expert section, part 2 (units 24-29): modern layout features, motion, responsive design, components,
architecture & theming, and capstone pages. Run exercises render in a script-less 600x400 frame and read back
COMPUTED CSS values, counts, text or attributes."""
from .dsl import code, fill, lesson, mcq, order, run, section, t, unit
from .htmlcss_adv import PAGE, page, starter_with, styled

EXPERT2 = section(
    "Expert",
    # ------------------------------------------------------------------ 24
    unit(
        "Unit 24 · Modern CSS features",
        lesson(
            "Container queries",
            """Media queries react to the VIEWPORT; container queries react to the size of the component's own PARENT - so a card adapts wherever it is placed (sidebar or full width).

.wrapper { container-type: inline-size; }
@container (min-width: 400px) {
  .card { flex-direction: row; }
}

Mark the parent with container-type; then @container rules apply when that container is wide enough. They make truly reusable components possible.""",
            mcq("What does a container query measure?", ["The size of a parent container", "The viewport", "The screen", "The font"], 0),
            mcq("What must the parent declare?", ["container-type", "container-name only", "display: container", "@media"], 0),
            mcq("Why are container queries useful?", ["Components adapt to where they are placed", "They are faster", "They replace HTML", "They remove CSS"], 0),
            run("Make .card a column flex box by default, but switch to row when its container (.wrap) is at least 400px wide. The .wrap is 500px wide, so the card should compute to row.", "html",
                [t("direction", selector=".card", prop="flex-direction"), t("container", selector=".wrap", prop="container-type")],
                ["row", "inline-size"], styled(".wrap {\n  width: 500px;\n  container-type: inline-size;\n}\n.card {\n  display: flex;\n  flex-direction: column;\n}\n@container (min-width: 400px) {\n  .card {\n    flex-direction: row;\n  }\n}", '<div class="wrap">\n  <div class="card"><span>A</span><span>B</span></div>\n</div>'),
                starter=starter_with('<div class="wrap">\n  <div class="card"><span>A</span><span>B</span></div>\n</div>'), require=[r"@container", r"container-type"]),
        ),
        lesson(
            "Cascade layers",
            """@layer lets you control which group of rules wins, regardless of specificity. Later layers beat earlier ones; unlayered styles beat all layers.

@layer reset, base, components, utilities;
@layer base { a { color: blue; } }
@layer components { .nav a { color: green; } }

Because the layer order is declared up front, a low-specificity utility in a later layer can override a high-specificity selector in an earlier one - ending most 'specificity wars'.""",
            mcq("Which wins: a rule in a later layer or an earlier layer?", ["The later layer", "The earlier layer", "The one with more selectors always", "Neither"], 0),
            mcq("What beats every layer?", ["Unlayered styles", "!important in no layer only", "Nothing", "Inline comments"], 0),
            mcq("What problem do layers reduce?", ["Specificity wars", "Slow loading", "Missing fonts", "Broken HTML"], 0),
            run("Declare layers 'base, utilities'. In base set p to colour rgb(0, 0, 255) using the very specific selector body main p; in utilities set .muted to rgb(128, 128, 128). Despite lower specificity the utility must win for the .muted paragraph.", "html",
                [t("muted", selector=".muted", prop="color"), t("normal", selector=".plain", prop="color")],
                ["rgb(128, 128, 128)", "rgb(0, 0, 255)"], styled("@layer base, utilities;\n@layer base {\n  body main p {\n    color: rgb(0, 0, 255);\n  }\n}\n@layer utilities {\n  .muted {\n    color: rgb(128, 128, 128);\n  }\n}", '<main>\n  <p class="plain">Plain</p>\n  <p class="muted">Muted</p>\n</main>'),
                starter=starter_with('<main>\n  <p class="plain">Plain</p>\n  <p class="muted">Muted</p>\n</main>'), require=[r"@layer"]),
        ),
        lesson(
            "Nesting and logical properties",
            """CSS now supports nesting, like Sass:

.card {
  padding: 16px;
  & h2 { font-size: 20px; }
  &:hover { background: #eee; }
  @media (width < 500px) { padding: 8px; }
}

Logical properties follow the writing direction instead of left/right: margin-inline-start, padding-block, inset-inline-end, border-inline. They make layouts work in right-to-left languages automatically.""",
            mcq("What does & mean inside a nested rule?", ["The parent selector", "And", "A comment", "The root"], 0),
            mcq("Which logical property is the start-side margin in left-to-right text?", ["margin-inline-start", "margin-top", "margin-block", "margin-start-x"], 0),
            mcq("Why prefer logical properties?", ["Layouts adapt to right-to-left languages", "They're shorter", "They are faster", "Browsers need them"], 0),
            run("Using nesting, give .card padding 16px and make the h2 inside it font-size 24px via '& h2'. Also set margin-inline-start: 20px on .card (computed margin-left is 20px in left-to-right text).", "html",
                [t("padding", selector=".card", prop="padding-top"), t("h2 size", selector=".card h2", prop="font-size"), t("margin", selector=".card", prop="margin-left")],
                ["16px", "24px", "20px"], styled(".card {\n  padding: 16px;\n  margin-inline-start: 20px;\n  & h2 {\n    font-size: 24px;\n  }\n}", '<div class="card"><h2>Title</h2></div>'),
                starter=starter_with('<div class="card"><h2>Title</h2></div>'), require=[r"&"]),
        ),
    ),
    # ------------------------------------------------------------------ 25
    unit(
        "Unit 25 · Motion",
        lesson(
            "Transitions in depth",
            """A transition animates a property change smoothly: transition: property duration timing-function delay.

.btn { background: navy; transition: background-color 0.3s ease, transform 0.2s ease; }
.btn:hover { background: blue; transform: translateY(-2px); }

Animate cheap properties - transform and opacity - for smooth 60fps; animating width, height or top forces the browser to recalculate layout every frame. Timing functions: ease, linear, ease-in-out, cubic-bezier().""",
            mcq("Which properties are cheapest to animate?", ["transform and opacity", "width and height", "top and left", "margin"], 0),
            mcq("What does transition: opacity 0.3s do?", ["Fades opacity changes over 0.3 seconds", "Hides the element", "Delays 0.3s forever", "Repeats"], 0),
            mcq("Which is NOT a timing function?", ["bounce-high", "ease", "linear", "ease-in-out"], 0),
            run("Give .btn a transition on background-color lasting 0.3s with ease-in-out timing.", "html",
                [t("property", selector=".btn", prop="transition-property"), t("duration", selector=".btn", prop="transition-duration"), t("timing", selector=".btn", prop="transition-timing-function")],
                ["background-color", "0.3s", "ease-in-out"], styled(".btn {\n  background: navy;\n  color: white;\n  transition: background-color 0.3s ease-in-out;\n}\n.btn:hover {\n  background: blue;\n}", '<button class="btn">Hover me</button>'),
                starter=starter_with('<button class="btn">Hover me</button>'), require=[r"transition"]),
        ),
        lesson(
            "Transforms",
            """transform moves, scales, rotates and skews WITHOUT disturbing the layout around the element:

transform: translateX(20px);         transform: scale(1.5);
transform: rotate(45deg);            transform: translate(10px, 5px) scale(2);   /* order matters */

transform-origin sets the pivot point (default: the centre). The browser exposes the result as a matrix in computed styles. Transforms don't change the space the element takes in the flow - perfect for hover effects and animation.""",
            mcq("Does transform change the space an element takes in the layout?", ["No", "Yes", "Only scale", "Only rotate"], 0),
            mcq("What does transform-origin set?", ["The pivot point of the transform", "The element's position", "The start of an animation", "The z-index"], 0),
            mcq("Does the order of transforms matter?", ["Yes", "No", "Only for scale", "Only for rotate"], 0),
            run("Scale .zoom to double size (scale(2)) and shift .shift right by 20px (translateX(20px)).", "html",
                [t("scale", selector=".zoom", prop="transform"), t("shift", selector=".shift", prop="transform")],
                ["matrix(2, 0, 0, 2, 0, 0)", "matrix(1, 0, 0, 1, 20, 0)"], styled(".zoom {\n  transform: scale(2);\n}\n.shift {\n  transform: translateX(20px);\n}", '<div class="zoom">Z</div>\n<div class="shift">S</div>'),
                starter=starter_with('<div class="zoom">Z</div>\n<div class="shift">S</div>'), require=[r"scale", r"translate"]),
        ),
        lesson(
            "Keyframe animations & reduced motion",
            """@keyframes defines steps; animation applies them:

@keyframes pulse { from { transform: scale(1); } 50% { transform: scale(1.1); } to { transform: scale(1); } }
.dot { animation: pulse 2s ease-in-out infinite; }

Respect people who get dizzy from motion:

@media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } }

Never rely on animation alone to convey information, and avoid flashing more than 3 times a second.""",
            mcq("Which media feature respects a user's motion settings?", ["prefers-reduced-motion", "motion-safe-only", "reduce-animation", "no-motion"], 0),
            mcq("What does animation: pulse 2s infinite do?", ["Plays 'pulse' over 2 seconds, forever", "Plays once", "Delays 2s", "Pauses"], 0),
            mcq("Why avoid flashing content?", ["It can trigger seizures", "It is slower", "It breaks HTML", "It uses more memory"], 0),
            run("Create @keyframes named pulse and apply it to .dot lasting 2s, repeating infinitely.", "html",
                [t("name", selector=".dot", prop="animation-name"), t("duration", selector=".dot", prop="animation-duration"), t("count", selector=".dot", prop="animation-iteration-count")],
                ["pulse", "2s", "infinite"], styled("@keyframes pulse {\n  from {\n    transform: scale(1);\n  }\n  50% {\n    transform: scale(1.1);\n  }\n  to {\n    transform: scale(1);\n  }\n}\n.dot {\n  width: 20px;\n  height: 20px;\n  background: tomato;\n  animation: pulse 2s ease-in-out infinite;\n}", '<div class="dot"></div>'),
                starter=starter_with('<div class="dot"></div>'), require=[r"@keyframes\s+pulse", r"animation"]),
        ),
    ),
    # ------------------------------------------------------------------ 26
    unit(
        "Unit 26 · Responsive & performance",
        lesson(
            "Media queries that really adapt",
            """Design mobile-first: write the small-screen styles as the default, then ADD complexity with min-width queries as space allows.

.nav { display: block; }
@media (min-width: 600px) { .nav { display: flex; } }
@media (prefers-color-scheme: dark) { body { background: #111; } }
@media (hover: hover) { a:hover { ... } }      /* only where hovering exists */

Use content-based breakpoints (where the layout starts to break), not specific device sizes. The test frame is 600px wide, so a (min-width: 600px) rule applies.""",
            mcq("What does mobile-first mean?", ["Default styles for small screens, then min-width additions", "Only phones are supported", "Desktop styles first", "Using JavaScript"], 0),
            mcq("Which media query detects dark mode?", ["prefers-color-scheme: dark", "dark-mode: on", "theme: dark", "color: dark"], 0),
            mcq("Which are better breakpoints?", ["Where the content layout breaks", "iPhone widths", "Random numbers", "1000px only"], 0),
            run("Mobile-first: .nav is display: block by default and display: flex when the viewport is at least 600px (the frame is exactly 600px wide).", "html",
                [t("display", selector=".nav", prop="display")],
                ["flex"], styled(".nav {\n  display: block;\n}\n@media (min-width: 600px) {\n  .nav {\n    display: flex;\n  }\n}", '<nav class="nav"><a href="#">A</a><a href="#">B</a></nav>'),
                starter=starter_with('<nav class="nav"><a href="#">A</a><a href="#">B</a></nav>'), require=[r"@media", r"min-width"]),
        ),
        lesson(
            "Fluid type with clamp and viewport units",
            """clamp(min, preferred, max) keeps a value between limits while it flows with the viewport:

h1 { font-size: clamp(1.5rem, 4vw, 3rem); }
.container { width: min(100% - 2rem, 70rem); margin-inline: auto; }

vw is 1% of the viewport width (the frame is 600px wide, so 4vw = 24px); vh is 1% of its height; dvh is the dynamic height on mobile browsers (address bar aware). Fluid sizing means fewer breakpoints.""",
            mcq("What is 4vw in a 600px-wide viewport?", ["24px", "4px", "600px", "2.4px"], 0),
            mcq("What does clamp(16px, 4vw, 32px) do at 600px width?", ["Gives 24px", "Always 16px", "Always 32px", "Gives 4px"], 0),
            mcq("What does min(100% - 2rem, 70rem) do?", ["Uses the smaller of the two", "Uses the larger", "Adds them", "Multiplies them"], 0),
            run("Make the h1 font-size fluid: clamp(16px, 4vw, 32px). In the 600px frame it should compute to 24px.", "html",
                [t("size", selector="h1", prop="font-size")],
                ["24px"], styled("h1 {\n  font-size: clamp(16px, 4vw, 32px);\n}", "<h1>Fluid heading</h1>"),
                starter=starter_with("<h1>Fluid heading</h1>"), require=[r"clamp\("]),
        ),
        lesson(
            "Responsive images and loading",
            """Serve the right image: <img> with srcset and sizes lets the browser pick a size; <picture> switches formats or art direction.

<img src="photo-800.jpg" srcset="photo-400.jpg 400w, photo-800.jpg 800w" sizes="(max-width: 600px) 100vw, 600px" alt="..." width="800" height="600" loading="lazy">

Always give width and height (or aspect-ratio) so the page doesn't jump when images load (layout shift). loading="lazy" delays below-the-fold images. Prefer modern formats like WebP/AVIF.""",
            mcq("Why set width and height on images?", ["To prevent layout shift while loading", "To make them bigger", "It's required for alt", "To enable lazy loading"], 0),
            mcq("What does loading=\"lazy\" do?", ["Delays offscreen images", "Hides images", "Compresses images", "Blocks the page"], 0),
            mcq("What does srcset provide?", ["Several image sizes to choose from", "Alt text", "A caption", "A link"], 0),
            run("Write an <img> with src photo.jpg, an alt text, width 400, height 300 and loading lazy. The test reads the attributes.", "html",
                [t("alt", selector="img", prop="attr:alt"), t("width", selector="img", prop="attr:width"), t("height", selector="img", prop="attr:height"), t("loading", selector="img", prop="attr:loading")],
                ["A mountain at sunrise", "400", "300", "lazy"], page('<img src="photo.jpg" alt="A mountain at sunrise" width="400" height="300" loading="lazy">'),
                starter=PAGE, require=[r"loading=[\"']lazy"]),
        ),
    ),
    # ------------------------------------------------------------------ 27
    unit(
        "Unit 27 · Building components",
        lesson(
            "Buttons with variants and states",
            """A button system has a base style plus variants (primary, danger) and states (hover, focus-visible, disabled):

.btn { padding: 8px 16px; border-radius: 6px; border: 2px solid transparent; font: inherit; cursor: pointer; }
.btn--primary { background: #1d6ff2; color: white; }
.btn:focus-visible { outline: 3px solid #93c5fd; outline-offset: 2px; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }

Use real <button> elements (keyboard and accessibility for free); never a div with a click handler. font: inherit stops buttons from using their own tiny default font.""",
            mcq("Why use a real <button> instead of a div?", ["Keyboard and accessibility support built in", "It is faster", "It is shorter", "Divs can't be styled"], 0),
            mcq("Which pseudo-class shows focus ring for keyboard users only?", [":focus-visible", ":hover", ":active", ":checked"], 0),
            mcq("What does cursor: not-allowed signal?", ["The control is unavailable", "It's draggable", "It's loading", "It's a link"], 0),
            run("Style .btn--primary: background rgb(29, 111, 242), white text, 8px 16px padding, 6px radius. Style disabled buttons with opacity 0.5.", "html",
                [t("bg", selector=".btn--primary", prop="background-color"), t("padding", selector=".btn--primary", prop="padding-left"), t("radius", selector=".btn--primary", prop="border-top-left-radius"), t("disabled", selector="button:disabled", prop="opacity")],
                ["rgb(29, 111, 242)", "16px", "6px", "0.5"], styled(".btn {\n  padding: 8px 16px;\n  border-radius: 6px;\n  font: inherit;\n}\n.btn--primary {\n  background: rgb(29, 111, 242);\n  color: white;\n}\n.btn:disabled {\n  opacity: 0.5;\n}", '<button class="btn btn--primary">Save</button>\n<button class="btn" disabled>Wait</button>'),
                starter=starter_with('<button class="btn btn--primary">Save</button>\n<button class="btn" disabled>Wait</button>'), require=[r":disabled"]),
        ),
        lesson(
            "Cards and media objects",
            """A card groups related content: image, title, text, action. A flexible card uses flex column so actions stay at the bottom:

.card { display: flex; flex-direction: column; border: 1px solid #ddd; border-radius: 12px; overflow: hidden; }
.card__body { padding: 16px; flex: 1; }
.card__action { margin-top: auto; }

overflow: hidden clips the image to the rounded corners. The 'media object' (image + text side by side) is a row flexbox with gap.""",
            mcq("Why overflow: hidden on a rounded card?", ["Images are clipped to the corners", "To hide the text", "To add scrollbars", "To speed loading"], 0),
            mcq("What does margin-top: auto do in a flex column?", ["Pushes the item to the bottom", "Adds 0 margin", "Centers it", "Hides it"], 0),
            mcq("What is a media object?", ["An image beside text", "A video tag", "A script", "A font"], 0),
            run("Build a card: .card is a flex column, 12px radius, 1px solid border and hides overflow; its .card__body grows (flex: 1).", "html",
                [t("display", selector=".card", prop="display"), t("direction", selector=".card", prop="flex-direction"), t("radius", selector=".card", prop="border-top-left-radius"), t("overflow", selector=".card", prop="overflow-x"), t("grow", selector=".card__body", prop="flex-grow")],
                ["flex", "column", "12px", "hidden", "1"], styled(".card {\n  display: flex;\n  flex-direction: column;\n  border: 1px solid #ddd;\n  border-radius: 12px;\n  overflow: hidden;\n}\n.card__body {\n  flex: 1;\n  padding: 16px;\n}", '<article class="card">\n  <div class="card__body"><h3>Title</h3><p>Text</p></div>\n  <a class="card__action" href="#">Read</a>\n</article>'),
                starter=starter_with('<article class="card">\n  <div class="card__body"><h3>Title</h3><p>Text</p></div>\n  <a class="card__action" href="#">Read</a>\n</article>'), require=[r"overflow"]),
        ),
        lesson(
            "Navigation bars",
            """A responsive nav is a list of links in a flex row:

.nav ul { display: flex; gap: 16px; list-style: none; margin: 0; padding: 0; }
.nav a { text-decoration: none; padding: 8px 12px; }
.nav a[aria-current="page"] { font-weight: 700; border-bottom: 2px solid currentColor; }

Mark the current page with aria-current="page" (it is both semantic and a styling hook). Keep the nav a real <nav> with a <ul> of links so screen readers announce 'navigation, list of 3 items'.""",
            mcq("How do you mark the current page link semantically?", ["aria-current=\"page\"", "class=\"active\" only", "id=\"current\"", "data-page"], 0),
            mcq("Which removes the bullets from a list?", ["list-style: none", "bullets: off", "text-decoration: none", "display: none"], 0),
            mcq("Why use <nav><ul><li><a>?", ["Screen readers announce it as a list of links", "It is faster", "It is shorter", "CSS requires it"], 0),
            run("Style the nav list: ul is a flex row with 16px gap and no bullets, margin and padding; the current page link (aria-current=page) is bold (700).", "html",
                [t("display", selector=".nav ul", prop="display"), t("gap", selector=".nav ul", prop="column-gap"), t("bullets", selector=".nav ul", prop="list-style-type"), t("current", selector=".nav a[aria-current=page]", prop="font-weight"), t("other", selector="#b", prop="font-weight")],
                ["flex", "16px", "none", "700", "400"], styled(".nav ul {\n  display: flex;\n  gap: 16px;\n  list-style: none;\n  margin: 0;\n  padding: 0;\n}\n.nav a[aria-current=\"page\"] {\n  font-weight: 700;\n}", '<nav class="nav">\n  <ul>\n    <li><a href="#" aria-current="page">Home</a></li>\n    <li><a id="b" href="#">Docs</a></li>\n    <li><a href="#">Blog</a></li>\n  </ul>\n</nav>'),
                starter=starter_with('<nav class="nav">\n  <ul>\n    <li><a href="#" aria-current="page">Home</a></li>\n    <li><a id="b" href="#">Docs</a></li>\n    <li><a href="#">Blog</a></li>\n  </ul>\n</nav>'), require=[r"aria-current"]),
        ),
    ),
    # ------------------------------------------------------------------ 28
    unit(
        "Unit 28 · Architecture & theming",
        lesson(
            "Design tokens with custom properties",
            """Store design decisions once as custom properties (tokens), and use them everywhere:

:root {
  --brand: #1d6ff2;
  --space-2: 8px;  --space-4: 16px;
  --radius: 8px;
}
.btn { background: var(--brand); padding: var(--space-2) var(--space-4); border-radius: var(--radius); }

Changing one token restyles the whole site. A fallback helps when a variable is missing: var(--accent, var(--brand)). Name tokens by purpose (--color-text) not by value (--blue).""",
            mcq("Why name tokens by purpose?", ["The value can change without renaming", "It is shorter", "It is required", "It is faster"], 0),
            mcq("What does var(--accent, red) do?", ["Uses --accent or falls back to red", "Sets --accent to red", "Errors", "Ignores --accent"], 0),
            mcq("What is the benefit of tokens?", ["Change one value, restyle everywhere", "Smaller HTML", "Faster fonts", "More selectors"], 0),
            run("Define --brand: rgb(29, 111, 242) and --space: 12px on :root, then use them: .btn gets background var(--brand) and padding var(--space).", "html",
                [t("bg", selector=".btn", prop="background-color"), t("padding", selector=".btn", prop="padding-top")],
                ["rgb(29, 111, 242)", "12px"], styled(":root {\n  --brand: rgb(29, 111, 242);\n  --space: 12px;\n}\n.btn {\n  background: var(--brand);\n  padding: var(--space);\n}", '<button class="btn">Go</button>'),
                starter=starter_with('<button class="btn">Go</button>'), require=[r"var\(--brand\)", r"var\(--space\)"]),
        ),
        lesson(
            "Naming and structure (BEM)",
            """BEM (Block__Element--Modifier) names make CSS predictable:

.card            the block (a standalone component)
.card__title     an element that belongs to the block
.card--featured  a modifier (a variation)

Keep selectors flat (one class) so specificity stays low and rules are easy to override. Organise files by component, and keep a short global layer for resets, tokens and utilities.""",
            mcq("What does .card__title mean in BEM?", ["An element inside the card block", "A modifier", "A new block", "An id"], 0),
            mcq("What does .card--featured mean?", ["A variation of the card", "A child element", "A page", "A state"], 0),
            mcq("Why keep selectors flat?", ["Low specificity is easy to override", "It is shorter", "Browsers require it", "It avoids classes"], 0),
            run("Use BEM: give .card a 1px solid border; .card--featured a 3px solid border; and .card__title bold (700) font weight.", "html",
                [t("normal border", selector="#a", prop="border-top-width"), t("featured border", selector="#b", prop="border-top-width"), t("title", selector=".card__title", prop="font-weight")],
                ["1px", "3px", "700"], styled(".card {\n  border: 1px solid gray;\n}\n.card--featured {\n  border-width: 3px;\n}\n.card__title {\n  font-weight: 700;\n}", '<div id="a" class="card"><span class="card__title">One</span></div>\n<div id="b" class="card card--featured"><span class="card__title">Two</span></div>'),
                starter=starter_with('<div id="a" class="card"><span class="card__title">One</span></div>\n<div id="b" class="card card--featured"><span class="card__title">Two</span></div>'), require=[r"card--featured", r"card__title"]),
        ),
        lesson(
            "Dark mode with tokens",
            """Theme switching is just swapping token values:

:root { --bg: white; --text: #111; }
@media (prefers-color-scheme: dark) { :root { --bg: #0b0b0f; --text: #f2f2f2; } }
[data-theme="dark"] { --bg: #0b0b0f; --text: #f2f2f2; }      /* a manual toggle */
body { background: var(--bg); color: var(--text); }

Also set color-scheme: light dark so built-in controls (scrollbars, form fields) match. Check contrast in BOTH themes.""",
            mcq("What is theme switching with tokens?", ["Swapping custom property values", "Rewriting every rule", "Using JavaScript only", "Duplicating the HTML"], 0),
            mcq("What does color-scheme: light dark do?", ["Lets built-in controls follow the theme", "Colours the page", "Disables dark mode", "Adds a toggle"], 0),
            mcq("What should you check in both themes?", ["Text contrast", "Page title", "Image count", "Font file size"], 0),
            run("Define --bg and --text on :root (white and rgb(17, 17, 17)), add a [data-theme=dark] block that swaps them, and apply them to body. The page uses data-theme=dark, so body should compute to a dark background (rgb(11, 11, 15)) and light text (rgb(242, 242, 242)).", "html",
                [t("bg", selector="body", prop="background-color"), t("text", selector="body", prop="color")],
                ["rgb(11, 11, 15)", "rgb(242, 242, 242)"], styled(":root {\n  --bg: white;\n  --text: rgb(17, 17, 17);\n}\n[data-theme=\"dark\"] {\n  --bg: rgb(11, 11, 15);\n  --text: rgb(242, 242, 242);\n}\nbody {\n  background: var(--bg);\n  color: var(--text);\n}", "<p>Hello</p>").replace("<body>", '<body data-theme="dark">'),
                starter=starter_with("<p>Hello</p>").replace("<body>", '<body data-theme="dark">'), require=[r"data-theme", r"var\(--bg\)"]),
        ),
    ),
    # ------------------------------------------------------------------ 29
    unit(
        "Unit 29 · Capstone pages",
        lesson(
            "Pricing cards",
            """Three plans side by side that stack on small screens - a grid with auto-fit does it with no media query:

.plans { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 16px; }
.plan { border: 1px solid #ddd; border-radius: 12px; padding: 16px; text-align: center; }
.plan--popular { border: 2px solid #1d6ff2; transform: scale(1.03); }

Highlight the recommended plan with a modifier, but don't rely on colour alone: also add a text badge such as 'Most popular'.""",
            mcq("How do pricing cards stack on narrow screens without media queries?", ["auto-fit with minmax", "float", "tables", "position: absolute"], 0),
            mcq("Why add a 'Most popular' text badge as well as colour?", ["Colour alone isn't accessible", "It looks bigger", "Browsers require it", "It is faster"], 0),
            mcq("What does a modifier class like .plan--popular do?", ["Changes one plan's look", "Adds a new component", "Replaces the grid", "Hides plans"], 0),
            run("Build three .plan cards in a .plans grid of auto-fit columns (minmax(160px, 1fr), gap 0, body margin 0, 600px wide container: three 200px columns). The popular plan has a 2px border.", "html",
                [t("columns", selector=".plans", prop="grid-template-columns"), t("plans", selector=".plan", prop="count"), t("popular border", selector=".plan--popular", prop="border-top-width"), t("badge", selector=".plan--popular .badge", prop="text")],
                ["200px 200px 200px", "3", "2px", "Most popular"], styled("body {\n  margin: 0;\n}\n.plans {\n  width: 600px;\n  display: grid;\n  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));\n  gap: 0;\n}\n.plan {\n  border: 1px solid #ddd;\n  box-sizing: border-box;\n}\n.plan--popular {\n  border: 2px solid rgb(29, 111, 242);\n}", '<div class="plans">\n  <div class="plan">Free</div>\n  <div class="plan plan--popular"><span class="badge">Most popular</span> Pro</div>\n  <div class="plan">Team</div>\n</div>'),
                starter=starter_with('<div class="plans">\n  <div class="plan">Free</div>\n  <div class="plan plan--popular"><span class="badge">Most popular</span> Pro</div>\n  <div class="plan">Team</div>\n</div>'), require=[r"auto-fit", r"minmax"]),
        ),
        lesson(
            "Profile card",
            """A profile card combines several skills: a round avatar, text hierarchy, a layout and a call-to-action.

.profile { display: flex; gap: 16px; align-items: center; padding: 16px; border-radius: 12px; }
.avatar { width: 64px; height: 64px; border-radius: 50%; object-fit: cover; }
.name { font-size: 20px; font-weight: 700; margin: 0; }
.role { color: #555; margin: 0; }

Give the image meaningful alt text (the person's name) and make sure text contrast is at least 4.5:1.""",
            mcq("What does object-fit: cover do to the avatar?", ["Fills the circle and crops the overflow", "Stretches it", "Shrinks it", "Hides it"], 0),
            mcq("What contrast ratio is the minimum for normal text?", ["4.5 : 1", "2 : 1", "10 : 1", "1 : 1"], 0),
            mcq("What alt text suits an avatar?", ["The person's name", "avatar.png", "image", "photo of"], 0),
            run("Build a profile: .profile is a flex row with a 16px gap, items centered; .avatar is a 64px circle; .name is 20px and bold.", "html",
                [t("display", selector=".profile", prop="display"), t("gap", selector=".profile", prop="column-gap"), t("align", selector=".profile", prop="align-items"), t("avatar size", selector=".avatar", prop="width"), t("avatar radius", selector=".avatar", prop="border-top-left-radius"), t("name", selector=".name", prop="font-size")],
                ["flex", "16px", "center", "64px", "50%", "20px"], styled(".profile {\n  display: flex;\n  gap: 16px;\n  align-items: center;\n}\n.avatar {\n  width: 64px;\n  height: 64px;\n  border-radius: 50%;\n  background: gray;\n}\n.name {\n  font-size: 20px;\n  font-weight: 700;\n  margin: 0;\n}", '<div class="profile">\n  <div class="avatar"></div>\n  <div><p class="name">Ada Lovelace</p><p class="role">Engineer</p></div>\n</div>'),
                starter=starter_with('<div class="profile">\n  <div class="avatar"></div>\n  <div><p class="name">Ada Lovelace</p><p class="role">Engineer</p></div>\n</div>'), require=[r"border-radius"]),
        ),
        lesson(
            "Article layout",
            """Long-form reading pages share a pattern: a centered column with a readable width, generous line height and clear headings.

.article { max-width: 65ch; margin-inline: auto; padding: 0 16px; line-height: 1.7; }
.article h2 { margin-top: 2em; }
.article img { max-width: 100%; height: auto; }

max-width (not width) lets the column shrink on small screens; margin-inline: auto centers it. img with max-width 100% never overflows its column.""",
            mcq("Why use max-width instead of width for the column?", ["It can shrink on small screens", "It is faster", "It is required for centering", "Width is invalid"], 0),
            mcq("Which centers a block horizontally?", ["margin-inline: auto (with a width)", "text-align: center on the block", "float: center", "position: center"], 0),
            mcq("What does img { max-width: 100%; height: auto } prevent?", ["Overflowing the column and distortion", "Loading", "Alt text", "Borders"], 0),
            run("Style .article: max-width 520px, centered with margin-inline auto (the 600px frame has an 8px body margin, so the side margins compute to 32px), line-height 1.7 (27.2px at 16px text); images are max-width 100% with auto height.", "html",
                [t("max width", selector=".article", prop="max-width"), t("left margin", selector=".article", prop="margin-left"), t("line height", selector=".article", prop="line-height"), t("img", selector=".article img", prop="max-width")],
                ["520px", "32px", "27.2px", "100%"], styled(".article {\n  max-width: 520px;\n  margin-inline: auto;\n  line-height: 1.7;\n}\n.article img {\n  max-width: 100%;\n  height: auto;\n}", '<article class="article">\n  <h1>Title</h1>\n  <p>Text</p>\n  <img alt="" src="x.png">\n</article>'),
                starter=starter_with('<article class="article">\n  <h1>Title</h1>\n  <p>Text</p>\n  <img alt="" src="x.png">\n</article>'), require=[r"max-width", r"margin-inline"]),
        ),
        lesson(
            "Final project: a mini landing page",
            """Combine everything into one page: a header with nav, a hero with a headline and call-to-action, a features grid, and a footer. A checklist:

- Semantic landmarks: header, nav, main, section (with headings), footer
- Tokens (custom properties) for colours and spacing
- A responsive grid for features (auto-fit)
- Accessible: alt text, labelled controls, visible focus, good contrast
- Fast: no heavy images, sizes set, lazy loading below the fold

Build it in small steps and view it at different widths as you go.""",
            order("Order a sensible build.", ["Write semantic HTML for every section", "Add tokens and base typography", "Lay out the hero and features with flex/grid", "Make it responsive and test narrow widths", "Check accessibility and contrast"]),
            mcq("Which should the landing page include?", ["One <main> with sections and headings", "Only divs", "A table layout", "No headings"], 0),
            mcq("What do you check last?", ["Accessibility and contrast", "The page title only", "File names", "Nothing"], 0),
            run("Build the skeleton: a <header> with a <nav>, a <main> containing a hero <section> (an <h1> and a link with class cta) and a features <section> with 3 .feature items, and a <footer>. The test counts the parts.", "html",
                [t("landmarks", selector="header nav", prop="count"), t("h1", selector="main h1", prop="count"), t("cta", selector="main a.cta", prop="count"), t("features", selector="section .feature", prop="count"), t("footer", selector="footer", prop="count")],
                ["1", "1", "1", "3", "1"], page('<header><nav><a href="#">Home</a></nav></header>\n<main>\n  <section class="hero"><h1>Build faster</h1><a class="cta" href="#start">Get started</a></section>\n  <section class="features">\n    <div class="feature">Fast</div>\n    <div class="feature">Simple</div>\n    <div class="feature">Secure</div>\n  </section>\n</main>\n<footer>(c) 2026</footer>'),
                starter=PAGE, require=[r"<footer", r"class=[\"']cta"]),
        ),
    ),
)
