# 📅 Day 10 — Docker Volumes + Docker Compose

## 🎯 What is today about?

Today we solved two critical problems:

**Problem 1:** Data disappears when containers restart
**Solution:** Docker Volumes — data lives outside containers

**Problem 2:** Managing multiple containers is complex
**Solution:** Docker Compose — one file defines everything

By the end of today we ran a complete 3-service application stack with one command — and proved database data survives container deletion.

---

## 🏢 How real companies use these features

| Company | Real use case |
|---------|-------------|
| **Spotify** | Docker Compose for local development — every developer runs the full stack locally |
| **GitHub** | Volumes for persistent storage — database data survives deployments |
| **Airbnb** | Compose files define entire microservice stacks for testing |
| **Netflix** | Volumes for log persistence — logs survive container restarts |
| **Uber** | Compose for integration testing — spins up full stack, runs tests, tears down |

---

## 💾 Docker Volumes — Data Persistence

### The problem without volumes

```bash
# Start a database container
docker run -d --name mydb postgres

# Add some important data
docker exec -it mydb psql -U postgres -c "CREATE TABLE users (id INT);"

# Container crashes or gets deleted
docker rm -f mydb

# Start again
docker run -d --name mydb postgres

# ALL DATA IS GONE ❌
```

### The solution — volumes

```bash
# Data lives in the volume — not the container
docker run -d --name mydb -v db-data:/var/lib/postgresql/data postgres

# Container deleted
docker rm -f mydb

# New container, same volume
docker run -d --name mydb -v db-data:/var/lib/postgresql/data postgres

# DATA IS STILL THERE ✅
```

---

## 📦 3 Types of Docker Volumes

### Type 1 — Named Volumes (recommended for databases)

Docker manages the storage location. You just give it a name.

```bash
# Create
docker volume create mydata

# Use in container
docker run -d -v mydata:/app/data nginx

# List
docker volume ls

# Inspect
docker volume inspect mydata

# Delete
docker volume rm mydata

# Delete all unused volumes
docker volume prune
```

### Type 2 — Bind Mounts (recommended for development)

You choose the exact path on your machine.

```bash
# Mount your local folder into container
docker run -d \
  -v /home/harsha/myapp:/usr/share/nginx/html \
  -p 8080:80 \
  nginx

# Edit files locally → changes appear instantly in container
# No rebuild needed!
```

### Type 3 — tmpfs Mounts (RAM only)

Data stored in memory — lost when container stops. For sensitive data that shouldn't touch disk.

```bash
docker run -d --tmpfs /app/temp nginx
```

---

## 🐳 Docker Compose — Manage Multiple Containers

### Without Compose — painful

```bash
# 6 separate commands to start a basic stack
docker network create myapp-network
docker volume create db-data
docker run -d --name postgres --network myapp-network \
  -v db-data:/var/lib/postgresql/data \
  -e POSTGRES_PASSWORD=secret postgres:15
docker run -d --name redis --network myapp-network redis:alpine
docker run -d --name webapp --network myapp-network -p 8080:80 nginx
# Manage each separately, remember all flags...
```

### With Compose — simple

```bash
docker compose up -d    # start everything
docker compose down     # stop everything
```

---

## 📝 docker-compose.yml — The Complete File

```yaml
services:
  # Web server
  web:
    image: nginx:alpine
    container_name: devops-web
    ports:
      - "8080:80"
    volumes:
      - ./html:/usr/share/nginx/html    # bind mount
    networks:
      - devops-network
    depends_on:
      - api                              # start after api

  # Python API
  api:
    image: awspractical57/devops-api:v1
    container_name: devops-api
    ports:
      - "8000:8000"
    environment:
      - PORT=8000
    networks:
      - devops-network

  # Database
  db:
    image: postgres:15-alpine
    container_name: devops-db
    environment:
      - POSTGRES_DB=devopsdb
      - POSTGRES_USER=devops
      - POSTGRES_PASSWORD=devops123
    volumes:
      - db-data:/var/lib/postgresql/data  # named volume
    networks:
      - devops-network

volumes:
  db-data:          # declare named volumes here

networks:
  devops-network:   # declare networks here
    driver: bridge
```

### Key concepts in docker-compose.yml

| Key | What it does |
|-----|-------------|
| `services` | Each container you want to run |
| `image` | Which Docker image to use |
| `ports` | `host:container` port mapping |
| `volumes` | Mount volumes or bind mounts |
| `environment` | Environment variables |
| `networks` | Which network to join |
| `depends_on` | Start order — wait for another service |
| `volumes:` | Declare named volumes (bottom of file) |
| `networks:` | Declare networks (bottom of file) |

---

## 📋 Essential Docker Compose Commands

```bash
# Start all services in background
docker compose up -d

# Start and rebuild images
docker compose up -d --build

# Stop all services (keeps containers and volumes)
docker compose stop

# Stop and remove containers and networks
docker compose down

# Stop, remove containers, networks AND volumes ⚠️
docker compose down -v

# See running services
docker compose ps

# See logs from all services
docker compose logs

# Follow live logs
docker compose logs -f

# Logs from specific service
docker compose logs web
docker compose logs db

# Run command in a service
docker compose exec db psql -U devops

# Scale a service
docker compose up -d --scale api=3

# See resource usage
docker compose top
```

> ⚠️ **WARNING:** `docker compose down -v` deletes your volumes too. Never run this in production unless you want to lose all database data!

---

## ✅ What we proved today

### Volume persistence test

