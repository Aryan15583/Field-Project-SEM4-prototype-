// Semester III Field Project report (B.Sc. Computer Science) - Codeingo. Layout follows the college's FPSEM3 format.
const fs = require("fs");
const path = require("path");
const L = require("../builder/lib");
const { D, run, ph, p, center, blank, bullets, numbered, table, captionTable, figure, tables, figures, toc } = L;
const { Document, Packer, Paragraph, TextRun, AlignmentType, Footer, PageNumber, ImageRun, LevelFormat, Table, TableRow, TableCell, WidthType, VerticalAlign, BorderStyle } = D;

const HERE = __dirname;
const pagesFile = path.join(HERE, "pages3.json");
const PAGES = fs.existsSync(pagesFile) ? JSON.parse(fs.readFileSync(pagesFile, "utf8")) : {};
const pageOf = (s) => (PAGES[s] != null ? String(PAGES[s]) : "0");

const TITLE = "Codeingo";
const STUDENT = "Aryan Sawant";
const GUIDE = "Ms. Pranali Patil";
const BLACK = "000000";
const W = L.TEXT_W;

// ------------------------------------------------------------------ headings (black, like the format)
const heading = (text, size, o = {}) => new Paragraph({ keepNext: true, alignment: o.align, pageBreakBefore: o.pageBreak, spacing: { before: o.before ?? 200, after: o.after ?? 120 }, heading: o.level, children: [run(text, { bold: true, size, color: BLACK })] });
function chapter(n, title) {
  const text = `Chapter ${n} ${title}`;
  toc.push({ level: 1, label: `Chapter ${n}`, title, search: text });
  return heading(text, 36, { align: AlignmentType.CENTER, pageBreak: true, before: 600, after: 360, level: D.HeadingLevel.HEADING_1 });
}
function h2(label, title) {
  toc.push({ level: 2, label, title, search: `${label} ${title}` });
  return heading(`${label} ${title}`, 28, { level: D.HeadingLevel.HEADING_2, before: 280 });
}
function h3(label, title) {
  toc.push({ level: 3, label, title, search: `${label} ${title}` });
  return heading(`${label} ${title}`, 24, { level: D.HeadingLevel.HEADING_3 });
}
const sub = (t) => heading(t, 24, { before: 160, after: 60 });
const body = (t, o = {}) => p(t, { line: 300, after: 120, align: AlignmentType.LEFT, ...o });
const interp = (text) => p([run("Interpretation: ", { bold: true }), run(text)], { line: 300, after: 200, align: AlignmentType.JUSTIFIED });

// ------------------------------------------------------------------ cover, certificate, front matter
const logo = (w, h) => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120, after: 160 }, children: [new ImageRun({ type: "jpg", data: fs.readFileSync(path.join(HERE, "logo-000.jpg")), transformation: { width: w, height: h }, altText: { title: "College logo", description: "Model College emblem", name: "logo" } })] });
const cb = (t, o = {}) => center(t, { bold: true, size: o.size || 26, after: o.after ?? 140, line: 300, ...o });

