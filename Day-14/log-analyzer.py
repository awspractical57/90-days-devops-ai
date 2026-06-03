#!/usr/bin/env python3
"""
log-analyzer.py
Day 14 — Advanced Linux + Python
Analyzes log files and generates reports
"""

import subprocess
import json
from datetime import datetime
from collections import Counter


def analyze_log(log_file):
    """Analyze a log file using Python"""

    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        return {"error": f"Log file not found: {log_file}"}

    total_lines = len(lines)
    levels = Counter()
    errors = []
    warnings = []

    for line in lines:
        parts = line.strip().split()
        if len(parts) < 3:
            continue

        level = parts[2]
        levels[level] += 1

        if level == "ERROR":
            errors.append(line.strip())
        elif level == "WARN":
            warnings.append(line.strip())

    return {
        "file": log_file,
        "total_lines": total_lines,
        "level_counts": dict(levels),
        "error_count": levels.get("ERROR", 0),
        "warning_count": levels.get("WARN", 0),
        "errors": errors,
        "warnings": warnings,
        "health": "CRITICAL" if levels.get("ERROR", 0) > 2
                  else "WARNING" if levels.get("WARN", 0) > 0
                  else "OK"
    }


def run_linux_analysis(log_file):
    """Use Linux tools for additional analysis"""

    commands = {
        "total_lines": f"wc -l < {log_file}",
        "error_count": f"grep -c ERROR {log_file} || echo 0",
        "unique_ips": f"grep -oE '[0-9]{{1,3}}\\.[0-9]{{1,3}}\\.[0-9]{{1,3}}\\.[0-9]{{1,3}}' {log_file} | sort -u | wc -l",
        "first_entry": f"head -1 {log_file} | awk '{{print $1, $2}}'",
        "last_entry": f"tail -1 {log_file} | awk '{{print $1, $2}}'"
    }

    results = {}
    for key, cmd in commands.items():
        result = subprocess.run(cmd, shell=True,
                               capture_output=True, text=True)
        results[key] = result.stdout.strip()

    return results


def print_report(analysis, linux_stats):
    """Print a formatted report"""
    print("=" * 50)
    print("       LOG ANALYSIS REPORT")
    print("=" * 50)
    print(f"File:      {analysis['file']}")
    print(f"Health:    {analysis['health']}")
    print(f"Total:     {analysis['total_lines']} lines")
    print()
    print("Log Level Breakdown:")
    for level, count in sorted(analysis['level_counts'].items()):
        bar = "█" * count
        print(f"  {level:8} {count:3} {bar}")
    print()

    if analysis['errors']:
        print(f"❌ Errors ({analysis['error_count']}):")
        for error in analysis['errors']:
            print(f"   {error}")
        print()

    if analysis['warnings']:
        print(f"⚠️  Warnings ({analysis['warning_count']}):")
        for warning in analysis['warnings']:
            print(f"   {warning}")
        print()

    print(f"Linux Analysis:")
    print(f"  Unique IPs found: {linux_stats['unique_ips']}")
    print(f"  First entry: {linux_stats['first_entry']}")
    print(f"  Last entry:  {linux_stats['last_entry']}")

    # Save JSON report
    report = {**analysis, "linux_stats": linux_stats,
              "generated_at": datetime.now().isoformat()}
    filename = f"log-report-{datetime.now().strftime('%Y-%m-%d')}.json"
    with open(filename, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n✅ Report saved to {filename}")


if __name__ == "__main__":
    log_file = "sample.log"
    analysis = analyze_log(log_file)
    linux_stats = run_linux_analysis(log_file)
    print_report(analysis, linux_stats)
