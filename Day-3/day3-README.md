# 📅 Day 3 — Linux Part 2: Processes, Services, Networking + Writing Scripts Yourself

## 🎯 What is today about?

Today we go deeper into Linux — learning how to manage running programs, control system services, and debug network issues.

Most importantly — today we write a Bash script **without AI help**. This is where real learning happens.

---

## 🏢 How real companies use these skills

| Company | Real use case |
|---------|-------------|
| **Netflix** | Uses process monitoring to detect when streaming services crash and auto-restart them |
| **Uber** | Uses networking commands to debug latency between microservices |
| **GitHub** | Manages hundreds of services using systemctl across their server fleet |
| **Amazon** | Uses automated scripts to check server health across millions of EC2 instances |
| **Cloudflare** | Uses network diagnostics to identify routing issues affecting millions of users |

---

## ⚙️ Process Management

Every program running on Linux is a **process** — it has a unique ID called a PID (Process ID).

### How processes work

```
You run a command
        │
        ▼
Linux creates a Process
        │
        ├── Gives it a PID (e.g. PID 1234)
        ├── Allocates CPU and Memory
        └── Runs until finished or killed
```

### Essential process commands

```bash
# See all running processes
ps aux

# Find a specific process
ps aux | grep nginx

# Top 10 processes by CPU usage
ps aux --sort=-%cpu | head -10

# Live process monitor (press Q to exit)
top

# Better visual process monitor
sudo apt install htop -y
htop

# Kill a process by PID
kill 1234        # Politely ask it to stop
kill -9 1234     # Force kill immediately
```

> 💡 **When to use kill -9:** Only when a process is completely frozen and won't respond to a normal kill. Think of it as pulling the power plug — it works but it's not clean.

---

## 🔧 Service Management

A **service** is a process that runs in the background automatically — starting when the server boots and restarting if it crashes.

### Services vs Processes

```
┌─────────────────────────────────────────────┐
│                  Services                    │
│  • Run in background always                  │
│  • Start automatically on boot               │
│  • Restart automatically if they crash       │
│  • Examples: nginx, mysql, docker            │
├─────────────────────────────────────────────┤
│                  Processes                   │
│  • Run when you start them                   │
│  • Stop when you close them                  │
│  • Examples: your terminal, a script running │
└─────────────────────────────────────────────┘
```

### Essential service commands

```bash
# Install nginx to practice with
sudo apt install nginx -y

# Check service status
sudo systemctl status nginx

# Start a service
sudo systemctl start nginx

# Stop a service
sudo systemctl stop nginx

# Restart a service (stop + start)
sudo systemctl restart nginx

# Reload config without restarting
sudo systemctl reload nginx

# Start automatically on boot
sudo systemctl enable nginx

# Prevent starting on boot
sudo systemctl disable nginx

# Check if service is running (returns active or inactive)
systemctl is-active nginx
```

---

## 🌐 Networking Commands

Networking is where most DevOps debugging happens. These commands are your detective tools.

### The networking debugging flow

```
Something can't connect to something else
              │
              ▼
Is the server reachable?  →  ping server-ip
              │
              ▼
Is the port open?  →  ss -tulnp | grep PORT
              │
              ▼
Can we make an HTTP request?  →  curl http://server-ip
              │
              ▼
Is DNS resolving correctly?  →  nslookup domain.com
              │
              ▼
What is my IP address?  →  ip addr / hostname -I
```

### Essential networking commands

```bash
# Basic connectivity check
ping google.com              # Is this reachable?
ping -c 4 google.com         # Send exactly 4 pings then stop

# HTTP requests
curl https://google.com      # Make HTTP request, show response
curl -I https://google.com   # Show only HTTP headers
wget https://example.com/file.zip  # Download a file

# Network info
ip addr                      # Show all IP addresses
hostname -I                  # Quick IP address display

# Open ports
ss -tulnp                    # Show ALL open ports
ss -tulnp | grep :80         # Who is using port 80?
ss -tulnp | grep :443        # Who is using port 443?

# DNS lookup
nslookup google.com          # Basic DNS lookup
dig google.com               # Detailed DNS information
```

---

## 📝 Today's Script — server-health.sh

This script was written **without AI help** — by understanding and combining what was learned today and yesterday.

**What it checks:**
- ✅ Prints a health check title
- ✅ Shows current date and time
- ✅ Shows total running process count
- ✅ Shows nginx service status
- ✅ Shows top 3 CPU-consuming processes

**How to run it:**
```bash
chmod +x server-health.sh
./server-health.sh
```

---

## 🔧 Troubleshooting — common errors and fixes

