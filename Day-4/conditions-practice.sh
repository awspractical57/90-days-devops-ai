#!/bin/bash

Disk_Usage=$(df / | tail -1 | awk '{print $5}' | tr -d '%')

if [ $Disk_Usage -gt 80 ]; then 
	echo "WARNING: Disk usage is ${Disk_Usage}% - above 80%!"
elif [ $Disk_Usage -gt 60 ]; then
	echo "Disk usage is ${Disk_Usage}% -getting full"
else
	echo "Disk Usage is ${Disk_Usage}% - all good "
fi

echo ""

echo "----- Checking service ------"

for SERVICE in nginx cron ssh; do
	STATUS=$(systemctl is-active $SERVICE)
	echo "$SERVICE: $STATUS"
done


LOG_FILE="health-$(date +%Y-%m-%d).log"
echo "Health Check Ran at $(date)" >> $LOG_FILE
echo "Disk: ${Disk_Usage}%" >> $LOG_FILE
echo "LOG Saved to $LOG_FILE"