function cover() {
  return [
    ...blank(2),
    center(TITLE, { bold: true, size: 56, after: 40 }),
    cb("A Field Project Report", { size: 26, after: 360 }),
    cb("BACHELOR OF SCIENCE (COMPUTER SCIENCE)", { size: 28, after: 200 }),
    center("By", { size: 24, after: 160 }),
    cb(STUDENT, { size: 32, after: 120 }),
    cb("Under the esteemed guidance", { size: 24, after: 40 }),
    cb("of", { size: 24, after: 100 }),
    cb(GUIDE, { size: 28, after: 240 }),
    logo(120, 102),
    ...blank(1),
    cb("DEPARTMENT OF INFORMATION TECHNOLOGY", { size: 24, after: 40 }),
    cb("&  COMPUTER SCIENCE", { size: 24, after: 220 }),
    cb("KERALEEYA SAMAJAM (REGD.) DOMBIVLI'S", { size: 28, after: 100 }),
    cb("MODEL COLLEGE", { size: 30, after: 60 }),
    cb("(EMPOWERED AUTONOMOUS)", { size: 24, after: 60 }),
    cb("DOMBIVLI, 421201", { size: 24, after: 60 }),
    cb("MAHARASHTRA", { size: 24, after: 60 }),
    cb("OCTOBER 2026", { size: 24, after: 0 }),
  ];
}
const ctitle = (t, o = {}) => new Paragraph({ pageBreakBefore: o.pageBreak !== false, alignment: AlignmentType.CENTER, spacing: { before: o.before ?? 600, after: 360 }, children: [run(t, { bold: true, size: o.size || 36 })] });
function certificate() {
  const sig = (a, b) => new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: [W / 2, W / 2], borders: { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE }, insideHorizontal: { style: BorderStyle.NONE }, insideVertical: { style: BorderStyle.NONE } }, rows: [new TableRow({ children: [a, b].map((t, i) => new TableCell({ width: { size: W / 2, type: WidthType.DXA }, borders: { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE } }, children: [new Paragraph({ alignment: i ? AlignmentType.RIGHT : AlignmentType.LEFT, children: [run(t, { bold: true, size: 22 })] })] })) })] });
  return [
    new Paragraph({ pageBreakBefore: true, alignment: AlignmentType.CENTER, spacing: { before: 400, after: 20 }, children: [run("KERALEEYA SAMAJAM (REGD.) DOMBIVLI'S MODEL COLLEGE", { bold: true, size: 26 })] }),
    center("(EMPOWERED AUTONOMOUS)", { bold: true, size: 26, after: 60 }),
    center("(Affiliated to University of Mumbai)", { italics: true, bold: true, size: 24, after: 60 }),
    center("DOMBIVLI- MAHARASHTRA-421201", { bold: true, size: 24, after: 360 }),
    cb("DEPARTMENT OF INFORMATION TECHNOLOGY", { size: 28, after: 80 }),
    cb("& COMPUTER SCIENCE", { size: 28, after: 160 }),
    logo(130, 110),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200, after: 200 }, children: [run("CERTIFICATE", { bold: true, size: 28, underline: {} })] }),
    p(["This is to certify that the project entitled, “", run(TITLE, { bold: true }), "”, is bonafied work of ", run(STUDENT, { underline: {} }), " bearing Seat No: ", ph("SEAT NO e.g. BSCS/III-2627-XXXX"), " submitted in partial fulfilment of the requirements for the award of degree of ", run("BACHELOR OF SCIENCE in COMPUTER SCIENCE", { bold: true }), " from Keraleeya Samajam (Regd.) Dombivli’s Model College."], { line: 360, align: AlignmentType.JUSTIFIED }),
    ...blank(4),
    sig("Internal Guide", "Coordinator"),
    ...blank(2),
    center("External Examiner", { bold: true, size: 22 }),
    ...blank(2),
    sig("Date", "College Seal"),
  ];
}
function frontPages() {
  return [
    ctitle("ABSTRACT", { before: 400 }),
    p([run("Codeingo", { bold: true }), " is a web-based, game-like platform that teaches programming through short, interactive lessons, in the spirit of language-learning apps such as Duolingo. It is designed to address common problems that beginners face when learning to code: confusing syntax, a lack of guidance, no real-world application and a loss of motivation after a few days."], { line: 300 }),
    p("The platform offers ten courses (Python, JavaScript, TypeScript, Java, C++, C, SQL, HTML & CSS, Git, and Data Structures & Algorithms) as a structured path of units and lessons. Learners write and run real programs inside the browser, earn XP, keep daily streaks, collect badges and complete projects at the end of each section. Answers are checked on the server so that expected results cannot be copied from the page. Sign-in uses a Google account protected by mandatory 2-step verification.", { line: 300 }),
    p("The system is built with Next.js and React for the interface and Python FastAPI with a SQL database for the server. Its features were chosen from a requirement survey of 53 young learners, which showed that 62% find a game-like way of learning appealing, that lack of guidance and confusing syntax are the main obstacles, and that building real projects is the strongest motivator. Overall, Codeingo gives beginners one simple, engaging place to learn programming step by step.", { line: 300 }),
    ctitle("Acknowledgement", { before: 600, size: 32 }),
    p(["     It gives me a pleasure to present my field project on “", run(TITLE, { bold: true }), "”. This is my milestone in Bachelor of Science (Computer Science). I would like to express my sincere thanks to all the teachers who helped me throughout the project. I would like to acknowledge the help and guidance provided by our guide ", run("Pranali Patil"), " in all places during the presentation of this project."], { line: 300, align: AlignmentType.JUSTIFIED }),
    p("     I am grateful to IT-CS Co-Ordinator Dr. Divya Premchandran for her constant support and motivation. I am thankful to our honourable Principal Dr. CA Ravindra P. Bambardekar. Onwards my project works, I am also thankful to the staff members of the IT-CS department for their moral support. I also thank the 53 learners who answered the requirement survey.", { line: 300, align: AlignmentType.JUSTIFIED }),
    ctitle("Declaration", { before: 600, size: 32 }),
    p(["     I hereby declare that the project entitled, ", run("“" + TITLE + "”", { bold: true }), " done at Keraleeya Samajam (Regd.) Dombivli’s Model College (Empowered Autonomous), has not been in any case duplicated to submit to any other university for the award of any degree. To the best of my knowledge other than me, no one has submitted to any other university."], { line: 360, align: AlignmentType.JUSTIFIED }),
    p(["     The project is done in partial fulfilment of the requirements for the award of degree of ", run("BACHELOR OF SCIENCE (COMPUTER SCIENCE)", { bold: true }), " to be submitted as a Third semester field project as part of our curriculum."], { line: 360, align: AlignmentType.JUSTIFIED }),
  ];
}

