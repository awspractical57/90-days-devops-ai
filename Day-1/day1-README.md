# 📅 Day 1 — DevOps + AI Fundamentals

## 🎯 What is today about?

Day 1 is about understanding the big picture before writing a single line of code.

Before we touch any tool or technology — we need to answer 3 questions:
- What is DevOps?
- What is AI doing in DevOps?
- Where do I start?

Today we also set up our learning infrastructure — GitHub repo, glossary, skills audit, and made our first public commitment on LinkedIn.

---

## 🤔 What is DevOps?

Imagine a company building a mobile app.

**Without DevOps:**
- Developers write code → throw it over the wall to operations team
- Operations team tries to deploy it → things break → blame game starts
- New features take weeks or months to reach users
- Bugs sit unfixed because nobody owns the process

**With DevOps:**
- Developers and operations work together from day one
- Code is automatically tested and deployed every time someone makes a change
- New features reach users in hours, not months
- Problems are caught early — before users see them

> 💡 **Simple definition:** DevOps is a way of working where building software and running software happen together, not separately.

---

## 🔄 The DevOps Lifecycle

Every DevOps engineer works around this cycle:

```
Plan → Code → Build → Test → Release → Deploy → Operate → Monitor
  ↑                                                              │
  └──────────────────────────────────────────────────────────────┘
                    (repeat continuously)
```

| Stage | What happens | Tools used |
|-------|-------------|------------|
| Plan | Decide what to build | Jira, Notion |
| Code | Write the application | Git, GitHub |
| Build | Compile and package the code | Docker, Maven |
| Test | Check if it works correctly | Jest, Selenium |
| Release | Prepare for deployment | GitHub Actions |
| Deploy | Put it on a server | Kubernetes, Terraform |
| Operate | Keep it running | Linux, AWS |
| Monitor | Watch for problems | Prometheus, Grafana |

---

## 🤖 What is AI doing in DevOps?

AI is changing DevOps in 3 ways:

### Way 1 — AI as your coding assistant
Instead of spending hours writing scripts, config files, and pipelines — AI writes the first draft in seconds. You review, understand, and improve it.

**Example:** "Write me a GitHub Actions pipeline that builds and tests a Docker image" → AI generates it in 10 seconds → you understand and customize it.

### Way 2 — AI watching your systems
Instead of engineers staring at dashboards at 2am — AI monitors your systems, detects problems automatically, and either fixes them or alerts the right person.

**Example:** CPU spikes suddenly → AI detects it's abnormal → automatically scales up servers → sends you a Slack message explaining what happened.

### Way 3 — DevOps for AI systems
Companies are building AI products (chatbots, recommendation engines, fraud detection). Someone needs to deploy those AI models, keep them running, and update them when they improve. That's an MLOps engineer — a DevOps engineer who works with AI systems.

---

## 🗺️ The 90-Day Plan

This journey is split into 3 phases:

### 🟢 Phase 1 — Foundation (Days 1–30)
Learn the core tools from scratch: Linux, Docker, GitHub Actions, CI/CD

### 🟡 Phase 2 — Integration (Days 31–60)
Learn Kubernetes, Terraform, Monitoring, and integrate AI into real workflows

### 🔴 Phase 3 — Advanced (Days 61–90)
MLOps, AI Agents, Capstone project, Portfolio and job readiness

---

## 📁 What we built today

### 1. GitHub Repository
A public repo where everything we build lives.
Every day gets its own folder. Every concept gets documented.
Anyone in the world can follow along.

🔗 [github.com/awspractical57/90-days-devops-ai](https://github.com/awspractical57/90-days-devops-ai)

### 2. Glossary — `glossary.md`
50+ key terms explained in plain English.

Covers: DevOps concepts, Containers, Cloud, Monitoring, AI/MLOps, Security, Networking.

This grows every week as we learn new things.

### 3. Skills Audit — `skills-audit.md`
An honest map of every skill we need to learn — starting from zero.

Updated every 30 days to show real progress.

---

## 🧠 Key Lessons from Day 1

> **Lesson 1:** DevOps is not a tool. It's a way of working — where building and running software happen together.

> **Lesson 2:** AI doesn't replace DevOps engineers. It makes them faster, smarter, and more valuable.

> **Lesson 3:** Learning in public is powerful. When you document your journey, you build a portfolio AND an audience at the same time.

> **Lesson 4:** Starting is the hardest part. Day 1 is done. That already puts you ahead of everyone who said "I'll start tomorrow."

---

## ❓ Common beginner questions

**Q: Do I need a computer science degree to learn DevOps?**
No. DevOps is a practical skill. What matters is what you can build — not what certificate you have.

**Q: Is DevOps hard to learn?**
It has a lot of tools. But each tool solves a specific problem. Once you understand the problem, the tool makes sense. We learn both together.

**Q: How long does it take to get a job in DevOps?**
With consistent daily practice and a strong portfolio — 3 to 6 months is realistic. That's exactly what this 90-day journey is building towards.

**Q: Do I need to know programming?**
Basic scripting (Bash, Python) is needed. We cover both from scratch in this journey — no prior experience required.

**Q: What's the difference between DevOps and Cloud Engineering?**
Cloud Engineers focus on building cloud infrastructure (AWS, Azure, GCP). DevOps Engineers focus on the software delivery process. In 2026 most companies expect you to know both — which is why we cover both.

---

## 📚 Want to learn more?

- [What is DevOps — AWS](https://aws.amazon.com/devops/what-is-devops/)
- [DevOps Roadmap 2026 — roadmap.sh](https://roadmap.sh/devops)
- [GitHub Docs — Getting Started](https://docs.github.com/en/get-started)

---

## 📁 Files in this folder

| File | What it is |
|------|-----------|
| `glossary.md` | 50+ DevOps + AI terms explained in plain English |
| `skills-audit.md` | Honest skill gap analysis — starting from zero |

---

## ➡️ Next Day
[Day 2 — Linux Fundamentals + First Bash Script](../day-02/)

---

*Part of my [90-Day DevOps + AI Journey](../../README.md) — documented daily for beginners and professionals alike.*
