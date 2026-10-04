"""Git - plain-language rewrites of the Beginner lesson texts (questions unchanged). Keyed "<unit>/<lesson>"."""

INTROS = {
    "1/1": """Imagine writing an important essay and saving a copy after each big change: "essay-v1", "essay-v2", "essay-final", "essay-final-REAL". That is a version history - but a messy one.

VERSION CONTROL does this properly and automatically. It records every saved version of your project (each one is called a COMMIT), along with who made it, when, and why. Then you can:
- go back to an older version if something breaks,
- see exactly what changed between two versions,
- let many people work on the same project, and try out ideas on the side without risking the working version.

GIT is the tool almost everyone uses for this. A project that Git watches is called a REPOSITORY, or "repo" for short.

GitHub and GitLab are websites where people keep copies of their repositories online to share them with teammates. (Git is the tool; GitHub is a website that uses it.)

In these lessons you type real Git commands into a safe practice terminal - one command per line. Nothing you do here can break anything.

In this lesson you will learn: what version control is for, and the words repository and commit.""",
    "1/2": """Git watches the files inside your project folder. Anything you change there is a "change" Git can notice. To ask what is going on, type:

git status

In the practice terminal you can create files with echo:

echo "Hello" > notes.txt     # create a file notes.txt containing Hello (replaces anything already there)
echo "more" >> notes.txt     # add another line at the end of it
cat notes.txt                # show what is inside the file
ls                           # list the files in the folder

A brand-new file is called UNTRACKED: Git can see it but is not saving its history yet. A short status shows it like this:

git status --short
?? notes.txt

The two question marks mean "I see this file, but nobody has told me to keep it."

In this lesson you will learn: how to make files and read Git's status.""",
    "1/3": """Saving a version in Git takes two steps, like packing a parcel.

STEP 1 - git add <file>: put the file in the STAGING AREA - the box of things that will go into the next snapshot. "git add ." adds everything at once.

STEP 2 - git commit -m "message": close the box and label it. This saves the snapshot (the commit) with a short message saying what you did.

Here is the whole flow:

git init                        # start a repository
echo "hi" > a.txt               # make a file
git add a.txt                   # put it in the box
git commit -m "Add greeting"    # save the snapshot

Why two steps? Because you may have changed five files but want to save only two of them together as one tidy snapshot. The staging area lets you choose exactly what goes into each commit.

In this lesson you will learn: the two-step way of saving: add, then commit.""",
    "2/1": """Every time you commit, Git adds an entry to the project's history. To read the history, use git log. It lists the commits, newest first.

git log --oneline          # one short line per commit: a short id and the message
git log --format=%s        # just the messages, nothing else
git log -n 2               # only the last 2 commits

Each commit has a unique ID, a long code like 3e63473... You can think of it as the commit's fingerprint: Git uses it to point at that exact snapshot.

The history is like a diary of your project: "Add home page", "Fix typo", "Make header blue". That is why clear commit messages matter - you will read them later.

In this lesson you will learn: how to read the history of a project.""",
    "2/2": """Before you save a snapshot, you often want to check exactly what you changed. git diff shows the differences line by line:
- a line starting with - was REMOVED.
- a line starting with + was ADDED.

git diff               # changes you have made but not staged yet
git diff --staged      # changes in the staging area (what you are about to commit)
git diff --name-only   # just the names of the files that changed

A quick look with git diff before you commit is a very good habit - it catches accidental changes, like a stray debug line you forgot to remove.

Think of it as proof-reading a letter before you post it.

In this lesson you will learn: how to review your changes before saving them.""",
    "2/3": """A project's history is only useful if it is easy to read. Habits of good commits:

- ONE logical change per commit. "Fix login bug" is good; "stuff" is not. If each commit does one thing, you can undo one thing without losing others.
- Write the message as a command: "Add search box", "Fix typo in README". Complete the sentence "This commit will..." and you have the right style.
- Commit OFTEN. Small commits are easier to understand, review, and undo.

A handy shortcut:

git commit -am "message"

The -a means "automatically stage every change to files Git already tracks", then commit. Note: brand-new files still need git add first, because Git isn't tracking them yet.

In this lesson you will learn: how to write a history that you and your teammates can read.""",
    "3/1": """Everyone makes mistakes. Suppose you changed a file and want the last saved version back. git restore throws away your unsaved edits:

git restore notes.txt     # put notes.txt back to how it was in the last commit
git restore .             # do that for every file

A WARNING: this cannot be undone. Those edits were never saved by Git, so after restoring they are gone for good. Be sure before you use it.

(That is another reason to commit often: committed work is always safe and recoverable.)

In this lesson you will learn: how to throw away changes you don't want.""",
    "3/2": """Staged a file by mistake? No problem. You can take it OUT of the staging area, and your changes stay safe in the file:

git restore --staged secrets.txt

The file goes back to being "modified" (or "untracked" if it is brand new). It is simply no longer in the box for the next commit.

This is useful when you used "git add ." but realised one file shouldn't be included. Unstage it, then commit only what you want.

Remember the difference:
- git restore <file>           throws away your EDITS.
- git restore --staged <file>  just unstages - your edits stay.

In this lesson you will learn: how to remove a file from the next commit without losing your work.""",
    "3/3": """What if you already COMMITTED something you wish you hadn't? Use git revert. It creates a NEW commit that does the exact opposite of an old one, cancelling its effect:

git revert HEAD       # undo the latest commit

HEAD is Git's word for "the commit I am on right now".

Why is this the safe way? Because it doesn't erase anything from the history - it ADDS a new entry saying "undone". So it is safe even if you have already shared your work with others; nobody's copy gets confused.

Compare: pretending a mistake never happened (rewriting history, with git reset, which you'll learn later) can cause trouble for teammates. Reverting is honest and simple.

In this lesson you will learn: how to safely undo a commit that is already in your history.""",
    "4/1": """A BRANCH is a separate line of work. Imagine a road with a side road: you can try something new on the side road without disturbing the main road. The main line is usually called main.

Why branches? You can build a new feature (say, dark mode) on its own branch. If it works, add it to main. If it goes wrong, throw the branch away - main is untouched.

git branch dark-mode        # create a branch called dark-mode
git switch dark-mode        # move onto it
git switch -c dark-mode     # create AND move, in one step
git branch                  # list the branches; a * marks the one you are on

Commits you make go onto the CURRENT branch only.

(Older tutorials use "git checkout -b" for the same idea.)

In this lesson you will learn: how to make a side line of work and move between lines.""",
    "4/2": """When your side work is finished, you bring it back into the main line. This is called MERGING. First move to the branch you want to merge INTO, then merge the other one:

git switch main
git merge blog

If main has not changed since you made the blog branch, Git has an easy job: it just slides main forward to include the blog commits, like extending a road. This is called a FAST-FORWARD merge, and it needs no new commit.

Picture it: main was at the place where you branched off. Your branch went further. Fast-forward just moves main's label to the branch's latest point.

In this lesson you will learn: how to merge finished work into main.""",
    "4/3": """After merging, the branch has done its job. Its commits are now safely in main, so you can delete the branch label to keep things tidy:

git branch -d blog        # delete; Git refuses if the branch has work not yet merged (a safety net)
git branch -D blog        # FORCE delete - warning: throws away any unmerged commits!
git branch -m old new     # rename a branch

Deleting a branch does NOT delete the commits that were merged - they live on in main. It only removes the label.

A good habit is to keep branches short-lived: make one for a task, merge it, delete it. A tidy repo is easier for everyone to understand.

In this lesson you will learn: how to clean up branches after merging.""",
}
