// A small, deterministic Git simulator for the Git course - shared by the in-browser runner (git-worker.mjs)
// AND the curriculum validator (scripts/run-examples.mjs), so expected outputs match exactly.
//
// Learners type a script: one shell or git command per line (# starts a comment). Everything happens in memory;
// nothing touches a real disk or network. Supported:
//   shell: echo "text" > file | >> file, cat, ls, touch, rm, mv, pwd
//   git:   init, status [--short], add, commit -m / -am, log [--oneline] [--format=%s|%h %s] [-n N], branch [-d|-D|-m],
//          switch [-c], checkout [-b], merge, restore [--staged], reset [--soft|--mixed|--hard] [HEAD~N], revert HEAD,
//          rm [--cached], mv, diff [--staged|--name-only], tag, stash [push|pop|list|apply|drop], show --name-only,
//          remote add/-v, push [-u], config
// Commit ids are content hashes (parents + message + snapshot), so the same history always gets the same ids.
// Merges are file-level: if both branches changed the same file differently, that file conflicts.

class GitError extends Error {}

const fnv = (str, seed) => {
  let h = seed >>> 0;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 16777619) >>> 0;
  }
  return h;
};
const hashId = (s) => (fnv(s, 2166136261).toString(16).padStart(8, "0") + fnv(s, 33554467).toString(16).padStart(8, "0")).slice(0, 40);

const sortedKeys = (m) => [...m.keys()].sort();
const sameMap = (a, b) => a.size === b.size && [...a].every(([k, v]) => b.get(k) === v);

/** Split a command line into words, honouring "double" and 'single' quotes. Redirections become own tokens. */
export function tokenize(line) {
  const out = [];
  let cur = "";
  let quote = null;
  let started = false;
  for (let i = 0; i < line.length; i++) {
    const c = line[i];
    if (quote) {
      if (c === quote) quote = null;
      else if (c === "\\" && quote === '"' && i + 1 < line.length && '"\\'.includes(line[i + 1])) cur += line[++i];
      else cur += c;
      continue;
    }
    if (c === '"' || c === "'") {
      quote = c;
      started = true;
    } else if (c === " " || c === "\t") {
      if (started) out.push(cur);
      cur = "";
      started = false;
    } else if (c === ">") {
      if (started) out.push(cur);
      const op = line[i + 1] === ">" ? (i++, ">>") : ">";
      out.push({ op });
      cur = "";
      started = false;
    } else {
      cur += c;
      started = true;
    }
  }
  if (quote) throw new GitError(`syntax error: unterminated quote`);
  if (started) out.push(cur);
  return out;
}

export class Repo {
  constructor() {
    this.files = new Map(); // working tree: path -> content
    this.ready = false; // git init done
    this.out = []; // command output
    this.transcript = []; // what the learner sees: "$ command" lines + output
  }

  print(text) {
    this.out.push(text);
    this.transcript.push(text);
  }

  // ---------------------------------------------------------------- refs & commits
  initGit() {
    this.index = new Map();
    this.commits = new Map(); // id -> { id, parents, message, tree }
    this.branches = new Map([["main", null]]);
    this.head = "main"; // current branch name
    this.tags = new Map();
    this.stashes = [];
    this.remotes = new Map();
    this.remoteRefs = new Map(); // "origin/main" -> id
    this.upstream = new Map(); // branch -> "origin/main"
    this.mergeHead = null;
    this.conflicted = new Set(); // paths with merge conflicts that haven't been resolved with git add
    this.seq = 0; // creation order - stands in for commit dates (ids stay pure content hashes)
    this.ready = true;
  }

  need() {
    if (!this.ready) throw new GitError("fatal: not a git repository (or any of the parent directories): .git");
  }

  headId() {
    return this.branches.get(this.head) ?? null;
  }

  tree(id) {
    return id ? this.commits.get(id).tree : new Map();
  }

  short(id) {
    return id.slice(0, 7);
  }

  makeCommit(message, parents) {
    const tree = new Map(this.index);
    const body = JSON.stringify([parents, message, [...tree].sort()]);
    const id = hashId(body);
    if (!this.commits.has(id)) this.commits.set(id, { id, parents, message, tree, seq: ++this.seq });
    this.branches.set(this.head, id);
    return id;
  }

