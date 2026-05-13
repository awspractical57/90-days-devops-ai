# 📅 Day 9 — Dockerfiles: Build Your Own Docker Images

## 🎯 What is today about?

Yesterday we ran other people's images.
Today we build our own from scratch.

A Dockerfile is a text file with instructions that tell Docker exactly how to build an image — step by step, layer by layer.

By the end of today we built 3 real images, pushed them to Docker Hub, and understood multi-stage builds — the advanced pattern that makes production images smaller and more secure.

---

## 🏢 How real companies use Dockerfiles

| Company | Real use case |
|---------|-------------|
| **Netflix** | Every microservice has its own Dockerfile — built and pushed by CI/CD on every merge |
| **Uber** | Multi-stage builds reduce image sizes from 800MB to 20MB for Go services |
| **Shopify** | Dockerfiles pinned to specific versions — no surprises in production |
| **GitHub** | Uses multi-stage builds for GitHub Actions runners |
| **Airbnb** | Every team owns their Dockerfile — self-service deployments |

---

## 🤔 What is a Dockerfile?

A Dockerfile is a recipe for building a Docker image.

```
Dockerfile  →  docker build  →  Image  →  docker run  →  Container
(recipe)        (baking)        (cake)      (serving)     (eating)
```

Every line in a Dockerfile = one instruction = one layer in the image.

---

## 🏗️ Dockerfile Instructions — every one explained

```dockerfile
# ── BASE IMAGE ──────────────────────────────────────────
FROM ubuntu:22.04
# ALWAYS the first instruction
# Defines what you're building on top of
# Always pin a version — never use :latest in production
# :latest changes without warning and breaks builds

# ── METADATA ────────────────────────────────────────────
LABEL maintainer="harsha@email.com"
LABEL version="1.0"
LABEL description="My DevOps app"
# Adds information about the image
# Doesn't affect how the image works

# ── ENVIRONMENT VARIABLES ───────────────────────────────
ENV APP_HOME=/app
ENV PORT=8080
# Set variables available inside the container at runtime
# Your app can read these with os.environ.get("PORT")

# ── WORKING DIRECTORY ───────────────────────────────────
WORKDIR /app
# Sets the directory for all following commands
# Creates it if it doesn't exist
# Like running cd /app before every command

# ── COPY FILES ──────────────────────────────────────────
COPY . .
# COPY <from-your-machine> <to-container>
# COPY . . = copy everything here to WORKDIR
# COPY app.py . = copy just app.py to WORKDIR

# ── RUN COMMANDS ────────────────────────────────────────
RUN apt-get update && apt-get install -y python3
# Runs during BUILD time — when creating the image
# Each RUN = one layer
# Chain commands with && to reduce layers

# ── EXPOSE PORT ─────────────────────────────────────────
EXPOSE 8080
# Documents which port the app listens on
# Doesn't actually open the port
# Opening port happens with -p in docker run

# ── START COMMAND ───────────────────────────────────────
CMD ["python3", "app.py"]
# Runs when the container STARTS
# Only one CMD per Dockerfile — last one wins
# Always use array format — not string format
```

---

## 📝 What we built today

### 1. Custom nginx image — my-first-image

```dockerfile
FROM nginx:alpine

LABEL maintainer="awspractical57"
LABEL description="My DevOps journey webpage"
LABEL version="1.0"

RUN rm -rf /usr/share/nginx/html/*
COPY index.html /usr/share/nginx/html/

EXPOSE 80
```

**Build and run:**
```bash
docker build -t mydevops-journey:v1 .
docker run -d -p 8080:80 --name my-journey mydevops-journey:v1
curl http://localhost:8080
```

**What it does:** Serves a custom HTML page showing your DevOps learning journey — inside a Docker container.

---

### 2. Python HTTP API — python-ap

```dockerfile
FROM python:3.11-slim

LABEL maintainer="awspractical57"
LABEL description="DevOps journey Python API"

WORKDIR /app
ENV PORT=8000

COPY app.py .

EXPOSE 8000
CMD ["python3", "app.py"]
```

**Build and run:**
```bash
docker build -t devops-api:v1 .
docker run -d -p 8000:8000 --name devops-api devops-api:v1
curl http://localhost:8000
curl http://localhost:8000/health
```

