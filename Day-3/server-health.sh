#!/bin/bash

echo "Server Health Check"

echo "Current Date and Time:"
date

echo "Running Processes Count:"
ps aux | wc -l

echo "Nginx Status:"
systemctl is-active nginx

echo "Top 3 CPU Consuming Processes:"
ps aux --sort=-%cpu | head -4