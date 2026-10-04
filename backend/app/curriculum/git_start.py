"""Git - gentle 'Start here' unit for people who have never used version control."""
from .dsl import fill, lesson, mcq, order, run, start_unit, t

STATUS = "git status --short"
LOG = "git log --format=%s"

START = [
    start_unit(
        1,
        "Start here · Saving your work's history",
        lesson(
            "Why do we need Git?",
            """Have you ever saved files called "essay.docx", "essay-final.docx", "essay-final-REAL.docx"? That is a messy way of keeping old versions!

Games solve this with SAVE POINTS: you can always go back to a moment where things were good.

GIT does the same for any project (code, writing, designs). It lets you:
- save a snapshot of your work whenever you like,
- see what changed and when,
- go back if something breaks,
- let many people work on the same project without overwriting each other.

Your project folder watched by Git is called a REPOSITORY (or "repo"). Each saved snapshot is called a COMMIT, and it comes with a short message describing it ("Add the home page").

GitHub is a website where people store their Git repositories online so they can share them. Git is the tool; GitHub is the website.

In this lesson you will learn: what Git is for, and two words: repository and commit.""",
            mcq("What does Git help with?", ["Saving the history of your work", "Editing photos", "Playing games", "Sending emails"], 0, "Git records versions of your project."),
            mcq("What is a commit?", ["A saved snapshot with a message", "A website", "A kind of file", "A person"], 0, "A commit is one saved version."),
            mcq("What is a repository?", ["A project folder tracked by Git", "A kind of virus", "A phone app", "A password"], 0, "A repo is a project Git keeps history for."),
            mcq("What is GitHub?", ["A website that stores Git repositories online", "The same thing as Git", "A text editor", "A computer"], 0, "Git is the tool; GitHub hosts repos online."),
        ),
        lesson(
            "Starting a repository",
            """You tell Git to start watching a folder with ONE command:

git init

"init" is short for "initialise" - get ready. You type commands into a TERMINAL, a place where you give the computer written instructions. In this course there is a safe practice terminal: nothing you do here can break anything.

After git init the folder is a repository. Git keeps its secret notes in a hidden folder called .git (you won't need to open it).

To check what is going on, ask for the STATUS:

git status

Git replies with the current state: which branch you are on and whether there is anything to save. A BRANCH is a line of saved history; the main one is usually called main.

In this lesson you will learn: how to start a repository and ask Git what is happening.""",
            mcq("What does git init do?", ["Starts a repository in the folder", "Saves a commit", "Deletes the folder", "Opens GitHub"], 0, "init sets up Git in your folder."),
            mcq("What does git status do?", ["Shows what is going on in the repository", "Saves your work", "Starts a repository", "Sends it online"], 0, "status is how you check on Git."),
            fill("Start a repository.", "git ___", "init", "init gets Git ready."),
            run("Start a repository, then check its status.", "git", [t("repo exists", append="git status")],
                ["On branch main\nNo commits yet\nnothing to commit (create/copy files and use \"git add\" to track)"], "git init\ngit status", require=[r"git\s+init"], hint="Two commands: git init, then git status"),
        ),
        lesson(
            "Making a file",
            """To see Git working we need something to save. In the practice terminal you can create a file with echo:

echo "Hello" > notes.txt

This writes the word Hello into a file called notes.txt (the > sign means "put it in this file"). To look inside a file use cat:

cat notes.txt        shows Hello

Now ask Git for a short status:

git status --short

A brand-new file that Git has not been told about is UNTRACKED. It shows with two question marks:

?? notes.txt

That means: "I can see this file, but I am not saving its history yet." Next we will tell Git to keep it.

In this lesson you will learn: what an untracked file is.""",
            mcq("What does ?? notes.txt mean in the status?", ["Git sees the file but is not tracking it yet", "The file is broken", "The file was deleted", "The file is saved"], 0, "?? means untracked."),
            mcq("What does echo \"Hello\" > notes.txt do?", ["Puts Hello into the file notes.txt", "Deletes notes.txt", "Shows notes.txt", "Commits notes.txt"], 0, "The > sends the text into the file."),
            run("Start a repository and create a file notes.txt containing Hello. Don't save it yet.", "git", [t("untracked", append=STATUS), t("content", append="cat notes.txt")], ["?? notes.txt", "Hello"],
                'git init\necho "Hello" > notes.txt', require=[r"git\s+init"], hint='git init, then echo "Hello" > notes.txt'),
        ),
        lesson(
            "Telling Git what to save: git add",
            """Saving in Git takes two steps - like packing for a trip.

STEP 1 - git add: choose what goes in the box. This is called STAGING.

git add notes.txt

STEP 2 - git commit: close the box and label it. This makes the snapshot.

Why two steps? Because you might change five files but want to save only two of them together as one meaningful snapshot.

After git add the status looks like this (A means "added, ready to commit"):

A  notes.txt

You can add everything at once with:

git add .

(the dot means "everything here").

In this lesson you will learn: how to stage files so they are ready to be saved.""",
            mcq("What does git add do?", ["Chooses files to include in the next snapshot", "Makes the snapshot", "Deletes files", "Uploads files"], 0, "add = stage."),
            mcq("What does git add . mean?", ["Add everything here", "Add nothing", "Delete everything", "Add one file"], 0, "The dot means the current folder - everything."),
            order("Put the saving steps in order.", ["Change or create a file", "git add the file", "git commit with a message"], "Change, stage, then commit."),
            run("Start a repository, create notes.txt containing Hello, and stage it with git add.", "git", [t("staged", append=STATUS)], ["A  notes.txt"],
                'git init\necho "Hello" > notes.txt\ngit add notes.txt', require=[r"git\s+add"], hint="git add notes.txt"),
        ),
        lesson(
            "Saving a snapshot: git commit",
            """The second step: git commit takes everything you staged and saves it as a snapshot. You add a short message with -m (m for "message"):

git commit -m "Add notes"

Write messages that say WHAT you did, like a headline: "Add notes", "Fix typo", "Make the page blue". Future-you will thank you.

To see the history of your snapshots, newest first:

git log --format=%s

(That prints just the messages.)

Congratulations - that is the heart of Git: change files, git add, git commit. Everything else is built on these three ideas.

In this lesson you will learn: how to save your first snapshot.""",
            mcq("What does git commit -m \"Add notes\" do?", ["Saves a snapshot with that message", "Stages a file", "Deletes a file", "Starts a repo"], 0, "commit saves the staged changes."),
            mcq("What is the message for?", ["Describing what the snapshot contains", "Decoration", "Naming the computer", "Nothing"], 0, "Messages explain what changed."),
            fill("Save with a message.", 'git commit ___ "Add notes"', "-m", "-m means 'message'."),
            run("Start a repository, create notes.txt containing Hello, stage it and commit it with the message: Add notes", "git", [t("history", append=LOG), t("clean", append=STATUS + "\ncat notes.txt")],
                ["Add notes", "Hello"], 'git init\necho "Hello" > notes.txt\ngit add notes.txt\ngit commit -m "Add notes"', require=[r"git\s+add", r"git\s+commit"],
                hint='git init, echo, git add notes.txt, then git commit -m "Add notes"'),
        ),
    ),
]
