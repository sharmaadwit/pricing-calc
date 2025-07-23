#!/bin/bash
echo "Starting Flask app with gunicorn..."
echo "PORT environment variable: '$PORT'"
echo "Using port: ${PORT:-8080}"
exec gunicorn app:app -b 0.0.0.0:${PORT:-8080} --log-level debug --access-logfile - --error-logfile - --capture-output 