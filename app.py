# --- Flask Pricing Calculator Application ---
# This app provides a pricing calculator for messaging services with dynamic inclusions, platform fees, and analytics.
# Key features: dynamic inclusions, robust error handling, session management, and professional UI.

from flask import Flask, render_template, request, session, redirect, url_for, flash
from calculator import calculate_pricing, get_suggested_price, price_tiers, meta_costs_table, calculate_total_mandays, calculate_total_manday_cost, COUNTRY_MANDAY_RATES, calculate_total_mandays_breakdown
import os
# from google_auth_oauthlib.flow import Flow
# from googleapiclient.discovery import build
# from google.oauth2.credentials import Credentials
import re
from collections import Counter, defaultdict
import statistics
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from sqlalchemy import func
import uuid
from calculator import get_committed_amount_rates
from pricing_config import COUNTRY_CURRENCY
from utils import parse_volume, parse_price, is_zero

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session

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
    # Add more fields as needed

# os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # For local testing only

SECRET_ANALYTICS_KEYWORD = "letmein123"

def initialize_inclusions():
    """
    Returns a dictionary of all possible inclusions for each feature/tier.
    Only the inclusions for the highest/most specific tier in each category should be shown.
    """
    inclusions = {
        'Platform Fee Used for Margin Calculation': [
            'Journey Builder Lite',
            'Campaign Manager',
            'CTWA (Meta, Tiktok)',
            'Agent Assist <20',
            'Personalize Lite (upto 1ml and no advanced events)',
            '80 TPS',
            '1 manday/month maintenance'
        ],
        'Personalize Load Lite': [
            'personalize lite upto 1 million records - no advanced events'
        ],
        'Human Agents <20': [
            'Agent Assist < 20 Agents,'
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
            'Data Encryption, Logging, Auditing, Purging (Logs) on  Reatargetting and Personalize'
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
        'Human Agents 20+': [
            '20-50 agents'
        ],
        'Human Agents 50+': [
            '50-100 agents'
        ],
        'Human Agents 100+': [
            'More than 100 agents, advanced routing rules'
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
    """
    # 1. Minimum platform fee (UPDATED)
    if country == 'India':
        min_fee = 120000
        currency = 'INR'
    elif country == 'Africa':
        min_fee = 1000
        currency = 'USD'
    elif country == 'Europe':
        min_fee = 2500
        currency = 'USD'
    else:
        min_fee = 2000
        currency = 'USD'
    fee = min_fee
    # 2. BFSI tier
    if bfsi_tier == 'Tier 1':
        if country == 'India': fee += 250000
        elif country == 'Africa': fee += 500
        else: fee += 1500
    elif bfsi_tier == 'Tier 2':
        if country == 'India': fee += 500000
        elif country == 'Africa': fee += 1000
        else: fee += 3000
    elif bfsi_tier == 'Tier 3':
        if country == 'India': fee += 800000
        elif country == 'Africa': fee += 1500
        else: fee += 5000
    # 3. Personalize load
    if personalize_load == 'Standard':
        if country == 'India': fee += 50000
        elif country == 'Africa': fee += 250
        else: fee += 500
    elif personalize_load == 'Advanced':
        if country == 'India': fee += 100000
        elif country == 'Africa': fee += 500
        else: fee += 1000
    # 4. Human agents (Agent Assist)
    if human_agents == '20+':
        if country == 'India': fee += 50000
        elif country == 'Africa': fee += 250
        elif country in ['LATAM', 'Europe']: fee += 1000
        else: fee += 500
    elif human_agents == '50+':
        if country == 'India': fee += 75000
        elif country == 'Africa': fee += 400
        elif country in ['LATAM', 'Europe']: fee += 1200
        else: fee += 700
    elif human_agents == '100+':
        if country == 'India': fee += 100000
        elif country == 'Africa': fee += 500
        elif country in ['LATAM', 'Europe']: fee += 1500
        else: fee += 1000
    # 5. AI Module Yes/No
    if ai_module == 'Yes':
        if country == 'India': fee += 50000
        elif country == 'Africa': fee += 250
        elif country in ['LATAM', 'Europe']: fee += 1000
        else: fee += 500
    # Smart CPaaS
    if smart_cpaas == 'Yes':
        if country == 'India':
            fee += 25000
        else:
            fee += 250
    # 6. Increased TPS
    if increased_tps == '250':
        if country == 'India': fee += 50000
        elif country == 'Africa': fee += 250
        else: fee += 500
    elif increased_tps == '1000':
        if country == 'India': fee += 100000
        elif country == 'Africa': fee += 500
        else: fee += 1000
    return fee, currency

def handle_volumes_step(request, session):
    # Clear previous session state for a new calculation
    for key in ['chosen_platform_fee', 'pricing_inputs', 'rate_card_platform_fee', 'results', 'selected_components', 'user_selections', 'inclusions']:
        if key in session:
            session.pop(key)
    calculation_id = str(uuid.uuid4())
    session['calculation_id'] = calculation_id
    user_name = request.form.get('user_name', '')
    country = request.form['country']
    ai_volume = int(float(request.form.get('ai_volume', '0') or 0))
    advanced_volume = int(float(request.form.get('advanced_volume', '0') or 0))
    basic_marketing_volume = int(float(request.form.get('basic_marketing_volume', '0') or 0))
    basic_utility_volume = int(float(request.form.get('basic_utility_volume', '0') or 0))
    bfsi_tier = request.form.get('bfsi_tier', 'NA')
    personalize_load = request.form.get('personalize_load', 'NA')
    human_agents = request.form.get('human_agents', 'NA')
    ai_module = request.form.get('ai_module', 'NA')
    smart_cpaas = request.form.get('smart_cpaas', 'No')
    increased_tps = request.form.get('increased_tps', 'NA')
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
    session['inputs'] = {
        'user_name': user_name,
        'country': country,
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
        'onboarding_price': onboarding_price,
        'ux_price': ux_price,
        'testing_qa_price': testing_qa_price,
        'aa_setup_price': aa_setup_price,
        'num_apis_price': num_apis_price,
        'num_journeys_price': num_journeys_price,
        'num_ai_workspace_commerce_price': num_ai_workspace_commerce_price,
        'num_ai_workspace_faq_price': num_ai_workspace_faq_price
    }
    if all(float(v) == 0.0 for v in [ai_volume, advanced_volume, basic_marketing_volume, basic_utility_volume]):
        return render_template('index.html', step='bundle', currency_symbol=currency_symbol, inputs=session.get('inputs', {}), platform_fee=platform_fee, calculation_id=calculation_id)
    suggested_prices = {
        'ai_price': get_suggested_price(country, 'ai', ai_volume) if ai_volume != 0 else get_lowest_tier_price(country, 'ai'),
        'advanced_price': get_suggested_price(country, 'advanced', advanced_volume) if advanced_volume != 0 else get_lowest_tier_price(country, 'advanced'),
        'basic_marketing_price': get_suggested_price(country, 'basic_marketing', basic_marketing_volume) if basic_marketing_volume != 0 else get_lowest_tier_price(country, 'basic_marketing'),
        'basic_utility_price': get_suggested_price(country, 'basic_utility', basic_utility_volume) if basic_utility_volume != 0 else get_lowest_tier_price(country, 'basic_utility'),
    }
    suggested_prices = patch_suggested_prices(suggested_prices, session.get('inputs', {}))
    return render_template('index.html', step='prices', suggested=suggested_prices, inputs=session.get('inputs', {}), currency_symbol=currency_symbol, platform_fee=platform_fee, calculation_id=calculation_id)


def handle_prices_step(request, session):
    inputs = session.get('inputs', {})
    if not inputs:
        flash('Session expired or missing. Please start again.', 'error')
        return redirect(url_for('index'))
    ai_price = parse_price(request.form.get('ai_price', ''))
    advanced_price = parse_price(request.form.get('advanced_price', ''))
    basic_marketing_price = parse_price(request.form.get('basic_marketing_price', ''))
    basic_utility_price = parse_price(request.form.get('basic_utility_price', ''))
    platform_fee = parse_price(request.form.get('platform_fee', '')) or 0.0
    bot_ui_manday_rate = parse_price(request.form.get('bot_ui_manday_rate', ''))
    custom_ai_manday_rate = parse_price(request.form.get('custom_ai_manday_rate', ''))
    session['manday_rates'] = {
        'bot_ui': bot_ui_manday_rate,
        'custom_ai': custom_ai_manday_rate
    }
    country = inputs.get('country', 'India')
    ai_volume = int(float(inputs.get('ai_volume', 0) or 0))
    advanced_volume = int(float(inputs.get('advanced_volume', 0) or 0))
    basic_marketing_volume = int(float(inputs.get('basic_marketing_volume', 0) or 0))
    basic_utility_volume = int(float(inputs.get('basic_utility_volume', 0) or 0))
    suggested_ai = get_suggested_price(country, 'ai', ai_volume)
    suggested_advanced = get_suggested_price(country, 'advanced', advanced_volume)
    suggested_marketing = get_suggested_price(country, 'basic_marketing', basic_marketing_volume)
    suggested_utility = get_suggested_price(country, 'basic_utility', basic_utility_volume)
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
    if ai_price is not None and (suggested_ai or 0) and ai_price < 0.3 * (suggested_ai or 0):
        discount_errors.append("AI Message price is less than 30% of the rate card.")
    if advanced_price is not None and (suggested_advanced or 0) and advanced_price < 0.3 * (suggested_advanced or 0):
        discount_errors.append("Advanced Message price is less than 30% of the rate card.")
    if basic_marketing_price is not None and (suggested_marketing or 0) and basic_marketing_price < 0.1 * (suggested_marketing or 0):
        discount_errors.append("Basic Marketing Message price is less than 10% of the rate card.")
    if basic_utility_price is not None and (suggested_utility or 0) and basic_utility_price < 0.3 * (suggested_utility or 0):
        discount_errors.append("Basic Utility/Authentication Message price is less than 30% of the rate card.")
    if platform_fee < 0.3 * rate_card_platform_fee:
        discount_errors.append("Platform Fee is less than 30% of the rate card platform fee.")
    if discount_errors:
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
        return render_template('index.html', step='prices', suggested=suggested_prices, inputs=inputs, currency_symbol=currency_symbol, platform_fee=platform_fee, calculation_id=session.get('calculation_id'))
    platform_fee, fee_currency = calculate_platform_fee(
        country,
        inputs.get('bfsi_tier', 'NA'),
        inputs.get('personalize_load', 'NA'),
        inputs.get('human_agents', 'NA'),
        inputs.get('ai_module', 'NA'),
        inputs.get('smart_cpaas', 'No'),
        inputs.get('increased_tps', 'NA')
    )
    session['pricing_inputs'] = {
        'ai_price': ai_price,
        'advanced_price': advanced_price,
        'basic_marketing_price': basic_marketing_price,
        'basic_utility_price': basic_utility_price,
        'platform_fee': platform_fee
    }
    return None  # Continue to results step

@app.route('/', methods=['GET', 'POST'])
def index():
    print("DEBUG: session at start of request:", dict(session))
    print("\n--- DEBUG ---")
    print("Form data:", dict(request.form))
    print("Session data:", dict(session))
    step = request.form.get('step', 'volumes')
    print("Current step:", step)
    calculation_id = session.get('calculation_id')
    print(f"Calculation ID: {calculation_id}")
    print("--- END DEBUG ---\n")
    suggested_prices = {}
    if step == 'volumes' and request.method == 'POST':
        return handle_volumes_step(request, session)
    elif step == 'prices' and request.method == 'POST':
        result = handle_prices_step(request, session)
        if result is not None:
            return result
        # Continue to results step
    elif step == 'bundle' and request.method == 'POST':
        # Get committed amount from form
        committed_amount = float(request.form.get('committed_amount', 0))
        inputs = session.get('inputs', {})
        inputs['committed_amount'] = committed_amount
        session['inputs'] = inputs

        from calculator import calculate_pricing, calculate_total_mandays, calculate_total_mandays_breakdown, get_committed_amount_rates, calculate_total_manday_cost
        country = inputs.get('country', 'India')
        platform_fee = float(inputs.get('platform_fee', 0))
        currency_symbol = COUNTRY_CURRENCY.get(country, '$')
        calculation_id = session.get('calculation_id')
        manday_breakdown = calculate_total_mandays_breakdown(inputs)
        total_mandays = calculate_total_mandays(inputs)
        manday_rates = session.get('manday_rates', {})

        # Get bundle rates for committed amount
        bundle_rates = get_committed_amount_rates(country, committed_amount)
        results = calculate_pricing(
            country=country,
            ai_volume=0,
            advanced_volume=0,
            basic_marketing_volume=0,
            basic_utility_volume=0,
            platform_fee=platform_fee,
            ai_price=bundle_rates['ai'],
            advanced_price=bundle_rates['advanced'],
            basic_marketing_price=bundle_rates['marketing'],
            basic_utility_price=bundle_rates['utility']
        )

        # Calculate dev cost breakdown
        total_dev_cost, dev_cost_currency, dev_cost_breakdown = calculate_total_manday_cost(inputs, manday_rates)

        return render_template(
            'index.html',
            step='results',
            results=results,
            inputs=inputs,
            currency_symbol=currency_symbol,
            platform_fee=platform_fee,
            calculation_id=calculation_id,
            committed_amount_route=True,
            expected_invoice_amount=platform_fee + committed_amount,
            manday_breakdown=manday_breakdown,
            total_mandays=total_mandays,
            manday_rates=manday_rates,
            dev_cost_currency=dev_cost_currency,
            dev_cost_breakdown=dev_cost_breakdown,
            final_inclusions=[],  # Add your inclusions logic if needed
            margin_table=[],      # Add your margin table logic if needed
            total_dev_cost=total_dev_cost
        )
    elif step == 'bundle':
        # Always set suggested_prices for bundle step
        inputs = session.get('inputs', {})
        country = inputs.get('country', 'India')
        ai_volume = int(float(inputs.get('ai_volume', 0) or 0))
        advanced_volume = int(float(inputs.get('advanced_volume', 0) or 0))
        basic_marketing_volume = int(float(inputs.get('basic_marketing_volume', 0) or 0))
        basic_utility_volume = int(float(inputs.get('basic_utility_volume', 0) or 0))
        suggested_prices = {
            'ai_price': get_suggested_price(country, 'ai', ai_volume) if ai_volume != 0 else get_lowest_tier_price(country, 'ai'),
            'advanced_price': get_suggested_price(country, 'advanced', advanced_volume) if advanced_volume != 0 else get_lowest_tier_price(country, 'advanced'),
            'basic_marketing_price': get_suggested_price(country, 'basic_marketing', basic_marketing_volume) if basic_marketing_volume != 0 else get_lowest_tier_price(country, 'basic_marketing'),
            'basic_utility_price': get_suggested_price(country, 'basic_utility', basic_utility_volume) if basic_utility_volume != 0 else get_lowest_tier_price(country, 'basic_utility'),
        }
    # Safe default: always return the initial form if no other return is hit
    return render_template('index.html', step='volumes', inputs={}, suggested={}, currency_symbol='$', platform_fee=None, calculation_id=None)

@app.route('/analytics', methods=['GET', 'POST'])
def analytics():
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
            countries = set(country_list)
            for country in countries:
                country_analytics = Analytics.query.filter_by(country=country).all()
                country_fees = [a.platform_fee for a in country_analytics if a.platform_fee is not None]
                country_ai = [a.ai_price for a in country_analytics if a.ai_price is not None]
                country_adv = [a.advanced_price for a in country_analytics if a.advanced_price is not None]
                country_mark = [a.basic_marketing_price for a in country_analytics if a.basic_marketing_price is not None]
                country_util = [a.basic_utility_price for a in country_analytics if a.basic_utility_price is not None]
                # --- One Time Dev Cost Aggregation ---
                dev_costs = []
                bot_ui_rates = [a.bot_ui_manday_rate for a in country_analytics if a.bot_ui_manday_rate not in (None, 0, '0', '', 'None')]
                custom_ai_rates = [a.custom_ai_manday_rate for a in country_analytics if a.custom_ai_manday_rate not in (None, 0, '0', '', 'None')]
                bot_ui_mandays = [getattr(a, 'bot_ui_mandays', None) for a in country_analytics]
                custom_ai_mandays = [getattr(a, 'custom_ai_mandays', None) for a in country_analytics]
                # Calculate one time dev cost for each record
                for a in country_analytics:
                    bot_ui_rate = a.bot_ui_manday_rate if a.bot_ui_manday_rate is not None else 0
                    custom_ai_rate = a.custom_ai_manday_rate if a.custom_ai_manday_rate is not None else 0
                    bot_days = getattr(a, 'bot_ui_mandays', 0) or 0
                    ai_days = getattr(a, 'custom_ai_mandays', 0) or 0
                    dev_cost = (bot_ui_rate * bot_days) + (custom_ai_rate * ai_days)
                    dev_costs.append(dev_cost)
                def stat_dict(vals):
                    # Exclude None, 0, '0', '', 'None' (as string)
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
                stats[country] = {
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
                    'one_time_dev_cost': stat_dict(dev_costs),
                    'bot_ui_manday_cost': stat_dict(bot_ui_rates),
                    'custom_ai_manday_cost': stat_dict(custom_ai_rates)
                }
                # Defensive: always include manday cost stats, even if empty
                stats[country]['bot_ui_manday_cost'] = stat_dict(bot_ui_rates) if 'bot_ui_manday_cost' not in stats[country] else stats[country]['bot_ui_manday_cost']
                stats[country]['custom_ai_manday_cost'] = stat_dict(custom_ai_rates) if 'custom_ai_manday_cost' not in stats[country] else stats[country]['custom_ai_manday_cost']
            # --- Add average discount per country for all message types and manday rates ---
            def avg_discount(chosen_list, rate_card_list):
                pairs = [(c, r) for c, r in zip(chosen_list, rate_card_list) if r and r != 0]
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
                bot_ui_rate = [COUNTRY_MANDAY_RATES.get(country, COUNTRY_MANDAY_RATES['India'])['bot_ui'] for _ in bot_ui_chosen]
                custom_ai_chosen = [a.custom_ai_manday_rate for a in country_analytics if a.custom_ai_manday_rate not in (None, 0, '0', '', 'None')]
                custom_ai_rate = [COUNTRY_MANDAY_RATES.get(country, COUNTRY_MANDAY_RATES['India'])['custom_ai'] for _ in custom_ai_chosen]
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
            print('DEBUG: analytics["stats"] structure:')
            for country, stat in stats.items():
                print(f'Country: {country}')
                print(f'  Keys: {list(stat.keys())}')
                print(f'  bot_ui_manday_cost: {stat.get("bot_ui_manday_cost")}, custom_ai_manday_cost: {stat.get("custom_ai_manday_cost")}')
            print('--- END DEBUG ---')
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
                rates = COUNTRY_MANDAY_RATES.get(country, COUNTRY_MANDAY_RATES['India'])
                if country == 'LATAM':
                    bot_ui_rate = rates['bot_ui'].get(country, rates['bot_ui']['India'])
                    custom_ai_rate = rates['custom_ai'].get(country, rates['custom_ai']['India'])
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
            analytics = {
                'calculations': total_calculations,
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
                'all_analytics': all_analytics
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
                    idx = min(int(d // 10), 9)
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
            return render_template('analytics.html', authorized=True, analytics=analytics)
        else:
            flash('Incorrect keyword.', 'error')
            return render_template('analytics.html', authorized=False, analytics={})
    # GET request or any other case
    return render_template('analytics.html', authorized=False, analytics={})

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
    rates = COUNTRY_MANDAY_RATES.get(country, COUNTRY_MANDAY_RATES['India'])
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

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 8081))
    app.run(host="0.0.0.0", port=port)