# --- Flask Pricing Calculator Application ---
# This app provides a pricing calculator for messaging services with dynamic inclusions, platform fees, and analytics.
# Key features: dynamic inclusions, robust error handling, session management, and professional UI.

from flask import Flask, render_template, request, session, redirect, url_for, flash
from calculator import calculate_pricing, get_suggested_price, price_tiers, meta_costs_table, calculate_total_mandays, calculate_total_manday_cost, COUNTRY_MANDAY_RATES
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
    # Add more fields as needed

# os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # For local testing only

# Country to currency symbol mapping
COUNTRY_CURRENCY = {
    'India': '₹',
    'MENA': '$',  # USD for MENA
    'LATAM': '$',
    'Africa': '$',
    'Europe': '€',
    'Rest of the World': '$',
}

SECRET_ANALYTICS_KEYWORD = "letmein123"

def initialize_inclusions():
    """
    Returns a dictionary of all possible inclusions for each feature/tier.
    Only the inclusions for the highest/most specific tier in each category should be shown.
    """
    inclusions = {
        'Platform Fee Used for Margin Calculation': [
            'Journey Builder Lite,',
            'Campaign Manager,',
            'CTWA - (Meta, Tiktok)'
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
    # 1. Minimum platform fee
    if country == 'India':
        min_fee = 100000
        currency = 'INR'
    elif country in ['Africa', 'Rest of the World']:
        min_fee = 500
        currency = 'USD'
    else:
        min_fee = 1000
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

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Main route for the pricing calculator. Handles all user steps (volumes, prices, bundle, results).
    Manages session data, input validation, pricing logic, and inclusions logic.
    """
    # Debug: Log form data, session data, and current step
    print("\n--- DEBUG ---")
    print("Form data:", dict(request.form))
    print("Session data:", dict(session))
    step = request.form.get('step', 'volumes')
    print("Current step:", step)
    print("--- END DEBUG ---\n")
    results = None
    currency_symbol = None

    # Defensive: ensure session data exists for edit actions
    if step == 'volumes' and request.method == 'POST':
        user_name = request.form.get('user_name', '')
        # Step 1: User submitted volumes and platform fee options
        country = request.form['country']
        def parse_volume(val):
            try:
                return float(val.replace(',', '')) if val and str(val).strip() else 0.0
            except Exception:
                return 0.0
        ai_volume = parse_volume(request.form.get('ai_volume', ''))
        advanced_volume = parse_volume(request.form.get('advanced_volume', ''))
        basic_marketing_volume = parse_volume(request.form.get('basic_marketing_volume', ''))
        basic_utility_volume = parse_volume(request.form.get('basic_utility_volume', ''))
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
        # Store in session for next step
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
        return render_template('index.html', step='prices', suggested=suggested_prices, inputs=session['inputs'], currency_symbol=currency_symbol, platform_fee=platform_fee)

    elif step == 'prices' and request.method == 'POST':
        # Step 2: User submitted prices
        inputs = session.get('inputs', {}) or {}
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
            return render_template('index.html', step='prices', suggested=suggested_prices, inputs=inputs, currency_symbol=currency_symbol, platform_fee=platform_fee)

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
            overage_price = float(price) * 1.2
            bundle_lines.append({
                'label': label,
                'volume': volume,
                'price': float(price),
                'overage_price': overage_price
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
        rates = COUNTRY_MANDAY_RATES.get(country, COUNTRY_MANDAY_RATES['India'])
        if country == 'LATAM':
            default_bot_ui = rates['bot_ui'][dev_location]
            default_custom_ai = rates['custom_ai'][dev_location]
        else:
            default_bot_ui = rates['bot_ui']
            default_custom_ai = rates['custom_ai']
        manday_rates = session.get('manday_rates', {}) or {}
        # Fill missing keys with defaults
        manday_rates['bot_ui'] = float(manday_rates.get('bot_ui', default_bot_ui))
        manday_rates['custom_ai'] = float(manday_rates.get('custom_ai', default_custom_ai))
        manday_rates['default_bot_ui'] = float(default_bot_ui)
        manday_rates['default_custom_ai'] = float(default_custom_ai)
        # Calculate discount percentages
        manday_rates['bot_ui_discount'] = round(100 * (default_bot_ui - manday_rates['bot_ui']) / default_bot_ui, 2) if default_bot_ui else 0
        manday_rates['custom_ai_discount'] = round(100 * (default_custom_ai - manday_rates['custom_ai']) / default_custom_ai, 2) if default_custom_ai else 0
        total_mandays = calculate_total_mandays(patched_form)
        total_dev_cost, dev_cost_currency, manday_breakdown = calculate_total_manday_cost(patched_form, manday_rates)
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
        else:
            flash('Pricing calculation failed. Please check your inputs and try again.', 'error')
            suggested_prices = {
                'ai_price': suggested_ai,
                'advanced_price': suggested_advanced,
                'basic_marketing_price': suggested_marketing,
                'basic_utility_price': suggested_utility,
            }
            currency_symbol = COUNTRY_CURRENCY.get(country, '$')
            return render_template('index.html', step='prices', suggested=suggested_prices, inputs=inputs, currency_symbol=currency_symbol, platform_fee=platform_fee)
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
        contradiction_warning = None
        # Platform base features (always included)
        final_inclusions += inclusions['Platform Fee Used for Margin Calculation']
        # Personalize Load (highest only)
        personalize_load = inputs.get('personalize_load', 'NA')
        if personalize_load == 'Advanced':
            final_inclusions += inclusions['Personalize Load Advanced']
        elif personalize_load == 'Standard':
            final_inclusions += inclusions['Personalize Load Standard']
        elif personalize_load == 'Lite' or personalize_load in ['NA', 'No', None]:
            final_inclusions += inclusions['Personalize Load Lite']
        # BFSI Tier (highest only)
        bfsi_tier = inputs.get('bfsi_tier', 'NA')
        if bfsi_tier == 'Tier 3':
            final_inclusions += inclusions['BFSI Tier 3']
        elif bfsi_tier == 'Tier 2':
            final_inclusions += inclusions['BFSI Tier 2']
        elif bfsi_tier == 'Tier 1':
            final_inclusions += inclusions['BFSI Tier 1']
        # Human Agents (highest only)
        human_agents = inputs.get('human_agents', 'NA')
        if human_agents == '100+':
            final_inclusions += inclusions['Human Agents 100+']
        elif human_agents == '50+':
            final_inclusions += inclusions['Human Agents 50+']
        elif human_agents == '20+':
            final_inclusions += inclusions['Human Agents 20+']
        elif human_agents == '<20' or human_agents in ['NA', 'No', None]:
            final_inclusions += inclusions['Human Agents <20']
        # Increased TPS (highest only)
        increased_tps = inputs.get('increased_tps', 'NA')
        if increased_tps == '1000':
            final_inclusions += inclusions['Increased TPS 1000']
        elif increased_tps == '250':
            final_inclusions += inclusions['Increased TPS 250']
        # AI Module
        if inputs.get('ai_module', 'No') == 'Yes':
            final_inclusions += inclusions['AI Module Yes']
        # Smart CPaaS
        if inputs.get('smart_cpaas', 'No') == 'Yes':
            final_inclusions += inclusions['Smart CPaaS Yes']
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
        for item in results['line_items']:
            if item.get('line_item') != 'Platform Fee (Chosen)':
                chosen_price = item.get('chosen_price', 0)
                suggested_price = item.get('suggested_price', 0)
                discount_percent = ''
                if chosen_price and suggested_price and suggested_price > 0:
                    try:
                        discount_percent = f"{((float(suggested_price) - float(chosen_price)) / float(suggested_price) * 100):.2f}%"
                    except Exception:
                        discount_percent = '0.00%'
                else:
                    discount_percent = '0.00%'
                margin_line_items.append({
                    'line_item': item.get('line_item') or item.get('label', ''),
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
            # Format numbers: no decimals if .00, else show up to 2 decimals
            try:
                if isinstance(val, str) and val.replace('.', '', 1).isdigit():
                    val = float(val)
                if isinstance(val, (int, float)):
                    s = f"{val:.2f}"
                    return s.rstrip('0').rstrip('.') if '.' in s else s
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
            custom_ai_manday_rate=manday_rates.get('custom_ai')
        )
        new_analytics = Analytics(**analytics_kwargs)
        db.session.add(new_analytics)
        db.session.commit()
        # Top 5 users by number of calculations
        user_names = [row[0] for row in db.session.query(Analytics.user_name).all() if row[0]]
        top_users = Counter(user_names).most_common(5)
        # When setting results['suggested_revenue'], use rate_card_platform_fee instead of platform_fee
        results['suggested_revenue'] = (results.get('suggested_revenue', 0) - platform_fee) + rate_card_platform_fee
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
            manday_rates=manday_rates
        )
    # Defensive: handle GET or POST for edit actions
    elif step == 'volumes':
        inputs = session.get('inputs', {}) or {}
        if not inputs:
            if request.method == 'POST':
                flash('Session expired or missing. Please start again.', 'error')
            currency_symbol = COUNTRY_CURRENCY.get('India', '₹')
            return render_template('index.html', step='volumes', currency_symbol=currency_symbol, inputs={})
        currency_symbol = COUNTRY_CURRENCY.get(inputs.get('country', 'India'), '$')
        return render_template('index.html', step='volumes', currency_symbol=currency_symbol, inputs=inputs)
    elif step == 'prices':
        inputs = session.get('inputs', {}) or {}
        pricing_inputs = session.get('pricing_inputs', {}) or {}
        country = inputs.get('country', 'India')
        dev_location = inputs.get('dev_location', 'India')
        # Get default rates
        rates = COUNTRY_MANDAY_RATES.get(country, COUNTRY_MANDAY_RATES['India'])
        if country == 'LATAM':
            default_bot_ui = rates['bot_ui'][dev_location]
            default_custom_ai = rates['custom_ai'][dev_location]
        else:
            default_bot_ui = rates['bot_ui']
            default_custom_ai = rates['custom_ai']
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
                }, inputs=inputs, currency_symbol=COUNTRY_CURRENCY.get(country, '$'), platform_fee=pricing_inputs.get('platform_fee', inputs.get('platform_fee', '')))
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
            }, inputs=inputs, currency_symbol=COUNTRY_CURRENCY.get(country, '$'), platform_fee=pricing_inputs.get('platform_fee', inputs.get('platform_fee', '')))
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
        # Go to prices page
        pricing_inputs = session.get('pricing_inputs', {}) or {}
        country = inputs.get('country', 'India')
        dev_location = inputs.get('dev_location', 'India')
        rates = COUNTRY_MANDAY_RATES.get(country, COUNTRY_MANDAY_RATES['India'])
        if country == 'LATAM':
            default_bot_ui = rates['bot_ui'][dev_location]
            default_custom_ai = rates['custom_ai'][dev_location]
        else:
            default_bot_ui = rates['bot_ui']
            default_custom_ai = rates['custom_ai']
        return render_template('index.html', step='prices', suggested={
            'ai_price': pricing_inputs.get('ai_price', ''),
            'advanced_price': pricing_inputs.get('advanced_price', ''),
            'basic_marketing_price': pricing_inputs.get('basic_marketing_price', ''),
            'basic_utility_price': pricing_inputs.get('basic_utility_price', ''),
            'bot_ui_manday_rate': default_bot_ui,
            'custom_ai_manday_rate': default_custom_ai,
        }, inputs=inputs, currency_symbol=COUNTRY_CURRENCY.get(country, '$'), platform_fee=pricing_inputs.get('platform_fee', inputs.get('platform_fee', '')))
    # Default: show volume input form
    country = session.get('inputs', {}).get('country', 'India')
    currency_symbol = COUNTRY_CURRENCY.get(country, '$')
    return render_template('index.html', step='volumes', currency_symbol=currency_symbol)

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
            from calculator import calculate_total_mandays, calculate_total_manday_cost, COUNTRY_MANDAY_RATES
            for country in countries:
                country_analytics = Analytics.query.filter_by(country=country).all()
                country_fees = [a.platform_fee for a in country_analytics if a.platform_fee is not None]
                country_ai = [a.ai_price for a in country_analytics if a.ai_price is not None]
                country_adv = [a.advanced_price for a in country_analytics if a.advanced_price is not None]
                country_mark = [a.basic_marketing_price for a in country_analytics if a.basic_marketing_price is not None]
                country_util = [a.basic_utility_price for a in country_analytics if a.basic_utility_price is not None]
                # --- One Time Dev Cost and Per Manday Cost Aggregation ---
                dev_costs = []
                per_manday_costs = []
                bot_ui_rates = []
                custom_ai_rates = []
                for a in country_analytics:
                    dev_location = 'India'
                    if hasattr(a, 'dev_location') and a.dev_location:
                        dev_location = a.dev_location
                    rates = COUNTRY_MANDAY_RATES.get(country, COUNTRY_MANDAY_RATES['India'])
                    if country == 'LATAM':
                        bot_ui_rate = rates['bot_ui'][dev_location]
                        custom_ai_rate = rates['custom_ai'][dev_location]
                    else:
                        bot_ui_rate = rates['bot_ui']
                        custom_ai_rate = rates['custom_ai']
                    bot_ui_rates.append(bot_ui_rate)
                    custom_ai_rates.append(custom_ai_rate)
                    per_manday_cost = (bot_ui_rate + custom_ai_rate) / 2
                    per_manday_costs.append(per_manday_cost)
                    dev_cost = bot_ui_rate + custom_ai_rate
                    dev_costs.append(dev_cost)
                def stat_dict(vals):
                    if vals:
                        return {
                            'avg': sum(vals)/len(vals),
                            'min': min(vals),
                            'max': max(vals),
                            'median': sorted(vals)[len(vals)//2]
                        }
                    else:
                        return {'avg': 0, 'min': 0, 'max': 0, 'median': 0}
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
                    'per_manday_cost': stat_dict(per_manday_costs),
                    'bot_ui_manday_cost': stat_dict(bot_ui_rates),
                    'custom_ai_manday_cost': stat_dict(custom_ai_rates)
                }
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
            # Top 5 users by number of calculations
            user_names = [row[0] for row in db.session.query(Analytics.user_name).all() if row[0]]
            top_users = Counter(user_names).most_common(5)
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
            return render_template('analytics.html', authorized=False)
    return render_template('analytics.html', authorized=False)

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

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 8081))
    app.run(host="0.0.0.0", port=port)