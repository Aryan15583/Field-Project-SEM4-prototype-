const L = require("./lib");
const { D, run, ph, p, center, blank, front, table, h4, toc, tables, figures, pageOf, TEXT_W } = L;
const { Paragraph, TextRun, AlignmentType, PositionalTab, PositionalTabAlignment, PositionalTabLeader, PositionalTabRelativeTo, PageBreak } = D;

const TITLE = "CODEINGO";
const SUBTITLE = "A Gamified, Secure Coding-Learning Platform";
const GROUP_ROWS = 5;

function cover() {
  const c = (t, o = {}) => center(t, { bold: true, after: o.after ?? 120, size: o.size || 26, line: 300 });
  return [
    c("A PROJECT REPORT ON", { size: 28, after: 200 }),
    c(TITLE, { size: 56, after: 80 }),
    center(SUBTITLE, { italics: true, size: 26, after: 360 }),
    c("A PROJECT REPORT SUBMITTED TO", { after: 60 }),
    c("THE UNIVERSITY OF MUMBAI IN PARTIAL FULFILMENT", { after: 60 }),
    c("FOR THE AWARD OF THE DEGREE OF", { after: 200 }),
    c("BACHELOR OF SCIENCE", { size: 30, after: 20 }),
    c("(INFORMATION TECHNOLOGY)", { size: 28, after: 240 }),
    c("By", { after: 100 }),
    center([ph("STUDENT NAME", { bold: true, size: 30 })], { after: 80 }),
    center([ph("SEAT NO. e.g. BSIT-V-2627-XXXXX", { bold: true, size: 26 })], { after: 260 }),
    c("UNDER THE ESTEEMED GUIDANCE OF", { after: 80 }),
    c("ASSISTANT PROFESSOR", { after: 60 }),
    center([ph("GUIDE NAME", { bold: true, size: 28 })], { after: 360 }),
    c("DEPARTMENT OF INFORMATION TECHNOLOGY", { after: 20, size: 24 }),
    c("& COMPUTER SCIENCE", { after: 280, size: 24 }),
    c("KERALEEYA SAMAJAM (REGD.) DOMBIVLI'S", { after: 60 }),
    c("MODEL COLLEGE", { size: 32, after: 60 }),
    c("(EMPOWERED AUTONOMOUS)", { size: 24, after: 20 }),
    center("(Affiliated to University of Mumbai)", { size: 22, after: 200 }),
    c("DOMBIVLI, 421201", { after: 20 }),
    c("MAHARASHTRA", { after: 20 }),
    c("OCTOBER 2026", { after: 0 }),
  ];
}

const college = () => [
  center("KERALEEYA SAMAJAM (REGD.) DOMBIVLI'S", { bold: true, size: 26, after: 20 }),
  center("MODEL COLLEGE (EMPOWERED AUTONOMOUS)", { bold: true, size: 26, after: 20 }),
  center("(Affiliated to University of Mumbai)", { size: 22, after: 20 }),
  center("DOMBIVLI - MAHARASHTRA - 421201", { size: 22, after: 120 }),
];
const sigRow = (a, b) => table([4513, 4513], null, [[[p(a, { align: AlignmentType.LEFT, after: 0, line: 260 })], [p(b, { align: AlignmentType.RIGHT, after: 0, line: 260 })]]], { size: 22 });

