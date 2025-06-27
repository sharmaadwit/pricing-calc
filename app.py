from flask import Flask, render_template, request, session, redirect, url_for, flash
from calculator import calculate_pricing, get_suggested_price
import os
# from google_auth_oauthlib.flow import Flow
# from googleapiclient.discovery import build
# from google.oauth2.credentials import Credentials
import re
import datetime
from collections import Counter, defaultdict
import statistics

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session

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

# Module-level global for analytics
analytics_data = {
    'calculations': 0,
    'calculations_by_day': defaultdict(int),
    'calculations_by_week': defaultdict(int),
    'country_counter': Counter(),
    'platform_fee_options': Counter(),
    'platform_fee_entries': [],
    'message_volumes': {'ai': [], 'advanced': [], 'basic_marketing': [], 'basic_utility': []},
    'discount_warnings': Counter(),
    'platform_fee_discount_triggered': 0,
    'margin_chosen': [],
    'margin_rate_card': [],
}

def calculate_platform_fee(country, bfsi_tier, personalize_load, human_agents, ai_module, smart_cpaas, increased_tps='NA'):
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
    # Defensive: always use .get() for form/session data
    step = request.form.get('step', 'volumes')
    results = None
    currency_symbol = None

    # Defensive: ensure session data exists for edit actions
    if step == 'volumes' and request.method == 'POST':
        # Step 1: User submitted volumes and platform fee options
        country = request.form['country']
        ai_volume = float(request.form['ai_volume'])
        advanced_volume = float(request.form['advanced_volume'])
        basic_marketing_volume = float(request.form['basic_marketing_volume'])
        basic_utility_volume = float(request.form['basic_utility_volume'])
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
        suggested_prices = {
            'ai_price': get_suggested_price(country, 'ai', ai_volume),
            'advanced_price': get_suggested_price(country, 'advanced', advanced_volume),
            'basic_marketing_price': get_suggested_price(country, 'basic_marketing', basic_marketing_volume),
            'basic_utility_price': get_suggested_price(country, 'basic_utility', basic_utility_volume),
        }
        return render_template('index.html', step='prices', suggested=suggested_prices, inputs=session['inputs'], currency_symbol=currency_symbol, platform_fee=platform_fee)

    elif step == 'prices' and request.method == 'POST':
        # Step 2: User submitted prices
        inputs = session.get('inputs', {})
        ai_price = float(request.form['ai_price'])
        advanced_price = float(request.form['advanced_price'])
        basic_marketing_price = float(request.form['basic_marketing_price'])
        basic_utility_price = float(request.form['basic_utility_price'])
        platform_fee = float(request.form['platform_fee'])

        # Get suggested prices for validation
        country = inputs.get('country', 'India')
        ai_volume = float(inputs.get('ai_volume', 0))
        advanced_volume = float(inputs.get('advanced_volume', 0))
        basic_marketing_volume = float(inputs.get('basic_marketing_volume', 0))
        basic_utility_volume = float(inputs.get('basic_utility_volume', 0))
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
        if ai_price < 0.5 * suggested_ai:
            discount_errors.append("AI Message price is less than 50% of the rate card.")
        if advanced_price < 0.5 * suggested_advanced:
            discount_errors.append("Advanced Message price is less than 50% of the rate card.")
        if basic_marketing_price < 0.5 * suggested_marketing:
            discount_errors.append("Basic Marketing Message price is less than 50% of the rate card.")
        if basic_utility_price < 0.5 * suggested_utility:
            discount_errors.append("Basic Utility/Authentication Message price is less than 50% of the rate card.")
        # Platform fee discount check
        if platform_fee < 0.5 * rate_card_platform_fee:
            discount_errors.append("Platform Fee is less than 50% of the rate card platform fee.")
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
        return render_template('index.html', step='bundle', inputs=inputs, currency_symbol=currency_symbol)

    elif step == 'bundle' and request.method == 'POST':
        bundle_choice = request.form.get('bundle_choice', 'No')
        session['bundle_choice'] = bundle_choice
        # Retrieve previous inputs
        inputs = session.get('inputs', {})
        pricing_inputs = session.get('pricing_inputs', {})
        ai_price = pricing_inputs.get('ai_price', 0)
        advanced_price = pricing_inputs.get('advanced_price', 0)
        basic_marketing_price = pricing_inputs.get('basic_marketing_price', 0)
        basic_utility_price = pricing_inputs.get('basic_utility_price', 0)
        platform_fee = pricing_inputs.get('platform_fee', 0)
        bundle_details = None
        bundle_cost = 0
        if bundle_choice == 'Yes':
            # Show each type of message, volume, and overage price
            bundle_lines = []
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
            # Fix: total_bundle_price is platform_fee + bundle_cost (do not add bundle_cost to platform_fee)
            total_bundle_price = float(pricing_inputs.get('platform_fee', 0)) + bundle_cost
            bundle_details = {
                'lines': bundle_lines,
                'bundle_cost': bundle_cost,
                'total_bundle_price': total_bundle_price,
                'inclusion_text': 'See table below for included volumes and overage prices.'
            }
        # Call calculation logic with updated platform fee (do not add bundle_cost to platform_fee)
        results = calculate_pricing(
            inputs['country'],
            inputs['ai_volume'],
            inputs['advanced_volume'],
            inputs['basic_marketing_volume'],
            inputs['basic_utility_volume'],
            float(pricing_inputs.get('platform_fee', 0)),
            ai_price=ai_price,
            advanced_price=advanced_price,
            basic_marketing_price=basic_marketing_price,
            basic_utility_price=basic_utility_price
        )
        currency_symbol = COUNTRY_CURRENCY.get(inputs['country'], '$')
        # Pass both chosen and rate card platform fee to results page
        chosen_platform_fee = float(pricing_inputs.get('platform_fee', 0))
        rate_card_platform_fee, _ = calculate_platform_fee(
            inputs['country'],
            inputs.get('bfsi_tier', 'NA'),
            inputs.get('personalize_load', 'NA'),
            inputs.get('human_agents', 'NA'),
            inputs.get('ai_module', 'NA'),
            inputs.get('smart_cpaas', 'No'),
            inputs.get('increased_tps', 'NA')
        )
        platform_fee_used = 'chosen'  # always use the chosen (editable) platform fee for margin calculation

        # Add platform fee line items to results['line_items']
        if 'line_items' in results:
            results['line_items'].append({
                'label': 'Platform Fee (Chosen)',
                'volume': '',
                'chosen_price': '',
                'suggested_price': '',
                'overage_price': '',
                'meta_cost': '',
                'final_price': '',
                'revenue': chosen_platform_fee,
                'suggested_revenue': ''
            })
            results['line_items'].append({
                'label': 'Platform Fee (Rate Card)',
                'volume': '',
                'chosen_price': '',
                'suggested_price': '',
                'overage_price': '',
                'meta_cost': '',
                'final_price': '',
                'revenue': '',
                'suggested_revenue': rate_card_platform_fee
            })

        # Pass expected_invoice_amount to template
        expected_invoice_amount = results.get('revenue', 0)

        # Gather non-NA/No selections for display
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

        # Inclusions mapping
        inclusions = {
            'Platform Fee Used for Margin Calculation': [
                '80 TPS',
                'Journey Builder Lite',
                'Campaign Manager',
                'CTWA - (Meta/Tiktok)',
                'Agent Assist < 20 Agents',
                'Personalize upto 1 Million profiles and external events not supported',
            ],
            'BFSI Tier 1': [
                'Audit trail to be stored for 60 days from JB Pro+Flows',
                'Conversational Data Encryption, Logging,Auditing, Purging (Data and Logs) from Agent Assist',
            ],
            'BFSI Tier 2': [
                'Audit trail to be stored for 60 days from JB Pro+Flows',
                'Conversational Data Encryption, Logging,Auditing, Purging (Data and Logs) from Agent Assist',
                'Conversational Data Encryption, Logging,Auditing, Purging (Data and Logs) for AI Conversations',
            ],
            'BFSI Tier 3': [
                'Audit trail to be stored for 60 days from JB Pro+Flows',
                'Conversational Data Encryption, Logging,Auditing, Purging (Data and Logs) from Agent Assist',
                'Conversational Data Encryption, Logging,Auditing, Purging (Data and Logs) for AI Conversations',
                'Data Encryption, Logging, Auditing, Purging (Logs) from Campaign Manager, Retargetting and Personalize layers',
            ],
            'Personalize Load Standard': [
                'Standard - upto 5 million records, no external events',
            ],
            'Personalize Load Advanced': [
                'Advanced - 10 million records, external events supported',
            ],
            'AI Module Yes': [
                'Access to Workspace Configuration and data retraining screens',
            ],
            'Human Agents 20+': [
                'Upto 50 agents',
            ],
            'Human Agents 50+': [
                'Upto 100 agents',
            ],
            'Human Agents 100+': [
                'More than 100 agents',
            ],
            'Smart CPaaS Yes': [
                'Auto failover between channels',
            ],
            'Increased TPS 250': [
                'Upto 250 Messages per Second',
            ],
            'Increased TPS 1000': [
                'Upto 1000 Messages per Second',
            ],
        }

        # Build dynamic inclusions list (no duplicate/contradictory inclusions)
        final_inclusions = inclusions['Platform Fee Used for Margin Calculation'][:]
        selected_components = []
        # BFSI Tier (show only the selected tier's inclusions, not lower tiers)
        bfsi_tier = inputs.get('bfsi_tier', 'NA')
        if bfsi_tier in ['Tier 1', 'Tier 2', 'Tier 3']:
            # Remove all BFSI inclusions from final_inclusions
            final_inclusions = [inc for inc in final_inclusions if not inc.startswith('Audit trail') and not inc.startswith('Conversational Data Encryption') and not inc.startswith('Data Encryption')]
            final_inclusions += inclusions.get(f'BFSI Tier {bfsi_tier.split(" ")[-1]}', [])
            selected_components.append(f"BFSI Tier: {bfsi_tier}")
        # Personalize Load (show only the selected tier's inclusion, not base)
        personalize_load = inputs.get('personalize_load', 'NA')
        if personalize_load in ['Standard', 'Advanced']:
            final_inclusions = [inc for inc in final_inclusions if not inc.startswith('Personalize') and not inc.startswith('Standard') and not inc.startswith('Advanced')]
            final_inclusions += inclusions.get(f'Personalize Load {personalize_load}', [])
            selected_components.append(f"Personalize Load: {personalize_load}")
        # Human Agents (show only the selected tier's inclusion, not base)
        human_agents = inputs.get('human_agents', 'NA')
        if human_agents in ['20+', '50+', '100+']:
            final_inclusions = [inc for inc in final_inclusions if not inc.startswith('Agent Assist') and not inc.startswith('Upto') and not inc.startswith('More than')]
            final_inclusions += inclusions.get(f'Human Agents {human_agents}', [])
            selected_components.append(f"Human Agents: {human_agents}")
        # AI Module
        ai_module = inputs.get('ai_module', 'NA')
        if ai_module == 'Yes':
            final_inclusions += inclusions.get('AI Module Yes', [])
            selected_components.append("AI Module: Yes")
        # Smart CPaaS
        smart_cpaas = inputs.get('smart_cpaas', 'No')
        if smart_cpaas == 'Yes':
            final_inclusions += inclusions.get('Smart CPaaS Yes', [])
            selected_components.append("Smart CPaaS: Yes")
        # Increased TPS
        increased_tps = inputs.get('increased_tps', 'NA')
        if increased_tps in ['250', '1000']:
            final_inclusions += inclusions.get(f'Increased TPS {increased_tps}', [])
            selected_components.append(f"Increased TPS: {increased_tps}")
        # Remove duplicates from inclusions
        final_inclusions = list(dict.fromkeys(final_inclusions))
        session['selected_components'] = selected_components

        session['results'] = results
        session['chosen_platform_fee'] = chosen_platform_fee
        session['rate_card_platform_fee'] = rate_card_platform_fee
        session['user_selections'] = user_selections
        session['inclusions'] = inclusions

        # Format all numbers with commas for display
        def fmt(val):
            try:
                # Handle None values
                if val is None:
                    return '0'
                # Handle string values that might already be formatted
                if isinstance(val, str):
                    # Remove any existing commas and try to convert
                    val = val.replace(',', '')
                    if not val.strip():  # Handle empty strings
                        return '0'
                    # Check if it's already a formatted number (e.g., "123.45")
                    if val.replace('.', '').replace('-', '').isdigit():
                        float_val = float(val)
                        if float_val == int(float_val):
                            return '{:,}'.format(int(float_val))
                        else:
                            return '{:,.2f}'.format(float_val)
                    else:
                        return val  # Return as-is if not a number
                # Convert to float first to handle decimals properly
                float_val = float(val)
                if float_val == int(float_val):
                    return '{:,}'.format(int(float_val))
                else:
                    return '{:,.2f}'.format(float_val)
            except (ValueError, TypeError):
                return str(val) if val is not None else '0'
        
        # Format the main results
        # Don't format revenue as string - let template handle formatting
        # results['revenue'] = fmt(results.get('revenue', 0))
        # results['suggested_revenue'] = fmt(results.get('suggested_revenue', 0))
        results['channel_cost'] = fmt(results.get('channel_cost', 0))
        results['ai_costs'] = fmt(results.get('ai_costs', 0))
        results['total_costs'] = fmt(results.get('total_costs', 0))
        
        # Format line item numbers
        for item in results.get('line_items', []):
            item['volume'] = fmt(item.get('volume', 0))
            item['chosen_price'] = fmt(item.get('chosen_price', 0))
            item['suggested_price'] = fmt(item.get('suggested_price', 0))
            item['overage_price'] = fmt(item.get('overage_price', 0))
            item['revenue'] = fmt(item.get('revenue', 0))
            item['suggested_revenue'] = fmt(item.get('suggested_revenue', 0))
        
        # Ensure all numeric values are floats for template formatting
        try:
            chosen_platform_fee = float(chosen_platform_fee)
        except Exception:
            chosen_platform_fee = 0.0
        try:
            rate_card_platform_fee = float(rate_card_platform_fee)
        except Exception:
            rate_card_platform_fee = 0.0
        if bundle_details:
            try:
                bundle_details['bundle_cost'] = float(bundle_details.get('bundle_cost', 0))
            except Exception:
                bundle_details['bundle_cost'] = 0.0
            try:
                bundle_details['total_bundle_price'] = float(bundle_details.get('total_bundle_price', 0))
            except Exception:
                bundle_details['total_bundle_price'] = 0.0
            for line in bundle_details.get('lines', []):
                try:
                    line['volume'] = float(line.get('volume', 0))
                except Exception:
                    line['volume'] = 0.0
                try:
                    line['price'] = float(line.get('price', 0))
                except Exception:
                    line['price'] = 0.0
                try:
                    line['overage_price'] = float(line.get('overage_price', 0))
                except Exception:
                    line['overage_price'] = 0.0
        # Before analytics tracking, ensure discount_errors is always defined
        if 'discount_errors' not in locals():
            discount_errors = []
        # In-memory analytics (resets on restart)
        now = datetime.datetime.now()
        day_str = now.strftime('%Y-%m-%d')
        week_str = now.strftime('%Y-W%U')
        analytics_data['calculations'] += 1
        analytics_data['calculations_by_day'][day_str] += 1
        analytics_data['calculations_by_week'][week_str] += 1
        analytics_data['country_counter'][inputs.get('country', 'Unknown')] += 1
        analytics_data['platform_fee_options'][inputs.get('platform_fee', 'Unknown')] += 1
        analytics_data['platform_fee_entries'].append(float(pricing_inputs.get('platform_fee', 0)))
        analytics_data['message_volumes']['ai'].append(float(inputs.get('ai_volume', 0)))
        analytics_data['message_volumes']['advanced'].append(float(inputs.get('advanced_volume', 0)))
        analytics_data['message_volumes']['basic_marketing'].append(float(inputs.get('basic_marketing_volume', 0)))
        analytics_data['message_volumes']['basic_utility'].append(float(inputs.get('basic_utility_volume', 0)))
        if discount_errors:
            for msg in discount_errors:
                analytics_data['discount_warnings'][msg] += 1
                if 'platform fee' in msg.lower():
                    analytics_data['platform_fee_discount_triggered'] += 1
        # Track margin
        try:
            margin_chosen = float(results.get('margin', '0').replace('%',''))
            margin_rate_card = float(results.get('suggested_margin', '0').replace('%',''))
            analytics_data['margin_chosen'].append(margin_chosen)
            analytics_data['margin_rate_card'].append(margin_rate_card)
        except Exception:
            pass

        return render_template(
            'index.html',
            step='results',
            results=results,
            inputs=inputs,
            currency_symbol=currency_symbol,
            chosen_platform_fee=chosen_platform_fee,
            rate_card_platform_fee=rate_card_platform_fee,
            platform_fee_used=platform_fee_used,
            user_selections=user_selections,
            inclusions=inclusions,
            bundle_details=bundle_details,
            final_inclusions=final_inclusions,
            expected_invoice_amount=expected_invoice_amount
        )

    # Defensive: handle GET or POST for edit actions
    elif step == 'volumes':
        inputs = session.get('inputs', {})
        if not inputs:
            flash('Session expired or missing. Please start again.', 'error')
            return redirect(url_for('index'))
        currency_symbol = COUNTRY_CURRENCY.get(inputs.get('country', 'India'), '₹')
        return render_template('index.html', step='volumes', currency_symbol=currency_symbol, inputs=inputs)
    elif step == 'prices':
        inputs = session.get('inputs', {})
        pricing_inputs = session.get('pricing_inputs', {})
        if not inputs or not pricing_inputs:
            flash('Session expired or missing. Please start again.', 'error')
            return redirect(url_for('index'))
        suggested_prices = {
            'ai_price': pricing_inputs.get('ai_price', ''),
            'advanced_price': pricing_inputs.get('advanced_price', ''),
            'basic_marketing_price': pricing_inputs.get('basic_marketing_price', ''),
            'basic_utility_price': pricing_inputs.get('basic_utility_price', ''),
        }
        platform_fee = pricing_inputs.get('platform_fee', inputs.get('platform_fee', ''))
        currency_symbol = COUNTRY_CURRENCY.get(inputs.get('country', 'India'), '₹')
        return render_template('index.html', step='prices', suggested=suggested_prices, inputs=inputs, currency_symbol=currency_symbol, platform_fee=platform_fee)
    else:
        # Default: show volume input form
        country = session.get('inputs', {}).get('country', 'India')
        currency_symbol = COUNTRY_CURRENCY.get(country, '₹')
        return render_template('index.html', step='volumes', currency_symbol=currency_symbol)

