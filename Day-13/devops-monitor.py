import subprocess
import json
import os
from datetime import datetime

def get_disk_usage():
    result = subprocess.run("df -h /", shell=True, capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')
    parts = lines[1].split()
    return {
	"total": parts[1],
	"used": parts[2],
	"available": parts[3],
	"percent": parts[4]
    }

def get_memory_usage():
    result = subprocess.run("free -m", shell=True, capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')
    parts = lines[1].split()
    total = int(parts[1])
    used = int(parts[2])
    percent = round((used / total) * 100, 1)
    return {
	"total_mb": total,
	"user_mb": used,
	"percent": f"{percent}%"
    }

def check_docker_containers():
    result = subprocess.run(
	"docker ps --format '{{.Names}}'",
	shell=True, capture_output=True, text=True
    )
    containers = [c for c in result.stdout.strip().split('\n') if c]
    return {
	"running": len(containers),
	"names": containers
    }

def generate_report():
    report = {
	"timestamp": datetime.now().isoformat(),
	"hostname": os.uname().nodename,
	"disk": get_disk_usage(),
	"memory": get_memory_usage(),
	"docker": check_docker_containers()
    }
    
    filename = f"report={datetime.now().strftime('%Y-%m-%d')}.json"
    with open(filename, "w") as f:
        json.dump(report, f, indent=2)
    
    print ("=" * 40)
    print ("  DEVOPS MONITOR REPORT")
    print ("=" * 40)
    print (f"Host:	{report['hostname']}")
    print (f"Time:	{report['timestamp']}")
    print (f"Disk:	{report['disk']['percent']} used")
    print (f"Memory:	{report['memory']['percent']} used")
    print (f"Dcoker:	{report['docker']['running']} containers running")
    if report['docker']['names']:
        for name in report['docker']['names']:
            print (f"   -> {name}")
    print (f"\n Report saved to {filename}")

if __name__== "__main__":
    generate_report()
