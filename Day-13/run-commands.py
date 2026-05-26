import subprocess
import sys

def run_command(command):
	"""Run a shell command and return output"""
	result = subprocess.run(
	   command,
	   shell=True,
	   capture_output=True,
	   text=True
	)
	return {
	  "command":command,
	  "output": result.stdout.strip(),
	  "error": result.stderr.strip(),
	  "success": result.returncode == 0
	}

commands = [
	"echo 'Hello from Python!'",
	"date",
	"whoami",
	"df -h /",
	"docker ps --format 'table {{.Names}}\t{{.Status}}'",
]

for cmd in commands:
	result = run_command(cmd)
	if result["success"]:
	   print (f"{result['command']}")
	   print (f"{result['output']}\n")
	else:
	   print (f"{result['command']}")
	   print (f"ERROR: {result['error']}\n")