// ------------------------------------------------------------------ TOC / lists (bordered tables like the format)
const row3 = (a, b, c) => [a, b, c];
function listings() {
  const w = [1700, 5726, 1600];
  const tocRows = toc.map((e) => (e.level === 1 ? [e.label, e.title, pageOf(e.search)] : [e.label, e.title, pageOf(e.search)]));
  const t = (title, header, rows) => [ctitle(title, { before: 400, size: 32 }), table(w, header, rows, { size: 22, headFill: "FFFFFF" })];
  return [
    ...t("TABLE OF CONTENTS", ["Sr.No", "Title", "Page No"], tocRows),
    ...t("LIST OF TABLES", ["Sr.no", "Name of the table", "Page No"], tables.map((x) => [x.label.replace("Table ", ""), x.text, pageOf(x.search)])),
    ...t("LIST OF FIGURES", ["Sr.no", "Name of the Figure", "Page No"], figures.map((x) => [x.label.replace("Fig. ", ""), x.text, pageOf(x.search)])),
  ];
}

// ------------------------------------------------------------------ Periodic Field Project Report page(s)
const FB = new Paragraph({ spacing: { after: 80 }, children: [ph("Feedback from the guide, Ms. Pranali Patil, to be written after the chapter review", { size: 24 })] });
function periodic(overview, outcomes, feedback) {
  const lab = (t, extra) => [new Paragraph({ spacing: { after: 40 }, children: [run(t, { bold: true, size: 22 })] }), new Paragraph({ spacing: { after: 40 }, children: [run(extra, { size: 22, bold: extra.startsWith("(Brief") })] })];
  const txt = (t) => (Array.isArray(t) ? t : [t]).map((x) => (typeof x === "string" ? new Paragraph({ alignment: AlignmentType.JUSTIFIED, spacing: { after: 80, line: 290 }, children: [run(x, { size: 24 })] }) : x));
  const kv = (k, v) => new TableRow({ cantSplit: true, children: [L.cell([new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 20 }, children: [run(k, { bold: true, size: 22 })] })], 3300, { valign: VerticalAlign.CENTER }), L.cell([new Paragraph({ spacing: { after: 20 }, children: Array.isArray(v) ? v : [run(v, { bold: true, size: 26 })] })], W - 3300)] });
  const full = (children) => new TableRow({ cantSplit: true, children: [new TableCell({ width: { size: W, type: WidthType.DXA }, columnSpan: 2, borders: L.borders, margins: { top: 60, bottom: 60, left: 120, right: 120 }, children })] });
  return [
    new Paragraph({ pageBreakBefore: true, spacing: { before: 400, after: 200 }, children: [run("Periodic Field Project Report", { bold: true, size: 30 })] }),
    new Table({
      width: { size: W, type: WidthType.DXA }, columnWidths: [3300, W - 3300],
      rows: [
        kv("Name of the Student", STUDENT), kv("Program /Semester", "III"), kv("Roll No/Seat No", [ph("ROLL / SEAT NO e.g. BSCS/III-2627-XXXX", { bold: true, size: 24 })]),
        kv("Field project Title", TITLE), kv("Name of the Faculty mentor", GUIDE),
        full(lab("Overview (Max 150 Words)", "(Brief summary of key activities, tasks and projects undertaken during the period)")),
        full(txt(overview)),
        full(lab("Learning Outcomes (Max 100 words):", "(Highlight the main lessons, skills, or knowledge gained during the week.)")),
        full(txt(outcomes)),
        full(lab("Mentor Feedback and Suggestions (Max 100 words):", "(Feedback received from the mentor and any additional suggestions for improvement.)")),
        full(txt(feedback || [FB])),
      ],
    }),
    ...blank(2),
    new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: [W / 2, W / 2], borders: { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE }, insideHorizontal: { style: BorderStyle.NONE }, insideVertical: { style: BorderStyle.NONE } }, rows: [new TableRow({ children: ["Student Sign with date", "Mentor's Signature with date"].map((t, i) => new TableCell({ width: { size: W / 2, type: WidthType.DXA }, borders: { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE } }, children: [new Paragraph({ alignment: i ? AlignmentType.RIGHT : AlignmentType.LEFT, children: [run(t, { bold: true, size: 22 })] })] })) })] }),
  ];
}

