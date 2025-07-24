# calculator.py

# --- Pricing and Cost Calculation Module ---
# This module provides pricing tiers, cost tables, and functions for calculating suggested prices, overage prices, and total pricing for the messaging calculator app.

# --- Price Tiers by Country and Message Type ---
# Each country has a set of volume-based price tiers for each message type.

# --- Cost Table by Country ---
# Meta costs for each country and message type.

from pricing_config import price_tiers, meta_costs_table, COUNTRY_MANDAY_RATES, ACTIVITY_MANDAYS, committed_amount_slabs

# New function to map volume to committed amount slab rate

def get_committed_amount_rate_for_volume(country, msg_type, volume):
    slabs = committed_amount_slabs.get(country, committed_amount_slabs['Rest of the World'])
    # Try each slab: estimate the committed amount for this volume at the slab's rate
    for lower, upper, rates in slabs:
        rate = rates[msg_type]
        est_amount = volume * rate
        if lower <= est_amount < upper:
            return rate
    # Fallback to lowest slab
    return slabs[0][2][msg_type]

# Update get_suggested_price to use committed amount slab rates for volume route

def get_suggested_price(country, msg_type, volume, currency=None):
    """
    Return the suggested price for a message type, country, and volume.
    Now uses the committed amount slab rate for the estimated monthly revenue.
    """
    return get_committed_amount_rate_for_volume(country, msg_type, volume)

def get_next_tier_price(country, msg_type, volume):
    """
    Deprecated: Overage prices are no longer used or displayed.
    """
    return 0.0

