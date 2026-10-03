// Helpers for the project report (University of Mumbai B.Sc. IT field-project format).
const fs = require("fs");
const path = require("path");
const D = require(process.env.DOCX_PATH || "/tmp/dx/node_modules/docx");
const {
  Paragraph, TextRun, Table, TableRow, TableCell, ImageRun, AlignmentType, WidthType, ShadingType, BorderStyle, HeadingLevel,
  PageBreak, PositionalTab, PositionalTabAlignment, PositionalTabLeader, PositionalTabRelativeTo, VerticalAlign, LevelFormat,
} = D;

const ROOT = path.resolve(__dirname, "..");
const FONT = "Times New Roman";
const MONO = "Courier New";
const TEXT_W = 9026; // A4 portrait, 1" margins (DXA)

// ---- registries filled while building (used for the static TOC / list of tables / list of figures)
const toc = []; // {level, label, search}
const tables = []; // {label, search}
const figures = []; // {label, search}
let pagesMap = {}; // search string -> printed page number (second pass)
const setPages = (m) => (pagesMap = m);
const pageOf = (search) => (pagesMap[search] != null ? String(pagesMap[search]) : "0");

// ---- text
const run = (text, o = {}) => new TextRun({ text, font: o.mono ? MONO : FONT, size: o.size || 24, bold: o.bold, italics: o.italics, color: o.color, highlight: o.highlight, break: o.break, underline: o.underline });
/** A value the student must fill in (highlighted yellow so it can't be missed). */
const ph = (text, o = {}) => run(`[${text}]`, { ...o, highlight: "yellow" });
const asRuns = (c, o) => (Array.isArray(c) ? c.map((x) => (typeof x === "string" ? run(x, o) : x)) : [run(c, o)]);

const p = (content, o = {}) =>
  new Paragraph({
    alignment: o.align ?? AlignmentType.JUSTIFIED,
    spacing: { after: o.after ?? 140, before: o.before ?? 0, line: o.line ?? 320 },
    indent: o.indent,
    keepNext: o.keepNext,
    keepLines: o.keepLines,
    pageBreakBefore: o.pageBreak,
    children: asRuns(content, o),
  });
const center = (content, o = {}) => p(content, { ...o, align: AlignmentType.CENTER });
const blank = (n = 1) => Array.from({ length: n }, () => p("", { after: 0 }));

// ---- headings (static TOC is built from the registry; real heading styles keep Word's navigation pane working)
function chapter(num, title, tocTitle) {
  const search = `CHAPTER ${num} ${title.toUpperCase()}`;
  toc.push({ level: 1, label: `Chapter ${num}`, title: tocTitle || title, search });
  return new Paragraph({
    heading: HeadingLevel.HEADING_1, alignment: AlignmentType.CENTER, pageBreakBefore: true, spacing: { before: 0, after: 360 },
    children: [run(`CHAPTER ${num}`, { bold: true, size: 40 }), run(title.toUpperCase(), { bold: true, size: 40, break: 1 })],
  });
}
function h2(label, title) {
  toc.push({ level: 2, label, title, search: `${label} ${title}` });
  return new Paragraph({ heading: HeadingLevel.HEADING_2, keepNext: true, spacing: { before: 280, after: 140 }, children: [run(`${label} ${title}`, { bold: true, size: 28 })] });
}
function h3(label, title) {
  toc.push({ level: 3, label, title, search: `${label} ${title}` });
  return new Paragraph({ heading: HeadingLevel.HEADING_3, keepNext: true, spacing: { before: 200, after: 100 }, children: [run(`${label} ${title}`, { bold: true, size: 24 })] });
}
const h4 = (text) => new Paragraph({ keepNext: true, spacing: { before: 160, after: 80 }, children: [run(text, { bold: true, size: 24 })] });
/** Front-matter title (not in the TOC): centered, bold, underlined like the template's. */
const front = (text, o = {}) => new Paragraph({ alignment: AlignmentType.CENTER, pageBreakBefore: o.pageBreak !== false, spacing: { before: o.before ?? 0, after: 360 }, children: [run(text, { bold: true, size: o.size || 32, underline: o.underline ? {} : undefined })] });

// ---- lists
const bullet = (content, o = {}) => new Paragraph({ numbering: { reference: "bullets", level: o.level || 0 }, alignment: AlignmentType.JUSTIFIED, spacing: { after: 70, line: 300 }, children: asRuns(content, o) });
const bullets = (items, o) => items.map((i) => bullet(i, o));
const numbered = (items, ref = "numbers") => items.map((i) => new Paragraph({ numbering: { reference: ref, level: 0 }, alignment: AlignmentType.JUSTIFIED, spacing: { after: 80, line: 300 }, children: asRuns(i) }));
/** "Label: text" bullet with a bold label. */
const lb = (label, text) => bullet([run(`${label}: `, { bold: true }), run(text)]);