// ------------------------------------------------------------------ Chapter 1
function ch1() {
  return [
    ...periodic(
      "This period was spent defining the Codeingo project: why a new coding-learning platform is needed, what it should achieve, who will use it and what is inside and outside its scope. Existing apps and the problems beginners face were studied, and a requirement survey was prepared. The main aim is to provide a simple, game-like and secure place where a beginner can learn programming step by step, write real code in the browser and stay motivated through streaks, points and projects.",
      "Through this chapter I learned how to state the background of a problem, write measurable objectives, and separate purpose, scope and applicability. I understood that a project should clearly list its limitations, and that beginners need guidance, feedback and a sense of progress more than long theory.",
    ),
    chapter(1, "Introduction"),
    h2("1.1.", "Background"),
    body("Almost every industry today depends on software, and the ability to write code has become a basic skill. Yet many beginners struggle to start. Installing tools, understanding confusing syntax and having nobody to guide them makes learning slow and boring, and many give up within the first weeks. Traditional ways of learning, such as long videos or text-only tutorials, lack interactive and engaging elements that keep learners motivated."),
    body("Language-learning apps such as Duolingo showed that short daily lessons, instant feedback, points and streaks can turn a difficult subject into a daily habit. Recent web technology also makes it possible to run real programming languages inside the browser, so nothing needs to be installed."),
    body("The concept of Codeingo is inspired by these ideas. It is a web-based platform in which a learner follows a guided path of courses, units and lessons, writes and runs real programs in the browser, and earns XP, streaks and badges. It builds upon existing work in online coding education and game-based learning to create a more engaging and beginner-friendly solution."),
    h2("1.2.", "Objectives"),
    body("The main objectives of the Codeingo project are:"),
    ...bullets([
      "To develop an interactive learning platform with a structured path of courses, units and lessons for beginners.",
      "To let learners write and run real code inside the browser without installing anything.",
      "To add game elements such as XP, daily streaks, hearts, badges and weekly leagues to improve motivation.",
      "To include practice, chapter tests and projects so that learners can apply what they learn.",
      "To protect user accounts with secure sign-in and mandatory 2-step verification.",
      "To design a simple, user-friendly interface that works on computers and phones in a light and a dark theme.",
    ]),
    h2("1.3.", "Purpose, Scope & Applicability"),
    h3("1.3.1.", "Purpose"),
    body("The purpose of this project is to create a digital environment that makes learning programming easy, engaging and habit-forming. The project answers key questions such as:"),
    body("- How can beginners be guided step by step so that they do not give up?"),
    body("- How can game-like features and real projects be used to keep learners motivated?"),
    body("The system helps learners practise regularly, get instant feedback and see their own progress. It also demonstrates how user-interface design, security and learning content can be combined in one application."),
    h3("1.3.2.", "Scope"),
    body("The scope of the Codeingo project includes:"),
    body("1. User Registration and Login: Users sign in with a Google account and finish 2-step verification (an emailed code, an authenticator app or a passkey)."),
    body("2. Learning Content: Ten courses with units, lessons and exercises, where learners write and run programs in the browser."),
    body("3. Game Elements: XP, streaks, hearts, badges, a daily challenge, chapter tests and weekly leagues."),
    body("4. Administration: A hidden admin area where only authorised administrators manage content and users."),
    body("Limitations:"),
    ...bullets([
      "Internet Dependency: The learner's progress is stored on the server, so sign-in and saving progress need an internet connection.",
      "Languages that need a compiler: Java, C and C++ programs cannot run inside the browser and need a server-side sandbox for full support.",
      "No video lessons: The lessons are text and exercise based; video explanations are not part of this version.",
    ]),
    h3("1.3.3.", "Applicability"),
    body("This project is useful for:"),
    ...bullets([
      "School and college students – who want to start programming without installing tools.",
      "Self-learners and career-switchers – who need a guided path from beginner to advanced level.",
      "Teachers and colleges – for contests and practice sessions with a leaderboard.",
    ]),
    body("The system provides both direct and indirect benefits by improving practice habits, reducing the fear of coding and making learning enjoyable. It contributes to the computer field by demonstrating how game-based learning, in-browser code execution and secure sign-in can be combined in one application."),
  ];
}

