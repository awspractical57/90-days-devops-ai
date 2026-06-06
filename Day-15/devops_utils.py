import os
import platform
from datetime import datetime


def get_system_info():
    """Return basic system information."""
    return {
        "hostname": os.uname().nodename,
        "os": platform.system(),
        "python_version": platform.python_version(),
        "timestamp": datetime.now().isoformat()
    }


def check_health(service_name):
    """Check if a service name is valid."""
    if not service_name or not isinstance(service_name, str):
        return {"status": "error", "message": "Invalid service name"}
    return {
        "status": "healthy",
        "service": service_name,
        "checked_at": datetime.now().isoformat()
    }


def format_bytes(bytes_value):
    """Convert bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024
    return f"{bytes_value:.2f} PB"
