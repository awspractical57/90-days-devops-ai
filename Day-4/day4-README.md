# 📅 Day 4 — Advanced Bash: Variables, Conditions, Loops & Cron Jobs

## 🎯 What is today about?

Today Bash scripting goes from "run commands" to "make decisions, repeat tasks, and schedule itself."

We learned 4 powerful concepts:
- **Variables** — store values and reuse them
- **Conditions** — make scripts think and decide
- **Loops** — repeat tasks automatically
- **Cron Jobs** — schedule scripts to run themselves

By the end of today our script runs automatically every 5 minutes — without us doing anything.

---

## 🏢 How real companies use these concepts

| Company | Real use case |
|---------|-------------|
| **Netflix** | Cron jobs run health checks every minute across thousands of servers |
| **Amazon** | Loop scripts check millions of EC2 instances for issues automatically |
| **GitHub** | Condition scripts detect failed builds and trigger alerts instantly |
| **Uber** | Variables store server thresholds — change once, updates everywhere |
| **Cloudflare** | Automated scripts restart failed services before users notice |

---

## 📦 Variables — store values, reuse everywhere

A variable is a named box that holds a value. Define it once, use it everywhere.

### Why variables matter

```bash
# Without variables — hardcoded everywhere
if [ $DISK -gt 80 ]; then alert; fi
if [ $CPU -gt 80 ]; then alert; fi
# Change threshold? Update every single line manually

# With variables — change once, updates everywhere
DISK_LIMIT=80
CPU_LIMIT=80
if [ $DISK -gt $DISK_LIMIT ]; then alert; fi
if [ $CPU -gt $CPU_LIMIT ]; then alert; fi
```

### Creating and using variables

```bash
#!/bin/bash

# Creating variables — NO spaces around =
NAME="DevOps Engineer"
DISK_LIMIT=80
SERVER="production-server-01"

# Using variables — prefix with $
echo "Hello $NAME"
echo "Disk limit: $DISK_LIMIT%"

# Store command output in a variable
CURRENT_DATE=$(date)
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | tr -d '%')

echo "Date: $CURRENT_DATE"
echo "Disk: $DISK_USAGE%"
```

### Special built-in variables

```bash
echo "Script name: $0"      # Name of the script
echo "Current user: $USER"  # Logged in username
echo "Home folder: $HOME"   # Home directory path
echo "Process ID: $$"       # Current process ID
```

> 💡 **Beginner tip:** NEVER put spaces around `=` when creating variables. `NAME="value"` works. `NAME = "value"` breaks.

---

## 🤔 Conditions — making scripts make decisions

Conditions let your script check something and decide what to do.

### Basic if/else structure

```bash
#!/bin/bash

DISK=$(df / | tail -1 | awk '{print $5}' | tr -d '%')

if [ $DISK -gt 80 ]; then
    echo "⚠️  WARNING: Disk is ${DISK}% — critical!"
elif [ $DISK -gt 60 ]; then
    echo "📊 Disk is ${DISK}% — getting full"
else
    echo "✅ Disk is ${DISK}% — all good"
fi
```

### Comparison operators

```bash
# Numbers
-eq   # equal to          [ $A -eq $B ]
-ne   # not equal         [ $A -ne $B ]
-gt   # greater than      [ $A -gt $B ]
-lt   # less than         [ $A -lt $B ]
-ge   # greater or equal  [ $A -ge $B ]
-le   # less or equal     [ $A -le $B ]

# Files
-f    # file exists       [ -f "/etc/nginx.conf" ]
-d    # directory exists  [ -d "/var/log" ]
-x    # file executable   [ -x "./script.sh" ]
```

### Golden rules for conditions

```
1. Always space after [
2. Always space before ]
3. Always ; before then
4. Always close with fi
```

```bash
# ✅ Correct pattern every time
if [ $VARIABLE -gt VALUE ]; then
    # do something
fi
```

---

## 🔄 Loops — repeat tasks automatically

Loops do the same thing multiple times — automatically.

### For loop — for each item in a list