**Health endpoint response:**
```json
{
  "status": "healthy",
  "day": "Day 9 of 90",
  "topic": "Dockerfiles",
  "python": "3.11.15",
  "hostname": "4ed523186a57"
}
```

The hostname is the container ID — this is how microservices report which instance handled a request.

---

### 3. Multi-stage build — multistage

```dockerfile
# Stage 1: Builder — has all build tools
FROM python:3.11 AS builder
WORKDIR /app
COPY app.py .

# Stage 2: Production — only what's needed to run
FROM python:3.11-slim AS production
WORKDIR /app
COPY --from=builder /app/app.py .
ENV PORT=8000
EXPOSE 8000
CMD ["python3", "app.py"]
```

---

## 🔑 Layer Caching — the most important performance concept

Every Dockerfile instruction creates a layer. Layers are cached.

```
First build:
[1/3] FROM python:3.11-slim    11s  ← downloaded
[2/3] WORKDIR /app              1s  ← created
[3/3] COPY app.py .             0s  ← copied
Total: 11 seconds

Second build (nothing changed):
CACHED [1/3] FROM python:3.11-slim  ← instant!
CACHED [2/3] WORKDIR /app           ← instant!
CACHED [3/3] COPY app.py .          ← instant!
Total: 0.3 seconds — 36x faster!

After changing app.py:
CACHED [1/3] FROM python:3.11-slim  ← cached
CACHED [2/3] WORKDIR /app           ← cached
[3/3] COPY app.py .                 ← rebuilt (changed)
Total: 3 seconds
```

### The golden rule of layer ordering

```dockerfile
# ❌ Bad order — requirements copied before code
# Changing code rebuilds requirements install (slow)
COPY . .
RUN pip install -r requirements.txt

# ✅ Good order — requirements copied first
# Changing code doesn't rebuild requirements install (fast)
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```

**Rule: Put things that change LEAST at the TOP. Put things that change MOST at the BOTTOM.**

---

## 🏗️ Multi-stage Builds — advanced pattern

Multi-stage builds use multiple FROM statements in one Dockerfile.

### Why multi-stage?

```
Problem: Build tools are huge, but you only need them to compile
Solution: Use a big image to build, copy just the result to a small image

Go application example:
Stage 1 (builder): golang:1.21    → 800MB (has compiler)
Stage 2 (production): alpine      → 10MB  (just the binary)
Final image: 10MB instead of 800MB!
```

### How it works

```dockerfile
# Stage 1: Builder
FROM python:3.11 AS builder    ← name this stage "builder"
WORKDIR /app
COPY app.py .
# install dependencies, compile code etc

# Stage 2: Production
FROM python:3.11-slim AS production
WORKDIR /app
COPY --from=builder /app/app.py .  ← copy FROM builder stage
# Only the files we need — nothing else
CMD ["python3", "app.py"]
```

---

## 🐳 Pushing to Docker Hub

```bash
# Login
docker login

# Tag your image with your Docker Hub username
docker tag mydevops-journey:v1 awspractical57/devops-journey:v1

# Push to Docker Hub
docker push awspractical57/devops-journey:v1

# Anyone can now pull and run your image
docker pull awspractical57/devops-journey:v1
docker run -d -p 8080:80 awspractical57/devops-journey:v1
```

**Our images on Docker Hub:**
- `awspractical57/devops-journey:v1` — custom nginx page
- `awspractical57/devops-api:v1` — Python health API

---

## 🔧 Troubleshooting — common errors and fixes

| Error | Why | Fix |
|-------|-----|-----|
| `requires 1 argument` | Missing `.` at end of build | Always end with `.`: `docker build -t name .` |
| `SyntaxError: bytes can only contain ASCII` | Unicode char in `b""` string | Use regular `-` not `—` (em dash) |
| `push access denied` | Wrong Docker Hub username | Check username — tag with exact username |
| `No such container` | Container already removed | It's fine — already cleaned up |
| `ConsistentInstructionCasing` warning | Mixed case in Dockerfile | Use ALL CAPS for instructions: `FROM` not `From` |
| Container exits immediately | App crashed on startup | Check `docker logs container-name` |
| `Couldn't connect to server` | Space in curl URL | No space: `curl http://localhost:8000/health` |

---

## 🧠 Key Lessons from Day 9

> **Lesson 1:** A Dockerfile is just a recipe. Every instruction = one layer. Layers are cached. Order matters.

