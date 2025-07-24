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

# Create the cron job entries for 11:00 AM, 2:00 PM, and 6:00 PM IST (05:30, 08:30, 12:30 UTC)
CRON_JOBS="30 5 * * * cd $PROJECT_DIR && python3 $SCRIPT_PATH >> $PROJECT_DIR/logs/analytics_update.log 2>&1
30 8 * * * cd $PROJECT_DIR && python3 $SCRIPT_PATH >> $PROJECT_DIR/logs/analytics_update.log 2>&1
30 12 * * * cd $PROJECT_DIR && python3 $SCRIPT_PATH >> $PROJECT_DIR/logs/analytics_update.log 2>&1"

# Remove any existing cron jobs for update_analytics_daily.py
if crontab -l 2>/dev/null | grep -q "update_analytics_daily.py"; then
    echo "Cron job already exists. Removing old entry..."
    crontab -l 2>/dev/null | grep -v "update_analytics_daily.py" | crontab -
fi

# Add the new cron jobs
(crontab -l 2>/dev/null; echo "$CRON_JOBS") | crontab -

echo "Cron jobs set up successfully!"
echo "The analytics update will run daily at 11:00 AM, 2:00 PM, and 6:00 PM IST (05:30, 08:30, 12:30 UTC)"
echo "Logs will be saved to: $PROJECT_DIR/logs/analytics_update.log"
echo ""
echo "To view current cron jobs: crontab -l"
echo "To edit cron jobs: crontab -e"
echo "To remove these cron jobs: crontab -e (then delete the lines)"
echo ""
echo "To test the script manually, run:"
echo "python3 $SCRIPT_PATH" 