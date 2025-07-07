# calculator.py

# --- Pricing and Cost Calculation Module ---
# This module provides pricing tiers, cost tables, and functions for calculating suggested prices, overage prices, and total pricing for the messaging calculator app.

# --- Price Tiers by Country and Message Type ---
# Each country has a set of volume-based price tiers for each message type.
price_tiers = {
    'India': {
        'ai': [
            (0, 10000, 1.00),
            (10000, 100000, 0.90),
            (100000, 500000, 0.80),
            (500000, 1000000, 0.70),
            (1000000, float('inf'), 0.60),
        ],
        'advanced': [
            (0, 50000, 0.50),
            (50000, 150000, 0.45),
            (150000, 500000, 0.40),
            (500000, float('inf'), 0.35),
        ],
        'basic_marketing': [
            (0, float('inf'), 0.05),
        ],
        'basic_utility': [
            (0, float('inf'), 0.03),
        ],
    },
    'MENA': {
        'ai': [
            (0, 10000, 0.084),
            (10000, 100000, 0.076),
            (100000, 500000, 0.067),
            (500000, 1000000, 0.059),
            (1000000, float('inf'), 0.050),
        ],
        'advanced': [
            (0, 50000, 0.042),
            (50000, 150000, 0.038),
            (150000, 500000, 0.034),
            (500000, float('inf'), 0.029),
        ],
        'basic_marketing': [
            (0, float('inf'), 0.0042),
        ],
        'basic_utility': [
            (0, float('inf'), 0.003),
        ],
    },
    'LATAM': {
        'ai': [
            (0, 10000, 0.120),
            (10000, 100000, 0.108),
            (100000, 500000, 0.096),
            (500000, 1000000, 0.084),
            (1000000, float('inf'), 0.072),
        ],
        'advanced': [
            (0, 50000, 0.060),
            (50000, 150000, 0.054),
            (150000, 500000, 0.048),
            (500000, float('inf'), 0.042),
        ],
        'basic_marketing': [
            (0, float('inf'), 0.006),
        ],
        'basic_utility': [
            (0, float('inf'), 0.004),
        ],
    },
    'Africa': {
        'ai': [
            (0, 10000, 0.048),
            (10000, 100000, 0.043),
            (100000, 500000, 0.038),
            (500000, 1000000, 0.034),
            (1000000, float('inf'), 0.029),
        ],
        'advanced': [
            (0, 50000, 0.024),
            (50000, 150000, 0.022),
            (150000, 500000, 0.019),
            (500000, float('inf'), 0.017),
        ],
        'basic_marketing': [
            (0, float('inf'), 0.002),
        ],
        'basic_utility': [
            (0, float('inf'), 0.001),
        ],
    },
    'Europe': {
        'ai': [
            (0, 10000, 0.240),
            (10000, 100000, 0.216),
            (100000, 500000, 0.192),
            (500000, 1000000, 0.168),
            (1000000, float('inf'), 0.144),
        ],
        'advanced': [
            (0, 50000, 0.120),
            (50000, 150000, 0.108),
            (150000, 500000, 0.096),
            (500000, float('inf'), 0.084),
        ],
        'basic_marketing': [
            (0, float('inf'), 0.012),
        ],
        'basic_utility': [
            (0, float('inf'), 0.007),
        ],
    },
    'Rest of the World': {
        'ai': [
            (0, 10000, 0.120),
            (10000, 100000, 0.108),
            (100000, 500000, 0.096),
            (500000, 1000000, 0.084),
            (1000000, float('inf'), 0.072),
        ],
        'advanced': [
            (0, 50000, 0.060),
            (50000, 150000, 0.054),
            (150000, 500000, 0.048),
            (500000, float('inf'), 0.042),
        ],
        'basic_marketing': [
            (0, float('inf'), 0.006),
        ],
        'basic_utility': [
            (0, float('inf'), 0.007),
        ],
    },
}

# --- Cost Table by Country ---
# Meta costs for each country and message type.
meta_costs_table = {
    'India': {'marketing': 0.78, 'utility': 0.12, 'ai': 0.30},
    'MENA': {'marketing': 0.0455 * 3.67, 'utility': 0.0115 * 3.67, 'ai': 0.0036 * 3.67},
    'LATAM': {'marketing': 0.0625, 'utility': 0.0080, 'ai': 0.0036},
    'Africa': {'marketing': 0.0379, 'utility': 0.0076, 'ai': 0.0036},
    'Europe': {'marketing': 0.0529, 'utility': 0.0220, 'ai': 0.0036},
    'Rest of the World': {'marketing': 0.0604, 'utility': 0.0077, 'ai': 0.0036},
}

