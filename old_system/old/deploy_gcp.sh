#!/bin/bash

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Python and pip
sudo apt-get install -y python3 python3-pip

# Install required system packages
sudo apt-get install -y git cron

# Set timezone to UTC-7
sudo timedatectl set-timezone America/Los_Angeles

# Create project directory
mkdir -p ~/google_news

cd ~/google_news

# Clone repository (replace with your actual repository URL)
git clone YOUR_REPOSITORY_URL .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements_004.txt

# Set up cron job for daily execution at 14:00 UTC-7 (2:00 PM)
(crontab -l 2>/dev/null; echo "0 14 * * * cd ~/google_news && source venv/bin/activate && python main_004.py >> scheduler.log 2>&1") | crontab -

# Make log directory
mkdir -p ~/google_news/logs

# Set permissions
chmod +x main_004.py

# Print cron jobs
crontab -l