> **Lesson 2:** Always pin versions in FROM. `FROM python:3.11-slim` not `FROM python:latest`. Latest changes without warning and breaks production builds.

> **Lesson 3:** Layer caching makes builds 10-36x faster. Put stable things at the top (base image, dependencies). Put changing things at the bottom (your code).

> **Lesson 4:** Multi-stage builds separate build-time tools from runtime. The production image only contains what's needed to run — nothing more. Smaller = faster + more secure.

> **Lesson 5:** Docker Hub is your image registry. Push once — anyone anywhere can pull and run your image with one command. That's the power of containerization.

---

## 🎯 Interview questions — practice these after Day 9

1. **What is a Dockerfile and what does it do?**
   > A Dockerfile is a text file containing instructions that Docker reads to build an image automatically. Each instruction creates a new layer in the image. The result is a portable, reproducible image that runs the same everywhere.

2. **What is the difference between CMD and RUN in a Dockerfile?**
   > RUN executes during image BUILD time — it creates a new layer. CMD executes when the container STARTS — it defines the default command. Example: `RUN apt-get install nginx` installs nginx during build. `CMD ["nginx", "-g", "daemon off;"]` starts nginx when the container runs.

3. **What is layer caching and why does it matter?**
   > Docker caches each layer. If a layer hasn't changed — it reuses the cached version instead of rebuilding. This makes subsequent builds much faster. It matters because CI/CD pipelines build images on every push — slow builds slow down deployments.

4. **What is a multi-stage build and when would you use it?**
   > Multi-stage builds use multiple FROM statements. The first stage builds/compiles the code (needs big tools). The second stage copies just the result into a smaller base image. Use it when build tools (compilers, package managers) aren't needed at runtime — results in dramatically smaller production images.

5. **What is the difference between COPY and ADD in a Dockerfile?**
   > Both copy files into the image. COPY is simple — copies files/directories. ADD does everything COPY does plus automatically extracts tar archives and supports URLs. Best practice: always use COPY unless you specifically need ADD's extra features.

6. **Why should you never use :latest tag in production Dockerfiles?**
   > The :latest tag points to whatever the most recent image is at pull time. This changes without warning — your build today might use a different version than yesterday's build. Pin specific versions (`python:3.11-slim`) so builds are reproducible and predictable.

---

## ❓ Frequently asked questions

**Q: What is `.dockerignore`?**
Like `.gitignore` but for Docker. Lists files Docker should NOT copy into the image — node_modules, .git, log files, secrets. Keeps images smaller and build context faster.

**Q: What is the difference between `FROM ubuntu` and `FROM ubuntu:22.04`?**
`FROM ubuntu` uses the latest tag — unpredictable. `FROM ubuntu:22.04` uses a specific version — always the same. Always use specific versions in production.

**Q: How do I reduce my Docker image size?**
Use slim or alpine base images, combine RUN commands with `&&`, use multi-stage builds, add a `.dockerignore` file, and remove package manager caches with `rm -rf /var/lib/apt/lists/*`.

**Q: Can I have multiple CMD instructions?**
You can write multiple but only the LAST one runs. If you need to run multiple commands on startup — use a shell script as the entrypoint.

---

## 📚 Resources to go deeper

- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Docker Hub](https://hub.docker.com/u/awspractical57)
- [Dockerfile Reference](https://docs.docker.com/engine/reference/builder/)

---

## 📁 Files in this folder

```
Day-9/
├── README.md                  ← This file
├── my-first-image/
│   ├── Dockerfile             ← Custom nginx image
│   └── index.html             ← DevOps journey webpage
├── python-ap/
│   ├── Dockerfile             ← Python slim image
│   └── app.py                 ← HTTP server with /health endpoint
└── multistage/
    ├── Dockerfile             ← Multi-stage build
    └── app.py                 ← Same app, cleaner build
```

**Images on Docker Hub:**
- `awspractical57/devops-journey:v1`
- `awspractical57/devops-api:v1`

---

## ⬅️ Previous Day
[Day 8 — Docker Fundamentals: Images, Containers, Networking](../Day-8/)

## ➡️ Next Day
[Day 10 — Docker Volumes + Docker Compose](../Day-10/)

---

*Part of my [90-Day DevOps + AI Journey](../../README.md) — documented daily for beginners and professionals alike.*