  /** Resolve HEAD, HEAD~N, a branch, a tag, origin/x or a (short) commit id. */
  resolve(ref) {
    let m = /^(.+?)~(\d+)$/.exec(ref);
    if (m) {
      let id = this.resolve(m[1]);
      for (let i = 0; i < Number(m[2]); i++) {
        id = this.commits.get(id).parents[0];
        if (!id) throw new GitError(`fatal: ambiguous argument '${ref}': unknown revision or path not in the working tree.`);
      }
      return id;
    }
    m = /^(.+?)\^$/.exec(ref);
    if (m) return this.resolve(`${m[1]}~1`);
    let id = null;
    if (ref === "HEAD") id = this.headId();
    else if (this.branches.has(ref)) id = this.branches.get(ref);
    else if (this.tags.has(ref)) id = this.tags.get(ref);
    else if (this.remoteRefs.has(ref)) id = this.remoteRefs.get(ref);
    else if (/^[0-9a-f]{4,40}$/.test(ref)) id = [...this.commits.keys()].find((c) => c.startsWith(ref)) ?? null;
    if (!id) throw new GitError(`fatal: ambiguous argument '${ref}': unknown revision or path not in the working tree.`);
    return id;
  }

  ancestors(id) {
    const seen = new Set();
    const stack = id ? [id] : [];
    while (stack.length) {
      const c = stack.pop();
      if (seen.has(c)) continue;
      seen.add(c);
      stack.push(...this.commits.get(c).parents);
    }
    return seen;
  }

  mergeBase(a, b) {
    const ours = this.ancestors(a);
    // breadth-first from b: the first commit also reachable from a
    const queue = [b];
    const seen = new Set();
    while (queue.length) {
      const c = queue.shift();
      if (!c || seen.has(c)) continue;
      seen.add(c);
      if (ours.has(c)) return c;
      queue.push(...this.commits.get(c).parents);
    }
    return null;
  }

  // ---------------------------------------------------------------- status helpers
  /** .gitignore support: plain names, *.ext style globs and dir/ prefixes, one per line (# comments). */
  ignored(path) {
    const rules = (this.files.get(".gitignore") || "").split("\n").map((l) => l.trim()).filter((l) => l && !l.startsWith("#"));
    return rules.some((rule) => {
      if (rule.endsWith("/")) return path.startsWith(rule) || path.includes(`/${rule}`);
      const re = new RegExp(`^${rule.replace(/[.+^${}()|[\]\\]/g, "\\$&").replace(/\*/g, "[^/]*").replace(/\?/g, "[^/]")}$`);
      return re.test(path) || re.test(path.split("/").pop());
    });
  }

  changes() {
    const head = this.tree(this.headId());
    const staged = [];
    const unstaged = [];
    const untracked = [];
    for (const p of new Set([...head.keys(), ...this.index.keys()])) {
      if (this.conflicted.has(p)) continue;
      if (!this.index.has(p)) staged.push(["deleted", p]);
      else if (!head.has(p)) staged.push(["new file", p]);
      else if (head.get(p) !== this.index.get(p)) staged.push(["modified", p]);
    }
    for (const p of this.index.keys()) {
      if (this.conflicted.has(p)) continue;
      if (!this.files.has(p)) unstaged.push(["deleted", p]);
      else if (this.files.get(p) !== this.index.get(p)) unstaged.push(["modified", p]);
    }
    for (const p of this.files.keys()) if (!this.index.has(p) && !this.ignored(p)) untracked.push(p);
    const byPath = (a, b) => (a[1] < b[1] ? -1 : 1);
    return { staged: staged.sort(byPath), unstaged: unstaged.sort(byPath), untracked: untracked.sort() };
  }

  dirtyTracked() {
    const { staged, unstaged } = this.changes();
    return staged.length + unstaged.length + this.conflicted.size > 0;
  }

  /** Make the working tree + index match a commit (used by switch, reset --hard, fast-forward). */
  checkoutTree(id) {
    const target = this.tree(id);
    for (const p of this.index.keys()) if (!target.has(p)) this.files.delete(p);
    for (const [p, c] of target) this.files.set(p, c);
    this.index = new Map(target);
  }

