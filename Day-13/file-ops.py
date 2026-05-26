import json
import os
from datetime import datetime

config = {
     "app": "devops-api",
     "version": "1.0",
     "port": 8000,
     "debug": False,
     "servers": ["web-01","web-02","web-03"]
}

with open("config.json", "w") as f:
    json.dump(config, f, indent=2)
print(" Config file written")

with open("config.json", "r") as f:
    loaded_config = json.load(f)
print (f"App: {loaded_config['app']}")
print (f"Servers: {loaded_config['servers']}")

log_entry = f"{datetime.now()} - Health check passed\n"
with open("app.log","a") as f:
	f.write(log_entry)
print ("Log entry written")

with open("app.log", "r") as f:
    lines = f.readlines()
    print(f"Last log entry: {lines[-1].strip()}")

os.remove("config.json")
os.remove("app.log")
print ("Cleanup done")
