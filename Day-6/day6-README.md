# 📅 Day 6 — GitHub Advanced: Issues, Branch Protection & GitHub Actions

## 🎯 What is today about?

Today GitHub transforms from a code storage tool into a full automation platform.

We learned 5 powerful GitHub features:
- **GitHub Issues** — track work like a professional team
- **Branch Protection** — nobody can break main ever again
- **GitHub Actions** — code that runs automatically on every push
- **ShellCheck in CI** — automatic Bash script validation
- **.gitignore** — keeping the repo clean and secure

By the end of today — every push to GitHub automatically triggers a pipeline that validates our code. Zero manual work.

---

## 🏢 How real companies use these features

| Company | Real use case |
|---------|-------------|
| **Netflix** | 100+ GitHub Actions workflows run on every PR — build, test, security scan, deploy |
| **Microsoft** | Branch protection on all repos — no direct pushes to main ever |
| **Airbnb** | GitHub Issues linked to every PR — full audit trail of why each change was made |
| **Shopify** | ShellCheck and linting run automatically on every commit |
| **GitHub itself** | Uses GitHub Actions to build and deploy GitHub — meta! |

---

## 📋 GitHub Issues — professional task tracking

Issues are how engineering teams track bugs, features, and tasks.

### How Issues work

```
Engineer notices a bug or need
         ↓
Creates a GitHub Issue
         ↓
Issue gets a number (#1, #2, #3...)
         ↓
Developer writes code to fix it
         ↓
Commits with "closes #2" in message
         ↓
PR merged to main
         ↓
Issue #2 closes automatically 🎯
```

### Creating a good Issue

```markdown
## What needs to be done
- Task 1
- Task 2
- Task 3

## Acceptance criteria
- [ ] Checkbox 1
- [ ] Checkbox 2
- [ ] Checkbox 3
```

### Linking commits to Issues

```bash
# These keywords auto-close the Issue on merge
git commit -m "feat: add workflow - closes #2"
git commit -m "fix: correct bug - fixes #3"
git commit -m "docs: update README - resolves #4"
```

> 💡 **Beginner tip:** Always create an Issue before writing code. This builds a habit of planning before coding — exactly how professional teams work.

---

## 🛡️ Branch Protection — keeping main safe

Branch protection rules prevent anyone from pushing directly to main.

### What branch protection enforces

```
Without protection:              With protection:
❌ Anyone pushes to main         ✅ PRs required — no direct push
❌ Broken code reaches main      ✅ Tests must pass before merge
❌ No review of changes          ✅ Code review enforced
❌ Production breaks at 2am      ✅ Only validated code merges
```

### Setting up branch protection

```
1. Repo → Settings → Branches
2. Add branch protection rule
3. Branch name pattern: main
4. Enable:
   ✅ Require a pull request before merging
   ✅ Do not allow bypassing the above settings
5. Save
```

### What happens when you try to push directly now

```bash
git push origin main
# remote: error: GH006: Protected branch update failed
# remote: Changes must be made through a pull request
```

This error is a good thing — it means protection is working!

---

## ⚡ GitHub Actions — your first CI pipeline

GitHub Actions runs code automatically when something happens in your repo.

### How GitHub Actions works

```
You push code to GitHub
        │
        ▼
GitHub detects the push
        │
        ▼
Finds .github/workflows/*.yml
        │
        ▼
Spins up fresh Ubuntu server (runner)
        │
        ▼
Runs every step in your workflow
        │
        ▼
Shows ✅ green or ❌ red on your commit
```

### YAML structure — memorize this

```yaml
name: Pipeline Name          # What this pipeline is called

on:                          # When to trigger
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:                        # What to run
  job-name:                  # Name your job
    runs-on: ubuntu-latest   # Which OS

    steps:                   # List of steps
      - name: Step name      # Label for the step
        run: command here    # The actual command
```

### The 4 things to remember

```
name → on → jobs → steps
```

That's the entire structure. Everything else is filling in the details.

### Today's complete workflow

```yaml
name: DevOps Learning Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  hello-devops:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Print welcome message
        run: echo "Hello from GitHub Actions!"

      - name: Show current date
        run: date

      - name: Show system info
        run: uname -a

      - name: List repo files
        run: ls -la

      - name: Run a simple health check
        run: |
          echo "Running health checks..."
          df -h
          free -h
          echo "All checks passed!"

  check-scripts:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Install shellcheck
        run: sudo apt install shellcheck -y

      - name: Check all shell scripts
        run: |
          echo "Checking shell scripts..."
          find . -name "*.sh" -exec shellcheck {} \;
          echo "All scripts passed!"
```

---

## 🧹 .gitignore — keeping your repo clean

.gitignore tells Git which files to never track.

### What to always ignore

```gitignore
# Log files — generated automatically, don't commit
*.log
health-*.log

# OS files — created by Windows/Mac, not your code
.DS_Store
Thumbs.db

# Editor files — personal settings, not project files
.vscode/
*.swp

# Temporary files
*.tmp
test.txt
```

### Why .gitignore matters

