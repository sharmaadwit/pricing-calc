# calculator.py

# --- Price Tiers by Country and Message Type ---
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
meta_costs_table = {
    'India': {'marketing': 0.78, 'utility': 0.12, 'ai': 0.30},
    'MENA': {'marketing': 0.0455 * 3.67, 'utility': 0.0115 * 3.67, 'ai': 0.0036 * 3.67},
    'LATAM': {'marketing': 0.0625, 'utility': 0.0080, 'ai': 0.0036},
    'Africa': {'marketing': 0.0379, 'utility': 0.0076, 'ai': 0.0036},
    'Europe': {'marketing': 0.0529, 'utility': 0.0220, 'ai': 0.0036},
    'Rest of the World': {'marketing': 0.0604, 'utility': 0.0077, 'ai': 0.0036},
}

def get_suggested_price(country, msg_type, volume, currency=None):
    """Return the suggested price for a message type, country, and volume."""
    tiers = price_tiers.get(country, {}).get(msg_type, [])
    for lower, upper, price in tiers:
        if lower < volume <= upper:
            return price
    return 0.0

def get_next_tier_price(country, msg_type, volume):
    """Return the next tier price for a message type, country, and volume (overage price)."""
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
    ai_final_price = costs['ai'] + user_ai_price
    advanced_final_price = costs['ai'] + user_advanced_price
    basic_marketing_final_price = costs['marketing'] + user_basic_marketing_price
    basic_utility_final_price = costs['utility'] + user_basic_utility_price

    ai_revenue = ai_final_price * ai_volume
    advanced_revenue = advanced_final_price * advanced_volume
    basic_marketing_revenue = basic_marketing_final_price * basic_marketing_volume
    basic_utility_revenue = basic_utility_final_price * basic_utility_volume
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
            'final_price': ai_final_price,
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
            'final_price': advanced_final_price,
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
            'final_price': basic_marketing_final_price,
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
            'final_price': basic_utility_final_price,
            'revenue': basic_utility_revenue,
            'suggested_revenue': basic_utility_revenue_s
        },
    ]

    return {
        'line_items': line_items,
        'platform_fee': platform_fee,
        'revenue': f"{(revenue + platform_fee):.2f}",
        'suggested_revenue': f"{(suggested_revenue + platform_fee):.2f}",
        'channel_cost': f"{channel_cost:.2f}",
        'ai_costs': f"{ai_costs:.2f}",
        'total_costs': f"{total_costs:.2f}",
        'margin': f"{margin_percentage:.2f}%",
        'suggested_margin': f"{suggested_margin_percentage:.2f}%"
    }
