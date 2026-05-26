#Strings - server names, URLs, commands

server_name = "web-server-01"
region = "us-east-1"
command = "docker ps"

# Numbers - ports, counts, thresholds

port = 8000
cpu_threshold = 80
instance_count = 3

# Booleans - status checks

is_running = True
is_healthy = False

# Lists - multiple servers, services

servers = ["web-01", "web-02", "web-03"]
services = ["nginx", "postgres", "redis"]

# Dictionaries - server config, API responses

server_config = {
	"name": "web-server-01",
	"ip": "172.17.0.2",
	"port": 8080,
	"status": "running"
}

print(f"Server: {server_name}")
print(f"Port: {port}")
print(f"Config: {server_config}")
print(f"Server: {services}")