```
Without .gitignore:             With .gitignore:
❌ Log files in every commit    ✅ Only real code committed
❌ OS junk files everywhere     ✅ Clean, professional repo
❌ Secrets accidentally pushed  ✅ Sensitive files excluded
❌ Repo size grows forever      ✅ Repo stays lean and fast
```

---

## 🔧 Troubleshooting — common errors and fixes

| Error | Why it happens | Fix |
|-------|---------------|-----|
| `Invalid workflow file` | YAML indentation wrong | Use 2 spaces — never tabs |
| `Required property missing: jobs` | Pasted partial YAML | Include full file with `name`, `on`, `jobs` |
| `Protected branch update failed` | Tried to push to main directly | Create a branch and PR instead |
| `shellcheck: command not found` | Not installed on runner | Add `sudo apt install shellcheck -y` step first |
| `Node.js 20 deprecated warning` | Using old action version | Update `actions/checkout@v3` to `@v4` |
| Pipeline runs but Issue stays open | Missing `closes #N` in commit | Add `closes #2` to commit message |
| PR can't be merged | Branch protection blocking | Check required status checks passed |

---

## 🧠 Key Lessons from Day 6

> **Lesson 1:** GitHub Issues + branch protection + CI pipeline = the professional engineering workflow. Every company uses this exact combination.

> **Lesson 2:** YAML is indentation-sensitive. Two spaces per level. Never tabs. One wrong space breaks everything.

> **Lesson 3:** `closes #2` in a commit message is magic — it automatically closes the Issue when the PR merges. Always link code to Issues.

> **Lesson 4:** Warning ≠ Error. A yellow warning means "fix this soon." A red error means "fix this now." Learn to tell the difference.

> **Lesson 5:** CI pipelines validate your code automatically. You never need to manually check "did my script work?" — the pipeline tells you on every push.

---

## 🎯 Interview questions — practice these after Day 6

1. **What is GitHub Actions and how does it work?**
   > GitHub Actions is a CI/CD platform built into GitHub. It runs automated workflows when events happen in your repo — like pushing code or opening a PR. Workflows are defined in YAML files in `.github/workflows/`. GitHub spins up a fresh server, runs your steps, and reports pass/fail on every commit.

2. **What is the difference between a job and a step in GitHub Actions?**
   > A job is a collection of steps that run on the same server. Steps are individual commands within a job. Multiple jobs run in parallel by default — multiple steps in a job run sequentially. Use jobs to separate concerns (build, test, deploy) and steps for the commands within each concern.

3. **What is branch protection and why is it important?**
   > Branch protection rules prevent direct pushes to important branches like main. They enforce PRs, require status checks to pass, and can require code reviews. This prevents broken code from reaching production and ensures all changes are reviewed and tested.

4. **How do you automatically close a GitHub Issue with a commit?**
   > Include keywords like `closes #N`, `fixes #N`, or `resolves #N` in your commit message — where N is the Issue number. When that commit is merged to the default branch, GitHub automatically closes the referenced Issue.

5. **What is ShellCheck and why use it in CI?**
   > ShellCheck is a static analysis tool for Bash scripts — it finds bugs, syntax errors, and bad practices before you run the script. Adding it to CI means every push automatically validates all shell scripts. Catches errors early — before they cause problems in production.

6. **What does `runs-on: ubuntu-latest` mean in GitHub Actions?**
   > It tells GitHub Actions which operating system to use for the runner — the server that executes your workflow. `ubuntu-latest` means the latest Ubuntu Linux version. You can also use `windows-latest` or `macos-latest` depending on your needs.

---

## ❓ Frequently asked questions

**Q: Is GitHub Actions free?**
For public repositories — completely free with unlimited minutes. For private repos — 2,000 free minutes per month on the free plan. Your learning repo is public so it's 100% free.

**Q: Can I run GitHub Actions on my own server?**
Yes — these are called self-hosted runners. Instead of GitHub's servers, your own machine runs the workflows. Useful for companies with security requirements or needing specific hardware.

**Q: What is `uses: actions/checkout@v4`?**
It's a pre-built action from the GitHub Actions marketplace. `checkout` downloads your repo code onto the runner so subsequent steps can access your files. Without it — your workflow can't see your code.

**Q: How many workflows can I have?**
As many as you need. Common setups: one for CI (test on every push), one for CD (deploy on merge to main), one for security scanning, one for dependency updates. Each is a separate `.yml` file in `.github/workflows/`.

---

## 📚 Resources to go deeper

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Actions Marketplace](https://github.com/marketplace?type=actions)
- [ShellCheck Documentation](https://www.shellcheck.net/)
- [YAML Syntax Guide](https://yaml.org/spec/1.2-old/spec.html)

---

## 📁 Files in this folder

| File | What it is |
|------|-----------|
| `README.md` | This file — Day 6 complete guide |
| `.github/workflows/learn-devops.yml` | First CI pipeline — 2 jobs |
| `.gitignore` | Files excluded from Git tracking |

---

## ⬅️ Previous Day
[Day 5 — Git Deep Dive: Branches, Merging, Pull Requests](../Day-5/)

## ➡️ Next Day
[Day 7 — Git Advanced + Week 1 Mini Project](../Day-7/)

---

*Part of my [90-Day DevOps + AI Journey](../../README.md) — documented daily for beginners and professionals alike.*
