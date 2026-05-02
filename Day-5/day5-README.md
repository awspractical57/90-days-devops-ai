# 📅 Day 5 — Git Deep Dive: Branches, Merging & Pull Requests

## 🎯 What is today about?

Today we go deep into Git — the tool that every DevOps engineer uses every single day.

We didn't just learn commands. We learned **how professional teams actually use Git** — branches, pull requests, code reviews, and clean commit history.

By the end of today we created a real branch, pushed it to GitHub, opened a Pull Request, merged it, and cleaned up. That's the complete professional workflow.

---

## 🏢 How real companies use Git

| Company | How they use Git |
|---------|----------------|
| **Google** | 2 billion lines of code in one Git repo — 25,000 engineers committing daily |
| **Microsoft** | Moved Windows source code to Git — the world's largest Git migration |
| **Netflix** | Every microservice has its own Git repo — hundreds of PRs merged daily |
| **Amazon** | No code goes to production without a PR review — Git enforces this |
| **Meta** | Uses Git branch protection — nobody can push directly to main |

> 💡 **Key insight:** In every professional company — nobody pushes directly to main. Everything goes through a branch and a Pull Request. Today you learned exactly that workflow.

---

## 🤔 What is Git and why does it exist?

Before Git — teams emailed code files to each other. Someone would overwrite someone else's work. There was no history of changes.

**Git solved all of that:**

```
Without Git:                    With Git:
❌ "Who changed this?"          ✅ git log shows every change
❌ "I broke everything!"        ✅ git restore goes back instantly
❌ "Our changes conflict!"      ✅ branches keep work separate
❌ "What did we deploy?"        ✅ every commit is tagged forever
```

---

## 🏗️ How Git works — the 3 areas

```
┌─────────────────────────────────────────────────────┐
│                                                      │
│   Working Directory  →  Staging Area  →  Repository │
│   (where you edit)      (git add)       (git commit) │
│                                                      │
│   your files here    ready to save    saved forever  │
│                                                      │
└─────────────────────────────────────────────────────┘
                                    │
                                    │ git push
                                    ▼
                             GitHub (remote)
```

**The flow every commit takes:**
1. You edit a file → it's in **Working Directory**
2. `git add file` → moves to **Staging Area**
3. `git commit` → saved to local **Repository**
4. `git push` → uploaded to **GitHub**

---

## 📋 Essential Git commands

### Checking status and history

```bash
git status                    # What files changed?
git log                       # Full commit history
git log --oneline             # Clean one-line history
git log --oneline --graph     # Visual branch history
git diff HEAD~1 HEAD          # What changed in last commit?
git diff --staged             # What's staged but not committed?
git show abc1234              # Full details of a specific commit
```

### Undoing mistakes

```bash
# Unstage a file (undo git add)
git restore --staged filename.sh

# Discard changes in working directory
git restore filename.sh

# Undo last commit but keep changes
git reset --soft HEAD~1
```

### Setup — run once

```bash
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
git config --global core.editor nano
git config --global core.autocrlf true    # Windows only
```

---

## 🌿 Branches — parallel universes for your code

A branch lets you work on something new without touching the working code.

### How branches work visually

```
main:     A ── B ── C ──────────────── F (merge)
                     \                /
feature:              D ── E ── (PR) /

A = Initial commit
B = Added glossary
C = Added scripts
D = Working on new feature (safe — main not affected)
E = Feature complete
F = Merged back to main via Pull Request
```

### Branch commands

```bash
# See all branches
git branch

# Create a new branch
git branch feature-name

# Switch to a branch
git checkout feature-name

# Create AND switch in one command (most common)
git checkout -b feature-name

# Push branch to GitHub
git push origin feature-name

# See all branches including remote
git branch -a

# Delete a branch after merging
git branch -d feature-name
git push origin --delete feature-name
```

---

## 🔀 Pull Requests — how professional teams merge code

A Pull Request (PR) is a formal request to merge your branch into main.

### Why PRs exist

```
Without PRs:                      With PRs:
❌ Push directly to main          ✅ Code reviewed before merging
❌ No one checks your code        ✅ Teammates catch bugs early
❌ Tests might not run            ✅ Automated tests run on every PR
❌ No record of why change made   ✅ Discussion and context saved forever
```

### The PR workflow we followed today

```
1. git checkout -b day-05-git-practice    ← create branch
2. make changes + git add + git commit    ← do the work
3. git push origin day-05-git-practice   ← push to GitHub
4. Open PR on GitHub                      ← request review
5. Add title + description               ← explain what + why
6. Merge PR                              ← code goes to main
7. git branch -d day-05-git-practice     ← clean up
```

---

## 📝 Professional commit message format

Good commit messages tell a story. Bad ones are useless.

```bash
# ❌ Bad commit messages
git commit -m "updated files"
git commit -m "fix"
git commit -m "changes"
git commit -m "asdfgh"

# ✅ Good commit messages (Conventional Commits format)
git commit -m "feat: add disk usage monitoring script"
git commit -m "fix: correct nginx service name typo"
git commit -m "docs: update Day 4 README with cron examples"
git commit -m "chore: remove unused health log files"
git commit -m "refactor: simplify service check loop"
```

### Commit types

| Type | When to use |
|------|------------|
| `feat` | Adding new functionality |
| `fix` | Fixing a bug |
| `docs` | Documentation changes |
| `chore` | Maintenance, cleanup |
| `refactor` | Improving code without changing behavior |
| `test` | Adding or fixing tests |

