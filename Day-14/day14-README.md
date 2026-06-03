# 📅 Day 14 — Advanced Linux + Week 2 Mini Project

## 🎯 What is today about?

Two things today:

**Part 1 — Advanced Linux tools** that DevOps engineers use every day in production — `sed`, `awk`, `grep -E`, `find`, `xargs`. These are the tools that separate junior engineers from senior ones.

**Part 2 — Week 2 Mini Project** — a Dockerized Python DevOps Dashboard combining every skill from Week 2: Python + Docker + Security + CI/CD.

---

## 🏢 How real companies use these tools

| Tool | Real use case |
|------|-------------|
| `sed` | Update config files during deployments — change DEBUG=True to DEBUG=False |
| `awk` | Parse Kubernetes pod logs, extract specific columns from `kubectl get pods` |
| `grep -E` | Search across thousands of log files for specific error patterns |
| `find` | Locate and delete log files older than 30 days to free disk space |
| `xargs` | Run the same command against hundreds of servers in parallel |

---

## 🔧 Advanced Linux Tools

### sed — Stream Editor

`sed` edits text without opening a file. Essential for automated config updates in CI/CD pipelines.

```bash
# Replace text in output (doesn't modify file)
sed 's/8080/9090/' config.txt

# Replace text IN the file (-i = in-place)
sed -i 's/8080/9090/' config.txt

# Delete comment lines
sed '/^#/d' config.txt

# Delete empty lines
sed '/^$/d' config.txt

# Print specific lines (2 to 5)
sed -n '2,5p' /etc/passwd

# Real DevOps use — update app config during deployment
sed -i 's/DEBUG=True/DEBUG=False/' app.env
sed -i 's/DB_HOST=localhost/DB_HOST=prod-db.company.com/' app.env
```

**How `s/old/new/` works:**
```
s = substitute
/ = delimiter
old = pattern to find
new = replacement text

sed 's/8080/9090/' means:
"substitute 8080 with 9090"
```

---

### awk — Text Processing Powerhouse

`awk` processes text column by column. Every line of output has fields ($1, $2, $3...).

```bash
# Print specific columns
docker ps | awk '{print $1, $2}'          # ID and image
ps aux | awk '{print $1, $3, $11}'        # user, CPU%, command

# Filter by condition
ps aux | awk '$3 > 1.0 {print $11, $3}'  # processes >1% CPU
df -h | awk '$5 > "80%" {print $0}'       # disks >80% full

# NR = row number — skip header
free -m | awk 'NR==2 {print "Used: " $3 "MB of " $2 "MB"}'

# Calculate and display
df -h | awk 'NR>1 {print $1, "is", $5, "full"}'

# Count log entries
awk '{print $3}' sample.log | sort | uniq -c | sort -rn
```

**Field reference:**
```
Line: "web-01  running  172.17.0.2  8080"
       $1       $2       $3          $4

$0 = entire line
$1 = web-01
$2 = running
NF = last field
NR = current line number
```

---

### grep — Advanced Patterns

```bash
# Multiple patterns (OR)
grep -E "ERROR|WARN|CRITICAL" app.log

# Lines starting with 4 digits (timestamp)
grep -E "^[0-9]{4}" app.log

# Find IP addresses
grep -oE "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}" access.log

# Context around matches
grep -A 3 "ERROR" app.log   # 3 lines AFTER
grep -B 2 "ERROR" app.log   # 2 lines BEFORE
grep -C 2 "ERROR" app.log   # 2 lines AROUND

# Count and files
grep -c "ERROR" app.log     # count matches
grep -r "password" /etc/    # recursive search
grep -l "ERROR" *.log       # list files with matches
```

---

### find + xargs — Locate and Act

```bash
# Find by name
find /var/log -name "*.log"
find . -name "*.py"

# Find by size
find /var/log -size +100M              # files >100MB
find /tmp -size +10M -delete           # delete large files

# Find and execute
find . -name "*.sh" -exec chmod +x {} \;   # make executable
find /var/log -name "*.log" -mtime +30 -delete  # delete old logs

# xargs — pass results as arguments
find . -name "*.py" | xargs grep -l "subprocess"  # Python files using subprocess
find /tmp -name "*.log" | xargs rm -f             # delete all found logs
```

---

## 📊 Log Analysis Practice

### Sample log file analyzed today

```
2026-05-26 10:01:23 INFO  Server started on port 8000
2026-05-26 10:02:11 ERROR Failed to connect to database
2026-05-26 10:02:15 WARN  Retrying connection attempt 1/3
2026-05-26 10:02:25 ERROR Connection timeout after 3 retries
2026-05-26 10:03:45 ERROR Disk usage above 90% on /dev/sda1
...
```