  // ---------------------------------------------------------------- shell
  shell(argv, redirect) {
    const [cmd, ...args] = argv;
    switch (cmd) {
      case "echo": {
        const text = args.join(" ");
        if (!redirect) return this.print(text);
        const { op, file } = redirect;
        if (!file) throw new GitError("syntax error near unexpected token `newline'");
        this.files.set(file, op === ">>" ? (this.files.get(file) ?? "") + text + "\n" : text + "\n");
        return;
      }
      case "cat":
        for (const f of args) {
          if (!this.files.has(f)) throw new GitError(`cat: ${f}: No such file or directory`);
          this.print(this.files.get(f).replace(/\n$/, ""));
        }
        return;
      case "ls":
        if (this.files.size) this.print(sortedKeys(this.files).join("\n"));
        return;
      case "touch":
        for (const f of args) if (!this.files.has(f)) this.files.set(f, "");
        return;
      case "rm":
        for (const f of args.filter((a) => !a.startsWith("-"))) {
          if (!this.files.delete(f)) throw new GitError(`rm: cannot remove '${f}': No such file or directory`);
        }
        return;
      case "mv": {
        const [a, b] = args;
        if (!this.files.has(a)) throw new GitError(`mv: cannot stat '${a}': No such file or directory`);
        this.files.set(b, this.files.get(a));
        this.files.delete(a);
        return;
      }
      case "pwd":
        return this.print("/project");
      case "clear":
      case "mkdir":
      case "cd":
        return;
      default:
        throw new GitError(`sh: ${cmd}: command not found`);
    }
  }

  // ---------------------------------------------------------------- git
  git(args) {
    const [sub, ...rest] = args;
    if (!sub) return this.print("usage: git <command> [<args>]");
    if (sub === "init") {
      if (this.ready) return this.print("Reinitialized existing Git repository in /project/.git/");
      this.initGit();
      return this.print("Initialized empty Git repository in /project/.git/");
    }
    if (sub === "--version" || sub === "version") return this.print("git version 2.47.0 (Codeingo simulator)");
    const fn = {
      status: this.status, add: this.add, commit: this.commit, log: this.log, branch: this.branch, switch: this.switchCmd,
      checkout: this.checkout, merge: this.merge, restore: this.restore, reset: this.reset, revert: this.revert, rm: this.rmCmd,
      mv: this.mvCmd, diff: this.diff, tag: this.tag, stash: this.stash, show: this.show, remote: this.remote, push: this.push,
      config: () => {},
    }[sub];
    if (!fn) throw new GitError(`git: '${sub}' is not a git command. See 'git --help'.`);
    this.need();
    return fn.call(this, rest);
  }

  status(args) {
    const { staged, unstaged, untracked } = this.changes();
    if (args.includes("--short") || args.includes("-s")) {
      const lines = new Map();
      const code = { "new file": "A", modified: "M", deleted: "D" };
      for (const [k, p] of staged) lines.set(p, [code[k], " "]);
      for (const [k, p] of unstaged) lines.set(p, [(lines.get(p) || [" "])[0], code[k]]);
      for (const p of this.conflicted) lines.set(p, ["U", "U"]);
      const rows = [...lines].sort((a, b) => (a[0] < b[0] ? -1 : 1)).map(([p, [x, y]]) => `${x}${y} ${p}`);
      rows.push(...untracked.map((p) => `?? ${p}`));
      if (rows.length) this.print(rows.join("\n"));
      return;
    }
    const lines = [`On branch ${this.head}`];
    const up = this.upstream.get(this.head);
    if (up) {
      const ahead = [...this.ancestors(this.headId())].filter((c) => !this.ancestors(this.remoteRefs.get(up)).has(c)).length;
      lines.push(ahead ? `Your branch is ahead of '${up}' by ${ahead} commit${ahead === 1 ? "" : "s"}.` : `Your branch is up to date with '${up}'.`);
    }
    if (!this.headId()) lines.push("No commits yet");
    if (this.conflicted.size) lines.push("You have unmerged paths.", "Unmerged paths:", ...[...this.conflicted].sort().map((p) => `  both modified:   ${p}`));
    else if (this.mergeHead) lines.push("All conflicts fixed but you are still merging.");
    if (staged.length) lines.push("Changes to be committed:", ...staged.map(([k, p]) => `  ${(k + ":").padEnd(12)}${p}`));
    if (unstaged.length) lines.push("Changes not staged for commit:", ...unstaged.map(([k, p]) => `  ${(k + ":").padEnd(12)}${p}`));
    if (untracked.length) lines.push("Untracked files:", ...untracked.map((p) => `  ${p}`));
    if (!staged.length && !unstaged.length && !untracked.length && !this.conflicted.size) lines.push(this.headId() ? "nothing to commit, working tree clean" : "nothing to commit (create/copy files and use \"git add\" to track)");
    this.print(lines.join("\n"));
  }

