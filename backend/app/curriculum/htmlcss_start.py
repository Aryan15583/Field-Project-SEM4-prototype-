"""HTML & CSS - gentle 'Start here' units for people who have never built a web page."""
from .dsl import fill, lesson, mcq, order, run, start_unit, t

PAGE = "<!DOCTYPE html>\n<html>\n  <head>\n    <title>My page</title>\n  </head>\n  <body>\n    \n  </body>\n</html>\n"


def page(body: str, style: str = "") -> str:
    head = "    <title>My page</title>\n" + (f"    <style>\n{style}\n    </style>\n" if style else "")
    inner = "\n".join(("    " + line) if line else "" for line in body.split("\n"))
    return f"<!DOCTYPE html>\n<html>\n  <head>\n{head}  </head>\n  <body>\n{inner}\n  </body>\n</html>\n"


def styled(css: str, body: str) -> str:
    return page(body, "\n".join("      " + line for line in css.split("\n")))


START = [
    start_unit(
        1,
        "Start here · Your first web page",
        lesson(
            "What is a web page?",
            """Every website you visit - a news site, a video page, a shop - is built from two simple languages that your browser (Chrome, Safari, Firefox) understands:

- HTML says WHAT is on the page: a heading, a paragraph, a picture, a link. Think of it as the skeleton, or the words and boxes of a poster.
- CSS says HOW it looks: colours, sizes, fonts, spacing. Think of it as the paint and the layout.

You do not need to "install" anything. A web page is just a text file. Your browser reads it and draws the page.

These aren't "programming" languages that make decisions. They DESCRIBE a page. That makes them the friendliest place to begin coding: you type something, and you instantly SEE the result.

In this lesson you will learn: what HTML and CSS are, and what each one does.""",
            mcq("What does HTML describe?", ["What is on the page (the content)", "How fast the page is", "Who visits it", "The internet speed"], 0, "HTML is the content and structure."),
            mcq("What does CSS describe?", ["How the page looks", "What the page says", "The page's address", "The visitor's name"], 0, "CSS is colours, sizes, spacing and so on."),
            mcq("What reads a web page and draws it?", ["The browser", "The keyboard", "The printer", "The mouse"], 0, "Browsers turn HTML and CSS into the page you see."),
        ),
        lesson(
            "Tags: the building blocks",
            """HTML is written with TAGS. A tag is a word in angle brackets that tells the browser what something is. Most tags come in pairs: an OPENING tag and a CLOSING tag with a slash:

<p>Hello there!</p>

- <p> opens a paragraph.
- Hello there! is the CONTENT.
- </p> closes it (notice the slash).

The pair together, with the content, is called an ELEMENT.

A whole page has a standard frame. For now, just copy it and put your content inside <body> - that's the part you see:

<!DOCTYPE html>
<html>
  <head>
    <title>My page</title>
  </head>
  <body>
    <p>Hello there!</p>
  </body>
</html>

The <title> is the name shown on the browser tab.

In this lesson you will learn: what a tag is, and where your content goes.""",
            mcq("What does </p> do?", ["Closes the paragraph", "Opens a paragraph", "Makes text bold", "Deletes the page"], 0, "A slash makes it a closing tag."),
            mcq("Where does the visible content go?", ["Inside <body>", "Inside <title>", "Nowhere", "Before <html>"], 0, "<body> holds everything you see on the page."),
            fill("Close the paragraph.", "<p>Hello</___>", "p", "The closing tag repeats the name after a slash."),
            order("Order the page frame.", ["<!DOCTYPE html>", "<html>", "<head><title>Hi</title></head>", "<body><p>Hi!</p></body>", "</html>"], "The frame wraps head and body."),
            run("Make a page whose body contains one paragraph that says: Hello, Web!", "html", [t("paragraph text", selector="p", prop="text")], ["Hello, Web!"],
                page("<p>Hello, Web!</p>"), starter=PAGE, hint="Between <body> and </body> write <p>Hello, Web!</p>"),
        ),
        lesson(
            "Headings and paragraphs",
            """Headings are titles and subtitles. There are six sizes, <h1> (biggest, most important) to <h6> (smallest). Use one <h1> for the page title.

<h1>My Pets</h1>
<h2>Cats</h2>
<p>Cats like to sleep.</p>
<h2>Dogs</h2>
<p>Dogs like to run.</p>

Think of it like a book: one big title (h1), chapter names (h2), and paragraphs of text (p).

Good to know: the browser ignores extra spaces and blank lines you type. If you want a new paragraph, use another <p>.

Try changing the words and watch the preview - you cannot break anything!

In this lesson you will learn: how to give a page headings and paragraphs.""",
            mcq("Which heading is the biggest?", ["<h1>", "<h6>", "<head>", "<p>"], 0, "h1 is the most important and biggest."),
            mcq("Which tag makes a paragraph?", ["<p>", "<h1>", "<body>", "<title>"], 0, "p stands for paragraph."),
            fill("Make a second-level heading.", "<___>Chapter 1</h2>", "h2", "The opening tag must match the closing one."),
            run("Write one h1 heading saying Pets and one paragraph saying I love animals.", "html",
                [t("heading", selector="h1", prop="text"), t("paragraph", selector="p", prop="text")], ["Pets", "I love animals."],
                page("<h1>Pets</h1>\n<p>I love animals.</p>"), starter=PAGE, hint="<h1>Pets</h1> then <p>I love animals.</p>"),
        ),
        lesson(
            "Lists and links",
            """A list is great for shopping lists, menus and steps. An unordered list (bullets) uses <ul>, and each item uses <li> ("list item"):

<ul>
  <li>Milk</li>
  <li>Eggs</li>
  <li>Bread</li>
</ul>

For a numbered list use <ol> instead of <ul>.

A LINK takes you to another page. It uses <a> (the "anchor" tag) with an address in href:

<a href="https://example.com">Visit the example site</a>

The words between the tags are what people click. The href part (an ATTRIBUTE - extra information inside the opening tag) is where the link goes.

In this lesson you will learn: how to make lists and links.""",
            mcq("Which tag makes ONE item in a list?", ["<li>", "<ul>", "<a>", "<p>"], 0, "li = list item."),
            mcq("Which tag makes a link?", ["<a>", "<link>", "<url>", "<go>"], 0, "The anchor tag <a> makes links."),
            mcq("Where does the link's address go?", ["In the href attribute", "Between the tags", "In the title", "Nowhere"], 0, "href=\"...\" holds the address."),
            run("Make a list (ul) with three items: Milk, Eggs, Bread.", "html", [t("number of items", selector="li", prop="count"), t("first", selector="li:nth-of-type(1)", prop="text")], ["3", "Milk"],
                page("<ul>\n  <li>Milk</li>\n  <li>Eggs</li>\n  <li>Bread</li>\n</ul>"), starter=PAGE, hint="<ul> with three <li> inside"),
        ),
    ),
    start_unit(
        2,
        "Start here · Making it look good with CSS",
        lesson(
            "Colour your page",
            """CSS describes how things LOOK. A CSS rule has three parts:

p {
  color: red;
}

- p is the SELECTOR - which elements to style (all paragraphs).
- color is the PROPERTY - what to change (the text colour).
- red is the VALUE - what to change it to.
The curly brackets { } wrap the settings, and each setting ends with a semicolon ;.

CSS goes in a <style> element inside <head>:

<head>
  <style>
    h1 { color: blue; }
  </style>
</head>

To change the background use background-color. Colours can be names (red, blue, orange) or codes like #ff0000 (that is red).

In this lesson you will learn: how to change colours with a CSS rule.""",
            mcq("In 'p { color: red; }', what is 'p'?", ["The selector (what to style)", "The value", "The property", "A comment"], 0, "The selector chooses which elements the rule affects."),
            mcq("Which property changes the text colour?", ["color", "paint", "font", "text-style"], 0, "color sets the text colour."),
            mcq("Where does a <style> element go?", ["Inside <head>", "Inside <title>", "After </html>", "Inside <p>"], 0, "In the head, with the page's settings."),
            run("Make every h1 red (#ff0000) using CSS.", "html", [t("h1 colour", selector="h1", prop="color")], ["rgb(255, 0, 0)"],
                styled("h1 { color: #ff0000; }", "<h1>Title</h1>"), starter=styled("", "<h1>Title</h1>"), hint="h1 { color: #ff0000; }"),
        ),
        lesson(
            "Size and alignment",
            """You can change how big and where text sits:

p {
  font-size: 24px;
  text-align: center;
}

- font-size sets the text size. A PIXEL (px) is one tiny dot on the screen - 16px is normal text, 24px is bigger.
- text-align moves text: left, center or right.
- font-weight: bold makes text bold.

You can put several settings inside one rule - one per line, each ending with ;.

A rule can style many elements at once. Separate the selectors with commas:

h1, h2 {
  color: navy;
}

In this lesson you will learn: how to change text size and alignment.""",
            mcq("Which property changes text size?", ["font-size", "text-big", "size", "big"], 0, "font-size, usually in px."),
            mcq("What does text-align: center do?", ["Puts the text in the middle", "Makes it bigger", "Makes it bold", "Colours it"], 0, "It centres the text."),
            fill("Make the text bold.", "p { font-weight: ___; }", "bold", "bold makes text thick."),
            run("Make every paragraph 24px and centred.", "html", [t("size", selector="p", prop="font-size"), t("align", selector="p", prop="text-align")], ["24px", "center"],
                styled("p { font-size: 24px; text-align: center; }", "<p>Hello</p>"), starter=styled("", "<p>Hello</p>"), hint="p { font-size: 24px; text-align: center; }"),
        ),
        lesson(
            "Boxes and spacing",
            """Here is a secret: every element on a web page is a BOX. CSS lets you control the space around and inside it:

- padding is space INSIDE the box, between the text and the edge.
- border is a line around the box.
- margin is space OUTSIDE the box, between it and its neighbours.

p {
  background-color: lightyellow;
  padding: 10px;
  border: 2px solid black;
  margin: 20px;
}

"2px solid black" means: 2 pixels thick, a solid line, black colour.

Picture a gift: padding is the bubble wrap, the border is the box itself, and margin is the gap between this present and the next one.

You have now met the core of HTML and CSS: tags for content, rules for looks. Great work!

In this lesson you will learn: padding, border and margin.""",
            mcq("What is padding?", ["Space inside the box, around the text", "Space outside the box", "A line around the box", "The text colour"], 0, "Padding is the cushion between text and the edge."),
            mcq("What is margin?", ["Space outside the box", "Space inside the box", "The border colour", "The text size"], 0, "Margin separates the box from its neighbours."),
            fill("Add a thin solid border.", "p { border: 1px ___ black; }", "solid", "solid draws a plain line."),
            run("Give every paragraph a light yellow background (#ffffcc) and 10px of padding.", "html", [t("background", selector="p", prop="background-color"), t("padding", selector="p", prop="padding-top")],
                ["rgb(255, 255, 204)", "10px"], styled("p { background-color: #ffffcc; padding: 10px; }", "<p>Box</p>"), starter=styled("", "<p>Box</p>"), hint="background-color: #ffffcc; padding: 10px;"),
        ),
    ),
]