@app.route('/authorize')
def authorize():
    # flow = Flow.from_client_secrets_file(
    #     'credentials.json',
    #     scopes=['https://www.googleapis.com/auth/documents'],
    #     redirect_uri=url_for('oauth2callback', _external=True)
    # )
    # authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    # session['state'] = state
    return redirect(url_for('index', step='results'))

@app.route('/oauth2callback')
def oauth2callback():
    # flow = Flow.from_client_secrets_file(
    #     'credentials.json',
    #     scopes=['https://www.googleapis.com/auth/documents'],
    #     state=session['state'],
    #     redirect_uri=url_for('oauth2callback', _external=True)
    # )
    # flow.fetch_token(authorization_response=request.url)
    # credentials = flow.credentials
    # session['credentials'] = credentials_to_dict(credentials)
    flash('Google authentication successful. You can now export to Google Docs.')
    return redirect(url_for('index', step='results'))

# def credentials_to_dict(credentials):
#     return {
#         'token': credentials.token,
#         'refresh_token': credentials.refresh_token,
#         'token_uri': credentials.token_uri,
#         'client_id': credentials.client_id,
#         'client_secret': credentials.client_secret,
#         'scopes': credentials.scopes
#     }

# def extract_doc_id(doc_link):
#     match = re.search(r'/d/([a-zA-Z0-9-_]+)', doc_link)
#     return match.group(1) if match else None