  add(args) {
    const paths = args.filter((a) => !a.startsWith("-") || a === "-A");
    if (!paths.length) return this.print("Nothing specified, nothing added.");
    const all = paths.includes(".") || paths.includes("-A") || args.includes("--all");
    const targets = all ? [...new Set([...this.files.keys(), ...this.index.keys()])].filter((p) => this.index.has(p) || !this.ignored(p)) : paths;
    for (const p of targets) {
      if (!all && !this.index.has(p) && this.files.has(p) && this.ignored(p)) {
        throw new GitError(`The following paths are ignored by one of your .gitignore files:\n${p}`);
      }
      if (this.files.has(p)) this.index.set(p, this.files.get(p));
      else if (this.index.has(p)) this.index.delete(p);
      else throw new GitError(`fatal: pathspec '${p}' did not match any files`);
      this.conflicted.delete(p); // adding a file marks its conflict as resolved
    }
  }

  commit(args) {
    let message = null;
    for (let i = 0; i < args.length; i++) if (args[i] === "-m" || args[i] === "-am") message = args[i + 1] ?? "";
    if (message === null) throw new GitError('error: add a message: git commit -m "your message"');
    if (!message.trim()) throw new GitError("Aborting commit due to empty commit message.");
    if (args.includes("-am") || args.includes("-a") || args.includes("--all")) {
      for (const p of [...this.index.keys()].filter((p) => !this.conflicted.has(p))) {
        if (this.files.has(p)) this.index.set(p, this.files.get(p));
        else this.index.delete(p);
      }
    }
    if (this.conflicted.size) {
      throw new GitError("error: Committing is not possible because you have unmerged files.\nfatal: Exiting because of an unresolved conflict.");
    }
    const parent = this.headId();
    if (!this.mergeHead && sameMap(this.index, this.tree(parent))) {
      const { unstaged, untracked } = this.changes();
      return this.print(unstaged.length || untracked.length ? "no changes added to commit (use \"git add\")" : "nothing to commit, working tree clean");
    }
    const parents = parent ? [parent] : [];
    if (this.mergeHead) parents.push(this.mergeHead);
    const id = this.makeCommit(message, parents);
    this.mergeHead = null;
    this.print(`[${this.head}${parent ? "" : " (root-commit)"} ${this.short(id)}] ${message}`);
  }

  log(args) {
    if (!this.headId()) throw new GitError(`fatal: your current branch '${this.head}' does not have any commits yet`);
    let limit = Infinity;
    let format = "full";
    let start = "HEAD";
    for (let i = 0; i < args.length; i++) {
      const a = args[i];
      if (a === "--oneline") format = "%h %s";
      else if (a.startsWith("--format=") || a.startsWith("--pretty=format:")) format = a.replace(/^--(format|pretty=format:)=?/, "");
      else if (a === "-n") limit = Number(args[++i]);
      else if (/^-\d+$/.test(a)) limit = Number(a.slice(1));
      else if (!a.startsWith("-")) start = a;
    }
    // every reachable commit, newest first (git log's default date order)
    const order = [...this.ancestors(this.resolve(start))].sort((a, b) => this.commits.get(b).seq - this.commits.get(a).seq);
    const lines = order.slice(0, limit).map((id) => {
      const c = this.commits.get(id);
      if (format === "full") return `commit ${id}\n\n    ${c.message}\n`;
      return this.formatCommit(id, format);
    });
    this.print(lines.join("\n").replace(/\n$/, ""));
  }

