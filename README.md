# Pricing Calculator

A modern, Flask-based pricing calculator for messaging services with advanced UI, dynamic pricing calculations, and comprehensive analytics.

## 🚀 Features

### Core Functionality
- **Multi-step Pricing Calculator** - Intuitive 3-step process (Volumes → Pricing → Results)
- **Dual Pricing Models** - Volume Route (pay-per-use) and Committed Amount Route (prepaid bundles)
- **Real-time Calculations** - Dynamic pricing with instant updates
- **Multi-currency Support** - INR, USD with region-specific pricing
- **Platform Fee Management** - Transparent fee structure

### Advanced UI/UX
- **Modern Design** - Clean, responsive interface with gradient backgrounds
- **Progress Indicator** - Visual step tracking through the calculator
- **Bundle Comparison** - Side-by-side comparison of lower and upper bundle options
- **Required Amount Analysis** - Detailed breakdown of actual requirements
- **Interactive Forms** - Real-time validation and formatting

### Analytics & Reporting
- **Comprehensive Analytics** - Temporal, customer, pricing, and geographic insights
- **Automated Daily Updates** - Scheduled data refresh at 8 PM IST
- **Visual Dashboards** - Interactive charts and graphs
- **Data Export** - CSV and JSON export capabilities
- **Real-time Monitoring** - Live analytics dashboard

## 🎯 Pricing Models

### Volume Route (Pay-per-Use)
- Pay only for messages you use
- Transparent per-message pricing
- No upfront commitment
- Ideal for variable usage patterns

### Committed Amount Route (Prepaid Bundles)
- **Bundle Options** - Lower and upper bundle amounts
- **Fixed Platform Fee** - One-time setup fee added on top
- **Message Coverage** - Clear breakdown of what each bundle covers
- **Rate Transparency** - User's chosen rates applied consistently
- **Required Amount Analysis** - Shows actual needs vs. available bundles

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.9+
- PostgreSQL database
- Git

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/sharmaadwit/pricing-calc.git
   cd pricing-calc
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure database**:
   ```python
   # Update DATABASE_URL in app.py
   DATABASE_URL = "postgresql://username:password@host:port/database"
   ```

4. **Run the application**:
   ```bash
   python3 app.py
   ```

5. **Access the calculator**:
   - Main Calculator: `http://localhost:5000/`
   - Analytics Dashboard: `http://localhost:5000/analyticsv2`

## 📊 Analytics Automation

### Automated Daily Updates

The system includes comprehensive analytics automation that runs daily at 8 PM IST:

#### Setup Analytics Automation

1. **Install Analytics Dependencies**:
   ```bash
   python3 -m pip install pandas matplotlib seaborn psycopg2-binary
   ```

2. **Set up Cron Job**:
   ```bash
   ./scripts/setup_cron.sh
   ```

3. **Test Manually**:
   ```bash
   python3 scripts/update_analytics_daily.py
   ```

#### What Gets Updated Daily

- **CSV Export** - Fresh data from PostgreSQL database
- **Analytics Charts** - New visualizations saved as PNG files
- **Summary Data** - JSON file with key metrics
- **Dashboard** - Real-time data in `/analyticsv2`

#### Generated Files

- `analytics.csv` - Latest data export
- `static/analytics_summary.json` - Summary statistics
- `static/*_analytics.png` - Chart images
- `logs/analytics_update.log` - Execution logs

#### Monitoring

Check automation status:
```bash
# View logs
tail -f logs/analytics_update.log

# Check cron jobs
crontab -l

# Manual execution
python3 scripts/update_analytics_daily.py
```

## 🎨 User Interface

### Calculator Flow

1. **Volumes Step**
   - Enter message volumes for AI, Advanced, Marketing, and Utility
   - Real-time validation and formatting
   - Clear input guidance

2. **Pricing Step**
   - Set Gupshup markup rates for each message type
   - Choose region (affects currency and base rates)
   - Preview pricing calculations

3. **Results Step**
   - **Volume Route Analysis** - Pay-per-use breakdown
   - **Committed Amount Route Analysis** - Bundle options comparison
   - **Required Amount Analysis** - What you actually need
   - **Platform Fee Information** - Transparent fee structure

### Bundle Comparison Features

