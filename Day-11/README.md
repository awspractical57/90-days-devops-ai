# 📅 Day 11 — Docker CI/CD: Automated Build and Push Pipeline

## 🎯 What is today about?

Today we automated everything.

Before today — every Docker image push required 4 manual commands. After today — `git push` is the only command you ever need. GitHub Actions handles the rest automatically.

This is CI/CD for Docker — the standard workflow used by every professional engineering team.

---

## 🏢 How real companies use Docker CI/CD

| Company | Real use case |
|---------|-------------|
| **Netflix** | 1000+ microservices — every merge triggers automatic image build and deploy |
| **Uber** | Docker images built and pushed on every PR — never manually |
| **Shopify** | Image builds cached with layer caching — 10x faster CI/CD |
| **GitHub** | Uses GitHub Actions to build and push its own container images |
| **Amazon** | AWS CodePipeline builds Docker images on every commit to main |

---

## 🤔 The Problem We Solved Today

### Before — manual (painful)

```bash
# Every single time you update your app:
docker build -t myapp .
docker tag myapp username/myapp:latest
docker login
docker push username/myapp:latest
# 4 commands. Every. Single. Time.
# Easy to forget. Easy to make mistakes.
# What version did we push? Who pushed it? When?
```

### After — automated (professional)

```bash
git push
# That's it. GitHub Actions does everything else.
```

---

## ⚙️ The Complete Pipeline

### Pipeline flow

```
Developer pushes code
        │
        ▼
GitHub detects push/PR
        │
        ▼
┌──────────────────┐
│  build-and-test  │  ← runs on EVERY push and PR
│  • Build image   │
│  • Run container │
│  • Test /health  │
└────────┬─────────┘
         │ only if passed
         ▼
┌──────────────────┐
│ push-to-dockerhub│  ← runs ONLY on merge to main
│  • Login         │
│  • Build image   │
│  • Tag latest    │
│  • Tag v{number} │
│  • Push          │
└──────────────────┘
```

### Why 2 separate jobs?

```
PRs: build + test only
     → Don't push unreviewed code to Docker Hub
     → Catch bugs before they reach production

Merges to main: build + test + push
     → Code has been reviewed ✅
     → Tests pass ✅
     → Safe to publish ✅
```

---

## 📝 The Workflow File

```yaml
name: Docker CI/CD Pipeline

on:
  push:
    branches: [ main ]
    paths:
      - 'Day-9/python-ap/**'
      - '.github/workflows/docker-cicd.yml'
  pull_request:
    branches: [ main ]
    paths:
      - 'Day-9/python-ap/**'

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build Docker image
        run: |
          cd Day-9/python-ap
          docker build -t devops-api:test .
          echo "✅ Image built successfully"

      - name: Test the image
        run: |
          docker run -d -p 8000:8000 --name test-api devops-api:test
          sleep 3
          curl -f http://localhost:8000/health
          echo "✅ Health check passed"
          docker stop test-api
          docker rm test-api

  push-to-dockerhub:
    runs-on: ubuntu-latest
    needs: build-and-test
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ secrets.DOCKER_USERNAME }}/devops-api
          tags: |
            type=raw,value=latest
            type=raw,value=v${{ github.run_number }}

      - name: Build and push to Docker Hub
        uses: docker/build-push-action@v5
        with:
          context: Day-9/python-ap
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Summary
        run: |
          echo "🐳 Image pushed to Docker Hub!"
          echo "Tags: ${{ steps.meta.outputs.tags }}"
```

---

## 🔑 GitHub Secrets — keeping credentials safe

Secrets are encrypted environment variables stored in GitHub — never visible in logs or code.

### Setting up secrets

```
1. Go to github.com/your-repo/settings/secrets/actions
2. Click "New repository secret"
3. Add:
   Name:  DOCKER_USERNAME
   Value: your-dockerhub-username

   Name:  DOCKER_PASSWORD
   Value: your-dockerhub-access-token
```

### Using secrets in workflows

```yaml
# ✅ Correct — credentials never exposed
username: ${{ secrets.DOCKER_USERNAME }}
password: ${{ secrets.DOCKER_PASSWORD }}

# ❌ Wrong — never hardcode credentials
username: myusername
password: mypassword123
```

### Generate Docker Hub Access Token (recommended)

```
1. hub.docker.com → Account Settings → Security
2. New Access Token → Name: github-actions
3. Permission: Read & Write
4. Copy token → use as DOCKER_PASSWORD secret
```

Access tokens are safer than passwords — they can be revoked individually without changing your password.

---

## 🏷️ Image Tagging Strategy

```yaml
tags: |
  type=raw,value=latest        # always points to newest
  type=raw,value=v${{ github.run_number }}  # e.g. v42
```

**Why two tags?**

```
latest     → always the most recent build
           → what people pull by default
           → docker pull username/devops-api

v42        → specific build number
           → can roll back to exact version
           → docker pull username/devops-api:v42
```

---

## ⚡ Layer Caching in CI

```yaml
cache-from: type=gha    # pull cached layers from GitHub Actions cache
cache-to: type=gha,mode=max  # push new layers to cache
```

**Without caching:**
```
Every build downloads base image + all layers
Build time: ~3 minutes
```

**With caching:**
```
Only changed layers rebuild
Build time: ~30 seconds
10x faster CI/CD!
```

---

## ✅ What we proved today