// ------------------------------------------------------------------ Chapter 2
const TECH = [
  ["Next.js", "Next.js is a React framework used to build the web pages and the installable app of Codeingo. It provides routing, server rendering and a production build, and lets the same code serve the landing page, lessons and admin area."],
  ["React", "React is a JavaScript library for building user interfaces from small reusable components. In Codeingo it is used for the lesson screens, quizzes, the learning path and the animated mascot."],
  ["Tailwind CSS", "Tailwind CSS is a utility-first styling tool. Colours are defined as variables, which allows the light theme (white and blue) and the dark theme (black and green) to be switched with one setting."],
  ["Python", "Python is the programming language of the server. It is simple to read, has a large library collection and is also the first language most survey respondents want to learn."],
  ["FastAPI", "FastAPI is a Python framework for building REST APIs. It validates incoming data automatically, is fast, and handles sign-in, lessons, progress, practice and contests."],
  ["SQLAlchemy", "SQLAlchemy is an object-relational mapper. It lets the server work with database tables through Python classes such as users, courses, lessons and attempts."],
  ["PostgreSQL and SQLite", "PostgreSQL is the production database that stores users, lessons, progress and certificates. SQLite is a light file database used during development and testing, so the same code runs on both."],
  ["JWT cookies and 2-step verification", "After sign-in the server issues short-lived signed tokens (JSON Web Tokens) in secure cookies. Sign-in needs a second step: an emailed code, an authenticator app or a passkey (WebAuthn)."],
  ["Pyodide and Web Workers", "Pyodide runs Python inside the browser using WebAssembly, and Web Workers run JavaScript, TypeScript and SQL in the background. This lets learners run real code safely without installing anything."],
  ["Progressive Web App", "A progressive web app can be installed from the browser to the home screen and opens like a normal app, with its own icon and an offline page."],
];
const CMP = [
  ["Next.js", "Create React App / plain React", "Next.js adds routing, server rendering and an optimised build. Plain React needs these to be added separately.", "Next.js is selected because it gives pages, routing and a production build in one framework."],
  ["React", "Angular", "React is a light library with a large community. Angular is a complete framework with a steeper learning curve.", "React is selected because it is easier to learn and fits small reusable lesson components."],
  ["Tailwind CSS", "Bootstrap", "Tailwind provides low-level utilities and full control of design. Bootstrap provides ready-made components with a fixed look.", "Tailwind is selected because Codeingo needs its own look and two colour themes."],
  ["Python", "Java", "Python has simple syntax and short code. Java is more verbose and needs compilation.", "Python is selected because it is fast to develop in and is the most requested first language in the survey."],
  ["FastAPI", "Django / Flask", "FastAPI validates data and creates API documentation automatically. Django is larger; Flask has fewer built-in features.", "FastAPI is selected because the project mainly needs a fast, typed REST API."],
  ["SQLAlchemy", "Raw SQL queries", "SQLAlchemy maps tables to Python classes and protects against SQL injection. Raw SQL is harder to maintain.", "SQLAlchemy is selected because it keeps the code clean and works with several databases."],
  ["PostgreSQL / SQLite", "MongoDB", "SQL databases use tables with relations and strict rules. MongoDB stores flexible documents.", "A relational database is selected because users, lessons and progress are closely related."],
  ["JWT cookies + 2-step verification", "Server sessions / passwords only", "Signed tokens are stateless and easy to scale; passwords alone are weaker.", "Selected because it is secure, and the survey groups are young learners who should not reuse passwords."],
  ["Pyodide / Web Workers", "Running code on the server", "In-browser execution costs the server nothing and is isolated; server execution is risky and expensive.", "Selected because it is safe and needs no installation."],
  ["Progressive Web App", "Native Android app", "A PWA reuses the web code and installs from the browser. A native app needs separate code per platform.", "Selected because it reaches phones and computers with one code base."],
];
function ch2() {
  const list = TECH.map((t) => t[0]);
  const out = [
    ...periodic(
      "During this period the existing coding-learning systems were studied to understand their features and limitations. The technologies needed for Codeingo were listed and described: Next.js, React, Tailwind CSS, Python, FastAPI, SQLAlchemy, PostgreSQL and SQLite, JWT cookies with 2-step verification, Pyodide with Web Workers, and Progressive Web Apps. A comparative study was made between the selected technologies and their alternatives, and the role of each part of the system was understood.",
      "I learned about the technologies used in building a web-based learning application: how a front end, a REST API and a database work together, how code can be run safely in the browser, and how secure sign-in works. I also learned how to compare technologies and justify the final selection.",
    ),
    chapter(2, "Survey of Technologies"),
    h2("2.1.", "Existing System"),
    body("To understand the requirements of Codeingo, several popular learning platforms and tools were surveyed. The survey respondents also named many of them:"),
    ...bullets([
      "Codecademy and freeCodeCamp: Interactive course sites with in-browser editors. Codecademy locks many projects and certificates behind a paid plan; freeCodeCamp is free but is mostly text based and gives little game-like motivation.",
      "Scratch: A visual block-based tool that is excellent for children, but it does not teach real text syntax, so the next step to Python or Java is a big jump.",
      "LeetCode and video channels (for example Takeuforward, CodeWithHarry): Strong for practice and explanation, but they assume that the learner already knows the basics and do not give a guided path or progress tracking.",
      "Local compilers and editors (Turbo C, Sublime Text): Need installation and set-up, and give no feedback or guidance.",
    ]),
    body("Out of the 53 survey respondents, 36 had not used any such platform. This shows that a simple, no-installation and guided platform can reach many beginners."),
    h2("2.2", "List of Technologies"),
    body("The following technologies are used for developing Codeingo:"),
    ...numbered(list, "numbers"),
  ];
  TECH.forEach(([t, d], i) => { out.push(h3(`2.2.${i + 1}`, t), body(d, { align: AlignmentType.JUSTIFIED })); });
  out.push(
    h2("2.3", "Comparative Study of Technologies"),
    body("The following table compares the selected technologies with related technologies that could also be used for developing similar functionality."),
    captionTable("Table 2.3.1", "Comparative Study"),
    table([600, 1500, 1700, 2800, 2426], ["No", "Selected Technology", "Related Technology", "Comparison", "Reason for Selecting"], CMP.map((r, i) => [String(i + 1), ...r]), { size: 19, headFill: "FFFFFF" }),
    h2("2.4", "Selected Technology"),
    body("The technologies selected for Codeingo are Next.js, React, Tailwind CSS, Python, FastAPI, SQLAlchemy, PostgreSQL with SQLite, JWT cookies with 2-step verification, Pyodide with Web Workers, and a Progressive Web App. The front end is developed using Next.js, React and Tailwind CSS: React builds the screens, Next.js provides routing and the production build, and Tailwind provides the light and dark themes.", { align: AlignmentType.JUSTIFIED }),
    body("The back end is developed using Python and FastAPI. A REST API connects the front end and the server, SQLAlchemy talks to the database, and PostgreSQL stores the data permanently. Learner code is executed in the browser with Pyodide and Web Workers, and the server only checks the results.", { align: AlignmentType.JUSTIFIED }),
    body("The application can be installed on a phone or computer as a Progressive Web App while reusing the same web code.", { align: AlignmentType.JUSTIFIED }),
  );
  return out;
}