```bash
#!/bin/bash

# Check multiple servers
for SERVER in web-01 web-02 web-03; do
    echo "Checking: $SERVER"
done

# Check multiple services
for SERVICE in nginx cron ssh mysql; do
    STATUS=$(systemctl is-active $SERVICE)
    echo "$SERVICE: $STATUS"
done

# Loop through numbers
for i in 1 2 3 4 5; do
    echo "Count: $i"
done
```

### While loop — repeat while condition is true

```bash
#!/bin/bash

COUNT=0
while [ $COUNT -lt 5 ]; do
    echo "Run number: $COUNT"
    COUNT=$((COUNT + 1))
    sleep 1
done
echo "Done!"
```

> 💡 **Beginner tip:** A loop that checks 10 servers takes the same effort as checking 1 server. That's the power of loops — scale without extra work.

---

## ⏰ Cron Jobs — Linux's alarm clock for scripts

Cron runs any script automatically at any schedule you define.

### Cron syntax

```
MIN   HOUR   DAY   MONTH   WEEKDAY   COMMAND
 *     *      *      *        *
```

### Reading cron schedules

```bash
* * * * *          # Every minute
0 * * * *          # Every hour
0 9 * * *          # Every day at 9:00 AM
0 9 * * 1          # Every Monday at 9:00 AM
*/5 * * * *        # Every 5 minutes
0 0 * * *          # Every day at midnight
0 9 1 * *          # 1st of every month at 9 AM
```

### Managing cron jobs

```bash
# Open cron editor
crontab -e

# View current cron jobs
crontab -l

# Remove all cron jobs
crontab -r
```

### Example cron job

```bash
# Run health check every 5 minutes and save output
*/5 * * * * /bin/bash ~/script.sh >> ~/health-log.txt 2>&1
```

> 💡 **What does `2>&1` mean?** It redirects error messages into the same log file as normal output. Without it — errors get lost silently.

---

## 📝 Today's Scripts

### Production-Server.sh — variables practice
Demonstrates creating and using variables to store server information and system data.

### smart-monitor.sh — full monitoring script
Uses all 4 concepts together:

```bash
#!/bin/bash
# ================================================
# smart-monitor.sh
# Day 4 of 90-Day DevOps + AI Journey
# Monitors disk usage and service status
# ================================================

DISK_LIMIT=80
CPU_LIMIT=90

# Check disk usage
DISK=$(df / | tail -1 | awk '{print $5}' | tr -d '%')

if [ $DISK -gt $DISK_LIMIT ]; then
    echo "⚠️  WARNING: Disk is ${DISK}% — above ${DISK_LIMIT}%"
else
    echo "✅ Disk is ${DISK}% — OK"
fi

# Check nginx service
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx is running"
else
    echo "❌ Alert: Nginx is not running!"
fi

# Loop through services
echo ""
echo "------- Service Status -----"
for SERVICE in nginx cron ssh; do
    STATUS=$(systemctl is-active $SERVICE)
    echo "$SERVICE: $STATUS"
done

# Save to dated log file
LOG_FILE="health-$(date +%Y-%m-%d).log"
echo "Health check ran at $(date)" >> $LOG_FILE
echo "✅ Log saved to $LOG_FILE"
```

**How to run:**
```bash
chmod +x smart-monitor.sh
./smart-monitor.sh
```

**Expected output:**
```
✅ Disk is 1% — OK
❌ Alert: Nginx is not running!

------- Service Status -----
nginx: inactive
cron: active
ssh: inactive
✅ Log saved to health-2026-05-01.log
```

---

## 🔧 Troubleshooting — common errors and fixes

| Error | Why it happens | Fix |
|-------|---------------|-----|
| `DISK_LIMIT: command not found` | Space around `=` | Remove spaces: `DISK_LIMIT=80` |
| `[: -gt: unary operator expected` | Variable is empty | Check command substitution works first |
| `syntax error near unexpected token` | Missing `;` before `then` | Add `;` → `if [ condition ]; then` |
| `[: too many arguments` | Missing quotes around variable | Use `"$VARIABLE"` instead of `$VARIABLE` |
| `command not found: ngnix` | Typo in service name | It's `nginx` not `ngnix` |
| Cron job not running | Wrong file path in crontab | Use full absolute path in cron |
| Log file not created | Wrong permissions | Check folder is writable with `ls -la` |

