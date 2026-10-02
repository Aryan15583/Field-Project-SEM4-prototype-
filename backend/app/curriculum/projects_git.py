"""Git projects - one at the end of each section (added to units 4, 6 and 8).

Each step continues from the learner's own script (carry=True): the whole script runs from a fresh start
every time, so the repository is rebuilt step by step.
"""
from .dsl import project, run, t
from .git import LOG, STATUS

# ------------------------------------------------------------------ Beginner: your first website repo
SITE_1 = """git init
echo "<h1>My site</h1>" > index.html
echo "h1 { color: navy; }" > style.css
git add .
git commit -m "Initial site"
"""
SITE_2 = SITE_1 + """git switch -c contact
echo "<h1>Contact</h1>" > contact.html
git add contact.html
git commit -m "Add contact page"
git switch main
git merge contact
git branch -d contact
"""
SITE_3 = SITE_2 + """echo "<marquee>SALE</marquee>" >> index.html
git commit -am "Add banner"
git revert HEAD
git tag v1.0
"""

BEGINNER = project(
    "Project: Your first website repo",
    "Put a small website under version control from day one:\n\n1. Create the repo and the first commit.\n2. Build a "
    "page on a branch and merge it.\n3. Ship a mistake, undo it safely, and tag the release.\n\nEach step continues "
    "your script from the step before.",
    run("Step 1 - Create a repo with index.html (<h1>My site</h1>) and style.css (h1 { color: navy; }), and commit both "
        "as 'Initial site'.", "git",
        [t("history", append=LOG), t("files", append=STATUS + "\nls")], ["Initial site", "index.html\nstyle.css"], SITE_1,
        starter="git init\n", require=[r"git\s+commit"]),
    run("Step 2 - On a new branch contact, add contact.html (<h1>Contact</h1>) and commit 'Add contact page'. Merge it "
        "into main, delete the branch, and end on main.", "git",
        [t("history", append=LOG), t("branches", append="git branch\nls")],
        ["Add contact page\nInitial site", "* main\ncontact.html\nindex.html\nstyle.css"], SITE_2, starter=SITE_1, carry=True,
        require=[r"git\s+merge\s+contact"]),
    run("Step 3 - Append <marquee>SALE</marquee> to index.html and commit it as 'Add banner'. That was a bad idea: undo "
        "it with git revert, then tag the result v1.0.", "git",
        [t("history", append=LOG), t("page", append="cat index.html\ngit tag")],
        ['Revert "Add banner"\nAdd banner\nAdd contact page\nInitial site', "<h1>My site</h1>\nv1.0"], SITE_3, starter=SITE_2,
        carry=True, require=[r"git\s+revert", r"git\s+tag\s+v1\.0"]),
)

# ------------------------------------------------------------------ Intermediate: hotfix during a feature
SHOP = """git init
echo "price = 10" > shop.py
echo "# Shop" > README.md
git add .
git commit -m "Start shop"
git switch -c feature/cart
echo "cart = []" > cart.py
git add .
git commit -m "Start cart"
echo "def add(item): cart.append(item)" >> cart.py
"""
HOT_1 = """git stash
git switch main
git switch -c hotfix
echo "price = 12" > shop.py
git commit -am "Fix price"
git switch main
git merge hotfix
git branch -d hotfix
"""
HOT_2 = HOT_1 + """git switch feature/cart
git stash pop
git commit -am "Finish cart"
git merge main
"""
HOT_3 = HOT_2 + """git switch main
git merge feature/cart
git tag v2.0
git remote add origin https://github.com/ada/shop.git
git push -u origin main
"""
FULL_HISTORY = "Merge branch 'main'\nFinish cart\nFix price\nStart cart\nStart shop"

