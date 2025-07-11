# calculator.py

# --- Pricing and Cost Calculation Module ---
# This module provides pricing tiers, cost tables, and functions for calculating suggested prices, overage prices, and total pricing for the messaging calculator app.

# --- Price Tiers by Country and Message Type ---
# Each country has a set of volume-based price tiers for each message type.

# --- Cost Table by Country ---
# Meta costs for each country and message type.

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

from pricing_config import COUNTRY_MANDAY_RATES, price_tiers, meta_costs_table, bundle_markup_rates
from typing import Any, Dict, Optional, Tuple, List

def get_suggested_price(country: str, msg_type: str, volume: int, currency: Optional[str] = None) -> float:
    """
    Return the suggested price for a message type, country, and volume.
    Looks up the correct tier based on volume.
    """
    tiers = price_tiers.get(country, {}).get(msg_type, [])
    for lower, upper, price in tiers:
        if lower < volume <= upper:
            return price
    return 0.0

def get_next_tier_price(country: str, msg_type: str, volume: int) -> float:
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

def _get_prices(country: str, ai_volume: int, advanced_volume: int, basic_marketing_volume: int, basic_utility_volume: int, ai_price: Optional[float], advanced_price: Optional[float], basic_marketing_price: Optional[float], basic_utility_price: Optional[float]) -> Dict[str, Dict[str, float]]:
    suggested = {
        'ai': get_suggested_price(country, 'ai', ai_volume),
        'advanced': get_suggested_price(country, 'advanced', advanced_volume),
        'basic_marketing': get_suggested_price(country, 'basic_marketing', basic_marketing_volume),
        'basic_utility': get_suggested_price(country, 'basic_utility', basic_utility_volume),
    }
    overage = {
        'ai': get_next_tier_price(country, 'ai', ai_volume),
        'advanced': get_next_tier_price(country, 'advanced', advanced_volume),
        'basic_marketing': get_next_tier_price(country, 'basic_marketing', basic_marketing_volume),
        'basic_utility': get_next_tier_price(country, 'basic_utility', basic_utility_volume),
    }
    user = {
        'ai': ai_price if ai_price is not None else suggested['ai'],
        'advanced': advanced_price if advanced_price is not None else suggested['advanced'],
        'basic_marketing': basic_marketing_price if basic_marketing_price is not None else suggested['basic_marketing'],
        'basic_utility': basic_utility_price if basic_utility_price is not None else suggested['basic_utility'],
    }
    return {'suggested': suggested, 'overage': overage, 'user': user}

def _calculate_revenue(costs: Dict[str, float], user_prices: Dict[str, float], volumes: Dict[str, int]) -> float:
    return (
        (costs['ai'] + user_prices['ai']) * volumes['ai'] +
        (costs['ai'] + user_prices['advanced']) * volumes['advanced'] +
        (costs['marketing'] + user_prices['basic_marketing']) * volumes['basic_marketing'] +
        (costs['utility'] + user_prices['basic_utility']) * volumes['basic_utility']
    )

def _calculate_costs(costs: Dict[str, float], volumes: Dict[str, int]) -> Tuple[float, float, float]:
    adv_marketing_vol = 0.0
    adv_utility_vol = 0.0
    channel_cost = (
        (costs['marketing'] * adv_marketing_vol)
        + (costs['utility'] * adv_utility_vol)
        + (volumes['basic_marketing'] * costs['marketing'])
        + (volumes['basic_utility'] * costs['utility'])
    )
    ai_costs = costs['ai'] * volumes['ai']
    total_costs = channel_cost + ai_costs
    return channel_cost, ai_costs, total_costs

def _calculate_margin(revenue: float, platform_fee: float, total_costs: float) -> Tuple[float, float]:
    margin_denom = revenue + platform_fee
    if margin_denom > 0:
        margin = (revenue + platform_fee - total_costs) / margin_denom
        margin_percentage = margin * 100
    else:
        margin = 0
        margin_percentage = 0
    return margin, margin_percentage

