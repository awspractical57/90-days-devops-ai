#!/bin/bash
#Create a variable (no space around =) 
Name="Devops Engineer" 
Age=25
Server="Production Server"
# Use Variable in echo statement
echo "Hello $Name"
echo "server: $Server"
# Command output into variable
Current_Date=$(date)
Disk_Usage=$(df -h / | tail -1 | awk '{print $5}')
echo "Current Date: $Current_Date"
echo "Disk Usage: $Disk_Usage"
# $0 = Script name

# $1, $2, ... = arguments passed to the script

#$? = exit status of the last command (0 = success)

# $$ = process ID of the current script

# $USER = current logged in user

#HOME = home directory path echo "Script Name: $0"
echo "Script name=$0"

echo "Current User: $USER"
echo "Home folder: $HOME"