# --- Activity to Manday Mapping (applies to all countries) ---
ACTIVITY_MANDAYS = {
    "journey": 1,
    "api": 1,
    "ai_agents": 10,
    "4_journey_4_api": 5,
    "aa_setup": 1,
    "onboarding": 0.5,
    "testing": 1,
    "ux": 1,
}

# --- Country-specific Manday Rates (Bot/UI and Custom/AI) ---
COUNTRY_MANDAY_RATES = {
    'India': {
        'currency': 'INR',
        'bot_ui': 27500,
        'custom_ai': 44000,
    },
    'LATAM': {
        'currency': 'USD',
        'bot_ui': {
            'LATAM': 825,
            'India': 440,
        },
        'custom_ai': {
            'LATAM': 1100,
            'India': 605,
        },
    },
    'MENA': {
        'currency': 'AED',
        'bot_ui': 1650,
        'custom_ai': 2750,
    },
    'Africa': {
        'currency': 'USD',
        'bot_ui': 440,
        'custom_ai': 605,
    },
    'Rest of the World': {
        'currency': 'USD',
        'bot_ui': 440,
        'custom_ai': 605,
    },
    'Europe': {
        'currency': 'USD',  # Not in table, fallback to Rest of the World?
        'bot_ui': 440,
        'custom_ai': 605,
    },
}

def get_suggested_price(country, msg_type, volume, currency=None):
    """
    Return the suggested price for a message type, country, and volume.
    Looks up the correct tier based on volume.
    """
    tiers = price_tiers.get(country, {}).get(msg_type, [])
    for lower, upper, price in tiers:
        if lower < volume <= upper:
            return price
    return 0.0

def get_next_tier_price(country, msg_type, volume):
    """
    Return the next tier price for a message type, country, and volume (overage price).
    """
    tiers = price_tiers.get(country, {}).get(msg_type, [])
    found = False
    for i, (lower, upper, price) in enumerate(tiers):
        if lower < volume <= upper:
            found = True
            if i + 1 < len(tiers):
                return tiers[i + 1][2]
            else:
                return price  # No higher tier, return current
    if not found and tiers:
        return tiers[0][2]
    return 0.0

def calculate_pricing(
    country, ai_volume, advanced_volume, basic_marketing_volume, basic_utility_volume, platform_fee,
    ai_price=None, advanced_price=None, basic_marketing_price=None, basic_utility_price=None
):
    """
    Calculate all pricing, revenue, costs, and margin for the given inputs.
    Returns a dictionary with detailed line items and summary values.
    """
    costs = meta_costs_table.get(country, meta_costs_table['India'])

    # Get suggested and overage prices for each type
    suggested_ai_price = get_suggested_price(country, 'ai', ai_volume)
    suggested_advanced_price = get_suggested_price(country, 'advanced', advanced_volume)
    suggested_basic_marketing_price = get_suggested_price(country, 'basic_marketing', basic_marketing_volume)
    suggested_basic_utility_price = get_suggested_price(country, 'basic_utility', basic_utility_volume)

    overage_ai_price = get_next_tier_price(country, 'ai', ai_volume)
    overage_advanced_price = get_next_tier_price(country, 'advanced', advanced_volume)
    overage_basic_marketing_price = get_next_tier_price(country, 'basic_marketing', basic_marketing_volume)
    overage_basic_utility_price = get_next_tier_price(country, 'basic_utility', basic_utility_volume)

    # Use user-chosen prices if provided, otherwise use suggested
    user_ai_price = ai_price if ai_price is not None else suggested_ai_price
    user_advanced_price = advanced_price if advanced_price is not None else suggested_advanced_price
    user_basic_marketing_price = basic_marketing_price if basic_marketing_price is not None else suggested_basic_marketing_price
    user_basic_utility_price = basic_utility_price if basic_utility_price is not None else suggested_basic_utility_price

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
            'overage_price': overage_ai_price,
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
            'overage_price': overage_advanced_price,
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
            'overage_price': overage_basic_marketing_price,
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
            'overage_price': overage_basic_utility_price,
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