  branch(args) {
    if (!args.length) {
      const names = [...this.branches.keys()].filter((b) => b === this.head || this.branches.get(b)).sort();
      return this.print(names.map((b) => `${b === this.head ? "*" : " "} ${b}`).join("\n"));
    }
    if (args[0] === "-r") return this.print([...this.remoteRefs.keys()].sort().map((r) => `  ${r}`).join("\n"));
    if (args[0] === "-d" || args[0] === "-D") {
      const name = args[1];
      if (!this.branches.has(name)) throw new GitError(`error: branch '${name}' not found.`);
      if (name === this.head) throw new GitError(`error: Cannot delete branch '${name}' checked out at '/project'`);
      const id = this.branches.get(name);
      if (args[0] === "-d" && !this.ancestors(this.headId()).has(id)) {
        throw new GitError(`error: The branch '${name}' is not fully merged.\nIf you are sure you want to delete it, run 'git branch -D ${name}'.`);
      }
      this.branches.delete(name);
      return this.print(`Deleted branch ${name} (was ${this.short(id)}).`);
    }
    if (args[0] === "-m") {
      const [from, to] = args.length === 3 ? [args[1], args[2]] : [this.head, args[1]];
      if (!this.branches.has(from)) throw new GitError(`error: refname refs/heads/${from} not found`);
      this.branches.set(to, this.branches.get(from));
      this.branches.delete(from);
      if (this.head === from) this.head = to;
      return;
    }
    const name = args[0];
    if (!this.headId()) throw new GitError(`fatal: not a valid object name: '${this.head}'`);
    if (this.branches.has(name)) throw new GitError(`fatal: a branch named '${name}' already exists`);
    if (!/^[\w./-]+$/.test(name)) throw new GitError(`fatal: '${name}' is not a valid branch name`);
    this.branches.set(name, args[1] ? this.resolve(args[1]) : this.headId());
  }

  switchTo(name, create) {
    if (create) {
      if (this.branches.has(name)) throw new GitError(`fatal: a branch named '${name}' already exists`);
      this.branches.set(name, this.headId());
      this.head = name;
      return this.print(`Switched to a new branch '${name}'`);
    }
    if (!this.branches.has(name)) throw new GitError(`fatal: invalid reference: ${name}`);
    if (name === this.head) return this.print(`Already on '${name}'`);
    const target = this.branches.get(name);
    if (this.dirtyTracked() && !sameMap(this.tree(target), this.tree(this.headId()))) {
      throw new GitError("error: Your local changes would be overwritten by checkout.\nPlease commit your changes or stash them before you switch branches.");
    }
    if (!this.dirtyTracked()) this.checkoutTree(target);
    this.head = name;
    this.print(`Switched to branch '${name}'`);
  }

  switchCmd(args) {
    if (args[0] === "-c" || args[0] === "--create") return this.switchTo(args[1], true);
    return this.switchTo(args[0], false);
  }

  checkout(args) {
    if (args[0] === "-b") return this.switchTo(args[1], true);
    if (args[0] === "--") return this.restore(args.slice(1));
    if (this.branches.has(args[0])) return this.switchTo(args[0], false);
    if (this.index.has(args[0]) || this.files.has(args[0])) return this.restore(args);
    throw new GitError(`error: pathspec '${args[0]}' did not match any file(s) known to git`);
  }

  merge(args) {
    if (args[0] === "--abort") {
      if (!this.mergeHead) throw new GitError("fatal: There is no merge to abort (MERGE_HEAD missing).");
      this.mergeHead = null;
      this.conflicted.clear();
      this.checkoutTree(this.headId());
      return;
    }
    const name = args.find((a) => !a.startsWith("-"));
    const theirs = this.resolve(name);
    const ours = this.headId();
    if (this.mergeHead) throw new GitError("error: Merging is not possible because you have unmerged files.\nfatal: Exiting because of an unresolved conflict.");
    if (this.dirtyTracked()) throw new GitError("error: Your local changes would be overwritten by merge.\nPlease commit your changes or stash them before you merge.");
    if (this.ancestors(ours).has(theirs)) return this.print("Already up to date.");
    if (!ours || this.ancestors(theirs).has(ours)) {
      if (!args.includes("--no-ff")) {
        this.branches.set(this.head, theirs);
        this.checkoutTree(theirs);
        return this.print(`Updating ${ours ? this.short(ours) : "0000000"}..${this.short(theirs)}\nFast-forward`);
      }
    }
    const base = this.tree(this.mergeBase(ours, theirs));
    const a = this.tree(ours);
    const b = this.tree(theirs);
    const conflicts = [];
    const merged = new Map();
    for (const p of [...new Set([...base.keys(), ...a.keys(), ...b.keys()])].sort()) {
      const [o, x, y] = [base.get(p), a.get(p), b.get(p)];
      let result;
      if (x === y) result = x;
      else if (x === o) result = y;
      else if (y === o) result = x;
      else {
        conflicts.push(p);
        result = `<<<<<<< HEAD\n${x ?? ""}=======\n${y ?? ""}>>>>>>> ${name}\n`;
      }
      if (result !== undefined) merged.set(p, result);
    }
    for (const p of this.index.keys()) if (!merged.has(p)) this.files.delete(p);
    for (const [p, c] of merged) this.files.set(p, c);
    this.index = new Map(merged);
    this.mergeHead = theirs;
    this.conflicted = new Set(conflicts);
    if (conflicts.length) {
      return this.print(
        [...conflicts.map((p) => `Auto-merging ${p}\nCONFLICT (content): Merge conflict in ${p}`), "Automatic merge failed; fix conflicts and then commit the result."].join("\n"),
      );
    }
    const id = this.makeCommit(`Merge branch '${name}'`, [ours, theirs]);
    this.mergeHead = null;
    this.print(`Merge made by the 'ort' strategy.`);
    return id;
  }

