"""Git - Expert section, part 2 (units 16-21): remotes & collaboration, tags & releases, configuration & automation,
security & hygiene, debugging with Git, capstone workflows. Same simulator rules as git_expert.py."""
from .dsl import code, fill, lesson, mcq, order, run, section, t, unit

LOG = "git log --format=%s"
STATUS = "git status --short"

BASE = """git init
echo "v1" > app.txt
git add app.txt
git commit -m "Add app"
"""

EXPERT2 = section(
    "Expert",
    # ------------------------------------------------------------------ 16
    unit(
        "Unit 16 · Remotes & collaboration",
        lesson(
            "Remotes and pushing",
            """A remote is another copy of the repository, usually on a server (GitHub, GitLab). The default name is origin.

git remote add origin https://example.com/team/app.git
git remote -v                  # list remotes
git push -u origin main        # upload main and remember it as the upstream

After -u, a plain git push and git pull know where to go. A push is rejected if the remote has commits you don't - fetch/pull and integrate first.""",
            mcq("What does git push -u origin main do?", ["Uploads main and sets it as the upstream", "Downloads main", "Deletes main", "Creates a tag"], 0),
            mcq("Why can a push be rejected?", ["The remote has commits you don't have", "The file is too small", "Tags are missing", "Your name is wrong"], 0),
            mcq("What is 'origin'?", ["The default name for the main remote", "The first commit", "A branch", "A tag"], 0),
            run("Add a remote named origin pointing to https://example.com/app.git, then show your remotes with git remote -v.", "git",
                [t("remotes", append="git remote -v")], ["origin\thttps://example.com/app.git (fetch)\norigin\thttps://example.com/app.git (push)"],
                "git remote add origin https://example.com/app.git", setup=BASE, require=[r"remote\s+add\s+origin"]),
        ),
        lesson(
            "Pull requests & forks",
            """On hosting sites you propose changes with a PULL REQUEST (PR, or merge request): push a branch, open a PR, teammates review, and it is merged when approved.

Forking copies someone else's repository to your account so you can propose changes to a project you can't write to: fork -> clone -> branch -> push to your fork -> open a PR to the original.

A good PR is small, has a clear title and description (what and why), links the issue and passes the automated checks.""",
            mcq("What is a pull request?", ["A proposal to merge a branch, with review", "A command that downloads code", "A tag", "A kind of fork"], 0),
            mcq("When do you fork a repository?", ["You can't push to the original", "You want to delete it", "You want to rename it", "Always"], 0),
            mcq("What makes a PR easy to review?", ["It is small and well described", "It changes everything at once", "It has no description", "It skips tests"], 0),
            run("Prepare a pull request branch: create a branch named fix-typo, change app.txt to v1 fixed and commit with the message 'Fix typo'. Show the branch list.", "git",
                [t("branches", append="git branch"), t("log", append=LOG)], ["* fix-typo\n  main", "Fix typo\nAdd app"],
                'git switch -c fix-typo\necho "v1 fixed" > app.txt\ngit add app.txt\ngit commit -m "Fix typo"', setup=BASE, require=[r"fix-typo"]),
        ),
        lesson(
            "Reviewing code kindly and well",
            """Code review catches bugs and spreads knowledge. Habits of good reviewers:

- Review the idea first, then the details.
- Ask questions ('What happens if this is empty?') instead of giving orders.
- Separate must-fix problems from nice-to-have suggestions.
- Praise good work.
- Never review in a rush - or a mood.

As an author: keep PRs small, explain WHY, and don't take comments personally. Everyone's code gets reviewed.""",
            mcq("Which comment is the better review style?", ["What happens if the list is empty?", "This is wrong.", "Rewrite everything.", "Obviously broken."], 0),
            mcq("What should reviewers separate?", ["Must-fix problems from optional suggestions", "Files from folders", "Tests from code", "Authors from names"], 0),
            mcq("How should authors take comments?", ["As help improving the code", "As personal attacks", "As orders to ignore", "As spam"], 0),
            run("Commit a change worth reviewing: add review.txt with the text ready and commit with the message 'Add review checklist'. Show the log.", "git",
                [t("log", append=LOG)], ["Add review checklist\nAdd app"],
                'echo "ready" > review.txt\ngit add review.txt\ngit commit -m "Add review checklist"', setup=BASE, require=[r"Add review checklist"]),
        ),
    ),
    # ------------------------------------------------------------------ 17
    unit(
        "Unit 17 · Tags & releases",
        lesson(
            "Tagging a release",
            """A tag is a permanent name for a commit - ideal for releases.

git tag v1.0.0                       # lightweight tag
git tag -a v1.0.0 -m "First release" # annotated tag (has author, date, message)
git tag                              # list tags
git push origin v1.0.0               # tags are pushed explicitly

Branches move as you commit; tags stay put. Prefer annotated tags for public releases.""",
            mcq("How do tags differ from branches?", ["Tags don't move", "Tags are longer", "Tags hold files", "Tags are remote only"], 0),
            mcq("Which tag type stores author, date and message?", ["Annotated", "Lightweight", "Remote", "Local"], 0),
            mcq("Are tags pushed automatically with git push?", ["No, push them explicitly", "Yes", "Only annotated ones", "Only on main"], 0),
            run("Tag the current commit as v1.0.0 and v1.1.0 is not needed yet - just v1.0.0. Then list the tags.", "git",
                [t("tags", append="git tag")], ["v1.0.0"],
                "git tag v1.0.0", setup=BASE, require=[r"git\s+tag\s+v1\.0\.0"]),
        ),
        lesson(
            "Semantic versioning",
            """Semantic versioning numbers releases MAJOR.MINOR.PATCH:

- PATCH (1.2.3 -> 1.2.4): backwards-compatible bug fixes
- MINOR (1.2.3 -> 1.3.0): new backwards-compatible features
- MAJOR (1.2.3 -> 2.0.0): breaking changes

Reset the lower numbers when a higher one grows. Users can then trust that 1.x upgrades won't break their code.""",
            mcq("Which change needs a MAJOR bump?", ["A breaking API change", "A typo fix", "A new optional feature", "A comment"], 0),
            mcq("What is the next version after 2.4.7 for a bug fix?", ["2.4.8", "2.5.0", "3.0.0", "2.4.7.1"], 0),
            mcq("What is the next version after 2.4.7 for a new compatible feature?", ["2.5.0", "2.4.8", "3.0.0", "2.5.7"], 0),
            run("Create tags for a release history: tag the first commit v1.0.0, then add a feature commit 'Add feature' and tag it v1.1.0. List the tags.", "git",
                [t("tags", append="git tag"), t("log", append=LOG)], ["v1.0.0\nv1.1.0", "Add feature\nAdd app"],
                'git tag v1.0.0\necho "f" > feature.txt\ngit add feature.txt\ngit commit -m "Add feature"\ngit tag v1.1.0', setup=BASE, require=[r"v1\.0\.0", r"v1\.1\.0"]),
        ),
        lesson(
            "Release workflow",
            """A simple release routine:

1. Make sure main is green (tests pass).
2. Update the version number and changelog.
3. Commit: 'Release 1.2.0'.
4. Tag it: git tag -a v1.2.0 -m "Release 1.2.0".
5. Push main and the tag.
6. Publish release notes (what's new, what changed, breaking changes).

Automation (CI/CD) can run steps 1, 4, 5 and 6 whenever you push a tag.""",
            order("Order the release steps.", ["Run the tests on main", "Update version and changelog", 'git commit -m "Release 1.2.0"', "git tag -a v1.2.0 -m \"Release 1.2.0\"", "git push origin main v1.2.0"]),
            mcq("What belongs in a changelog?", ["What's new, fixed and breaking", "Every line of code", "Passwords", "Only commit hashes"], 0),
            mcq("What can CI/CD automate?", ["Testing, tagging and publishing", "Only typing", "Only reviews", "Nothing"], 0),
            run("Do a release: commit a version file (echo \"1.2.0\" > VERSION) with the message 'Release 1.2.0', then tag it v1.2.0. List tags and show the log.", "git",
                [t("tags", append="git tag"), t("log", append=LOG)], ["v1.2.0", "Release 1.2.0\nAdd app"],
                'echo "1.2.0" > VERSION\ngit add VERSION\ngit commit -m "Release 1.2.0"\ngit tag v1.2.0', setup=BASE, require=[r"git\s+tag"]),
        ),
    ),
    # ------------------------------------------------------------------ 18
    unit(
        "Unit 18 · Configuration & automation",
        lesson(
            "git config and aliases",
            """git config sets your identity and preferences. Three levels: --system (all users), --global (you, in ~/.gitconfig) and local (this repository).

git config --global user.name "Ada Lovelace"
git config --global user.email "ada@example.com"
git config --global init.defaultBranch main
git config --global alias.st "status --short"     # now: git st

Set your name and email BEFORE your first commit - they are stored in every commit you make.""",
            mcq("Where does --global config apply?", ["All your repositories", "One repository", "All users", "The remote"], 0),
            mcq("Why set user.name and user.email?", ["Commits record who made them", "To log in", "To speed up Git", "To pay"], 0),
            mcq("What does alias.st 'status --short' create?", ["A shortcut: git st", "A branch", "A tag", "A remote"], 0),
            code("Write the command to set your global name to Ada Lovelace.", [r"git\s+config\s+--global\s+user\.name\s+['\"]?Ada Lovelace['\"]?"], 'git config --global user.name "Ada Lovelace"'),
        ),
        lesson(
            "Hooks: automatic checks",
            """Hooks are scripts Git runs at certain moments, in .git/hooks:

pre-commit    runs before a commit is created (lint, format, run quick tests); non-zero exit cancels
commit-msg    checks the message format (e.g. Conventional Commits)
pre-push      runs before pushing (full tests)

Hooks live in .git and are NOT shared by clone, so teams use tools (like Husky or pre-commit) to install them. Server-side checks (CI) are the real gate - local hooks can be skipped.""",
            mcq("What happens if a pre-commit hook exits with an error?", ["The commit is cancelled", "The commit continues", "The repo is deleted", "A tag is made"], 0),
            mcq("Are hooks copied when someone clones the repo?", ["No", "Yes", "Only pre-commit", "Only on main"], 0),
            mcq("Why is CI still needed if you have hooks?", ["Local hooks can be skipped", "Hooks are slower", "CI is local", "Hooks cost money"], 0),
            fill("Which hook checks the commit message?", "The ___ hook can reject badly formatted messages.", "commit-msg"),
        ),
        lesson(
            "CI and protected branches",
            """Continuous Integration (CI) automatically builds and tests every push and pull request. Combined with PROTECTED BRANCHES it keeps main healthy:

- main can't be pushed to directly
- a pull request needs passing checks and an approving review
- force-pushes and deletions are blocked

This turns 'please don't break main' into a rule the system enforces.""",
            mcq("What does CI do on every push?", ["Builds and runs the tests", "Deletes old branches", "Rewrites history", "Merges automatically"], 0),
            mcq("What does a protected branch block?", ["Direct pushes and force-pushes", "Reading", "Cloning", "Forking"], 0),
            mcq("Why require passing checks before merging?", ["Broken code can't reach main", "It's faster", "It's cheaper", "Git requires it"], 0),
            run("Practise the PR-based flow instead of committing straight to main: create a branch add-ci, commit ci.txt (content on) with the message 'Add CI config', and leave main unchanged. Show the log of main.", "git",
                [t("main log", append="git log --format=%s main"), t("current", append="git branch")], ["Add app", "* add-ci\n  main"],
                'git switch -c add-ci\necho "on" > ci.txt\ngit add ci.txt\ngit commit -m "Add CI config"', setup=BASE, require=[r"add-ci"]),
        ),
    ),
    # ------------------------------------------------------------------ 19
    unit(
        "Unit 19 · Security & hygiene",
        lesson(
            "Never commit secrets",
            """API keys, passwords and tokens must never be committed - history is forever and repositories get shared, forked and leaked.

- Keep secrets in environment variables or a secrets manager
- Add .env and key files to .gitignore from day one
- If you commit one by mistake: REVOKE/rotate the secret immediately (removing the commit isn't enough)

Bots scan public repositories for keys within minutes.""",
            mcq("A key was committed by mistake. What is the FIRST priority?", ["Revoke and replace the key", "Delete the file", "Rename the branch", "Tell nobody"], 0),
            mcq("Where should secrets live?", ["Environment variables or a secrets manager", "In the README", "In commit messages", "In code constants"], 0),
            mcq("Why isn't deleting the commit enough?", ["Copies may already exist elsewhere", "Git refuses", "It is slow", "It deletes the repo"], 0),
            run("A repo has app.txt and a committed .env (KEY=123). Stop tracking .env, ignore it going forward and commit the cleanup with the message 'Stop tracking .env'. Show tracked files by listing git status --short (should be clean) and the log.", "git",
                [t("status", append=STATUS), t("log", append=LOG)], ["", "Stop tracking .env\nAdd app and env"],
                'git rm --cached .env\necho ".env" > .gitignore\ngit add .gitignore\ngit commit -m "Stop tracking .env"',
                setup='git init\necho "code" > app.txt\necho "KEY=123" > .env\ngit add .\ngit commit -m "Add app and env"\n', require=[r"--cached"]),
        ),
        lesson(
            "Removing data from history (concepts)",
            """Deleting a file in a new commit doesn't remove it from OLD commits. To erase something (like a leaked secret or a huge file) from the whole history you must REWRITE history with a tool such as git filter-repo (or BFG), then force-push and ask everyone to re-clone.

git filter-repo --path secrets.env --invert-paths

Consequences: every commit hash changes, open PRs break, collaborators must reset. It's a last resort - prevention is better.""",
            mcq("Does deleting a file in a new commit erase it from history?", ["No, old commits still contain it", "Yes", "Only on main", "Only for text files"], 0),
            mcq("Which tool rewrites history to remove files?", ["git filter-repo", "git stash", "git blame", "git tag"], 0),
            mcq("What must collaborators do after history is rewritten?", ["Re-clone or reset to the new history", "Nothing", "Delete GitHub", "Rebase old work"], 0),
            code("Write the command that removes every trace of secrets.env from history using git filter-repo.", [r"git\s+filter-repo[\s\S]*--path\s+secrets\.env[\s\S]*--invert-paths|git\s+filter-repo[\s\S]*--invert-paths[\s\S]*--path\s+secrets\.env"], "git filter-repo --path secrets.env --invert-paths"),
        ),
        lesson(
            "Signed commits and large files",
            """Signed commits prove who made a commit: Git attaches a cryptographic signature (GPG or SSH key), and hosting sites show a 'Verified' badge. Enable with git config commit.gpgsign true.

Large binary files (videos, datasets, builds) bloat the repository forever. Keep them out of Git, or use Git LFS (Large File Storage), which stores pointers in the repo and the big files elsewhere: git lfs track "*.psd".""",
            mcq("What does a signed commit prove?", ["Who really made it", "That it compiles", "That it's fast", "That it's small"], 0),
            mcq("What does Git LFS store in the repository?", ["Small pointers to large files", "The large files themselves", "Passwords", "Branches"], 0),
            mcq("Why avoid committing big binaries?", ["They bloat the history permanently", "Git can't read them", "They are illegal", "They slow typing"], 0),
            code("Write the command to track all .psd files with Git LFS.", [r"git\s+lfs\s+track\s+['\"]?\*\.psd['\"]?"], 'git lfs track "*.psd"'),
        ),
    ),
    # ------------------------------------------------------------------ 20
    unit(
        "Unit 20 · Debugging with Git",
        lesson(
            "git blame and log -S",
            """Git remembers who changed what and why:

git blame app.py            # who last touched each line, and in which commit
git log -S "calculateTax"   # commits that added or removed that exact text ('pickaxe')
git log -p -- app.py        # history of a file, with the actual changes
git log --follow file.py    # follow a file across renames

'Blame' isn't about fault - it leads you to the commit message that explains why the line exists.""",
            mcq("What does git blame show?", ["The last commit that changed each line", "Who is at fault", "Deleted files", "Branch names"], 0),
            mcq("Which finds commits that added or removed the text calculateTax?", ["git log -S calculateTax", "git blame -S", "git diff -S", "git tag -S"], 0),
            mcq("What does git log --follow do?", ["Tracks a file across renames", "Follows a remote", "Follows a branch", "Follows a tag"], 0),
            code("Write the command that lists the commits that added or removed the text calculateTax.", [r"git\s+log\s+-S\s*['\"]?calculateTax['\"]?"], 'git log -S "calculateTax"'),
        ),
        lesson(
            "Finding a bug with bisect",
            """git bisect binary-searches history for the commit that introduced a bug. You tell Git one good and one bad commit; it checks out the middle; you test and answer good or bad; repeat. For 1,000 commits it needs only about 10 steps.

git bisect start
git bisect bad              # current commit is broken
git bisect good v1.0.0      # this old one worked
...test...
git bisect good             # or: git bisect bad
git bisect reset            # finished: go back

git bisect run ./test.sh automates it with a script.""",
            mcq("How many steps does bisect need for about 1,000 commits?", ["About 10", "About 500", "About 1,000", "About 100"], 0),
            mcq("What do you tell bisect first?", ["One bad and one good commit", "A branch name", "A file name", "A tag message"], 0),
            mcq("What does git bisect reset do?", ["Ends the session and returns to your branch", "Deletes commits", "Marks good", "Reverts"], 0),
            order("Order the bisect session.", ["git bisect start", "git bisect bad", "git bisect good v1.0.0", "test the checked-out commit and answer good/bad", "git bisect reset"]),
        ),
        lesson(
            "Recovering with the reflog",
            """The reflog records every place HEAD has pointed, even after resets and deleted branches:

git reflog
# abc1234 HEAD@{0}: reset: moving to HEAD~2
# def5678 HEAD@{1}: commit: Add search

You 'lost' two commits with reset --hard? Find them in the reflog and bring them back: git reset --hard def5678 (or git branch rescue def5678). Entries expire after a few months, and it only covers YOUR local repository.""",
            mcq("What does the reflog record?", ["Everywhere HEAD has pointed", "Only commits on main", "Remote branches", "File blame"], 0),
            mcq("How do you rescue a commit found in the reflog?", ["Create a branch or reset to its hash", "Delete it", "Tag it as lost", "Clone again"], 0),
            mcq("Is the reflog shared with teammates?", ["No, it is local", "Yes", "Only on main", "Only tags"], 0),
            code("Write the command that creates a branch named rescue pointing at commit def5678.", [r"git\s+branch\s+rescue\s+def5678|git\s+(switch\s+-c|checkout\s+-b)\s+rescue\s+def5678"], "git branch rescue def5678"),
        ),
    ),
    # ------------------------------------------------------------------ 21
    unit(
        "Unit 21 · Capstone workflows",
        lesson(
            "Hotfix workflow",
            """Production is broken and main has unfinished work? The hotfix routine:

1. Branch from the released code: git switch -c hotfix-login main
2. Fix it, test, commit.
3. Merge into main (and into develop if you have one).
4. Tag the patch release: v1.0.1.

Keep the fix small and focused - only the bug, nothing else.""",
            mcq("What should a hotfix contain?", ["Only the bug fix", "New features", "Refactoring", "Experiments"], 0),
            mcq("What version follows 1.0.0 after a hotfix?", ["1.0.1", "1.1.0", "2.0.0", "1.0.0.1"], 0),
            mcq("Where does a hotfix branch start?", ["From the released code (main)", "From develop", "From an old tag only", "From nowhere"], 0),
            run("Perform a hotfix: create branch hotfix-login from main, fix app.txt to v1.0.1 and commit with the message 'Fix login crash', merge it into main and tag v1.0.1. Show the log, tags and file.", "git",
                [t("log", append=LOG), t("tags", append="git tag"), t("file", append="cat app.txt")], ["Fix login crash\nAdd app", "v1.0.1", "v1.0.1"],
                'git switch -c hotfix-login\necho "v1.0.1" > app.txt\ngit add app.txt\ngit commit -m "Fix login crash"\ngit switch main\ngit merge hotfix-login\ngit tag v1.0.1', setup=BASE, require=[r"hotfix-login", r"git\s+tag"]),
        ),
        lesson(
            "Undoing a bad commit on shared main",
            """A bad commit reached main and teammates have pulled it. Don't rewrite history - REVERT it:

git revert HEAD            # new commit that undoes the bad one
git push origin main

Explain in the revert message why. The history stays honest: bad commit, then its undo. Fix the underlying problem on a branch and merge again.""",
            mcq("Why revert instead of reset on shared main?", ["History others rely on stays intact", "Revert is faster", "Reset needs a password", "Revert deletes the bug"], 0),
            mcq("What does git revert HEAD create?", ["A new commit that undoes the last one", "A tag", "A branch", "A stash"], 0),
            mcq("What do you do after reverting?", ["Fix the problem on a branch and merge again", "Delete main", "Force-push", "Ignore it"], 0),
            run("main has three commits; the last, 'Break build', added broken.txt. Undo it safely with a revert, then list files and show the log subject count (the log must still contain the bad commit).", "git",
                [t("files", append="ls"), t("log", append="git log --format=%s -n 2")], ["app.txt", "Revert \"Break build\"\nBreak build"],
                'git revert HEAD', setup=BASE + 'echo "x" > broken.txt\ngit add broken.txt\ngit commit -m "Break build"\n', require=[r"git\s+revert"]),
        ),
        lesson(
            "Team scenario: resolve and ship",
            """A realistic end-to-end flow: you and a teammate edited the same line. Merge your feature, resolve the conflict, test, commit the resolution and tag a release.

git merge feature            # CONFLICT
# edit the file to the agreed content
git add notes.txt
git commit -m "Merge feature"
git tag v0.2.0

Tip: after resolving, run the tests before committing - a merge can compile but behave wrongly.""",
            mcq("What should you do before committing a conflict resolution?", ["Run the tests", "Delete the other branch", "Force-push", "Rename files"], 0),
            mcq("Which command marks a conflicted file resolved?", ["git add file", "git resolve file", "git merge --done", "git fix file"], 0),
            mcq("What follows a successful merge commit when releasing?", ["Tag the release", "Reset --hard", "Delete tags", "Stash"], 0),
            run("Merge the feature branch into main (it conflicts on notes.txt). Resolve by writing 'agreed text', stage it, commit as 'Merge feature' and tag the result v0.2.0. Show the file, log and tags.", "git",
                [t("file", append="cat notes.txt"), t("log", append="git log --format=%s -n 1"), t("tags", append="git tag")], ["agreed text", "Merge feature", "v0.2.0"],
                'git merge feature\necho "agreed text" > notes.txt\ngit add notes.txt\ngit commit -m "Merge feature"\ngit tag v0.2.0',
                setup='git init\necho "line one" > notes.txt\ngit add notes.txt\ngit commit -m "Start notes"\ngit branch feature\ngit switch feature\necho "feature edit" > notes.txt\ngit add notes.txt\ngit commit -m "Edit on feature"\ngit switch main\necho "main edit" > notes.txt\ngit add notes.txt\ngit commit -m "Edit on main"\n', require=[r"git\s+merge", r"git\s+tag"]),
        ),
        lesson(
            "Repository health checklist",
            """A healthy repository has:

- A README explaining what it is, how to run and test it
- A .gitignore suited to the language
- Protected main with required reviews and passing checks
- Small commits with clear messages
- Tags for releases and a changelog
- No secrets, no large binaries
- CONTRIBUTING notes and a license

Take this list to any project you join - and to the one you submit for your own portfolio.""",
            mcq("Which belongs in a healthy repository?", ["A README and a .gitignore", "Passwords", "A 2 GB video", "Only code"], 0),
            mcq("What does a license tell others?", ["How they may use your code", "How to compile it", "Who the authors are", "Nothing"], 0),
            mcq("Which protects the main branch?", ["Required reviews and passing checks", "Deleting tests", "Force-pushes", "Hidden commits"], 0),
            run("Set up a tidy starting repo: create README.md (content # Project), .gitignore (content node_modules/) and commit both in one commit with the message 'Initial commit'. Show the log and files.", "git",
                [t("log", append=LOG), t("files", append="ls")], ["Initial commit", ".gitignore\nREADME.md"],
                'git init\necho "# Project" > README.md\necho "node_modules/" > .gitignore\ngit add README.md .gitignore\ngit commit -m "Initial commit"', require=[r"README\.md", r"\.gitignore"]),
        ),
    ),
)
