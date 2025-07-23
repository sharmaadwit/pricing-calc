#!/bin/bash
echo "Starting Flask app with gunicorn..."
exec gunicorn app:app -b 0.0.0.0:$PORT 