> 💡 **Why this matters:** Netflix, Google, Microsoft all use this format. Interviewers check your commit history. Good messages show professionalism instantly.

---

## 🔧 Troubleshooting — common Git errors and fixes

| Error | Why it happens | Fix |
|-------|---------------|-----|
| `fatal: no upstream branch` | First push of new branch | Use `git push origin branchname` |
| `fatal: ambiguous argument HEAD-1` | Wrong syntax | Use tilde: `HEAD~1` not `HEAD-1` |
| `error: Your local changes would be overwritten` | Uncommitted changes | `git stash` then `git pull` |
| `CONFLICT: Merge conflict` | Two branches changed same line | Open file, fix conflict markers, commit |
| `LF will be replaced by CRLF` | Windows line endings | Run `git config --global core.autocrlf true` |
| `git add.` not working | Missing space | Always `git add .` with space |
| Committed to wrong branch | Forgot to checkout branch first | `git reset --soft HEAD~1` then switch branch |

---

## 🧠 Key Lessons from Day 5

> **Lesson 1:** Git is a time machine. Every commit is a snapshot you can return to. Never fear breaking things — Git has your back.

> **Lesson 2:** Branches are parallel universes. Experiment freely without touching main. If it works — merge. If it breaks — delete.

> **Lesson 3:** Never push directly to main in a professional team. Always branch → PR → review → merge.

> **Lesson 4:** `git log --oneline --graph` shows your entire history visually. Run it often — it makes Git click.

> **Lesson 5:** Good commit messages are professional communication. "feat: add disk monitoring" tells a story. "fix stuff" tells nothing.

---

## 🎯 Interview questions — practice these after Day 5

1. **What is the difference between `git merge` and `git rebase`?**
   > `git merge` combines two branches and creates a merge commit — preserving full history. `git rebase` moves your branch commits on top of another branch — creates cleaner linear history but rewrites commits. For beginners — always use merge. Rebase is for advanced users.

2. **What is a Pull Request and why is it important?**
   > A PR is a request to merge a feature branch into main. It enables code review, automated testing, and discussion before code reaches production. In professional teams nothing goes to main without a PR — it's the quality gate for all code changes.

3. **How do you undo a commit that hasn't been pushed yet?**
   > `git reset --soft HEAD~1` — removes the commit but keeps your changes staged. `git reset --hard HEAD~1` — removes the commit AND discards all changes permanently. Always use `--soft` unless you're sure you want to lose the changes.

4. **What does `git stash` do?**
   > It temporarily saves your uncommitted changes and cleans your working directory. Useful when you need to switch branches but aren't ready to commit. `git stash` to save, `git stash pop` to restore.

5. **What is the difference between `git fetch` and `git pull`?**
   > `git fetch` downloads changes from remote but doesn't apply them — you can review first. `git pull` downloads AND applies changes immediately. `git pull` = `git fetch` + `git merge`.

6. **How do you resolve a merge conflict?**
   > Open the conflicted file — Git marks conflicts with `<<<<<<<`, `=======`, `>>>>>>>`. The section above `=======` is your change, below is the incoming change. Delete the markers, keep what you want, save the file, then `git add` and `git commit`.

---

## ❓ Frequently asked questions

**Q: What is HEAD in Git?**
HEAD is a pointer to your current position in the Git history — usually the latest commit on your current branch. `HEAD~1` means "one commit before current." `HEAD~2` means two commits back.

**Q: What is origin in `git push origin main`?**
`origin` is the default name Git gives to your remote repository (GitHub). When you clone a repo, Git automatically names the remote `origin`. You can have multiple remotes with different names.

**Q: Can I have multiple branches at the same time?**
Yes — you can have as many branches as you want. But you can only be ON one branch at a time. The branch you're currently on is shown with `*` in `git branch` and in your terminal prompt.

**Q: What happens if I delete a branch before merging?**
Using `git branch -d branchname` — Git will warn you if the branch isn't merged and refuse to delete it. Using `git branch -D branchname` (capital D) forces deletion even if not merged — be careful with this.

**Q: Should I commit often or in big batches?**
Commit often — small, focused commits. One commit = one logical change. "Add disk monitoring script" is good. "Added scripts, fixed bugs, updated docs, changed config" in one commit is bad. Small commits are easier to review, revert, and understand.

---

## 📚 Resources to go deeper

- [Git Official Documentation](https://git-scm.com/doc)
- [Oh My Git — visual Git learning game](https://ohmygit.org/)
- [Learn Git Branching — interactive](https://learngitbranching.js.org/)
- [Conventional Commits Standard](https://www.conventionalcommits.org/)

---

## 📁 Files in this folder

| File | What it is |
|------|-----------|
| `README.md` | This file — Day 5 complete guide |
| `git-notes.md` | Personal Git command reference |
| `branch-practice.md` | Created on feature branch — merged via PR |

---

## ⬅️ Previous Day
[Day 4 — Advanced Bash: Variables, Conditions, Loops, Cron Jobs](../Day-4/)

## ➡️ Next Day
[Day 6 — GitHub Collaboration: Issues, Actions, Branch Protection](../Day-6/)

---

*Part of my [90-Day DevOps + AI Journey](../../README.md) — documented daily for beginners and professionals alike.*