// ------------------------------------------------------------------ Chapter 3
function ch3() {
  return [
    ...periodic(
      "This chapter focused on identifying the problem, the requirements and the resources needed for developing Codeingo. The main problems identified were confusing syntax, lack of guidance, no real-world application and loss of motivation. The things in the system (course path, lessons, exercises, XP and streak) and the actions on them were specified. Hardware and software requirements were listed, and a conceptual model showing how a learner moves through the system was prepared.",
      [
        "Learning outcomes from this chapter are:",
        "• Learned how to identify and define a software problem.",
        "• Understood the functional requirements of the Codeingo system.",
        "• Learned how to identify hardware and software requirements.",
        "• Understood the importance of system analysis before development.",
        "• Gained an understanding of the conceptual structure of the proposed system.",
      ],
    ),
    chapter(3, "Requirements and Analysis"),
    h2("3.1.", "Problem Definition"),
    body("The overall problem we are addressing is that many beginners start learning programming and then quit. Most tutorials are long, text-heavy and assume tools are already installed, and nobody tells the learner what to learn next. The survey confirmed this: of the learners who tried before, 13 gave up, and the biggest reasons for stopping were lack of guidance and no time. We can divide the problem into three sub-problems:", { align: AlignmentType.JUSTIFIED }),
    ...bullets([
      "The Guidance Problem: Learners do not know the order in which to learn topics and get lost between many tutorials.",
      "The Practice Problem: Reading or watching is not enough; learners need to write code and get instant feedback, but setting up a compiler is difficult.",
      "The Motivation Problem: Without rewards, a streak or friends, learners lose interest after a few days.",
    ]),
    h2("3.2.", "Requirement Specification"),
    body("Independent of how we code the system, Codeingo needs to handle a specific set of core things and actions to be useful for a learner:"),
    body("Things in the System:"),
    ...bullets([
      "The Learning Path: Courses divided into units and lessons, unlocked one after another.",
      "The Exercise: A question (choice, fill-in-the-blank or a small program) that is graded by the server.",
      "The Progress Record: XP, daily streak, hearts and badges of each learner.",
      "The Test and Project: Chapter tests that unlock the next unit and a project at the end of each section.",
    ]),
    body("Actions Performed on These Things:"),
    ...bullets([
      "Learners can sign in with Google and complete 2-step verification.",
      "Learners can open a lesson, read the explanation and answer or run code exercises.",
      "Learners can take a chapter test, practise mistakes later and complete the daily challenge.",
      "Learners can follow friends, see leagues and enter a weekly contest.",
      "Administrators can manage content and users from a hidden admin area.",
    ]),
    h2("3.3.", "Software & Hardware Requirements"),
    sub("3.3.1. Hardware Requirements"),
    body("To develop and run the application, the following minimal hardware configuration is required:"),
    ...bullets([
      "Processor: Intel Core i3 or AMD Ryzen 3 (or equivalent mobile processor).",
      "RAM Capacity: Minimum 4 GB of system memory (8 GB recommended for development).",
      "Disk Capacity: At least 1 GB of free storage space for project code and packages.",
      "Input Devices: A standard mouse, trackpad, keyboard or a capacitive touch screen.",
      "Display: Any standard display that can render a responsive layout (phone to desktop).",
    ]),
    sub("3.3.2. Software Requirements"),
    body("The development tools, libraries and environments used to write and package the application include:"),
    ...bullets([
      "Operating System: Windows 10/11, macOS or Linux.",
      "Code Editor: Visual Studio Code as the primary editor.",
      "Runtime Environments: Node.js 20 or higher for the front end and Python 3.11 or higher for the server.",
      "Database: SQLite for development and PostgreSQL for production.",
      "Testing Environments: Modern web browsers (Chrome, Edge or Safari) and the pytest tool for back-end tests.",
    ]),
    h2("3.4", "Conceptual Model"),
    sub("3.4.1 Conceptual Model"),
    body("The diagram shows how a learner moves through Codeingo: sign-in with 2-step verification, the learning path, the choice of activity (lesson, test, practice, friends and contests), server-side grading, and rewards that end with a certificate."),
    ...figure("figures/conceptual.png", "Fig. 3.4.1", "Conceptual Model of Codeingo", { maxW: 440, maxH: 600 }),
  ];
}

