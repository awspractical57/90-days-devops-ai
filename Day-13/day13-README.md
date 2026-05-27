# 📅 Day 13 — Python for DevOps: Fundamentals

## 🎯 What is today about?

Today we learned Python — but not Python for software developers.

Python for **DevOps engineers**. Every concept tied to real infrastructure use cases — server health checks, config management, log parsing, running shell commands, and calling APIs.

Python is the bridge between everything learned so far and everything coming next — boto3 for AWS automation, Kubernetes client, MLOps frameworks, and AI agents. All of it runs on Python.

---

## 🏢 How real companies use Python for DevOps

| Company | Real use case |
|---------|-------------|
| **Netflix** | Python scripts manage their entire AWS infrastructure — thousands of EC2 instances |
| **Instagram** | Django (Python) serves 2 billion users — DevOps team uses Python for all automation |
| **Dropbox** | Migrated 500 petabytes of data using Python automation scripts |
| **AWS** | boto3 (Python SDK) is the standard way to automate AWS — used by millions of engineers |
| **Kubernetes** | Official Python client for K8s — used for custom operators and automation |

---

## 🐍 Why Python for DevOps (not Bash)?

```
Bash is great for:             Python is better for:
→ Quick one-liners             → Complex logic
→ Simple file operations       → API calls
→ Chaining Linux commands      → JSON/YAML parsing
→ Cron jobs                    → Error handling
                               → AWS automation (boto3)
                               → Building tools and CLIs
```

**Use both.** Bash for simple tasks. Python for complex automation.

---

## 📚 Python Fundamentals — DevOps Context

### Variables and Data Types

```python
# Strings — server names, URLs, regions
server_name = "web-server-01"
region = "us-east-1"

# Numbers — ports, thresholds, counts
port = 8080
cpu_threshold = 80
instance_count = 3

# Booleans — status flags
is_running = True
is_healthy = False

# Lists — multiple servers, services
servers = ["web-01", "web-02", "web-03"]
services = ["nginx", "postgres", "redis"]

# Dictionaries — server configs, API responses
server_config = {
    "name": "web-server-01",
    "ip": "172.17.0.2",
    "port": 8080,
    "status": "running"
}

# f-strings — the modern way to format strings
print(f"Server: {server_name} on port {port}")
print(f"Config: {server_config['name']}")
```

> 💡 **Beginner tip:** Python variables don't need a type declaration. Just assign and use. `name = "hello"` not `String name = "hello"`.

---

### Conditions and Loops

```python
servers = ["web-01", "web-02", "web-03", "db-01"]
cpu_usage = {"web-01": 45, "web-02": 92, "web-03": 30, "db-01": 78}

for server in servers:
    cpu = cpu_usage[server]

    if cpu > 90:
        status = "🔴 CRITICAL"
    elif cpu > 70:
        status = "🟡 WARNING"
    else:
        status = "🟢 OK"

    print(f"{server}: CPU {cpu}% — {status}")

# List comprehension — filter in one line
healthy = [s for s in servers if cpu_usage[s] < 70]
print(f"Healthy servers: {len(healthy)}/{len(servers)}")
```

**Output:**
```
web-01: CPU 45% — 🟢 OK
web-02: CPU 92% — 🔴 CRITICAL
web-03: CPU 30% — 🟢 OK
db-01:  CPU 78% — 🟡 WARNING
Healthy servers: 2/4
```

---

### Functions

```python
def check_cpu(server_name, cpu_percent, threshold=80):
    """Check if CPU usage is above threshold"""
    if cpu_percent > threshold:
        return f"⚠️  {server_name}: CPU {cpu_percent}% above {threshold}%"
    return f"✅ {server_name}: CPU {cpu_percent}% — normal"

def count_by_status(servers_list):
    """Count servers grouped by status"""
    counts = {}
    for server in servers_list:
        status = server["status"]
        counts[status] = counts.get(status, 0) + 1
    return counts

# Usage
print(check_cpu("web-01", 95))          # above threshold
print(check_cpu("web-02", 45))          # normal
print(check_cpu("web-03", 75, threshold=70))  # custom threshold
```

> 💡 **Key concepts:** `def` creates a function. `"""docstring"""` documents it. Default parameters (`threshold=80`) make arguments optional.

---

### File Handling — configs and logs

```python
import json
import os
from datetime import datetime

# Write JSON config
config = {
    "app": "devops-api",
    "port": 8000,
    "servers": ["web-01", "web-02", "web-03"]
}

with open("config.json", "w") as f:
    json.dump(config, f, indent=2)

# Read JSON config
with open("config.json", "r") as f:
    loaded = json.load(f)
print(f"App: {loaded['app']}, Servers: {loaded['servers']}")

# Append to log file
log_entry = f"{datetime.now()} — Health check passed\n"
with open("app.log", "a") as f:
    f.write(log_entry)
```