```bash
# Changed app.py
"day": "Day 11 of 90 - CI/CD automated!"

# Pushed to GitHub → PR → merged
git push

# GitHub Actions ran automatically:
build-and-test     ✅  31s
push-to-dockerhub  ✅  29s

# Pulled new image
docker pull awspracttical57/devops-api:latest
curl http://localhost:8000/health

# Output:
{"day": "Day 11 of 90 - CI/CD automated!"}  ✅
```

Zero manual docker commands. One git push. Done.

---

## 🔧 Troubleshooting — common errors and fixes

| Error | Why | Fix |
|-------|-----|-----|
| `push access denied` | Wrong Docker Hub username in secret | Check DOCKER_USERNAME matches exactly |
| `push-to-dockerhub skipped on PR` | Working as intended | PRs don't push — only merges do |
| Pipeline not triggering | Files changed outside `paths` filter | Update `paths` or remove the filter |
| `needs: build-and-test` failing | Dependency job failed | Fix build-and-test first |
| Image shows old content after pull | Docker cached old image locally | `docker rmi image:latest` then pull again |
| `LF will be replaced by CRLF` | Windows line endings | Run `git config --global core.autocrlf true` |

---

## 🧠 Key Lessons from Day 11

> **Lesson 1:** Never push Docker images manually in a team. Automate it. Every manual step is a chance for human error.

> **Lesson 2:** PRs build and test only. Merges push to production. This single rule prevents unreviewed code from reaching Docker Hub.

> **Lesson 3:** GitHub Secrets keep credentials encrypted. Never hardcode passwords in YAML files — they're visible to everyone with repo access.

> **Lesson 4:** Layer caching makes CI pipelines 3-10x faster. Always enable `cache-from` and `cache-to` in Docker build steps.

> **Lesson 5:** Two tags per release — `latest` for easy access, `v{number}` for rollbacks. Always have a way to go back to a specific version.

---

## 🎯 Interview questions — practice these after Day 11

1. **What is the difference between CI and CD?**
   > CI (Continuous Integration) automatically builds and tests code on every push. CD (Continuous Delivery/Deployment) automatically delivers that tested code to a registry or environment. Our pipeline does both — builds and tests on every push (CI), deploys to Docker Hub on every merge (CD).

2. **How do you prevent credentials from being exposed in GitHub Actions?**
   > Use GitHub Secrets — encrypted key-value pairs stored in repository settings. Reference them as `${{ secrets.SECRET_NAME }}`. They're never printed in logs, never visible in the YAML file, and can be rotated without changing code.

3. **What does `needs: build-and-test` do in GitHub Actions?**
   > It creates a dependency between jobs. `push-to-dockerhub` will only start after `build-and-test` completes successfully. If `build-and-test` fails, `push-to-dockerhub` is automatically skipped. This enforces the rule: never push untested code.

4. **What is Docker Buildx and why use it?**
   > Docker Buildx is an extended build tool that supports multi-platform builds, build caching, and advanced Dockerfile features. Using `docker/setup-buildx-action@v3` in CI enables layer caching with `cache-from/cache-to`, which dramatically speeds up builds.

5. **How do you roll back a Docker image to a previous version?**
   > Using specific version tags. If `latest` is broken: `docker pull username/app:v41` where v41 is the last known good build. This is why tagging with build numbers is important — `latest` alone doesn't allow rollbacks.

6. **What is the `if` condition in GitHub Actions?**
   > `if: github.ref == 'refs/heads/main' && github.event_name == 'push'` means: only run this job when the event is a direct push to the main branch. This prevents the job from running on PRs or other branches.

---

## ❓ Frequently asked questions

**Q: What is a Docker Hub Access Token?**
An access token is a credential that gives specific permissions to Docker Hub without using your password. Safer because: scoped to specific permissions, can be revoked individually, doesn't expire with password changes. Always use tokens over passwords in CI/CD.

**Q: What does `type=gha` mean in cache settings?**
GHA = GitHub Actions. `cache-from: type=gha` tells Docker Buildx to look for cached layers in the GitHub Actions cache. `cache-to: type=gha,mode=max` saves all layers to cache for future builds. This persists cache between workflow runs.

**Q: Why use `docker/build-push-action` instead of plain `docker build`?**
The GitHub Action handles authentication, multi-platform builds, layer caching, and tagging automatically. Plain `docker build` + `docker push` requires manual auth and doesn't support caching in CI environments easily.

---

## 📚 Resources to go deeper

- [GitHub Actions Docker Guide](https://docs.github.com/en/actions/publishing-packages/publishing-docker-images)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [Docker Hub Access Tokens](https://docs.docker.com/security/for-developers/access-tokens/)
- [GitHub Encrypted Secrets](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions)

---

## 📁 Files changed today

| File | What changed |
|------|-------------|
| `.github/workflows/docker-cicd.yml` | Created Docker CI/CD pipeline |
| `Day-9/python-ap/app.py` | Updated day number to test pipeline |
| `Day-11/README.md` | This file |

---

## ⬅️ Previous Day
[Day 10 — Docker Volumes + Docker Compose](../Day-10/)

## ➡️ Next Day
[Day 12 — DevSecOps: Security Scanning with Trivy](../Day-12/)

---

*Part of my [90-Day DevOps + AI Journey](../../README.md) — documented daily for beginners and professionals alike.*