function certificates() {
  const noBorderSig = (pairs) => pairs.map(([a, b]) => table([4513, 4513], null, [[a, b]], { size: 22 }));
  const out = [];
  // 1) project certificate
  out.push(front("DEPARTMENT OF INFORMATION TECHNOLOGY & COMPUTER SCIENCE", { size: 24, before: 0, pageBreak: false }));
  out.push(front("CERTIFICATE", { pageBreak: false, size: 36 }));
  out.push(p(['This is to certify that the project entitled, "', run(TITLE, { bold: true }), '", is bonafide work of ', ph("STUDENT NAME"), " bearing Seat No: ", ph("SEAT NO"), " submitted in FIELD PROJECT of SEM V of BACHELOR OF SCIENCE in INFORMATION TECHNOLOGY."], { line: 400 }));
  out.push(...blank(5));
  out.push(table([4513, 4513], null, [[[p("Internal Guide", { align: AlignmentType.LEFT, after: 0 })], [p("Head of the Dept./Principal", { align: AlignmentType.RIGHT, after: 0 })]]], { size: 22 }));
  out.push(...blank(2));
  out.push(table([4513, 4513], null, [[[p("Internal Examiner", { align: AlignmentType.LEFT, after: 0 })], [p("External Examiner", { align: AlignmentType.RIGHT, after: 0 })]]], { size: 22 }));

  // 2) group certificate
  out.push(new Paragraph({ pageBreakBefore: true, alignment: AlignmentType.CENTER, spacing: { after: 20 }, children: [run("Keraleeya Samajam (Regd.) Dombivli's", { bold: true, size: 24 })] }));
  out.push(center("MODEL COLLEGE", { bold: true, size: 28, after: 20 }));
  out.push(center("(Empowered Autonomous)", { size: 22, after: 20 }));
  out.push(center("(Affiliated to University of Mumbai)", { size: 22, after: 20 }));
  out.push(center('Re-Accredited Grade "A" by NAAC', { size: 22, after: 240 }));
  out.push(center("CERTIFICATE", { bold: true, size: 36, after: 200 }));
  out.push(p(['This is to certify that the following students of the B.Sc.I.T. Program studying in Semester V, have successfully completed a group project titled: "', run(TITLE, { bold: true }), '" in the area of Information Technology specialization, during the academic year 2026-2027. The students listed below have contributed to this project work and to the best of our knowledge, the work is original and all information provided is accurate and relevant.'], { line: 340 }));
  out.push(p("List of Group members:", { bold: true, after: 80 }));
  out.push(table([900, 4700, 3426], ["Sr. No", "Name", "Roll/Seat No"], Array.from({ length: GROUP_ROWS }, (_, i) => [String(i + 1), [new Paragraph({ spacing: { after: 20 }, children: [ph("MEMBER NAME")] })], [new Paragraph({ spacing: { after: 20 }, children: [ph("ROLL / SEAT NO")] })]]), { size: 22 }));
  out.push(...blank(3));
  out.push(table([4513, 4513], null, [[[p("Internal Guide", { align: AlignmentType.LEFT, after: 0 })], [p("Head of the Dept./Principal", { align: AlignmentType.RIGHT, after: 0 })]]], { size: 22 }));
  out.push(...blank(2));
  out.push(table([4513, 4513], null, [[[p("Internal Examiner", { align: AlignmentType.LEFT, after: 0 })], [p("External Examiner", { align: AlignmentType.RIGHT, after: 0 })]]], { size: 22 }));

  // 3) individual certificate
  out.push(new Paragraph({ pageBreakBefore: true, alignment: AlignmentType.CENTER, spacing: { after: 20 }, children: [run("Keraleeya Samajam (Regd.) Dombivli's", { bold: true, size: 24 })] }));
  out.push(center("MODEL COLLEGE", { bold: true, size: 28, after: 20 }));
  out.push(center("(Empowered Autonomous)", { size: 22, after: 20 }));
  out.push(center("(Affiliated to University of Mumbai)", { size: 22, after: 20 }));
  out.push(center('Re-Accredited Grade "A" by NAAC', { size: 22, after: 20 }));
  out.push(center('Conferred with "Best College Award" by University of Mumbai', { size: 22, after: 280 }));
  out.push(center("CERTIFICATE", { bold: true, size: 36, after: 240 }));
  out.push(p(["I hereby certify that Mr./Ms. ", ph("STUDENT NAME"), ", Student of B.Sc.I.T. Program studying in V Semester, has completed a project titled ", run(TITLE, { bold: true }), " in the area of Information Technology specialization/Major for the academic year 2026-2027."], { line: 400 }));
  out.push(p("To the best of my knowledge the work of the student is original and the information included in the project is correct.", { line: 400 }));
  out.push(...blank(4));
  out.push(table([4513, 4513], null, [[[p("Internal Guide", { align: AlignmentType.LEFT, after: 0 })], [p("Head of the Dept./Principal", { align: AlignmentType.RIGHT, after: 0 })]]], { size: 22 }));
  out.push(...blank(2));
  out.push(table([4513, 4513], null, [[[p("Internal Examiner", { align: AlignmentType.LEFT, after: 0 })], [p("External Examiner", { align: AlignmentType.RIGHT, after: 0 })]]], { size: 22 }));
  return out.filter(Boolean);
}

