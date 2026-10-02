"""C++ projects - one at the end of each section (added to units 8, 12 and 16)."""
from .cpp_adv import STARTER, prog
from .dsl import project, run, t

# ------------------------------------------------------------------ Beginner: tic-tac-toe referee
TTT_INC = "#include <iostream>\n#include <string>\n#include <vector>\n"
READ = '''std::vector<std::string> b(3);
for (auto& row : b) std::cin >> row;
'''
PRINT = '''for (int r = 0; r < 3; r++) {
    std::cout << " " << b[r][0] << " | " << b[r][1] << " | " << b[r][2] << "\\n";
    if (r < 2) std::cout << "---+---+---\\n";
}
'''
WINNER = '''char winner(const std::vector<std::string>& b) {
    const int lines[8][3][2] = {{{0, 0}, {0, 1}, {0, 2}}, {{1, 0}, {1, 1}, {1, 2}}, {{2, 0}, {2, 1}, {2, 2}},
                                {{0, 0}, {1, 0}, {2, 0}}, {{0, 1}, {1, 1}, {2, 1}}, {{0, 2}, {1, 2}, {2, 2}},
                                {{0, 0}, {1, 1}, {2, 2}}, {{0, 2}, {1, 1}, {2, 0}}};
    for (const auto& l : lines) {
        char c = b[l[0][0]][l[0][1]];
        if (c != '.' && c == b[l[1][0]][l[1][1]] && c == b[l[2][0]][l[2][1]]) return c;
    }
    return '.';
}

'''
TTT1 = prog(READ + PRINT, includes=TTT_INC)
TTT2 = prog(READ + PRINT + '''char w = winner(b);
std::cout << (w == '.' ? "No winner yet" : std::string(1, w) + " wins") << "\\n";''', includes=TTT_INC, before=WINNER)
TTT3 = prog(READ + PRINT + '''int x = 0, o = 0;
for (const auto& row : b)
    for (char c : row) {
        if (c == 'X') x++;
        if (c == 'O') o++;
    }
if (o > x || x > o + 1) {
    std::cout << "Invalid board\\n";
    return 0;
}
char w = winner(b);
if (w != '.') std::cout << w << " wins\\n";
else if (x + o == 9) std::cout << "Draw\\n";
else std::cout << (x == o ? 'X' : 'O') << " to move\\n";''', includes=TTT_INC, before=WINNER)

BOARD_X = "XOX\n.XO\nO.X"
BOARD_OPEN = "X..\n.O.\n..."
BOARD_DRAW = "XOX\nXOO\nOXX"
BOARD_BAD = "OO.\n...\n..."

BEGINNER = project(
    "Project: Tic-tac-toe referee",
    "Write the referee for a game of tic-tac-toe:\n\n1. Read and draw the board.\n2. Detect a winner.\n3. Spot draws, "
    "whose turn it is, and impossible boards.\n\nInput: three lines like 'XOX', '.XO', 'O.X' ('.' is an empty square).",
    run("Step 1 - Read the 3 rows into a vector<string> and print the board like:\n X | O | X\n---+---+---\n…", "cpp",
        [t("board", stdin=BOARD_X)], [" X | O | X\n---+---+---\n . | X | O\n---+---+---\n O | . | X"], TTT1, starter=STARTER,
        fallback=[r"vector\s*<\s*(std::)?string\s*>", r"---\+---\+---"]),
    run("Step 2 - Write char winner(board) checking all 8 lines; after the board print 'X wins', 'O wins' or 'No winner yet'.",
        "cpp", [t("x wins", stdin=BOARD_X), t("open", stdin=BOARD_OPEN)],
        [" X | O | X\n---+---+---\n . | X | O\n---+---+---\n O | . | X\nX wins",
         " X | . | .\n---+---+---\n . | O | .\n---+---+---\n . | . | .\nNo winner yet"],
        TTT2, starter=TTT1, carry=True, fallback=[r"char\s+winner\s*\(", r"wins"]),
    run("Step 3 - Instead of 'No winner yet', print 'Draw' for a full board, else 'X to move' / 'O to move' (X starts). "
        "Print only 'Invalid board' (after the drawing) if the counts are impossible.", "cpp",
        [t("x wins", stdin=BOARD_X), t("to move", stdin=BOARD_OPEN), t("draw", stdin=BOARD_DRAW), t("invalid", stdin=BOARD_BAD)],
        [" X | O | X\n---+---+---\n . | X | O\n---+---+---\n O | . | X\nX wins",
         " X | . | .\n---+---+---\n . | O | .\n---+---+---\n . | . | .\nX to move",
         " X | O | X\n---+---+---\n X | O | O\n---+---+---\n O | X | X\nDraw",
         " O | O | .\n---+---+---\n . | . | .\n---+---+---\n . | . | .\nInvalid board"],
        TTT3, starter=TTT2, carry=True, fallback=[r"Invalid board", r"Draw", r"to move"]),
)

