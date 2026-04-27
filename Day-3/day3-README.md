# 📅 Day 3 — Server Health Monitoring

## 🎯 What is today about?

Today we dive into monitoring server health, a critical aspect of DevOps. We create a simple bash script to check key server metrics and service status, automating basic health checks that every DevOps engineer performs regularly.

---

## 🏥 Why Server Health Monitoring Matters

In DevOps, monitoring isn't just about reacting to problems — it's about preventing them. Server health checks help you:

- **Detect issues early** before they affect users
- **Understand system performance** and resource usage
- **Ensure services are running** as expected
- **Make informed decisions** about scaling and maintenance

Our script checks the most fundamental metrics: time, process count, service status, and CPU usage.

---

## 📜 The Server Health Script

The `server-health.sh` script performs these checks:

1. **Current Date and Time** - Ensures system clock is working
2. **Running Processes Count** - Shows system activity level
3. **Nginx Status** - Checks if the web server is active
4. **Top 3 CPU Consuming Processes** - Identifies resource-intensive processes

### How to run the script:

```bash
chmod +x server-health.sh
./server-health.sh
```

### Sample output:

```
Server Health Check
Current Date and Time:
Mon Apr 28 12:00:00 UTC 2026
Running Processes Count:
42
Nginx Status:
active
Top 3 CPU Consuming Processes:
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.1  12345  1234 ?        Ss   00:00   0:01 init
nginx      123  0.1  0.2  23456  2345 ?        S    00:01   0:00 nginx
user       456  0.0  0.1  34567  3456 pts/0    S+   00:02   0:00 bash
```

---

## 🔧 Prerequisites

- Linux environment (WSL2 on Windows works perfectly)
- Bash shell
- Nginx installed and running (or modify script for your services)
- Basic permissions to run system commands

### Installing Nginx (if needed):

```bash
sudo apt update
sudo apt install nginx
sudo systemctl start nginx
```

---

## 🚀 Next Steps

This is just the beginning of monitoring. In future days, we'll learn:
- Automated monitoring with tools like Prometheus
- Alerting when things go wrong
- Monitoring in cloud environments
- Building dashboards for visualization

Remember: Monitoring is not a one-time task — it's continuous vigilance that keeps your systems healthy and your users happy! 👀