---

## 🧠 Key Lessons from Day 4

> **Lesson 1:** Variables make scripts maintainable. Change a threshold in one place — it updates everywhere.

> **Lesson 2:** `[` is a command in Bash — it always needs a space after it. This trips up everyone at first.

> **Lesson 3:** Loops are how one script manages 1000 servers as easily as 1. Scale without extra effort.

> **Lesson 4:** Cron jobs are how real DevOps automation works. Scripts that run themselves while you sleep.

> **Lesson 5:** `2>&1` in cron redirects errors to your log file. Without it — silent failures are impossible to debug.

---

## 🎯 Interview questions — practice these after Day 4

1. **What is the difference between `=` and `-eq` in Bash?**
   > `=` compares strings. `-eq` compares numbers. Use `-eq` for integers: `[ $NUM -eq 5 ]`. Use `=` for strings: `[ "$NAME" = "nginx" ]`.

2. **How do you schedule a script to run every day at midnight?**
   > Add to crontab: `0 0 * * * /bin/bash /path/to/script.sh`. The format is MIN HOUR DAY MONTH WEEKDAY — `0 0` means minute 0, hour 0 = midnight.

3. **What does `>> logfile.txt` do vs `> logfile.txt`?**
   > `>` overwrites the file every time — previous content is lost. `>>` appends to the file — previous content is kept. For logs always use `>>`.

4. **How do you loop through all `.log` files in a directory?**
   > `for FILE in /var/log/*.log; do echo $FILE; done` — the `*` wildcard matches all files ending in `.log`.

5. **What does `$?` mean in Bash?**
   > It holds the exit code of the last command. `0` means success. Anything else means failure. Use it to check if a command worked: `if [ $? -eq 0 ]; then echo "success"; fi`

6. **How do you pass arguments to a Bash script?**
   > Use `$1`, `$2`, `$3` for arguments. Example: `./script.sh hello world` — inside the script `$1` = "hello", `$2` = "world".

---

## ❓ Frequently asked questions

**Q: Why does Bash need spaces inside `[ ]`?**
Because `[` is actually a command in Linux — not just a bracket. Commands need spaces between them and their arguments. `[$VAR]` looks for a command called `[$VAR]` which doesn't exist.

**Q: What happens if my cron job fails silently?**
Without `2>&1` errors go to `/dev/null` (deleted). Always use `>> logfile.txt 2>&1` in cron so both output and errors are saved.

**Q: Can I run a cron job every second?**
No — cron's minimum interval is 1 minute. For sub-minute scheduling use `sleep` inside a while loop or use a tool called `systemd timers`.

**Q: How do I know if my cron job actually ran?**
Check your log file. If you used `>> logfile.txt 2>&1` — every run appends to the log. If the log is empty — cron didn't run or the path is wrong.

---

## 📚 Resources to go deeper

- [Bash Variables Guide](https://www.gnu.org/software/bash/manual/bash.html#Shell-Variables)
- [Crontab Guru — visual cron editor](https://crontab.guru/)
- [Bash If Statements](https://www.shellscript.sh/if.html)
- [Linux Loops Guide](https://www.cyberciti.biz/faq/bash-for-loop/)

---

## 📁 Files in this folder

| File | What it is |
|------|-----------|
| `README.md` | This file — Day 4 complete guide |
| `Production-Server.sh` | Variables practice script |
| `Production-Server02.sh` | Conditions + loops practice |
| `smart-monitor.sh` | Full monitoring script — all concepts combined |
| `health-2026-05-01.log` | Auto-generated log from cron job |

---

## ⬅️ Previous Day
[Day 3 — Linux Part 2: Processes, Services, Networking](../day-03/)

## ➡️ Next Day
[Day 5 — Git Deep Dive: Branching, Merging, Pull Requests](../day-05/)

---

*Part of my [90-Day DevOps + AI Journey](../../README.md) — documented daily for beginners and professionals alike.*