def _build_line_items(costs: Dict[str, float], user_prices: Dict[str, float], suggested_prices: Dict[str, float], overage_prices: Dict[str, float], volumes: Dict[str, int], revenues: Dict[str, float], suggested_revenues: Dict[str, float]) -> List[Dict[str, Any]]:
    return [
        {
            'label': 'AI Message',
            'volume': volumes['ai'],
            'chosen_price': user_prices['ai'],
            'suggested_price': suggested_prices['ai'],
            'overage_price': overage_prices['ai'],
            'meta_cost': costs['ai'],
            'final_price': costs['ai'] + user_prices['ai'],
            'revenue': revenues['ai'],
            'suggested_revenue': suggested_revenues['ai']
        },
        {
            'label': 'Advanced Message',
            'volume': volumes['advanced'],
            'chosen_price': user_prices['advanced'],
            'suggested_price': suggested_prices['advanced'],
            'overage_price': overage_prices['advanced'],
            'meta_cost': costs['ai'],
            'final_price': costs['ai'] + user_prices['advanced'],
            'revenue': revenues['advanced'],
            'suggested_revenue': suggested_revenues['advanced']
        },
        {
            'label': 'Basic Marketing Message',
            'volume': volumes['basic_marketing'],
            'chosen_price': user_prices['basic_marketing'],
            'suggested_price': suggested_prices['basic_marketing'],
            'overage_price': overage_prices['basic_marketing'],
            'meta_cost': costs['marketing'],
            'final_price': costs['marketing'] + user_prices['basic_marketing'],
            'revenue': revenues['basic_marketing'],
            'suggested_revenue': suggested_revenues['basic_marketing']
        },
        {
            'label': 'Basic Utility/Authentication Message',
            'volume': volumes['basic_utility'],
            'chosen_price': user_prices['basic_utility'],
            'suggested_price': suggested_prices['basic_utility'],
            'overage_price': overage_prices['basic_utility'],
            'meta_cost': costs['utility'],
            'final_price': costs['utility'] + user_prices['basic_utility'],
            'revenue': revenues['basic_utility'],
            'suggested_revenue': suggested_revenues['basic_utility']
        },
    ]

def calculate_pricing(
    country: str,
    ai_volume: int,
    advanced_volume: int,
    basic_marketing_volume: int,
    basic_utility_volume: int,
    platform_fee: float,
    ai_price: Optional[float] = None,
    advanced_price: Optional[float] = None,
    basic_marketing_price: Optional[float] = None,
    basic_utility_price: Optional[float] = None
) -> Dict[str, Any]:
    costs = meta_costs_table.get(country, meta_costs_table['India'])
    volumes = {
        'ai': ai_volume,
        'advanced': advanced_volume,
        'basic_marketing': basic_marketing_volume,
        'basic_utility': basic_utility_volume,
    }
    prices = _get_prices(country, ai_volume, advanced_volume, basic_marketing_volume, basic_utility_volume, ai_price, advanced_price, basic_marketing_price, basic_utility_price)
    user_prices = prices['user']
    suggested_prices = prices['suggested']
    overage_prices = prices['overage']
    revenue = _calculate_revenue(costs, user_prices, volumes)
    suggested_revenue = _calculate_revenue(costs, suggested_prices, volumes)
    channel_cost, ai_costs, total_costs = _calculate_costs(costs, volumes)
    margin, margin_percentage = _calculate_margin(revenue, platform_fee, total_costs)
    suggested_margin, suggested_margin_percentage = _calculate_margin(suggested_revenue, platform_fee, total_costs)
    revenues = {
        'ai': (costs['ai'] + user_prices['ai']) * ai_volume,
        'advanced': (costs['ai'] + user_prices['advanced']) * advanced_volume,
        'basic_marketing': (costs['marketing'] + user_prices['basic_marketing']) * basic_marketing_volume,
        'basic_utility': (costs['utility'] + user_prices['basic_utility']) * basic_utility_volume,
    }
    suggested_revenues = {
        'ai': (costs['ai'] + suggested_prices['ai']) * ai_volume,
        'advanced': (costs['ai'] + suggested_prices['advanced']) * advanced_volume,
        'basic_marketing': (costs['marketing'] + suggested_prices['basic_marketing']) * basic_marketing_volume,
        'basic_utility': (costs['utility'] + suggested_prices['basic_utility']) * basic_utility_volume,
    }
    line_items = _build_line_items(costs, user_prices, suggested_prices, overage_prices, volumes, revenues, suggested_revenues)
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

def calculate_total_mandays(inputs: Dict[str, Any]) -> float:
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

def calculate_total_mandays_breakdown(inputs: Dict[str, Any]) -> Dict[str, float]:
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

def calculate_total_manday_cost(inputs: Dict[str, Any], manday_rates: Optional[Dict[str, Any]] = None) -> Tuple[float, str, Dict[str, Any]]:
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

def get_committed_amount_rates(country: str, committed_amount: float) -> Dict[str, float]:
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

def get_committed_amount_rates_india(committed_amount: float) -> Dict[str, float]:
    return get_committed_amount_rates('India', committed_amount)
