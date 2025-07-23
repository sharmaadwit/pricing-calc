#!/bin/bash
echo "Starting Flask app with gunicorn..."
echo "PORT environment variable: '$PORT'"
echo "Using port: 8080"
exec gunicorn app:app -b 0.0.0.0:8080 --log-level debug --access-logfile - --error-logfile - --capture-output 