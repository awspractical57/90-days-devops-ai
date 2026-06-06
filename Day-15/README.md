# 📅 Day 15 — GitHub Actions Advanced CI/CD

## 🎯 What is today about?

On Day 6 we wrote our first GitHub Actions pipeline.
Today we go advanced — 3 powerful features that separate junior from senior engineers.

By the end of today we added manual triggers, matrix builds across 3 Python versions, and reusable workflows to our CI/CD pipeline.

---

## 🏢 How real companies use these features

| Feature | Real company use case |
|---------|----------------------|
| `workflow_dispatch` | Netflix triggers deployments manually during planned releases |
| Matrix builds | Microsoft tests VS Code on Windows, Mac, Linux simultaneously |
| Reusable workflows | Google defines standard security scans used by 100s of teams |

---

## 🤔 What is CI/CD — quick recap

```
CI = Continuous Integration
   → Every code change is automatically tested
   → Problems caught immediately — not in production

CD = Continuous Delivery/Deployment
   → Tested code automatically deployed
   → No manual steps between commit and production
```

**Your pipeline flow:**
```
Developer pushes code
       ↓
GitHub Actions triggers automatically
       ↓
Build → Test → Security Scan → Push to Docker Hub
       ↓
Deployed to production (or staging)
```

---

## 🏗️ What was wrong with the old pipeline

```yaml
# Problem 1: Only triggered on push/PR
# No way to run manually
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
# ❌ Missing: workflow_dispatch

# Problem 2: Tested on only one environment
# No matrix — no version testing
runs-on: ubuntu-latest
# ❌ Missing: matrix strategy

# Problem 3: Health check copy-pasted everywhere
# Every pipeline duplicates the same steps
# ❌ Missing: reusable workflow
```

---

## Feature 1 — workflow_dispatch (Manual Trigger)

### What it does
Adds a "Run workflow" button to GitHub Actions UI.
You can trigger the pipeline manually without making any code change.

### Why it matters
```
Scenario: Production is down at 2AM
You need to redeploy — but you don't want to change code
Without workflow_dispatch: make a dummy commit just to trigger pipeline ❌
With workflow_dispatch:    click "Run workflow" → choose production → done ✅
```

### How to add it

```yaml
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:          # ← add this
    inputs:
      environment:
        description: 'Deploy to which environment?'
        required: true
        default: 'staging'
        type: choice
        options:
          - staging
          - production
```

### Key rules
```
✅ workflow_dispatch only shows button on DEFAULT branch (main)
✅ Adding it to feature branch — button won't appear until merged
✅ inputs: are optional — you can have workflow_dispatch with no inputs
✅ inputs appear as form fields in the GitHub UI
```

### What we proved today
```
Before: Actions tab showed NO "Run workflow" button
After:  "Run workflow" button appeared with staging/production dropdown
Manual trigger ran: build-and-test ✅ → security-scan ✅ → push skipped ✅
```

---

## Feature 2 — Matrix Builds

### What it does
Runs the same job multiple times with different parameters — simultaneously.

### Why it matters
```
Your app works on Python 3.11 but crashes on Python 3.12
Without matrix: you'd never know until a user reports it in production ❌
With matrix: caught automatically on every PR ✅
```

### How matrix works

```yaml
jobs:
  test-matrix:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
        os: [ubuntu-latest]
      fail-fast: false    # ← don't cancel others if one fails
```

```
This creates 3 jobs automatically:
Job 1: python-version=3.10, os=ubuntu-latest
Job 2: python-version=3.11, os=ubuntu-latest
Job 3: python-version=3.12, os=ubuntu-latest

All run IN PARALLEL — same time, not one after another
```

### Matrix with multiple dimensions

```yaml
matrix:
  python-version: ['3.10', '3.11', '3.12']
  os: [ubuntu-latest, windows-latest, macos-latest]
```

```
This creates 9 jobs (3 versions × 3 OS):
3.10 + ubuntu  |  3.10 + windows  |  3.10 + macos
3.11 + ubuntu  |  3.11 + windows  |  3.11 + macos
3.12 + ubuntu  |  3.12 + windows  |  3.12 + macos
```

### fail-fast explained