function declarationPages() {
  const dates = Array.from({ length: 10 }, (_, i) => [String(i + 1), [new Paragraph({ spacing: { after: 20 }, children: [ph("DATE")] })], ""]);
  return [
    front("GUIDE INTERACTION DECLARATION", { underline: true, size: 30 }),
    p(["I, the undersigned ", ph("STUDENT NAME"), " Roll/Seat No. ", ph("ROLL NO / SEAT NO"), " studying in the V Semester of B.Sc.I.T. Program, hereby declare that I am carrying out my Field Project under the guidance of ", ph("GUIDE NAME"), " and I have interacted with my Guide on the following dates as part of my project development process:"], { line: 340 }),
    p("Guide Interaction Record", { bold: true, after: 80 }),
    table([800, 3000, 5226], ["Sr. No.", "Date", "Signature of the Internal Guide"], dates, { size: 22 }),
    p("", { after: 100 }),
    p("I affirm that the information provided above is true to the best of my knowledge and that I have received timely academic guidance throughout the project duration.", { line: 340 }),
    ...blank(1),
    p("Signature of the Student", { align: AlignmentType.RIGHT, bold: true }),
    p("Guide Certification", { bold: true, after: 60 }),
    p("Certified that the above interactions have been held as mentioned.", { after: 200 }),
    p("Signature of Internal Guide", { align: AlignmentType.RIGHT, bold: true }),
  ];
}