def calculate_pricing(
    country, ai_volume, advanced_volume, basic_marketing_volume, basic_utility_volume, platform_fee,
    ai_price=None, advanced_price=None, basic_marketing_price=None, basic_utility_price=None
):
    """
    Calculate all pricing, revenue, costs, and margin for the given inputs.
    Returns a dictionary with detailed line items and summary values.
    """
    costs = meta_costs_table.get(country, meta_costs_table['Rest of the World'])

    # Get suggested and overage prices for each type
    suggested_ai_price = get_suggested_price(country, 'ai', ai_volume)
    suggested_advanced_price = get_suggested_price(country, 'advanced', advanced_volume)
    suggested_basic_marketing_price = get_suggested_price(country, 'basic_marketing', basic_marketing_volume)
    suggested_basic_utility_price = get_suggested_price(country, 'basic_utility', basic_utility_volume)

    # Use user-chosen prices if provided, otherwise use suggested
    user_ai_price = ai_price if ai_price is not None else suggested_ai_price
    user_advanced_price = advanced_price if advanced_price is not None else suggested_advanced_price
    user_basic_marketing_price = basic_marketing_price if basic_marketing_price is not None else suggested_basic_marketing_price
    user_basic_utility_price = basic_utility_price if basic_utility_price is not None else suggested_basic_utility_price

    # Calculate overage prices using 1.2x multiplier for consistency with bundle flow
    overage_ai_price = float(user_ai_price) * 1.2
    overage_advanced_price = float(user_advanced_price) * 1.2
    overage_basic_marketing_price = float(user_basic_marketing_price) * 1.2
    overage_basic_utility_price = float(user_basic_utility_price) * 1.2

    # Revenue (user-chosen)
    ai_revenue = (costs['ai'] + user_ai_price) * ai_volume
    advanced_revenue = (costs['ai'] + user_advanced_price) * advanced_volume
    basic_marketing_revenue = (costs['marketing'] + user_basic_marketing_price) * basic_marketing_volume
    basic_utility_revenue = (costs['utility'] + user_basic_utility_price) * basic_utility_volume
    revenue = ai_revenue + advanced_revenue + basic_marketing_revenue + basic_utility_revenue

    # Revenue (suggested)
    ai_final_price_s = costs['ai'] + suggested_ai_price
    advanced_final_price_s = costs['ai'] + suggested_advanced_price
    basic_marketing_final_price_s = costs['marketing'] + suggested_basic_marketing_price
    basic_utility_final_price_s = costs['utility'] + suggested_basic_utility_price

    ai_revenue_s = ai_final_price_s * ai_volume
    advanced_revenue_s = advanced_final_price_s * advanced_volume
    basic_marketing_revenue_s = basic_marketing_final_price_s * basic_marketing_volume
    basic_utility_revenue_s = basic_utility_final_price_s * basic_utility_volume
    suggested_revenue = ai_revenue_s + advanced_revenue_s + basic_marketing_revenue_s + basic_utility_revenue_s

    # Channel cost (as per your logic)
    adv_marketing_vol = 0.0
    adv_utility_vol = 0.0
    channel_cost = (
        (costs['marketing'] * adv_marketing_vol)
        + (costs['utility'] * adv_utility_vol)
        + (basic_marketing_volume * costs['marketing'])
        + (basic_utility_volume * costs['utility'])
    )

    # AI costs
    ai_costs = costs['ai'] * ai_volume

    # Total costs (platform infra cost is 0)
    total_costs = channel_cost + ai_costs

    # Margin (user-chosen, business formula)
    margin_denom = revenue + platform_fee
    if margin_denom > 0:
        margin = (revenue + platform_fee - total_costs) / margin_denom
        margin_percentage = margin * 100
    else:
        margin = 0
        margin_percentage = 0

    # Suggested margin (business formula)
    suggested_margin_denom = suggested_revenue + platform_fee
    if suggested_margin_denom > 0:
        suggested_margin = (suggested_revenue + platform_fee - total_costs) / suggested_margin_denom
        suggested_margin_percentage = suggested_margin * 100
    else:
        suggested_margin = 0
        suggested_margin_percentage = 0

    # Detailed breakdown for each line item
    line_items = [
        {
            'label': 'AI Message',
            'volume': ai_volume,
            'chosen_price': user_ai_price,
            'suggested_price': suggested_ai_price,
            'meta_cost': costs['ai'],
            'final_price': costs['ai'] + user_ai_price,
            'revenue': ai_revenue,
            'suggested_revenue': ai_revenue_s
        },
        {
            'label': 'Advanced Message',
            'volume': advanced_volume,
            'chosen_price': user_advanced_price,
            'suggested_price': suggested_advanced_price,
            'meta_cost': costs['ai'],
            'final_price': costs['ai'] + user_advanced_price,
            'revenue': advanced_revenue,
            'suggested_revenue': advanced_revenue_s
        },
        {
            'label': 'Basic Marketing Message',
            'volume': basic_marketing_volume,
            'chosen_price': user_basic_marketing_price,
            'suggested_price': suggested_basic_marketing_price,
            'meta_cost': costs['marketing'],
            'final_price': costs['marketing'] + user_basic_marketing_price,
            'revenue': basic_marketing_revenue,
            'suggested_revenue': basic_marketing_revenue_s
        },
        {
            'label': 'Basic Utility/Authentication Message',
            'volume': basic_utility_volume,
            'chosen_price': user_basic_utility_price,
            'suggested_price': suggested_basic_utility_price,
            'meta_cost': costs['utility'],
            'final_price': costs['utility'] + user_basic_utility_price,
            'revenue': basic_utility_revenue,
            'suggested_revenue': basic_utility_revenue_s
        },
    ]

    return {
        'line_items': line_items,
        'platform_fee': platform_fee,
        'revenue': revenue + platform_fee,
        'suggested_revenue': suggested_revenue + platform_fee if suggested_revenue is not None else None,
        'channel_cost': channel_cost,
        'ai_costs': ai_costs,
        'total_costs': total_costs,
        'margin': f"{margin_percentage:.2f}%",
        'suggested_margin': f"{suggested_margin_percentage:.2f}%"
    }

