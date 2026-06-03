#!/usr/bin/env/python3
"""
week 2 mini project - Devops Dashboard API
Combines: python + Docker + CICD + Security

"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import subprocess
import platform
from datetime import datetime

def get_system_info():
    """Get System information"""
    return {
        "hostname": os.uname().nodename,
        "os": platform.system(),
        "python": platform.python_version(),
        "timestamp": datetime.now().isoformat()
    }

def get_disk_info():
    """Get Dik Usage information"""
    result = subprocess.run("df -h /" , shell=True, capture_output=True, text=True)
    lines = result.stdout.strip().split("\n")
    parts = lines[1].split()
    return{
        "total": parts[1],
        "used": parts[2],
        "available": parts[3],
        "percent_used": parts[4]
    }
def get_memeory_info():
    """Get Memory Usage"""
    result = subprocess.run("free -m" , shell=True, capture_output=True, text=True)
    lines = result.stdout.strip().split("\n")
    parts = lines[1].split()
    total = int(parts[1])
    used = int(parts[2])
    return{
        "total_mb": total,
        "used_mb": used,
        "free_mb": total - used,
        "percent_used": f"{round((used/total)*100, 1)}%"
    }

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            response = {
                "status": "healthy",
                "version": "2.0",
                "day": "Day 14 of 90",
                "week": "week 2 Complete"
            }
            self.send_json(200, response)
        elif self.path == '/system':
            self.send_json(200, get_system_info())
        elif self.path == '/disk':
            self.send_json(200, get_disk_info())

        elif self.path == '/memory':
            self.send_json(200, get_memeory_info())
        elif self.path == '/dashboard':
            dashboard = {
                "system": get_system_info(),
                "disk": get_disk_info(),
                "memory": get_memeory_info(),
                "status": "all systems operational"
            }
            self.send_json(200, dashboard)
        
        else:
            self.send_json(404, {"error": "endpoint not found", "available_endpoints": ["/health", "/system", "/disk", "/memory", "/dashboard"]})
    
    def send_json(self, code, data):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(('0.0.0.0', port), DashboardHandler)
    print(f"DevOps Dashboard running on port {port}")
    print(f" Endpoints available: /health, /system, /disk, /memory, /dashboard")
    server.serve_forever()
    
    