  restore(args) {
    const staged = args.includes("--staged") || args.includes("-S");
    const paths = args.filter((a) => !a.startsWith("-"));
    const all = paths.includes(".");
    const head = this.tree(this.headId());
    const targets = all ? [...new Set([...this.index.keys(), ...(staged ? head.keys() : [])])] : paths;
    for (const p of targets) {
      if (staged) {
        if (head.has(p)) this.index.set(p, head.get(p));
        else this.index.delete(p);
      } else {
        if (!this.index.has(p)) throw new GitError(`error: pathspec '${p}' did not match any file(s) known to git`);
        this.files.set(p, this.index.get(p));
      }
    }
  }

  reset(args) {
    const mode = args.find((a) => ["--soft", "--mixed", "--hard"].includes(a)) || "--mixed";
    const refs = args.filter((a) => !a.startsWith("-"));
    if (refs.length && !refs[0].match(/^(HEAD|[\w./-]+)(~\d+|\^)?$/)) throw new GitError(`fatal: ambiguous argument '${refs[0]}'`);
    // "git reset file" = unstage
    if (refs.length && !refs[0].startsWith("HEAD") && (this.index.has(refs[0]) || this.files.has(refs[0])) && !this.branches.has(refs[0])) {
      return this.restore(["--staged", ...refs]);
    }
    const target = this.resolve(refs[0] || "HEAD");
    this.branches.set(this.head, target);
    this.mergeHead = null;
    this.conflicted.clear();
    if (mode === "--hard") {
      this.checkoutTree(target);
      return this.print(`HEAD is now at ${this.short(target)} ${this.commits.get(target).message}`);
    }
    if (mode === "--mixed") this.index = new Map(this.tree(target));
  }

  revert(args) {
    const id = this.resolve(args.find((a) => !a.startsWith("-")) || "HEAD");
    if (this.dirtyTracked()) throw new GitError("error: your local changes would be overwritten by revert.");
    const c = this.commits.get(id);
    const before = this.tree(c.parents[0]);
    for (const p of new Set([...before.keys(), ...c.tree.keys()])) {
      if (before.get(p) === c.tree.get(p)) continue;
      if (before.has(p)) {
        this.index.set(p, before.get(p));
        this.files.set(p, before.get(p));
      } else {
        this.index.delete(p);
        this.files.delete(p);
      }
    }
    const message = `Revert "${c.message}"`;
    const nid = this.makeCommit(message, [this.headId()]);
    this.print(`[${this.head} ${this.short(nid)}] ${message}`);
  }

  rmCmd(args) {
    const cached = args.includes("--cached");
    for (const p of args.filter((a) => !a.startsWith("-"))) {
      if (!this.index.has(p)) throw new GitError(`fatal: pathspec '${p}' did not match any files`);
      this.index.delete(p);
      if (!cached) this.files.delete(p);
      this.print(`rm '${p}'`);
    }
  }

  mvCmd(args) {
    const [a, b] = args;
    if (!this.index.has(a)) throw new GitError(`fatal: not under version control, source=${a}, destination=${b}`);
    this.files.set(b, this.files.get(a));
    this.files.delete(a);
    this.index.set(b, this.index.get(a));
    this.index.delete(a);
  }