function preface() {
  return [
    ...declarationPages(),
    front("ABSTRACT", { size: 32 }),
    p([run("CODEINGO", { bold: true }), " is a gamified web platform that teaches programming through short, interactive lessons, in the spirit of language-learning apps such as Duolingo. A learner signs in with a Google account, protects it with mandatory 2-step verification (an emailed code, an authenticator app, or a passkey), and follows a structured path of units and lessons that run from beginner to advanced level."], { line: 340 }),
    p("The platform offers ten courses - Python, JavaScript, TypeScript, Java, C++, C, SQL, HTML & CSS, Git, and Data Structures & Algorithms - with 438 lessons, 2,130 exercises and 30 hands-on projects. Learners do not only read: in every lesson they write real programs that run safely inside the browser (Python through WebAssembly, JavaScript and TypeScript in sandboxed workers, SQL on an in-browser SQLite engine, Git in a built-in simulator). Answers are graded on the server, and the expected results are never sent to the browser, so they cannot be copied.", { line: 340 }),
    p("To keep learners motivated the system adds XP, streaks, hearts, badges, a daily challenge, chapter tests with jump-ahead readiness tests, spaced-repetition practice for mistakes, public certificates, friends and weekly leagues, timed weekly contests with a live leaderboard, and optional streak reminder e-mails. The design was guided by a requirement survey of 43 young learners, which showed that 65% find game-like learning appealing, that confusing syntax and lack of guidance are the main reasons for quitting, and that building real projects is the strongest motivator.", { line: 340 }),
    p("Codeingo is built with Next.js and React on the front end and FastAPI with PostgreSQL on the back end. It is installable as a progressive web app, available in a light (white/blue) and a dark (black/green) theme, protected by a strict security design (CSRF protection, content-security policy, rate limiting, audit log, hidden admin panel) and verified by 95 automated tests and by executing every one of its 492 runnable reference solutions.", { line: 340 }),
    front("ACKNOWLEDGEMENT", { size: 32 }),
    p(["It gives me pleasure to present my Field Project on ", run('"CODEINGO"', { bold: true }), ". This is my milestone in Bachelor of Science (Information Technology). I would like to express my sincere thanks to all the teachers who helped me throughout the project. I would like to acknowledge the help and guidance provided by our guide ", ph("GUIDE NAME"), " in all places during the presentation of this project."], { line: 360 }),
    p(["I am thankful to our honorable Principal ", ph("PRINCIPAL NAME"), ". Onwards my project works, I am also thankful to the staff members of the IT-CS department for their moral support. I extend my gratitude to ", ph("COORDINATOR NAME"), ", Coordinator of IT & CS Department for the support and guidance."], { line: 360 }),
    p("I also thank the 43 learners who took the time to answer the requirement survey; their honest answers shaped the features of this platform. Finally, I thank my family and friends for their constant encouragement.", { line: 360 }),
    ...blank(3),
    p("Name and Signature of Student", { align: AlignmentType.RIGHT, bold: true, after: 60 }),
    p([ph("STUDENT NAME")], { align: AlignmentType.RIGHT }),
    front("DECLARATION", { size: 32 }),
    p(['I hereby declare that the project entitled, "', run("CODEINGO", { bold: true }), '" done at Keraleeya Samajam (Regd.) Dombivli\'s Model College (Empowered Autonomous), has not been in any case duplicated to submit to any other university for the award of any degree. To the best of my knowledge other than me, no one has submitted to any other university.'], { line: 380 }),
    p("The project is done in partial fulfilment of the requirements for the award of degree of BACHELOR OF SCIENCE (INFORMATION TECHNOLOGY) to be submitted as a Fifth Semester Field Project as part of our curriculum.", { line: 380 }),
    ...blank(3),
    p("Name and Signature of Student", { align: AlignmentType.RIGHT, bold: true, after: 60 }),
    p([ph("STUDENT NAME")], { align: AlignmentType.RIGHT }),
  ];
}

// ---- table of contents / list of tables / list of figures (static, page numbers filled from a first render)
function dotted(left, page, o = {}) {
  return new Paragraph({
    tabStops: [{ type: D.TabStopType.RIGHT, position: TEXT_W, leader: D.LeaderType.DOT }], spacing: { after: o.after ?? 60, line: 280 }, indent: { left: o.indent || 0, right: 700, hanging: 0 },
    children: [new TextRun({ text: left + "\t" + page, font: L.FONT, size: o.size || 24, bold: o.bold })],
  });
}
function listings() {
  const out = [front("TABLE OF CONTENTS", { size: 32 })];
  for (const e of toc) {
    if (e.level === 1) out.push(dotted(`${e.label}   ${e.title}`, pageOf(e.search), { bold: true, after: 80, indent: 0 }));
    else if (e.level === 2) out.push(dotted(`${e.label}   ${e.title}`, pageOf(e.search), { indent: 360, size: 23 }));
    else out.push(dotted(`${e.label}   ${e.title}`, pageOf(e.search), { indent: 900, size: 22, after: 30 }));
  }
  out.push(front("LIST OF TABLES", { size: 32 }));
  for (const t of tables) out.push(dotted(`${t.label}   ${t.text}`, pageOf(t.search), { size: 23, after: 50 }));
  out.push(front("LIST OF FIGURES", { size: 32 }));
  for (const f of figures) out.push(dotted(`${f.label}   ${f.text}`, pageOf(f.search), { size: 23, after: 50 }));
  return out;
}

module.exports = { cover, certificates, preface, listings };