# def find_heading_index(service, doc_id, heading_text):
#     doc = service.documents().get(documentId=doc_id).execute()
#     content = doc.get('body', {}).get('content', [])
#     for element in content:
#         if 'paragraph' in element:
#             elements = element['paragraph'].get('elements', [])
#             text = ''.join([e.get('textRun', {}).get('content', '') for e in elements])
#             if heading_text in text:
#                 return element['endIndex']
#     return None

# def build_results_table_data(results, chosen_platform_fee, rate_card_platform_fee, user_selections, inclusions):
#     table = [
#         ['Platform Fee Section', 'Value', 'Inclusions'],
#         ['Platform Fee Used for Margin Calculation', str(chosen_platform_fee), ', '.join(inclusions['Platform Fee Used for Margin Calculation'])],
#         ['Rate Card Platform Fee', str(rate_card_platform_fee), ''],
#     ]
#     for label, value in user_selections:
#         if label == 'BFSI Tier' and value in ['Tier 1', 'Tier 2', 'Tier 3']:
#             key = f'BFSI Tier {value.split(" ")[-1]}'
#             table.append([f'BFSI {value}', 'Included', ', '.join(inclusions.get(key, ['No inclusions defined yet.']))])
#         if label == 'Personalize Load' and value in ['Standard', 'Advanced']:
#             key = f'Personalize Load {value}'
#             table.append([f'Personalize Load {value}', 'Included', ', '.join(inclusions.get(key, ['No inclusions defined yet.']))])
#         if label == 'AI Module' and value == 'Yes':
#             key = 'AI Module Yes'
#             table.append(['AI Module', 'Included', ', '.join(inclusions.get(key, ['No inclusions defined yet.']))])
#         if label == 'Human Agents' and value in ['20+', '50+', '100+']:
#             key = f'Human Agents {value}'
#             table.append([f'Human Agents {value}', 'Included', ', '.join(inclusions.get(key, ['No inclusions defined yet.']))])
#     return table