- **Lower Bundle Card** - Shows coverage and rates
- **Upper Bundle Card** - Shows coverage and rates
- **Required Amount Analysis** - Actual needs breakdown
- **Platform Fee Details** - Clear fee structure
- **Message Coverage** - What each amount can cover

## 📈 Analytics Dashboard

### Analytics v2 (`/analyticsv2`)

Comprehensive dashboard featuring:

- **Temporal Analytics** - Usage patterns by hour, day, month
- **Customer Behavior** - CLV, churn, service preferences
- **Pricing Strategy** - Discounts, revenue trends
- **Geographic Intelligence** - Country-wise performance
- **Resource Utilization** - Manday efficiency, rate variations
- **Platform Analytics** - Feature usage, calculation routes

### Data Sources

- PostgreSQL database (primary)
- `analytics.csv` (exported data)
- Real-time summary statistics

## ⚙️ Configuration

### Database Configuration

Update the connection string in `app.py`:
```python
DATABASE_URL = "postgresql://username:password@host:port/database"
```

### Analytics Configuration

Configure analytics in `scripts/update_analytics_daily.py`:
```python
DB_URL = "your_postgresql_connection_string"
CSV_PATH = "analytics.csv"
```

### Pricing Configuration

Modify pricing tiers in `pricing_config.py`:
- `meta_costs_table` - Channel-specific costs
- `committed_amount_slabs` - Bundle pricing tiers
- `currency_symbols` - Region-specific currencies

## 🔧 Development

### Adding New Features

1. **New Analytics Charts**:
   - Add function in `scripts/update_analytics_daily.py`
   - Update charts list in `generate_analytics_charts()`
   - Add corresponding chart in `templates/analyticsv2.html`

2. **New Pricing Models**:
   - Update `calculate_pricing_simulation()` in `app.py`
   - Add UI components in `templates/index.html`
   - Update configuration in `pricing_config.py`

3. **UI Improvements**:
   - Modify `templates/index.html` for layout changes
   - Update CSS in the template for styling
   - Add JavaScript for interactivity

### Modifying Automation Schedule

Edit cron schedule in `scripts/setup_cron.sh`:
```bash
# Current: 8 PM IST daily
CRON_JOB="30 14 * * * ..."

# Example: Every 6 hours
CRON_JOB="0 */6 * * * ..."
```

## 🐛 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Kill process using port 5000
lsof -ti:5000 | xargs kill -9

# Or use different port
export PORT=5001
python3 app.py
```

#### Database Connection Issues
1. Verify database URL format
2. Check database server status
3. Ensure credentials are correct

#### Analytics Not Updating
1. Check cron service status:
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

#### UI Issues
1. Clear browser cache
2. Check browser console for errors
3. Verify all static files are accessible

### Logs and Monitoring

- **Application Logs**: `logs/app.log`
- **Analytics Logs**: `logs/analytics_update.log`
- **Error Tracking**: Check browser console and server logs

## 📁 Project Structure

```
pricing-calc/
├── app.py                          # Main Flask application
├── calculator.py                   # Core pricing calculations
├── pricing_config.py              # Pricing configurations
├── requirements.txt               # Python dependencies
├── templates/
│   ├── index.html                 # Main calculator UI
│   ├── analytics.html             # Analytics v1
│   └── analyticsv2.html           # Analytics v2 dashboard
├── static/
│   ├── analytics_summary.json     # Analytics data
│   └── *_analytics.png           # Chart images
├── scripts/
│   ├── update_analytics_daily.py  # Daily analytics automation
│   ├── export_to_csv.py          # Data export utility
│   └── setup_cron.sh             # Cron job setup
├── logs/                          # Application logs
├── migrations/                    # Database migrations
└── notebooks/                     # Jupyter notebooks
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

[Your License Here]

## 🆕 Recent Updates

### v2.0.0 - Major UI/UX Overhaul
- ✨ Modern, responsive design with gradient backgrounds
- 🎯 Bundle comparison cards with detailed breakdowns
- 📊 Required amount analysis instead of recommendations
- 💰 Transparent platform fee structure
- 🚀 Improved user experience and clarity

### v1.5.0 - Analytics Enhancement
- 📈 Comprehensive analytics dashboard
- 🤖 Automated daily data updates
- 📊 Visual charts and reporting
- 🔄 Real-time data synchronization

---

**Built with ❤️ using Flask, PostgreSQL, and modern web technologies**