// ---- tables
const border = { style: BorderStyle.SINGLE, size: 4, color: "808080" };
const borders = { top: border, bottom: border, left: border, right: border };
function cell(content, w, o = {}) {
  const paras = (Array.isArray(content) && content.length && content[0] instanceof Paragraph ? content : [null]).map((x) => x);
  const children = paras[0] instanceof Paragraph ? paras : (Array.isArray(content) ? content : [content]).map((c) => (c instanceof Paragraph ? c : new Paragraph({ alignment: o.align ?? AlignmentType.LEFT, spacing: { after: 20, line: 250 }, children: asRuns(String(c), { size: o.size || 20, bold: o.bold, color: o.color }) })));
  return new TableCell({
    width: { size: w, type: WidthType.DXA }, borders, verticalAlign: o.valign || VerticalAlign.TOP,
    shading: o.fill ? { type: ShadingType.CLEAR, fill: o.fill, color: "auto" } : undefined,
    margins: { top: 50, bottom: 50, left: 90, right: 90 }, columnSpan: o.span, children,
  });
}
/** table(widths, header[], rows[][], {size, headFill}) - widths in DXA, must sum to the table width. */
function table(widths, header, rows, o = {}) {
  const total = widths.reduce((a, b) => a + b, 0);
  const size = o.size || 20;
  const head = header
    ? [new TableRow({ tableHeader: true, cantSplit: true, children: header.map((h, i) => cell(String(h), widths[i], { bold: true, fill: o.headFill || "D9E2F3", size })) })]
    : [];
  const body = rows.map(
    (r, ri) => new TableRow({ cantSplit: o.cantSplit !== false, children: r.map((c, i) => cell(c, widths[i], { size, fill: o.zebra && ri % 2 ? "F5F7FB" : undefined, bold: o.boldFirst && i === 0 })) }),
  );
  return new Table({ width: { size: total, type: WidthType.DXA }, columnWidths: widths, rows: [...head, ...body] });
}
const keyValue = (pairs, w = [3000, 6026], size = 22) => table(w, null, pairs.map(([k, v]) => [[new Paragraph({ spacing: { after: 20 }, children: [run(k, { bold: true, size })] })], Array.isArray(v) ? [new Paragraph({ spacing: { after: 20 }, children: v })] : v]), { size });
function captionTable(label, text) {
  tables.push({ label, text, search: `${label}: ${text}` });
  return new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 200, after: 100 }, children: [run(`${label}: ${text}`, { bold: true, size: 22 })] });
}
function captionFigure(label, text) {
  figures.push({ label, text, search: `${label}: ${text}` });
  return new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 80, after: 220 }, children: [run(`${label}: ${text}`, { italics: true, size: 22 })] });
}

// ---- images
function pngSize(file) {
  const b = fs.readFileSync(file);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20), data: b };
}
/** Inserts an image scaled to fit maxW x maxH pixels (96 dpi) + a numbered caption. */
function figure(rel, label, text, o = {}) {
  const file = path.join(ROOT, rel);
  const { w, h, data } = pngSize(file);
  const maxW = o.maxW || 600, maxH = o.maxH || 640;
  const s = Math.min(maxW / w, maxH / h, 1.6);
  const out = [
    new Paragraph({
      alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 120, after: 60 },
      children: [new ImageRun({ type: "png", data, transformation: { width: Math.round(w * s), height: Math.round(h * s) }, altText: { title: label, description: text, name: label } })],
    }),
    captionFigure(label, text),
  ];
  return out;
}

// ---- code blocks (one shaded single-cell table; monospace)
function code(src, o = {}) {
  const lines = src.replace(/\t/g, "    ").split("\n");
  const children = lines.map((l) => new Paragraph({ spacing: { after: 0, line: 220 }, children: [new TextRun({ text: l === "" ? " " : l, font: MONO, size: o.size || 17 })] }));
  return new Table({
    width: { size: TEXT_W, type: WidthType.DXA }, columnWidths: [TEXT_W],
    rows: [new TableRow({ children: [new TableCell({ width: { size: TEXT_W, type: WidthType.DXA }, shading: { type: ShadingType.CLEAR, fill: "F3F4F6", color: "auto" }, borders, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children })] })],
  });
}

// ---- Guide Interaction Report (after every chapter, as in the template)
function guideReport(chapterLabel, projectTitle, { overview, outcomes, challenges, feedback }) {
  const info = [
    ["Name of the Student", [ph("STUDENT NAME", { size: 22 })]],
    ["Program /Semester", "B.Sc I.T./ Semester V"],
    ["Roll No/Seat No", [ph("ROLL NO / SEAT NO", { size: 22 })]],
    ["Major Subject / Specialization", "Information Technology"],
    ["Field project Title", projectTitle],
    ["Name of the Faculty mentor", [ph("GUIDE NAME", { size: 22 })]],
  ];
  const para = (t) => p(t, { after: 100 });
  return [
    new Paragraph({ pageBreakBefore: true, alignment: AlignmentType.CENTER, spacing: { after: 100 }, children: [run("GUIDE INTERACTION REPORT", { bold: true, size: 30 })] }),
    center("(To be maintained by the student and submitted as part of the Field Project documentation)", { size: 20, italics: true, after: 200 }),
    keyValue(info, [3400, 5626]),
    p("", { after: 120 }),
    h4("Overview (Max 150 Words)"),
    p("(Brief summary of key activities, tasks and projects undertaken during the period)", { size: 20, italics: true, after: 80 }),
    p(chapterLabel, { bold: true, after: 80 }),
    ...[].concat(overview).map(para),
    h4("Learning Outcomes (Max 100 words):"),
    ...[].concat(outcomes).map(para),
    h4("Challenges Faced (Max 100 words):"),
    ...[].concat(challenges).map(para),
    h4("Mentor Feedback and Suggestions (Max 100 words):"),
    feedback ? p(feedback) : p([ph("To be filled in by the guide")], { after: 60 }),
    ...blank(2),
    new Paragraph({ alignment: AlignmentType.RIGHT, children: [run("Signature of the Internal Guide", { size: 22 })] }),
  ];
}

module.exports = { D, ROOT, FONT, MONO, TEXT_W, toc, tables, figures, setPages, pageOf, run, ph, p, center, blank, chapter, h2, h3, h4, front, bullet, bullets, numbered, lb, cell, table, keyValue, captionTable, captionFigure, figure, code, guideReport, border, borders, asRuns };
