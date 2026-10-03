/*
 * Codeingo's mascot cast. Every mascot is a 16x16 pixel drawing built from one head/body template plus
 * its own top (ears, antennae, hats), crown, body, accessories and colours - so they all share Codi's
 * face system (eyes follow the pointer, blink, moods) but each has its own silhouette and personality.
 *
 * Pixel characters:  P body  S shade / outline  W face plate  G accent  A second accent  B third accent
 *                    E eye colour (used for pupils drawn into the art)   . empty
 */

const EMPTY = "................";
const CROWN = "...PPPPPPPPPP...";
const HEAD_TOP = "..PPPPPPPPPPPP.."; // row 3
const PLATE = "..PWWWWWWWWWWP.."; // rows 4-9
const CHIN = "..PPPPPPPPPPPP.."; // row 10
const COLLAR = "...SSSSSSSSSS..."; // row 11
const TORSO = "...PPPPPPPPPP..."; // rows 12-14
const FEET = "....SSS..SSS...."; // row 15

/** Builds the 16 rows from a few overrides, then paints single-pixel extras on top. */
function art({ top = [EMPTY, EMPTY], crown = CROWN, head = {}, body = [COLLAR, TORSO, TORSO, TORSO, FEET], dots = [] }) {
  const rows = [
    ...top,
    crown,
    head[3] || HEAD_TOP,
    ...[4, 5, 6, 7, 8, 9].map((r) => head[r] || PLATE),
    head[10] || CHIN,
    ...body,
  ];
  const grid = rows.map((r) => r.split(""));
  for (const [ch, pts] of dots) for (const [x, y] of pts) grid[y][x] = ch;
  return grid.map((r) => r.join(""));
}
const col = (x, ys) => ys.map((y) => [x, y]);
const row = (y, xs) => xs.map((x) => [x, y]);

// Arm shapes (drawn separately so they can wave). Each is [left pixels, right pixels].
const ARMS = {
  brackets: [[[1, 12], [0, 13], [1, 14]], [[14, 12], [15, 13], [14, 14]]], // < >   (Codi)
  paws: [[[2, 12], [2, 13]], [[13, 12], [13, 13]]],
  nubs: [[[3, 12], [3, 13]], [[12, 12], [12, 13]]],
  flippers: [[[2, 12], [1, 13], [1, 14]], [[13, 12], [14, 13], [14, 14]]],
  wings: [[[1, 10], [1, 11], [0, 11], [0, 12], [1, 12]], [[14, 10], [14, 11], [15, 11], [15, 12], [14, 12]]],
  fists: [[[0, 12], [0, 13]], [[15, 12], [15, 13]]],
  wand: [[[2, 12], [2, 13]], [[13, 12], [14, 11], [15, 10]]],
  none: [[], []],
};

const SHINE = "rgba(255,255,255,0.55)";

