#!/bin/bash
# =====================================================
# system-info.sh
# Day 2 of 90-Day DevOps + AI Journey
# Shows key system information in a readable format
# =====================================================

# Print a separator line for clean output
echo "========================================="

# Print the script title
echo "        SYSTEM INFORMATION REPORT        "

# Print another separator line
echo "========================================="

# Print an empty line for spacing
echo ""

# ---- HOSTNAME ----
# 'hostname' command returns the name of the machine
echo "🖥️  Hostname:"

# Run the hostname command and display the result
hostname

# Print empty line for spacing
echo ""

# ---- DATE AND TIME ----
# 'date' command returns the current system date and time
echo "📅  Current Date and Time:"

# Display the date in a readable format
date "+%A, %B %d %Y | %H:%M:%S"

# Print empty line for spacing
echo ""

# ---- CPU USAGE ----
# 'top -bn1' runs top once in batch mode (non-interactive)
# 'grep' filters only the line containing "Cpu"
# 'awk' extracts the idle percentage from that line
echo "⚙️  CPU Usage:"

# Extract CPU idle percentage and calculate usage
CPU_IDLE=$(top -bn1 | grep "Cpu(s)" | awk '{print $8}' | cut -d'%' -f1)

# Calculate CPU usage by subtracting idle from 100
CPU_USAGE=$(echo "100 - $CPU_IDLE" | bc 2>/dev/null || echo "See top command")

# Display the result
echo "CPU Usage: ${CPU_USAGE}%"

# Print empty line for spacing
echo ""

# ---- MEMORY USAGE ----
# 'free -h' shows memory in human-readable format (MB/GB)
echo "🧠  Memory Usage:"

# Run free command and skip the first header line
# Show total, used, and available memory
free -h | awk 'NR==2 {print "Total: " $2 "  |  Used: " $3 "  |  Available: " $7}'

# Print empty line for spacing
echo ""

# ---- DISK USAGE ----
# 'df -h' shows disk space in human-readable format
# We filter only the main filesystem line
echo "💾  Disk Usage:"

# Show disk usage for the root filesystem only
df -h | grep -E "^/dev|^overlay|Filesystem" | head -3

# Print empty line for spacing
echo ""

# ---- TOP 5 RUNNING PROCESSES ----
# 'ps aux' lists all running processes with details
# '--sort=-%cpu' sorts by CPU usage (highest first)
# 'head -6' takes first 6 lines (1 header + 5 processes)
echo "🔄  Top 5 Running Processes (by CPU):"

# Display header + top 5 processes sorted by CPU usage
ps aux --sort=-%cpu | awk 'NR<=6 {printf "%-10s %-6s %-6s %s\n", $1, $2, $3, $11}' | head -6

# Print empty line for spacing
echo ""

# Print closing separator
echo "========================================="

# Print completion message
echo "         Report generated successfully!  "

# Print final separator
echo "========================================="
