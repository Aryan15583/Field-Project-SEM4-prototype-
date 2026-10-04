"""HTML & CSS - plain-language rewrites of the Beginner lesson texts (questions unchanged). Keyed "<unit>/<lesson>"."""

INTROS = {
    "1/1": """HTML describes the CONTENT of a web page using TAGS. A tag is a word in angle brackets that tells the browser what something is. Most tags come in pairs - an OPENING tag and a CLOSING tag (with a slash):

<p>Welcome to my page.</p>

Every page has the same frame. Think of it like a book with a cover page (head) and the pages you read (body):

<!DOCTYPE html>
<html>
  <head>
    <title>My page</title>
  </head>
  <body>
    <h1>Hello!</h1>
    <p>Welcome to my page.</p>
  </body>
</html>

- <head> holds information ABOUT the page, like its title (shown on the browser tab). Visitors don't see it on the page.
- <body> holds everything the visitor SEES.
- Tags can sit INSIDE other tags - that is how a page gets its structure.

In this lesson you will learn: the frame of every web page and what goes where.""",
    "1/2": """Headings work like the titles in a book. There are six levels:

<h1>  the biggest, most important title (use one per page)
<h2>  a chapter title
<h3> ... down to <h6>

Use them IN ORDER, like an outline: h1, then h2 sections, then h3 inside those. Don't pick a heading just because of its size - pick it for its meaning.

<p> makes a paragraph of text.

Two special tags have no closing partner because they don't wrap any content:
<br>   a line break (like pressing Enter inside a paragraph)
<hr>   a horizontal line across the page

A thing to know: browsers squash extra spaces and blank lines in your HTML into a single space. To start a new paragraph, you need a new <p> - pressing Enter in your code isn't enough.

In this lesson you will learn: how to structure text with headings and paragraphs.""",
    "1/3": """Tags can also mark up single words INSIDE a sentence:

<strong>important</strong>   shown bold, and tells screen readers it is important
<em>emphasis</em>            shown in italics, like stressing a word when you speak
<code>print()</code>         shows computer code
<mark>highlight</mark>       highlighted, like a marker pen

Tip: prefer <strong> and <em> (they describe MEANING) over <b> and <i> (which only describe how it LOOKS). Meaning helps people who use screen readers.

What if you want to show a < sign in text? The browser would think it starts a tag! Use special codes (called entities):

&lt;   shows <
&gt;   shows >
&amp;  shows &

In this lesson you will learn: how to emphasise words and show special characters.""",
    "2/1": """A LINK takes the visitor to another page when clicked. It uses the <a> tag (a for "anchor"). The place it goes to is in an ATTRIBUTE called href (extra information inside the opening tag):

<a href="https://example.com">Visit Example</a>

The words between the tags are what people see and click.

Where can a link go?
<a href="about.html">About us</a>          another page on your own site
<a href="#contact">Jump to contact</a>     a spot on the same page (the element with id="contact")
<a href="mailto:hi@example.com">Email</a>  opens an email

To open the link in a new tab, add target="_blank". For safety also add rel="noopener", which stops the new page from controlling yours.

In this lesson you will learn: how to make links to other pages, to spots on a page, and to email.""",
    "2/2": """The <img> tag shows a picture. It has no closing tag because it wraps no content:

<img src="cat.jpg" alt="A ginger cat asleep on a sofa" width="300">

Its attributes:
- src - where the picture file is (its source).
- alt - a short written description of the picture. This is IMPORTANT: it is read aloud to people who can't see the picture, and it appears if the picture fails to load.
- width - how wide to show it, in pixels.

Write alt text that describes the picture's meaning, like you would to a friend on the phone. For a picture that is purely decoration, use an empty alt: alt="".

In this lesson you will learn: how to show images, and why alt text matters.""",
    "2/3": """Lists present items neatly. There are two kinds.

A bulleted list (unordered) - use <ul>:

<ul>
  <li>Milk</li>
  <li>Eggs</li>
</ul>

A numbered list (ordered) - use <ol>:

<ol>
  <li>Preheat</li>
  <li>Bake</li>
</ol>

Every item in either kind is an <li> (list item). The browser adds the bullets or numbers for you.

You can put a list INSIDE an item to make sub-points:

<ul>
  <li>Fruit
    <ul><li>Apple</li><li>Pear</li></ul>
  </li>
</ul>

Use <ol> when order matters (steps) and <ul> when it doesn't (a shopping list).

In this lesson you will learn: how to make bulleted and numbered lists.""",
    "3/1": """A page is more than a heap of paragraphs: it has a header, a menu, main content, and a footer. SEMANTIC tags give each part a name that says what it IS - helpful for search engines and for people using screen readers.

<header>   the top of the page (logo, title)
<nav>      the main menu of links
<main>     the main content (only one per page)
<article>  a self-contained piece, like a blog post
<section>  a themed group of content
<aside>    side content related to the main content
<footer>   the bottom (contact, copyright)

Compare with <div> and <span>: these are generic boxes with NO meaning. They are useful for grouping things for styling, but whenever a meaningful tag fits, use that one instead.

Think of a newspaper: front-page headline, menu of sections, articles, sidebars, and a footer. Semantic tags are the labels for those parts.

In this lesson you will learn: how to give the parts of a page meaningful names.""",
    "3/2": """A table shows data in rows and columns, like a spreadsheet.

<table>
  <thead>
    <tr><th>Name</th><th>Score</th></tr>
  </thead>
  <tbody>
    <tr><td>Ada</td><td>95</td></tr>
  </tbody>
</table>

The tags:
- <table> the whole table
- <tr> a table ROW
- <th> a HEADER cell (the column title, shown bold)
- <td> a normal DATA cell
- <thead> and <tbody> group the top row(s) and the main rows

Read the example: one header row (Name, Score) and one data row (Ada, 95).

Important: use tables only for DATA - things that really are rows and columns. Don't use tables to lay out the page; there are better tools for that (you will meet them soon).

In this lesson you will learn: how to show data in a table.""",
    "3/3": """A FORM lets visitors type information into the page - signing up, searching, sending a message.

<form action="/signup" method="post">
  <label for="email">Email</label>
  <input id="email" name="email" type="email" required>
  <button type="submit">Sign up</button>
</form>

The pieces:
- <form> wraps the whole thing. action says where the data is sent.
- <input> is a box to type in. Its type changes how it behaves: text, email, password, number, checkbox, radio, date...
- required stops the form being sent if the box is empty.
- <button type="submit"> sends the form.
- <label> is the visible name of the box. Linking it to the input (for="email" matches id="email") makes the label clickable and lets screen readers announce it. Every input should have one.

In this lesson you will learn: how to collect input from visitors.""",
    "4/1": """HTML says WHAT is on the page; CSS says HOW it looks. A CSS rule has two parts: a SELECTOR (which elements) and DECLARATIONS (what to change):

p {
  color: navy;
  background-color: lightyellow;
}

Read it: "for every paragraph, make the text navy and the background light yellow."

Each declaration is property: value; - and ends with a semicolon.

Where does CSS go? Put it in a <style> element inside <head>, or in a separate .css file that you link to the page.

Colours can be written as a name (red), a hex code (#ff0000), or rgb(255, 0, 0). They are all just different ways of saying the same thing; hex and rgb give you millions of choices.

In this lesson you will learn: how to write CSS rules and colour things.""",
    "4/2": """So far a selector like p styled EVERY paragraph. To style only some, you give elements names with attributes, and select them:

.card { ... }      a CLASS selector (starts with a dot) - for any elements marked class="card". Many elements can share a class.
#logo { ... }      an ID selector (starts with #) - for the ONE element marked id="logo".
nav a { ... }      a descendant selector - every <a> that sits inside a <nav>.
h1, h2 { ... }     a group - styles both at once.

In the HTML: <div class="card"> and <img id="logo">.

What if two rules disagree? The more SPECIFIC one wins: an id beats a class, and a class beats a plain tag. That makes sense - pointing at one particular thing is more precise than a general rule.

In this lesson you will learn: how to style particular elements, and what happens when rules clash.""",
    "4/3": """CSS has many properties for text:

font-family: Georgia, serif;    the typeface. The extras after the comma are backups, in case the first isn't available.
font-size: 20px;                how big the letters are
font-weight: 700;               how thick (700 = bold)
line-height: 1.5;               the space between lines (1.5 = one and a half times the text size)
text-align: center;             left, center or right
text-transform: uppercase;      makes the letters capitals (or lowercase)
letter-spacing: 2px;            the gap between letters

Good reading comfort: a line-height of about 1.5 makes paragraphs much easier on the eyes.

Try changing the numbers and watch the preview - you can't break anything!

In this lesson you will learn: how to style the look of text.""",
    "5/1": """Here is a secret: every element on a page is a BOX, and CSS lets you control the spacing. Picture a framed photo on a wall:

  margin   - the gap OUTSIDE the frame, between this picture and its neighbours
  border   - the frame itself
  padding  - the space INSIDE the frame, between the frame and the photo (like a mat)
  content  - the photo

padding: 10px;           the same on all four sides
padding: 10px 20px;      10px top and bottom, 20px left and right
margin: 0 auto;          centre a box that has a set width (auto splits the leftover space equally)

Remember: padding is INSIDE, margin is OUTSIDE.

In this lesson you will learn: how to control the space inside and outside a box.""",
    "5/2": """Two more box ideas.

BORDER - a line around the box. Three values: thickness, style, colour.
border: 2px solid black;

ROUNDED CORNERS:
border-radius: 8px;     (50% on a square makes a circle!)

A surprise about size: by default, setting a width sets only the CONTENT width. The padding and border are then ADDED on top, so the box ends up wider than you asked for. That is confusing.

The fix is one line that most websites use:

*, *::before, *::after { box-sizing: border-box; }

With border-box, the width you set INCLUDES the padding and border - the box is exactly the width you wrote. Much easier to plan layouts!

In this lesson you will learn: borders, rounded corners, and the box-sizing fix.""",
    "5/3": """Different elements behave differently on the page. The display property controls this:

block         takes the full width and starts on a new line (div, p, h1 are like this)
inline        flows inside a line of text; width and height are ignored (span, a)
inline-block  flows in the line like text, but accepts a width and a height
none          the element is completely hidden and takes up no space

There is a sibling: visibility: hidden hides the element, but its space stays empty, like an invisible person standing in the queue.

Think of block as a paragraph and inline as a single word within it.

In this lesson you will learn: how elements flow on the page and how to hide them.""",
    "6/1": """Making elements sit side by side used to be hard. FLEXBOX makes it easy. Turn on flex for a parent, and its children line up in a row:

.row {
  display: flex;
  gap: 16px;               space between the children
  flex-direction: row;     the direction: row, or column for top to bottom
  flex-wrap: wrap;         let items move to a new line when there isn't room
}

.item { flex: 1; }         every item takes an equal share of the free space

Imagine a shelf: display: flex puts the books on the shelf in a row; gap is the space between them; flex: 1 makes the books stretch to fill it evenly.

Flexbox works in ONE direction at a time (a row or a column).

In this lesson you will learn: how to put elements side by side in a flexible row.""",
    "6/2": """A flex container has two directions:
- the MAIN axis - the way the items flow (a row goes left to right).
- the CROSS axis - the other direction, at right angles.

Two properties place the items:

justify-content   places them along the MAIN axis:   flex-start | center | space-between | space-around
align-items       places them along the CROSS axis:  stretch | center | flex-start | flex-end

space-between pushes the first and last items to the edges and spreads the rest evenly. center bunches them in the middle.

The famous trick - perfectly centre something both ways:

.center {
  display: flex;
  justify-content: center;
  align-items: center;
}

In this lesson you will learn: how to position and centre items in a flex container.""",
    "6/3": """Flexbox lays things out in one direction. CSS GRID works in rows AND columns at the same time - perfect for galleries and page layouts.

.gallery {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

Read it: "make a grid with 3 columns, each taking an equal share, with 8px gaps." Items then fill the grid cell by cell, left to right, row by row.

fr means "a fraction of the free space". 1fr 1fr 1fr is three equal columns; 2fr 1fr gives the first column twice the width of the second.

You can make one item span more than one column:

grid-column: span 2;

A rule of thumb: use flexbox for one row or one column of things; use grid for a full two-dimensional layout.

In this lesson you will learn: how to lay out items in rows and columns.""",
    "7/1": """You can write colours in several ways. They all describe the same thing - a mix of red, green and blue light:

#1d6ff2              hex: a code made of three pairs (red, green, blue)
rgb(29, 111, 242)    the same colour: red, green, blue, each from 0 to 255
rgb(0 0 0 / 50%)     with transparency (50% see-through)
hsl(220 90% 53%)     hue (colour wheel position), saturation, lightness

For backgrounds:

background-color: lightyellow;
background-image: url(bg.png);
background-image: linear-gradient(to right, #1d6ff2, #22c55e);     a smooth fade between colours

And opacity: 0.5 fades the WHOLE element, including its text, to half see-through.

In this lesson you will learn: the ways to write colours, and how to make backgrounds.""",
    "7/2": """A PSEUDO-CLASS styles an element depending on its STATE or its POSITION. You add a colon and a keyword to a selector:

a:hover           when the mouse pointer is over it
input:focus       while the visitor is typing in it
li:first-child    the first item in its list
li:last-child     the last item
li:nth-child(2)   the 2nd item
tr:nth-child(even)   every even table row - this makes "zebra stripes"

Example - make links change colour when hovered:

a:hover { color: red; }

These are how pages feel alive: buttons that glow when you point at them, boxes that highlight when you click.

In this lesson you will learn: how to style by state and position.""",
    "7/3": """Normally boxes are placed one after another down the page. The position property lets you place a box differently:

static     the normal flow (the default)
relative   nudged from where it would normally be
absolute   placed relative to the nearest positioned parent; it leaves the normal flow
fixed      stuck to the screen, even when you scroll (like a chat button)
sticky     normal until you scroll past it, then it sticks (like a header)

You move a positioned box with top, right, bottom and left, for example top: 10px; right: 10px;

When boxes overlap, z-index decides which is on top: the higher number wins.

A common pattern: make a parent position: relative, then put a child position: absolute with top: 0; right: 0; - the child sits in the parent's top-right corner.

In this lesson you will learn: how to place elements exactly where you want them.""",
    "8/1": """People view websites on phones, tablets and large monitors. A MEDIA QUERY applies CSS only when the screen matches a condition:

.menu { display: flex; }

@media (max-width: 700px) {
  .menu { flex-direction: column; }
}

Read it: "normally the menu is a row; but on screens up to 700px wide, stack it in a column."

One more line is essential in the page's <head>, so phones use their real width instead of pretending to be a big screen:

<meta name="viewport" content="width=device-width, initial-scale=1">

A good approach is "mobile-first": write the phone styles first, then add min-width queries to improve the layout on bigger screens.

In this lesson you will learn: how to make a page adapt to different screen sizes.""",
    "8/2": """Fixed units like px don't adapt to the user. RELATIVE units do:

rem    relative to the page's base font size (usually 16px). 1.5rem = 24px.
em     relative to the element's OWN font size
%      a percentage of the PARENT (often used for widths)
vw     1% of the screen width        vh   1% of the screen height

Why does it matter? Some people make text larger in their browser because it helps them read. If you size fonts in px, you ignore that choice; if you use rem, the text grows with their setting. It is both friendlier and a good habit.

Example: font-size: 1.25rem; means "a quarter bigger than normal text", whatever the user's setting.

In this lesson you will learn: sizing that adapts to people and screens.""",
    "8/3": """An ACCESSIBLE page works for everyone, including people who use screen readers (software that reads the page aloud) or only a keyboard. A good checklist:

- Give images meaningful alt text.
- Give every form input a <label>.
- Use real <button> tags for actions and <a href> for links - they work with the keyboard automatically.
- Use headings in order: h1, then h2, then h3.
- Keep enough colour contrast between text and background, and don't use colour alone to carry meaning.
- Give icon-only buttons a name: <button aria-label="Close">✕</button>
- Set the page language: <html lang="en">

Accessibility is not an extra - it is part of good HTML. Most of it is just using the right tags for the right job, and it helps everyone, not just a few people.

In this lesson you will learn: how to build pages that everyone can use.""",
}
