# 🚀 Week 1 Mini Project — DevOps Automation Toolkit

## 📋 Project Overview

This is the Week 1 capstone project of the 90-Day DevOps + AI learning journey.

It combines every skill learned in Week 1 into a single interactive DevOps automation toolkit — a menu-driven Bash script that performs real system monitoring and reporting tasks.

**Built in:** 7 days from scratch
**Tagged as:** v0.1.0
**CI validated:** GitHub Actions pipeline

---

## 🎯 What this project demonstrates

| Skill | Where used |
|-------|-----------|
| Linux commands | df, free, ping, systemctl |
| Variables | CHOICE, SERVICE, REPORT, STATUS |
| Conditions | case statement for menu |
| Loops | for loop checking services |
| User input | read -p for menu selection |
| File generation | dated report file |
| Git workflow | feature branch + PR |
| CI pipeline | GitHub Actions validates script |

---

## 🖥️ How to run

```bash
# Clone the repo
git clone https://github.com/awspractical57/90-days-devops-ai.git
cd 90-days-devops-ai/Week-1-Project

# Make executable
chmod +x devops-toolkit.sh

# Run it
./devops-toolkit.sh
```

---

## 📱 Menu options

```
==================================
     DevOps Automation Toolkit
==================================
1. System Health Check
2. Service Status
3. Network Check
4. Generate Report
5. Exit
==================================
```

### Option 1 — System Health Check
Shows memory usage and disk space across all mounted filesystems.

```
--- System Health Check ---
CPU and Memory:
              total   used   free
Mem:          7.7Gi  460Mi  7.2Gi
Disk Usage:
/dev/sde  1007G  2.0G  954G  1%  /
```

### Option 2 — Service Status
Loops through nginx, cron, and ssh — shows active or inactive for each.

```
--- Service Status ---
nginx: inactive
cron: active
ssh: inactive
```

### Option 3 — Network Check
Pings Google to verify internet connectivity. Shows latency and packet loss.

```
--- Network Check ---
PING google.com (142.250.77.110)
64 bytes: icmp_seq=1 ttl=117 time=38.2 ms
2 packets transmitted, 2 received, 0% packet loss
```

### Option 4 — Generate Report
Creates a dated text report file with disk and memory data.

```
--- Generating Report ---
Report saved to report-2026-05-07.txt
```

### Option 5 — Exit
Cleanly exits the toolkit.

```
Goodbye!
```

---

## 📝 The Script

```bash
#!/bin/bash
# ================================================
# devops-toolkit.sh
# Week 1 Mini Project — DevOps Automation Toolkit
# 90-Day DevOps + AI Journey
# ================================================

echo "=================================="
echo "     DevOps Automation Toolkit    "
echo "=================================="
echo "1. System Health Check"
echo "2. Service Status"
echo "3. Network Check"
echo "4. Generate Report"
echo "5. Exit"
echo "=================================="

read -p "Enter your choice (1-5): " CHOICE

case $CHOICE in
    1)
        echo ""
        echo "--- System Health Check ---"
        echo "CPU and Memory:"
        free -h
        echo "Disk Usage:"
        df -h
        ;;
    2)
        echo ""
        echo "--- Service Status ---"
        for SERVICE in nginx cron ssh; do
            STATUS=$(systemctl is-active $SERVICE)
            echo "$SERVICE: $STATUS"
        done
        ;;
    3)
        echo ""
        echo "--- Network Check ---"
        ping -c 2 -4 google.com
        ;;
    4)
        echo ""
        echo "--- Generating Report ---"
        REPORT="report-$(date +%Y-%m-%d).txt"
        echo "Report: $(date)" > $REPORT
        df -h >> $REPORT
        free -h >> $REPORT
        echo "Report saved to $REPORT"
        ;;
    5)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid option. Please enter 1-5"
        ;;
esac
```

---

## 🔧 Troubleshooting

| Issue | Fix |
|-------|-----|
| `ping: invalid argument` | Use `ping -c 2 -4 google.com` on WSL2 |
| `Permission denied` | Run `chmod +x devops-toolkit.sh` |
| Service shows inactive | Normal on WSL2 — services don't auto-start |
| Report not saving | Check folder write permissions |

---

## 🧠 What I learned building this

> Writing a menu-driven script feels simple — but it requires combining variables, conditions, loops, functions, and user input all working together. Each piece was learned on a different day. Putting them together on Day 7 proved the learning was real.

---

## 📈 What's next

Week 2 builds on this foundation with Docker — containerizing this toolkit so it runs on any machine without setup.

---

## ⬅️ Back to main roadmap
[90-Day DevOps + AI Journey](../README.md)

---

*Week 1 of the [90-Day DevOps + AI Journey](../README.md) — tagged as v0.1.0*
