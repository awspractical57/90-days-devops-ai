import urllib.request
import json

def check_url(url):
    """Check if a URL is reachable"""
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return {
                "url": url,
                "status": response.status,
                "reachable": True
            }
    except Exception as e:
        return {
            "url": url,
            "status": 0,
            "reachable": False,
            "error": str(e)
        }

# Check multiple endpoints
endpoints = [
    "http://httpbin.org/get",
    "http://httpbin.org/status/200",
    "http://httpbin.org/status/404",
]

print("=== Endpoint Health Check ===")
for url in endpoints:
    result = check_url(url)
    icon = "✅" if result["reachable"] else "❌"
    print(f"{icon} {url} — Status: {result['status']}")
