#!/bin/bash

echo "=================================="
echo "	DevOps Automation Toolkit	"
echo "=================================="
echo "1. System Health Check"
echo "2. Service Status"
echo "3. Network Check"
echo "4. Generate Report"
echo "5. Exit"
echo "=================================="

read -p "Enter your choice:" CHOICE


case $CHOICE in
    1)
	echo ""
	echo "--- System Health Check---"
	echo "CPU and Memory"
	free -h
	echo "Disk Usage"
	df -h
	;;
    2)
	echo ""
	echo "--- Service Status---"
	for SERVICE in nginx cron ssh; do
	    STATUS=$(systemctl is-active $SERVICE)
	    echo "$SERVICE: $STATUS"
	done
	;;
    3)
	echo ""
	echo "--- Network Check ---"
	ping -c 2 -4 google.com
	;;
    4)
        echo ""
        echo "--- Generating Report ---"
        REPORT="report-$(date +%Y-%m-%d).txt"
        echo "Report: $(date)" > $REPORT
        df -h >> $REPORT
        free -h >> $REPORT
        echo "Report saved to $REPORT"
        ;;
    5)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid option. Please enter 1-5"
        ;;
esac



