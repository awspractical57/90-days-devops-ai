# 📅 Day 8 — Docker Fundamentals: Images, Containers, Networking

## 🎯 What is today about?

Today we start Week 2 — Docker week.

We didn't just learn Docker commands. We understood Docker deeply — what problem it solves, how images and containers work, how containers talk to each other, and how to limit their resources.

By the end of today we ran a real web server, went inside it, proved container DNS works, and understood why companies use containers instead of VMs.

---

## 🏢 How real companies use Docker

| Company | Real use case |
|---------|-------------|
| **Netflix** | Runs 1000+ microservices in Docker containers — deploys 100s of times daily |
| **Uber** | Each microservice (payments, maps, notifications) runs in its own container |
| **Spotify** | Uses Docker to ensure same environment from developer laptop to production |
| **Amazon** | AWS ECS and EKS run billions of containers daily for customers worldwide |
| **Google** | Invented container technology — runs everything in containers internally |

---

## 🤔 What is Docker and why does it exist?

### The problem before Docker

```
Developer builds app on Mac
→ Python 3.11, specific libraries, config files
→ Works perfectly on their machine

Operations deploys to Linux server
→ Server has Python 3.8, different libraries
→ App crashes immediately
→ Hours of debugging
→ "But it works on MY machine!"

This happened EVERY deployment. EVERY company. EVERY team.
```

### How Docker solves it

```
Developer packages app WITH everything it needs:
→ Python 3.11 ✅
→ All libraries ✅
→ Config files ✅
→ Everything in one container ✅

Operations runs the container:
→ Same Python 3.11 ✅
→ Same libraries ✅
→ Works exactly the same ✅
→ "Works on MY machine" = "Works everywhere" ✅
```

### Docker vs Virtual Machine

```
Virtual Machine:                    Docker Container:
┌─────────────────┐                ┌─────────────────┐
│   Your App      │                │   Your App      │
├─────────────────┤                ├─────────────────┤
│   Full OS 1GB+  │ ← heavy        │   Libraries     │ ← MBs only
├─────────────────┤                ├─────────────────┤
│   Hypervisor    │                │   Docker Engine │
├─────────────────┤                ├─────────────────┤
│   Host OS       │                │   Host OS       │
└─────────────────┘                └─────────────────┘

VM  = full OS copy — heavy, slow, expensive
Container = just app + libraries — light, fast, cheap
```

**Real numbers from today:**
```
VM running nginx:        1GB+ RAM minimum
Container running nginx: 10MB RAM
```

100x more efficient. That's why companies run thousands of containers on one server.

---

## 🏗️ The 3 Core Concepts

### Image
- A read-only blueprint/template
- Built from a Dockerfile
- Never changes — always the same
- Stored in registries
- Example: `nginx:latest`, `ubuntu:22.04`, `python:3.11`

### Container
- A running instance created FROM an image
- Can be started, stopped, deleted
- Many containers from one image
- Has its own filesystem, network, processes
- Example: 5 nginx containers all from same nginx image

### Registry
- Where images are stored and shared
- Docker Hub = public registry (hub.docker.com)
- AWS ECR = private registry for companies
- You PULL images FROM registries
- You PUSH your images TO registries

### The relationship

```
Recipe (Image) → Bake → Cake (Container)

One recipe makes many cakes.
Burn one cake — recipe still exists.
Make more cakes anytime.

Docker Hub = Cookbook (stores all recipes)
```

---

## 📋 Essential Docker Commands

### Image commands

```bash
docker pull nginx              # Download image from Docker Hub
docker images                  # List all images on your machine
docker history nginx           # See image layers
docker rmi nginx               # Delete an image
docker image prune             # Delete unused images
```

### Container commands

