from flask import Flask, render_template, request, session
from calculator import calculate_pricing, get_suggested_price

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session

# Country to currency symbol mapping
COUNTRY_CURRENCY = {
    'India': '₹',
    'MENA': 'د.إ',  # AED
    'LATAM': '$',   # USD (or local, but $ is common)
    'Africa': '$',  # USD (or local)
    'Europe': '€',
    'Rest of the World': '$',
}

def calculate_platform_fee(country, bfsi_tier, personalize_load, human_agents, ai_module):
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
        platform_fee, fee_currency = calculate_platform_fee(country, bfsi_tier, personalize_load, human_agents, ai_module)
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
            'ai_module': ai_module
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
            inputs.get('ai_module', 'NA')
        )
        platform_fee_used = 'chosen'  # always use the chosen (editable) platform fee for margin calculation
        return render_template(
            'index.html',
            step='results',
            results=results,
            inputs=inputs,
            currency_symbol=currency_symbol,
            chosen_platform_fee=chosen_platform_fee,
            rate_card_platform_fee=rate_card_platform_fee,
            platform_fee_used=platform_fee_used
        )

    # Default: show volume input form
    country = session.get('inputs', {}).get('country', 'India')
    currency_symbol = COUNTRY_CURRENCY.get(country, '₹')
    return render_template('index.html', step='volumes', currency_symbol=currency_symbol)

if __name__ == '__main__':
    app.run(debug=True)