# def insert_and_fill_table(service, doc_id, table_data, insert_index):
#     # 1. Insert the table
#     requests = [
#         {
#             'insertTable': {
#                 'rows': len(table_data),
#                 'columns': len(table_data[0]),
#                 'location': {'index': insert_index}
#             }
#         }
#     ]
#     response = service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()
#     # 2. Insert text into each cell
#     # After insertion, the table starts at insert_index
#     # Each cell is filled left-to-right, top-to-bottom
#     # We need to keep track of the current index as we insert text
#     # We'll fetch the document again to get the table's start index
#     doc = service.documents().get(documentId=doc_id).execute()
#     content = doc.get('body', {}).get('content', [])
#     table_start = None
#     for element in content:
#         if 'table' in element and element['startIndex'] >= insert_index:
#             table_start = element['startIndex']
#             break
#     if table_start is None:
#         raise Exception('Could not find inserted table in document.')

#     # Now, fill each cell
#     requests = []
#     cell_index = table_start + 4  # Table start + 4 (table element overhead)
#     for row in table_data:
#         for cell in row:
#             requests.append({
#                 'insertText': {
#                     'location': {'index': cell_index},
#                     'text': str(cell)
#                 }
#             })
#             cell_index += len(str(cell)) + 1  # +1 for the end-of-cell marker

#     if requests:
#         service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()

# @app.route('/export_to_gdoc', methods=['POST'])
# def export_to_gdoc():
#     doc_link = request.form.get('gdoc_link')
#     doc_id = extract_doc_id(doc_link)
#     if not doc_id:
#         flash('Invalid Google Doc link.')
#         return redirect(url_for('index', step='results'))

#     if 'credentials' not in session:
#         return redirect(url_for('authorize'))

#     creds = Credentials(**session['credentials'])

@app.route('/analytics', methods=['GET', 'POST'])
def analytics():
    if request.method == 'POST':
        keyword = request.form.get('keyword', '')
        if keyword == SECRET_ANALYTICS_KEYWORD:
            return render_template('analytics.html', authorized=True, analytics=analytics_data)
        else:
            flash('Incorrect keyword.', 'error')
            return render_template('analytics.html', authorized=False)
    return render_template('analytics.html', authorized=False)

if __name__ == '__main__':
    app.run(debug=True, port=5001)