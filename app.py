from flask import Flask, render_template, request, session
from calculator import calculate_pricing, get_suggested_price

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        # Always show the first step on GET (reset)
        return render_template('index.html', step='volumes')
    step = request.form.get('step', 'volumes')
    results = None

    if step == 'volumes' and request.method == 'POST':
        # Step 1: User submitted volumes
        country = request.form['country']
        ai_volume = float(request.form['ai_volume'])
        advanced_volume = float(request.form['advanced_volume'])
        basic_marketing_volume = float(request.form['basic_marketing_volume'])
        basic_utility_volume = float(request.form['basic_utility_volume'])
        platform_fee = float(request.form['platform_fee'])

        # Store in session for next step
        session['inputs'] = {
            'country': country,
            'ai_volume': ai_volume,
            'advanced_volume': advanced_volume,
            'basic_marketing_volume': basic_marketing_volume,
            'basic_utility_volume': basic_utility_volume,
            'platform_fee': platform_fee
        }

        # Suggest prices
        suggested_prices = {
            'ai_price': get_suggested_price(country, 'ai', ai_volume),
            'advanced_price': get_suggested_price(country, 'advanced', advanced_volume),
            'basic_marketing_price': get_suggested_price(country, 'basic_marketing', basic_marketing_volume),
            'basic_utility_price': get_suggested_price(country, 'basic_utility', basic_utility_volume),
        }
        return render_template('index.html', step='prices', suggested=suggested_prices, inputs=session['inputs'])

    elif step == 'prices' and request.method == 'POST':
        # Step 2: User submitted prices
        inputs = session.get('inputs', {})
        ai_price = float(request.form['ai_price'])
        advanced_price = float(request.form['advanced_price'])
        basic_marketing_price = float(request.form['basic_marketing_price'])
        basic_utility_price = float(request.form['basic_utility_price'])

        # Call calculation logic with user-chosen prices
        results = calculate_pricing(
            inputs['country'],
            inputs['ai_volume'],
            inputs['advanced_volume'],
            inputs['basic_marketing_volume'],
            inputs['basic_utility_volume'],
            inputs['platform_fee'],
            ai_price=ai_price,
            advanced_price=advanced_price,
            basic_marketing_price=basic_marketing_price,
            basic_utility_price=basic_utility_price
        )
        return render_template('index.html', step='results', results=results, inputs=inputs)

    # Default: show volume input form
    return render_template('index.html', step='volumes')

if __name__ == '__main__':
    app.run(debug=True)