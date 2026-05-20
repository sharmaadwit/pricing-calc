#!/bin/bash
echo "Starting Flask app with gunicorn..."
PORT="${PORT:-8080}"
echo "PORT environment variable: '$PORT'"
echo "Using port: ${PORT}"
exec gunicorn app:app -b "0.0.0.0:${PORT}" --log-level debug --access-logfile - --error-logfile - --capture-output --timeout 120 