```bash
# Run containers
docker run nginx                          # Run in foreground
docker run -d nginx                       # Run in background (detached)
docker run -d -p 8080:80 nginx            # With port mapping
docker run -d -p 8080:80 --name web nginx # With custom name
docker run -it ubuntu bash                # Interactive shell

# Manage containers
docker ps                      # List running containers
docker ps -a                   # List ALL containers
docker stop container-name     # Stop gracefully
docker start container-name    # Start stopped container
docker restart container-name  # Stop and start
docker rm container-name       # Delete container
docker container prune         # Delete all stopped containers

# Inspect and debug
docker logs container-name     # See container output
docker logs -f container-name  # Follow live logs
docker exec -it container bash # Open shell inside container
docker inspect container-name  # Full container details
docker stats container-name    # Live resource usage
```

### Resource limits

```bash
# Limit memory and CPU
docker run -d \
  --memory="256m" \
  --cpus="0.5" \
  --name limited-nginx \
  -p 8081:80 \
  nginx

# Verify limits applied
docker inspect limited-nginx | grep -E "Memory|NanoCpus"
```

---

## 🌐 Docker Networking

### Default networks

```bash
docker network ls
```

```
bridge  ← default — containers get private IPs, isolated from host
host    ← container shares host network — no isolation
none    ← no network — completely isolated
```

### Bridge network — default behavior

```
Docker Bridge Network (172.17.0.0/16):
├── mywebserver   → 172.17.0.2
└── limited-nginx → 172.17.0.3

Problem: containers find each other by IP only
If IP changes — connection breaks
```

### Custom network — production approach

```bash
# Create custom network
docker network create devops-network

# Run container on custom network
docker run -d --network devops-network --name my-app nginx
```

```
Custom Network (172.18.0.0/16):
├── network-nginx  → 172.18.0.2
└── test-container → 172.18.0.3

Advantage: containers find each other by NAME
ping network-nginx ← works! Docker resolves name to IP automatically
curl http://network-nginx ← works! Full HTTP by container name
```

### Container DNS — proved it works today

```bash
# From inside test-container on devops-network:
ping -c 2 network-nginx
# PING network-nginx (172.18.0.2) — resolved by NAME! ✅

curl http://network-nginx
# Welcome to nginx! — full HTTP response by name! ✅
```

**Why this matters:**
```
This is exactly how microservices work in production.
payment-service → calls → database (by name)
order-service → calls → payment-service (by name)
No hardcoded IPs. Docker handles DNS automatically.
```

### Networking modes comparison

| Mode | Use case | Container communication |
|------|---------|------------------------|
| bridge | Default — most containers | By IP only |
| custom | Microservices | By name (DNS built-in) |
| host | High performance | Shares host network |
| none | Maximum security | No network |

---

## 🔍 Image Layers — How Docker images are built

```bash
docker history nginx
```

```
Layer 1: debian base OS              87.4MB  ← foundation
Layer 2: ENV nginx version           0B      ← metadata only
Layer 3: RUN install nginx           86.7MB  ← biggest layer
Layer 4: COPY entrypoint scripts     ~50KB   ← small files
Layer 5: EXPOSE 80                   0B      ← metadata only
Layer 6: CMD nginx -g daemon off     0B      ← start command
```

**Key rules:**
- Only RUN, COPY, ADD create layers with actual size
- ENV, EXPOSE, CMD, LABEL = 0B metadata
- Layers are cached — unchanged layers don't rebuild
- Change bottom layer → rebuild everything above it
- Change top layer → only that layer rebuilds

**This is why Dockerfile order matters** — we'll learn this on Day 9.

---

## 🔧 Troubleshooting — common errors and fixes

| Error | Why | Fix |
|-------|-----|-----|
| `docker network ps` not found | Wrong command | Use `docker network ls` |
| Container exits immediately | No process running | Use `-it` flag or check CMD |
| Port already in use | Another service on that port | Change host port: `-p 8081:80` |
| `Permission denied` on docker | User not in docker group | `sudo usermod -aG docker $USER` |
| Image not found locally | Never pulled | Docker auto-pulls on `docker run` |
| Can't ping by name | On default bridge network | Use custom network for DNS |
| Container keeps restarting | App crashing inside | Check `docker logs container` |

