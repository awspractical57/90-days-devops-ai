def check_cpu(server_name, cpu_percent, threshold=80):
	"""Check if CPU usage is above threshold"""
	if cpu_percent > threshold:
	   return f"{server_name}: CPU {cpu_percent}% above threshold {threshold}%"
	return f"{server_name}: CPU {cpu_percent}% - normal"

def format_server_info(name, ip, port, status):
	"""Format server information for display"""
	return {
	   "name": name,
	   "endpoint": f"http://{ip}:{port}",
	   "status": status,
	   "healthy": status == "running"
}

def count_by_status(server_list):
	"""Count servers by their status"""
	counts ={}
	for server in server_list:
	    status = server ["status"]
	    counts[status] = counts.get(status,0) + 1
	return counts

#Test the functions

print(check_cpu("web-01", 95))
print(check_cpu("web-02", 45))
print(check_cpu("web-03", 75, threshold=70))

server = format_server_info("api-server", "172.17.0.2", 8000, "running")
print (f"\nServer endpoint: {server['endpoint']}")
print (f"Healthy: {server['healthy']}")

servers = [
	{"name": "web-01", "status": "running"},
	{"name": "web-02", "status": "stopped"},
	{"name": "web-03", "status": "running"},
	{"name": "db-01", "status": "running"},
]
print (f"\nStatus counts: {count_by_status(servers)}")
