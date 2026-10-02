"""Git - version control, practised in a safe in-browser Git simulator (frontend/public/runners/git-sim.mjs).

Learners type real commands, one per line. Each test runs their script and then some check commands
(`append`, e.g. git log --format=%s); only the checks' output is graded, so extra exploring never breaks a
test. `setup` (where given) silently builds a starting repository first.

8 units: Beginner (1-4), Intermediate (5-6), Advanced (7-8). Projects are added to units 4, 6 and 8
(see projects_git.py).
"""
from .dsl import course, fill, lesson, mcq, order, run, section, t, unit

LOG = "git log --format=%s"
STATUS = "git status --short"

# a small repository several exercises start from
SITE = """git init
echo "<h1>Home</h1>" > index.html
echo "body { margin: 0; }" > style.css
git add .
git commit -m "Add home page"
echo "<h1>About</h1>" > about.html
git add about.html
git commit -m "Add about page"
"""

BEGINNER = section(
    "Beginner",
    # ------------------------------------------------------------------ 1
    unit(
        "Unit 1 · Getting started",
        lesson(
            "What is version control?",
            "Version control records every saved version (a COMMIT) of your project, with who changed what and why. You can go back in time, see exactly what changed, and work on features in parallel without breaking the main code.\n\nGit is the version control system almost everyone uses. Each project is a REPOSITORY (repo). GitHub and GitLab are websites that host Git repositories so teams can share them.\n\nIn these lessons you type real Git commands into a safe practice terminal - one command per line.",
            mcq("What is a commit?", ["A copy of Git", "A saved snapshot of your project with a message", "A website", "A branch"], 1),
            mcq("Git vs GitHub?", ["They're the same", "Git is the tool; GitHub hosts Git repositories online", "GitHub is the tool; Git is the website", "Git only works on GitHub"], 1),
            mcq("Which is NOT a reason to use version control?", ["Go back to an older version", "See who changed a line and why", "Make your code run faster", "Work on features in parallel"], 2),
            fill("A Git project is called a ___ (repo).", "a Git ___", "repository"),
            run("Create your first repository: type git init. Then type git status to see what Git thinks.", "git",
                [t("repo exists", append="git status")], ["On branch main\nNo commits yet\nnothing to commit (create/copy files and use \"git add\" to track)"],
                "git init\ngit status", require=[r"git\s+init"], hint="Just two commands, one per line."),
        ),
        lesson(
            "Files & git status",
            "Git watches the files in your project folder (the WORKING TREE). git status tells you what changed.\n\nIn the practice terminal you create files with echo:\n\necho \"Hello\" > notes.txt     # create / overwrite a file\necho \"more\" >> notes.txt     # add a line\ncat notes.txt                # show it\nls                           # list files\n\nA brand-new file is UNTRACKED - Git sees it but isn't saving its history yet. git status --short shows it as ?? notes.txt.",
            mcq("What does ?? mean in git status --short?", ["The file has a conflict", "The file is untracked", "The file was deleted", "The file is staged"], 1),
            mcq("What does echo \"hi\" >> a.txt do?", ["Replaces a.txt with hi", "Adds the line hi to the end of a.txt", "Deletes a.txt", "Prints hi"], 1),
            fill("See what changed in the repository.", "git ___", "status"),
            mcq("Where do you edit your files?", ["In the commit", "In the working tree", "In GitHub only", "In .git"], 1),
            run("Start a repo, then create two files: README.md containing # My project, and todo.txt containing buy milk. (Don't add them yet.)", "git",
                [t("untracked", append=STATUS), t("README", append="cat README.md")], ["?? README.md\n?? todo.txt", "# My project"],
                'git init\necho "# My project" > README.md\necho "buy milk" > todo.txt',
                require=[r"git\s+init"], hint='echo "# My project" > README.md'),
        ),
        lesson(
            "Staging & committing",
            "Saving a version is two steps:\n\n1. git add <file>  - put the change in the STAGING AREA (what goes into the next commit). git add . adds everything.\n2. git commit -m \"message\"  - save the staged snapshot with a message.\n\ngit init\necho \"hi\" > a.txt\ngit add a.txt\ngit commit -m \"Add greeting\"\n\nThe staging area lets you choose exactly what goes into each commit.",
            order("Order the commands to save a new file.", ['echo "hi" > a.txt', "git add a.txt", 'git commit -m "Add a.txt"']),
            mcq("What does git add do?", ["Saves a commit", "Stages changes for the next commit", "Uploads to GitHub", "Creates a file"], 1),
            fill("Commit with a message.", 'git commit ___ "Fix typo"', "-m"),
            mcq("You ran git add a.txt. What does git status --short show for a new file?", ["?? a.txt", "A  a.txt", " M a.txt", "D  a.txt"], 1),
            run("Create a repo with a file hello.txt containing Hello, Git! and commit it with the message: Add hello", "git",
                [t("history", append=LOG), t("clean", append=STATUS + "\ncat hello.txt")], ["Add hello", "Hello, Git!"],
                'git init\necho "Hello, Git!" > hello.txt\ngit add hello.txt\ngit commit -m "Add hello"',
                require=[r"git\s+add", r"git\s+commit"]),
        ),
    ),
    # ------------------------------------------------------------------ 2
    unit(
        "Unit 2 · History & changes",
        lesson(
            "Reading history with git log",
            "git log lists commits, newest first. Useful forms:\n\ngit log --oneline          # short id + message\ngit log --format=%s        # just the messages\ngit log -n 2               # only the last 2\n\nEach commit has an ID (a hash like 3e63473…). Git uses it to refer to that exact snapshot.",
            mcq("In which order does git log list commits?", ["Oldest first", "Newest first", "Alphabetical", "Random"], 1),
            mcq("What does git log --oneline show for each commit?", ["The full diff", "A short id and the message", "Only the author", "The files"], 1),
            fill("Show only the last 3 commits.", "git log -n ___", "3"),
            mcq("What is 3e63473 in '3e63473 Add hello'?", ["A line number", "The commit's (short) id", "A password", "The branch"], 1),
            run("Make three commits in a new repo: create a.txt and commit 'Add a', create b.txt and commit 'Add b', then append a line to a.txt and commit 'Update a'.", "git",
                [t("history", append=LOG), t("last two", append="git log --format=%s -n 2")], ["Update a\nAdd b\nAdd a", "Update a\nAdd b"],
                'git init\necho "a" > a.txt\ngit add a.txt\ngit commit -m "Add a"\necho "b" > b.txt\ngit add b.txt\ngit commit -m "Add b"\necho "more" >> a.txt\ngit add a.txt\ngit commit -m "Update a"',
                require=[r"(git\s+commit[\s\S]*){3}"]),
        ),
        lesson(
            "Seeing changes with git diff",
            "git diff shows what you changed but haven't staged yet, line by line: - removed, + added.\n\ngit diff             # working tree vs staging area\ngit diff --staged    # staging area vs last commit (what you're about to commit)\ngit diff --name-only # just the file names\n\nA quick git diff before committing catches accidental changes.",
            mcq("A line starting with + in a diff was…", ["Removed", "Added", "Renamed", "Unchanged"], 1),
            mcq("You staged your changes. Which shows them?", ["git diff", "git diff --staged", "git log", "git status --short only"], 1),
            fill("List only the changed file names.", "git diff ___", "--name-only"),
            mcq("When does plain git diff show nothing?", ["When no files exist", "When every change is staged (or there are none)", "Always", "When there are commits"], 1),
            run("The repo has index.html, style.css and about.html committed. Change style.css to body { margin: 8px; } and stage it, and change about.html to <h1>About us</h1> WITHOUT staging it.", "git",
                [t("unstaged", append="git diff --name-only"), t("staged", append="git diff --staged --name-only"),
                 t("status", append=STATUS)], ["about.html", "style.css", " M about.html\nM  style.css"],
                'echo "body { margin: 8px; }" > style.css\ngit add style.css\necho "<h1>About us</h1>" > about.html',
                setup=SITE),
        ),
        lesson(
            "Good commits",
            "Good history is easy to read and easy to undo:\n\n- One logical change per commit (\"Fix login bug\", not \"stuff\").\n- Write the message in the imperative: \"Add search box\", \"Fix typo in README\".\n- Commit often - small commits are easier to review and revert.\n\nShortcut: git commit -am \"msg\" stages every change to files Git ALREADY tracks, then commits. New files still need git add.",
            mcq("Which is the best commit message?", ["stuff", "Fixed things", "Fix crash when cart is empty", "asdf"], 2),
            mcq("Does git commit -am include a brand-new, never-added file?", ["Yes", "No - only files Git already tracks"], 1),
            fill("Stage tracked changes and commit in one go.", 'git commit ___ "Update styles"', "-am"),
            mcq("Why prefer small commits?", ["Git is faster", "They're easier to review, understand and undo", "GitHub requires it", "They use less disk"], 1),
            run("Fix the about page (set about.html to <h1>About us</h1>) and add a new contact.html containing <h1>Contact</h1>, as TWO commits: 'Fix about heading' (use commit -am) then 'Add contact page'.", "git",
                [t("history", append=LOG), t("clean", append=STATUS + "\ncat contact.html")],
                ["Add contact page\nFix about heading\nAdd about page\nAdd home page", "<h1>Contact</h1>"],
                'echo "<h1>About us</h1>" > about.html\ngit commit -am "Fix about heading"\necho "<h1>Contact</h1>" > contact.html\ngit add contact.html\ngit commit -m "Add contact page"',
                setup=SITE, require=[r"commit\s+-am"]),
        ),
    ),
    # ------------------------------------------------------------------ 3
    unit(
        "Unit 3 · Undoing things",
        lesson(
            "Discarding changes",
            "Changed a file and want the last saved version back?\n\ngit restore notes.txt     # throw away unstaged changes to notes.txt\ngit restore .             # ...to every file\n\nCareful: discarded changes are gone for good - Git never saved them.",
            mcq("What does git restore file.txt do?", ["Deletes file.txt", "Replaces your unstaged changes with the last staged/committed version", "Commits file.txt", "Unstages file.txt"], 1),
            mcq("Can you get back changes you discarded with git restore?", ["Yes, with git log", "No - they were never saved", "Yes, with git undo", "Only on GitHub"], 1),
            fill("Discard changes to every file.", "git restore ___", "."),
            mcq("Which command shows whether you have changes to discard?", ["git log", "git status", "git init", "git tag"], 1),
            run("Oops - style.css and index.html were edited by mistake. Discard BOTH changes so the working tree is clean again.", "git",
                [t("clean", append=STATUS + "\ncat style.css")], ["body { margin: 0; }"],
                "git restore style.css index.html",
                setup=SITE + 'echo "body { color: red }" > style.css\necho "broken" > index.html\n', require=[r"git\s+(restore|checkout)"]),
        ),
        lesson(
            "Unstaging",
            "Staged something you didn't mean to commit? Unstage it - the change stays in your file:\n\ngit restore --staged secrets.txt\n\nThe file goes back to 'modified' (or 'untracked' if it's new). Then commit just what you want.",
            mcq("After git restore --staged a.txt, your edits to a.txt are…", ["Lost", "Still in the file, just not staged", "Committed", "Pushed"], 1),
            mcq("You ran git add . but one file shouldn't be committed. What now?", ["git restore --staged that-file", "git restore that-file", "git init", "Delete the repo"], 0),
            fill("Unstage a file.", "git restore ___ debug.log", "--staged"),
            mcq("What does a staged-then-unstaged NEW file show in git status --short?", ["A  file", "?? file", " M file", "D  file"], 1),
            run("Someone ran git add . and staged debug.log along with a real change to index.html. Unstage debug.log, then commit only index.html with the message 'Update home heading'.", "git",
                [t("history", append="git log --format=%s -n 1"), t("left over", append=STATUS)], ["Update home heading", "?? debug.log"],
                'git restore --staged debug.log\ngit commit -m "Update home heading"',
                setup=SITE + 'echo "<h1>Welcome</h1>" > index.html\necho "trace" > debug.log\ngit add .\n', require=[r"--staged"]),
        ),
        lesson(
            "Undoing commits: revert",
            "To undo a COMMIT that's already in your history, use git revert. It adds a NEW commit that does the opposite:\n\ngit revert HEAD      # undo the latest commit\n\nHEAD means 'the commit you're on now'. Revert is safe even after you've shared your work, because it doesn't rewrite history - it adds to it. (Rewriting with git reset comes later.)",
            mcq("What does git revert HEAD do?", ["Deletes the last commit", "Adds a new commit that undoes the last one", "Moves to an older commit", "Undoes uncommitted changes"], 1),
            mcq("What is HEAD?", ["The first commit", "The commit you're currently on", "The remote", "The newest file"], 1),
            fill("Undo the latest commit safely.", "git ___ HEAD", "revert"),
            mcq("Why is revert safe for shared history?", ["It hides commits", "It doesn't rewrite existing commits - it adds a new one", "It needs no commit", "It deletes the remote"], 1),
            run("The last commit ('Add about page') was a mistake. Undo it with git revert so about.html is gone, keeping the history.", "git",
                [t("history", append=LOG), t("files", append="ls")],
                ['Revert "Add about page"\nAdd about page\nAdd home page', "index.html\nstyle.css"],
                "git revert HEAD", setup=SITE, require=[r"git\s+revert"]),
        ),
    ),
    # ------------------------------------------------------------------ 4
    unit(
        "Unit 4 · Branches",
        lesson(
            "Creating & switching branches",
            "A BRANCH is a movable label on a line of commits. main is the default. Make a branch to work on something without touching main:\n\ngit branch dark-mode        # create\ngit switch dark-mode        # move onto it\ngit switch -c dark-mode     # both at once\ngit branch                  # list; * marks the current one\n\nCommits you make go on the current branch only. (Older tutorials use git checkout -b - same idea.)",
            mcq("What does git switch -c search do?", ["Deletes search", "Creates the branch search and switches to it", "Merges search", "Lists branches"], 1),
            mcq("In git branch output, * marks…", ["The newest branch", "The branch you're on", "A deleted branch", "The remote"], 1),
            fill("Move onto an existing branch.", "git ___ feature", "switch"),
            mcq("You commit on branch feature. Does main change?", ["Yes", "No - only the current branch moves"], 1),
            run("Create a branch blog, switch to it, and commit a new blog.html (<h1>Blog</h1>) with the message 'Add blog'. Stay on blog.", "git",
                [t("branches", append="git branch"), t("blog history", append=LOG), t("main untouched", append="git log --format=%s main")],
                ["* blog\n  main", "Add blog\nAdd about page\nAdd home page", "Add about page\nAdd home page"],
                'git switch -c blog\necho "<h1>Blog</h1>" > blog.html\ngit add blog.html\ngit commit -m "Add blog"',
                setup=SITE, require=[r"git\s+(switch|checkout|branch)"]),
        ),
        lesson(
            "Merging (fast-forward)",
            "When a branch is finished, MERGE it into main:\n\ngit switch main\ngit merge blog\n\nIf main hasn't moved since you branched, Git just slides main forward to include the branch's commits - a FAST-FORWARD merge. No new commit is needed.",
            order("Order the commands to bring branch blog into main.", ["git switch main", "git merge blog"]),
            mcq("When is a merge a fast-forward?", ["Always", "When main has no new commits since the branch was made", "When there are conflicts", "Never"], 1),
            fill("Merge the branch into the current one.", "git ___ feature", "merge"),
            mcq("Which branch do you need to be ON to merge feature into main?", ["feature", "main", "Either", "None"], 1),
            run("Branch blog has one new commit. Merge it into main (you're on blog right now) and end on main.", "git",
                [t("main history", append=LOG), t("branch", append="git branch")],
                ["Add blog\nAdd about page\nAdd home page", "  blog\n* main"],
                "git switch main\ngit merge blog",
                setup=SITE + 'git switch -c blog\necho "<h1>Blog</h1>" > blog.html\ngit add .\ngit commit -m "Add blog"\n',
                require=[r"git\s+merge\s+blog"]),
        ),
        lesson(
            "Cleaning up branches",
            "After merging, delete the branch - its commits are safe in main:\n\ngit branch -d blog        # refuses if blog has unmerged work\ngit branch -D blog        # force delete (throws away unmerged commits!)\ngit branch -m old new     # rename\n\nShort-lived branches keep the repo tidy.",
            mcq("git branch -d refuses when…", ["The branch is merged", "The branch has commits not merged anywhere", "You're on main", "Always"], 1),
            mcq("What's the risk of git branch -D?", ["None", "It can throw away commits that were never merged", "It deletes main", "It pushes"], 1),
            fill("Rename a branch.", "git branch ___ old-name new-name", "-m"),
            mcq("Can you delete the branch you're currently on?", ["Yes", "No - switch away first"], 1),
            run("Branch blog is merged into main and branch experiment was never merged (abandon it). Delete both, and rename main to trunk. You're on main.", "git",
                [t("branches", append="git branch"), t("history", append=LOG)],
                ["* trunk", "Add blog\nAdd about page\nAdd home page"],
                "git branch -d blog\ngit branch -D experiment\ngit branch -m main trunk",
                setup=SITE + 'git switch -c blog\necho "<h1>Blog</h1>" > blog.html\ngit add .\ngit commit -m "Add blog"\ngit switch main\ngit merge blog\n'
                             'git switch -c experiment\necho "x" > x.txt\ngit add .\ngit commit -m "Try something"\ngit switch main\n',
                require=[r"-D\s+experiment"]),
        ),
    ),
)

