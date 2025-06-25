from flask import Flask, render_template, request, session, redirect, url_for, flash
from calculator import calculate_pricing, get_suggested_price
import os
# from google_auth_oauthlib.flow import Flow
# from googleapiclient.discovery import build
# from google.oauth2.credentials import Credentials
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session

# os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # For local testing only

# Country to currency symbol mapping
COUNTRY_CURRENCY = {
    'India': '₹',
    'MENA': 'د.إ',  # AED
    'LATAM': '$',   # USD (or local, but $ is common)
    'Africa': '$',  # USD (or local)
    'Europe': '€',
    'Rest of the World': '$',
}

def calculate_platform_fee(country, bfsi_tier, personalize_load, human_agents, ai_module, smart_cpaas):
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
    return fee, currency

@app.route('/', methods=['GET', 'POST'])
def index():
    step = request.form.get('step', 'volumes')
    results = None
    currency_symbol = None

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
        platform_fee, fee_currency = calculate_platform_fee(country, bfsi_tier, personalize_load, human_agents, ai_module, smart_cpaas)
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
            'smart_cpaas': smart_cpaas
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
        # Call calculation logic with user-chosen prices
        results = calculate_pricing(
            inputs['country'],
            inputs['ai_volume'],
            inputs['advanced_volume'],
            inputs['basic_marketing_volume'],
            inputs['basic_utility_volume'],
            platform_fee,
            ai_price=ai_price,
            advanced_price=advanced_price,
            basic_marketing_price=basic_marketing_price,
            basic_utility_price=basic_utility_price
        )
        currency_symbol = COUNTRY_CURRENCY.get(inputs['country'], '$')
        # Pass both chosen and rate card platform fee to results page
        chosen_platform_fee = platform_fee
        rate_card_platform_fee, _ = calculate_platform_fee(
            inputs['country'],
            inputs.get('bfsi_tier', 'NA'),
            inputs.get('personalize_load', 'NA'),
            inputs.get('human_agents', 'NA'),
            inputs.get('ai_module', 'NA'),
            inputs.get('smart_cpaas', 'No')
        )
        platform_fee_used = 'chosen'  # always use the chosen (editable) platform fee for margin calculation

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

        # Inclusions mapping
        inclusions = {
            'Platform Fee Used for Margin Calculation': [
                '80 TPS',
                'Journey Builder Lite',
                'Campaign Manager',
                'CTWA - (Meta/Tiktok/Google)',
                'Agent Assist < 20 Agents',
                'Personalize upto 1 Million profiles',
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
                'Personalize upto 5 million profiles',
            ],
            'Personalize Load Advanced': [
                'Personalize upto 10 million profiles',
            ],
            'AI Module Yes': [
                'UI based retarining and configuration features',
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
                'Channel failover support for',
                'First channel : WhatsApp or RCS',
                'Second channel: WhatsApp, SMS or RCS',
            ],
        }

        session['results'] = results
        session['chosen_platform_fee'] = chosen_platform_fee
        session['rate_card_platform_fee'] = rate_card_platform_fee
        session['user_selections'] = user_selections
        session['inclusions'] = inclusions

        # Format all numbers with commas for display
        def fmt(val):
            try:
                # Handle string values that might already be formatted
                if isinstance(val, str):
                    # Remove any existing commas and try to convert
                    val = val.replace(',', '')
                # Convert to float first to handle decimals properly
                float_val = float(val)
                if float_val == int(float_val):
                    return '{:,}'.format(int(float_val))
                else:
                    return '{:,.2f}'.format(float_val)
            except (ValueError, TypeError):
                return str(val)
        
        # Format the main results
        results['revenue'] = fmt(results['revenue'])
        results['suggested_revenue'] = fmt(results['suggested_revenue'])
        results['channel_cost'] = fmt(results['channel_cost'])
        results['ai_costs'] = fmt(results['ai_costs'])
        results['total_costs'] = fmt(results['total_costs'])
        
        # Format line item numbers
        for item in results['line_items']:
            item['volume'] = fmt(item['volume'])
            item['chosen_price'] = fmt(item['chosen_price'])
            item['suggested_price'] = fmt(item['suggested_price'])
            item['overage_price'] = fmt(item['overage_price'])
            item['revenue'] = fmt(item['revenue'])
            item['suggested_revenue'] = fmt(item['suggested_revenue'])
        
        chosen_platform_fee = fmt(chosen_platform_fee)
        rate_card_platform_fee = fmt(rate_card_platform_fee)

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
            inclusions=inclusions
        )

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

if __name__ == '__main__':
    app.run(debug=True)