def _calculate_set_mandays(num_apis, num_journeys):
    """
    Helper for set logic: For each set where either APIs or journeys is at least 4 and the other is > 0, count 5 mandays and subtract up to 4 from each. Returns (mandays, remaining_apis, remaining_journeys).
    """
    mandays = 0
    while (num_apis >= 4 or num_journeys >= 4) and (num_apis > 0 and num_journeys > 0):
        used_apis = min(4, num_apis)
        used_journeys = min(4, num_journeys)
        num_apis -= used_apis
        num_journeys -= used_journeys
        mandays += 5
    return mandays, num_apis, num_journeys

def _calculate_extras_mandays(inputs, activity_mandays):
    """
    Helper for extras logic: onboarding, UX, testing, AA setup. Returns total extra mandays.
    """
    extras = 0
    if inputs.get('aa_setup_price', 'No') == 'Yes':
        extras += activity_mandays['aa_setup']
    if inputs.get('onboarding_price', 'No') == 'Yes':
        extras += activity_mandays['onboarding']
    if inputs.get('testing_qa_price', 'No') == 'Yes':
        extras += activity_mandays['testing']
    if inputs.get('ux_price', 'No') == 'Yes':
        extras += activity_mandays['ux']
    return extras

# --- refactored calculate_total_mandays ---
def calculate_total_mandays(inputs):
    """
    Calculate the total mandays based on user inputs and the activity-to-manday mapping.
    Uses shared helpers for set and extras logic.
    """
    total_mandays = 0
    num_journeys = int(inputs.get('num_journeys_price') or 0)
    num_apis = int(inputs.get('num_apis_price') or 0)
    set_mandays, rem_apis, rem_journeys = _calculate_set_mandays(num_apis, num_journeys)
    total_mandays += set_mandays
    total_mandays += rem_apis + rem_journeys
    # AI Agents (Commerce + FAQ)
    total_mandays += int(inputs.get('num_ai_workspace_commerce_price') or 0) * ACTIVITY_MANDAYS['ai_agents']
    total_mandays += int(inputs.get('num_ai_workspace_faq_price') or 0) * ACTIVITY_MANDAYS['ai_agents']
    # Extras
    total_mandays += _calculate_extras_mandays(inputs, ACTIVITY_MANDAYS)
    return total_mandays

# --- refactored calculate_total_mandays_breakdown ---
def calculate_total_mandays_breakdown(inputs):
    """
    Returns a dict with mandays for bot_ui and custom_ai activities, using shared helpers for set and extras logic.
    """
    num_journeys = int(inputs.get('num_journeys_price') or 0)
    num_apis = int(inputs.get('num_apis_price') or 0)
    num_ai_commerce = int(inputs.get('num_ai_workspace_commerce_price') or 0)
    num_ai_faq = int(inputs.get('num_ai_workspace_faq_price') or 0)
    bot_ui_mandays, rem_apis, rem_journeys = _calculate_set_mandays(num_apis, num_journeys)
    bot_ui_mandays += rem_apis + rem_journeys
    # Extras for bot_ui
    bot_ui_mandays += _calculate_extras_mandays(inputs, ACTIVITY_MANDAYS)
    # Custom/AI: AI workspaces
    custom_ai_mandays = 0
    if num_ai_commerce > 0:
        custom_ai_mandays += num_ai_commerce * ACTIVITY_MANDAYS['ai_agents']
    if num_ai_faq > 0:
        custom_ai_mandays += num_ai_faq * ACTIVITY_MANDAYS['ai_agents']
    return {
        'bot_ui': bot_ui_mandays,
        'custom_ai': custom_ai_mandays,
        'total': bot_ui_mandays + custom_ai_mandays
    }