// ------------------------------------------------------------------ Chapter 4
const QUESTIONS = [
  ["What is your name?", null],
  ["Which age group are you in?", ["Under 15", "15–18", "19–22", "23+"]],
  ["Have you tried learning programming before?", ["Yes, currently learning", "Yes, but gave up", "No, never tried"]],
  ["If you tried before, what made it difficult or boring?", ["Confusing syntax", "Lack of guidance", "No real-world application", "Lost motivation", "Too much theory", "Other"]],
  ["How do you prefer to learn new skills?", ["Watching videos", "Hands-on practice", "Playing games", "Interactive challenges", "Reading text"]],
  ["Have you ever used a coding platform before (like Scratch, Codecademy, freeCodeCamp, etc.)? Which one?", null],
  ["On a scale of 1–5, how appealing is the idea of learning to code through a game-like experience?", ["1  (not appealing)", "2", "3", "4", "5  (very appealing)"]],
  ["Which programming language would you be most interested in learning first?", ["Python", "Java", "JavaScript", "C++", "Other", "Not sure"]],
  ["What would motivate you the most to keep learning on a platform like this?", ["Building real projects", "Points/levels & rewards", "Competing with friends", "Certificates", "Just curiosity"]],
  ["Would you prefer learning solo or with a community (leaderboards, group challenges, forums)?", ["Solo", "Community-based", "Mix of both"]],
  ["What's the biggest reason you'd stop using a learning platform like this?", ["Not enough guidance", "No time", "Gets boring", "Lost interest", "Too difficult"]],
];
function ch4() {
  const out = [
    ...periodic(
      "This chapter focused on collecting and analysing user responses through a survey conducted for the Codeingo project. The Coding Platform Interest Survey asked 53 learners about their age group, earlier programming experience, difficulties, preferred learning style, platforms used, interest in game-like learning, first language, motivation, solo or community preference, and reasons for quitting. The responses were interpreted to understand user requirements. The results showed strong interest in guided, hands-on and game-like learning with real projects and friendly competition.",
      [
        "Learning outcomes from this chapter are:",
        "• Learned how to design a survey for collecting user requirements.",
        "• Learned how to analyse and interpret survey responses.",
        "• Understood how user feedback can influence software requirements.",
        "• Identified the important features preferred by potential users.",
        "• Learned how to present survey findings in an organised manner.",
      ],
    ),
  ];
  toc.push({ level: 1, label: "Chapter 4", title: "Data Analysis, Interpretation and Presentation", search: "CHAPTER 4 Data Analysis: Interpretation and Presentation" });
  out.push(
    new Paragraph({ heading: D.HeadingLevel.HEADING_1, pageBreakBefore: true, spacing: { before: 400, after: 240 }, children: [run("CHAPTER 4 Data Analysis: Interpretation and Presentation", { bold: true, size: 32, color: BLACK })] }),
    h2("4.1", "Survey Form"),
    body("The survey was prepared as a Google Form titled “Coding Platform Interest Survey”. It contains the following questions:"),
  );
  QUESTIONS.forEach(([q, opts], i) => {
    out.push(p(`${i + 1}.  ${q}`, { line: 290, after: 60, align: AlignmentType.LEFT, keepNext: true }));
    if (opts) opts.forEach((o) => out.push(p(`●  ${o}`, { line: 270, after: 20, indent: { left: 540 }, align: AlignmentType.LEFT })));
    else out.push(p("______________________________", { line: 270, after: 20, align: AlignmentType.LEFT }));
    out.push(p("", { after: 80 }));
  });
  out.push(
    h2("4.2", "Responses"),
    body("The Google Form received 53 responses between 26 September 2026 and 3 October 2026. The figure shows the first 30 responses (names and e-mail addresses are left out for privacy)."),
    ...figure("sem3/figures/responses.png", "Fig. 4.2.1", "Responses", { maxW: 600, maxH: 520 }),
    h2("4.3", "Data Analysis"),
    body("Total responses: 53. Each question is shown as a chart followed by its interpretation."),
  );
  const chart = (file, label, text, interpretation) => out.push(...figure(`sem3/figures/${file}`, label, text, { maxW: 520, maxH: 330 }), interp(interpretation));
  chart("survey_age.png", "Fig. 4.3.1", "Age group of the respondents (Question 2)", "The respondents are young learners: 23 (43%) are aged 19–22 and 22 (42%) are aged 15–18, so 85% are school or college age. Seven (13%) are 23 or older and one is under 15. This matches the target users of Codeingo.");
  chart("survey_experience.png", "Fig. 4.3.2", "Earlier programming experience (Question 3)", "22 respondents (42%) are currently learning, 18 (34%) have never tried and 13 (25%) tried but gave up. So about one in four beginners quits, and one in three has not even started – both groups need an easy, guided start.");
  chart("survey_difficulty.png", "Fig. 4.3.3", "What made learning difficult or boring (Question 4)", "Confusing syntax (14) and lack of guidance (12) are the two biggest difficulties, followed by no real-world application (9). Together they account for 35 of the 50 answers. This supports short guided lessons, hints and projects in Codeingo.");
  chart("survey_style.png", "Fig. 4.3.4", "Preferred way of learning (Question 5)", "Watching videos is preferred by 19 (36%), hands-on practice by 15 (28%) and playing games by 10 (19%). Together hands-on practice, games and interactive challenges make up 29 answers (55%), which supports an interactive, practice-first design. Video lessons are noted as a future improvement.");
  out.push(
    ...figure("sem3/figures/survey_platform.png", "Fig. 4.3.5", "Coding platforms used before (Question 6)", { maxW: 520, maxH: 330 }),
    interp("36 of 53 respondents (68%) gave no platform at all, meaning they have not used a coding platform. Of the 17 who named one, Codecademy (6) and freeCodeCamp (5) are the most common. Many beginners therefore have no experience with such platforms, and a very simple start is important."),
  );
  chart("survey_appeal.png", "Fig. 4.3.6", "Appeal of game-like learning (Question 7)", "The average rating is 3.6 out of 5. 17 respondents gave 4 and 16 gave 5, so 33 (62%) rated it 4 or 5, while only 10 (19%) gave 1 or 2. This shows a clear interest in learning to code through a game-like experience.");
  chart("survey_language.png", "Fig. 4.3.7", "First language to learn (Question 8)", "Python is the most wanted first language (17, 32%), followed by Java (11, 21%) and JavaScript and C++ (7 each). Nine respondents (17%) are not sure. Codeingo therefore starts with Python and also offers Java, JavaScript and C++.");
  chart("survey_motivation.png", "Fig. 4.3.8", "What keeps learners motivated (Question 9)", "Building real projects is the strongest motivator (22, 42%), followed by points/levels and rewards (11) and competing with friends (10). This is why Codeingo has projects at the end of every section, XP, badges and leagues.");
  chart("survey_social.png", "Fig. 4.3.9", "Solo or community learning (Question 10)", "25 respondents (47%) prefer a mix of both and 15 (28%) prefer a community, while only 13 (25%) prefer to learn alone. So 75% want some community, which supports friends, leagues and contests.");
  chart("survey_quit.png", "Fig. 4.3.10", "Biggest reason to stop using a platform (Question 11)", "Not enough guidance is the biggest reason to quit (18, 34%), followed by no time (13, 25%). Gets boring, lost interest and too difficult together account for 22 answers. Short five-minute lessons, clear next steps and daily streak reminders respond to these reasons.");
  out.push(
    h2("4.4", "Conclusion"),
    body("The survey and analysis conducted for the Codeingo project show the need for a simple, guided and engaging platform for beginners. The responses highlight issues such as confusing syntax, lack of guidance, no real-world application and loss of motivation. The survey also shows interest in game-like learning (62% rated it 4 or 5), hands-on practice, real projects, and learning together with friends.", { align: AlignmentType.JUSTIFIED }),
    body("The proposed Codeingo brings these ideas together in one application: a guided path of lessons, code that runs in the browser, XP, streaks, badges, projects, friends and contests. The survey also considers the preference for Python as a first language and for community learning, which shaped the course list and the social features.", { align: AlignmentType.JUSTIFIED }),
    body("Overall, the survey helped identify the practical requirements of Codeingo and provided a basis for developing a user-friendly platform that makes learning to program engaging and habit-forming.", { align: AlignmentType.JUSTIFIED }),
  );
  return out;
}