def calculate_total_mandays(inputs):
    """
    Calculate the total mandays based on user inputs and the activity-to-manday mapping.
    Applies the '4_journey_4_api' logic for all countries: for every set of 4 journeys and 4 apis, use 5 mandays;
    for remaining journeys and apis, use 1 manday each.
    """
    total_mandays = 0
    num_journeys = int(inputs.get('num_journeys_price', 0))
    num_apis = int(inputs.get('num_apis_price', 0))

    # Calculate sets of 4 journeys and 4 apis
    sets_of_4 = min(num_journeys // 4, num_apis // 4)
    total_mandays += sets_of_4 * ACTIVITY_MANDAYS['4_journey_4_api']

    # Subtract used journeys and apis
    remaining_journeys = num_journeys - sets_of_4 * 4
    remaining_apis = num_apis - sets_of_4 * 4

    # Add mandays for remaining journeys and apis
    total_mandays += remaining_journeys * ACTIVITY_MANDAYS['journey']
    total_mandays += remaining_apis * ACTIVITY_MANDAYS['api']

    # AI Agents (Commerce + FAQ)
    total_mandays += int(inputs.get('num_ai_workspace_commerce_price', 0)) * ACTIVITY_MANDAYS['ai_agents']
    total_mandays += int(inputs.get('num_ai_workspace_faq_price', 0)) * ACTIVITY_MANDAYS['ai_agents']
    # AA Setup
    if inputs.get('aa_setup_price', 'No') == 'Yes':
        total_mandays += ACTIVITY_MANDAYS['aa_setup']
    # Onboarding
    if inputs.get('onboarding_price', 'No') == 'Yes':
        total_mandays += ACTIVITY_MANDAYS['onboarding']
    # Testing
    if inputs.get('testing_qa_price', 'No') == 'Yes':
        total_mandays += ACTIVITY_MANDAYS['testing']
    # UX
    if inputs.get('ux_price', 'No') == 'Yes':
        total_mandays += ACTIVITY_MANDAYS['ux']
    return total_mandays

def calculate_total_mandays_breakdown(inputs):
    """
    Returns a dict with mandays for bot_ui and custom_ai activities, ignoring items with 0 value.
    """
    num_journeys = int(inputs.get('num_journeys_price', 0))
    num_apis = int(inputs.get('num_apis_price', 0))
    num_ai_commerce = int(inputs.get('num_ai_workspace_commerce_price', 0))
    num_ai_faq = int(inputs.get('num_ai_workspace_faq_price', 0))
    # 4-journey-4-api logic
    sets_of_4 = min(num_journeys // 4, num_apis // 4)
    remaining_journeys = num_journeys - sets_of_4 * 4
    remaining_apis = num_apis - sets_of_4 * 4
    bot_ui_mandays = 0
    custom_ai_mandays = 0
    # Bot/UI: journeys, apis, 4-journey-4-api, AA Setup, Onboarding, Testing, UX
    if sets_of_4 > 0:
        bot_ui_mandays += sets_of_4 * ACTIVITY_MANDAYS['4_journey_4_api']
    if remaining_journeys > 0:
        bot_ui_mandays += remaining_journeys * ACTIVITY_MANDAYS['journey']
    if remaining_apis > 0:
        bot_ui_mandays += remaining_apis * ACTIVITY_MANDAYS['api']
    if inputs.get('aa_setup_price', 'No') == 'Yes':
        bot_ui_mandays += ACTIVITY_MANDAYS['aa_setup']
    if inputs.get('onboarding_price', 'No') == 'Yes':
        bot_ui_mandays += ACTIVITY_MANDAYS['onboarding']
    if inputs.get('testing_qa_price', 'No') == 'Yes':
        bot_ui_mandays += ACTIVITY_MANDAYS['testing']
    if inputs.get('ux_price', 'No') == 'Yes':
        bot_ui_mandays += ACTIVITY_MANDAYS['ux']
    # Custom/AI: AI workspaces
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
    Ignores items with 0 value.
    If manday_rates is provided, use user-supplied rates for bot_ui and custom_ai.
    Returns (total_cost, currency, breakdown_dict)
    """
    country = inputs.get('country', 'India')
    dev_location = inputs.get('dev_location', 'India')
    rates = COUNTRY_MANDAY_RATES.get(country, COUNTRY_MANDAY_RATES['India'])
    breakdown = calculate_total_mandays_breakdown(inputs)
    # Get rates
    if manday_rates:
        bot_ui_rate = manday_rates.get('bot_ui', rates['bot_ui'][dev_location] if country == 'LATAM' else rates['bot_ui'])
        custom_ai_rate = manday_rates.get('custom_ai', rates['custom_ai'][dev_location] if country == 'LATAM' else rates['custom_ai'])
    else:
        if country == 'LATAM':
            bot_ui_rate = rates['bot_ui'][dev_location]
            custom_ai_rate = rates['custom_ai'][dev_location]
        else:
            bot_ui_rate = rates['bot_ui']
            custom_ai_rate = rates['custom_ai']
    currency = rates['currency'] if not manday_rates else rates['currency']
    total_cost = breakdown['bot_ui'] * bot_ui_rate + breakdown['custom_ai'] * custom_ai_rate
    return total_cost, currency, breakdown