### Linux commands that analyzed it

```bash
# Count errors
grep -c "ERROR" sample.log
# Output: 3

# Show all errors
grep "ERROR" sample.log

# Count by log level
awk '{print $3}' sample.log | sort | uniq -c | sort -rn
# Output:
#   5 INFO
#   3 ERROR
#   2 WARN

# Find unique IPs
grep -oE "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}" sample.log | sort -u
# Output:
# 192.168.1.10
# 192.168.1.11
```

---

## 🐍 Python Log Analyzer — log-analyzer.py

Combined Python + Linux tools for production-grade log analysis:

**What it does:**
- Reads any log file
- Counts by log level (INFO/WARN/ERROR)
- Lists all errors and warnings with full context
- Uses Linux commands for additional stats (unique IPs, timestamps)
- Saves a JSON report
- Shows health status: OK / WARNING / CRITICAL

**Output:**
```
==================================================
       LOG ANALYSIS REPORT
==================================================
File:      sample.log
Health:    CRITICAL
Total:     10 lines

Log Level Breakdown:
  ERROR      3 ███
  INFO       5 █████
  WARN       2 ██

❌ Errors (3):
   2026-05-26 10:02:11 ERROR Failed to connect to database
   2026-05-26 10:02:25 ERROR Connection timeout after 3 retries
   2026-05-26 10:03:45 ERROR Disk usage above 90% on /dev/sda1

Linux Analysis:
  Unique IPs found: 2
  First entry: 2026-05-26 10:01:23
  Last entry:  2026-05-26 10:04:30

✅ Report saved to log-report-2026-06-02.json
```

---

## 🐳 Week 2 Mini Project — DevOps Dashboard

### What it is

A Python HTTP server running inside Docker that provides system health information via REST API endpoints.

### Why it matters

Every production service needs health endpoints. Load balancers ping `/health` to know if a service is alive. Kubernetes uses health checks to decide whether to restart pods. Monitoring tools call `/metrics`. You built this pattern from scratch.

### Endpoints

| Endpoint | What it returns |
|----------|----------------|
| `/health` | Service status, version, day number |
| `/system` | Hostname, OS, Python version, timestamp |
| `/disk` | Total, used, available disk space |
| `/memory` | Total, used, free RAM in MB + percentage |
| `/dashboard` | All of the above in one response |

### Actual responses from today

```json
GET /health
{
  "status": "healthy",
  "version": "2.0",
  "day": "Day 14 of 90",
  "week": "Week 2 Complete"
}

GET /dashboard
{
  "system": {
    "hostname": "a94e173b31d9",
    "os": "Linux",
    "python": "3.11.15"
  },
  "disk": {
    "total": "1006.9G",
    "used": "6.9G",
    "percent_used": "1%"
  },
  "memory": {
    "total_mb": 7860,
    "used_mb": 605,
    "percent_used": "7.7%"
  },
  "status": "all systems operational"
}
```

### Security results

```
Trivy scan: devops-dashboard:v2
HIGH:     0 ✅
CRITICAL: 0 ✅
```

Zero vulnerabilities — achieved by:
- `python:3.11-alpine` base image
- `pip install --upgrade pip setuptools wheel`
- Non-root user (`appuser`)

### How to run it

```bash
# Build
docker build -t devops-dashboard:v2 .

# Run
docker run -d -p 8000:8000 --name dashboard devops-dashboard:v2

# Test
curl http://localhost:8000/health
curl http://localhost:8000/dashboard

# Stop
docker stop dashboard
docker rm dashboard
```

---

## 🐛 Bug fixed today

```python
# ❌ Wrong — isoformat() returns string, strings don't have strftime()
print(f"[{datetime.now().isoformat().strftime('%H:%M:%S')}] {args[0]}")

# ✅ Correct — call strftime() directly on datetime object
print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")
```

**Lesson:** `datetime.now()` returns a datetime object. `.isoformat()` converts it to a string. Once it's a string you can't call datetime methods on it anymore. Always check what type a method returns.

---

## 🧠 Key Lessons from Day 14

> **Lesson 1:** `awk` is a complete data processing tool. `ps aux | awk '$3 > 1.0 {print $11}'` filters processes using more than 1% CPU — in one command. Master awk and you can process any text output.

> **Lesson 2:** `sed -i` edits files in place without opening them. This is how CI/CD pipelines update config files during deployment — no human interaction needed.

> **Lesson 3:** Combine tools with pipes. `grep "ERROR" app.log | awk '{print $NF}' | sort | uniq -c | sort -rn | head -5` counts the top 5 unique error messages. Each tool does one thing. Pipes connect them.

