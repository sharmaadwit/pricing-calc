# Pricing Calculator

A Flask-based pricing calculator for messaging services with dynamic inclusions, platform fees, and analytics.

## Features

- Dynamic pricing calculations
- Platform fee management
- Analytics and reporting
- Automated daily data updates

## Analytics Automation

The system includes automated analytics updates that run daily at 8 PM IST:

### Setup

1. **Install Dependencies**:
   ```bash
   python3 -m pip install pandas matplotlib seaborn psycopg2-binary
   ```

2. **Set up Cron Job**:
   ```bash
   ./scripts/setup_cron.sh
   ```

3. **Manual Test**:
   ```bash
   python3 scripts/update_analytics_daily.py
   ```

### What Gets Updated Daily

- **CSV Export**: Fresh data from PostgreSQL database
- **Analytics Charts**: New visualizations saved as PNG files
- **Summary Data**: JSON file with key metrics
- **Dashboard**: Real-time data in `/analyticsv2`

### Files Generated

- `analytics.csv` - Latest data export
- `static/analytics_summary.json` - Summary statistics
- `static/*_analytics.png` - Chart images
- `logs/analytics_update.log` - Execution logs

### Cron Schedule

- **Time**: 8 PM IST (14:30 UTC) daily
- **Command**: `python3 scripts/update_analytics_daily.py`
- **Logs**: `logs/analytics_update.log`

### Manual Execution

To run the analytics update manually:

```bash
cd /path/to/pricing-calc
python3 scripts/update_analytics_daily.py
```

### Monitoring

Check the logs to monitor the automation:

```bash
tail -f logs/analytics_update.log
```

View current cron jobs:

```bash
crontab -l
```

## Usage

1. Start the Flask application:
   ```bash
   python3 app.py
   ```

2. Access the pricing calculator:
   - Main calculator: `http://localhost:5000/`
   - Analytics v1: `http://localhost:5000/analytics`
   - Analytics v2: `http://localhost:5000/analyticsv2`

3. Export data manually:
   ```bash
   python3 scripts/export_to_csv.py
   ```

## Analytics Reports

### Analytics v2 (`/analyticsv2`)

Comprehensive dashboard with:
- **Temporal Analytics**: Usage patterns by hour, day, month
- **Customer Behavior**: CLV, churn, service preferences
- **Pricing Strategy**: Discounts, revenue trends
- **Geographic Intelligence**: Country-wise performance
- **Resource Utilization**: Manday efficiency, rate variations
- **Platform Analytics**: Feature usage, calculation routes

### Data Sources

- PostgreSQL database (primary)
- `analytics.csv` (exported data)
- Real-time summary statistics

## Configuration

### Database

The application connects to PostgreSQL using the connection string in `app.py`:

```python
DATABASE_URL = "postgresql://postgres:password@host:port/database"
```

### Analytics

Analytics configuration is in `scripts/update_analytics_daily.py`:

```python
DB_URL = "your_postgresql_connection_string"
CSV_PATH = "analytics.csv"
```

## Troubleshooting

### Cron Job Issues

1. Check if cron is running:
   ```bash
   sudo service cron status
   ```

2. View cron logs:
   ```bash
   grep CRON /var/log/syslog
   ```

3. Test script manually:
   ```bash
   python3 scripts/update_analytics_daily.py
   ```

### Analytics Dashboard Issues

1. Check if summary file exists:
   ```bash
   ls -la static/analytics_summary.json
   ```

2. Verify data export:
   ```bash
   wc -l analytics.csv
   ```

3. Check browser console for JavaScript errors

## Development

### Adding New Analytics

1. Add chart generation function in `scripts/update_analytics_daily.py`
2. Update the charts list in `generate_analytics_charts()`
3. Add corresponding chart in `templates/analyticsv2.html`

### Modifying Schedule

Edit the cron schedule in `scripts/setup_cron.sh`:

```bash
# Current: 8 PM IST daily
CRON_JOB="30 14 * * * ..."

# Example: Every 6 hours
CRON_JOB="0 */6 * * * ..."
```

## License

[Your License Here] 