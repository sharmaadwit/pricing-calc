web: gunicorn --log-level debug --access-logfile - --error-logfile - -w 4 -b 0.0.0.0:$PORT app:app
worker: sh -c "while true; do python3 scripts/update_analytics_daily.py; sleep 43200; done"