const fs = require("fs");
const L = require("./lib");
const { D } = L;
const { Document, Packer, Paragraph, TextRun, AlignmentType, LevelFormat, Footer, PageNumber, PageOrientation, SectionType } = D;
const pagesFile = L.ROOT + "/builder/pages.json";
if (fs.existsSync(pagesFile)) L.setPages(JSON.parse(fs.readFileSync(pagesFile, "utf8")));

const front = require("./front");
const { ch1, ch1Report, ch2, ch2Report } = require("./ch1_2");
const { ch3, ch3Report } = require("./ch3");
const { ch4, ch4Report } = require("./ch4");
const { ch5Coding, ch5Testing, ch5Report } = require("./ch5");
const { ch6, ch6Report, ch7, ch7Report, annexes } = require("./ch6_7");

const tests = 95;
const A4 = { width: 11906, height: 16838 };
const margin = { top: 1440, bottom: 1440, left: 1440, right: 1440 };
const footer = (fmt) => ({ default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: L.FONT, size: 22 })] })] }) });
const noFooter = { default: new Footer({ children: [new Paragraph("")] }) };
const portrait = (num) => ({ page: { size: A4, margin, pageNumbers: num }, });
const numbering = { config: [
  { reference: "bullets", levels: [0, 1].map((l) => ({ level: l, format: LevelFormat.BULLET, text: l ? "-" : "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720 + l * 360, hanging: 360 } } } })) },
  ...["numbers", ...Array.from({ length: 14 }, (_, i) => `numbers${i + 2}`)].map((reference) => ({ reference, levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] })),
] };

// body is built first so the registries (toc/tables/figures) are filled before listings()
const body1 = [...ch1(), ...ch1Report(), ...ch2(), ...ch2Report(), ...ch3(), ...ch3Report(), ...ch4(), ...ch4Report(), ...ch5Coding()];
const t5 = ch5Testing(tests);
body1.push(...t5.intro);
const landscape = t5.cases;
const body2 = [...t5.after, ...ch5Report(), ...ch6(), ...ch6Report(), ...ch7(), ...ch7Report(), ...annexes()];
const certs = front.certificates();
const pref = front.preface();
const lists = front.listings();

const doc = new Document({
  creator: "Codeingo", title: "Codeingo - Field Project Report", styles: { default: { document: { run: { font: L.FONT, size: 24 } } } },
  numbering,
  sections: [].concat(0)&&[
    { properties: { page: { size: A4, margin: { top: 1000, bottom: 1000, left: 1300, right: 1300 } } }, footers: noFooter, children: front.cover() },
    { properties: { type: SectionType.NEXT_PAGE, page: { size: A4, margin, pageNumbers: { start: 1, formatType: D.NumberFormat.LOWER_ROMAN } } }, footers: footer(), children: [...certs, ...pref, ...lists] },
    { properties: { type: SectionType.NEXT_PAGE, page: { size: A4, margin, pageNumbers: { start: 1, formatType: D.NumberFormat.DECIMAL } } }, footers: footer(), children: body1 },
    { properties: { type: SectionType.NEXT_PAGE, page: { size: { width: 16838, height: 11906 }, orientation: PageOrientation.LANDSCAPE, margin: { top: 1000, bottom: 1000, left: 1000, right: 1000 } } }, footers: footer(), children: landscape },
    { properties: { type: SectionType.NEXT_PAGE, page: { size: A4, margin } }, footers: footer(), children: body2 },
  ].filter((_, i) => !process.env.ONLY || process.env.ONLY.split(",").includes(String(i))),
});
Packer.toBuffer(doc).then((b) => {
  const out = process.argv[2] || L.ROOT + "/Codeingo_Field_Project_Report.docx";
  fs.writeFileSync(out, b);
  fs.writeFileSync(L.ROOT + "/builder/registry.json", JSON.stringify({ toc: L.toc, tables: L.tables, figures: L.figures }));
  console.log("written", out, b.length);
});