INTERMEDIATE = section(
    "Intermediate",
    # ------------------------------------------------------------------ 5
    unit(
        "Unit 5 · Merging for real",
        lesson(
            "Three-way merges",
            "If main ALSO got new commits while you worked on a branch, Git can't fast-forward. It does a THREE-WAY merge using the common ancestor, and records a MERGE COMMIT with two parents:\n\n      A---B  feature\n     /     \\\n----o---C---M  main\n\ngit merge feature   # \"Merge made by the 'ort' strategy.\" - commit M is \"Merge branch 'feature'\"\n\nChanges to different files combine automatically.",
            mcq("Why can't Git fast-forward here?", ["The branch is empty", "Both branches have new commits", "There's a conflict", "main is deleted"], 1),
            mcq("How many parents does a merge commit have?", ["0", "1", "2", "3"], 2),
            fill("The commit both branches started from is the common ___.", "common ___", "ancestor"),
            mcq("main changed style.css; feature changed blog.html. Merging…", ["Conflicts", "Combines both automatically", "Loses one change", "Fails"], 1),
            run("main and blog have both moved on. Merge blog into main (you're on main), then delete blog.", "git",
                [t("history", append=LOG), t("files", append="ls\ngit branch")],
                ["Merge branch 'blog'\nTweak styles\nAdd blog\nAdd about page\nAdd home page", "about.html\nblog.html\nindex.html\nstyle.css\n* main"],
                "git merge blog\ngit branch -d blog",
                setup=SITE + 'git switch -c blog\necho "<h1>Blog</h1>" > blog.html\ngit add .\ngit commit -m "Add blog"\ngit switch main\n'
                             'echo "body { margin: 4px; }" > style.css\ngit commit -am "Tweak styles"\n',
                require=[r"git\s+merge"]),
        ),
        lesson(
            "Merge conflicts",
            "If both branches changed the SAME file differently, Git can't decide and stops with a CONFLICT:\n\nCONFLICT (content): Merge conflict in index.html\n\ngit status --short shows UU index.html, and the file contains both versions between markers:\n\n<<<<<<< HEAD\n<h1>Welcome</h1>        (your branch)\n=======\n<h1>Hello there</h1>    (the branch you're merging)\n>>>>>>> greeting\n\nConflicts are normal - they just need a human decision.",
            mcq("What does UU mean in git status --short?", ["Untracked", "Unmerged - a conflict to resolve", "Up to date", "Uploaded"], 1),
            mcq("Between <<<<<<< HEAD and ======= you see…", ["The other branch's version", "Your current branch's version", "The common ancestor", "Git's suggestion"], 1),
            mcq("When does a merge conflict happen?", ["Every merge", "When both sides changed the same file differently", "When a branch is deleted", "On fast-forwards"], 1),
            fill("Give up on a merge and go back.", "git merge ___", "--abort"),
            run("Branches main and greeting both changed index.html. Merge greeting into main and leave the conflict in place - you'll resolve it in the next lesson. (Look around with git status and cat index.html.)", "git",
                [t("conflict", append=STATUS), t("markers", append="cat index.html")],
                ["UU index.html", "<<<<<<< HEAD\n<h1>Welcome</h1>\n=======\n<h1>Hello there</h1>\n>>>>>>> greeting"],
                "git merge greeting\ngit status\ncat index.html",
                setup=SITE + 'git switch -c greeting\necho "<h1>Hello there</h1>" > index.html\ngit commit -am "Friendlier heading"\ngit switch main\n'
                             'echo "<h1>Welcome</h1>" > index.html\ngit commit -am "New welcome heading"\n',
                require=[r"git\s+merge\s+greeting"]),
        ),
        lesson(
            "Resolving conflicts",
            "To resolve a conflict:\n\n1. Edit the file so it says what it SHOULD say (remove the <<<<<<< ======= >>>>>>> markers).\n2. git add the file - this marks it resolved.\n3. git commit -m \"Merge greeting\" to finish the merge.\n\nIn the practice terminal you rewrite the file with echo:\n\necho \"<h1>Welcome - hello there!</h1>\" > index.html",
            order("Order the steps to finish a conflicted merge.", ["git merge greeting", 'echo "<h1>Hi!</h1>" > index.html', "git add index.html", 'git commit -m "Merge greeting"']),
            mcq("How do you tell Git a conflict is resolved?", ["git resolve", "git add the file", "git push", "Delete the markers only"], 1),
            mcq("Can you commit while a file is still UU?", ["Yes", "No - resolve and add it first"], 1),
            fill("Mark index.html as resolved.", "git ___ index.html", "add"),
            run("Merge greeting into main, resolve the conflict in index.html so it contains exactly <h1>Welcome - hello there!</h1>, and finish with the commit message 'Merge greeting'.", "git",
                [t("merged", append=LOG + "\ncat index.html"), t("clean", append=STATUS + "\ngit branch")],
                ["Merge greeting\nNew welcome heading\nFriendlier heading\nAdd about page\nAdd home page\n<h1>Welcome - hello there!</h1>", "  greeting\n* main"],
                'git merge greeting\necho "<h1>Welcome - hello there!</h1>" > index.html\ngit add index.html\ngit commit -m "Merge greeting"',
                setup=SITE + 'git switch -c greeting\necho "<h1>Hello there</h1>" > index.html\ngit commit -am "Friendlier heading"\ngit switch main\n'
                             'echo "<h1>Welcome</h1>" > index.html\ngit commit -am "New welcome heading"\n',
                require=[r"git\s+add", r"git\s+commit"]),
        ),
    ),
    # ------------------------------------------------------------------ 6
    unit(
        "Unit 6 · Working smarter",
        lesson(
            "Stashing work in progress",
            "Half-way through something and need to switch branches? STASH your changes - they're put aside and your working tree becomes clean:\n\ngit stash          # save and clean up\ngit stash list     # see what's stashed\ngit stash pop      # bring the latest stash back (and remove it from the list)\n\nPerfect for 'quick, fix this bug on main!' moments.",
            mcq("After git stash, your working tree is…", ["Deleted", "Clean - the changes are saved in the stash", "Committed", "Merged"], 1),
            mcq("What does git stash pop do?", ["Deletes the stash", "Re-applies the latest stash and removes it from the list", "Lists stashes", "Pushes"], 1),
            fill("Bring your stashed changes back.", "git stash ___", "pop"),
            mcq("Which is a good time to stash?", ["Before switching branches with unfinished work", "After every commit", "To delete files", "Never"], 0),
            run("You're mid-way through editing style.css when a typo in index.html needs fixing NOW. Stash your work, fix index.html to <h1>Home page</h1> and commit 'Fix home heading', then bring your style.css work back.", "git",
                [t("history", append="git log --format=%s -n 2"), t("work restored", append=STATUS + "\ncat style.css")],
                ["Fix home heading\nAdd about page", " M style.css\nbody { margin: 0; padding: 1rem; }"],
                'git stash\necho "<h1>Home page</h1>" > index.html\ngit commit -am "Fix home heading"\ngit stash pop',
                setup=SITE + 'echo "body { margin: 0; padding: 1rem; }" > style.css\n', require=[r"git\s+stash\b", r"stash\s+pop"]),
        ),
        lesson(
            "Tags & releases",
            "A TAG is a permanent name for one commit - usually a release:\n\ngit tag v1.0          # tag the current commit\ngit tag               # list tags\ngit show v1.0 --name-only\n\nUnlike branches, tags don't move when you make new commits. Version numbers usually follow MAJOR.MINOR.PATCH (semantic versioning).",
            mcq("What's the difference between a tag and a branch?", ["None", "A tag stays on one commit; a branch moves forward with new commits", "Tags are remote only", "Branches can't be deleted"], 1),
            mcq("In v2.4.1, what changed for a bug-fix-only release?", ["MAJOR", "MINOR", "PATCH", "Nothing"], 2),
            fill("Tag the current commit as v1.0.", "git ___ v1.0", "tag"),
            mcq("Which command lists tags?", ["git tag", "git tags --all", "git log --tags", "git branch -t"], 0),
            run("Tag the current commit v1.0. Then add a footer: append <footer>(c) 2026</footer> to index.html, commit it as 'Add footer', and tag that v1.1.", "git",
                [t("tags", append="git tag"), t("v1.0 is older", append="git log --format=%s v1.0"), t("v1.1", append="git log --format=%s -n 1 v1.1")],
                ["v1.0\nv1.1", "Add about page\nAdd home page", "Add footer"],
                'git tag v1.0\necho "<footer>(c) 2026</footer>" >> index.html\ngit commit -am "Add footer"\ngit tag v1.1',
                setup=SITE, require=[r"git\s+tag\s+v1\.0", r"git\s+tag\s+v1\.1"]),
        ),
        lesson(
            "Remotes & pushing",
            "A REMOTE is a copy of the repository somewhere else - usually GitHub. By convention it's called origin:\n\ngit remote add origin https://github.com/you/site.git\ngit push -u origin main     # upload main; -u remembers origin/main as its upstream\ngit push                    # later pushes\n\ngit status then tells you how far ahead of origin/main you are. (In the practice terminal the push is simulated - nothing leaves your browser.)",
            mcq("What is origin, usually?", ["Your first commit", "The name of the main remote (e.g. on GitHub)", "The main branch", "A tag"], 1),
            mcq("What does -u in git push -u origin main do?", ["Undo", "Remember origin/main as the upstream for future push/status", "Update all branches", "Use HTTPS"], 1),
            fill("Upload your commits.", "git ___ origin main", "push"),
            mcq("'Your branch is ahead of origin/main by 2 commits' means…", ["You need to pull", "You have 2 commits not pushed yet", "Origin has 2 newer commits", "There are conflicts"], 1),
            run("Connect the repo to https://github.com/ada/site.git as origin and push main with an upstream. Then commit a change to style.css (body { margin: 2px; }) as 'Tighten margins' WITHOUT pushing it.", "git",
                [t("remote", append="git remote -v"), t("ahead", append="git status")],
                ["origin\thttps://github.com/ada/site.git (fetch)\norigin\thttps://github.com/ada/site.git (push)",
                 "On branch main\nYour branch is ahead of 'origin/main' by 1 commit.\nnothing to commit, working tree clean"],
                'git remote add origin https://github.com/ada/site.git\ngit push -u origin main\necho "body { margin: 2px; }" > style.css\ngit commit -am "Tighten margins"',
                setup=SITE, require=[r"push\s+-u"]),
        ),
    ),
)

