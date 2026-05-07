# 📅 Day 7 — Git Advanced + Week 1 Mini Project

## 🎯 What is today about?

Day 7 wraps up Week 1 with two Git commands every professional uses daily — `git stash` and `git tag` — and builds a mini project that combines everything learned this week into one working tool.

---

## 🏢 How real companies use these features

| Company | Real use case |
|---------|-------------|
| **Google** | Tags every release — v1.0, v2.0, v3.0 — triggers production deployments |
| **Netflix** | Engineers use git stash dozens of times daily switching between urgent fixes |
| **Amazon** | Release tags trigger automated deployment pipelines to production |
| **Microsoft** | Every Windows release is tagged in Git — full history going back years |
| **GitHub** | Uses stash when switching between feature work and urgent hotfixes |

---

## 💾 Git Stash — save work without committing

### The problem it solves

```
You're halfway through a feature
Manager: "Fix this urgent bug RIGHT NOW"
You: Can't commit half-done work...
Solution: git stash
```

### How stash works

```
Working on feature (half done)
        │
        ▼
git stash          → saves work in a drawer
        │
        ▼
Working directory is clean
        │
        ▼
Fix urgent bug → commit → merge
        │
        ▼
git stash pop      → your feature work is back
        │
        ▼
Continue where you left off
```

### Stash commands

```bash
git stash           # Save current work temporarily
git stash pop       # Restore last saved work
git stash list      # See all stashes
git stash drop      # Delete last stash
git stash clear     # Delete all stashes
```

> 💡 **Beginner tip:** git stash is like a temporary clipboard for your code. Save it, do something else, paste it back. Nothing is lost.

---

## 🏷️ Git Tags — marking important versions

### Why tags exist

Tags mark specific points in history as important milestones — releases, completed phases, deployments.

```
Commit history:
A → B → C → D → E → F → G
              ↑           ↑
           v1.0.0      v2.0.0
        (Week 1 done) (Week 2 done)
```

### Tag commands

```bash
# Create annotated tag
git tag -a v0.1.0 -m "Week 1 complete: Linux, Bash, Git, GitHub Actions"

# List all tags
git tag

# See tag details
git show v0.1.0

# Push tag to GitHub
git push origin v0.1.0

# Push all tags
git push origin --tags

# Delete local tag
git tag -d v0.1.0

# Delete remote tag
git push origin --delete v0.1.0
```

### Tag naming convention

```
v1.0.0  ← Major release (big new features)
v1.1.0  ← Minor release (small new features)
v1.1.1  ← Patch release (bug fixes only)
v0.1.0  ← Pre-release (still in development)
```

---

## 🚀 Week 1 Mini Project — DevOps Automation Toolkit

The mini project combines every skill from Week 1 into one interactive tool.

### What it does

```
./devops-toolkit.sh
        │
        ▼
==================================
     DevOps Automation Toolkit
==================================
1. System Health Check
2. Service Status
3. Network Check
4. Generate Report
5. Exit
==================================
Enter your choice: _
```

### Skills used from each day

| Day | Skill | Used in project |
|-----|-------|----------------|
| Day 2 | Linux commands | df, free, ping |
| Day 3 | Service management | systemctl is-active |
| Day 4 | Variables | CHOICE, SERVICE, REPORT |
| Day 4 | Conditions | case statement |
| Day 4 | Loops | for SERVICE in nginx cron ssh |
| Day 5 | Git workflow | feature branch + PR |
| Day 6 | GitHub Actions | CI validates the script |

### How to run it

```bash
chmod +x devops-toolkit.sh
./devops-toolkit.sh
```

### What each option does

| Option | What it runs |
|--------|-------------|
| 1 — System Health | `free -h` + `df -h` |
| 2 — Service Status | loops through nginx, cron, ssh |
| 3 — Network Check | `ping -c 2 -4 google.com` |
| 4 — Generate Report | saves dated report file |
| 5 — Exit | clean exit with message |

---

## 🔧 Troubleshooting

| Error | Why | Fix |
|-------|-----|-----|
| `ping: invalid argument` | WSL2 needs IPv4 flag | Use `ping -c 2 -4 google.com` |
| `case #CHOICE in` not working | `#` is a comment in Bash | Use `$CHOICE` not `#CHOICE` |
| Tag already exists error | Tag created twice | Delete with `git tag -d v0.1.0` then recreate |
| Protected branch push failed | Branch protection active | Always use feature branch + PR |
| `git stash pop` shows conflicts | Stash conflicts with current state | Resolve conflicts manually then commit |

---

## 🧠 Key Lessons from Day 7

> **Lesson 1:** `git stash` is your emergency pause button. Half-done work saved instantly — restore it anytime.

> **Lesson 2:** Tags are permanent bookmarks. Every release, every milestone — tag it. Your entire project history becomes navigable.

> **Lesson 3:** `#` means comment in Bash. `$` means variable. Confusing them breaks scripts silently.

> **Lesson 4:** A menu-driven script is more powerful than individual scripts — one tool, multiple functions, professional feel.

> **Lesson 5:** Week 1 is done. You went from zero to a working CI pipeline and an interactive DevOps toolkit in 7 days. That's real.

---

## 🎯 Interview questions — practice these

1. **What is git stash and when would you use it?**
   > git stash temporarily saves uncommitted work and cleans the working directory. Use it when you need to switch branches urgently but aren't ready to commit. `git stash` to save, `git stash pop` to restore.

2. **What is the difference between a git tag and a branch?**
   > A branch moves forward with every commit — it's a pointer that keeps updating. A tag is fixed — it permanently marks one specific commit. Tags are for releases (v1.0), branches are for ongoing work (feature/add-monitoring).

3. **What is semantic versioning?**
   > A versioning standard: MAJOR.MINOR.PATCH. v2.1.3 means major version 2, minor version 1, patch 3. Major = breaking changes. Minor = new features. Patch = bug fixes. Used by every professional software project.

4. **How do you use a case statement in Bash?**
   > `case $VARIABLE in` followed by patterns and commands, each ending with `;;`, closed with `esac`. Better than multiple if/elif for menu selections — cleaner and faster.

5. **What does `read -p` do in Bash?**
   > It displays a prompt and waits for user input, storing it in a variable. `read -p "Enter choice: " CHOICE` shows the prompt and saves what the user types into `$CHOICE`.

---

## 📚 Resources

- [Git Tags Documentation](https://git-scm.com/book/en/v2/Git-Basics-Tagging)
- [Git Stash Guide](https://www.atlassian.com/git/tutorials/saving-changes/git-stash)
- [Semantic Versioning](https://semver.org/)
- [Bash case Statement](https://www.gnu.org/software/bash/manual/bash.html#Conditional-Constructs)

---

## 📁 Files in this folder

| File | What it is |
|------|-----------|
| `README.md` | This file — Day 7 complete guide |

---

## 📁 Week 1 Mini Project

See [Week-1-Project/README.md](../Week-1-Project/README.md) for full project documentation.

---

## ⬅️ Previous Day
[Day 6 — GitHub Advanced: Issues, Branch Protection, GitHub Actions](../Day-6/)

## ➡️ Next Week
[Week 2 — Docker: Containers from scratch](../Day-8/)

---

*Part of my [90-Day DevOps + AI Journey](../../README.md) — documented daily for beginners and professionals alike.*
