/*
 * Quiz questions and tips for the "server is waking up" screen (components/WakingScreen.jsx).
 * To add a language: add one entry below - it shows up in the dropdown and in the "Mix" automatically.
 *   slugs: course slugs it belongs to (so the quiz opens on the course the learner was last in)
 *   quiz:  [question, [options], index of the right option]
 */
export const TOPICS = {
  python: {
    slugs: ["python"],
    label: "Python",
    tips: ["Python is named after Monty Python, not the snake.", "Indentation is part of Python's syntax - it marks blocks of code.", "Tip: len(x) tells you how many items a list or text has."],
    quiz: [
      ["Which symbol starts a comment in Python?", ["//", "#", "<!--"], 1],
      ["What does print(2 + 3 * 2) show?", ["10", "8", "12"], 1],
      ["Which one makes a list?", ["[1, 2, 3]", "{1, 2, 3}", "(1 2 3)"], 0],
      ["What does len(\"code\") return?", ["3", "4", "5"], 1],
      ["Which keyword starts a function?", ["func", "def", "fun"], 1],
      ["What is the type of 3.14?", ["int", "str", "float"], 2],
    ],
  },
  javascript: {
    slugs: ["javascript", "typescript"],
    label: "JavaScript",
    tips: ["JavaScript was written in just 10 days.", "Use === instead of == to compare without surprises.", "Tip: console.log() is your best friend for checking values."],
    quiz: [
      ["Which keyword makes a variable you can't reassign?", ["var", "let", "const"], 2],
      ["What does [1, 2, 3].length give?", ["2", "3", "4"], 1],
      ["Which prints to the console?", ["console.log()", "print()", "echo()"], 0],
      ["What is typeof \"hi\" ?", ["string", "text", "char"], 0],
      ["Which is an arrow function?", ["(x) => x * 2", "function => x", "x -> x * 2"], 0],
      ["What does '5' + 3 give?", ["8", "'53'", "error"], 1],
    ],
  },
  sql: {
    slugs: ["sql"],
    label: "SQL",
    tips: ["SQL is usually pronounced 'sequel' or letter by letter - both are fine.", "Always add WHERE to UPDATE and DELETE unless you mean every row!", "Tip: SELECT * is handy for peeking, but name the columns you need."],
    quiz: [
      ["Which command reads rows from a table?", ["SELECT", "FETCHALL", "READ"], 0],
      ["Which clause filters rows?", ["WHERE", "ORDER", "GROUP"], 0],
      ["What does ORDER BY age DESC do?", ["Oldest first", "Youngest first", "Deletes ages"], 0],
      ["Which function counts rows?", ["COUNT()", "TOTAL()", "NUMBER()"], 0],
      ["What does a PRIMARY KEY do?", ["Uniquely identifies a row", "Encrypts the table", "Sorts the table"], 0],
      ["Which adds a new row?", ["INSERT INTO", "ADD ROW", "PUT"], 0],
    ],
  },
  htmlcss: {
    slugs: ["html-css"],
    label: "HTML & CSS",
    tips: ["The very first website is still online.", "Tip: one <h1> per page is a good habit for headings.", "Tip: browser DevTools (F12) let you edit CSS live."],
    quiz: [
      ["What does HTML stand for?", ["HyperText Markup Language", "High Tech Modern Logic", "Home Tool Making Language"], 0],
      ["Which tag makes a link?", ["<a>", "<link>", "<url>"], 0],
      ["What does CSS mostly control?", ["How a page looks", "The database", "Internet speed"], 0],
      ["Which CSS property changes text colour?", ["color", "font-paint", "text-style"], 0],
      ["Which tag is the biggest heading?", ["<h1>", "<h6>", "<head>"], 0],
      ["Which layout system arranges items in a row or column?", ["Flexbox", "Floatbox", "Rowbox"], 0],
    ],
  },
  git: {
    slugs: ["git"],
    label: "Git",
    tips: ["Git was created by Linus Torvalds in 2005, in about two weeks.", "Tip: commit small and often, with a message that says why.", "Tip: git status tells you what's going on - use it a lot."],
    quiz: [
      ["Which command saves a snapshot to history?", ["git commit", "git cook", "git paint"], 0],
      ["Which command shows what changed?", ["git status", "git where", "git look"], 0],
      ["What does git clone do?", ["Copies a repository", "Deletes a branch", "Makes a backup of Git"], 0],
      ["What is a branch?", ["A parallel line of work", "A type of error", "A file format"], 0],
      ["Which stages files for the next commit?", ["git add", "git push", "git pull"], 0],
      ["Which uploads your commits to a remote?", ["git push", "git pull", "git fetch"], 0],
    ],
  },
  java: {
    slugs: ["java", "cpp", "c"],
    label: "Java / C / C++",
    tips: ["Java's mascot is called Duke.", "In C and C++, every statement ends with a semicolon.", "Tip: these languages are compiled - read the compiler's first error first."],
    quiz: [
      ["Which Java method is the program's entry point?", ["main", "start", "run"], 0],
      ["What does int x = 5; do?", ["Stores 5 in a whole-number variable", "Prints 5", "Makes a loop"], 0],
      ["Which loop runs a set number of times?", ["for", "if", "else"], 0],
      ["What ends a statement in C?", [";", ".", ":"], 0],
      ["Which prints in C++?", ["std::cout", "print()", "echo"], 0],
      ["What does 7 / 2 give with whole numbers?", ["3", "3.5", "4"], 0],
    ],
  },
};

export const TOPIC_IDS = Object.keys(TOPICS);

/** Every question from every topic, for the default "Mix of everything". */
export const MIX_QUIZ = TOPIC_IDS.flatMap((id) => TOPICS[id].quiz);
export const MIX_TIPS = TOPIC_IDS.flatMap((id) => TOPICS[id].tips);

/** The topic for a course slug (e.g. "cpp" -> "java"), or "mix" when there is none. */
export const topicForCourse = (slug) => TOPIC_IDS.find((id) => TOPICS[id].slugs?.includes(slug)) || "mix";
