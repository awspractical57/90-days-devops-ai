# 📅 Day 1 — DevOps + AI Fundamentals

## 🎯 What is today about?

Day 1 is about understanding the big picture before writing a single line of code.

Before we touch any tool or technology — we need to answer 3 questions:
- What is DevOps?
- What is AI doing in DevOps?
- Where do I start?

Today we also set up our learning infrastructure — GitHub repo, glossary, skills audit, and made our first public commitment on LinkedIn.

---

## 🏢 How real companies use DevOps

| Company | How they use DevOps |
|---------|-------------------|
| **Netflix** | Deploys code 1000s of times per day using CI/CD pipelines |
| **Amazon** | Deploys every 11.7 seconds using automated pipelines |
| **Google** | Manages millions of servers using IaC and automation |
| **Airbnb** | Uses Kubernetes to run 1000+ microservices reliably |
| **Spotify** | Built Backstage — an internal developer platform used by 1000s of companies |

> 💡 DevOps is not a startup thing or a big company thing. Every company that builds software needs it.

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

## 🏗️ DevOps Architecture — The Big Picture

This is what a modern DevOps system looks like. By Day 90 you will have built this:

```
Developer writes code
        │
        ▼
┌───────────────┐
│    GitHub     │  ← Version control (Day 5-7)
└───────┬───────┘
        │ push triggers
        ▼
┌───────────────┐
│ GitHub Actions│  ← CI/CD pipeline (Day 15-20)
│  Build        │
│  Test         │
│  Security scan│
│  Docker build │
└───────┬───────┘
        │ image pushed
        ▼
┌───────────────┐
│  Docker Hub   │  ← Container registry (Day 8-14)
│  / AWS ECR    │
└───────┬───────┘
        │ deploy
        ▼
┌───────────────┐
│  Kubernetes   │  ← Orchestration (Day 31-40)
│  on AWS EKS   │
└───────┬───────┘
        │ monitored by
        ▼
┌───────────────┐
│  Prometheus   │  ← Monitoring (Day 47-53)
│  + Grafana    │
└───────┬───────┘
        │ alerts trigger
        ▼
┌───────────────┐
│   AI Agent    │  ← Auto-remediation (Day 76-78)
│  auto-fixes   │
└───────────────┘
```

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

## 🔧 Common beginner mistakes on Day 1

| Mistake | Why it happens | Fix |
|---------|---------------|-----|
| Making GitHub repo private | Fear of judgment | Make it public — that's the whole point |
| Waiting until setup is perfect | Perfectionism | Ship it now, improve later |
| Skipping the skills audit | It feels unnecessary | It's your roadmap — do it honestly |
| Not posting on LinkedIn | Fear of what people think | Post anyway — nobody judges beginners who try |
| Trying to learn everything at once | Excitement overload | Trust the plan — one day at a time |

---

## ❓ Frequently asked questions

**Q: Do I need a computer science degree to learn DevOps?**
No. DevOps is a practical skill. What matters is what you can build — not what certificate you have.

**Q: Is DevOps hard to learn?**
It has a lot of tools. But each tool solves a specific problem. Once you understand the problem, the tool makes sense. We learn both together.

**Q: How long does it take to get a job in DevOps?**
With consistent daily practice and a strong portfolio — 3 to 6 months is realistic. That's exactly what this 90-day journey builds towards.

**Q: Do I need to know programming?**
Basic scripting (Bash, Python) is needed. We cover both from scratch in this journey — no prior experience required.

**Q: What's the difference between DevOps and Cloud Engineering?**
Cloud Engineers focus on building cloud infrastructure (AWS, Azure, GCP). DevOps Engineers focus on the software delivery process. In 2026 most companies expect you to know both — which is why we cover both.

---

## 🎯 Interview questions — practice these after Day 1

These are real questions asked in DevOps interviews. Practice answering them out loud.

1. **What is DevOps and why does it matter?**
   > Answer: DevOps is a culture and set of practices that brings development and operations together to deliver software faster and more reliably. It matters because it reduces deployment time from months to hours and catches problems before users see them.

2. **What is the difference between CI and CD?**
   > CI (Continuous Integration) = automatically building and testing code every time a developer pushes changes. CD (Continuous Delivery) = automatically deploying that tested code to production or staging.

3. **What is Infrastructure as Code?**
   > Writing your infrastructure (servers, networks, databases) as code files instead of clicking through a console. Benefits: version controlled, repeatable, auditable, automated.

4. **What is the difference between DevOps and Agile?**
   > Agile is about how teams plan and build software (sprints, user stories). DevOps is about how software gets deployed and operated. They complement each other — Agile builds it, DevOps ships it.

5. **What tools have you used in DevOps?**
   > Answer honestly based on what you know. Then add: "I'm currently on a 90-day journey learning Docker, Kubernetes, Terraform, GitHub Actions, and AI integration — here's my GitHub with daily progress."

---

## 📚 Resources to go deeper

- [DevOps Roadmap 2026 — roadmap.sh](https://roadmap.sh/devops)
- [What is DevOps — AWS](https://aws.amazon.com/devops/what-is-devops/)
- [GitHub Docs — Getting Started](https://docs.github.com/en/get-started)
- [The Phoenix Project — book about DevOps culture](https://www.goodreads.com/book/show/17255186-the-phoenix-project)

---

## 📁 Files in this folder

| File | What it is |
|------|-----------|
| `README.md` | This file — Day 1 complete guide |
| `glossary.md` | 50+ DevOps + AI terms explained in plain English |
| `skills-audit.md` | Honest skill gap analysis — starting from zero |

---

## ➡️ Next Day
[Day 2 — Linux Fundamentals + First Bash Script](../day-02/)

---

*Part of my [90-Day DevOps + AI Journey](../../README.md) — documented daily for beginners and professionals alike.*
