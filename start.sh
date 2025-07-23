#!/bin/bash
echo "Starting Flask app with gunicorn..."
echo "Port: $PORT"
exec gunicorn app:app -b 0.0.0.0:$PORT --log-level debug --access-logfile - --error-logfile - --capture-output 