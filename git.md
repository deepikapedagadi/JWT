Setup

git init → Initialize a new Git repository.
git clone <repo-url> → Copy (clone) an existing repo from GitHub.
git config --global user.name "Your Name" → Set your Git username.
git config --global user.email "you@example.com" → Set your Git email.

Basic Workflow

git status→ Check current repo status.
git add <file> → Stage a file for commit.
git add . → Stage all changes.
git commit -m "message" → Save changes with a message.
git log → View commit history.

Remote Repositories

git remote -v → Show remote repo URLs.
git remote add origin <url> → Add remote repo.
git push -u origin main → Push local code to GitHub (set upstream).
git pull → Fetch & merge latest changes from remote.
git fetch → Fetch latest changes without merging.

Branching

git branch → List branches.
git branch <name> → Create a new branch.
git checkout <name> → Switch to another branch.
git checkout -b <name> → Create & switch to new branch.
git merge <branch> → Merge branch into current branch.

Undo/Reset

git restore <file> → Discard changes in a file.
git reset <file> → Unstage a file.
git reset --hard → Reset repo to last commit (⚠ deletes changes).

Collaboration

git stash → Save changes temporarily.
git stash pop → Reapply stashed changes.
git rebase <branch> → Reapply commits on top of another branch.
