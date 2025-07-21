#!/bin/bash

# Setup Cron Job for Daily Analytics Update
# This script sets up a cron job to run the analytics update daily at 8 PM IST

echo "Setting up daily analytics update cron job..."

# Get the absolute path to the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_PATH="$PROJECT_DIR/scripts/update_analytics_daily.py"

# Make the script executable
chmod +x "$SCRIPT_PATH"

# Create log directory
mkdir -p "$PROJECT_DIR/logs"

# Create the cron job entry (4 PM IST = 10:30 UTC)
# The cron job will run daily at 4 PM IST (10:30 UTC)
CRON_JOB="30 10 * * * cd $PROJECT_DIR && python3 $SCRIPT_PATH >> $PROJECT_DIR/logs/analytics_update.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "update_analytics_daily.py"; then
    echo "Cron job already exists. Removing old entry..."
    crontab -l 2>/dev/null | grep -v "update_analytics_daily.py" | crontab -
fi

# Add the new cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "Cron job set up successfully!"
echo "The analytics update will run daily at 8 PM IST (14:30 UTC)"
echo "Logs will be saved to: $PROJECT_DIR/logs/analytics_update.log"
echo ""
echo "To view current cron jobs: crontab -l"
echo "To edit cron jobs: crontab -e"
echo "To remove this cron job: crontab -e (then delete the line)"
echo ""
echo "To test the script manually, run:"
echo "python3 $SCRIPT_PATH" 