> 💡 **`with open()` pattern** automatically closes the file even if an error occurs. Always use it — never `f = open()` without closing.

---

### Running Shell Commands

```python
import subprocess

def run_command(command):
    """Run a shell command and return output"""
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )
    return {
        "output": result.stdout.strip(),
        "error": result.stderr.strip(),
        "success": result.returncode == 0
    }

# Run real system commands
commands = ["date", "whoami", "df -h /"]

for cmd in commands:
    result = run_command(cmd)
    if result["success"]:
        print(f"✅ {cmd}: {result['output']}")
    else:
        print(f"❌ {cmd}: {result['error']}")
```

> 💡 **`returncode == 0`** means success in Linux. Any non-zero return code means failure — same as `$?` in Bash.

---

### HTTP Requests — calling APIs

```python
import urllib.request
import json

def check_url(url):
    """Check if a URL is reachable"""
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return {"url": url, "status": response.status, "reachable": True}
    except Exception as e:
        return {"url": url, "status": 0, "reachable": False, "error": str(e)}

# Check multiple endpoints
endpoints = ["http://httpbin.org/get", "http://httpbin.org/status/200"]

for url in endpoints:
    result = check_url(url)
    icon = "✅" if result["reachable"] else "❌"
    print(f"{icon} {url} — Status: {result['status']}")
```

---

## 🛠️ Today's Main Script — devops-monitor.py

Combines all concepts into one real DevOps tool:

```python
import subprocess
import json
import os
from datetime import datetime

def get_disk_usage():
    result = subprocess.run("df -h /", shell=True,
                           capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')
    parts = lines[1].split()
    return {"total": parts[1], "used": parts[2],
            "available": parts[3], "percent": parts[4]}

def get_memory_usage():
    result = subprocess.run("free -m", shell=True,
                           capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')
    parts = lines[1].split()
    total = int(parts[1])
    used = int(parts[2])
    percent = round((used / total) * 100, 1)
    return {"total_mb": total, "used_mb": used, "percent": f"{percent}%"}

def check_docker_containers():
    result = subprocess.run(
        "docker ps --format '{{.Names}}'",
        shell=True, capture_output=True, text=True
    )
    containers = [c for c in result.stdout.strip().split('\n') if c]
    return {"running": len(containers), "names": containers}

def generate_report():
    report = {
        "timestamp": datetime.now().isoformat(),
        "hostname": os.uname().nodename,
        "disk": get_disk_usage(),
        "memory": get_memory_usage(),
        "docker": check_docker_containers()
    }
    filename = f"report-{datetime.now().strftime('%Y-%m-%d')}.json"
    with open(filename, "w") as f:
        json.dump(report, f, indent=2)
    print(f"✅ Report saved to {filename}")

if __name__ == "__main__":
    generate_report()
```

**Output:**
```
========================================
   DEVOPS MONITOR REPORT
========================================
Host:    HARSHA
Time:    2026-05-26T12:38:05.807691
Disk:    1% used
Memory:  6.1% used
Docker:  0 containers running
✅ Report saved to report-2026-05-26.json
```

---

## 🐛 Errors Fixed Today — Python lessons learned

| Error | Cause | Fix |
|-------|-------|-----|
| `NameError: cpu_usage` | Typo `cpu_usages` vs `cpu_usage` | Variable names must match exactly |
| `SyntaxError: "name": name;` | Used `;` instead of `,` in dict | Python dicts use `,` between items |
| `NameError: Check_cpu` | Used capital C | Python is case-sensitive — `check_cpu` |
| `NameError: server_list` | Parameter name mismatch | Function definition must match call |
| `ValueError: invalid mode 'W'` | Used uppercase `"W"` | File modes are lowercase: `"w"`, `"r"`, `"a"` |
| `SyntaxError: else` missing `:` | Forgot colon | Every Python block ends with `:` |
| `TabError` | Mixed tabs and spaces | Use 4 spaces only — never tabs in Python |
| `SyntaxError: for c cin` | Missing space | `for c in` not `for cin` |
| `NameError: check_docket` | Typo docker → docket | Read error messages carefully |

> 💡 **The most important lesson:** Python's error messages tell you exactly what's wrong and on which line. Read them carefully — don't guess.

---

## 🔧 Python Golden Rules for DevOps

