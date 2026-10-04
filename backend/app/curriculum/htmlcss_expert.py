"""HTML & CSS - Expert section, part 1 (units 17-23): typography, the box model, flexbox, grid, colour & effects,
advanced selectors, semantic & accessible HTML. Run exercises render in a script-less 600x400 frame and read back
text, counts, attributes or COMPUTED CSS values."""
from .dsl import code, fill, lesson, mcq, order, run, section, t, unit
from .htmlcss_adv import PAGE, page, starter_with, styled

EXPERT = section(
    "Expert",
    # ------------------------------------------------------------------ 17
    unit(
        "Unit 17 · Typography",
        lesson(
            "Font sizes, line height and rhythm",
            """Readable text needs a comfortable size and spacing:

body { font-size: 16px; line-height: 1.5; }     /* unitless line-height scales with the font */
h1   { font-size: 2rem; }                       /* rem = relative to the root font size */
p    { max-width: 65ch; }                       /* ch = width of a '0': about 65 characters per line is easy to read */

A unitless line-height (1.5) is multiplied by each element's own font-size, so headings and paragraphs both get sensible spacing. Use rem for sizes and em for spacing that should scale with the element's text.""",
            mcq("What does line-height: 1.5 mean for a 20px font?", ["30px", "1.5px", "21.5px", "15px"], 0),
            mcq("What is rem relative to?", ["The root (html) font size", "The parent element", "The viewport", "The screen"], 0),
            mcq("About how many characters per line is easiest to read?", ["45 to 75", "10", "150", "200"], 0),
            run("Style .lead with font-size 20px and line-height 1.5, and set its max-width to 30ch.", "html",
                [t("size", selector=".lead", prop="font-size"), t("line height", selector=".lead", prop="line-height")],
                ["20px", "30px"], styled(".lead {\n  font-size: 20px;\n  line-height: 1.5;\n  max-width: 30ch;\n}", '<p class="lead">Readable text needs space to breathe.</p>'),
                starter=starter_with('<p class="lead">Readable text needs space to breathe.</p>'), require=[r"line-height\s*:\s*1\.5", r"ch"]),
        ),
        lesson(
            "Text styling and truncation",
            """More text controls:

text-transform: uppercase;       letter-spacing: 2px;       text-align: center;
text-decoration: underline;      font-weight: 700;          font-style: italic;

Truncate one line with an ellipsis (all three are needed):

.title { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

For multi-line clamping use -webkit-line-clamp with display: -webkit-box.""",
            mcq("Which three properties make a one-line ellipsis?", ["white-space: nowrap, overflow: hidden, text-overflow: ellipsis", "text-overflow only", "width and height", "display and position"], 0),
            mcq("What does letter-spacing do?", ["Adds space between letters", "Changes the font", "Adds line spacing", "Sets word count"], 0),
            fill("Make the text capitals.", "text-___: uppercase;", "transform"),
            run("Make the h2 uppercase with 2px letter spacing, bold (700) and centered.", "html",
                [t("transform", selector="h2", prop="text-transform"), t("spacing", selector="h2", prop="letter-spacing"), t("weight", selector="h2", prop="font-weight"), t("align", selector="h2", prop="text-align")],
                ["uppercase", "2px", "700", "center"], styled("h2 {\n  text-transform: uppercase;\n  letter-spacing: 2px;\n  font-weight: 700;\n  text-align: center;\n}", "<h2>Sale ends soon</h2>"),
                starter=starter_with("<h2>Sale ends soon</h2>"), require=[r"text-transform", r"letter-spacing"]),
        ),
        lesson(
            "Font stacks and web fonts",
            """font-family takes a STACK: the browser uses the first font that is available, so end with a generic family.

body { font-family: "Inter", "Segoe UI", system-ui, sans-serif; }
code { font-family: ui-monospace, "SFMono-Regular", Menlo, monospace; }

Custom fonts load with @font-face (and should use font-display: swap so text shows immediately):

@font-face { font-family: "Brand"; src: url("brand.woff2") format("woff2"); font-display: swap; }

system-ui gives the operating system's own font: fast, no download.""",
            mcq("Why end a font stack with a generic family like sans-serif?", ["A fallback always exists", "It is faster", "It is required by HTML", "It adds bold"], 0),
            mcq("What does font-display: swap do?", ["Shows fallback text immediately, then swaps", "Hides text until loaded", "Blocks the page", "Removes fonts"], 0),
            mcq("What does system-ui use?", ["The device's own UI font", "A downloaded font", "Times", "A random font"], 0),
            run("Give body the font stack Georgia, serif and make code use a monospace generic family.", "html",
                [t("body stack", selector="body", prop="font-family"), t("code", selector="code", prop="font-family")],
                ["Georgia, serif", "monospace"], styled("body {\n  font-family: Georgia, serif;\n}\ncode {\n  font-family: monospace;\n}", "<p>Use <code>npm test</code> to run the tests.</p>"),
                starter=starter_with("<p>Use <code>npm test</code> to run the tests.</p>"), require=[r"font-family"]),
        ),
    ),
    # ------------------------------------------------------------------ 18
    unit(
        "Unit 18 · The box model, mastered",
        lesson(
            "box-sizing and predictable widths",
            """By default width is the CONTENT width; padding and border are added outside it, which makes layouts hard to predict:

.box { width: 200px; padding: 20px; border: 5px solid; }     /* occupies 250px! */

box-sizing: border-box makes width include padding and border - what you write is what you get:

*, *::before, *::after { box-sizing: border-box; }

Almost every modern stylesheet starts with this reset.""",
            mcq("With content-box, what is the full width of width: 200px + padding: 20px + border: 5px?", ["250px", "200px", "225px", "230px"], 0),
            mcq("With border-box, what does width: 200px mean?", ["Content + padding + border = 200px", "Content only", "Margin included", "Nothing"], 0),
            mcq("Why do most stylesheets set border-box globally?", ["Widths become predictable", "It is faster", "It is required", "It adds borders"], 0),
            run("Make .card exactly 200px wide INCLUDING its 20px padding and 5px border (use box-sizing: border-box). The computed width then reads 200px.", "html",
                [t("box sizing", selector=".card", prop="box-sizing"), t("width", selector=".card", prop="width")],
                ["border-box", "200px"], styled(".card {\n  box-sizing: border-box;\n  width: 200px;\n  padding: 20px;\n  border: 5px solid black;\n}", '<div class="card">Card</div>'),
                starter=starter_with('<div class="card">Card</div>'), require=[r"box-sizing\s*:\s*border-box"]),
        ),
        lesson(
            "Margins, collapsing and spacing systems",
            """Vertical margins between block siblings COLLAPSE: a 30px bottom margin meeting a 20px top margin gives 30px, not 50px (the larger wins). Padding never collapses.

Instead of margins on both sides, give spacing ONE direction - for example a gap on the parent:

.stack { display: flex; flex-direction: column; gap: 16px; }

Use a small scale of spacing values (4, 8, 16, 24, 32px) so the design feels consistent.""",
            mcq("A 30px bottom margin meets a 20px top margin between two blocks. What is the space?", ["30px", "50px", "20px", "10px"], 0),
            mcq("Does padding collapse?", ["No", "Yes", "Only vertically", "Only in flex"], 0),
            mcq("Why use a spacing scale?", ["Consistent rhythm across the design", "It is faster to render", "Browsers require it", "It prevents bugs in HTML"], 0),
            run("Use a column flex container .stack with gap 16px so the three items are spaced without margins.", "html",
                [t("display", selector=".stack", prop="display"), t("direction", selector=".stack", prop="flex-direction"), t("gap", selector=".stack", prop="row-gap"), t("item margin", selector=".stack div", prop="margin-top")],
                ["flex", "column", "16px", "0px"], styled(".stack {\n  display: flex;\n  flex-direction: column;\n  gap: 16px;\n}", '<div class="stack">\n  <div>One</div>\n  <div>Two</div>\n  <div>Three</div>\n</div>'),
                starter=starter_with('<div class="stack">\n  <div>One</div>\n  <div>Two</div>\n  <div>Three</div>\n</div>'), require=[r"gap"]),
        ),
        lesson(
            "aspect-ratio and object-fit",
            """aspect-ratio keeps a box in proportion without padding hacks:

.video { width: 320px; aspect-ratio: 16 / 9; }      /* height becomes 180px */

For images inside a fixed box, object-fit controls scaling: cover fills and crops, contain fits entirely, fill stretches.

img { width: 100%; height: 200px; object-fit: cover; }""",
            mcq("What height does width: 320px; aspect-ratio: 16 / 9 give?", ["180px", "160px", "320px", "90px"], 0),
            mcq("Which object-fit fills the box and crops the overflow?", ["cover", "contain", "fill", "none"], 0),
            mcq("Which object-fit shows the whole image, with empty space if needed?", ["contain", "cover", "crop", "stretch"], 0),
            run("Make .thumb 300px wide with a 3 / 2 aspect ratio. The computed height should be 200px.", "html",
                [t("width", selector=".thumb", prop="width"), t("height", selector=".thumb", prop="height"), t("ratio", selector=".thumb", prop="aspect-ratio")],
                ["300px", "200px", "3 / 2"], styled(".thumb {\n  width: 300px;\n  aspect-ratio: 3 / 2;\n  background: gray;\n}", '<div class="thumb"></div>'),
                starter=starter_with('<div class="thumb"></div>'), require=[r"aspect-ratio"]),
        ),
    ),
    # ------------------------------------------------------------------ 19
    unit(
        "Unit 19 · Flexbox, mastered",
        lesson(
            "flex-grow, shrink and basis",
            """Flex items can grow to fill free space, shrink when there isn't enough, and start from a basis size. The shorthand flex: grow shrink basis:

.sidebar { flex: 0 0 200px; }     /* fixed 200px: no grow, no shrink */
.main    { flex: 1; }             /* take all the remaining space */

flex: 1 means flex: 1 1 0. Items with grow 1 and 2 share free space in a 1:2 ratio.""",
            mcq("What does flex: 1 do?", ["Takes the remaining free space", "Sets width to 1px", "Hides the item", "Disables shrinking only"], 0),
            mcq("What does flex: 0 0 200px mean?", ["Fixed 200px: no grow, no shrink", "Grow twice", "Shrink to 0", "Nothing"], 0),
            mcq("Two items with flex-grow 1 and 3 share free space as…", ["1 : 3", "3 : 1", "Equally", "Randomly"], 0),
            run("In the 600px-wide .row (display: flex), make .side fixed 200px (flex: 0 0 200px) and .main fill the rest (flex: 1). Body margin is 0, so .main should be 400px wide.", "html",
                [t("side", selector=".side", prop="width"), t("main", selector=".main", prop="width")],
                ["200px", "400px"], styled("body {\n  margin: 0;\n}\n.row {\n  display: flex;\n  width: 600px;\n}\n.side {\n  flex: 0 0 200px;\n}\n.main {\n  flex: 1;\n}", '<div class="row">\n  <div class="side">Side</div>\n  <div class="main">Main</div>\n</div>'),
                starter=starter_with('<div class="row">\n  <div class="side">Side</div>\n  <div class="main">Main</div>\n</div>'), require=[r"flex"]),
        ),
        lesson(
            "Alignment and centering",
            """Two axes: justify-content works along the main axis, align-items across it. Perfect centering:

.center { display: flex; justify-content: center; align-items: center; }

Other values: flex-start, flex-end, space-between, space-around, space-evenly (main axis); stretch, baseline (cross axis). align-self overrides the alignment for ONE item. margin-left: auto pushes an item to the far end.""",
            mcq("Which centers children both ways in a flex container?", ["justify-content: center + align-items: center", "text-align: center", "margin: auto only", "float: center"], 0),
            mcq("Which spreads items with the first and last at the edges?", ["space-between", "space-around", "center", "stretch"], 0),
            mcq("What does align-self do?", ["Aligns one item differently", "Aligns the container", "Aligns text", "Sets order"], 0),
            run("Center the .dot both horizontally and vertically in a 600 x 200 flex box (body margin 0). The dot stays 40px square.", "html",
                [t("justify", selector=".box", prop="justify-content"), t("align", selector=".box", prop="align-items"), t("display", selector=".box", prop="display"), t("dot width", selector=".dot", prop="width")],
                ["center", "center", "flex", "40px"], styled("body {\n  margin: 0;\n}\n.box {\n  display: flex;\n  justify-content: center;\n  align-items: center;\n  width: 600px;\n  height: 200px;\n}\n.dot {\n  width: 40px;\n  height: 40px;\n  background: tomato;\n}", '<div class="box"><div class="dot"></div></div>'),
                starter=starter_with('<div class="box"><div class="dot"></div></div>'), require=[r"justify-content", r"align-items"]),
        ),
        lesson(
            "Wrapping and the holy grail",
            """flex-wrap: wrap lets items flow onto new lines instead of shrinking. The classic header / sidebar / content / footer page is easy with column flexbox:

body { display: flex; flex-direction: column; min-height: 100vh; }
main { flex: 1; }          /* pushes the footer to the bottom */

order can rearrange items visually, but keep DOM order = reading order for accessibility.""",
            mcq("What does flex-wrap: wrap do?", ["Lets items move to a new line", "Hides overflow", "Wraps text only", "Centers items"], 0),
            mcq("What does main { flex: 1 } do in a column body?", ["Fills the space so the footer sits at the bottom", "Hides main", "Shrinks main", "Adds a border"], 0),
            mcq("Why avoid reordering with order for content?", ["Screen reader and keyboard order follow the DOM", "It's slower", "It's removed", "It breaks colours"], 0),
            run("Make .tags a wrapping flex container 300px wide with gap 0; six 100px-wide tags should wrap to 2 rows. Tags are 30px high, so the container should compute to a 60px height.", "html",
                [t("wrap", selector=".tags", prop="flex-wrap"), t("container height", selector=".tags", prop="height")],
                ["wrap", "60px"], styled("body {\n  margin: 0;\n}\n.tags {\n  display: flex;\n  flex-wrap: wrap;\n  width: 300px;\n}\n.tag {\n  width: 100px;\n  height: 30px;\n  box-sizing: border-box;\n}", '<div class="tags">\n  <div class="tag">1</div>\n  <div class="tag">2</div>\n  <div class="tag">3</div>\n  <div class="tag">4</div>\n  <div class="tag">5</div>\n  <div class="tag">6</div>\n</div>'),
                starter=starter_with('<div class="tags">\n  <div class="tag">1</div>\n  <div class="tag">2</div>\n  <div class="tag">3</div>\n  <div class="tag">4</div>\n  <div class="tag">5</div>\n  <div class="tag">6</div>\n</div>'), require=[r"flex-wrap"]),
        ),
    ),
    # ------------------------------------------------------------------ 20
    unit(
        "Unit 20 · Grid, mastered",
        lesson(
            "Explicit grids and fr units",
            """grid-template-columns defines the columns; fr is a share of the free space:

.grid { display: grid; grid-template-columns: 100px 1fr 2fr; gap: 10px; }

In a 600px grid with gap 10px: 600 - 100 - 20 = 480px free, split 1 : 2 -> 160px and 320px. Rows can be set with grid-template-rows, and implicit rows are sized by grid-auto-rows.""",
            mcq("What is 1fr?", ["One share of the free space", "One pixel", "One row", "One percent"], 0),
            mcq("In 600px with columns 100px 1fr 2fr and gap 10px, how wide is the 1fr column?", ["160px", "200px", "100px", "320px"], 0),
            mcq("What sizes rows created automatically?", ["grid-auto-rows", "grid-rows", "row-size", "auto-flow"], 0),
            run("Make .grid 600px wide with columns 100px 1fr 2fr and a 10px gap. The 1fr column should compute to 160px.", "html",
                [t("columns", selector=".grid", prop="grid-template-columns"), t("column gap", selector=".grid", prop="column-gap")],
                ["100px 160px 320px", "10px"], styled("body {\n  margin: 0;\n}\n.grid {\n  display: grid;\n  width: 600px;\n  grid-template-columns: 100px 1fr 2fr;\n  gap: 10px;\n}", '<div class="grid">\n  <div>A</div>\n  <div>B</div>\n  <div>C</div>\n</div>'),
                starter=starter_with('<div class="grid">\n  <div>A</div>\n  <div>B</div>\n  <div>C</div>\n</div>'), require=[r"1fr", r"2fr"]),
        ),
        lesson(
            "Spanning and placing items",
            """Items can span several tracks:

.wide { grid-column: 1 / 3; }          /* from line 1 to line 3 = spans 2 columns */
.tall { grid-row: span 2; }
.hero { grid-column: 1 / -1; }          /* -1 = the last line: spans every column */

Lines are numbered from 1; a grid with 3 columns has 4 column lines. Overlapping items can share cells.""",
            mcq("What does grid-column: 1 / -1 do?", ["Spans every column", "Hides the item", "Places it in column 1 only", "Reverses columns"], 0),
            mcq("How many column lines does a 3-column grid have?", ["4", "3", "2", "6"], 0),
            mcq("What does grid-row: span 2 mean?", ["The item covers two rows", "Row number 2", "Two items", "Skip 2 rows"], 0),
            run("In a 3-column grid of 100px columns (body margin 0), make .hero span all columns. Its width should compute to 300px.", "html",
                [t("hero width", selector=".hero", prop="width"), t("hero column", selector=".hero", prop="grid-column-start"), t("card width", selector=".card", prop="width")],
                ["300px", "1", "100px"], styled("body {\n  margin: 0;\n}\n.grid {\n  display: grid;\n  grid-template-columns: repeat(3, 100px);\n}\n.hero {\n  grid-column: 1 / -1;\n}", '<div class="grid">\n  <div class="hero">Hero</div>\n  <div class="card">1</div>\n  <div class="card">2</div>\n  <div class="card">3</div>\n</div>'),
                starter=starter_with('<div class="grid">\n  <div class="hero">Hero</div>\n  <div class="card">1</div>\n  <div class="card">2</div>\n  <div class="card">3</div>\n</div>'), require=[r"grid-column"]),
        ),
        lesson(
            "Grid alignment and auto-placement",
            """grid-auto-flow controls how items fill the grid: row (default), column, or dense (fill holes). Alignment inside cells: justify-items and align-items (items), justify-content and align-content (the whole grid inside its container), place-items: center is the shortcut for both items axes.

.grid { display: grid; place-items: center; }

Use grid for two-dimensional layout (rows AND columns together) and flexbox for one dimension.""",
            mcq("Which shortcut centers items in their cells both ways?", ["place-items: center", "text-align: center", "margin: auto", "align: center"], 0),
            mcq("What does grid-auto-flow: dense do?", ["Fills holes with later items", "Makes the grid smaller", "Removes gaps", "Sorts items"], 0),
            mcq("When is grid better than flex?", ["Two-dimensional layouts", "A single row of buttons", "Inline text", "Animations"], 0),
            run("Make .grid a 2-column grid of 150px columns where each cell's item is centered with place-items: center. The 40px square .dot keeps its size.", "html",
                [t("justify", selector=".grid", prop="justify-items"), t("align", selector=".grid", prop="align-items"), t("dot width", selector=".dot", prop="width")],
                ["center", "center", "40px"], styled("body {\n  margin: 0;\n}\n.grid {\n  display: grid;\n  grid-template-columns: 150px 150px;\n  grid-auto-rows: 100px;\n  place-items: center;\n}\n.dot {\n  width: 40px;\n  height: 40px;\n  background: teal;\n}", '<div class="grid">\n  <div class="dot"></div>\n</div>'),
                starter=starter_with('<div class="grid">\n  <div class="dot"></div>\n</div>'), require=[r"place-items|justify-items"]),
        ),
    ),
    # ------------------------------------------------------------------ 21
    unit(
        "Unit 21 · Colour, backgrounds & effects",
        lesson(
            "Colour formats and transparency",
            """CSS colours can be named, hex, rgb(), hsl() - and most can carry transparency:

color: #1d6ff2;            color: rgb(29 111 242);
color: hsl(217 89% 53%);   background: rgb(0 0 0 / 50%);     /* 50% transparent black */
currentColor               /* the element's own text colour: borders and icons can follow it */

opacity fades the WHOLE element (including its children); an rgb()/hsl() alpha affects only that colour. HSL is easy to adjust: change lightness for a lighter or darker shade.""",
            mcq("What does opacity: 0.5 affect?", ["The whole element including children", "Only the background", "Only the text", "Only the border"], 0),
            mcq("Which is 50% transparent black?", ["rgb(0 0 0 / 50%)", "rgb(0 0 0 50)", "black 50", "#000000"], 0),
            mcq("What does currentColor mean?", ["The element's text colour", "The page background", "The browser theme", "The last colour used"], 0),
            run("Give .badge a text colour of rgb(255, 255, 255), a background of rgb(29, 111, 242) and a border that follows the text colour (border: 2px solid currentColor).", "html",
                [t("color", selector=".badge", prop="color"), t("background", selector=".badge", prop="background-color"), t("border color", selector=".badge", prop="border-top-color")],
                ["rgb(255, 255, 255)", "rgb(29, 111, 242)", "rgb(255, 255, 255)"], styled(".badge {\n  color: white;\n  background: rgb(29, 111, 242);\n  border: 2px solid currentColor;\n}", '<span class="badge">New</span>'),
                starter=starter_with('<span class="badge">New</span>'), require=[r"currentColor"]),
        ),
        lesson(
            "Shadows and borders",
            """box-shadow adds depth: offset-x offset-y blur spread colour.

.card { box-shadow: 0 2px 8px rgb(0 0 0 / 15%); }      /* soft shadow */
.card:hover { box-shadow: 0 8px 24px rgb(0 0 0 / 25%); }

border-radius rounds corners (50% makes a circle from a square). outline draws outside the border and doesn't change layout - ideal for focus rings. text-shadow does the same for text.""",
            mcq("What does 50% border-radius do to a square?", ["Makes a circle", "Makes a diamond", "Hides it", "Adds a border"], 0),
            mcq("Why is outline good for focus rings?", ["It doesn't change layout", "It's faster", "It's thicker", "It's required"], 0),
            mcq("In box-shadow: 0 2px 8px black, what is 8px?", ["The blur radius", "The x offset", "The colour", "The spread only"], 0),
            run("Make the .avatar a 80px circle (border-radius 50%) with a 3px solid rgb(29, 111, 242) border.", "html",
                [t("radius", selector=".avatar", prop="border-top-left-radius"), t("border width", selector=".avatar", prop="border-top-width"), t("border color", selector=".avatar", prop="border-top-color")],
                ["50%", "3px", "rgb(29, 111, 242)"], styled(".avatar {\n  width: 80px;\n  height: 80px;\n  border-radius: 50%;\n  border: 3px solid rgb(29, 111, 242);\n  box-sizing: border-box;\n}", '<div class="avatar"></div>'),
                starter=starter_with('<div class="avatar"></div>'), require=[r"border-radius"]),
        ),
        lesson(
            "Gradients and filters",
            """Gradients are generated images: background: linear-gradient(135deg, #6366f1, #ec4899); a radial-gradient(circle, ...) glows from the centre. Layer several backgrounds separated by commas; the first is on top.

Filters change the look of an element: filter: blur(4px) grayscale(100%) brightness(1.2); backdrop-filter: blur(8px) blurs what is BEHIND a translucent element (frosted glass).

Keep text contrast readable over any gradient.""",
            mcq("What does backdrop-filter: blur(8px) blur?", ["What's behind the element", "The element's text", "The page", "The cursor"], 0),
            mcq("Which background layer is on top when several are listed?", ["The first", "The last", "The biggest", "None"], 0),
            mcq("What does filter: grayscale(100%) do?", ["Removes colour", "Adds a grey border", "Makes it smaller", "Hides it"], 0),
            run("Give .hero a linear-gradient background (any two colours) and apply filter: grayscale(100%) to .photo. The test checks the background-image starts with linear-gradient and the filter value.", "html",
                [t("gradient", selector=".hero", prop="background-image"), t("filter", selector=".photo", prop="filter")],
                ["linear-gradient(135deg, rgb(99, 102, 241), rgb(236, 72, 153))", "grayscale(1)"], styled(".hero {\n  height: 100px;\n  background: linear-gradient(135deg, #6366f1, #ec4899);\n}\n.photo {\n  filter: grayscale(100%);\n  width: 40px;\n  height: 40px;\n  background: tomato;\n}", '<div class="hero"></div>\n<div class="photo"></div>'),
                starter=starter_with('<div class="hero"></div>\n<div class="photo"></div>'), require=[r"linear-gradient", r"grayscale"]),
        ),
    ),
    # ------------------------------------------------------------------ 22
    unit(
        "Unit 22 · Selectors for experts",
        lesson(
            ":not, :is, :where and :has",
            """Modern selectors cut repetition:

button:not(.primary) { ... }        /* every button except .primary */
:is(h1, h2, h3) a { ... }           /* one rule for many parents (takes the highest specificity inside) */
:where(h1, h2, h3) a { ... }        /* same, but with ZERO specificity - easy to override */
.card:has(img) { ... }              /* style a parent based on its children! */
li:has(> input:checked) { ... }

:has() is the 'parent selector' CSS never had.""",
            mcq("What does .card:has(img) select?", ["Cards that contain an image", "Images in cards", "The card's image only", "Cards next to an image"], 0),
            mcq("What is special about :where()?", ["It adds zero specificity", "It is faster", "It selects parents", "It negates"], 0),
            mcq("Which selects every button except .primary?", ["button:not(.primary)", "button.not(primary)", "button!primary", "button:except(.primary)"], 0),
            run("Make every button except the .primary one have a grey (rgb(128, 128, 128)) text colour using :not(). The primary one keeps rgb(0, 0, 0).", "html",
                [t("normal", selector="#a", prop="color"), t("primary", selector="#b", prop="color")],
                ["rgb(128, 128, 128)", "rgb(0, 0, 0)"], styled("button:not(.primary) {\n  color: rgb(128, 128, 128);\n}", '<button id="a">Cancel</button>\n<button id="b" class="primary">Save</button>'),
                starter=starter_with('<button id="a">Cancel</button>\n<button id="b" class="primary">Save</button>'), require=[r":not\("]),
        ),
        lesson(
            "nth-child formulas",
            """:nth-child(an + b) picks repeating patterns:

li:nth-child(odd)       /* 1st, 3rd, 5th ... */
li:nth-child(even)
li:nth-child(3n)        /* every 3rd */
li:nth-child(3n + 1)    /* 1st, 4th, 7th ... */
li:nth-child(n + 4)     /* from the 4th onward */
li:nth-last-child(1)    /* the last (like :last-child) */

Great for zebra striping tables and grid edge cases.""",
            mcq("Which items does li:nth-child(3n) select?", ["3rd, 6th, 9th...", "1st, 4th, 7th...", "Only the 3rd", "Every item"], 0),
            mcq("Which items does :nth-child(n + 4) select?", ["The 4th onward", "The first 4", "Only the 4th", "Every 4th"], 0),
            mcq("Which gives zebra stripes starting with a coloured first row?", [":nth-child(odd)", ":nth-child(even)", ":first-child", ":last-child"], 0),
            run("Zebra-stripe the list: odd items get background rgb(240, 240, 240).", "html",
                [t("1st", selector="li:nth-child(1)", prop="background-color"), t("2nd", selector="li:nth-child(2)", prop="background-color"), t("3rd", selector="li:nth-child(3)", prop="background-color")],
                ["rgb(240, 240, 240)", "rgba(0, 0, 0, 0)", "rgb(240, 240, 240)"], styled("li:nth-child(odd) {\n  background: rgb(240, 240, 240);\n}", "<ul>\n  <li>One</li>\n  <li>Two</li>\n  <li>Three</li>\n</ul>"),
                starter=starter_with("<ul>\n  <li>One</li>\n  <li>Two</li>\n  <li>Three</li>\n</ul>"), require=[r"nth-child"]),
        ),
        lesson(
            "Generated content & counters",
            """::before and ::after insert content that doesn't exist in the HTML - decoration only, never essential information:

.required::after { content: " *"; color: red; }
blockquote::before { content: "\\201C"; }       /* a curly quote */

CSS counters number things automatically:

ol.steps { counter-reset: step; }
ol.steps li::before { counter-increment: step; content: "Step " counter(step) ": "; }

Screen readers may or may not read generated content - don't put important text in it.""",
            mcq("Which property is required for ::before to appear?", ["content", "display", "text", "value"], 0),
            mcq("What does counter-increment do?", ["Increases the counter for each element", "Resets it", "Prints it", "Sorts items"], 0),
            mcq("Should essential information live in ::before content?", ["No - decoration only", "Yes", "Only for headings", "Only for lists"], 0),
            code("Write a CSS rule that inserts the text 'Tip: ' before every .tip element, using ::before and the content property.", [r"\.tip\s*::?before", r"content\s*:\s*[\"']Tip: [\"']"], '.tip::before {\n  content: "Tip: ";\n}',
                 starter=".tip::before {\n  \n}", hint="content takes a quoted string."),
        ),
    ),
    # ------------------------------------------------------------------ 23
    unit(
        "Unit 23 · Semantic, accessible HTML",
        lesson(
            "Landmarks and document outline",
            """Landmark elements tell browsers and screen readers what each region is:

<header>  <nav>  <main>  <aside>  <footer>  <section aria-labelledby="...">  <article>

Use ONE <main> per page. Headings give the outline: one <h1>, then <h2> for sections, <h3> inside them - never skip levels just for size (use CSS for appearance). Screen reader users jump between landmarks and headings to navigate.""",
            mcq("How many <main> elements should a page have?", ["One", "Two", "As many as you like", "None"], 0),
            mcq("Why not skip from <h1> to <h4> for a smaller look?", ["It breaks the outline; use CSS for size", "It is invalid HTML", "Browsers refuse it", "It slows loading"], 0),
            mcq("What is <nav> for?", ["A block of navigation links", "A footer", "A form", "An image"], 0),
            run("Build a page skeleton with a <header>, one <nav>, one <main> and a <footer>. The test counts each landmark.", "html",
                [t("header", selector="header", prop="count"), t("nav", selector="nav", prop="count"), t("main", selector="main", prop="count"), t("footer", selector="footer", prop="count")],
                ["1", "1", "1", "1"], page('<header><h1>My site</h1></header>\n<nav><a href="/">Home</a></nav>\n<main><p>Content</p></main>\n<footer>Footer</footer>'),
                starter=PAGE, require=[r"<main"]),
        ),
        lesson(
            "Accessible names and alt text",
            """Every control needs an accessible NAME. Buttons and links get theirs from their text; form fields from a <label>; icon-only buttons need aria-label.

<label for="email">Email</label> <input id="email" type="email">
<button aria-label="Close dialog">×</button>
<img src="chart.png" alt="Sales rose 20% in March">

Alt text describes the image's PURPOSE (empty alt="" for purely decorative images so they are skipped). Never write 'image of'.""",
            mcq("What should alt text describe?", ["The image's purpose or content", "The file name", "The image size", "'image of'"], 0),
            mcq("Which gives an icon-only button a name?", ["aria-label", "title only", "color", "id"], 0),
            mcq("What alt value is right for a purely decorative image?", ['alt=""', "alt='image'", "No attribute", "alt='decoration.png'"], 0),
            run("Make a labelled email field: an input with id email and a <label for=\"email\"> reading Email. Also add an icon-only close <button> with aria-label \"Close\". The test checks the label text and the aria-label.", "html",
                [t("label", selector="label[for=email]", prop="text"), t("input", selector="input#email", prop="attr:type"), t("aria", selector="button", prop="attr:aria-label")],
                ["Email", "email", "Close"], page('<label for="email">Email</label>\n<input id="email" type="email">\n<button aria-label="Close">×</button>'),
                starter=PAGE, require=[r"aria-label", r"for=[\"']email"]),
        ),
        lesson(
            "Native widgets: details, dialog and tables",
            """Prefer built-in elements - they come with keyboard support and accessibility for free:

<details><summary>Shipping info</summary> Free over $50. </details>      collapsible content
<dialog id="d">...</dialog>      a modal with d.showModal() (focus trapping and Esc built in)

Data tables: <table><caption>Prices</caption><thead><tr><th scope="col">Item</th><th scope="col">Cost</th></tr></thead><tbody>...</tbody></table>

Use tables for DATA, never for layout. <th scope> tells assistive tech which cells each header describes.""",
            mcq("Which element makes collapsible content with no JavaScript?", ["<details>", "<collapse>", "<toggle>", "<fold>"], 0),
            mcq("What does <th scope=\"col\"> tell assistive technology?", ["The header describes the column below", "The header is bold", "The cell is hidden", "The table has columns"], 0),
            mcq("Should you use tables for page layout?", ["No - for data only", "Yes", "Only on desktops", "Only in email"], 0),
            run("Create a <details> with a <summary> reading More info and a paragraph inside, plus a small table with a <caption>Prices</caption>, a <thead> with two <th scope=\"col\"> cells and one body row. The test counts these parts.", "html",
                [t("summary", selector="details > summary", prop="text"), t("caption", selector="table caption", prop="text"), t("col headers", selector="th[scope=col]", prop="count"), t("body rows", selector="tbody tr", prop="count")],
                ["More info", "Prices", "2", "1"], page('<details>\n  <summary>More info</summary>\n  <p>Hidden until opened.</p>\n</details>\n<table>\n  <caption>Prices</caption>\n  <thead><tr><th scope="col">Item</th><th scope="col">Cost</th></tr></thead>\n  <tbody><tr><td>Pen</td><td>$2</td></tr></tbody>\n</table>'),
                starter=PAGE, require=[r"<details", r"<caption"]),
        ),
    ),
)
