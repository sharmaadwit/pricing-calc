# --- Flask Pricing Calculator Application ---
# This app provides a pricing calculator for messaging services with dynamic inclusions, platform fees, and analytics.
# Key features: dynamic inclusions, robust error handling, session management, and professional UI.

from flask import Flask, render_template, request, session, redirect, url_for, flash
from calculator import calculate_pricing, get_suggested_price, price_tiers, meta_costs_table, calculate_total_mandays, calculate_total_manday_cost, COUNTRY_MANDAY_RATES, calculate_total_mandays_breakdown
import os
import sys
import re
from collections import Counter, defaultdict
import statistics
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from sqlalchemy import func
import uuid
from calculator import get_committed_amount_rates
from pricing_config import committed_amount_slabs, PLATFORM_PRICING_GUIDANCE

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session

# Test log to verify logging is working
print("=== FLASK APP STARTING UP ===", file=sys.stderr, flush=True)
print(f"Python version: {sys.version}", file=sys.stderr, flush=True)
print("=== END STARTUP LOG ===", file=sys.stderr, flush=True)

# Set up proper logging for Railway/gunicorn
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)
logger.info("Flask app logger initialized")

# Health check endpoint - moved to top for immediate availability
@app.route('/health')
def health_check():
    logger.info("Health check endpoint accessed")
    print("HEALTH CHECK ACCESSED", file=sys.stderr, flush=True)
    return "OK", 200

# Root route for basic connectivity test
@app.route('/ping')
def ping():
    return "pong", 200

def initialize_inclusions():
    """
    Returns a dictionary of all possible inclusions for each feature/tier.
    Only the inclusions for the highest/most specific tier in each category should be shown.
    """
    inclusions = {
         'Platform Fee Used for Margin Calculation': [
            'Journey Builder Lite',
            'Campaign Manager',
            'CTWA - (Meta, Tiktok)',
            'Agent Assist < 20 Agents',
            'personalize lite upto 1 million records - no advanced events',
            '80 TPS',
            '1 manday/month maintenance'
        ],
        'Personalize Load Lite': [
            'personalize lite upto 1 million records - no advanced events'
        ],
        'Human Agents <20': [
            'Agent Assist < 20 Agents'
        ],
        'Human Agents 20+': [
            'Agent Assist 20-50 agents'
        ],
        'Human Agents 50+': [
            'Agent Assist 50-100 agents'
        ],
        'Human Agents 100+': [
            'Agent Assist 100+ agents, advanced routing rules'
        ],
        'BFSI Tier 1': [
            'Auditing to be stored for XX days for JB PRO+Flows',
            'Conversational Data Encryption, Logging,Auditing, Purging (Data and Logs)'
        ],
        'BFSI Tier 2': [
            'Auditing to be stored for XX days for JB PRO+Flows',
            'Conversational Data Encryption, Logging,Auditing, Purging (Data and Logs) on Agent Assist',
            'Conversational Data Encryption, Logging,Auditing,Purging (Data and Logs) on AI Agents',
            'Encryption, Auditing,Logging on Campaign Manager'
        ],
        'BFSI Tier 3': [
            'Auditing to be stored for XX days for JB PRO+Flows',
            'Conversational Data Encryption, Logging,Auditing, Purging (Data and Logs) on Agent Assist',
            'Conversational Data Encryption, Logging,Auditing,Purging (Data and Logs) on AI Agents',
            'Encryption, Auditing,Logging on Campaign Manager',
            'Data Encryption, Logging, Auditing, Purging (Logs) on Reatargetting and Personalize'
        ],
        'Personalize Load Standard': [
            'Standard - upto 5 million records, no external events supported'
        ],
        'Personalize Load Advanced': [
            'Advanced - upto 10 million records, external events supported'
        ],
        'AI Module Yes': [
            'AI- Workspace Configuration and Data retarining UI'
        ],
        'Increased TPS 250': [
            '250 - Upto 250 messages per second'
        ],
        'Increased TPS 1000': [
            '1000 - upto 1000 messages per second'
        ],
        'Smart CPaaS Yes': [
            'Smart CPaaS - Intelligent failover between channels'
        ]
    }
    return inclusions

def get_lowest_tier_price(country, msg_type):
    """
    Returns the lowest tier price for a given country and message type.
    Used for rate card price display when volume is zero.
    """
    tiers = price_tiers.get(country, {}).get(msg_type.replace('_price', ''), [])
    if tiers:
        return tiers[0][2]
    return 0.0

def calculate_platform_fee(country, bfsi_tier, personalize_load, human_agents, ai_module, smart_cpaas, increased_tps='NA'):
    """
    Calculates the platform fee based on country and selected options.
    Returns (fee, currency).
    Now uses PLATFORM_PRICING_GUIDANCE for all values.
    """
    guidance = PLATFORM_PRICING_GUIDANCE.get(country, PLATFORM_PRICING_GUIDANCE['Rest of the World'])
    fee = guidance['minimum']
    currency = 'INR' if country == 'India' else 'USD'
    # BFSI Tiers
    if bfsi_tier == 'Tier 1':
        fee += guidance.get('BFSI_Tier_1', 0)
    elif bfsi_tier == 'Tier 2':
        fee += guidance.get('BFSI_Tier_2', 0)
    elif bfsi_tier == 'Tier 3':
        fee += guidance.get('BFSI_Tier_3', 0)
    # TPS
    if increased_tps == '250':
        fee += guidance.get('TPS_250', 0)
    elif increased_tps == '1000':
        fee += guidance.get('TPS_1000', 0)
    # Personalize Load
    if personalize_load == 'Standard':
        fee += guidance.get('Personalize_Standard', 0)
    elif personalize_load in ['Advanced', 'Pro']:
        fee += guidance.get('Personalize_Pro', 0)
    # Agent Assist (Human Agents)
    if human_agents == '20+':
        fee += guidance.get('Agent_Assist_20_50', 0)
    elif human_agents == '50+':
        fee += guidance.get('Agent_Assist_50_100', 0)
    elif human_agents == '100+':
        fee += guidance.get('Agent_Assist_100_plus', 0)
    # AI Module
    if ai_module == 'Yes':
        fee += guidance.get('AI_Module', 0)
    # Smart CPaaS
    if smart_cpaas == 'Yes':
        fee += guidance.get('Smart_CPaaS', 0)
    return fee, currency

# Custom Jinja2 filter for number formatting
@app.template_filter('smart_format')
def smart_format_filter(value):
    """Format numbers: no decimals if zero, up to 4 decimals if non-zero"""
    try:
        if value is None:
            return ''
        val = float(value)
        # Check if the number is a whole number
        if val == int(val):
            return f"{int(val):,}"
        else:
            # Show up to 4 decimal places, but remove trailing zeros
            s = f"{val:.4f}"
            return f"{s.rstrip('0').rstrip('.'):,}"
    except (ValueError, TypeError):
        return str(value) if value is not None else ''

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:prdeuXwtBzpLZaOGpxgRspfjfLNEQrys@gondola.proxy.rlwy.net:25504/railway')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Example Analytics model (expand as needed)
class Analytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    calculation_id = db.Column(db.String(64), unique=False, nullable=True)  # Transaction ID for each calculation
    timestamp = db.Column(db.DateTime, nullable=False)
    user_name = db.Column(db.String(128))
    country = db.Column(db.String(64))
    region = db.Column(db.String(64))  # Added region column for region-specific analytics
    platform_fee = db.Column(db.Float)
    ai_price = db.Column(db.Float)
    advanced_price = db.Column(db.Float)
    basic_marketing_price = db.Column(db.Float)
    basic_utility_price = db.Column(db.Float)
    currency = db.Column(db.String(8))
    # New fields for advanced analytics
    ai_rate_card_price = db.Column(db.Float)
    advanced_rate_card_price = db.Column(db.Float)
    basic_marketing_rate_card_price = db.Column(db.Float)
    basic_utility_rate_card_price = db.Column(db.Float)
    ai_volume = db.Column(db.Float)
    advanced_volume = db.Column(db.Float)
    basic_marketing_volume = db.Column(db.Float)
    basic_utility_volume = db.Column(db.Float)
    # New fields for user-submitted manday rates
    bot_ui_manday_rate = db.Column(db.Float)
    custom_ai_manday_rate = db.Column(db.Float)
    # New fields for manday counts
    bot_ui_mandays = db.Column(db.Float)
    custom_ai_mandays = db.Column(db.Float)
    committed_amount = db.Column(db.Float, nullable=True)  # New column for message bundle amount
    # Add more fields as needed
    calculation_route = db.Column(db.String(16))  # "volumes" or "bundle"

# os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # For local testing only

# Country to currency symbol mapping
COUNTRY_CURRENCY = {
    'India': '₹',
    'MENA': '$',  # USD for MENA
    'LATAM': '$',
    'Africa': '$',
    'Europe': '$',  # Use USD for Europe
    'Rest of the World': '$',
}

SECRET_ANALYTICS_KEYWORD = "letmein123"