// ------------------------------------------------------------------ assemble (body first so the registries are filled)
const bodyParts = [...ch1(), ...ch2(), ...ch3(), ...ch4()];
const certs = certificate();
const front = frontPages();
const lists = listings();
const numbering = { config: [
  { reference: "bullets", levels: [0, 1].map((l) => ({ level: l, format: LevelFormat.BULLET, text: l ? "-" : "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720 + l * 360, hanging: 360 } } } })) },
  { reference: "numbers", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
] };
const footer = new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ children: [PageNumber.CURRENT], font: L.FONT, size: 24 })] })] });
const doc = new Document({
  creator: STUDENT, title: "Codeingo - Field Project Report (Semester III)",
  styles: { default: { document: { run: { font: L.FONT, size: 24 } } } },
  numbering,
  sections: [{ properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1440, bottom: 1300, left: 1440, right: 1440 } } }, footers: { default: footer }, children: [...cover(), ...certs, ...front, ...lists, ...bodyParts] }],
});
Packer.toBuffer(doc).then((b) => {
  const out = process.argv[2] || path.join(HERE, "Aryan_Sawant_Codeingo_Field_Project_Report.docx");
  fs.writeFileSync(out, b);
  fs.writeFileSync(path.join(HERE, "registry3.json"), JSON.stringify({ toc, tables, figures }));
  console.log("written", out, b.length);
});
