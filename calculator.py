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
            (0, 10000, 0.12),
            (10000, 100000, 0.11),
            (100000, 500000, 0.10),
            (500000, 1000000, 0.09),
            (1000000, float('inf'), 0.08),
        ],
        'advanced': [
            (0, 50000, 0.06),
            (50000, 150000, 0.055),
            (150000, 500000, 0.05),
            (500000, float('inf'), 0.045),
        ],
        'basic_marketing': [
            (0, float('inf'), 0.006),
        ],
        'basic_utility': [
            (0, float('inf'), 0.004),
        ],
    },
    'LATAM': {
        'ai': [
            (0, 10000, 0.12),
            (10000, 100000, 0.11),
            (100000, 500000, 0.10),
            (500000, 1000000, 0.09),
            (1000000, float('inf'), 0.08),
        ],
        'advanced': [
            (0, 50000, 0.06),
            (50000, 150000, 0.055),
            (150000, 500000, 0.05),
            (500000, float('inf'), 0.045),
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
            (0, 10000, 0.12),
            (10000, 100000, 0.11),
            (100000, 500000, 0.10),
            (500000, 1000000, 0.09),
            (1000000, float('inf'), 0.08),
        ],
        'advanced': [
            (0, 50000, 0.06),
            (50000, 150000, 0.055),
            (150000, 500000, 0.05),
            (500000, float('inf'), 0.045),
        ],
        'basic_marketing': [
            (0, float('inf'), 0.006),
        ],
        'basic_utility': [
            (0, float('inf'), 0.004),
        ],
    },
    'Europe': {
        'ai': [
            (0, 10000, 0.12),
            (10000, 100000, 0.11),
            (100000, 500000, 0.10),
            (500000, 1000000, 0.09),
            (1000000, float('inf'), 0.08),
        ],
        'advanced': [
            (0, 50000, 0.06),
            (50000, 150000, 0.055),
            (150000, 500000, 0.05),
            (500000, float('inf'), 0.045),
        ],
        'basic_marketing': [
            (0, float('inf'), 0.006),
        ],
        'basic_utility': [
            (0, float('inf'), 0.004),
        ],
    },
    'Rest of the World': {
        'ai': [
            (0, 10000, 0.12),
            (10000, 100000, 0.11),
            (100000, 500000, 0.10),
            (500000, 1000000, 0.09),
            (1000000, float('inf'), 0.08),
        ],
        'advanced': [
            (0, 50000, 0.06),
            (50000, 150000, 0.055),
            (150000, 500000, 0.05),
            (500000, float('inf'), 0.045),
        ],
        'basic_marketing': [
            (0, float('inf'), 0.006),
        ],
        'basic_utility': [
            (0, float('inf'), 0.004),
        ],
    },
}

# --- Cost Table by Country ---
# Meta costs for each country and message type.
meta_costs_table = {
    'India': {'marketing': 0.78, 'utility': 0.12, 'ai': 0.30},
    'MENA': {'marketing': 0.06, 'utility': 0.01, 'ai': 0.01},
    'LATAM': {'marketing': 0.06, 'utility': 0.01, 'ai': 0.01},
    'Africa': {'marketing': 0.06, 'utility': 0.01, 'ai': 0.01},
    'Europe': {'marketing': 0.06, 'utility': 0.01, 'ai': 0.01},
    'Rest of the World': {'marketing': 0.06, 'utility': 0.01, 'ai': 0.01},
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
        'bot_ui': 20000,
        'custom_ai': 30000,
    },
    'LATAM': {
        'currency': 'USD',
        'bot_ui': {
            'LATAM': 580,
            'India': 400,
        },
        'custom_ai': {
            'LATAM': 750,
            'India': 500,
        },
    },
    'MENA': {
        'currency': 'USD',
        'bot_ui': 300,
        'custom_ai': 500,
    },
    'Africa': {
        'currency': 'USD',
        'bot_ui': 300,
        'custom_ai': 420,
    },
    'Europe': {
        'currency': 'USD',
        'bot_ui': 300,
        'custom_ai': 420,
    },
    'Rest of the World': {
        'currency': 'USD',
        'bot_ui': 300,
        'custom_ai': 420,
    },
}