```bash
# Write data in container 1
docker run -it --name writer -v testdata:/data ubuntu bash
echo "This data will survive!" > /data/important.txt
exit

# Delete container 1
docker rm writer

# Read data in container 2 — same volume
docker run -it --name reader -v testdata:/data ubuntu bash
cat /data/important.txt
# Output: This data will survive! ✅
```

### Compose persistence test

```bash
docker compose up -d      # start stack
# database initialized with devopsdb

docker compose down       # stop everything
docker volume ls          # web-app_db-data still exists! ✅

docker compose up -d      # restart
docker exec -it devops-db psql -U devops -d devopsdb -c "\l"
# devopsdb still there! ✅ Data survived!
```

---

## 🔧 Troubleshooting — common errors and fixes

| Error | Why | Fix |
|-------|-----|-----|
| `no configuration file provided` | Wrong folder | Run `docker compose` from folder with `docker-compose.yml` |
| `version is obsolete` warning | Old attribute | Remove `version: '3.8'` line from compose file |
| `Port already in use` | Another service on that port | Change host port in `ports` section |
| `volume not found` | Volume doesn't exist | Docker Compose creates volumes automatically |
| `depends_on` not waiting | Service started but not ready | Use `healthcheck` with `condition: service_healthy` |
| Data lost after `down` | Used `down -v` | Never use `-v` flag with production data |
| `bind mount` changes not showing | Wrong path | Check path exists and matches exactly |

---

## 🧠 Key Lessons from Day 10

> **Lesson 1:** Without volumes — containers are stateless. Delete = data gone. Volumes decouple data from containers. Data persists independently.

> **Lesson 2:** Bind mounts are for development. Named volumes are for production. Never store database data without a named volume.

> **Lesson 3:** Docker Compose is not just for local development. Production systems use it too. It's the standard way to define multi-service applications.

> **Lesson 4:** `depends_on` controls start order — not readiness. The database container starts before the API — but the database might not be ready yet. Use health checks for true readiness.

> **Lesson 5:** `docker compose down -v` is dangerous in production. It deletes your volumes. Know the difference between `down`, `down -v`, and `stop`.

---

## 🎯 Interview questions — practice these after Day 10

1. **What is a Docker volume and why is it needed?**
   > Containers are ephemeral — all data inside is lost when the container is deleted. A Docker volume stores data outside the container on the host filesystem. The volume persists independently of the container lifecycle. Databases, logs, and user uploads must use volumes in production.

2. **What is the difference between a bind mount and a named volume?**
   > A bind mount maps a specific host path into the container — you control the location. A named volume is managed by Docker — Docker chooses where to store it. Bind mounts are great for development (edit code locally, see changes in container). Named volumes are better for production (Docker manages the path, easier to backup).

3. **What is Docker Compose and what problem does it solve?**
   > Docker Compose defines and runs multi-container applications using a single YAML file. Without it, you need separate `docker run` commands for each service with all flags manually specified. With Compose, `docker compose up -d` starts everything — services, networks, and volumes — defined in one place.

4. **What is the difference between `docker compose down` and `docker compose down -v`?**
   > `docker compose down` stops and removes containers and networks but keeps volumes intact — data is safe. `docker compose down -v` also deletes all volumes — ALL data is permanently lost. Never use `-v` in production unless you intend to wipe the database.

5. **What does `depends_on` do in Docker Compose?**
   > It controls the start order of services — the listed service starts before the current one. However, `depends_on` only waits for the container to start, not for the application inside to be ready. For true readiness (database accepting connections), combine `depends_on` with `healthcheck` and `condition: service_healthy`.

6. **How do you pass environment variables to a Docker Compose service?**
   > Use the `environment` key in the service definition. Values can be hardcoded (`POSTGRES_PASSWORD=secret`) or referenced from a `.env` file in the same directory. Never commit secrets to Git — use `.env` files and add them to `.gitignore`.

---

## ❓ Frequently asked questions

**Q: Where does Docker store named volume data?**
On Linux: `/var/lib/docker/volumes/volume-name/_data`. On Windows with Docker Desktop: inside the WSL2 filesystem. You can inspect the exact path with `docker volume inspect volume-name`.

**Q: Can two containers share the same volume?**
Yes — multiple containers can mount the same volume simultaneously. This is how you share data between services. Be careful with write conflicts if both containers write to the same files.

**Q: What happens to volumes when I run `docker compose down`?**
Named volumes defined in the `volumes:` section survive `docker compose down`. They're only deleted with `docker compose down -v` or `docker volume rm`.

**Q: Should I use Docker Compose in production?**
For simple single-server deployments — yes. For multi-server, high availability production — use Kubernetes instead. Docker Compose is excellent for local development, testing, and simple production setups.

---

## 📚 Resources to go deeper

- [Docker Volumes Documentation](https://docs.docker.com/storage/volumes/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Compose File Reference](https://docs.docker.com/compose/compose-file/)
- [Docker Compose Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

## 📁 Files in this folder

```
Day-10/
└── web-app/
    ├── docker-compose.yml    ← 3-service stack definition
    └── html/
        └── index.html        ← custom nginx page
```

---

## ⬅️ Previous Day
[Day 9 — Dockerfiles: Build Your Own Images](../Day-9/)

## ➡️ Next Day
[Day 11 — Docker + GitHub Actions CI/CD Pipeline](../Day-11/)

---

*Part of my [90-Day DevOps + AI Journey](../../README.md) — documented daily for beginners and professionals alike.*
