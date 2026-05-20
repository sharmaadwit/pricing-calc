#!/bin/bash
echo "Starting Flask app with gunicorn..."
PORT="${PORT:-8080}"
LOG_LEVEL="${LOG_LEVEL:-info}"
echo "PORT environment variable: '$PORT'"
echo "Using port: ${PORT}, log level: ${LOG_LEVEL}"
exec gunicorn app:app -b "0.0.0.0:${PORT}" --log-level "${LOG_LEVEL}" --access-logfile - --error-logfile - --capture-output --timeout 120 