  diff(args) {
    const staged = args.includes("--staged") || args.includes("--cached");
    const from = staged ? this.tree(this.headId()) : this.index;
    const to = staged ? this.index : new Map([...this.index.keys()].filter((p) => this.files.has(p)).map((p) => [p, this.files.get(p)]));
    const paths = [...new Set([...from.keys(), ...to.keys()])].filter((p) => from.get(p) !== to.get(p)).sort();
    if (!staged) for (const p of this.index.keys()) if (!this.files.has(p) && !paths.includes(p)) paths.push(p);
    if (args.includes("--name-only")) {
      if (paths.length) this.print(paths.join("\n"));
      return;
    }
    const out = [];
    for (const p of paths) {
      out.push(`--- a/${p}`, `+++ b/${p}`);
      out.push(...lineDiff(from.get(p) ?? "", to.get(p) ?? ""));
    }
    if (out.length) this.print(out.join("\n"));
  }

  tag(args) {
    if (!args.length) {
      if (this.tags.size) this.print(sortedKeys(this.tags).join("\n"));
      return;
    }
    if (args[0] === "-d") {
      this.tags.delete(args[1]);
      return;
    }
    // positional arguments: NAME [COMMIT]  (skipping -a and the value of -m)
    const pos = args.filter((a, i) => !a.startsWith("-") && args[i - 1] !== "-m");
    const [name, at] = pos;
    if (this.tags.has(name)) throw new GitError(`fatal: tag '${name}' already exists`);
    this.tags.set(name, this.resolve(at || "HEAD"));
  }

  stash(args) {
    const sub = args[0] || "push";
    if (sub === "push" || sub === "save") {
      if (!this.dirtyTracked()) return this.print("No local changes to save");
      const head = this.headId();
      const base = this.tree(head);
      // only what differs from the last commit (null = deleted), like a real stash's diff
      const changed = [...new Set([...this.index.keys(), ...base.keys()])].filter((p) => this.files.get(p) !== base.get(p) || this.index.get(p) !== base.get(p));
      this.stashes.unshift({ files: new Map(changed.map((p) => [p, this.files.has(p) ? this.files.get(p) : null])), branch: this.head, base: head });
      this.checkoutTree(head);
      return this.print(`Saved working directory and index state WIP on ${this.head}: ${this.short(head)} ${this.commits.get(head).message}`);
    }
    if (sub === "list") {
      if (this.stashes.length) this.print(this.stashes.map((s, i) => `stash@{${i}}: WIP on ${s.branch}: ${this.short(s.base)} ${this.commits.get(s.base).message}`).join("\n"));
      return;
    }
    if (!this.stashes.length) throw new GitError("No stash entries found.");
    if (sub === "drop") {
      this.stashes.shift();
      return;
    }
    if (sub === "pop" || sub === "apply") {
      const s = this.stashes[0];
      for (const [p, c] of s.files) {
        if (c === null) this.files.delete(p);
        else this.files.set(p, c);
      }
      if (sub === "pop") this.stashes.shift();
      return;
    }
    throw new GitError(`error: unknown subcommand: ${sub}`);
  }

  formatCommit(id, format) {
    const c = this.commits.get(id);
    return format.replace(/%H/g, id).replace(/%h/g, this.short(id)).replace(/%s/g, c.message).replace(/%p/g, c.parents.map((p) => this.short(p)).join(" "));
  }

  /** git show [COMMIT] [--name-only] [--format=...]: the commit line, then the files it changed. */
  show(args) {
    const format = (args.find((a) => a.startsWith("--format=") || a.startsWith("--pretty=format:")) || "--format=%h %s").replace(/^--(format|pretty=format:)=?/, "");
    const id = this.resolve(args.find((a) => !a.startsWith("-")) || "HEAD");
    const c = this.commits.get(id);
    const before = this.tree(c.parents[0]);
    const changed = [...new Set([...before.keys(), ...c.tree.keys()])].filter((p) => before.get(p) !== c.tree.get(p)).sort();
    this.print([this.formatCommit(id, format), ...changed].join("\n"));
  }

  remote(args) {
    if (args[0] === "add") {
      if (this.remotes.has(args[1])) throw new GitError(`error: remote ${args[1]} already exists.`);
      this.remotes.set(args[1], args[2]);
      return;
    }
    if (args[0] === "-v") {
      return this.print([...this.remotes].map(([n, u]) => `${n}\t${u} (fetch)\n${n}\t${u} (push)`).join("\n"));
    }
    if (this.remotes.size) this.print(sortedKeys(this.remotes).join("\n"));
  }

