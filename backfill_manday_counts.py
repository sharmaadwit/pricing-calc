from app import db, Analytics, app
from calculator import calculate_total_mandays_breakdown, COUNTRY_MANDAY_RATES
import sys

# Helper to get default rates for a country
def get_default_rates(country, dev_location='India'):
    country = country.strip()
    rates = COUNTRY_MANDAY_RATES.get(country, COUNTRY_MANDAY_RATES['Rest of the World'])
    if country == 'India':
        dev_location = dev_location.strip() if 'dev_location' in locals() else 'India'
        bot_ui_rate = rates['bot_ui'][dev_location] if isinstance(rates['bot_ui'], dict) else rates['bot_ui']
        custom_ai_rate = rates['custom_ai'][dev_location] if isinstance(rates['custom_ai'], dict) else rates['custom_ai']
        currency = rates['currency']
    else:
        bot_ui_rate = rates['bot_ui']
        custom_ai_rate = rates['custom_ai']
        currency = rates['currency']
    print(f"DEBUG: [backfill_manday_counts.py] dev_cost_currency = {currency}, country = '{country}'", file=sys.stderr, flush=True)
    return bot_ui_rate, custom_ai_rate

with app.app_context():
    updated = 0
    for a in Analytics.query.all():
        # Reconstruct the inputs dict as best as possible from the record
        inputs = {
            'num_journeys_price': getattr(a, 'num_journeys_price', 0),
            'num_apis_price': getattr(a, 'num_apis_price', 0),
            'num_ai_workspace_commerce_price': getattr(a, 'num_ai_workspace_commerce_price', 0),
            'num_ai_workspace_faq_price': getattr(a, 'num_ai_workspace_faq_price', 0),
            'aa_setup_price': getattr(a, 'aa_setup_price', 'No'),
            'onboarding_price': getattr(a, 'onboarding_price', 'No'),
            'testing_qa_price': getattr(a, 'testing_qa_price', 'No'),
            'ux_price': getattr(a, 'ux_price', 'No'),
        }
        breakdown = calculate_total_mandays_breakdown(inputs)
        a.bot_ui_mandays = breakdown['bot_ui']
        a.custom_ai_mandays = breakdown['custom_ai']
        # Set rates to default if missing
        if not a.bot_ui_manday_rate:
            bot_ui_rate, _ = get_default_rates(a.country or 'India')
            a.bot_ui_manday_rate = bot_ui_rate
        if not a.custom_ai_manday_rate:
            _, custom_ai_rate = get_default_rates(a.country or 'India')
            a.custom_ai_manday_rate = custom_ai_rate
        updated += 1

    db.session.commit()
    print(f"Backfill complete. Updated {updated} records.") 