```python
# Rule 1: Use 4 spaces for indentation — NEVER tabs
def my_function():
    if True:        # 4 spaces
        print("ok") # 8 spaces

# Rule 2: Use f-strings for string formatting
name = "web-01"
print(f"Server: {name}")  # ✅ modern
print("Server: " + name)  # ❌ old style

# Rule 3: Use with for file operations
with open("file.txt", "r") as f:  # ✅ auto-closes
    content = f.read()

# Rule 4: Handle exceptions
try:
    result = risky_operation()
except Exception as e:
    print(f"Error: {e}")

# Rule 5: Use meaningful variable names
cpu = 45        # ❌ what CPU?
web01_cpu = 45  # ✅ clear

# Rule 6: returncode 0 = success
result = subprocess.run("ls", shell=True, capture_output=True)
if result.returncode == 0:
    print("Command succeeded")
```

---

## 🎯 Interview questions — practice these after Day 13

1. **What is the difference between a list and a dictionary in Python?**
   > A list is an ordered collection of items accessed by index: `servers[0]`. A dictionary is a key-value store accessed by key: `config["port"]`. Use lists when order matters and items are similar. Use dicts when you need to look up values by name — perfect for server configs and API responses.

2. **What does `subprocess.run()` do and why use it in DevOps?**
   > `subprocess.run()` executes shell commands from Python and captures their output. DevOps engineers use it to run `docker`, `kubectl`, `terraform`, `aws` CLI commands programmatically — combining the power of Linux tools with Python's logic, error handling, and data processing.

3. **What is `returncode == 0` and why does it matter?**
   > In Linux, every command exits with a return code. 0 means success. Non-zero means failure. `subprocess.run()` captures this as `returncode`. Checking it lets your Python script know if a command succeeded before continuing — essential for reliable automation.

4. **What is the `with` statement and why use it for files?**
   > `with open() as f` is a context manager that automatically closes the file when the block exits — even if an error occurs. Without it, you must manually call `f.close()` and risk leaving files open if an exception happens. Always use `with` for file operations.

5. **What is a TabError in Python and how do you fix it?**
   > Python uses indentation to define code blocks. A TabError means you mixed tabs and spaces in the same file — Python can't tell which level of indentation you mean. Fix by using only 4 spaces everywhere. Most code editors have a "convert tabs to spaces" option.

6. **What is `json.dump()` vs `json.dumps()`?**
   > `json.dump(data, file)` writes JSON directly to a file object. `json.dumps(data)` converts to a JSON string in memory. Similarly `json.load(file)` reads from a file, `json.loads(string)` parses a JSON string. DevOps engineers use `dump/load` for config files, `dumps/loads` for API responses.

---

## ❓ Frequently asked questions

**Q: Should I use Python 2 or Python 3?**
Always Python 3. Python 2 reached end-of-life in January 2020. Every modern tool, library, and company uses Python 3. Use `python3` and `pip3` commands.

**Q: What is `if __name__ == "__main__":`?**
This block only runs when you execute the script directly (`python3 script.py`). It doesn't run when the file is imported by another Python file. Best practice for scripts that should also be importable as modules.

**Q: What is the difference between `=` and `==` in Python?**
`=` assigns a value: `cpu = 80`. `==` compares values: `if cpu == 80`. Common mistake — using `=` in an if condition instead of `==`.

**Q: Why does Python use indentation instead of curly braces?**
Python's creator Guido van Rossum designed it for readability. Indentation forces consistent formatting — you can't write unreadable code with misaligned blocks. It also means less syntax clutter (no `{}` or `;`).

---

## 📚 Resources to go deeper

- [Python Official Tutorial](https://docs.python.org/3/tutorial/)
- [Python for DevOps — O'Reilly Book](https://www.oreilly.com/library/view/python-for-devops/9781492057987/)
- [Real Python — DevOps Articles](https://realpython.com/)
- [subprocess Documentation](https://docs.python.org/3/library/subprocess.html)

---

## 📁 Files in this folder

| File | What it does |
|------|-------------|
| `README.md` | This file — Day 13 complete guide |
| `variables.py` | Variables, data types, f-strings |
| `devops_checks.py` | Loops, conditions, list comprehension |
| `functions.py` | Reusable functions with parameters |
| `file-ops.py` | JSON config read/write, log appending |
| `run-commands.py` | Running shell commands from Python |
| `api-calls.py` | HTTP requests to check endpoints |
| `devops-monitor.py` | Complete monitoring script — all concepts |

---

## ⬅️ Previous Day
[Day 12 — DevSecOps: Security Scanning with Trivy](../Day-12/)

## ➡️ Next Day
[Day 14 — Advanced Linux + Week 2 Mini Project](../Day-14/)

---

*Part of my [90-Day DevOps + AI Journey](../../README.md) — documented daily for beginners and professionals alike.*
