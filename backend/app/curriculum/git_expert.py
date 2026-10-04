"""Git - Expert section, part 1 (units 9-15): commit craft, reading history, undo toolkit, branching strategies,
merging & conflicts, rewriting history, remotes. The in-browser simulator supports the everyday commands
(see frontend/public/runners/git-sim.mjs); lessons about commands it doesn't have (rebase, cherry-pick, bisect,
reflog...) check the command you would type with `code()` patterns instead."""
from .dsl import code, fill, lesson, mcq, order, run, section, t, unit

LOG = "git log --format=%s"
STATUS = "git status --short"

BASE = """git init
echo "v1" > app.txt
git add app.txt
git commit -m "Add app"
"""

TEAM = """git init
echo "line one" > notes.txt
git add notes.txt
git commit -m "Start notes"
git branch feature
"""

EXPERT = section(
    "Expert",
    # ------------------------------------------------------------------ 9
    unit(
        "Unit 9 · Commit craft",
        lesson(
            "Atomic commits",
            """An atomic commit does ONE logical thing and leaves the project working. Why it matters:

- Reviewers understand small commits quickly.
- You can revert or cherry-pick one change without side effects.
- git bisect can pinpoint which change broke something.

Bad: 'WIP', 'misc fixes', one commit mixing a bug fix, a rename and a new feature.
Good: 'Fix crash when the cart is empty', then separately 'Rename Cart.total to Cart.sum'.""",
            mcq("What is an atomic commit?", ["One logical change that leaves the project working", "A commit of one file", "A commit with no message", "Any small commit"], 0),
            mcq("Why are atomic commits easier to revert?", ["They contain only one change", "They are smaller files", "They are signed", "They are older"], 0),
            mcq("Which message best describes ONE change?", ["Fix crash when the cart is empty", "misc fixes", "WIP", "stuff"], 0),
            run("Make two separate commits in a new repo: first create a.txt (content A) and commit it with the message 'Add a', then create b.txt (content B) and commit it with 'Add b'. The log must show both, newest first.", "git",
                [t("history", append=LOG), t("files", append="ls")], ["Add b\nAdd a", "a.txt\nb.txt"],
                'git init\necho "A" > a.txt\ngit add a.txt\ngit commit -m "Add a"\necho "B" > b.txt\ngit add b.txt\ngit commit -m "Add b"',
                require=[r"git\s+commit[\s\S]*git\s+commit"]),
        ),
        lesson(
            "Writing good commit messages",
            """A good message has a short summary line (about 50 characters, imperative mood) and, when needed, a body explaining WHY.

Add password reset email         <- summary: what this commit does, 'Add' not 'Added'

Users could not recover accounts. The email contains a one-time link valid for 30 minutes.   <- body: why

Convention helpers: 'Fix ...', 'Add ...', 'Remove ...', 'Refactor ...'. Many teams use Conventional Commits: feat:, fix:, docs:, chore:. Finish the sentence 'If applied, this commit will ...'.""",
            mcq("Which is imperative mood?", ["Fix login bug", "Fixed login bug", "Fixes login bug", "Fixing login bug"], 0),
            mcq("What should the message BODY explain?", ["Why the change was made", "Every line changed", "Who is to blame", "The file names"], 0),
            mcq("How long should the summary line be?", ["About 50 characters", "A full paragraph", "One word", "Exactly 100"], 0),
            run("Create notes.txt containing hello and commit it with the message: Add notes file (imperative, no period).", "git",
                [t("history", append=LOG)], ["Add notes file"],
                'git init\necho "hello" > notes.txt\ngit add notes.txt\ngit commit -m "Add notes file"', require=[r"Add notes file"]),
        ),
        lesson(
            "Ignoring files",
            """A .gitignore file lists patterns for files Git should never track: build output, dependencies, secrets.

node_modules/
*.log
.env
dist/

Patterns: * matches any name part, a trailing / means a directory, ! un-ignores. Ignored files never show in git status. Files ALREADY tracked stay tracked - remove them with git rm --cached.""",
            mcq("What does a .gitignore entry like *.log do?", ["Hides every .log file from Git", "Deletes log files", "Compresses logs", "Commits logs twice"], 0),
            mcq("A file is already tracked, then you add it to .gitignore. What happens?", ["It stays tracked until git rm --cached", "It is untracked automatically", "It is deleted", "Git errors"], 0),
            mcq("Which should always be ignored?", ["Secrets like .env files", "README.md", "Source code", "Tests"], 0),
            run("Create .gitignore containing *.log and a file debug.log. Also create app.txt. Stage everything with git add . and show the staged files with git status --short; debug.log must NOT appear.", "git",
                [t("status", append=STATUS)], ["A  .gitignore\nA  app.txt"],
                'git init\necho "*.log" > .gitignore\necho "x" > debug.log\necho "code" > app.txt\ngit add .',
                require=[r"\.gitignore"]),
        ),
    ),
    # ------------------------------------------------------------------ 10
    unit(
        "Unit 10 · Reading history",
        lesson(
            "git log in depth",
            """git log has many views:

git log --oneline            # one short line per commit
git log -n 3                 # only the last 3
git log --format=%s          # just the subjects
git log --oneline --graph    # draw the branch shape
git log --author="Ada"       # by person
git log -- file.txt          # commits touching a file

Add --all to include every branch. A good history is something you can READ.""",
            mcq("Which shows only the last 3 commits?", ["git log -n 3", "git log --last 3", "git log 3", "git show 3"], 0),
            mcq("Which draws the branch structure?", ["git log --graph", "git log --tree", "git branch --draw", "git show --graph"], 0),
            mcq("What does git log -- file.txt show?", ["Commits that changed file.txt", "The file's content", "All files", "Untracked files"], 0),
            run("In this repository, show only the 2 most recent commit subjects using git log with --format=%s and a count of 2.", "git",
                [t("two", append="")], ["Add styles\nAdd about page"],
                "git log --format=%s -n 2", setup="git init\necho a > index.html\ngit add .\ngit commit -m \"Add home page\"\necho b > about.html\ngit add .\ngit commit -m \"Add about page\"\necho c > style.css\ngit add .\ngit commit -m \"Add styles\"\n",
                require=[r"-n\s*2|-2"]),
        ),
        lesson(
            "Comparing with git diff",
            """git diff shows what changed:

git diff                 # working tree vs staging area (unstaged changes)
git diff --staged        # staging area vs last commit (what you're about to commit)
git diff --name-only     # only the file names
git diff main..feature   # one branch vs another

Read it before every commit: it is your last chance to catch debug code and secrets.""",
            mcq("Which shows what you are ABOUT to commit?", ["git diff --staged", "git diff", "git log", "git status -v"], 0),
            mcq("What does a plain git diff compare?", ["Working tree vs staging area", "Staging vs last commit", "Two branches", "Two tags"], 0),
            mcq("Which lists only the changed file names?", ["git diff --name-only", "git diff -q", "git ls", "git names"], 0),
            run("Create app.txt and commit it. Change the file to a new line (echo \"v2\" > app.txt) but do NOT stage it. Then show only the changed file names with git diff --name-only.", "git",
                [t("names", append="git diff --name-only")], ["app.txt"],
                'git init\necho "v1" > app.txt\ngit add app.txt\ngit commit -m "Add app"\necho "v2" > app.txt',
                require=[r"echo"]),
        ),
        lesson(
            "Inspecting a single commit",
            """git show <commit> displays one commit: its message and the files it changed.

git show --name-only HEAD       # the last commit and its files
git show HEAD~1                 # the one before it
git show main~3                 # three commits before main

HEAD is where you are now. ~1 means 'one parent back', ~2 'two back'. Commits can also be named by their short hash.""",
            mcq("What does HEAD~2 mean?", ["Two commits before HEAD", "The second branch", "Two files ago", "Two tags"], 0),
            mcq("What is HEAD?", ["Your current position (usually the tip of the current branch)", "The first commit", "The remote", "A tag"], 0),
            mcq("Which shows the changed files of the previous commit?", ["git show --name-only HEAD~1", "git show HEAD+1", "git last", "git files"], 0),
            run("Using the repository below, show the subject of the commit BEFORE the latest one (HEAD~1) with git show and --format=%s --name-only... Keep it simple: print only its subject using git log --format=%s -n 1 HEAD~1.", "git",
                [t("one", append="")], ["Add about page"],
                "git log --format=%s -n 1 HEAD~1", setup="git init\necho a > index.html\ngit add .\ngit commit -m \"Add home page\"\necho b > about.html\ngit add .\ngit commit -m \"Add about page\"\necho c > style.css\ngit add .\ngit commit -m \"Add styles\"\n",
                require=[r"HEAD~1"]),
        ),
    ),
    # ------------------------------------------------------------------ 11
    unit(
        "Unit 11 · The undo toolkit",
        lesson(
            "restore: discard or unstage",
            """git restore has two jobs:

git restore file.txt            # throw away UNSTAGED edits (back to the last staged/committed version)
git restore --staged file.txt   # unstage a file but keep your edits

Discarding is permanent for uncommitted work - there's nothing to get back. Check git status first.""",
            mcq("What does git restore file.txt do to unstaged edits?", ["Discards them", "Stages them", "Commits them", "Stashes them"], 0),
            mcq("Which unstages but keeps the edits?", ["git restore --staged file", "git restore file", "git reset --hard", "git rm file"], 0),
            mcq("Can you recover edits discarded with git restore?", ["No, uncommitted work is gone", "Yes with git undo", "Yes with git log", "Yes from the stash"], 0),
            run("Commit app.txt (v1). Then edit it to v2 and stage it. Unstage it WITHOUT losing the edit, then show git status --short (it should be modified but unstaged) and the file content.", "git",
                [t("status", append=STATUS), t("content", append="cat app.txt")], [" M app.txt", "v2"],
                'git init\necho "v1" > app.txt\ngit add app.txt\ngit commit -m "Add app"\necho "v2" > app.txt\ngit add app.txt\ngit restore --staged app.txt',
                require=[r"restore\s+--staged"]),
        ),
        lesson(
            "reset: soft, mixed and hard",
            """git reset moves the current branch back to an earlier commit. How much it touches depends on the mode:

--soft   moves the branch only; your changes stay STAGED
--mixed  (default) moves the branch and unstages; changes stay in your files
--hard   moves the branch and DISCARDS changes in files too

git reset --soft HEAD~1 is the classic 'undo my last commit but keep the work, ready to recommit'. Never reset commits you've already pushed and shared.""",
            mcq("Which reset keeps your changes staged?", ["--soft", "--mixed", "--hard", "None"], 0),
            mcq("Which reset throws away your file changes?", ["--hard", "--soft", "--mixed", "--keep-all"], 0),
            mcq("When should you avoid git reset?", ["On commits already shared with others", "On local commits", "On staged files", "On new repos"], 0),
            run("A repo has three commits. Undo the LAST commit but keep its changes staged (so you can recommit) with git reset --soft HEAD~1. Then show the log subjects and status.", "git",
                [t("log", append=LOG), t("status", append=STATUS)], ["Add b\nAdd a", "A  c.txt"],
                "git reset --soft HEAD~1", setup='git init\necho A > a.txt\ngit add .\ngit commit -m "Add a"\necho B > b.txt\ngit add .\ngit commit -m "Add b"\necho C > c.txt\ngit add .\ngit commit -m "Add c"\n',
                require=[r"reset\s+--soft"]),
        ),
        lesson(
            "revert: undo safely",
            """git revert creates a NEW commit that reverses an earlier one, leaving history intact. Use it for commits that are already shared:

git revert HEAD          # undo the latest commit with a new commit
git revert abc1234       # undo a specific commit

Reset rewrites history (private work); revert adds to it (public work).""",
            mcq("How is revert different from reset?", ["Revert adds a new undoing commit; reset moves the branch back", "Revert deletes files", "Reset is safer on shared branches", "They are the same"], 0),
            mcq("Which is right for a bug already pushed to the main branch?", ["git revert", "git reset --hard", "git clean", "Delete the repo"], 0),
            mcq("Does revert remove the original commit from history?", ["No", "Yes", "Only with --hard", "Only for merges"], 0),
            run("Create app.txt (v1) and commit; change it to v2 and commit as 'Bad change'. Revert the last commit with git revert HEAD, then show the file content (it must be v1 again).", "git",
                [t("content", append="cat app.txt")], ["v1"],
                'git init\necho "v1" > app.txt\ngit add app.txt\ngit commit -m "Add app"\necho "v2" > app.txt\ngit add app.txt\ngit commit -m "Bad change"\ngit revert HEAD',
                require=[r"git\s+revert"]),
        ),
    ),
    # ------------------------------------------------------------------ 12
    unit(
        "Unit 12 · Stash & working states",
        lesson(
            "Shelving work with stash",
            """git stash puts uncommitted changes on a shelf so you can switch tasks with a clean working tree:

git stash push           # shelve
git stash list           # see the shelf
git stash pop            # bring the latest back (and drop it from the shelf)
git stash apply          # bring it back but keep it on the shelf

Typical use: you're mid-feature and need to fix an urgent bug on another branch.""",
            mcq("What does git stash pop do?", ["Re-applies the latest stash and removes it", "Deletes all stashes", "Commits the stash", "Lists stashes"], 0),
            mcq("When is a stash handy?", ["Switching tasks with unfinished changes", "Sharing code", "Tagging releases", "Reverting merges"], 0),
            mcq("What is the difference between pop and apply?", ["pop removes the stash after applying", "apply removes it", "No difference", "pop is for branches"], 0),
            run("You edited app.txt to 'wip' (uncommitted) but must switch tasks. Stash the change so the working tree is clean; the file must be back to v1.", "git",
                [t("status", append=STATUS), t("content", append="cat app.txt")], ["", "v1"],
                'git stash push', setup=BASE + 'echo "wip" > app.txt\n', require=[r"git\s+stash"]),
        ),
        lesson(
            "Cleaning up: rm and mv",
            """git rm removes a file from the working tree AND the next commit; git rm --cached stops tracking it but keeps your file. git mv renames and stages in one go.

git rm old.txt
git rm --cached secrets.env     # keep the file, stop tracking it
git mv draft.txt final.txt""",
            mcq("What does git rm --cached file do?", ["Stops tracking but keeps the file on disk", "Deletes the file", "Stages the file", "Stashes the file"], 0),
            mcq("What does git mv a b do?", ["Renames a to b and stages the change", "Copies a", "Deletes b", "Commits a"], 0),
            mcq("When do you need git rm --cached?", ["A file was committed by mistake and should be ignored now", "To delete a branch", "To undo a merge", "To rename a branch"], 0),
            run("A repo tracks app.txt and secrets.env (committed by mistake). Stop tracking secrets.env but keep the file, then list files with ls and show git status --short.", "git",
                [t("files", append="ls"), t("status", append=STATUS)], ["app.txt\nsecrets.env", "D  secrets.env\n?? secrets.env"],
                "git rm --cached secrets.env", setup='git init\necho "code" > app.txt\necho "KEY=1" > secrets.env\ngit add .\ngit commit -m "Add everything"\n', require=[r"--cached"]),
        ),
        lesson(
            "Choosing the right undo",
            """Decision guide:

- Edited a file and want it back as committed?  git restore file
- Staged the wrong file?                         git restore --staged file
- Last commit was wrong, not yet pushed?         git reset --soft HEAD~1 (keep work) or --hard (discard)
- Bad commit already shared?                     git revert <commit>
- Need a clean tree for a moment?                git stash

Ask: 'Has anyone else got this commit?' If yes, revert; if no, reset is fine.""",
            mcq("A commit is already on the shared main branch and is wrong. What do you use?", ["git revert", "git reset --hard", "git stash", "git restore"], 0),
            mcq("You staged the wrong file by accident. What do you use?", ["git restore --staged", "git revert", "git reset --hard", "git stash"], 0),
            mcq("You have unfinished edits and must switch branches. What do you use?", ["git stash", "git revert", "git commit --amend", "git rm"], 0),
            run("A repo has app.txt committed as v1. You edit it to oops and want it back exactly as committed. Do it with one command, then show the content.", "git",
                [t("content", append="cat app.txt")], ["v1"],
                "git restore app.txt", setup=BASE + 'echo "oops" > app.txt\n', require=[r"git\s+restore"]),
        ),
    ),
    # ------------------------------------------------------------------ 13
    unit(
        "Unit 13 · Branching strategies",
        lesson(
            "Feature branches",
            """A feature branch isolates one piece of work from main until it's ready:

git switch -c add-search      # create and move to the branch
...commit, commit...
git switch main
git merge add-search          # bring the work in
git branch -d add-search      # tidy up

Good names say what and why: add-search, fix-login-crash. Keep branches short-lived - the longer they live, the harder the merge.""",
            mcq("Why keep feature branches short-lived?", ["Long branches cause painful merges", "Git deletes old branches", "They cost money", "They slow Git"], 0),
            mcq("Which creates and switches to a branch?", ["git switch -c name", "git branch -c name", "git new name", "git checkout name"], 0),
            mcq("Which is the better branch name?", ["fix-login-crash", "stuff", "branch2", "my-branch"], 0),
            run("Create a feature branch called add-search, commit search.txt (content search) on it, switch back to main and merge it. Show the log subjects of main.", "git",
                [t("log", append=LOG), t("files", append="ls")], ["Add search\nAdd app", "app.txt\nsearch.txt"],
                'git switch -c add-search\necho "search" > search.txt\ngit add search.txt\ngit commit -m "Add search"\ngit switch main\ngit merge add-search',
                setup=BASE, require=[r"git\s+(switch\s+-c|checkout\s+-b)", r"git\s+merge"]),
        ),
        lesson(
            "Trunk-based development",
            """In trunk-based development everyone commits small changes to ONE main branch (the trunk) at least daily, using very short branches (hours) and feature flags to hide unfinished work.

+ Few long-lived branches, so fewer painful merges
+ Pairs well with automated tests and continuous integration
- Needs discipline and good tests: main must always work

Teams that deploy many times a day usually work this way.""",
            mcq("What is the trunk?", ["The single main branch everyone integrates into", "A remote server", "A tag", "A stash"], 0),
            mcq("What hides unfinished work in trunk-based development?", ["Feature flags", "Long branches", "Stashes", "Tags"], 0),
            mcq("What must always be true of the trunk?", ["It works", "It is empty", "It is private", "It has no tests"], 0),
            run("Practise a tiny trunk-based change: on main, add a line to app.txt (append v2 with >>) and commit it with the message 'Small change'. Show the log.", "git",
                [t("log", append=LOG), t("content", append="cat app.txt")], ["Small change\nAdd app", "v1\nv2"],
                'echo "v2" >> app.txt\ngit add app.txt\ngit commit -m "Small change"', setup=BASE, require=[r">>"]),
        ),
        lesson(
            "GitFlow and release branches",
            """GitFlow uses several long-lived branches: main (released code), develop (integration), feature/* (work), release/* (stabilising a release) and hotfix/* (urgent fixes to production).

It suits software with scheduled versions and several supported releases (desktop apps, libraries). It is heavier than trunk-based development: more branches, more merges.

Rule: choose the lightest model that fits how you release.""",
            mcq("Which branch holds released code in GitFlow?", ["main", "develop", "feature/*", "release/*"], 0),
            mcq("What is a hotfix branch for?", ["Urgent fixes to production", "Experiments", "New features", "Documentation"], 0),
            mcq("When is GitFlow a good fit?", ["Scheduled releases and several supported versions", "Deploying every hour", "Solo scripts", "Tiny websites"], 0),
            run("Create a develop branch, switch to it and commit feature.txt (content f) there with message 'Add feature'. Then list branches with git branch.", "git",
                [t("branches", append="git branch"), t("log", append=LOG)], ["* develop\n  main", "Add feature\nAdd app"],
                'git switch -c develop\necho "f" > feature.txt\ngit add feature.txt\ngit commit -m "Add feature"', setup=BASE, require=[r"develop"]),
        ),
    ),
    # ------------------------------------------------------------------ 14
    unit(
        "Unit 14 · Merging & conflicts",
        lesson(
            "Fast-forward vs merge commits",
            """If main hasn't moved since you branched, Git can simply slide main forward - a FAST-FORWARD with no new commit. If both branches have new commits, Git creates a MERGE COMMIT with two parents.

git merge feature            # fast-forwards when possible
git merge --no-ff feature    # always create a merge commit (keeps the branch visible in history)

Merge commits record 'this was developed as a unit'; fast-forwards give a straight line.""",
            mcq("When can Git fast-forward?", ["When the target branch has no new commits", "Always", "Only with --no-ff", "Never"], 0),
            mcq("What does --no-ff do?", ["Forces a merge commit", "Disables merging", "Squashes commits", "Deletes the branch"], 0),
            mcq("A merge commit has how many parents?", ["Two", "One", "Zero", "Three"], 0),
            run("Merge the feature branch into main using --no-ff so a merge commit is created. Then show the number of commit lines in git log --format=%s (3 expected: the feature commit, the merge, and the start).", "git",
                [t("count", append=LOG)], ["Merge branch 'feature'\nAdd feature\nStart notes"],
                'git merge --no-ff feature', setup=TEAM + 'git switch feature\necho "x" > feature.txt\ngit add feature.txt\ngit commit -m "Add feature"\ngit switch main\n', require=[r"--no-ff"]),
        ),
        lesson(
            "Resolving a conflict",
            """A conflict happens when both branches changed the same lines. Git stops and asks you to decide:

1. git merge feature      -> CONFLICT in notes.txt
2. Open the file, keep the right content, delete the <<<<<<<, =======, >>>>>>> markers
3. git add notes.txt      -> marks it resolved
4. git commit             -> finishes the merge

git merge --abort backs out if you panic. Conflicts are normal - they just mean two people touched the same spot.""",
            mcq("What does git add do to a conflicted file?", ["Marks it as resolved", "Deletes it", "Reverts it", "Commits it"], 0),
            mcq("How do you cancel a conflicted merge?", ["git merge --abort", "git revert", "git stash", "git restore"], 0),
            mcq("Why do conflicts happen?", ["Two branches changed the same lines", "Git is broken", "Files are too big", "Tags clash"], 0),
            run("The branches below conflict on notes.txt. Merge feature into main, resolve the conflict by writing the final content 'both ideas' into notes.txt, stage it and commit with the message 'Merge feature'. Show the file and the log.", "git",
                [t("content", append="cat notes.txt"), t("log", append=LOG)], ["both ideas", "Merge feature\nChange on main\nChange on feature\nStart notes"],
                'git merge feature\necho "both ideas" > notes.txt\ngit add notes.txt\ngit commit -m "Merge feature"',
                setup=TEAM + 'git switch feature\necho "feature idea" > notes.txt\ngit add notes.txt\ngit commit -m "Change on feature"\ngit switch main\necho "main idea" > notes.txt\ngit add notes.txt\ngit commit -m "Change on main"\n', require=[r"git\s+merge", r"git\s+add", r"git\s+commit"]),
        ),
        lesson(
            "Avoiding painful conflicts",
            """Habits that keep conflicts small:

- Pull and merge main into your branch OFTEN (daily).
- Keep commits and branches small and focused.
- Don't reformat whole files in a feature commit - it touches every line.
- Talk: if two people edit the same file, say so.
- Let formatters and linters run automatically so style never conflicts.

Most conflicts come from long-lived branches and big, mixed commits.""",
            mcq("Which habit reduces conflicts most?", ["Merge main into your branch often", "Wait until the end to merge", "Reformat files in every commit", "Avoid talking"], 0),
            mcq("Why avoid whole-file reformatting in feature commits?", ["It touches every line and invites conflicts", "It is slower", "It is illegal", "Git forbids it"], 0),
            mcq("What is the main cause of big conflicts?", ["Long-lived branches", "Short commits", "Tags", "Stashes"], 0),
            run("Bring main's latest work into your feature branch before continuing: switch to feature and merge main. Show the log subjects.", "git",
                [t("branches", append="git branch"), t("log", append=LOG)], ["* feature\n  main", "Add main work\nStart notes"],
                'git switch feature\ngit merge main', setup=TEAM + 'echo "m" > main.txt\ngit add main.txt\ngit commit -m "Add main work"\n', require=[r"git\s+merge\s+main"]),
        ),
    ),
    # ------------------------------------------------------------------ 15
    unit(
        "Unit 15 · Rewriting history (concepts)",
        lesson(
            "Amending the last commit",
            """git commit --amend replaces the LAST commit with a new one - perfect for fixing a typo in the message or adding a forgotten file:

git add forgotten.txt
git commit --amend            # opens the message editor
git commit --amend -m "Better message"

It creates a new commit (new hash), so only amend commits you haven't shared.""",
            mcq("What does git commit --amend do?", ["Replaces the last commit with an updated one", "Adds a second commit", "Reverts the commit", "Pushes the commit"], 0),
            mcq("When is amend safe?", ["Before the commit is pushed and shared", "Always", "After a release", "Only on tags"], 0),
            mcq("Does an amended commit keep its old hash?", ["No, it gets a new one", "Yes", "Only if the message is unchanged", "Only with --no-edit"], 0),
            code("Write the command that fixes the last commit's message to: Fix typo in README", [r"git\s+commit\s+--amend\s+-m\s+['\"]?Fix typo in README['\"]?"], 'git commit --amend -m "Fix typo in README"',
                 hint="Use --amend together with -m."),
        ),
        lesson(
            "Rebase: a straight history",
            """git rebase replays your branch's commits on top of another branch, making a straight line instead of a merge commit:

git switch feature
git rebase main        # feature now starts from the tip of main

Pros: a clean, linear history. Cons: it REWRITES the branch's commits (new hashes). Golden rule: never rebase commits that others have already pulled.""",
            mcq("What does git rebase main do on a feature branch?", ["Replays your commits on top of main", "Merges main with a merge commit", "Deletes main", "Pushes main"], 0),
            mcq("What is the golden rule of rebasing?", ["Never rebase commits others have already pulled", "Always rebase main", "Rebase once a week", "Rebase only tags"], 0),
            mcq("What does rebasing change?", ["The commits' hashes", "Only the branch name", "The remote URL", "Nothing"], 0),
            code("Write the command to rebase the current branch onto main.", [r"git\s+rebase\s+main"], "git rebase main"),
        ),
        lesson(
            "cherry-pick, reflog & bisect",
            """Three powerful tools to know:

git cherry-pick abc123     # copy ONE commit onto the current branch
git reflog                 # list where HEAD has been - rescues 'lost' commits after a bad reset
git bisect start           # binary-search the history for the commit that introduced a bug
git bisect bad / good      # tell Git whether the current commit is broken

reflog is your safety net: even after reset --hard, the old commits remain reachable for a while.""",
            mcq("What does git cherry-pick abc123 do?", ["Copies that commit onto the current branch", "Deletes it", "Reverts it", "Tags it"], 0),
            mcq("Which command can rescue a commit after a bad reset --hard?", ["git reflog", "git stash", "git clean", "git blame"], 0),
            mcq("What does git bisect find?", ["The commit that introduced a bug", "The largest file", "The newest tag", "The last author"], 0),
            code("Write the command to copy commit 9f3c2a1 onto your current branch.", [r"git\s+cherry-pick\s+9f3c2a1"], "git cherry-pick 9f3c2a1"),
        ),
    ),
)