ADVANCED = section(
    "Advanced",
    # ------------------------------------------------------------------ 7
    unit(
        "Unit 7 · Rewriting history",
        lesson(
            "git reset",
            "git reset moves the current branch back to an earlier commit. HEAD~1 is 'one commit before HEAD':\n\ngit reset --soft HEAD~1    # undo the commit, keep the changes STAGED\ngit reset HEAD~1           # (--mixed) undo the commit, keep the changes UNSTAGED\ngit reset --hard HEAD~1    # undo the commit AND throw the changes away\n\nReset rewrites history - only do it on commits you haven't pushed/shared. For shared commits use revert.",
            mcq("Which reset keeps your changes staged?", ["--soft", "--mixed", "--hard", "None"], 0),
            mcq("Which reset throws your changes away?", ["--soft", "--mixed", "--hard", "All of them"], 2),
            fill("The commit before HEAD.", "git reset --soft HEAD___1", "~"),
            mcq("You already pushed the commit. Safest way to undo it?", ["git reset --hard", "git revert", "Delete .git", "git branch -D main"], 1),
            run("The last commit 'WIP' should never have been committed - but you want to keep its changes and re-commit them with a better message: 'Add contact page'. Use git reset --soft.", "git",
                [t("history", append=LOG), t("files", append=STATUS + "\nls")], ["Add contact page\nAdd about page\nAdd home page", "about.html\ncontact.html\nindex.html\nstyle.css"],
                'git reset --soft HEAD~1\ngit commit -m "Add contact page"',
                setup=SITE + 'echo "<h1>Contact</h1>" > contact.html\ngit add .\ngit commit -m "WIP"\n', require=[r"reset\s+--soft"]),
        ),
        lesson(
            "Inspecting history",
            "Detective tools:\n\ngit log --oneline -n 5          # the last 5 commits\ngit log --format=\"%h %s\"         # custom format: %h short id, %s subject, %H full id\ngit show HEAD --name-only        # what the latest commit changed (add --format=%s to hide the id)\ngit log --format=%s main         # history of another branch or tag\n\nCommit ids are hashes of the content and history - the same snapshot always gets the same id.",
            mcq("What does %s mean in --format?", ["Short id", "The commit subject (message)", "The author", "The date"], 1),
            mcq("Which shows the files changed by the latest commit?", ["git show HEAD --name-only", "git diff --staged", "git status", "git branch"], 0),
            fill("Show just the last 2 commits.", "git log --oneline -n ___", "2"),
            mcq("HEAD~2 is…", ["Two branches back", "The commit two before HEAD", "A tag", "The second file"], 1),
            run("Explore the history (try git log --oneline and git show HEAD~1 --name-only), then mark the very first commit with the tag first-commit and the current commit with the tag about-page. Hint: git tag NAME COMMIT tags any commit.", "git",
                [t("tags", append="git tag"), t("first", append="git log --format=%s -n 1 first-commit"),
                 t("current", append="git log --format=%s -n 1 about-page")],
                ["about-page\nfirst-commit", "Add home page", "Add about page"],
                "git log --oneline\ngit show HEAD~1 --name-only\ngit tag first-commit HEAD~1\ngit tag about-page", setup=SITE,
                require=[r"git\s+tag\s+first-commit\s+\S+"]),
        ),
        lesson(
            "Revert in shared history",
            "Once commits are pushed, teammates build on them. Rewriting them (reset) makes their copies disagree with yours. So on shared branches you undo with revert - even an older commit:\n\ngit revert HEAD~1     # undo the commit before the latest one\n\nEach revert is its own commit with a clear message, so everyone can see what was undone and why.",
            mcq("Why avoid reset on pushed commits?", ["It's slow", "Teammates' copies would no longer match the rewritten history", "It's not allowed by Git", "It deletes the remote"], 1),
            mcq("What does git revert HEAD~1 undo?", ["The latest commit", "The commit before the latest one", "Two commits", "Nothing"], 1),
            fill("Undo an older commit with a new commit.", "git ___ HEAD~2", "revert"),
            mcq("Is a revert visible in git log?", ["No", "Yes - it's a normal commit"], 1),
            run("The about page commit turned out to be wrong, but a later commit 'Tweak styles' is fine. Revert ONLY the about page commit (it's HEAD~1) and push the result to origin.", "git",
                [t("history", append=LOG), t("files", append="ls\ngit status")],
                ['Revert "Add about page"\nTweak styles\nAdd about page\nAdd home page',
                 "index.html\nstyle.css\nOn branch main\nYour branch is up to date with 'origin/main'.\nnothing to commit, working tree clean"],
                "git revert HEAD~1\ngit push",
                setup=SITE + 'echo "body { margin: 4px; }" > style.css\ngit commit -am "Tweak styles"\n'
                             "git remote add origin https://github.com/ada/site.git\ngit push -u origin main\n",
                require=[r"revert\s+HEAD~1"]),
        ),
    ),
    # ------------------------------------------------------------------ 8
    unit(
        "Unit 8 · Team workflows",
        lesson(
            "Feature branches & pull requests",
            "The everyday team workflow:\n\n1. Update main, then git switch -c feature/search.\n2. Commit in small steps; git push -u origin feature/search.\n3. Open a PULL REQUEST (PR) on GitHub: teammates review, CI runs the tests.\n4. Merge the PR into main, delete the branch.\n\nmain stays deployable at all times; work happens on branches.",
            order("Order the feature-branch workflow.", ["git switch -c feature/search", 'git commit -am "Add search box"', "git push -u origin feature/search", "Open a pull request and get it reviewed", "Merge into main"]),
            mcq("What is a pull request?", ["A git command", "A request on GitHub/GitLab to review and merge a branch", "Downloading a repo", "A conflict"], 1),
            mcq("Why keep main deployable?", ["Git requires it", "Anyone can ship or branch from it at any time", "It's faster", "Branches can't be deployed"], 1),
            fill("Push a new branch and set its upstream.", "git push ___ origin feature/search", "-u"),
            run("Start a feature: create branch feature/search, add search.html (<input type=search>) and commit 'Add search page', then push the branch to origin with an upstream.", "git",
                [t("pushed", append="git branch -r\ngit status"), t("main untouched", append="git log --format=%s -n 1 main")],
                ["  origin/feature/search\n  origin/main\nOn branch feature/search\nYour branch is up to date with 'origin/feature/search'.\nnothing to commit, working tree clean", "Add about page"],
                'git switch -c feature/search\necho "<input type=search>" > search.html\ngit add search.html\ngit commit -m "Add search page"\ngit push -u origin feature/search',
                setup=SITE + "git remote add origin https://github.com/ada/site.git\ngit push -u origin main\n", require=[r"push\s+-u\s+origin\s+feature/search"]),
        ),
        lesson(
            "Rebase & a tidy history",
            "Besides merge, Git can REBASE: replay your branch's commits on top of the latest main, giving a straight line of history instead of a merge commit.\n\ngit switch feature\ngit rebase main\n\nRules of thumb:\n- Rebase your OWN unpushed branch to tidy it up; never rebase commits others already have.\n- Interactive rebase (git rebase -i) can squash, reorder and reword commits.\n\n(The practice terminal doesn't simulate rebase - these questions cover the ideas.)",
            mcq("What does git rebase main do on a feature branch?", ["Deletes main", "Replays the feature's commits on top of main", "Merges with a merge commit", "Pushes to main"], 1),
            mcq("Golden rule of rebasing?", ["Always rebase main", "Don't rebase commits that others already have", "Rebase only tags", "Never use it"], 1),
            mcq("Merge vs rebase: which keeps a straight-line history?", ["Merge", "Rebase", "Both", "Neither"], 1),
            fill("Tidy up your last commits interactively.", "git rebase ___ HEAD~3", "-i"),
            order("Order a typical 'update my branch' with rebase.", ["git switch main", "git pull", "git switch feature", "git rebase main"]),
        ),
        lesson(
            "Keeping secrets out",
            "Never commit passwords, API keys or .env files - once pushed, assume they're leaked (history keeps them even if you delete the file later).\n\nA .gitignore file lists files Git should never track:\n\n.env\nnode_modules/\n*.log\n\nIf you staged a secret by accident, unstage it (git restore --staged .env); if you committed it but haven't pushed, git reset --soft HEAD~1 and fix it; if you pushed it, ROTATE the key immediately.",
            mcq("You pushed an API key. What's most important?", ["Delete the file", "Rotate (replace) the key immediately", "Revert the commit", "Rename the repo"], 1),
            mcq("What does .gitignore do?", ["Deletes files", "Tells Git not to track matching files", "Encrypts files", "Ignores commits"], 1),
            fill("Ignore every .log file in .gitignore.", "___.log", "*"),
            mcq("Deleting a secret file in a new commit removes it from history?", ["Yes", "No - older commits still contain it"], 1),
            run("You accidentally committed .env (with a password) along with app.js in the last commit 'Add app'. It's NOT pushed. Undo the commit keeping the changes, unstage .env, add a .gitignore containing .env, and commit app.js and .gitignore as 'Add app'.", "git",
                [t("history", append=LOG), t("safe", append="git show HEAD --name-only --format=%s\n" + STATUS)],
                ["Add app\nAdd about page\nAdd home page", "Add app\n.gitignore\napp.js"],
                'git reset --soft HEAD~1\ngit restore --staged .env\necho ".env" > .gitignore\ngit add .gitignore\ngit commit -m "Add app"',
                setup=SITE + 'echo "PASSWORD=hunter2" > .env\necho "console.log(1)" > app.js\ngit add .\ngit commit -m "Add app"\n',
                require=[r"reset\s+--soft", r"\.gitignore"]),
        ),
    ),
)

COURSE = course(
    "git", "Git", "🌿", "Version control like a pro: commits, branches, merges and team workflows - in a safe practice terminal.",
    BEGINNER, INTERMEDIATE, ADVANCED,
)
