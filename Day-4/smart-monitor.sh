#!/bin/bash

DISK_LIMIT=80

CPU_LIMIT=90


#----- Checking disk usage --- 

DISK=$(df / | tail -1 | awk '{print $5}' | tr -d %)

if [ $DISK -gt $DISK_LIMIT ]; then
	echo "WARNING: Disk Usage is ${DISK}% - above ${DISK_LIMIT}%"
else
	echo "Disk Usage is ${DISK}% - OK"
fi

if systemctl is-active --quiet ngix; then
	echo "Nginx is running"
else
	echo "Alert: Nginx is not running!"
fi

echo ""

echo "-------Service Status -----"

for SERVICE in ngix cron ssh; do
	STATUS=$(systemctl is-active $SERVICE)
	echo "$SERVICE: $STATUS"
done

LOG_FILE="health-$(date +%Y-%m-%d).log"
echo "Health check ran at $(date)" >> $LOG_FILE
echo "Log Saved to $LOG_FILE"