def calculate_total_manday_cost(inputs, manday_rates=None):
    """
    Calculate the total cost for mandays, using the correct rate for each activity and country/dev location.
    If user enters 0 for bot_ui rate but selects any of Onboarding, UX, Testing/QA, AA Setup as Yes, use default rate for those activities.
    Returns (total_cost, currency, breakdown_dict)
    """
    country = inputs.get('country', 'India')
    dev_location = inputs.get('dev_location', 'India')
    # Use Rest of the World as fallback, not India
    rates = COUNTRY_MANDAY_RATES.get(country, COUNTRY_MANDAY_RATES['Rest of the World'])
    breakdown = calculate_total_mandays_breakdown(inputs)
    if manday_rates:
        user_bot_ui_rate = manday_rates.get('bot_ui', rates['bot_ui'][dev_location] if country == 'LATAM' else rates['bot_ui'])
        user_custom_ai_rate = manday_rates.get('custom_ai', rates['custom_ai'][dev_location] if country == 'LATAM' else rates['custom_ai'])
    else:
        if country == 'LATAM':
            user_bot_ui_rate = rates['bot_ui'][dev_location]
            user_custom_ai_rate = rates['custom_ai'][dev_location]
        else:
            user_bot_ui_rate = rates['bot_ui']
            user_custom_ai_rate = rates['custom_ai']
    default_bot_ui_rate = rates['bot_ui'][dev_location] if country == 'LATAM' else rates['bot_ui']
    default_custom_ai_rate = rates['custom_ai'][dev_location] if country == 'LATAM' else rates['custom_ai']
    currency = rates['currency']  # This will be 'USD' for Rest of the World

    activity_mandays = {
        'onboarding': ACTIVITY_MANDAYS['onboarding'],
        'ux': ACTIVITY_MANDAYS['ux'],
        'testing': ACTIVITY_MANDAYS['testing'],
        'aa_setup': ACTIVITY_MANDAYS['aa_setup'],
    }
    bot_ui_cost = 0
    activity_manday_total = 0
    if float(user_bot_ui_rate) == 0:
        for activity, field in [('onboarding', 'onboarding_price'), ('ux', 'ux_price'), ('testing', 'testing_qa_price'), ('aa_setup', 'aa_setup_price')]:
            if inputs.get(field, 'No') == 'Yes':
                bot_ui_cost += default_bot_ui_rate * activity_mandays[activity]
                activity_manday_total += activity_mandays[activity]
        other_bot_ui_mandays = breakdown['bot_ui'] - activity_manday_total
        if other_bot_ui_mandays > 0:
            bot_ui_cost += other_bot_ui_mandays * default_bot_ui_rate
    else:
        bot_ui_cost = breakdown['bot_ui'] * float(user_bot_ui_rate)

    custom_ai_rate = float(user_custom_ai_rate) if float(user_custom_ai_rate) != 0 else default_custom_ai_rate
    custom_ai_cost = breakdown['custom_ai'] * custom_ai_rate

    build_cost = bot_ui_cost + custom_ai_cost
    ba_cost = 0.15 * build_cost
    qa_cost = 0.10 * build_cost
    pm_cost = 0.05 * build_cost
    uplift_amount = ba_cost + qa_cost + pm_cost
    total_cost = build_cost + uplift_amount

    breakdown_dict = {
        'bot_ui_cost': bot_ui_cost,
        'custom_ai_cost': custom_ai_cost,
        'build_cost': build_cost,
        'ba_cost': ba_cost,
        'qa_cost': qa_cost,
        'pm_cost': pm_cost,
        'uplift_amount': uplift_amount,
        'total_cost': total_cost,
        'currency': currency,
        'mandays_breakdown': breakdown,
    }
    return total_cost, currency, breakdown_dict

def get_committed_amount_rates(country, committed_amount):
    """
    Return default per-message rates for a country based on committed amount slabs.
    country: str
    committed_amount: float (in INR or USD as per country)
    Returns: dict with keys 'marketing', 'utility', 'advanced', 'ai'
    """
    slabs = committed_amount_slabs.get(country, committed_amount_slabs['Rest of the World'])
    for lower, upper, rates in slabs:
        if lower <= committed_amount < upper:
            return rates
    return slabs[0][2]  # fallback to first slab

def get_committed_amount_rates_india(committed_amount):
    return get_committed_amount_rates('India', committed_amount)
