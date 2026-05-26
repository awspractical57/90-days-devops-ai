servers = ["web-01", "web-02", "web-03", "db-01"]
cpu_usage = {"web-01": 45, "web-02": 92, "web-03": 30, "db-01": 78}

print ("======= Server Health Check =======")

for server in servers:
	cpu = cpu_usage[server]
	if cpu > 90:
	   status = " CRITICAL"
	elif cpu > 70:
	     status = "WARNING"
	else:
	   status = "OK"
	print (f"{server}:CPU {cpu}% - {status}")

# Count healthy servers
healthy = [s for s in servers if cpu_usage[s] < 70]
print (f"\n Healthy Servers: {len(healthy)}/{len(servers)}")