# Add this near the top
CALC_PASSWORD = os.environ.get('CALC_PASSWORD', 'gup$hup.i0')  # Set your password here or via env var

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == CALC_PASSWORD:
            session['authenticated'] = True
            return redirect(url_for('index'))
        else:
            flash('Incorrect password. Please try again.', 'error')
    return render_template('login.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    """
    Main route for the pricing calculator. Handles all user steps (volumes, prices, bundle, results).
    Manages session data, input validation, pricing logic, and inclusions logic.
    """
    print("DEBUG: session at start of request:", dict(session), file=sys.stderr, flush=True)
    step = request.form.get('step', 'volumes')
    print("\n--- DEBUG ---", file=sys.stderr, flush=True)
    print("Form data:", dict(request.form), file=sys.stderr, flush=True)
    print("Session data:", dict(session), file=sys.stderr, flush=True)
    calculation_id = session.get('calculation_id', str(uuid.uuid4()))
    print("Current step:", step, file=sys.stderr, flush=True)
    print("--- END DEBUG ---\n", file=sys.stderr, flush=True)
    results = None
    currency_symbol = None

    # Defensive: ensure session data exists for edit actions
    if step == 'volumes' and request.method == 'POST':
        # Clear previous session state for a new calculation
        for key in ['chosen_platform_fee', 'pricing_inputs', 'rate_card_platform_fee', 'results', 'selected_components', 'user_selections', 'inclusions']:
            if key in session:
                session.pop(key)
        # Generate a new calculation_id for each new calculation
        calculation_id = str(uuid.uuid4())
        session['calculation_id'] = calculation_id
        print(f"DEBUG: New calculation started. Calculation ID: {calculation_id}", file=sys.stderr, flush=True)
        user_name = request.form.get('user_name', '')
        # Step 1: User submitted volumes and platform fee options
        country = request.form['country'].strip()  # Always strip country
        region = request.form.get('region', '')
        # Ignore region for Europe and Rest of the World
        if country in ['Europe', 'Rest of the World']:
            region = ''
        # Set currency: Only use INR for India, all others use USD
        if country == 'India':
            currency = 'INR'
        else:
            currency = 'USD'
        # Use dev_location only for India
        dev_location = request.form.get('dev_location', 'India').strip() if country == 'India' else None
        print(f"[app.py] After country/currency logic: country='{country}', currency='{currency}', dev_location='{dev_location}'", file=sys.stderr, flush=True)
        def parse_volume(val):
            try:
                return float(val.replace(',', '')) if val and str(val).strip() else 0.0
            except Exception:
                return 0.0
        ai_volume = parse_volume(request.form.get('ai_volume', ''))
        advanced_volume = parse_volume(request.form.get('advanced_volume', ''))
        basic_marketing_volume = parse_volume(request.form.get('basic_marketing_volume', ''))
        basic_utility_volume = parse_volume(request.form.get('basic_utility_volume', ''))
        # Debug: Log parsed volumes
        print(f"DEBUG: Parsed volumes - ai: {ai_volume}, advanced: {advanced_volume}, marketing: {basic_marketing_volume}, utility: {basic_utility_volume}", file=sys.stderr, flush=True)
        bfsi_tier = request.form.get('bfsi_tier', 'NA')
        personalize_load = request.form.get('personalize_load', 'NA')
        human_agents = request.form.get('human_agents', 'NA')
        ai_module = request.form.get('ai_module', 'NA')
        smart_cpaas = request.form.get('smart_cpaas', 'No')
        increased_tps = request.form.get('increased_tps', 'NA')
        # --- One Time Dev Activity Fields ---
        onboarding_price = request.form.get('onboarding_price', 'No')
        ux_price = request.form.get('ux_price', 'No')
        testing_qa_price = request.form.get('testing_qa_price', 'No')
        aa_setup_price = request.form.get('aa_setup_price', 'No')
        num_apis_price = request.form.get('num_apis_price', '0')
        num_journeys_price = request.form.get('num_journeys_price', '0')
        num_ai_workspace_commerce_price = request.form.get('num_ai_workspace_commerce_price', '0')
        num_ai_workspace_faq_price = request.form.get('num_ai_workspace_faq_price', '0')
        platform_fee, fee_currency = calculate_platform_fee(country, bfsi_tier, personalize_load, human_agents, ai_module, smart_cpaas, increased_tps)
        currency_symbol = COUNTRY_CURRENCY.get(country, '$')
        # Always update session['inputs'] with latest form data
        session['inputs'] = {
            'user_name': user_name,
            'country': country,
            'region': region,
            'ai_volume': ai_volume,
            'advanced_volume': advanced_volume,
            'basic_marketing_volume': basic_marketing_volume,
            'basic_utility_volume': basic_utility_volume,
            'platform_fee': platform_fee,
            'bfsi_tier': bfsi_tier,
            'personalize_load': personalize_load,
            'human_agents': human_agents,
            'ai_module': ai_module,
            'smart_cpaas': smart_cpaas,
            'increased_tps': increased_tps,
            # One time dev fields
            'onboarding_price': onboarding_price,
            'ux_price': ux_price,
            'testing_qa_price': testing_qa_price,
            'aa_setup_price': aa_setup_price,
            'num_apis_price': num_apis_price,
            'num_journeys_price': num_journeys_price,
            'num_ai_workspace_commerce_price': num_ai_workspace_commerce_price,
            'num_ai_workspace_faq_price': num_ai_workspace_faq_price
        }
        print("DEBUG: session['inputs'] just set to:", session['inputs'], file=sys.stderr, flush=True)
        if all(float(v) == 0.0 for v in [ai_volume, advanced_volume, basic_marketing_volume, basic_utility_volume]):
            currency_symbol = COUNTRY_CURRENCY.get(country, '$')
            return render_template('index.html', step='bundle', currency_symbol=currency_symbol, inputs=session.get('inputs', {}), platform_fee=platform_fee, calculation_id=calculation_id)
        # Suggest prices
        def is_zero(val):
            try:
                return float(val) == 0.0
            except Exception:
                return True
        suggested_prices = {
            'ai_price': get_suggested_price(country, 'ai', ai_volume) if not is_zero(ai_volume) else get_lowest_tier_price(country, 'ai'),
            'advanced_price': get_suggested_price(country, 'advanced', advanced_volume) if not is_zero(advanced_volume) else get_lowest_tier_price(country, 'advanced'),
            'basic_marketing_price': get_suggested_price(country, 'basic_marketing', basic_marketing_volume) if not is_zero(basic_marketing_volume) else get_lowest_tier_price(country, 'basic_marketing'),
            'basic_utility_price': get_suggested_price(country, 'basic_utility', basic_utility_volume) if not is_zero(basic_utility_volume) else get_lowest_tier_price(country, 'basic_utility'),
        }
        suggested_prices = patch_suggested_prices(suggested_prices, session.get('inputs', {}))
        return render_template('index.html', step='prices', suggested=suggested_prices, inputs=session.get('inputs', {}), currency_symbol=currency_symbol, platform_fee=platform_fee, calculation_id=calculation_id)

    elif step == 'prices' and request.method == 'POST':
        print('HANDLER: Entered prices POST step', file=sys.stderr, flush=True)
        inputs = session.get('inputs', {})
        if not inputs:
            print('HANDLER: No inputs in session, redirecting to index', file=sys.stderr, flush=True)
            flash('Session expired or missing. Please start again.', 'error')
            return redirect(url_for('index'))
        def parse_price(val):
            try:
                return float(val.replace(',', '')) if val and str(val).strip() else None
            except Exception:
                return None
        ai_price = parse_price(request.form.get('ai_price', ''))
        advanced_price = parse_price(request.form.get('advanced_price', ''))
        basic_marketing_price = parse_price(request.form.get('basic_marketing_price', ''))
        basic_utility_price = parse_price(request.form.get('basic_utility_price', ''))
        platform_fee = parse_price(request.form.get('platform_fee', '')) or 0.0
        # Parse manday rates from form and save to session
        bot_ui_manday_rate = parse_price(request.form.get('bot_ui_manday_rate', ''))
        custom_ai_manday_rate = parse_price(request.form.get('custom_ai_manday_rate', ''))
        session['manday_rates'] = {
            'bot_ui': bot_ui_manday_rate,
            'custom_ai': custom_ai_manday_rate
        }
        # Get suggested prices for validation
        country = inputs.get('country', 'India')
        ai_volume = float(inputs.get('ai_volume', 0) or 0)
        advanced_volume = float(inputs.get('advanced_volume', 0) or 0)
        basic_marketing_volume = float(inputs.get('basic_marketing_volume', 0) or 0)
        basic_utility_volume = float(inputs.get('basic_utility_volume', 0) or 0)
        suggested_ai = get_suggested_price(country, 'ai', ai_volume)
        suggested_advanced = get_suggested_price(country, 'advanced', advanced_volume)
        suggested_marketing = get_suggested_price(country, 'basic_marketing', basic_marketing_volume)
        suggested_utility = get_suggested_price(country, 'basic_utility', basic_utility_volume)
        # Calculate rate card platform fee for discount check
        rate_card_platform_fee, _ = calculate_platform_fee(
            country,
            inputs.get('bfsi_tier', 'NA'),
            inputs.get('personalize_load', 'NA'),
            inputs.get('human_agents', 'NA'),
            inputs.get('ai_module', 'NA'),
            inputs.get('smart_cpaas', 'No'),
            inputs.get('increased_tps', 'NA')
        )
        discount_errors = []
        # Discount checks: allow up to 90% discount for basic marketing, 70% for all others
        if ai_price is not None and (suggested_ai or 0) and ai_price < 0.3 * (suggested_ai or 0):
            discount_errors.append("AI Message price is less than 30% of the rate card.")
        if advanced_price is not None and (suggested_advanced or 0) and advanced_price < 0.3 * (suggested_advanced or 0):
            discount_errors.append("Advanced Message price is less than 30% of the rate card.")
        if basic_marketing_price is not None and (suggested_marketing or 0) and basic_marketing_price < 0.1 * (suggested_marketing or 0):
            discount_errors.append("Basic Marketing Message price is less than 10% of the rate card.")
        if basic_utility_price is not None and (suggested_utility or 0) and basic_utility_price < 0.3 * (suggested_utility or 0):
            discount_errors.append("Basic Utility/Authentication Message price is less than 30% of the rate card.")
        # Platform fee discount check
        if platform_fee < 0.3 * rate_card_platform_fee:
            discount_errors.append("Platform Fee is less than 30% of the rate card platform fee.")
        if discount_errors:
            print('HANDLER: Discount errors found, rendering prices page with errors', file=sys.stderr, flush=True)
            for msg in discount_errors:
                flash(msg, 'error')
            flash("Probability of deal desk rejection is high.", 'error')
            suggested_prices = {
                'ai_price': suggested_ai,
                'advanced_price': suggested_advanced,
                'basic_marketing_price': suggested_marketing,
                'basic_utility_price': suggested_utility,
            }
            currency_symbol = COUNTRY_CURRENCY.get(country, '$')
            # Re-render the pricing page with user input and error
            return render_template('index.html', step='prices', suggested=suggested_prices, inputs=inputs, currency_symbol=currency_symbol, platform_fee=platform_fee, calculation_id=calculation_id)
        print('HANDLER: No discount errors, continuing to results calculation', file=sys.stderr, flush=True)

        # Always recalculate platform fee before saving to session['pricing_inputs']
        calculated_platform_fee, fee_currency = calculate_platform_fee(
            country,
            inputs.get('bfsi_tier', 'NA'),
            inputs.get('personalize_load', 'NA'),
            inputs.get('human_agents', 'NA'),
            inputs.get('ai_module', 'NA'),
            inputs.get('smart_cpaas', 'No'),
            inputs.get('increased_tps', 'NA')
        )
        # Use user input if provided and valid, else use calculated
        user_platform_fee = request.form.get('platform_fee')
        if user_platform_fee and float(user_platform_fee) > 0:
            platform_fee = float(user_platform_fee)
        else:
            platform_fee = calculated_platform_fee
        # Overwrite any previous platform_fee value for this calculation
        session['pricing_inputs'] = {
            'ai_price': ai_price,
            'advanced_price': advanced_price,
            'basic_marketing_price': basic_marketing_price,
            'basic_utility_price': basic_utility_price,
            'platform_fee': platform_fee
        }

        currency_symbol = COUNTRY_CURRENCY.get(country, '$')
        # --- Restored logic for results calculation and rendering ---
        bundle_choice = 'No'
        session['bundle_choice'] = bundle_choice
        ai_price = session['pricing_inputs'].get('ai_price', 0)
        advanced_price = session['pricing_inputs'].get('advanced_price', 0)
        basic_marketing_price = session['pricing_inputs'].get('basic_marketing_price', 0)
        basic_utility_price = session['pricing_inputs'].get('basic_utility_price', 0)
        platform_fee = session['pricing_inputs'].get('platform_fee', 0)
        bundle_lines = []
        bundle_cost = 0
        for label, key, price in [
            ("AI Message", 'ai_volume', ai_price),
            ("Advanced Message", 'advanced_volume', advanced_price),
            ("Basic Marketing Message", 'basic_marketing_volume', basic_marketing_price),
            ("Basic Utility/Authentication Message", 'basic_utility_volume', basic_utility_price),
        ]:
            volume = float(inputs.get(key, 0))
            bundle_lines.append({
                'label': label,
                'volume': volume,
                'price': float(price)
            })
            bundle_cost += volume * float(price)
        total_bundle_price = float(platform_fee) + bundle_cost
        bundle_details = {
            'lines': bundle_lines,
            'bundle_cost': bundle_cost,
            'total_bundle_price': total_bundle_price,
            'inclusion_text': 'See table below for included volumes and overage prices.'
        }
        # Use one-time dev activity fields from form if present, else from session
        dev_fields = [
            'onboarding_price', 'ux_price', 'testing_qa_price', 'aa_setup_price',
            'num_apis_price', 'num_journeys_price', 'num_ai_workspace_commerce_price', 'num_ai_workspace_faq_price'
        ]
        patched_form = (request.form.copy() if hasattr(request.form, 'copy') else dict(request.form)) or {}
        for field in dev_fields:
            if field not in patched_form and field in inputs:
                patched_form[field] = inputs[field]
        for k in list(patched_form.keys()):
            if k.endswith('_price') or k.endswith('_rate') or k.endswith('_volume') or k.startswith('num_'):
                try:
                    patched_form[k] = str(patched_form[k]).replace(',', '')
                except Exception:
                    pass
        # --- Ensure manday_rates is always set and complete ---
        country = inputs.get('country', 'India')
        dev_location = inputs.get('dev_location', 'India')
        rates = COUNTRY_MANDAY_RATES.get(country, COUNTRY_MANDAY_RATES['Rest of the World'])
        # Always reset manday_rates to backend defaults when country or dev_location changes
        if country == 'LATAM':
            default_bot_ui = float(rates['bot_ui'].get(dev_location, 0.0) or 0.0)
            default_custom_ai = float(rates['custom_ai'].get(dev_location, 0.0) or 0.0)
        else:
            default_bot_ui = float(rates.get('bot_ui', 0.0) or 0.0)
            default_custom_ai = float(rates.get('custom_ai', 0.0) or 0.0)
        manday_rates = {
            'bot_ui': default_bot_ui,
            'custom_ai': default_custom_ai,
            'default_bot_ui': default_bot_ui,
            'default_custom_ai': default_custom_ai
        }
        # Fill missing keys with defaults
        manday_rates['bot_ui'] = float(manday_rates.get('bot_ui', default_bot_ui))
        manday_rates['custom_ai'] = float(manday_rates.get('custom_ai', default_custom_ai))
        manday_rates['default_bot_ui'] = float(default_bot_ui)
        manday_rates['default_custom_ai'] = float(default_custom_ai)
        # Calculate discount percentages
        manday_rates['bot_ui_discount'] = round(100 * (default_bot_ui - manday_rates['bot_ui']) / default_bot_ui, 2) if default_bot_ui else 0
        manday_rates['custom_ai_discount'] = round(100 * (default_custom_ai - manday_rates['custom_ai']) / default_custom_ai, 2) if default_custom_ai else 0
        total_mandays = calculate_total_mandays(patched_form)
        # --- PATCH: Always .strip() the country and set dev_location only for India before dev cost calculation ---
        if 'country' in patched_form:
            patched_form['country'] = patched_form['country'].strip()
        else:
            patched_form['country'] = inputs.get('country', 'India').strip()
        if patched_form['country'] != 'India':
            patched_form['dev_location'] = None
        else:
            patched_form['dev_location'] = patched_form.get('dev_location', 'India').strip()
        total_dev_cost, dev_cost_currency, dev_cost_breakdown = calculate_total_manday_cost(patched_form, manday_rates)
        print(f"DEBUG: dev_cost_currency = {dev_cost_currency}, country = {country}", file=sys.stderr, flush=True)
        manday_breakdown = dev_cost_breakdown['mandays_breakdown']
        
        # Debug: Log inputs being used for calculation
        print(f"DEBUG: Calculation inputs - ai_volume: {inputs.get('ai_volume', 0)}, advanced_volume: {inputs.get('advanced_volume', 0)}, marketing_volume: {inputs.get('basic_marketing_volume', 0)}, utility_volume: {inputs.get('basic_utility_volume', 0)}", file=sys.stderr, flush=True)
        
        # Calculate pricing results
        try:
            results = calculate_pricing(
                country=inputs.get('country', 'India'),
                ai_volume=float(inputs.get('ai_volume', 0) or 0),
                advanced_volume=float(inputs.get('advanced_volume', 0) or 0),
                basic_marketing_volume=float(inputs.get('basic_marketing_volume', 0) or 0),
                basic_utility_volume=float(inputs.get('basic_utility_volume', 0) or 0),
                platform_fee=float(platform_fee),
                ai_price=ai_price,
                advanced_price=advanced_price,
                basic_marketing_price=basic_marketing_price,
                basic_utility_price=basic_utility_price
            )
            print(f"DEBUG: Calculation successful, results: {results}", file=sys.stderr, flush=True)
        except Exception as e:
            print(f"DEBUG: Calculation failed with error: {e}", file=sys.stderr, flush=True)
            flash('Pricing calculation failed. Please check your inputs and try again.', 'error')
            suggested_prices = {
                'ai_price': suggested_ai,
                'advanced_price': suggested_advanced,
                'basic_marketing_price': suggested_marketing,
                'basic_utility_price': suggested_utility,
            }
            currency_symbol = COUNTRY_CURRENCY.get(country, '$')
            return render_template('index.html', step='prices', suggested=suggested_prices, inputs=inputs, currency_symbol=currency_symbol, platform_fee=platform_fee, calculation_id=calculation_id)
        
        # Remove duplicate Committed Amount if present
        seen = set()
        unique_line_items = []
        if results and 'line_items' in results:
            for item in results['line_items']:
                key = (item.get('line_item'), item.get('chosen_price'), item.get('suggested_price'))
                if key not in seen:
                    unique_line_items.append(item)
                    seen.add(key)
            results['line_items'] = unique_line_items
        # Validate results
        if not results or 'line_items' not in results:
            print(f"DEBUG: Invalid results: {results}", file=sys.stderr, flush=True)
            flash('Pricing calculation failed. Please check your inputs and try again.', 'error')
            suggested_prices = {
                'ai_price': suggested_ai,
                'advanced_price': suggested_advanced,
                'basic_marketing_price': suggested_marketing,
                'basic_utility_price': suggested_utility,
            }
            currency_symbol = COUNTRY_CURRENCY.get(country, '$')
            return render_template('index.html', step='prices', suggested=suggested_prices, inputs=inputs, currency_symbol=currency_symbol, platform_fee=platform_fee, calculation_id=calculation_id)
        print("PASSED results validation, about to render results page", file=sys.stderr, flush=True)
        try:
            # --- Ensure manday_rates is always set and complete ---
            country = inputs.get('country', 'India')
            dev_location = inputs.get('dev_location', 'India')
            rates = COUNTRY_MANDAY_RATES.get(country, COUNTRY_MANDAY_RATES['Rest of the World'])
            # Always reset manday_rates to backend defaults when country or dev_location changes
            if country == 'LATAM':
                default_bot_ui = float(rates['bot_ui'].get(dev_location, 0.0) or 0.0)
                default_custom_ai = float(rates['custom_ai'].get(dev_location, 0.0) or 0.0)
            else:
                default_bot_ui = float(rates.get('bot_ui', 0.0) or 0.0)
                default_custom_ai = float(rates.get('custom_ai', 0.0) or 0.0)
            manday_rates = {
                'bot_ui': default_bot_ui,
                'custom_ai': default_custom_ai,
                'default_bot_ui': default_bot_ui,
                'default_custom_ai': default_custom_ai
            }
            # Fill missing keys with defaults
            manday_rates['bot_ui'] = float(manday_rates.get('bot_ui', default_bot_ui))
            manday_rates['custom_ai'] = float(manday_rates.get('custom_ai', default_custom_ai))
            manday_rates['default_bot_ui'] = float(default_bot_ui)
            manday_rates['default_custom_ai'] = float(default_custom_ai)
            # Calculate discount percentages
            manday_rates['bot_ui_discount'] = round(100 * (default_bot_ui - manday_rates['bot_ui']) / default_bot_ui, 2) if default_bot_ui else 0
            manday_rates['custom_ai_discount'] = round(100 * (default_custom_ai - manday_rates['custom_ai']) / default_custom_ai, 2) if default_custom_ai else 0
            total_mandays = calculate_total_mandays(patched_form)
            total_dev_cost, dev_cost_currency, dev_cost_breakdown = calculate_total_manday_cost(patched_form, manday_rates)
            print(f"DEBUG: dev_cost_currency = {dev_cost_currency}, country = {country}", file=sys.stderr, flush=True)
            manday_breakdown = dev_cost_breakdown['mandays_breakdown']
            # Debug: Log inputs being used for calculation
            print(f"DEBUG: Calculation inputs - ai_volume: {inputs.get('ai_volume', 0)}, advanced_volume: {inputs.get('advanced_volume', 0)}, marketing_volume: {inputs.get('basic_marketing_volume', 0)}, utility_volume: {inputs.get('basic_utility_volume', 0)}", file=sys.stderr, flush=True)
            # Calculate pricing results
            try:
                results = calculate_pricing(
                    country=inputs.get('country', 'India'),
                    ai_volume=float(inputs.get('ai_volume', 0) or 0),
                    advanced_volume=float(inputs.get('advanced_volume', 0) or 0),
                    basic_marketing_volume=float(inputs.get('basic_marketing_volume', 0) or 0),
                    basic_utility_volume=float(inputs.get('basic_utility_volume', 0) or 0),
                    platform_fee=float(platform_fee),
                    ai_price=ai_price,
                    advanced_price=advanced_price,
                    basic_marketing_price=basic_marketing_price,
                    basic_utility_price=basic_utility_price
                )
                print(f"DEBUG: Calculation successful, results: {results}", file=sys.stderr, flush=True)
            except Exception as e:
                print(f"DEBUG: Calculation failed with error: {e}", file=sys.stderr, flush=True)
                flash('Pricing calculation failed. Please check your inputs and try again.', 'error')
                suggested_prices = {
                    'ai_price': suggested_ai,
                    'advanced_price': suggested_advanced,
                    'basic_marketing_price': suggested_marketing,
                    'basic_utility_price': suggested_utility,
                }
                currency_symbol = COUNTRY_CURRENCY.get(country, '$')
                return render_template('index.html', step='prices', suggested=suggested_prices, inputs=inputs, currency_symbol=currency_symbol, platform_fee=platform_fee, calculation_id=calculation_id)
        except Exception as e:
            print(f"DEBUG: Error in manday/dev cost or pricing calculation: {e}", file=sys.stderr, flush=True)
            flash('Internal error during calculation. Please try again.', 'error')
            return render_template('index.html', step='prices', suggested={}, inputs=inputs, currency_symbol=currency_symbol, platform_fee=platform_fee, calculation_id=calculation_id)
        results['margin'] = results.get('margin', '')
        expected_invoice_amount = results.get('revenue', 0)
        chosen_platform_fee = float(platform_fee)
        rate_card_platform_fee, _ = calculate_platform_fee(
            inputs['country'],
            inputs.get('bfsi_tier', 'NA'),
            inputs.get('personalize_load', 'NA'),
            inputs.get('human_agents', 'NA'),
            inputs.get('ai_module', 'NA'),
            inputs.get('smart_cpaas', 'No'),
            inputs.get('increased_tps', 'NA')
        )
        user_selections = []
        if inputs.get('bfsi_tier', 'NA') not in ['NA', 'No']:
            user_selections.append(('BFSI Tier', inputs['bfsi_tier']))
        if inputs.get('personalize_load', 'NA') not in ['NA', 'No']:
            user_selections.append(('Personalize Load', inputs['personalize_load']))
        if inputs.get('human_agents', 'NA') not in ['NA', 'No']:
            user_selections.append(('Human Agents', inputs['human_agents']))
        if inputs.get('ai_module', 'NA') not in ['NA', 'No']:
            user_selections.append(('AI Module', inputs['ai_module']))
        if inputs.get('smart_cpaas', 'No') == 'Yes':
            user_selections.append(('Smart CPaaS', 'Yes'))
        if inputs.get('increased_tps', 'NA') not in ['NA', 'No']:
            user_selections.append(('Increased TPS', inputs['increased_tps']))
        inclusions = initialize_inclusions()
        final_inclusions = []
        # Always include base inclusions except those that overlap with selected options
        # Ensure these variables are defined before use
        personalize_load = inputs.get('personalize_load', 'NA')
        human_agents = inputs.get('human_agents', 'NA')
        increased_tps = inputs.get('increased_tps', 'NA')
        overlap_map = {
       'Personalize Load': ['Personalize Lite (upto 1ml and no advanced events)'],
       'Human Agents': ['Agent Assist <20'],
       'Increased TPS': ['80 TPS']
   }
        base_inclusions = inclusions['Platform Fee Used for Margin Calculation']
        # Remove overlapping items from base inclusions
        base_inclusions_filtered = []
        # Map of option to their possible overlapping base inclusions
        overlap_map = {
            'Personalize Load': ['Personalize Lite (upto 1ml and no advanced events)'],
            'Human Agents': ['Agent Assist <20'],
            'Increased TPS': ['80 TPS'],
        }
        # Get selected options
        personalize_load = inputs.get('personalize_load', 'NA')
        human_agents = inputs.get('human_agents', 'NA')
        increased_tps = inputs.get('increased_tps', 'NA')
        # Only add base inclusions that do not overlap with selected options
        for item in base_inclusions:
            if (personalize_load != 'Lite' and item in overlap_map['Personalize Load']) or \
               (human_agents not in ['NA', 'No', '<20'] and item in overlap_map['Human Agents']) or \
               (increased_tps not in ['NA', 'No', '80'] and item in overlap_map['Increased TPS']):
                continue
            base_inclusions_filtered.append(item)
        final_inclusions += base_inclusions_filtered
        # Add only the selected option inclusions
        if personalize_load == 'Advanced':
            final_inclusions += inclusions['Personalize Load Advanced']
        elif personalize_load == 'Standard':
            final_inclusions += inclusions['Personalize Load Standard']
        elif personalize_load == 'Lite':
            final_inclusions += inclusions['Personalize Load Lite']
        # Human Agents
        agent_inclusion_added = False
        if human_agents == '100+':
            final_inclusions += inclusions.get('Human Agents 100+', [])
            agent_inclusion_added = True
        elif human_agents == '50+':
            final_inclusions += inclusions.get('Human Agents 50+', [])
            agent_inclusion_added = True
        elif human_agents == '20+':
            final_inclusions += inclusions.get('Human Agents 20+', [])
            agent_inclusion_added = True
        elif human_agents == '<20':
            final_inclusions += inclusions.get('Human Agents <20', [])
            agent_inclusion_added = True
        # Fallback: if a Human Agents value is selected but not found, show generic inclusion
        if not agent_inclusion_added and human_agents not in ['NA', 'No', '']:
            final_inclusions.append('Agent Assist included')
        # Increased TPS
        if increased_tps == '1000':
            final_inclusions += inclusions['Increased TPS 1000']
        elif increased_tps == '250':
            final_inclusions += inclusions['Increased TPS 250']
        else:
            if '80 TPS' not in final_inclusions:
                final_inclusions.append('80 TPS')
        # AI Module
        if inputs.get('ai_module', 'No') == 'Yes':
            final_inclusions += inclusions['AI Module Yes']
        # Smart CPaaS
        if inputs.get('smart_cpaas', 'No') == 'Yes':
            final_inclusions += inclusions['Smart CPaaS Yes']
        # BFSI Tier (highest only)
        bfsi_tier = inputs.get('bfsi_tier', 'NA')
        if bfsi_tier == 'Tier 3':
            final_inclusions += inclusions['BFSI Tier 3']
        elif bfsi_tier == 'Tier 2':
            final_inclusions += inclusions['BFSI Tier 2']
        elif bfsi_tier == 'Tier 1':
            final_inclusions += inclusions['BFSI Tier 1']
        # Remove lower-tier inclusions if higher tier is selected
        if human_agents in ['20+', '50+', '100+']:
            if 'Agent Assist < 20 Agents' in final_inclusions:
                final_inclusions.remove('Agent Assist < 20 Agents')
        if personalize_load in ['Standard', 'Advanced']:
            if 'personalize lite upto 1 million records - no advanced events' in final_inclusions:
                final_inclusions.remove('personalize lite upto 1 million records - no advanced events')
        if increased_tps in ['250', '1000']:
            if '80 TPS' in final_inclusions:
                final_inclusions.remove('80 TPS')
        # Remove duplicates
        final_inclusions = list(dict.fromkeys(final_inclusions))
        # Pass contradiction_warning to the template for display if needed
        session['selected_components'] = user_selections
        session['results'] = results
        session['chosen_platform_fee'] = chosen_platform_fee
        session['rate_card_platform_fee'] = rate_card_platform_fee
        session['user_selections'] = user_selections
        session['inclusions'] = inclusions
        # Add platform fee as a line item if not already present (for volume path)
        platform_fee_line = {
            'line_item': 'Platform Fee (Chosen)',
            'volume': '',
            'chosen_price': '',
            'suggested_price': '',
            'overage_price': '',
            'revenue': float(platform_fee)
        }
        if not any(item.get('line_item') == 'Platform Fee (Chosen)' for item in results['line_items']):
            results['line_items'].append(platform_fee_line)
        # Create margin table for volume-based path
        margin_line_items = []
        # --- Determine rate card markups for India ---
        rate_card_markups = {}
        if inputs.get('country') == 'India':
            # Committed amount route
            committed_amount = float(inputs.get('committed_amount', 0) or 0)
            if committed_amount > 0:
                ca_rates = get_committed_amount_rates(inputs.get('country', 'India'), committed_amount)
                rate_card_markups = {
                    'AI Message': ca_rates['ai'],
                    'Advanced Message': ca_rates['advanced'],
                    'Basic Marketing Message': ca_rates['basic_marketing'],
                    'Basic Utility/Authentication Message': ca_rates['basic_utility'],
                }
            else:
                # Volumes route: use price_tiers
                from calculator import price_tiers
                for msg_type, label in [('ai', 'AI Message'), ('advanced', 'Advanced Message'), ('basic_marketing', 'Basic Marketing Message'), ('basic_utility', 'Basic Utility/Authentication Message')]:
                    tiers = price_tiers['India'][msg_type]
                    rate_card_markups[label] = tiers[0][2] if tiers else 0.0
        # ---
        for item in results['line_items']:
            if item.get('line_item') != 'Platform Fee (Chosen)':
                chosen_price = item.get('chosen_price', 0)
                # Use correct rate card markup for India
                rate_card_key = item.get('line_item') or item.get('label', '')
                if inputs.get('country') == 'India' and rate_card_key in rate_card_markups:
                    suggested_price = rate_card_markups[rate_card_key]
                else:
                    suggested_price = item.get('suggested_price', 0)
                discount_percent = ''
                if chosen_price and suggested_price and float(suggested_price) > 0:
                    try:
                        discount_percent = f"{((float(suggested_price) - float(chosen_price)) / float(suggested_price) * 100):.2f}%"
                    except Exception:
                        discount_percent = '0.00%'
                else:
                    discount_percent = '0.00%'
                margin_line_items.append({
                    'line_item': rate_card_key,
                    'chosen_price': chosen_price,
                    'rate_card_price': suggested_price,
                    'discount_percent': discount_percent
                })
        # Add platform fee to margin table with correct discount percent
        pf_discount = '0.00%'
        try:
            if rate_card_platform_fee and float(rate_card_platform_fee) > 0:
                pf_discount = f"{((float(rate_card_platform_fee) - float(platform_fee)) / float(rate_card_platform_fee) * 100):.2f}%"
        except Exception:
            pf_discount = '0.00%'
        margin_line_items.append({
            'line_item': 'Platform Fee',
            'chosen_price': platform_fee,
            'rate_card_price': rate_card_platform_fee,
            'discount_percent': pf_discount
        })
        # Helper to format numbers for display
        def fmt(val):
            # Format numbers: no decimals if .00, else show up to 4 decimals
            try:
                if isinstance(val, str) and val.replace('.', '', 1).isdigit():
                    val = float(val)
                if isinstance(val, (int, float)):
                    # Check if the number is a whole number
                    if val == int(val):
                        return str(int(val))
                    else:
                        # Show up to 4 decimal places, but remove trailing zeros
                        s = f"{val:.4f}"
                        return s.rstrip('0').rstrip('.')
            except Exception:
                pass
            return val
        # Format pricing_line_items
        for item in results['line_items']:
            for key in ['chosen_price', 'overage_price', 'suggested_price', 'revenue', 'volume']:
                if key in item and (isinstance(item[key], (int, float)) or (isinstance(item[key], str) and item[key].replace('.', '', 1).isdigit())) and item[key] != '':
                    item[key] = fmt(item[key])
        # Format margin_line_items
        for item in margin_line_items:
            for key in ['chosen_price', 'rate_card_price']:
                if key in item and (isinstance(item[key], (int, float)) or (isinstance(item[key], str) and item[key].replace('.', '', 1).isdigit())) and item[key] != '':
                    item[key] = fmt(item[key])
        # Log analytics for volumes flow
        analytics_kwargs = dict(
            timestamp=datetime.utcnow(),
            user_name=inputs.get('user_name', ''),
            country=inputs.get('country', ''),
            region=inputs.get('region', ''),
            platform_fee=platform_fee,
            ai_price=ai_price,
            advanced_price=advanced_price,
            basic_marketing_price=basic_marketing_price,
            basic_utility_price=basic_utility_price,
            currency=COUNTRY_CURRENCY.get(inputs.get('country', 'India'), '$'),
            ai_rate_card_price=suggested_ai,
            advanced_rate_card_price=suggested_advanced,
            basic_marketing_rate_card_price=suggested_marketing,
            basic_utility_rate_card_price=suggested_utility,
            ai_volume=ai_volume,
            advanced_volume=advanced_volume,
            basic_marketing_volume=basic_marketing_volume,
            basic_utility_volume=basic_utility_volume,
            # Store user-submitted manday rates
            bot_ui_manday_rate=manday_rates.get('bot_ui'),
            custom_ai_manday_rate=manday_rates.get('custom_ai'),
            bot_ui_mandays=manday_breakdown.get('bot_ui', 0),
            custom_ai_mandays=manday_breakdown.get('custom_ai', 0),
            committed_amount=inputs.get('committed_amount', None),
        )
        analytics_kwargs['calculation_id'] = session.get('calculation_id')
        # Set calculation_route for analytics
        if all(float(inputs.get(v, 0)) == 0.0 for v in ['ai_volume', 'advanced_volume', 'basic_marketing_volume', 'basic_utility_volume']) and float(inputs.get('committed_amount', 0) or 0) > 0:
            analytics_kwargs['calculation_route'] = 'bundle'
        else:
            analytics_kwargs['calculation_route'] = 'volumes'
        # Debug: Log manday rates and breakdown before saving to Analytics
        print(f"DEBUG: Saving Analytics: bot_ui_manday_rate={analytics_kwargs.get('bot_ui_manday_rate')}, custom_ai_manday_rate={analytics_kwargs.get('custom_ai_manday_rate')}, bot_ui_mandays={analytics_kwargs.get('bot_ui_mandays')}, custom_ai_mandays={analytics_kwargs.get('custom_ai_mandays')}, calculation_route={analytics_kwargs.get('calculation_route')}", file=sys.stderr, flush=True)
        new_analytics = Analytics(**analytics_kwargs)
        db.session.add(new_analytics)
        db.session.commit()
        # Top 5 users by number of calculations
        user_names = [row[0] for row in db.session.query(Analytics.user_name).all() if row[0]]
        top_users = Counter(user_names).most_common()  # Remove the 5 limit
        # When setting results['suggested_revenue'], use rate_card_platform_fee instead of platform_fee
        results['suggested_revenue'] = (results.get('suggested_revenue', 0) - platform_fee) + rate_card_platform_fee
        print("RENDERING RESULTS PAGE", file=sys.stderr, flush=True)
        contradiction_warning = None
        # Always calculate final_price_details for all routes
        committed_amount = float(inputs.get('committed_amount', 0) or 0)
        country = inputs.get('country', 'India')
        ai_volume = float(inputs.get('ai_volume', 0) or 0)
        advanced_volume = float(inputs.get('advanced_volume', 0) or 0)
        platform_fee_total = float(platform_fee)
        meta_costs = meta_costs_table.get(country, meta_costs_table['Rest of the World'])
        if all(float(inputs.get(v, 0)) == 0.0 for v in ['ai_volume', 'advanced_volume', 'basic_marketing_volume', 'basic_utility_volume']):
            rates = get_committed_amount_rates(country, committed_amount)
            ai_price = rates['ai']
            advanced_price = rates['advanced']
        else:
            ai_price = session.get('pricing_inputs', {}).get('ai_price', 0)
            advanced_price = session.get('pricing_inputs', {}).get('advanced_price', 0)
        final_price_details = {
            'platform_fee_total': platform_fee_total,
            'fixed_platform_fee': platform_fee,
            'ai_messages': {
                'volume': int(ai_volume),
                'price_per_msg': round(ai_price + meta_costs['ai'], 4),
                'overage_price': round((ai_price + meta_costs['ai']) * 1.2, 4)
            },
            'advanced_messages': {
                'volume': int(advanced_volume),
                'price_per_msg': round(advanced_price + meta_costs['ai'], 4),
                'overage_price': round((advanced_price + meta_costs['ai']) * 1.2, 4)
            },
            'marketing_message': {
                'volume': int(inputs.get('basic_marketing_volume', 0) or 0),
                'price_per_msg': round(session.get('pricing_inputs', {}).get('basic_marketing_price', 0) + meta_costs.get('marketing', 0), 4),
                'overage_price': round((session.get('pricing_inputs', {}).get('basic_marketing_price', 0) + meta_costs.get('marketing', 0)) * 1.2, 4)
            },
            'utility_message': {
                'volume': int(inputs.get('basic_utility_volume', 0) or 0),
                'price_per_msg': round(session.get('pricing_inputs', {}).get('basic_utility_price', 0) + meta_costs.get('utility', 0), 4),
                'overage_price': round((session.get('pricing_inputs', {}).get('basic_utility_price', 0) + meta_costs.get('utility', 0)) * 1.2, 4)
            }
        }
        if all(float(inputs.get(v, 0)) == 0.0 for v in ['ai_volume', 'advanced_volume', 'basic_marketing_volume', 'basic_utility_volume']):
            committed_amount = float(inputs.get('committed_amount', 0) or 0)
            rates = get_committed_amount_rates(inputs.get('country', 'India'), committed_amount)
            meta_costs = meta_costs_table.get(inputs.get('country', 'India'), meta_costs_table['Rest of the World'])
            ai_volume = float(inputs.get('ai_volume', 0) or 0)
            advanced_volume = float(inputs.get('advanced_volume', 0) or 0)
            basic_marketing_volume = float(inputs.get('basic_marketing_volume', 0) or 0)
            basic_utility_volume = float(inputs.get('basic_utility_volume', 0) or 0)
            platform_fee_total = float(platform_fee)  # You can adjust this if you want to sum other fees
            final_price_details = {
                'platform_fee_total': platform_fee_total,
                'fixed_platform_fee': platform_fee,
                'ai_messages': {
                    'volume': int(ai_volume),
                    'price_per_msg': round(rates['ai'] + meta_costs['ai'], 4),
                    'overage_price': round((rates['ai'] + meta_costs['ai']) * 1.2, 4)
                },
                'advanced_messages': {
                    'volume': int(advanced_volume),
                    'price_per_msg': round(rates['advanced'] + meta_costs['ai'], 4),
                    'overage_price': round((rates['advanced'] + meta_costs['ai']) * 1.2, 4)
                },
                'marketing_message': {
                    'volume': int(inputs.get('basic_marketing_volume', 0) or 0),
                    'price_per_msg': round(session.get('pricing_inputs', {}).get('basic_marketing_price', 0) + meta_costs.get('marketing', 0), 4),
                    'overage_price': round((session.get('pricing_inputs', {}).get('basic_marketing_price', 0) + meta_costs.get('marketing', 0)) * 1.2, 4)
                },
                'utility_message': {
                    'volume': int(inputs.get('basic_utility_volume', 0) or 0),
                    'price_per_msg': round(session.get('pricing_inputs', {}).get('basic_utility_price', 0) + meta_costs.get('utility', 0), 4),
                    'overage_price': round((session.get('pricing_inputs', {}).get('basic_utility_price', 0) + meta_costs.get('utility', 0)) * 1.2, 4)
                }
            }
            return render_template(
                'index.html',
                step='results',
                currency_symbol=currency_symbol,
                inclusions=final_inclusions,
                final_inclusions=final_inclusions,
                results=results,
                bundle_details=bundle_details,
                expected_invoice_amount=expected_invoice_amount,
                chosen_platform_fee=chosen_platform_fee,
                rate_card_platform_fee=rate_card_platform_fee,
                platform_fee=platform_fee,
                platform_fee_rate_card=rate_card_platform_fee,
                pricing_table=results['line_items'],
                margin_table=margin_line_items,
                user_selections=user_selections,
                inputs=inputs,
                contradiction_warning=contradiction_warning,
                top_users=top_users,
                total_mandays=total_mandays,
                total_dev_cost=total_dev_cost,
                dev_cost_currency=dev_cost_currency,
                manday_breakdown=manday_breakdown,
                manday_rates=manday_rates,
                calculation_id=calculation_id,
                dev_cost_breakdown=dev_cost_breakdown,
                final_price_details=final_price_details,
                pricing_simulation=None
            )
        # Recalculate platform fee for the current country and selections before rendering results
        country = inputs.get('country', 'India')
        platform_fee, fee_currency = calculate_platform_fee(
            country,
            inputs.get('bfsi_tier', 'NA'),
            inputs.get('personalize_load', 'NA'),
            inputs.get('human_agents', 'NA'),
            inputs.get('ai_module', 'NA'),
            inputs.get('smart_cpaas', 'No'),
            inputs.get('increased_tps', 'NA')
        )
        session['chosen_platform_fee'] = platform_fee
        if 'pricing_inputs' in session:
            session['pricing_inputs']['platform_fee'] = platform_fee
        # Use this platform_fee for all downstream calculations and rendering
        pricing_simulation = calculate_pricing_simulation(inputs)
        return render_template(
            'index.html',
            step='results',
            currency_symbol=currency_symbol,
            inclusions=final_inclusions,
            final_inclusions=final_inclusions,
            results=results,
            bundle_details=bundle_details,
            expected_invoice_amount=expected_invoice_amount,
            chosen_platform_fee=chosen_platform_fee,
            rate_card_platform_fee=rate_card_platform_fee,
            platform_fee=chosen_platform_fee,
            platform_fee_rate_card=rate_card_platform_fee,
            pricing_table=results['line_items'],
            margin_table=margin_line_items,
            user_selections=user_selections,
            inputs=inputs,
            contradiction_warning=contradiction_warning,
            top_users=top_users,
            total_mandays=total_mandays,
            total_dev_cost=total_dev_cost,
            dev_cost_currency=dev_cost_currency,
            manday_breakdown=manday_breakdown,
            manday_rates=manday_rates,
            calculation_id=calculation_id,
            dev_cost_breakdown=dev_cost_breakdown,
            final_price_details=final_price_details,
            pricing_simulation=pricing_simulation
        )
    # Defensive: handle GET or POST for edit actions
    elif step == 'volumes':
        inputs = session.get('inputs', {})
        if not inputs:
            if request.method == 'POST':
                flash('Session expired or missing. Please start again.', 'error')
            currency_symbol = COUNTRY_CURRENCY.get('India', '₹')
            return render_template('index.html', step='volumes', currency_symbol=currency_symbol, inputs={}, calculation_id=calculation_id)
        currency_symbol = COUNTRY_CURRENCY.get(inputs.get('country', 'India'), '$')
        return render_template('index.html', step='volumes', currency_symbol=currency_symbol, inputs=inputs, calculation_id=calculation_id)
    elif step == 'prices':
        inputs = session.get('inputs', {})
        pricing_inputs = session.get('pricing_inputs', {}) or {}
        country = inputs.get('country', 'India')
        dev_location = inputs.get('dev_location', 'India')
        # Get default rates
        country = inputs.get('country', 'India').strip()
        print(f"DEBUG: country used for manday rates = '{country}'", file=sys.stderr, flush=True)
        rates = COUNTRY_MANDAY_RATES.get(country, COUNTRY_MANDAY_RATES['Rest of the World'])
        if country == 'LATAM':
            default_bot_ui = float(rates['bot_ui'].get(dev_location, 0.0) or 0.0)
            default_custom_ai = float(rates['custom_ai'].get(dev_location, 0.0) or 0.0)
        else:
            default_bot_ui = float(rates.get('bot_ui', 0.0) or 0.0)
            default_custom_ai = float(rates.get('custom_ai', 0.0) or 0.0)
        if request.method == 'POST':
            # Validate user rates
            def parse_number(val):
                try:
                    return float(str(val).replace(',', '')) if val and str(val).strip() else 0.0
                except Exception:
                    return 0.0
            user_bot_ui = parse_number(request.form.get('bot_ui_manday_rate', default_bot_ui))
            user_custom_ai = parse_number(request.form.get('custom_ai_manday_rate', default_custom_ai))
            if user_bot_ui < 0.5 * default_bot_ui or user_custom_ai < 0.5 * default_custom_ai:
                flash('Manday rates cannot be discounted by more than 50% from the default rate.', 'error')
                return render_template('index.html', step='prices', suggested={
                    'ai_price': pricing_inputs.get('ai_price', ''),
                    'advanced_price': pricing_inputs.get('advanced_price', ''),
                    'basic_marketing_price': pricing_inputs.get('basic_marketing_price', ''),
                    'basic_utility_price': pricing_inputs.get('basic_utility_price', ''),
                    'bot_ui_manday_rate': default_bot_ui,
                    'custom_ai_manday_rate': default_custom_ai,
                }, inputs=inputs, currency_symbol=COUNTRY_CURRENCY.get(country, '$'), platform_fee=pricing_inputs.get('platform_fee', inputs.get('platform_fee', '')), calculation_id=calculation_id)
            # Save user rates for use in results
            session['manday_rates'] = {
                'bot_ui': user_bot_ui,
                'custom_ai': user_custom_ai,
                'default_bot_ui': default_bot_ui,
                'default_custom_ai': default_custom_ai,
            }
        else:
            # GET: pre-fill with defaults
            return render_template('index.html', step='prices', suggested={
                'ai_price': pricing_inputs.get('ai_price', ''),
                'advanced_price': pricing_inputs.get('advanced_price', ''),
                'basic_marketing_price': pricing_inputs.get('basic_marketing_price', ''),
                'basic_utility_price': pricing_inputs.get('basic_utility_price', ''),
                'bot_ui_manday_rate': default_bot_ui,
                'custom_ai_manday_rate': default_custom_ai,
            }, inputs=inputs, currency_symbol=COUNTRY_CURRENCY.get(country, '$'), platform_fee=pricing_inputs.get('platform_fee', inputs.get('platform_fee', '')), calculation_id=calculation_id)
    elif step == 'bundle' and request.method == 'POST':
        # User submitted messaging bundle commitment (can be 0)
        inputs = session.get('inputs', {}) or {}
        committed_amount = request.form.get('committed_amount', '0')
        # Remove commas if present
        try:
            committed_amount = float(str(committed_amount).replace(',', ''))
        except Exception:
            committed_amount = 0.0
        inputs['committed_amount'] = committed_amount
        session['inputs'] = inputs
        # Recalculate platform fee for the current country and selections
        country = inputs.get('country', 'India')
        platform_fee, fee_currency = calculate_platform_fee(
            country,
            inputs.get('bfsi_tier', 'NA'),
            inputs.get('personalize_load', 'NA'),
            inputs.get('human_agents', 'NA'),
            inputs.get('ai_module', 'NA'),
            inputs.get('smart_cpaas', 'No'),
            inputs.get('increased_tps', 'NA')
        )
        session['chosen_platform_fee'] = platform_fee
        # Go to prices page
        pricing_inputs = session.get('pricing_inputs', {}) or {}
        dev_location = inputs.get('dev_location', 'India')
        rates = COUNTRY_MANDAY_RATES.get(country, COUNTRY_MANDAY_RATES['Rest of the World'])
        if country == 'LATAM':
            default_bot_ui = float(rates['bot_ui'].get(dev_location, 0.0) or 0.0)
            default_custom_ai = float(rates['custom_ai'].get(dev_location, 0.0) or 0.0)
        else:
            default_bot_ui = float(rates.get('bot_ui', 0.0) or 0.0)
            default_custom_ai = float(rates.get('custom_ai', 0.0) or 0.0)
        # --- Set default per-message prices for all countries based on committed amount using committed_amount_slabs ---
        slabs = committed_amount_slabs.get(country, committed_amount_slabs.get('Rest of the World', []))
        # Find the correct slab for the committed amount
        selected_slab = None
        for lower, upper, rates in slabs:
            if lower <= committed_amount < upper:
                selected_slab = rates
                break
        if not selected_slab and slabs:
            # If above all slabs, use the highest slab
            selected_slab = slabs[-1][2]
        suggested_prices = {
            'ai_price': selected_slab['ai'] if selected_slab else '',
            'advanced_price': selected_slab['advanced'] if selected_slab else '',
            'basic_marketing_price': selected_slab['basic_marketing'] if selected_slab else '',
            'basic_utility_price': selected_slab['basic_utility'] if selected_slab else '',
            'bot_ui_manday_rate': default_bot_ui,
            'custom_ai_manday_rate': default_custom_ai,
        }
        suggested_prices = patch_suggested_prices(suggested_prices, inputs)
        return render_template('index.html', step='prices', suggested=suggested_prices, inputs=inputs, currency_symbol=COUNTRY_CURRENCY.get(country, '$'), platform_fee=pricing_inputs.get('platform_fee', inputs.get('platform_fee', '')), calculation_id=calculation_id)
    # Default: show volume input form
    country = session.get('inputs', {}).get('country', 'India')
    currency_symbol = COUNTRY_CURRENCY.get(country, '$')
    return render_template('index.html', step='volumes', currency_symbol=currency_symbol, inputs=session.get('inputs', {}), calculation_id=calculation_id)

@app.route('/analytics', methods=['GET', 'POST'])
def analytics():
    try:
        if request.method == 'POST':
            keyword = request.form.get('keyword', '')
            if keyword == SECRET_ANALYTICS_KEYWORD:
                # Query the database for analytics
                total_calculations = Analytics.query.count()
                # Calculations by day
                calculations_by_day = {str(row[0]): row[1] for row in db.session.query(func.date(Analytics.timestamp), func.count()).group_by(func.date(Analytics.timestamp)).all()}
                # Calculations by week
                calculations_by_week = {str(row[0]): row[1] for row in db.session.query(
                    func.to_char(Analytics.timestamp, 'IYYY-"W"IW'),
                    func.count()
                ).group_by(
                    func.to_char(Analytics.timestamp, 'IYYY-"W"IW')
                ).all()}
                # Most common countries
                from collections import Counter
                country_list = [row[0] for row in db.session.query(Analytics.country).all() if row[0] is not None]
                country_counter = Counter(country_list).most_common(5)
                # Platform fee stats
                platform_fees = [row[0] for row in db.session.query(Analytics.platform_fee).all() if row[0] is not None]
                if platform_fees:
                    avg_platform_fee = sum(platform_fees) / len(platform_fees)
                    min_platform_fee = min(platform_fees)
                    max_platform_fee = max(platform_fees)
                    median_platform_fee = sorted(platform_fees)[len(platform_fees)//2]
                else:
                    avg_platform_fee = min_platform_fee = max_platform_fee = median_platform_fee = 0
                # Platform fee options (most common platform_fee values)
                platform_fee_options = Counter(platform_fees).most_common(5)
                # Message price stats by type
                def get_stats(field):
                    vals = [getattr(a, field) for a in Analytics.query.all() if getattr(a, field) is not None]
                    if vals:
                        return {
                            'avg': sum(vals)/len(vals),
                            'min': min(vals),
                            'max': max(vals),
                            'median': sorted(vals)[len(vals)//2]
                        }
                    else:
                        return {'avg': 0, 'min': 0, 'max': 0, 'median': 0}
                ai_stats = get_stats('ai_price')
                advanced_stats = get_stats('advanced_price')
                marketing_stats = get_stats('basic_marketing_price')
                utility_stats = get_stats('basic_utility_price')
                # Message volume distribution (sum, min, max, median for each type)
                def get_volume_stats(field):
                    vals = [getattr(a, field) for a in Analytics.query.all() if getattr(a, field) is not None]
                    if vals:
                        return [sum(vals), min(vals), max(vals), sorted(vals)[len(vals)//2]]
                    else:
                        return [0, 0, 0, 0]
                message_volumes = {
                    'ai': get_volume_stats('ai_price'),
                    'advanced': get_volume_stats('advanced_price'),
                    'basic_marketing': get_volume_stats('basic_marketing_price'),
                    'basic_utility': get_volume_stats('basic_utility_price')
                }
                # Platform fee discount triggered (count)
                platform_fee_discount_triggered = db.session.query(Analytics).filter(Analytics.platform_fee < 0.3 * avg_platform_fee).count() if avg_platform_fee else 0
                # Margin chosen and rate card (dummy values for now, replace with real if available)
                margin_chosen = [95.825]  # Example value, replace with real calculation if available
                margin_rate_card = [0.0]  # Example value, replace with real calculation if available
                # Per-country stats for table
                stats = {}
                stats_by_region = {}
                countries = set(country_list)
                for country in countries:
                    country_analytics = Analytics.query.filter_by(country=country).all()
                    # Group by region within country
                    region_map = {}
                    for a in country_analytics:
                        region = getattr(a, 'region', '') or 'All'
                        if region == 'All' or not region:
                            region = a.country
                        if region not in region_map:
                            region_map[region] = []
                        region_map[region].append(a)
                    stats_by_region[country] = {}
                    for region, region_analytics in region_map.items():
                        country_fees = [a.platform_fee for a in region_analytics if a.platform_fee is not None]
                        country_ai = [a.ai_price for a in region_analytics if a.ai_price is not None]
                        country_adv = [a.advanced_price for a in region_analytics if a.advanced_price is not None]
                        country_mark = [a.basic_marketing_price for a in region_analytics if a.basic_marketing_price is not None]
                        country_util = [a.basic_utility_price for a in region_analytics if a.basic_utility_price is not None]
                        country_committed = [a.committed_amount for a in region_analytics if a.committed_amount not in (None, 0, '0', '', 'None')]
                        # --- One Time Dev Cost Aggregation ---
                        dev_costs = []
                        bot_ui_rates = [a.bot_ui_manday_rate for a in region_analytics if a.bot_ui_manday_rate not in (None, 0, '0', '', 'None')]
                        custom_ai_rates = [a.custom_ai_manday_rate for a in region_analytics if a.custom_ai_manday_rate not in (None, 0, '0', '', 'None')]
                        bot_ui_mandays = [getattr(a, 'bot_ui_mandays', None) for a in region_analytics]
                        custom_ai_mandays = [getattr(a, 'custom_ai_mandays', None) for a in region_analytics]
                        for a in region_analytics:
                            bot_ui_rate = a.bot_ui_manday_rate if a.bot_ui_manday_rate is not None else 0
                            custom_ai_rate = a.custom_ai_manday_rate if a.custom_ai_manday_rate is not None else 0
                            bot_days = getattr(a, 'bot_ui_mandays', 0) or 0
                            ai_days = getattr(a, 'custom_ai_mandays', 0) or 0
                            dev_cost = (bot_ui_rate * bot_days) + (custom_ai_rate * ai_days)
                            dev_costs.append(dev_cost)
                        def stat_dict(vals):
                            filtered = [float(v) for v in vals if v not in (None, 0, '0', '', 'None')]
                            if not filtered:
                                return {'avg': 0, 'min': 0, 'max': 0, 'median': 0}
                            avg = sum(filtered) / len(filtered)
                            min_v = min(filtered)
                            max_v = max(filtered)
                            sorted_vals = sorted(filtered)
                            n = len(sorted_vals)
                            if n % 2 == 1:
                                median = sorted_vals[n // 2]
                            else:
                                median = (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2
                            return {'avg': avg, 'min': min_v, 'max': max_v, 'median': median}
                        stats_by_region[country][region] = {
                            'platform_fee': stat_dict(country_fees),
                            'msg_types': {
                                'ai': {
                                    'avg': sum(country_ai)/len(country_ai) if country_ai else 0,
                                    'min': min(country_ai) if country_ai else 0,
                                    'max': max(country_ai) if country_ai else 0,
                                    'median': sorted(country_ai)[len(country_ai)//2] if country_ai else 0
                                },
                                'advanced': {
                                    'avg': sum(country_adv)/len(country_adv) if country_adv else 0,
                                    'min': min(country_adv) if country_adv else 0,
                                    'max': max(country_adv) if country_adv else 0,
                                    'median': sorted(country_adv)[len(country_adv)//2] if country_adv else 0
                                },
                                'basic_marketing': {
                                    'avg': sum(country_mark)/len(country_mark) if country_mark else 0,
                                    'min': min(country_mark) if country_mark else 0,
                                    'max': max(country_mark) if country_mark else 0,
                                    'median': sorted(country_mark)[len(country_mark)//2] if country_mark else 0
                                },
                                'basic_utility': {
                                    'avg': sum(country_util)/len(country_util) if country_util else 0,
                                    'min': min(country_util) if country_util else 0,
                                    'max': max(country_util) if country_util else 0,
                                    'median': sorted(country_util)[len(country_util)//2] if country_util else 0
                                }
                            },
                            'committed_amount': stat_dict(country_committed),
                            'one_time_dev_cost': stat_dict(dev_costs),
                            'bot_ui_manday_cost': stat_dict(bot_ui_rates),
                            'custom_ai_manday_cost': stat_dict(custom_ai_rates)
                        }
                    # For backward compatibility, keep the old stats[country] as the sum of all regions
                    stats[country] = stats_by_region[country].get('All', list(stats_by_region[country].values())[0])
                # --- Add average discount per country for all message types and manday rates ---
                def avg_discount(chosen_list, rate_card_list):
                    pairs = [
                        (c, r)
                        for c, r in zip(chosen_list, rate_card_list)
                        if isinstance(c, (int, float)) and isinstance(r, (int, float)) and r
                    ]
                    if not pairs:
                        return 0.0
                    return 100 * sum((r - c) / r for c, r in pairs) / len(pairs)
                for country in countries:
                    country_analytics = Analytics.query.filter_by(country=country).all()
                    # Message types
                    ai_chosen = [a.ai_price for a in country_analytics if a.ai_price is not None]
                    ai_rate = [a.ai_rate_card_price for a in country_analytics if a.ai_rate_card_price is not None]
                    adv_chosen = [a.advanced_price for a in country_analytics if a.advanced_price is not None]
                    adv_rate = [a.advanced_rate_card_price for a in country_analytics if a.advanced_rate_card_price is not None]
                    mark_chosen = [a.basic_marketing_price for a in country_analytics if a.basic_marketing_price is not None]
                    mark_rate = [a.basic_marketing_rate_card_price for a in country_analytics if a.basic_marketing_rate_card_price is not None]
                    util_chosen = [a.basic_utility_price for a in country_analytics if a.basic_utility_price is not None]
                    util_rate = [a.basic_utility_rate_card_price for a in country_analytics if a.basic_utility_rate_card_price is not None]
                    # Manday rates
                    bot_ui_chosen = [a.bot_ui_manday_rate for a in country_analytics if a.bot_ui_manday_rate not in (None, 0, '0', '', 'None')]
                    bot_ui_rate = [COUNTRY_MANDAY_RATES.get(country, COUNTRY_MANDAY_RATES['Rest of the World'])['bot_ui'] for _ in bot_ui_chosen]
                    custom_ai_chosen = [a.custom_ai_manday_rate for a in country_analytics if a.custom_ai_manday_rate not in (None, 0, '0', '', 'None')]
                    custom_ai_rate = [COUNTRY_MANDAY_RATES.get(country, COUNTRY_MANDAY_RATES['Rest of the World'])['custom_ai'] for _ in custom_ai_chosen]
                    stats[country]['avg_discount'] = {
                        'ai': avg_discount(ai_chosen, ai_rate),
                        'advanced': avg_discount(adv_chosen, adv_rate),
                        'basic_marketing': avg_discount(mark_chosen, mark_rate),
                        'basic_utility': avg_discount(util_chosen, util_rate),
                        'bot_ui_manday': avg_discount(bot_ui_chosen, bot_ui_rate),
                        'custom_ai_manday': avg_discount(custom_ai_chosen, custom_ai_rate),
                    }
                # Defensive: Ensure every stat in analytics['stats'] is a dict
                for country in list(stats.keys()):
                    if not isinstance(stats[country], dict):
                        stats[country] = {}
                # Debug: Print stats structure before rendering
                print('DEBUG: analytics["stats"] structure:', file=sys.stderr, flush=True)
                for country, stat in stats.items():
                    # Debug: Check if stat is a dict or something else
                    # print(f'  {country}: {type(stat)} = {stat}')
                    pass
                print('--- END DEBUG ---', file=sys.stderr, flush=True)
                # Per-user stats for table
                user_stats = {}
                user_country_currency_list = db.session.query(Analytics.user_name, Analytics.country, Analytics.currency).distinct().all()
                for user, country, currency in user_country_currency_list:
                    user_entries = Analytics.query.filter_by(user_name=user, country=country, currency=currency).all()
                    def get_user_stats(field):
                        vals = [getattr(a, field) for a in user_entries if getattr(a, field) is not None]
                        if vals:
                            return {
                                'avg': sum(vals)/len(vals),
                                'min': min(vals),
                                'max': max(vals),
                                'median': sorted(vals)[len(vals)//2]
                            }
                        else:
                            return {'avg': 0, 'min': 0, 'max': 0, 'median': 0}
                    # Add one_time_dev_cost and per_manday_cost for user/country/currency
                    rates = COUNTRY_MANDAY_RATES.get(country, COUNTRY_MANDAY_RATES['Rest of the World'])
                    if country == 'LATAM':
                        if isinstance(rates['bot_ui'], dict):
                            bot_ui_rate = rates['bot_ui'].get(country, list(rates['bot_ui'].values())[0])
                        else:
                            bot_ui_rate = rates['bot_ui']
                        if isinstance(rates['custom_ai'], dict):
                            custom_ai_rate = rates['custom_ai'].get(country, list(rates['custom_ai'].values())[0])
                        else:
                            custom_ai_rate = rates['custom_ai']
                    else:
                        bot_ui_rate = rates['bot_ui']
                        custom_ai_rate = rates['custom_ai']
                    per_manday_cost = (bot_ui_rate + custom_ai_rate) / 2
                    dev_cost = bot_ui_rate + custom_ai_rate
                    one_time_dev_cost_stats = {'avg': dev_cost, 'min': dev_cost, 'max': dev_cost, 'median': dev_cost}
                    per_manday_cost_stats = {'avg': per_manday_cost, 'min': per_manday_cost, 'max': per_manday_cost, 'median': per_manday_cost}
                    user_stats.setdefault(user, {})[(country, currency)] = {
                        'platform_fee': get_user_stats('platform_fee'),
                        'ai': get_user_stats('ai_price'),
                        'advanced': get_user_stats('advanced_price'),
                        'basic_marketing': get_user_stats('basic_marketing_price'),
                        'basic_utility': get_user_stats('basic_utility_price'),
                        'committed_amount': get_user_stats('committed_amount'),
                        'one_time_dev_cost': one_time_dev_cost_stats,
                        'per_manday_cost': per_manday_cost_stats
                    }
                # Compute avg_price_data and avg_platform_fee_data for Chart.js graphs
                avg_price_data = {}
                avg_platform_fee_data = {}
                for country in countries:
                    country_analytics = Analytics.query.filter_by(country=country).all()
                    avg_price_data[country] = {
                        'ai': {
                            'sum': sum(a.ai_price or 0 for a in country_analytics),
                            'count': len([a for a in country_analytics if a.ai_price is not None])
                        },
                        'advanced': {
                            'sum': sum(a.advanced_price or 0 for a in country_analytics),
                            'count': len([a for a in country_analytics if a.advanced_price is not None])
                        },
                        'basic_marketing': {
                            'sum': sum(a.basic_marketing_price or 0 for a in country_analytics),
                            'count': len([a for a in country_analytics if a.basic_marketing_price is not None])
                        },
                        'basic_utility': {
                            'sum': sum(a.basic_utility_price or 0 for a in country_analytics),
                            'count': len([a for a in country_analytics if a.basic_utility_price is not None])
                        }
                    }
                    avg_platform_fee_data[country] = {
                        'sum': sum(a.platform_fee or 0 for a in country_analytics),
                        'count': len([a for a in country_analytics if a.platform_fee is not None])
                    }
                # Top users by number of calculations (show all, not just top 5)
                user_names = [row[0] for row in db.session.query(Analytics.user_name).all() if row[0]]
                top_users = Counter(user_names).most_common()  # Remove the 5 limit
                all_analytics = Analytics.query.all()
                # Add calculation route counts
                volumes_count = Analytics.query.filter_by(calculation_route='volumes').count()
                bundle_count = Analytics.query.filter_by(calculation_route='bundle').count()
                analytics = {
                    'calculations': total_calculations,
                    'volumes_count': volumes_count,
                    'bundle_count': bundle_count,
                    'calculations_by_day': calculations_by_day,
                    'calculations_by_week': calculations_by_week,
                    'country_counter': country_counter,
                    'platform_fee_stats': {
                        'avg': avg_platform_fee,
                        'min': min_platform_fee,
                        'max': max_platform_fee,
                        'median': median_platform_fee
                    },
                    'platform_fee_options': platform_fee_options,
                    'ai_stats': ai_stats,
                    'advanced_stats': advanced_stats,
                    'marketing_stats': marketing_stats,
                    'utility_stats': utility_stats,
                    'message_volumes': message_volumes,
                    'platform_fee_discount_triggered': platform_fee_discount_triggered,
                    'margin_chosen': margin_chosen,
                    'margin_rate_card': margin_rate_card,
                    'stats': stats,
                    'discount_warnings': {},
                    'avg_price_data': avg_price_data,
                    'avg_platform_fee_data': avg_platform_fee_data,
                    'top_users': top_users,
                    'user_stats': user_stats,
                    'all_analytics': all_analytics,
                    'stats_by_region': stats_by_region,
                }
                # --- Advanced Analytics Calculations ---
                # 1. Discount calculations (by type and platform fee)
                def get_discount_stats(price_field, rate_card_field):
                    discounts = []
                    for a in Analytics.query.all():
                        price = getattr(a, price_field, None)
                        rate_card = getattr(a, rate_card_field, None)
                        if price is not None and rate_card is not None and rate_card > 0:
                            discount = (rate_card - price) / rate_card * 100
                            discounts.append(discount)
                    if discounts:
                        avg = sum(discounts) / len(discounts)
                        minv = min(discounts)
                        maxv = max(discounts)
                        median = sorted(discounts)[len(discounts)//2]
                    else:
                        avg = minv = maxv = median = 0
                    # Distribution buckets (0-10%, 10-20%, ...)
                    buckets = [0]*10
                    for d in discounts:
                        idx = min(max(int(d // 10), 0), 9)
                        buckets[idx] += 1
                    return {'avg': avg, 'min': minv, 'max': maxv, 'median': median, 'buckets': buckets, 'count': len(discounts)}

                ai_discount = get_discount_stats('ai_price', 'ai_rate_card_price')
                advanced_discount = get_discount_stats('advanced_price', 'advanced_rate_card_price')
                marketing_discount = get_discount_stats('basic_marketing_price', 'basic_marketing_rate_card_price')
                utility_discount = get_discount_stats('basic_utility_price', 'basic_utility_rate_card_price')
                platform_fee_discount = get_discount_stats('platform_fee', 'platform_fee')  # always 0, but for completeness

                # 2. Most common prices (mode)
                def get_mode(field):
                    vals = [getattr(a, field) for a in Analytics.query.all() if getattr(a, field) is not None]
                    if vals:
                        return Counter(vals).most_common(1)[0][0]
                    return None
                ai_mode = get_mode('ai_price')
                advanced_mode = get_mode('advanced_price')
                marketing_mode = get_mode('basic_marketing_price')
                utility_mode = get_mode('basic_utility_price')
                platform_fee_mode = get_mode('platform_fee')

                # 3. Popular message types (by total volume)
                def get_total_volume(field):
                    return sum(getattr(a, field) or 0 for a in Analytics.query.all())
                total_ai_vol = get_total_volume('ai_volume')
                total_adv_vol = get_total_volume('advanced_volume')
                total_marketing_vol = get_total_volume('basic_marketing_volume')
                total_utility_vol = get_total_volume('basic_utility_volume')
                popular_types = sorted([
                    ('AI', total_ai_vol),
                    ('Advanced', total_adv_vol),
                    ('Marketing', total_marketing_vol),
                    ('Utility', total_utility_vol)
                ], key=lambda x: x[1], reverse=True)

                # 4. Platform fee vs. deal size (correlation)
                import math
                fees = [a.platform_fee for a in Analytics.query.all() if a.platform_fee is not None]
                deal_sizes = [
                    (getattr(a, 'ai_volume') or 0) + (getattr(a, 'advanced_volume') or 0) +
                    (getattr(a, 'basic_marketing_volume') or 0) + (getattr(a, 'basic_utility_volume') or 0)
                    for a in Analytics.query.all()
                ]
                if fees and deal_sizes and len(fees) == len(deal_sizes):
                    n = len(fees)
                    mean_fee = sum(fees)/n
                    mean_deal = sum(deal_sizes)/n
                    cov = sum((fees[i]-mean_fee)*(deal_sizes[i]-mean_deal) for i in range(n)) / n
                    std_fee = math.sqrt(sum((f-mean_fee)**2 for f in fees)/n)
                    std_deal = math.sqrt(sum((d-mean_deal)**2 for d in deal_sizes)/n)
                    correlation = cov / (std_fee*std_deal) if std_fee and std_deal else 0
                else:
                    correlation = 0

                # 5. Seasonality (by month)
                from collections import defaultdict
                month_counts = defaultdict(int)
                for a in Analytics.query.all():
                    if a.timestamp:
                        month = a.timestamp.strftime('%Y-%m')
                        month_counts[month] += 1
                seasonality = dict(sorted(month_counts.items()))

                # Add to analytics dict
                analytics.update({
                    'discounts': {
                        'ai': ai_discount,
                        'advanced': advanced_discount,
                        'marketing': marketing_discount,
                        'utility': utility_discount,
                        'platform_fee': platform_fee_discount
                    },
                    'modes': {
                        'ai': ai_mode,
                        'advanced': advanced_mode,
                        'marketing': marketing_mode,
                        'utility': utility_mode,
                        'platform_fee': platform_fee_mode
                    },
                    'popular_types': popular_types,
                    'platform_fee_vs_deal_correlation': correlation,
                    'seasonality': seasonality
                })
                # Debug: Log manday rates and breakdown before saving to Analytics
                #print(f"DEBUG: About to save Analytics record with bot_ui_manday_rate={manday_rates.get('bot_ui')}, custom_ai_manday_rate={manday_rates.get('custom_ai')}, bot_ui_mandays={manday_breakdown.get('bot_ui', 0)}, custom_ai_mandays={manday_breakdown.get('custom_ai', 0)}")
                return render_template('analytics.html', authorized=True, analytics=analytics)
            else:
                flash('Incorrect keyword.', 'error')
                return render_template('analytics.html', authorized=False, analytics={})
        # GET request or any other case
        return render_template('analytics.html', authorized=False, analytics={})
    except Exception as e:
        import traceback
        print("ANALYTICS ERROR:", e, file=sys.stderr, flush=True)
        traceback.print_exc()
        return "Internal Server Error (analytics)", 500

@app.route('/reset-analytics', methods=['POST'])
def reset_analytics():
    """
    Resets the analytics_data dictionary to its initial state.
    """
    db.session.query(Analytics).delete()
    db.session.commit()
    return 'Analytics reset successfully', 200

@app.route('/readme')
def readme():
    """Render the native HTML documentation page."""
    return render_template('readme.html')

# --- Minimal session test routes ---
@app.route('/set-session')
def set_session():
    session['test'] = 'hello'
    return 'Session set!'

@app.route('/get-session')
def get_session():
    return f"Session value: {session.get('test', 'not set')}"

# --- PATCH: Ensure manday rates always included in suggested_prices for 'prices' step ---
def get_default_manday_rates(inputs):
    country = inputs.get('country', 'India') if inputs else 'India'
    dev_location = inputs.get('dev_location', 'India') if inputs else 'India'
    from calculator import COUNTRY_MANDAY_RATES
    rates = COUNTRY_MANDAY_RATES.get(country, COUNTRY_MANDAY_RATES['Rest of the World'])
    if country == 'LATAM':
        default_bot_ui = rates['bot_ui'][dev_location]
        default_custom_ai = rates['custom_ai'][dev_location]
    else:
        default_bot_ui = rates['bot_ui']
        default_custom_ai = rates['custom_ai']
    return default_bot_ui, default_custom_ai

# --- PATCH: Wrap all suggested_prices dicts before rendering 'prices' step ---
def patch_suggested_prices(suggested_prices, inputs):
    default_bot_ui, default_custom_ai = get_default_manday_rates(inputs)
    if 'bot_ui_manday_rate' not in suggested_prices or suggested_prices['bot_ui_manday_rate'] is None:
        suggested_prices['bot_ui_manday_rate'] = default_bot_ui
    if 'custom_ai_manday_rate' not in suggested_prices or suggested_prices['custom_ai_manday_rate'] is None:
        suggested_prices['custom_ai_manday_rate'] = default_custom_ai
    return suggested_prices

@app.route('/analyticsv2', methods=['GET'])
def analytics_v2():
    """
    New advanced analytics and reporting page using analytics.csv.
    """
    return render_template('analyticsv2.html')

def calculate_pricing_simulation(inputs):
    """
    Returns a dict with detailed calculations for both volume and committed amount routes for the given user inputs.
    """
    country = inputs.get('country', 'India')
    ai_volume = float(inputs.get('ai_volume', 0) or 0)
    advanced_volume = float(inputs.get('advanced_volume', 0) or 0)
    basic_marketing_volume = float(inputs.get('basic_marketing_volume', 0) or 0)
    basic_utility_volume = float(inputs.get('basic_utility_volume', 0) or 0)
    platform_fee = float(inputs.get('platform_fee', 0) or 0)
    committed_amount = float(inputs.get('committed_amount', 0) or 0)
    from pricing_config import price_tiers, meta_costs_table, committed_amount_slabs
    meta_costs = meta_costs_table.get(country, meta_costs_table['Rest of the World'])
    def get_lowest_tier(country, msg_type):
        tiers = price_tiers.get(country, {}).get(msg_type, [])
        return tiers[0][2] if tiers else 0.0
    ai_price_vol = get_lowest_tier(country, 'ai')
    adv_price_vol = get_lowest_tier(country, 'advanced')
    ai_final_vol = ai_price_vol + meta_costs['ai']
    adv_final_vol = adv_price_vol + meta_costs['ai']
    ai_cost_vol = ai_volume * ai_final_vol
    adv_cost_vol = advanced_volume * adv_final_vol
    total_vol = ai_cost_vol + adv_cost_vol + platform_fee
    slabs = committed_amount_slabs.get(country, committed_amount_slabs['Rest of the World'])
    def get_slab_rate(msg_type, volume):
        for lower, upper, rates in slabs:
            rate = rates[msg_type]
            est_amount = volume * rate
            if lower <= est_amount < upper:
                return rate, lower, upper
        return slabs[0][2][msg_type], slabs[0][0], slabs[0][1]
    ai_rate_bundle, ai_slab_low, ai_slab_high = get_slab_rate('ai', ai_volume)
    adv_rate_bundle, adv_slab_low, adv_slab_high = get_slab_rate('advanced', advanced_volume)
    ai_final_bundle = ai_rate_bundle + meta_costs['ai']
    adv_final_bundle = adv_rate_bundle + meta_costs['ai']
    # If committed_amount is 0, suggest a value that covers the entered volumes
    if committed_amount == 0:
        committed_amount = (ai_volume * ai_final_bundle) + (advanced_volume * adv_final_bundle)
    included_ai = committed_amount / ai_final_bundle if ai_final_bundle else 0
    included_adv = committed_amount / adv_final_bundle if adv_final_bundle else 0
    ai_overage = max(0, ai_volume - included_ai)
    adv_overage = max(0, advanced_volume - included_adv)
    ai_overage_rate = ai_final_bundle * 1.2
    adv_overage_rate = adv_final_bundle * 1.2
    ai_overage_cost = ai_overage * ai_overage_rate
    adv_overage_cost = adv_overage * adv_overage_rate
    total_bundle = committed_amount + ai_overage_cost + adv_overage_cost + platform_fee
    return {
        'volume_route': {
            'ai_price': ai_final_vol, 'adv_price': adv_final_vol,
            'ai_cost': ai_cost_vol, 'adv_cost': adv_cost_vol,
            'platform_fee': platform_fee, 'total': total_vol,
            'ai_volume': ai_volume, 'adv_volume': advanced_volume
        },
        'bundle_route': {
            'ai_price': ai_final_bundle, 'adv_price': adv_final_bundle,
            'ai_slab': (ai_slab_low, ai_slab_high), 'adv_slab': (adv_slab_low, adv_slab_high),
            'included_ai': included_ai, 'included_adv': included_adv,
            'ai_overage': ai_overage, 'adv_overage': adv_overage,
            'ai_overage_rate': ai_overage_rate, 'adv_overage_rate': adv_overage_rate,
            'ai_overage_cost': ai_overage_cost, 'adv_overage_cost': adv_overage_cost,
            'committed_amount': committed_amount, 'platform_fee': platform_fee, 'total': total_bundle,
            'ai_volume': ai_volume, 'adv_volume': advanced_volume
        }
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Flask app on port {port}")
    print(f"STARTING FLASK APP ON PORT {port}", file=sys.stderr, flush=True)
    app.run(host='0.0.0.0', port=port, debug=True)