# ------------------------------------------------------------------ Intermediate: word statistics
WS_INC = "#include <algorithm>\n#include <cctype>\n#include <iostream>\n#include <map>\n#include <string>\n#include <vector>\n"
CLEAN = '''std::string clean(const std::string& raw) {
    std::string w;
    for (char c : raw)
        if (std::isalpha(static_cast<unsigned char>(c))) w += static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
    return w;
}

'''
COUNT = '''std::map<std::string, int> counts;
std::string raw;
while (std::cin >> raw) {
    std::string w = clean(raw);
    if (!w.empty()) counts[w]++;
}
std::cout << "Words: " << counts.size() << " distinct\\n";
'''
TOP3 = '''std::vector<std::pair<std::string, int>> v(counts.begin(), counts.end());
std::sort(v.begin(), v.end(), [](const auto& a, const auto& b) {
    if (a.second != b.second) return a.second > b.second;
    return a.first < b.first;
});
for (std::size_t i = 0; i < v.size() && i < 3; i++) std::cout << v[i].first << " " << v[i].second << "\\n";
'''
WS1 = prog(COUNT, includes=WS_INC, before=CLEAN)
WS2 = prog(COUNT + TOP3, includes=WS_INC, before=CLEAN)
WS3 = prog(COUNT + TOP3 + '''std::string longest;
int letters = 0, total = 0;
for (const auto& [word, n] : counts) {
    if (word.size() > longest.size()) longest = word;
    letters += static_cast<int>(word.size()) * n;
    total += n;
}
std::cout << "Longest: " << longest << "\\n";
std::cout << std::fixed << std::setprecision(2) << "Average length: " << (total ? static_cast<double>(letters) / total : 0.0) << "\\n";''',
           includes=WS_INC + "#include <iomanip>\n", before=CLEAN)

TEXT = "The cat and the hat. The CAT sat! A hat, a mat."

INTERMEDIATE = project(
    "Project: Word statistics",
    "Analyse text like a search engine would:\n\n1. Count words (case-insensitive, punctuation stripped) in a map.\n2. "
    "Find the 3 most common words.\n3. Report the longest word and the average word length.",
    run("Step 1 - Read words until the input ends, keep only letters, lower-case them, count them in a std::map, then "
        "print 'Words: N distinct'.", "cpp", [t("text", stdin=TEXT)], ["Words: 7 distinct"], WS1, starter=STARTER,
        fallback=[r"map\s*<\s*(std::)?string\s*,\s*int\s*>", r"tolower"]),
    run("Step 2 - Then print the 3 most common words as 'word count' (most frequent first, ties alphabetically) - copy "
        "the map into a vector of pairs and sort it with a lambda.", "cpp",
        [t("text", stdin=TEXT)], ["Words: 7 distinct\nthe 3\na 2\ncat 2"], WS2, starter=WS1, carry=True,
        fallback=[r"sort\s*\(", r"\[\s*\]\s*\("]),
    run("Step 3 - Finally print 'Longest: word' (first alphabetically if tied) and 'Average length: X.XX' over all words "
        "(counting repeats).", "cpp",
        [t("text", stdin=TEXT), t("one word", stdin="Hello!")],
        ["Words: 7 distinct\nthe 3\na 2\ncat 2\nLongest: and\nAverage length: 2.67",
         "Words: 1 distinct\nhello 1\nLongest: hello\nAverage length: 5.00"],
        WS3, starter=WS2, carry=True, fallback=[r"Longest", r"setprecision"]),
)