# --- Messaging Bundle Markup Rates by Country (for committed amount/bundle flow) ---
bundle_markup_rates = {
    'India': [
        {'min': 0, 'max': 50000, 'basic_marketing': 0.20, 'basic_utility': 0.05, 'advanced': 0.50, 'ai': 1.00},
        {'min': 50001, 'max': 150000, 'basic_marketing': 0.18, 'basic_utility': 0.05, 'advanced': 0.45, 'ai': 0.95},
        {'min': 150001, 'max': 200000, 'basic_marketing': 0.15, 'basic_utility': 0.04, 'advanced': 0.40, 'ai': 0.90},
        {'min': 200001, 'max': 250000, 'basic_marketing': 0.12, 'basic_utility': 0.04, 'advanced': 0.35, 'ai': 0.85},
        {'min': 250001, 'max': 500000, 'basic_marketing': 0.10, 'basic_utility': 0.03, 'advanced': 0.30, 'ai': 0.80},
        {'min': 500001, 'max': 750000, 'basic_marketing': 0.08, 'basic_utility': 0.03, 'advanced': 0.25, 'ai': 0.75},
        {'min': 750001, 'max': 1000000, 'basic_marketing': 0.05, 'basic_utility': 0.02, 'advanced': 0.20, 'ai': 0.70},
        {'min': 1000001, 'max': 2000000, 'basic_marketing': 0.03, 'basic_utility': 0.02, 'advanced': 0.15, 'ai': 0.65},
    ],
    'MENA': [
        {'min': 0, 'max': 1000, 'basic_marketing': 0.0033, 'basic_utility': 0.0008, 'advanced': 0.0083, 'ai': 0.0167},
        {'min': 1001, 'max': 1500, 'basic_marketing': 0.0030, 'basic_utility': 0.0008, 'advanced': 0.0075, 'ai': 0.0158},
        {'min': 1501, 'max': 2500, 'basic_marketing': 0.0025, 'basic_utility': 0.0007, 'advanced': 0.0067, 'ai': 0.0150},
        {'min': 2501, 'max': 3500, 'basic_marketing': 0.0020, 'basic_utility': 0.0006, 'advanced': 0.0058, 'ai': 0.0142},
        {'min': 3501, 'max': 5000, 'basic_marketing': 0.0017, 'basic_utility': 0.0005, 'advanced': 0.0050, 'ai': 0.0133},
        {'min': 5001, 'max': 7500, 'basic_marketing': 0.0013, 'basic_utility': 0.0004, 'advanced': 0.0042, 'ai': 0.0125},
        {'min': 7501, 'max': 10000, 'basic_marketing': 0.0008, 'basic_utility': 0.0003, 'advanced': 0.0033, 'ai': 0.0117},
        {'min': 10001, 'max': 15000, 'basic_marketing': 0.0005, 'basic_utility': 0.0003, 'advanced': 0.0025, 'ai': 0.0108},
    ],
    'LATAM': [
        {'min': 0, 'max': 1000, 'basic_marketing': 0.0033, 'basic_utility': 0.0008, 'advanced': 0.0083, 'ai': 0.0167},
        {'min': 1001, 'max': 1500, 'basic_marketing': 0.0030, 'basic_utility': 0.0008, 'advanced': 0.0075, 'ai': 0.0158},
        {'min': 1501, 'max': 2500, 'basic_marketing': 0.0025, 'basic_utility': 0.0007, 'advanced': 0.0067, 'ai': 0.0150},
        {'min': 2501, 'max': 3500, 'basic_marketing': 0.0020, 'basic_utility': 0.0006, 'advanced': 0.0058, 'ai': 0.0142},
        {'min': 3501, 'max': 5000, 'basic_marketing': 0.0017, 'basic_utility': 0.0005, 'advanced': 0.0050, 'ai': 0.0133},
        {'min': 5001, 'max': 7500, 'basic_marketing': 0.0013, 'basic_utility': 0.0004, 'advanced': 0.0042, 'ai': 0.0125},
        {'min': 7501, 'max': 10000, 'basic_marketing': 0.0008, 'basic_utility': 0.0003, 'advanced': 0.0033, 'ai': 0.0117},
        {'min': 10001, 'max': 15000, 'basic_marketing': 0.0005, 'basic_utility': 0.0003, 'advanced': 0.0025, 'ai': 0.0108},
    ],
    'Africa': [
        {'min': 0, 'max': 1000, 'basic_marketing': 0.0017, 'basic_utility': 0.0004, 'advanced': 0.0042, 'ai': 0.0083},
        {'min': 1001, 'max': 1500, 'basic_marketing': 0.0015, 'basic_utility': 0.0004, 'advanced': 0.0037, 'ai': 0.0079},
        {'min': 1501, 'max': 2500, 'basic_marketing': 0.0012, 'basic_utility': 0.0003, 'advanced': 0.0033, 'ai': 0.0075},
        {'min': 2501, 'max': 3500, 'basic_marketing': 0.0010, 'basic_utility': 0.0003, 'advanced': 0.0029, 'ai': 0.0071},
        {'min': 3501, 'max': 5000, 'basic_marketing': 0.0008, 'basic_utility': 0.0002, 'advanced': 0.0025, 'ai': 0.0067},
        {'min': 5001, 'max': 7500, 'basic_marketing': 0.0007, 'basic_utility': 0.0002, 'advanced': 0.0021, 'ai': 0.0062},
        {'min': 7501, 'max': 10000, 'basic_marketing': 0.0004, 'basic_utility': 0.0002, 'advanced': 0.0017, 'ai': 0.0058},
        {'min': 10001, 'max': 15000, 'basic_marketing': 0.0002, 'basic_utility': 0.0001, 'advanced': 0.0012, 'ai': 0.0054},
    ],
    'Europe': [
        {'min': 0, 'max': 1000, 'basic_marketing': 0.0042, 'basic_utility': 0.0010, 'advanced': 0.0105, 'ai': 0.0209},
        {'min': 1001, 'max': 1500, 'basic_marketing': 0.0038, 'basic_utility': 0.0009, 'advanced': 0.0094, 'ai': 0.0199},
        {'min': 1501, 'max': 2500, 'basic_marketing': 0.0031, 'basic_utility': 0.0008, 'advanced': 0.0084, 'ai': 0.0188},
        {'min': 2501, 'max': 3500, 'basic_marketing': 0.0025, 'basic_utility': 0.0007, 'advanced': 0.0073, 'ai': 0.0178},
        {'min': 3501, 'max': 5000, 'basic_marketing': 0.0021, 'basic_utility': 0.0006, 'advanced': 0.0063, 'ai': 0.0167},
        {'min': 5001, 'max': 7500, 'basic_marketing': 0.0017, 'basic_utility': 0.0005, 'advanced': 0.0052, 'ai': 0.0157},
        {'min': 7501, 'max': 10000, 'basic_marketing': 0.0010, 'basic_utility': 0.0004, 'advanced': 0.0042, 'ai': 0.0146},
        {'min': 10001, 'max': 15000, 'basic_marketing': 0.0006, 'basic_utility': 0.0003, 'advanced': 0.0031, 'ai': 0.0136},
    ],
    'Rest of the World': [
        {'min': 0, 'max': 1000, 'basic_marketing': 0.0033, 'basic_utility': 0.0008, 'advanced': 0.0083, 'ai': 0.0167},
        {'min': 1001, 'max': 1500, 'basic_marketing': 0.0030, 'basic_utility': 0.0008, 'advanced': 0.0075, 'ai': 0.0158},
        {'min': 1501, 'max': 2500, 'basic_marketing': 0.0025, 'basic_utility': 0.0007, 'advanced': 0.0067, 'ai': 0.0150},
        {'min': 2501, 'max': 3500, 'basic_marketing': 0.0020, 'basic_utility': 0.0006, 'advanced': 0.0058, 'ai': 0.0142},
        {'min': 3501, 'max': 5000, 'basic_marketing': 0.0017, 'basic_utility': 0.0005, 'advanced': 0.0050, 'ai': 0.0133},
        {'min': 5001, 'max': 7500, 'basic_marketing': 0.0013, 'basic_utility': 0.0004, 'advanced': 0.0042, 'ai': 0.0125},
        {'min': 7501, 'max': 10000, 'basic_marketing': 0.0008, 'basic_utility': 0.0003, 'advanced': 0.0033, 'ai': 0.0117},
        {'min': 10001, 'max': 15000, 'basic_marketing': 0.0005, 'basic_utility': 0.0003, 'advanced': 0.0025, 'ai': 0.0108},
    ],
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
    num_journeys = int(inputs.get('num_journeys_price') or 0)
    num_apis = int(inputs.get('num_apis_price') or 0)

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
    total_mandays += int(inputs.get('num_ai_workspace_commerce_price') or 0) * ACTIVITY_MANDAYS['ai_agents']
    total_mandays += int(inputs.get('num_ai_workspace_faq_price') or 0) * ACTIVITY_MANDAYS['ai_agents']
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
    num_journeys = int(inputs.get('num_journeys_price') or 0)
    num_apis = int(inputs.get('num_apis_price') or 0)
    num_ai_commerce = int(inputs.get('num_ai_workspace_commerce_price') or 0)
    num_ai_faq = int(inputs.get('num_ai_workspace_faq_price') or 0)
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
    If user enters 0 for bot_ui rate but selects any of Onboarding, UX, Testing/QA, AA Setup as Yes, use default rate for those activities.
    Returns (total_cost, currency, breakdown_dict)
    """
    country = inputs.get('country', 'India')
    dev_location = inputs.get('dev_location', 'India')
    rates = COUNTRY_MANDAY_RATES.get(country, COUNTRY_MANDAY_RATES['India'])
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
    currency = rates['currency']

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
    slabs_by_country = {
        'India': [
            (0, 50000,    {'marketing': 0.20, 'utility': 0.05, 'advanced': 0.50, 'ai': 1.00}),
            (50000, 150000, {'marketing': 0.18, 'utility': 0.05, 'advanced': 0.45, 'ai': 0.95}),
            (150000, 200000, {'marketing': 0.15, 'utility': 0.04, 'advanced': 0.40, 'ai': 0.90}),
            (200000, 250000, {'marketing': 0.12, 'utility': 0.04, 'advanced': 0.35, 'ai': 0.85}),
            (250000, 500000, {'marketing': 0.10, 'utility': 0.03, 'advanced': 0.30, 'ai': 0.80}),
            (500000, 750000, {'marketing': 0.08, 'utility': 0.03, 'advanced': 0.25, 'ai': 0.75}),
            (750000, 1000000, {'marketing': 0.05, 'utility': 0.02, 'advanced': 0.20, 'ai': 0.70}),
            (1000000, float('inf'), {'marketing': 0.03, 'utility': 0.02, 'advanced': 0.15, 'ai': 0.65}),
        ],
        'MENA': [
            (0, 2500,    {'marketing': 0.0168, 'utility': 0.0042, 'advanced': 0.0420, 'ai': 0.0840}),
            (2500, 5000, {'marketing': 0.0151, 'utility': 0.0038, 'advanced': 0.0378, 'ai': 0.0798}),
            (5000, 7500, {'marketing': 0.0126, 'utility': 0.0034, 'advanced': 0.0336, 'ai': 0.0756}),
            (7500, 10000, {'marketing': 0.0101, 'utility': 0.0029, 'advanced': 0.0294, 'ai': 0.0714}),
            (10000, 15000, {'marketing': 0.0084, 'utility': 0.0025, 'advanced': 0.0252, 'ai': 0.0672}),
            (15000, 20000, {'marketing': 0.0067, 'utility': 0.0021, 'advanced': 0.0210, 'ai': 0.0630}),
            (20000, 50000, {'marketing': 0.0042, 'utility': 0.0017, 'advanced': 0.0168, 'ai': 0.0588}),
            (50000, 100000, {'marketing': 0.0025, 'utility': 0.0013, 'advanced': 0.0126, 'ai': 0.0546}),
            (100000, float('inf'), {'marketing': 0.0025, 'utility': 0.0013, 'advanced': 0.0126, 'ai': 0.0546}),
        ],
        'LATAM': [
            (0, 2500,    {'marketing': 0.0240, 'utility': 0.0060, 'advanced': 0.0600, 'ai': 0.1200}),
            (2500, 5000, {'marketing': 0.0216, 'utility': 0.0054, 'advanced': 0.0540, 'ai': 0.1140}),
            (5000, 7500, {'marketing': 0.0180, 'utility': 0.0048, 'advanced': 0.0480, 'ai': 0.1080}),
            (7500, 10000, {'marketing': 0.0144, 'utility': 0.0042, 'advanced': 0.0420, 'ai': 0.1020}),
            (10000, 15000, {'marketing': 0.0120, 'utility': 0.0036, 'advanced': 0.0360, 'ai': 0.0960}),
            (15000, 20000, {'marketing': 0.0096, 'utility': 0.0030, 'advanced': 0.0300, 'ai': 0.0900}),
            (20000, 50000, {'marketing': 0.0060, 'utility': 0.0024, 'advanced': 0.0240, 'ai': 0.0840}),
            (50000, 100000, {'marketing': 0.0036, 'utility': 0.0018, 'advanced': 0.0180, 'ai': 0.0780}),
            (100000, float('inf'), {'marketing': 0.0036, 'utility': 0.0018, 'advanced': 0.0180, 'ai': 0.0780}),
        ],
        'Africa': [
            (0, 2500,    {'marketing': 0.0096, 'utility': 0.0024, 'advanced': 0.0240, 'ai': 0.0480}),
            (2500, 5000, {'marketing': 0.0086, 'utility': 0.0022, 'advanced': 0.0216, 'ai': 0.0456}),
            (5000, 7500, {'marketing': 0.0072, 'utility': 0.0019, 'advanced': 0.0192, 'ai': 0.0432}),
            (7500, 10000, {'marketing': 0.0058, 'utility': 0.0017, 'advanced': 0.0168, 'ai': 0.0408}),
            (10000, 15000, {'marketing': 0.0048, 'utility': 0.0014, 'advanced': 0.0144, 'ai': 0.0384}),
            (15000, 20000, {'marketing': 0.0038, 'utility': 0.0012, 'advanced': 0.0120, 'ai': 0.0360}),
            (20000, 50000, {'marketing': 0.0024, 'utility': 0.0010, 'advanced': 0.0096, 'ai': 0.0336}),
            (50000, 100000, {'marketing': 0.0014, 'utility': 0.0007, 'advanced': 0.0072, 'ai': 0.0312}),
            (100000, float('inf'), {'marketing': 0.0014, 'utility': 0.0007, 'advanced': 0.0072, 'ai': 0.0312}),
        ],
        'Europe': [
            (0, 2500,    {'marketing': 0.0480, 'utility': 0.0120, 'advanced': 0.1200, 'ai': 0.2400}),
            (2500, 5000, {'marketing': 0.0432, 'utility': 0.0108, 'advanced': 0.1080, 'ai': 0.2280}),
            (5000, 7500, {'marketing': 0.0360, 'utility': 0.0096, 'advanced': 0.0960, 'ai': 0.2160}),
            (7500, 10000, {'marketing': 0.0288, 'utility': 0.0084, 'advanced': 0.0840, 'ai': 0.2040}),
            (10000, 15000, {'marketing': 0.0240, 'utility': 0.0072, 'advanced': 0.0720, 'ai': 0.1920}),
            (15000, 20000, {'marketing': 0.0192, 'utility': 0.0060, 'advanced': 0.0600, 'ai': 0.1800}),
            (20000, 50000, {'marketing': 0.0120, 'utility': 0.0048, 'advanced': 0.0480, 'ai': 0.1680}),
            (50000, 100000, {'marketing': 0.0072, 'utility': 0.0036, 'advanced': 0.0360, 'ai': 0.1560}),
            (100000, float('inf'), {'marketing': 0.0072, 'utility': 0.0036, 'advanced': 0.0360, 'ai': 0.1560}),
        ],
        'Rest of the World': [
            (0, 2500,    {'marketing': 0.0240, 'utility': 0.0060, 'advanced': 0.0600, 'ai': 0.1200}),
            (2500, 5000, {'marketing': 0.0216, 'utility': 0.0054, 'advanced': 0.0540, 'ai': 0.1140}),
            (5000, 7500, {'marketing': 0.0180, 'utility': 0.0048, 'advanced': 0.0480, 'ai': 0.1080}),
            (7500, 10000, {'marketing': 0.0144, 'utility': 0.0042, 'advanced': 0.0420, 'ai': 0.1020}),
            (10000, 15000, {'marketing': 0.0120, 'utility': 0.0036, 'advanced': 0.0360, 'ai': 0.0960}),
            (15000, 20000, {'marketing': 0.0096, 'utility': 0.0030, 'advanced': 0.0300, 'ai': 0.0900}),
            (20000, 50000, {'marketing': 0.0060, 'utility': 0.0024, 'advanced': 0.0240, 'ai': 0.0840}),
            (50000, 100000, {'marketing': 0.0036, 'utility': 0.0018, 'advanced': 0.0180, 'ai': 0.0780}),
            (100000, float('inf'), {'marketing': 0.0036, 'utility': 0.0018, 'advanced': 0.0180, 'ai': 0.0780}),
        ],
    }
    slabs = slabs_by_country.get(country, slabs_by_country['Rest of the World'])
    for lower, upper, rates in slabs:
        if lower <= committed_amount < upper:
            return rates
    return slabs[0][2]  # fallback to first slab

def get_committed_amount_rates_india(committed_amount):
    return get_committed_amount_rates('India', committed_amount)

