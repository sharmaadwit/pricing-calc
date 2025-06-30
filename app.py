# --- Flask Pricing Calculator Application ---
# This app provides a pricing calculator for messaging services with dynamic inclusions, platform fees, and analytics.
# Key features: dynamic inclusions, robust error handling, session management, and professional UI.

from flask import Flask, render_template, request, session, redirect, url_for, flash
from calculator import calculate_pricing, get_suggested_price, price_tiers, meta_costs_table
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
    # Defensive: always use .get() for form/session data
    step = request.form.get('step', 'volumes')
    results = None
    currency_symbol = None

    # Defensive: ensure session data exists for edit actions
    if step == 'volumes' and request.method == 'POST':
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
        platform_fee, fee_currency = calculate_platform_fee(country, bfsi_tier, personalize_load, human_agents, ai_module, smart_cpaas, increased_tps)
        currency_symbol = COUNTRY_CURRENCY.get(country, '$')
        # Store in session for next step
        session['inputs'] = {
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
            'increased_tps': increased_tps
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
        inputs = session.get('inputs', {})
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
        all_volumes_zero = (ai_volume == 0 and advanced_volume == 0 and basic_marketing_volume == 0 and basic_utility_volume == 0)

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
        if all_volumes_zero:
            return render_template('index.html', step='bundle', inputs=inputs, currency_symbol=currency_symbol)
        else:
            # Directly call the bundle logic for nonzero volumes (simulate POST to bundle step)
            # Copy the relevant code from the bundle POST handler for nonzero volumes
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
        results = calculate_pricing(
            inputs['country'],
            inputs['ai_volume'],
            inputs['advanced_volume'],
            inputs['basic_marketing_volume'],
            inputs['basic_utility_volume'],
            float(platform_fee),
            ai_price=ai_price,
            advanced_price=advanced_price,
            basic_marketing_price=basic_marketing_price,
            basic_utility_price=basic_utility_price
        )
        # Remove duplicate Committed Amount if present
        seen = set()
        unique_line_items = []
        for item in results['line_items']:
            key = (item.get('line_item'), item.get('chosen_price'), item.get('suggested_price'))
            if key not in seen:
                unique_line_items.append(item)
                seen.add(key)
        results['line_items'] = unique_line_items
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
                margin_change = ''
                if chosen_price and suggested_price and suggested_price > 0:
                    try:
                        margin_change = f"{((float(chosen_price) - float(suggested_price)) / float(suggested_price) * 100):.2f}%"
                    except Exception:
                        margin_change = '0.00%'
                else:
                    margin_change = '0.00%'
                margin_line_items.append({
                    'line_item': item.get('line_item') or item.get('label', ''),
                    'chosen_price': chosen_price,
                    'rate_card_price': suggested_price,
                    'margin_change': margin_change
                })
        
        # Add platform fee to margin table
        margin_line_items.append({
            'line_item': 'Platform Fee',
            'chosen_price': f"₹{int(platform_fee):,}",
            'rate_card_price': f"₹{int(rate_card_platform_fee):,}",
            'margin_change': '0.00%'
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
            contradiction_warning=contradiction_warning
        )

    elif step == 'bundle' and request.method == 'POST':
        # Step 3: User submitted committed amount (for zero volumes path)
        inputs = session.get('inputs', {})
        pricing_inputs = session.get('pricing_inputs', {})
        
        if not inputs or not pricing_inputs:
            flash('Session expired or missing. Please start again.', 'error')
            currency_symbol = COUNTRY_CURRENCY.get(inputs.get('country', 'India'), '₹')
            return render_template('index.html', step='bundle', inputs=inputs, currency_symbol=currency_symbol)
        
        # Parse committed amount
        committed_amount = float(request.form.get('committed_amount', '0').replace(',', ''))
        if committed_amount <= 0:
            flash('Committed amount must be greater than 0.', 'error')
            currency_symbol = COUNTRY_CURRENCY.get(inputs.get('country', 'India'), '₹')
            return render_template('index.html', step='bundle', inputs=inputs, currency_symbol=currency_symbol)
        
        # Get pricing inputs
        ai_price = pricing_inputs.get('ai_price', 0)
        advanced_price = pricing_inputs.get('advanced_price', 0)
        basic_marketing_price = pricing_inputs.get('basic_marketing_price', 0)
        basic_utility_price = pricing_inputs.get('basic_utility_price', 0)
        platform_fee = pricing_inputs.get('platform_fee', 0)
        country = inputs.get('country', 'India')
        
        # Get rate card prices for margin table
        def get_rate_card(msg_type):
            # Use the lowest tier price if volume is zero
            return get_lowest_tier_price(country, msg_type)
        
        # Build line items for all message types (even if volume is zero)
        message_types = [
            ('AI Message', 'ai', ai_price, get_rate_card('ai')),
            ('Advanced Message', 'advanced', advanced_price, get_rate_card('advanced')),
            ('Basic Marketing Message', 'basic_marketing', basic_marketing_price, get_rate_card('basic_marketing')),
            ('Basic Utility/Authentication Message', 'basic_utility', basic_utility_price, get_rate_card('basic_utility')),
        ]
        pricing_line_items = []
        margin_line_items = []
        for label, key, chosen, rate_card in message_types:
            overage = float(chosen) * 1.2 if chosen else ''
            pricing_line_items.append({
                'line_item': label,
                'volume': 0,
                'chosen_price': chosen,
                'overage_price': overage,
                'revenue': '',
            })
            # Margin calculation (N/A for committed, but show prices)
            margin_change = ''
            if chosen and rate_card:
                try:
                    margin_change = f"{((float(chosen) - float(rate_card)) / float(rate_card) * 100):.2f}%"
                except Exception:
                    margin_change = ''
            margin_line_items.append({
                'line_item': label,
                'chosen_price': chosen,
                'rate_card_price': rate_card,
                'margin_change': margin_change or '0.00%'
            })
        # Add committed amount and platform fee as line items
        pricing_line_items.append({
            'line_item': 'Committed Amount',
            'volume': '',
            'chosen_price': '',
            'overage_price': '',
            'revenue': committed_amount
        })
        pricing_line_items.append({
            'line_item': 'Platform Fee (Chosen)',
            'volume': '',
            'chosen_price': '',
            'overage_price': '',
            'revenue': float(platform_fee)
        })
        margin_line_items.append({
            'line_item': 'Committed Amount',
            'chosen_price': '₹',
            'rate_card_price': '₹',
            'margin_change': 'N/A'
        })
        margin_line_items.append({
            'line_item': 'Platform Fee',
            'chosen_price': f"₹{int(platform_fee):,}",
            'rate_card_price': f"₹{int(platform_fee):,}",
            'margin_change': '0.00%'
        })
        # Calculate results for committed amount path
        results = {
            'line_items': pricing_line_items,
            'revenue': committed_amount + float(platform_fee),
            'margin': 'N/A',
            'margin_table': margin_line_items,
            'platform_fee': float(platform_fee),
            'total_costs': 0.0,
            'channel_cost': 0.0,
            'ai_costs': 0.0,
            'suggested_revenue': float(platform_fee),
            'suggested_margin': '100.00%'
        }
        # Calculate expected invoice amount
        expected_invoice_amount = committed_amount + float(platform_fee)
        # Get rate card platform fee for margin calculation
        rate_card_platform_fee, _ = calculate_platform_fee(
            inputs['country'],
            inputs.get('bfsi_tier', 'NA'),
            inputs.get('personalize_load', 'NA'),
            inputs.get('human_agents', 'NA'),
            inputs.get('ai_module', 'NA'),
            inputs.get('smart_cpaas', 'No'),
            inputs.get('increased_tps', 'NA')
        )
        # Build user selections
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
        # Build inclusions
        inclusions = initialize_inclusions()
        personalize_load = inputs.get('personalize_load', 'NA')
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
        session['chosen_platform_fee'] = float(platform_fee)
        session['rate_card_platform_fee'] = rate_card_platform_fee
        session['user_selections'] = user_selections
        session['inclusions'] = inclusions
        session['committed_amount'] = committed_amount
        currency_symbol = COUNTRY_CURRENCY.get(inputs.get('country', 'India'), '₹')
        # Create bundle details for committed amount
        bundle_details = {
            'lines': [],
            'bundle_cost': committed_amount,
            'total_bundle_price': committed_amount + float(platform_fee),
            'inclusion_text': f'Committed amount of {COUNTRY_CURRENCY.get(country, "₹")}{committed_amount:,.0f} for messaging services.'
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
            chosen_platform_fee=float(platform_fee),
            rate_card_platform_fee=rate_card_platform_fee,
            platform_fee=float(platform_fee),
            platform_fee_rate_card=rate_card_platform_fee,
            pricing_table=pricing_line_items,
            margin_table=margin_line_items,
            user_selections=user_selections,
            inputs=inputs,
            contradiction_warning=contradiction_warning
        )

    # Defensive: handle GET or POST for edit actions
    elif step == 'volumes':
        inputs = session.get('inputs', {})
        if not inputs:
            if request.method == 'POST':
                flash('Session expired or missing. Please start again.', 'error')
            currency_symbol = COUNTRY_CURRENCY.get('India', '₹')
            return render_template('index.html', step='volumes', currency_symbol=currency_symbol, inputs={})
        currency_symbol = COUNTRY_CURRENCY.get(inputs.get('country', 'India'), '₹')
        return render_template('index.html', step='volumes', currency_symbol=currency_symbol, inputs=inputs)
    elif step == 'prices':
        inputs = session.get('inputs', {})
        pricing_inputs = session.get('pricing_inputs', {})
        if not inputs or not pricing_inputs:
            if request.method == 'POST':
                flash('Session expired or missing. Please start again.', 'error')
            currency_symbol = COUNTRY_CURRENCY.get('India', '₹')
            return render_template('index.html', step='volumes', currency_symbol=currency_symbol, inputs={})
        suggested_prices = {
            'ai_price': pricing_inputs.get('ai_price', ''),
            'advanced_price': pricing_inputs.get('advanced_price', ''),
            'basic_marketing_price': pricing_inputs.get('basic_marketing_price', ''),
            'basic_utility_price': pricing_inputs.get('basic_utility_price', ''),
        }
        platform_fee = pricing_inputs.get('platform_fee', inputs.get('platform_fee', ''))
        currency_symbol = COUNTRY_CURRENCY.get(inputs.get('country', 'India'), '₹')
        return render_template('index.html', step='prices', suggested=suggested_prices, inputs=inputs, currency_symbol=currency_symbol, platform_fee=platform_fee)
    elif step == 'bundle':
        inputs = session.get('inputs', {})
        pricing_inputs = session.get('pricing_inputs', {})
        if not inputs or not pricing_inputs:
            if request.method == 'POST':
                flash('Session expired or missing. Please start again.', 'error')
            currency_symbol = COUNTRY_CURRENCY.get('India', '₹')
            return render_template('index.html', step='volumes', currency_symbol=currency_symbol, inputs={})
        currency_symbol = COUNTRY_CURRENCY.get(inputs.get('country', 'India'), '₹')
        return render_template('index.html', step='bundle', inputs=inputs, currency_symbol=currency_symbol)
    else:
        # Default: show volume input form
        country = session.get('inputs', {}).get('country', 'India')
        currency_symbol = COUNTRY_CURRENCY.get(country, '₹')
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
            country_counter = dict(db.session.query(Analytics.country, func.count()).group_by(Analytics.country).all())
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
            platform_fee_options = Counter(platform_fees)
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
                'utility_stats': utility_stats
            }
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