| Error | Why it happens | Fix |
|-------|---------------|-----|
| `systemctl: command not found` | WSL2 doesn't run systemd by default | Run `sudo apt install systemd` or use `service nginx start` instead |
| `Failed to start nginx` | Port 80 already in use | Run `ss -tulnp \| grep :80` to find what's using it |
| `ping: connect: Network is unreachable` | No network in WSL2 | Restart WSL2: close terminal, run `wsl --shutdown` in PowerShell, reopen |
| `kill: (1234): Operation not permitted` | Process belongs to another user | Add `sudo` before kill: `sudo kill 1234` |
| `htop: command not found` | Not installed yet | Run `sudo apt install htop -y` |
| `curl: command not found` | Not installed | Run `sudo apt install curl -y` |
| `dig: command not found` | Not installed | Run `sudo apt install dnsutils -y` |
| Script runs but shows wrong output | Logic error in script | Read each line carefully, check command syntax |

---

## 🧠 Key Lessons from Day 3

> **Lesson 1:** Every program on Linux is a process. Processes have IDs. You can find them, monitor them, and kill them.

> **Lesson 2:** Services are processes that run automatically in the background. `systemctl` is how you manage them.

> **Lesson 3:** When something can't connect — follow the debugging flow: ping → port → curl → DNS. Don't guess, investigate.

> **Lesson 4:** Writing code without AI feels uncomfortable. That discomfort IS the learning. The struggle builds real understanding.

> **Lesson 5:** A script you wrote yourself — even if imperfect — is worth more than a perfect script you copy-pasted.

---

## 🎯 Interview questions — practice these after Day 3

1. **How do you find and kill a process that is consuming too much CPU?**
   > Use `ps aux --sort=-%cpu | head -5` to find the top CPU consumers and their PIDs. Then use `kill PID` to stop it gracefully or `kill -9 PID` to force kill it.

2. **What is the difference between `systemctl stop` and `systemctl disable`?**
   > `stop` stops the service right now but it will start again on next reboot. `disable` prevents it from starting automatically on boot but doesn't stop it right now. To do both: `systemctl stop nginx && systemctl disable nginx`.

3. **A developer says "I can't reach the app on port 8080." How do you debug this?**
   > First check if the app is running: `ps aux | grep app`. Then check if port 8080 is open: `ss -tulnp | grep :8080`. Then try to curl it locally: `curl http://localhost:8080`. Then check firewall rules. This is the systematic debugging approach.

4. **What is the difference between `ping` and `curl`?**
   > `ping` tests if a server is reachable at the network level (ICMP). `curl` tests if an HTTP service is responding at the application level. A server can respond to ping but not curl if the web server is down.

5. **How do you check what is running on a specific port?**
   > `ss -tulnp | grep :PORT` — this shows which process is listening on that port, its PID, and the service name.

6. **What does `ps aux` show?**
   > All running processes with their PID, CPU%, memory%, user, and command. `a` = all users, `u` = user-oriented format, `x` = include processes without a terminal.

---

## ❓ Frequently asked questions

**Q: What is the difference between a process and a service?**
A process is any running program. A service is a special type of process designed to run in the background automatically and restart if it crashes.

**Q: What happens if I kill the wrong process?**
If you kill a system process accidentally, Linux might become unstable or the terminal might crash. WSL2 can just be restarted. On a real server — be very careful and always double-check the PID before killing.

**Q: Why use `ping -c 4` instead of just `ping`?**
Without `-c 4`, ping runs forever until you press Ctrl+C. `-c 4` sends exactly 4 packets and stops automatically. Better for scripts and quick checks.

**Q: What is port 80 and port 443?**
Port 80 is standard HTTP (unencrypted web traffic). Port 443 is HTTPS (encrypted web traffic). When you visit a website — your browser connects to port 80 or 443 on the server.

---

## 📚 Resources to go deeper

- [Linux Process Management — Red Hat](https://www.redhat.com/sysadmin/linux-process-management)
- [systemctl Guide](https://www.digitalocean.com/community/tutorials/how-to-use-systemctl-to-manage-systemd-services-and-units)
- [Linux Networking Commands](https://www.geeksforgeeks.org/linux-networking-tools/)
- [Bash Scripting Tutorial](https://www.shellscript.sh/)

---

## 📁 Files in this folder

| File | What it is |
|------|-----------|
| `README.md` | This file — Day 3 complete guide |
| `server-health.sh` | Health check script — written without AI |

---

## ⬅️ Previous Day
[Day 2 — Linux Fundamentals + First Bash Script](../day-02/)

## ➡️ Next Day
[Day 4 — Linux Part 3: Advanced Scripting + Cron Jobs](../day-04/)

---

*Part of my [90-Day DevOps + AI Journey](../../README.md) — documented daily for beginners and professionals alike.*