  push(args) {
    const pos = args.filter((a) => !a.startsWith("-"));
    const remote = pos[0] || (this.upstream.get(this.head) || "").split("/")[0];
    const branch = pos[1] || this.head;
    if (!remote || !this.remotes.has(remote)) throw new GitError(`fatal: '${remote || "origin"}' does not appear to be a git repository`);
    if (!this.branches.get(branch)) throw new GitError(`error: src refspec ${branch} does not match any`);
    const ref = `${remote}/${branch}`;
    const before = this.remoteRefs.get(ref);
    const now = this.branches.get(branch);
    if (before && !this.ancestors(now).has(before)) {
      throw new GitError(`! [rejected]        ${branch} -> ${branch} (non-fast-forward)\nerror: failed to push some refs`);
    }
    this.remoteRefs.set(ref, now);
    if (args.includes("-u") || args.includes("--set-upstream")) this.upstream.set(branch, ref);
    const line = before === now ? "Everything up-to-date" : `To ${this.remotes.get(remote)}\n ${before ? `  ${this.short(before)}..${this.short(now)}` : "* [new branch]     "} ${branch} -> ${branch}`;
    this.print(line);
  }

  // ---------------------------------------------------------------- run a script
  run(script, prompt = "$") {
    for (const raw of script.split("\n")) {
      const line = raw.trim();
      if (!line || line.startsWith("#")) continue;
      this.transcript.push(`${prompt} ${line}`);
      for (const part of line.split(/\s*&&\s*/)) {
        const tokens = tokenize(part);
        const r = tokens.findIndex((tk) => typeof tk === "object");
        const argv = (r >= 0 ? tokens.slice(0, r) : tokens).map(String);
        const redirect = r >= 0 ? { op: tokens[r].op, file: tokens[r + 1] } : null;
        if (!argv.length) continue;
        if (argv[0] === "git") this.git(argv.slice(1));
        else this.shell(argv, redirect);
      }
    }
  }
}

function lineDiff(a, b) {
  const x = a.split("\n").filter((l, i, arr) => i < arr.length - 1 || l !== "");
  const y = b.split("\n").filter((l, i, arr) => i < arr.length - 1 || l !== "");
  // longest common subsequence table (files here are tiny)
  const dp = Array.from({ length: x.length + 1 }, () => new Array(y.length + 1).fill(0));
  for (let i = x.length - 1; i >= 0; i--) for (let j = y.length - 1; j >= 0; j--) dp[i][j] = x[i] === y[j] ? dp[i + 1][j + 1] + 1 : Math.max(dp[i + 1][j], dp[i][j + 1]);
  const out = [];
  let i = 0;
  let j = 0;
  while (i < x.length || j < y.length) {
    if (i < x.length && j < y.length && x[i] === y[j]) {
      out.push(` ${x[i]}`);
      i++;
      j++;
    } else if (j < y.length && (i >= x.length || dp[i][j + 1] >= dp[i + 1][j])) out.push(`+${y[j++]}`);
    else out.push(`-${x[i++]}`);
  }
  return out;
}

const text = (lines) => (lines.length ? lines.join("\n") + "\n" : "");

/**
 * Runs one test: optional `setup` (silent - e.g. an existing repository), the learner's script, then the
 * test's `append` check commands. The first error stops the script, like `set -e`.
 * Returns { stdout, stderr, transcript }: when a test has check commands, ONLY their output is graded (stdout),
 * so exploring with extra `git status` calls never breaks a test; `transcript` is the full terminal session.
 */
export function runGitProgram(code, test, setup) {
  const repo = new Repo();
  try {
    if (setup) repo.run(setup);
  } catch (ex) {
    return { stdout: "", stderr: `setup failed: ${ex.message}\n`, transcript: "" };
  }
  repo.out = [];
  repo.transcript = [];
  let stderr = "";
  let graded = null;
  try {
    repo.run(code);
    if (test.append) {
      repo.out = [];
      repo.run(test.append, "$ # check:");
      graded = repo.out;
    }
  } catch (ex) {
    if (!(ex instanceof GitError)) throw ex;
    stderr = ex.message + "\n";
    repo.transcript.push(ex.message);
    if (test.append) graded = graded ?? [];
  }
  return { stdout: text(graded ?? repo.out), stderr, transcript: text(repo.transcript) };
}