---

## 🧠 Key Lessons from Day 8

> **Lesson 1:** Docker solves "works on my machine" permanently. The container IS the environment — same everywhere.

> **Lesson 2:** Image = blueprint (never changes). Container = running instance (temporary). Registry = storage (Docker Hub).

> **Lesson 3:** `docker exec -it container bash` is your most important debugging tool. When something is wrong inside a container — exec in and investigate.

> **Lesson 4:** Always use custom networks in production. Default bridge = IPs only. Custom network = DNS by name. Microservices need DNS.

> **Lesson 5:** Resource limits are not optional in production. Without them — one container can crash the entire server by consuming all memory.

---

## 🎯 Interview questions — practice these after Day 8

1. **What is the difference between a Docker image and a container?**
   > An image is a read-only template/blueprint that defines what a container will contain. A container is a running instance created from an image. One image can create many containers. Delete a container — the image still exists. It's like a recipe (image) and the dish you cook from it (container).

2. **What is the difference between Docker and a Virtual Machine?**
   > A VM runs a full OS (1GB+ RAM) on top of a hypervisor. A container shares the host OS kernel and only packages the app and its dependencies (MBs of RAM). Containers are 10-100x lighter than VMs, start in seconds vs minutes, and you can run thousands on one server vs tens of VMs.

3. **What does `docker run -d -p 8080:80 --name web nginx` do?**
   > Creates and starts a container named "web" from the nginx image. `-d` runs it in the background. `-p 8080:80` maps port 8080 on your machine to port 80 inside the container. Visit localhost:8080 to reach nginx running inside.

4. **What is the difference between Docker bridge and custom networks?**
   > Default bridge network — containers communicate by IP address only. Custom networks — Docker provides built-in DNS so containers find each other by name. In production always use custom networks so microservices can call each other by service name, not hardcoded IPs.

5. **How do you limit container resources?**
   > Use `--memory="256m"` to limit RAM and `--cpus="0.5"` to limit CPU. Without limits, one container can consume all server resources and crash other containers. Resource limits are mandatory in production Kubernetes and Docker environments.

6. **How do you debug a container that isn't working correctly?**
   > First check `docker logs container-name` for application errors. Then `docker exec -it container bash` to get a shell inside and investigate files, processes, and network. Use `docker inspect container` for full configuration details and `docker stats` for resource usage.

---

## ❓ Frequently asked questions

**Q: What happens to data when a container is deleted?**
Data inside a container is lost when it's deleted. To persist data — use Docker volumes (covered on Day 10). This is why databases should never run without volumes.

**Q: Can I run multiple containers from the same image?**
Yes — this is one of Docker's superpowers. Run 10 nginx containers from one nginx image. Each is isolated. This is how horizontal scaling works.

**Q: What is Docker Hub?**
Docker Hub is a public registry where anyone can push and pull Docker images. Like GitHub but for Docker images. Over 100,000 images available — nginx, ubuntu, python, postgres, redis, everything.

**Q: Does deleting a container delete the image?**
No — images and containers are separate. Delete all containers — images remain. You can always create new containers from existing images.

---

## 📚 Resources to go deeper

- [Docker Official Documentation](https://docs.docker.com/)
- [Docker Hub](https://hub.docker.com/)
- [Play with Docker — free online playground](https://labs.play-with-docker.com/)
- [Docker Networking Deep Dive](https://docs.docker.com/network/)

---

## 📁 Files in this folder

| File | What it is |
|------|-----------|
| `README.md` | This file — Day 8 complete guide |
| `docker-commands.md` | Personal Docker command reference |

---

## ⬅️ Previous Day
[Day 7 — Git Advanced + Week 1 Mini Project](../Day-7/)

## ➡️ Next Day
[Day 9 — Dockerfiles: Build Your Own Images](../Day-9/)

---

*Part of my [90-Day DevOps + AI Journey](../../README.md) — documented daily for beginners and professionals alike.*