# ------------------------------------------------------------------ Advanced: route planner
RP_INC = "#include <iostream>\n#include <queue>\n#include <vector>\n"
GRAPH = '''int n, m;
std::cin >> n >> m;
std::vector<std::vector<std::pair<int, int>>> adj(n);
for (int i = 0; i < m; i++) {
    int u, v, w;
    std::cin >> u >> v >> w;
    adj[u].push_back({v, w});
    adj[v].push_back({u, w});
}
'''
DIJKSTRA = '''const long long INF = 1e18;
std::vector<long long> dist(n, INF);
std::vector<int> prev(n, -1);
std::priority_queue<std::pair<long long, int>, std::vector<std::pair<long long, int>>, std::greater<>> pq;
dist[0] = 0;
pq.push({0, 0});
while (!pq.empty()) {
    auto [d, u] = pq.top();
    pq.pop();
    if (d > dist[u]) continue;
    for (auto [v, w] : adj[u]) {
        if (dist[u] + w < dist[v]) {
            dist[v] = dist[u] + w;
            prev[v] = u;
            pq.push({dist[v], v});
        }
    }
}
for (int i = 0; i < n; i++) std::cout << (i ? " " : "") << (dist[i] == INF ? -1 : dist[i]);
std::cout << "\\n";
'''
RP1 = prog(GRAPH + '''for (int i = 0; i < n; i++) std::cout << "Stop " << i << ": " << adj[i].size() << " roads\\n";''', includes=RP_INC)
RP2 = prog(GRAPH + DIJKSTRA, includes=RP_INC)
RP3 = prog(GRAPH + DIJKSTRA + '''int target;
std::cin >> target;
if (dist[target] == INF) {
    std::cout << "No route\\n";
} else {
    std::vector<int> path;
    for (int v = target; v != -1; v = prev[v]) path.push_back(v);
    for (std::size_t i = path.size(); i-- > 0;) std::cout << path[i] << (i ? " -> " : "\\n");
}''', includes=RP_INC + "#include <algorithm>\n")

MAP_IN = "5 6\n0 1 4\n0 2 1\n2 1 2\n1 3 5\n2 3 8\n3 4 3"

ADVANCED = project(
    "Project: Route planner",
    "Build the core of a maps app:\n\n1. Load a road network as a weighted graph.\n2. Compute the shortest distance "
    "from stop 0 to every stop (Dijkstra).\n3. Rebuild the actual route to a destination.\n\nInput: n m, then m roads "
    "'u v length' (two-way).",
    run("Step 1 - Build an adjacency list of (neighbour, length) pairs and print 'Stop i: K roads' for every stop.", "cpp",
        [t("map", stdin=MAP_IN)], ["Stop 0: 2 roads\nStop 1: 3 roads\nStop 2: 3 roads\nStop 3: 3 roads\nStop 4: 1 roads"],
        RP1, starter=STARTER, fallback=[r"vector\s*<\s*(std::)?vector\s*<\s*(std::)?pair", r"push_back"]),
    run("Step 2 - Replace the degree lines with Dijkstra's algorithm (priority_queue): print the shortest distance from "
        "stop 0 to every stop on one line, -1 if unreachable.", "cpp",
        [t("map", stdin=MAP_IN), t("unreachable", stdin="3 1\n0 1 7")], ["0 3 1 8 11", "0 7 -1"],
        RP2, starter=RP1, carry=True, fallback=[r"priority_queue", r"greater"]),
    run("Step 3 - Track each stop's previous stop. After the distances, read a target and print the route like "
        "'0 -> 2 -> 1 -> 3', or 'No route'.", "cpp",
        [t("route", stdin=MAP_IN + "\n4"), t("no route", stdin="3 1\n0 1 7\n2")],
        ["0 3 1 8 11\n0 -> 2 -> 1 -> 3 -> 4", "0 7 -1\nNo route"], RP3, starter=RP2, carry=True,
        fallback=[r"prev\w*\s*\[", r"->", r"No route"]),
)

PROJECTS = {8: BEGINNER, 12: INTERMEDIATE, 16: ADVANCED}