```yaml
fail-fast: false  # ← recommended for matrix
```

```
fail-fast: true  (default)
→ If Python 3.10 fails → cancel 3.11 and 3.12 immediately
→ You only know 3.10 failed — don't know about others

fail-fast: false  (recommended)
→ If Python 3.10 fails → 3.11 and 3.12 continue running
→ You see ALL failures at once
→ More useful — fix everything in one go
```

### What we proved today

```
Test Python 3.10 on ubuntu-latest  ✅ 12s
Test Python 3.11 on ubuntu-latest  ✅ 9s
Test Python 3.12 on ubuntu-latest  ✅ 12s

All 3 ran simultaneously → total time 17s
Sequential would be: 33s
Matrix saved: 16s per run (50% faster)
```

---

## Feature 3 — Reusable Workflows

### What it does
Define a workflow once — call it from any other workflow.
Like a function in programming — write once, use everywhere.

### Why it matters

```
Problem: 5 pipelines all need a health check
Without reusable: copy-paste 20 lines in each pipeline → 100 lines total
With reusable:    define once, call 5 times → 5 lines total

Update needed? Change 1 file — all 5 pipelines updated ✅
```

### How to define a reusable workflow

```yaml
# reusable-health-check.yml
on:
  workflow_call:          # ← this makes it reusable
    inputs:
      image-name:
        required: true
        type: string
      port:
        required: false
        type: string
        default: '8000'
    outputs:
      health-status:
        value: ${{ jobs.health-check.outputs.status }}
```

### How to call a reusable workflow

```yaml
# ci-advanced.yml
jobs:
  call-health-check:
    uses: ./.github/workflows/reusable-health-check.yml
    with:
      image-name: awspracttical57/devops-api:v1
      port: '8000'
```

### workflow_call vs workflow_dispatch

```
workflow_dispatch → triggered by human (button click)
workflow_call     → triggered by another workflow (called programmatically)
```

### What we proved today

```
ci-advanced.yml called reusable-health-check.yml
Reusable workflow:
  → Pulled Docker image from Docker Hub
  → Started container
  → Hit /health endpoint
  → Verified healthy response
  → Cleaned up container
Result: ✅ 20s
```

---

## 📋 Complete Workflow Structure After Day 15

```
.github/workflows/
├── docker-cicd.yml              ← Day 11/12 + Day 15 update
│   ├── trigger: push, PR, workflow_dispatch (NEW)
│   ├── job 1: build-and-test
│   ├── job 2: security-scan (needs job 1)
│   └── job 3: push-to-dockerhub (needs job 1+2, main only)
│
├── ci-advanced.yml              ← Day 15 NEW
│   ├── trigger: push, PR (Day-15/** paths)
│   ├── job 1: test-matrix (Python 3.10, 3.11, 3.12)
│   └── job 2: call-health-check (calls reusable workflow)
│
└── reusable-health-check.yml    ← Day 15 NEW
    ├── trigger: workflow_call only
    ├── inputs: image-name, port
    ├── outputs: health-status
    └── job: pull → run → curl /health → cleanup
```

---

## 🔧 Troubleshooting — errors and fixes

| Error | Why | Fix |
|-------|-----|-----|
| "Run workflow" button not showing | workflow_dispatch not on main branch | Merge branch to main first |
| `No file matched requirements.txt` | cache: pip needs requirements.txt | Add `cache-dependency-path` pointing to requirements.txt |
| `pull access denied` for Docker image | Wrong Docker Hub username | Double-check username — yours is `awspracttical57` (double t) |
| Matrix job cancelled suddenly | fail-fast: true (default) | Add `fail-fast: false` to strategy |
| Reusable workflow not found | Wrong path in `uses:` | Use `./.github/workflows/filename.yml` format |

---

## 🧠 Key Lessons from Day 15

> **Lesson 1:** `workflow_dispatch` only appears on the default branch. Always merge to main before expecting to see the manual trigger button.

> **Lesson 2:** Matrix builds run IN PARALLEL — not sequentially. 3 versions × 12s each = 12s total (not 36s). This is why matrix builds are used in every professional CI pipeline.