INTERMEDIATE = project(
    "Project: Hotfix during a feature",
    "You're half-way through a shopping-cart feature (branch feature/cart, with unsaved edits to cart.py) when "
    "production breaks. Handle it like a pro:\n\n1. Stash your work and ship a hotfix on main.\n2. Get back to your "
    "feature and bring the fix into it.\n3. Release everything: merge, tag and push.",
    run("Step 1 - Stash your cart work, then from main create a branch hotfix, set shop.py to price = 12, commit 'Fix "
        "price', merge hotfix into main and delete it.", "git",
        [t("main", append="git log --format=%s main"), t("branches", append="git branch\ncat shop.py")],
        ["Fix price\nStart shop", "  feature/cart\n* main\nprice = 12"], HOT_1, setup=SHOP,
        require=[r"git\s+stash", r"hotfix"]),
    run("Step 2 - Switch back to feature/cart, restore your stashed work, commit it as 'Finish cart', and merge main into "
        "the feature branch so it has the hotfix.", "git",
        [t("feature", append=LOG), t("files", append=STATUS + "\ncat shop.py cart.py")],
        [FULL_HISTORY, "price = 12\ncart = []\ndef add(item): cart.append(item)"], HOT_2, setup=SHOP, starter=HOT_1, carry=True,
        require=[r"stash\s+pop", r"git\s+merge\s+main"]),
    run("Step 3 - Release: merge feature/cart into main, tag it v2.0, add the remote origin "
        "(https://github.com/ada/shop.git) and push main with an upstream.", "git",
        [t("main", append=LOG + "\ngit tag"), t("pushed", append="git branch -r\ngit status")],
        [FULL_HISTORY + "\nv2.0", "  origin/main\nOn branch main\nYour branch is up to date with 'origin/main'.\nnothing to commit, working tree clean"],
        HOT_3, setup=SHOP, starter=HOT_2, carry=True, require=[r"git\s+tag\s+v2\.0", r"push\s+-u"]),
)

# ------------------------------------------------------------------ Advanced: team release
TEAM = """git init
echo "v1" > VERSION
echo "Welcome" > banner.txt
git add .
git commit -m "Release 1"
git remote add origin https://github.com/team/app.git
git push -u origin main
git switch -c feature/banner
echo "Welcome back!" > banner.txt
git commit -am "Friendlier banner"
git switch main
git switch -c feature/sale
echo "Big sale today" > banner.txt
git commit -am "Sale banner"
echo "50%" > sale.txt
git add .
git commit -m "Add sale details"
git switch main
"""
REL_1 = """git merge feature/banner
git merge feature/sale
echo "Welcome back! Big sale today" > banner.txt
git add banner.txt
git commit -m "Merge sale"
"""
REL_2 = REL_1 + """echo "v2" > VERSION
git commit -am "Release 2"
git tag v2.0
git push
"""
REL_3 = REL_2 + """git revert feature/sale
git push
"""
MERGED = "Merge sale\nAdd sale details\nSale banner\nFriendlier banner\nRelease 1"
UP_TO_DATE = "On branch main\nYour branch is up to date with 'origin/main'.\nnothing to commit, working tree clean"

ADVANCED = project(
    "Project: Team release",
    "Two teammates finished their branches - feature/banner and feature/sale - and it's your job to ship the "
    "release:\n\n1. Merge both, resolving the conflict between them.\n2. Bump the version, tag and push.\n3. A "
    "problem is found after release: undo one feature the safe way.\n\nThe repository already has a remote "
    "origin with main pushed.",
    run("Step 1 - Merge feature/banner, then feature/sale. They both changed banner.txt: resolve it to exactly "
        "Welcome back! Big sale today and commit the merge as 'Merge sale'.", "git",
        [t("history", append=LOG), t("resolved", append=STATUS + "\ncat banner.txt sale.txt")],
        [MERGED, "Welcome back! Big sale today\n50%"], REL_1, setup=TEAM, require=[r"merge\s+feature/banner", r"merge\s+feature/sale"]),
    run("Step 2 - Set VERSION to v2, commit 'Release 2', tag it v2.0 and push main (it already tracks origin/main).", "git",
        [t("release", append="git log --format=%s -n 1 v2.0\ngit tag"), t("pushed", append="git status")],
        ["Release 2\nv2.0", UP_TO_DATE], REL_2, setup=TEAM, starter=REL_1, carry=True, require=[r"git\s+tag\s+v2\.0", r"git\s+push"]),
    run("Step 3 - The sale details must come down, but main is already pushed - so don't rewrite history. Revert the "
        "'Add sale details' commit (the branch feature/sale still points at it) and push.", "git",
        [t("history", append="git log --format=%s -n 3"), t("files", append="ls\ngit status")],
        ['Revert "Add sale details"\nRelease 2\nMerge sale', "VERSION\nbanner.txt\n" + UP_TO_DATE], REL_3, setup=TEAM,
        starter=REL_2, carry=True, require=[r"git\s+revert"], forbid=[r"reset\s+--hard"]),
)

PROJECTS = {4: BEGINNER, 6: INTERMEDIATE, 8: ADVANCED}