> **Lesson 4:** Python and Linux tools complement each other. Use Linux commands inside Python with `subprocess.run()` to get the best of both worlds — Linux's powerful text tools and Python's logic and data structures.

> **Lesson 5:** Always check container logs when something doesn't work. `docker logs container-name` tells you exactly what went wrong inside the container — it's the first debugging step for any container issue.

---

## 🎯 Interview questions — practice these after Day 14

1. **What does `awk 'NR==2 {print $3}'` do?**
   > NR is the current line number. `NR==2` means "only process line 2". `$3` means the third field/column. So this prints the third column of the second line — commonly used to skip headers when parsing command output like `df -h` or `free -m`.

2. **What is the difference between `grep` and `grep -E`?**
   > `grep` uses basic regular expressions. `grep -E` uses extended regular expressions which support `|` (OR), `+`, `?`, `{}` without escaping. `grep -E "ERROR|WARN"` finds lines with either ERROR or WARN. With basic grep you'd need `grep "ERROR\|WARN"`.

3. **How do you find and delete log files older than 30 days?**
   > `find /var/log -name "*.log" -mtime +30 -delete`. `-mtime +30` means "modified more than 30 days ago". `-delete` removes them. In production, this runs as a cron job to prevent disk from filling up.

4. **What does `$NF` mean in awk?**
   > NF = Number of Fields. `$NF` refers to the last field in a line, regardless of how many fields there are. Useful when you always want the last column but lines have different lengths — like getting the last word in a log message.

5. **Why use `subprocess.run()` instead of `os.system()` in Python?**
   > `subprocess.run()` captures stdout and stderr separately, returns a result object with the exit code, and is more secure. `os.system()` just runs the command and prints output directly — you can't capture or process the output in Python.

6. **What is a REST API health endpoint and why does every service need one?**
   > A `/health` endpoint returns the service's current status as JSON. Load balancers call it every few seconds — if it returns non-200, the server is taken out of rotation. Kubernetes uses `livenessProbe` and `readinessProbe` to call health endpoints and restart unhealthy pods automatically.

---

## ❓ Frequently asked questions

**Q: When should I use awk vs Python for text processing?**
Quick one-liners with simple column extraction → awk. Complex logic, multiple files, need to save results, call APIs → Python. Both tools have their place. Senior engineers know when to use each.

**Q: What is the difference between `sed 's/a/b/'` and `sed 's/a/b/g'`?**
Without `g` (global), sed replaces only the FIRST occurrence on each line. With `g`, it replaces ALL occurrences. `echo "aaa" | sed 's/a/b/'` → `baa`. `echo "aaa" | sed 's/a/b/g'` → `bbb`.

**Q: How do I search for a pattern in all files recursively?**
`grep -r "pattern" /path/` searches all files recursively. Add `-l` to only list filenames. Add `--include="*.py"` to limit to specific file types: `grep -r "import subprocess" . --include="*.py"`.

---

## 📚 Resources to go deeper

- [GNU awk User's Guide](https://www.gnu.org/software/gawk/manual/gawk.html)
- [sed Tutorial](https://www.grymoire.com/Unix/Sed.html)
- [grep Manual](https://www.gnu.org/software/grep/manual/grep.html)
- [Python subprocess docs](https://docs.python.org/3/library/subprocess.html)

---

## 📁 Files in this folder

```
Day-14/
├── README.md              ← This file
├── sample.log             ← Practice log file
├── log-analyzer.py        ← Python + Linux log analysis tool
├── log-report-*.json      ← Generated analysis reports
└── config.txt             ← sed practice file

Week-2-Project/
├── app.py                 ← Python DevOps Dashboard server
└── Dockerfile             ← Alpine + non-root + pip upgrade
```

---

## ✅ Week 2 Complete!

| Day | Topic | Key deliverable |
|-----|-------|----------------|
| Day 8 | Docker fundamentals | Containers, networking, resource limits |
| Day 9 | Dockerfiles | Custom images, Docker Hub |
| Day 10 | Volumes + Compose | 3-service stack, data persistence |
| Day 11 | Docker CI/CD | Automated build and push pipeline |
| Day 12 | DevSecOps | Zero vulnerability image, Trivy in CI |
| Day 13 | Python basics | Variables, loops, functions, subprocess |
| Day 14 | Advanced Linux + Project | awk/sed/grep + DevOps Dashboard |

---

## ⬅️ Previous Day
[Day 13 — Python for DevOps: Fundamentals](../Day-13/)

## ➡️ Next Week
[Week 3 — AWS + boto3 + Advanced Automation](../Day-15/)

---

*Part of my [90-Day DevOps + AI Journey](../../README.md) — documented daily for beginners and professionals alike.*