> **Lesson 3:** `fail-fast: false` is almost always what you want in matrix builds. See ALL failures at once — fix everything together.

> **Lesson 4:** Reusable workflows follow the DRY principle (Don't Repeat Yourself). If you're copy-pasting steps between workflows — extract them into a reusable workflow.

> **Lesson 5:** `workflow_call` (reusable) and `workflow_dispatch` (manual) are different triggers. One is called by humans, one by other workflows.

---

## 🎯 Interview questions — practice these

1. **What is the difference between `workflow_dispatch` and `workflow_call`?**
   > `workflow_dispatch` is triggered manually by a human clicking "Run workflow" in the GitHub UI — it can include input parameters like environment selection. `workflow_call` makes a workflow reusable — it can only be triggered by another workflow using the `uses:` keyword. One is for humans, one is for automation.

2. **What are matrix builds and when would you use them?**
   > Matrix builds run the same job multiple times with different parameter combinations — simultaneously in parallel. Use them when you need to test across multiple versions (Python 3.10/3.11/3.12), operating systems (ubuntu/windows/macos), or configurations. They catch compatibility issues automatically before they reach production.

3. **What does `fail-fast: false` do in a matrix strategy?**
   > By default `fail-fast: true` — if one matrix job fails, GitHub cancels all remaining jobs immediately. Setting `fail-fast: false` lets all matrix jobs complete regardless of failures, giving you a complete picture of which combinations pass and which fail. This is usually preferred so you can fix all issues in one go.

4. **What is a reusable workflow and why use one?**
   > A reusable workflow is defined with `on: workflow_call:` and can be called from other workflows using `uses:`. It follows the DRY principle — define once, use everywhere. If 5 pipelines need the same security scan, define it once and call it 5 times. Update one file and all pipelines get the update automatically.

5. **How do you pass data between jobs in GitHub Actions?**
   > Use `outputs:` at the job level and `steps.id.outputs.variable` at the step level. Set values with `echo "key=value" >> $GITHUB_OUTPUT`. Read them in other jobs with `needs.job-name.outputs.key`. For reusable workflows, outputs are declared in the `on: workflow_call: outputs:` section.

6. **What is `$GITHUB_STEP_SUMMARY` used for?**
   > It's a special file that GitHub reads and displays as a formatted summary on the workflow run page. Write markdown to it with `echo "## Title" >> $GITHUB_STEP_SUMMARY`. Useful for showing test results, build summaries, or deployment status in a readable format without digging into logs.

---

## ❓ Frequently asked questions

**Q: Can I use matrix builds for Docker too?**
Yes — matrix with different base images, different architectures (amd64/arm64), or different build arguments. Very common in multi-platform Docker builds.

**Q: How many parallel jobs can run in a matrix?**
GitHub Free tier: 20 concurrent jobs. GitHub Team/Enterprise: up to 500. Matrix is capped at 256 combinations per workflow.

**Q: Can a reusable workflow call another reusable workflow?**
Yes — up to 4 levels of nesting. But keep it simple — deep nesting is hard to debug.

**Q: What's the difference between `needs` and `uses`?**
`needs` creates a dependency between jobs in the SAME workflow. `uses` calls a completely separate reusable workflow file.

---

## 📁 Files in this folder

```
Day-15/
├── README.md          ← This file
├── devops_utils.py    ← Python utilities (system info, health check, format bytes)
├── test_devops.py     ← pytest tests for devops_utils
└── requirements.txt   ← pytest dependency for matrix builds
```

**New workflows added:**
```
.github/workflows/
├── ci-advanced.yml              ← Matrix builds + reusable workflow call
└── reusable-health-check.yml    ← Reusable health check for any Docker image
```

**Updated workflow:**
```
.github/workflows/
└── docker-cicd.yml    ← Added workflow_dispatch with environment input
```

---

## ⬅️ Previous Day
[Day 14 — Advanced Linux + Week 2 Mini Project](../Day-14/)

## ➡️ Next Day
[Day 16 — AWS CLI + boto3: Cloud Automation with Python](../Day-16/)

---

*Part of my [90-Day DevOps + AI Journey](../../README.md) — documented daily for beginners and professionals alike.*