export const MASCOTS = [
  {
    id: "codi",
    name: "Codi",
    tagline: "The original screen-faced bot",
    glow: true,
    arms: "brackets",
    palette: { P: "rgb(var(--primary))", S: "rgb(var(--primary-strong))", W: "rgb(var(--codi-screen))", G: "rgb(var(--gold))", eye: "rgb(var(--codi-eye))", shine: "rgb(var(--codi-shine))" },
    rows: art({ top: [".......GG.......", ".......SS......."] }),
  },
  {
    id: "kitto",
    name: "Kitto",
    tagline: "Curious cat who pounces on bugs",
    arms: "paws",
    palette: { P: "#f59e0b", S: "#b45309", W: "#fff7ed", G: "#fb7185", A: "#fde68a", eye: "#1f2937", shine: SHINE },
    rows: art({
      top: ["..SS........SS..", "..SPS......SPS.."],
      crown: HEAD_TOP,
      dots: [["G", [[3, 1], [12, 1], [3, 8], [12, 8]]], ["S", [[15, 12], [14, 13], [15, 13], [13, 14]]]],
    }),
  },
  {
    id: "pupper",
    name: "Pupper",
    tagline: "Loyal pup that fetches answers",
    arms: "paws",
    palette: { P: "#d6a46b", S: "#7c4a21", W: "#fff4e0", G: "#8b5a2b", A: "#5b3a1a", eye: "#2b1608", shine: SHINE },
    rows: art({
      dots: [["G", [...col(1, [3, 4, 5, 6, 7, 8]), ...col(14, [3, 4, 5, 6, 7, 8]), [2, 3], [13, 3]]], ["A", [[9, 4], [10, 4], [11, 4], [11, 5]]], ["G", [[14, 12], [15, 11]]]],
    }),
  },
  {
    id: "owly",
    name: "Owly",
    tagline: "Night owl, loves late-night code",
    arms: "wings",
    palette: { P: "#92603a", S: "#4a2f1c", W: "#fef3c7", G: "#f97316", A: "#fbbf24", eye: "#1c1008", shine: SHINE },
    rows: art({
      top: ["..S..........S..", "..SS........SS.."],
      crown: HEAD_TOP,
      dots: [
        ["A", [...row(5, [4, 5, 6, 7]), ...row(8, [4, 5, 6, 7]), ...row(5, [8, 9, 10, 11]), ...row(8, [8, 9, 10, 11]), [4, 6], [4, 7], [7, 6], [7, 7], [8, 6], [8, 7], [11, 6], [11, 7]]],
        ["G", [[7, 8], [8, 8]]],
        ["A", [[5, 12], [7, 12], [9, 12], [6, 13], [8, 13], [10, 13], [5, 14], [7, 14], [9, 14]]],
      ],
    }),
  },
  {
    id: "foxy",
    name: "Foxy",
    tagline: "Quick fox, quicker at loops",
    arms: "paws",
    palette: { P: "#f97316", S: "#9a3412", W: "#ffedd5", G: "#fdba74", A: "#ffffff", eye: "#2a1004", shine: SHINE },
    rows: art({
      top: ["...S........S...", "..SPS......SPS.."],
      crown: HEAD_TOP,
      dots: [
        ["A", [[3, 8], [3, 9], [4, 9], [12, 8], [11, 9], [12, 9]]],
        ["P", [[14, 13], [15, 12], [15, 13], [14, 14]]],
        ["A", [[15, 11], [15, 14]]],
        ["G", [[3, 1], [12, 1]]],
      ],
    }),
  },
  {
    id: "pandy",
    name: "Pandy",
    tagline: "Calm panda, bamboo-powered",
    arms: "paws",
    palette: { P: "#f8fafc", S: "#374151", W: "#ffffff", G: "#fda4af", A: "#374151", eye: "#ffffff", shine: SHINE },
    rows: art({
      top: ["..SS........SS..", "..SS........SS.."],
      dots: [
        ["A", [...[3, 4, 5, 6].flatMap((x) => [5, 6, 7, 8].map((y) => [x, y])), ...[9, 10, 11, 12].flatMap((x) => [5, 6, 7, 8].map((y) => [x, y]))]],
        ["G", [[3, 9], [12, 9]]],
      ],
    }),
  },
  {
    id: "froggo",
    name: "Froggo",
    tagline: "Hops through every challenge",
    arms: "paws",
    palette: { P: "#22c55e", S: "#166534", W: "#dcfce7", G: "#fda4af", A: "#bbf7d0", eye: "#052e16", shine: SHINE },
    rows: art({
      top: ["..SSSS....SSSS..", "..SWES....SEWS.."],
      crown: HEAD_TOP,
      body: [COLLAR, TORSO, TORSO, TORSO, "..SSSS....SSSS.."],
      dots: [["G", [[3, 8], [12, 8]]], ["A", [...row(12, [5, 6, 7, 8, 9, 10]), ...row(13, [5, 6, 7, 8, 9, 10]), ...row(14, [6, 7, 8, 9])]]],
    }),
  },
  {
    id: "rexo",
    name: "Rexo",
    tagline: "Tiny dino with big ideas",
    arms: "nubs",
    palette: { P: "#14b8a6", S: "#0f766e", W: "#ccfbf1", G: "#f59e0b", A: "#99f6e4", eye: "#042f2e", shine: SHINE },
    rows: art({
      top: [EMPTY, ".....G..G..G...."],
      dots: [
        ["A", [...row(12, [5, 6, 7, 8, 9, 10]), ...row(13, [5, 6, 7, 8, 9, 10]), ...row(14, [6, 7, 8, 9])]],
        ["P", [[13, 13], [14, 13], [14, 14]]],
        ["S", [[15, 15], [15, 14]]],
      ],
    }),
  },
  {
    id: "octo",
    name: "Octo",
    tagline: "Eight arms, zero bugs",
    arms: "none",
    palette: { P: "#a855f7", S: "#6b21a8", W: "#f3e8ff", G: "#f472b6", A: "#d8b4fe", eye: "#2e1065", shine: SHINE },
    rows: art({
      top: ["....SSSSSSSS....", "...SPPPPPPPPS..."],
      crown: "..PPPPPPPPPPPP..",
      body: ["..SSSSSSSSSSSS..", CHIN, ".PPP.PP..PP.PPP.", ".PP..PP..PP..PP.", "PP..PP....PP..PP"],
      dots: [["A", [[5, 1], [10, 1], [4, 2]]], ["G", [[3, 8], [12, 8]]]],
    }),
  },
  {
    id: "ghosty",
    name: "Ghosty",
    tagline: "Friendly ghost of old code",
    arms: "nubs",
    palette: { P: "#c7d2fe", S: "#818cf8", W: "#f5f3ff", G: "#fbcfe8", A: "#e0e7ff", eye: "#1e1b4b", shine: SHINE },
    rows: art({
      top: ["....SSSSSSSS....", "...SPPPPPPPPS..."],
      crown: "..SPPPPPPPPPPS..",
      body: [CHIN, CHIN, CHIN, CHIN, "..PP.PPPPPP.PP.."],
      dots: [["G", [[3, 8], [12, 8]]], ["A", [[4, 11], [11, 12]]]],
    }),
  },
  {
    id: "rocky",
    name: "Rocky",
    tagline: "Solid as granite, slow and sure",
    arms: "fists",
    palette: { P: "#94a3b8", S: "#475569", W: "#e2e8f0", G: "#fde047", A: "#4ade80", eye: "#0f172a", shine: SHINE },
    rows: art({
      top: [EMPTY, "....A.AA..AA.A.."],
      crown: "..PPPPPPPPPPPP..",
      head: {
        3: ".PPPPPPPPPPPPPP.",
        4: ".PPWWWWWWWWWWPP.",
        5: ".PPWWWWWWWWWWPP.",
        6: ".PPWWWWWWWWWWPP.",
        7: ".PPWWWWWWWWWWPP.",
        8: ".PPWWWWWWWWWWPP.",
        9: ".PPWWWWWWWWWWPP.",
        10: ".PPPPPPPPPPPPPP.",
      },
      body: [".SSSSSSSSSSSSSS.", ".PPPPPPPPPPPPPP.", ".PPPPPPPPPPPPPP.", ".PPPPPPPPPPPPPP.", "..SSSS....SSSS.."],
      dots: [["G", [[7, 0]]], ["S", [[2, 12], [3, 13], [2, 14], [12, 13], [13, 12]]]],
    }),
  },
  {
    id: "bunny",
    name: "Bunny",
    tagline: "Hops from lesson to lesson",
    arms: "paws",
    palette: { P: "#f9a8d4", S: "#be185d", W: "#fdf2f8", G: "#fb7185", A: "#ffffff", eye: "#500724", shine: SHINE },
    rows: art({
      top: ["...PGP....PGP...", "...PGP....PGP..."],
      dots: [["G", [[3, 8], [12, 8]]], ["A", [[13, 14], [14, 14], [13, 13]]]],
    }),
  },
  {
    id: "pengu",
    name: "Pengu",
    tagline: "Cool-headed, scarf always on",
    arms: "flippers",
    palette: { P: "#334155", S: "#0f172a", W: "#f1f5f9", G: "#f59e0b", A: "#f8fafc", B: "#ef4444", eye: "#0f172a", shine: SHINE },
    rows: art({
      body: ["...BBBBBBBBBB...", TORSO, TORSO, TORSO, "....GGG..GGG...."],
      dots: [
        ["A", [...row(12, [5, 6, 7, 8, 9, 10]), ...row(13, [4, 5, 6, 7, 8, 9, 10, 11]), ...row(14, [4, 5, 6, 7, 8, 9, 10, 11])]],
        ["B", [[11, 12], [11, 13]]],
        ["G", [[7, 8], [8, 8]]],
      ],
    }),
  },
  {
    id: "buzz",
    name: "Buzz",
    tagline: "Busy bee, always on task",
    arms: "wings",
    palette: { P: "#facc15", S: "#78350f", W: "#fffbeb", G: "#fb923c", B: "#bae6fd", arm: "#bae6fd", eye: "#3b1d08", shine: SHINE },
    rows: art({
      top: [".....S....S.....", "......S..S......"],
      body: [TORSO, "...SSSSSSSSSS...", TORSO, "...SSSSSSSSSS...", FEET],
      dots: [["G", [[3, 8], [12, 8]]]],
    }),
  },
  {
    id: "zorp",
    name: "Zorp",
    tagline: "Visitor from Planet Python",
    glow: true,
    arms: "nubs",
    palette: { P: "#84cc16", S: "#3f6212", W: "#052e16", G: "#f0abfc", A: "#a3e635", eye: "#bef264", shine: "rgba(190,242,100,0.25)" },
    rows: art({
      top: ["....G......G....", "....S......S...."],
      head: {
        3: ".PPPPPPPPPPPPPP.",
        4: ".PPWWWWWWWWWWPP.",
        5: ".PPWWWWWWWWWWPP.",
        6: ".PPWWWWWWWWWWPP.",
        7: ".PPWWWWWWWWWWPP.",
        8: ".PPWWWWWWWWWWPP.",
        9: ".PPWWWWWWWWWWPP.",
      },
      body: ["....SSSSSSSS....", "....PPPPPPPP....", "....PPPPPPPP....", "....PPPPPPPP....", "....SS....SS...."],
      dots: [["A", [[7, 13], [8, 13]]]],
    }),
  },
  {
    id: "wizzy",
    name: "Wizzy",
    tagline: "Casts spells, compiles dreams",
    arms: "wand",
    palette: { P: "#6366f1", S: "#3730a3", W: "#ffedd5", G: "#fbbf24", A: "#f8fafc", arm: "#92400e", eye: "#1e1b4b", shine: SHINE },
    rows: art({
      top: [".......PP.......", "......PPPP......"],
      crown: ".....GGGGGG.....",
      head: { 3: ".SSSSSSSSSSSSSS.", 10: "..AAAAAAAAAAAA.." },
      body: ["...AAAAAAAAAA...", "....AAAAAAAA....", TORSO, TORSO, FEET],
      dots: [["G", [[7, 14], [8, 14], [7, 13], [8, 0]]]],
    }),
  },
];

export const MASCOT_IDS = MASCOTS.map((m) => m.id);
export const DEFAULT_MASCOT = "codi";
export const getMascot = (id) => MASCOTS.find((m) => m.id === id) || MASCOTS[0];
export const MASCOT_ARMS = ARMS;
