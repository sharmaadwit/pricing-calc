# calculator.py

# --- Pricing and Cost Calculation Module ---
# This module provides pricing tiers, cost tables, and functions for calculating suggested prices, overage prices, and total pricing for the messaging calculator app.

# --- Price Tiers by Country and Message Type ---
# Each country has a set of volume-based price tiers for each message type.

# --- Cost Table by Country ---
# Meta costs for each country and message type.

from pricing_config import (
    meta_costs_table,
    COUNTRY_MANDAY_RATES,
    ACTIVITY_MANDAYS,
    committed_amount_slabs,
    VOICE_DEV_EFFORT,
    VOICE_PLATFORM_FEES,
    PSTN_CALLING_CHARGES,
    WHATSAPP_VOICE_CHARGES,
    get_whatsapp_voice_rate,
)
import sys

# New function to map volume to committed amount slab rate

def get_committed_amount_rate_for_volume(country, msg_type, volume):
    slabs = committed_amount_slabs.get(country, committed_amount_slabs['APAC'])
    for lower, upper, rates in slabs:
        if lower <= volume < upper:
            return rates[msg_type]
    # Fallback to highest slab if above all
    return slabs[-1][2][msg_type]

# Update get_suggested_price to use committed amount slab rates for volume route

def get_suggested_price(country, msg_type, volume, currency=None):
    """
    Return the suggested price for a message type, country, and volume.
    Now uses the committed amount slab rate for the estimated monthly revenue.
    """
    return get_committed_amount_rate_for_volume(country, msg_type, volume)

def get_lowest_tier_price(country, msg_type):
    """
    Return the lowest (smallest volume) price for a given country and message type
    using the first slab in committed_amount_slabs.
    """
    slabs = committed_amount_slabs.get(country, committed_amount_slabs.get('Rest of the World', []))
    if not slabs:
        return 0
    return slabs[0][2][msg_type]

def get_next_tier_price(country, msg_type, volume):
    """
    Deprecated: Overage prices are no longer used or displayed.
    """
    return 0.0

def calculate_pricing(
    country, ai_volume, advanced_volume, basic_marketing_volume, basic_utility_volume, platform_fee,
    ai_price=None, advanced_price=None, basic_marketing_price=None, basic_utility_price=None,
    voice_notes_rate=None
):
    """
    Calculate all pricing, revenue, costs, and margin for the given inputs.
    Returns a dictionary with detailed line items and summary values.
    """
    costs = meta_costs_table.get(country, meta_costs_table['APAC'])

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
    # Ensure overage prices are never lower than rate card prices
    def safe_overage_price(base_price, markup=1.2):
        return max(base_price * markup, base_price)
    
    overage_ai_price = safe_overage_price(float(user_ai_price))
    overage_advanced_price = safe_overage_price(float(user_advanced_price))
    overage_basic_marketing_price = safe_overage_price(float(user_basic_marketing_price))
    overage_basic_utility_price = safe_overage_price(float(user_basic_utility_price))

    # Revenue (user-chosen)
    ai_revenue = (costs['ai'] + user_ai_price) * ai_volume
    advanced_revenue = user_advanced_price * advanced_volume  # Only markup for advanced
    basic_marketing_revenue = (costs['marketing'] + user_basic_marketing_price) * basic_marketing_volume
    basic_utility_revenue = (costs['utility'] + user_basic_utility_price) * basic_utility_volume
    voice_notes_revenue = 0  # Billed on actuals, no volume input
    revenue = ai_revenue + advanced_revenue + basic_marketing_revenue + basic_utility_revenue + voice_notes_revenue

    # Revenue (suggested)
    ai_final_price_s = costs['ai'] + suggested_ai_price
    advanced_final_price_s = suggested_advanced_price
    basic_marketing_final_price_s = costs['marketing'] + suggested_basic_marketing_price
    basic_utility_final_price_s = costs['utility'] + suggested_basic_utility_price

    ai_revenue_s = ai_final_price_s * ai_volume
    advanced_revenue_s = advanced_final_price_s * advanced_volume
    basic_marketing_revenue_s = basic_marketing_final_price_s * basic_marketing_volume
    basic_utility_revenue_s = basic_utility_final_price_s * basic_utility_volume
    voice_notes_revenue_s = 0  # Billed on actuals, no volume input
    suggested_revenue = ai_revenue_s + advanced_revenue_s + basic_marketing_revenue_s + basic_utility_revenue_s + voice_notes_revenue_s

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
            'meta_cost': 0,  # Always 0 for advanced
            'final_price': user_advanced_price,  # Only the slab/user price
            'revenue': user_advanced_price * advanced_volume,
            'suggested_revenue': suggested_advanced_price * advanced_volume
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
    
    # Add voice notes to line items if enabled
    if voice_notes_rate:
        line_items.append({
            'label': 'Voice Notes',
            'volume': 0,  # Billed on actuals, no volume input
            'chosen_price': voice_notes_rate,
            'suggested_price': voice_notes_rate,
            'meta_cost': 0,  # No meta cost for voice notes
            'final_price': voice_notes_rate,
            'revenue': voice_notes_revenue,
            'suggested_revenue': voice_notes_revenue_s
        })

    return {
        'line_items': line_items,
        'platform_fee': platform_fee,
        'revenue': revenue + platform_fee,
        'suggested_revenue': suggested_revenue + platform_fee if suggested_revenue is not None else None,
        'channel_cost': channel_cost,
        'ai_costs': ai_costs,
        'total_costs': total_costs,
        'margin': f"{margin_percentage:.3f}%",
        'suggested_margin': f"{suggested_margin_percentage:.3f}%"
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
    # AI Agents (Commerce + FAQ + Support)
    total_mandays += int(inputs.get('num_ai_workspace_commerce_price') or 0) * ACTIVITY_MANDAYS['ai_agents']
    total_mandays += int(inputs.get('num_ai_workspace_faq_price') or 0) * ACTIVITY_MANDAYS['ai_agents']
    total_mandays += int(inputs.get('num_ai_workspace_support_price') or 0) * ACTIVITY_MANDAYS['ai_workspace_support']
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
    num_ai_support = int(inputs.get('num_ai_workspace_support_price') or 0)
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
    if num_ai_support > 0:
        custom_ai_mandays += num_ai_support * ACTIVITY_MANDAYS['ai_workspace_support']
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
    country = inputs.get('country', 'India').strip()
    dev_location = (inputs.get('dev_location') or 'India').strip()
    rates = COUNTRY_MANDAY_RATES.get(country, COUNTRY_MANDAY_RATES['APAC'])
    # Only use dev_location for India, otherwise use the main rate
    if country == 'India':
        bot_ui_rate = rates['bot_ui'][dev_location] if isinstance(rates['bot_ui'], dict) else rates['bot_ui']
        custom_ai_rate = rates['custom_ai'][dev_location] if isinstance(rates['custom_ai'], dict) else rates['custom_ai']
        currency = rates['currency']
    else:
        bot_ui_rate = rates['bot_ui']
        custom_ai_rate = rates['custom_ai']
        currency = rates['currency']
    print(f"DEBUG: [calculator.py] dev_cost_currency = {currency}, country = '{country}', dev_location = '{dev_location}'", file=sys.stderr, flush=True)
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
    # currency = rates['currency']  # This will be 'USD' for Rest of the World

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
    slabs = committed_amount_slabs.get(country, committed_amount_slabs['APAC'])
    for lower, upper, rates in slabs:
        if lower <= committed_amount < upper:
            return rates
    return slabs[0][2]  # fallback to first slab

def get_committed_amount_rates_india(committed_amount):
    return get_committed_amount_rates('India', committed_amount)

# =============================================================================
# Voice Channel Helpers
# =============================================================================

def calculate_voice_dev_mandays(inputs):
    """
    Calculate total mandays for voice development work based on inputs and VOICE_DEV_EFFORT.
    """
    total_mandays = 0
    try:
        num_voice_journeys = int(inputs.get('num_voice_journeys', 0) or 0)
        total_mandays += num_voice_journeys * VOICE_DEV_EFFORT['journey']
    except Exception:
        pass
    try:
        num_voice_apis = int(inputs.get('num_voice_apis', 0) or 0)
        total_mandays += num_voice_apis * VOICE_DEV_EFFORT['api_integration']
    except Exception:
        pass
    try:
        num_additional_languages = int(inputs.get('num_additional_voice_languages', 0) or 0)
        if num_additional_languages > 0:
            base_effort = total_mandays
            total_mandays += base_effort * VOICE_DEV_EFFORT['additional_language_multiplier'] * num_additional_languages
    except Exception:
        pass
    agent_handover_pstn = inputs.get('agent_handover_pstn', 'None')
    if agent_handover_pstn == 'Knowlarity':
        total_mandays += VOICE_DEV_EFFORT['agent_handover_pstn_knowlarity']
    elif agent_handover_pstn == 'Other':
        total_mandays += VOICE_DEV_EFFORT['agent_handover_pstn_other']
    whatsapp_voice_platform = inputs.get('whatsapp_voice_platform', 'None')
    if whatsapp_voice_platform == 'Knowlarity':
        total_mandays += VOICE_DEV_EFFORT['whatsapp_voice_knowlarity']
    elif whatsapp_voice_platform == 'Other':
        total_mandays += VOICE_DEV_EFFORT['whatsapp_voice_other']
    return total_mandays

def calculate_voice_platform_fee(inputs, has_text_ai=False):
    """
    Calculate voice platform fee components in INR.
    """
    total_fee = 0.0
    if inputs.get('voice_ai_enabled', 'No') == 'Yes':
        if not has_text_ai:
            total_fee += VOICE_PLATFORM_FEES['voice_ai']
    if inputs.get('agent_handover_pstn', 'None') == 'Knowlarity':
        total_fee += VOICE_PLATFORM_FEES['knowlarity_platform']
    if inputs.get('virtual_number_required', 'No') == 'Yes':
        total_fee += VOICE_PLATFORM_FEES['virtual_number']
    return total_fee

def _parse_float(val):
    try:
        return float(str(val).replace(',', '')) if val not in (None, '') else 0.0
    except Exception:
        return 0.0

def calculate_voice_calling_costs(inputs, country='India'):
    """
    Calculate PSTN and WhatsApp voice calling costs as per configured rates.
    Returns a dict with line items and total.
    """
    costs = {
        'pstn_inbound_ai': 0.0,
        'pstn_outbound_ai': 0.0,
        'pstn_manual_c2c': 0.0,
        'whatsapp_voice_outbound': 0.0,
        'whatsapp_voice_inbound': 0.0,
        'total': 0.0,
    }
    # Optional user override rates for PSTN/WhatsApp
    try:
        pstn_in_bundled_rate = float(inputs.get('vr_pstn_in_bundled', 0) or 0)
    except Exception:
        pstn_in_bundled_rate = 0
    try:
        pstn_in_overage_rate = float(inputs.get('vr_pstn_in_overage', 0) or 0)
    except Exception:
        pstn_in_overage_rate = 0
    try:
        pstn_out_bundled_rate = float(inputs.get('vr_pstn_out_bundled', 0) or 0)
    except Exception:
        pstn_out_bundled_rate = 0
    try:
        pstn_out_overage_rate = float(inputs.get('vr_pstn_out_overage', 0) or 0)
    except Exception:
        pstn_out_overage_rate = 0
    try:
        pstn_manual_bundled_rate = float(inputs.get('vr_pstn_manual_bundled', 0) or 0)
    except Exception:
        pstn_manual_bundled_rate = 0
    try:
        pstn_manual_overage_rate = float(inputs.get('vr_pstn_manual_overage', 0) or 0)
    except Exception:
        pstn_manual_overage_rate = 0
    try:
        wa_out_rate_override = float(inputs.get('vr_wa_out_per_min', 0) or 0)
    except Exception:
        wa_out_rate_override = 0
    try:
        wa_in_rate_override = float(inputs.get('vr_wa_in_per_min', 0) or 0)
    except Exception:
        wa_in_rate_override = 0

    # PSTN bundled vs overage
    inbound_min = _parse_float(inputs.get('pstn_inbound_ai_minutes', 0))
    inbound_commit = _parse_float(inputs.get('pstn_inbound_committed', 0))
    outbound_min = _parse_float(inputs.get('pstn_outbound_ai_minutes', 0))
    outbound_commit = _parse_float(inputs.get('pstn_outbound_committed', 0))
    manual_min = _parse_float(inputs.get('pstn_manual_minutes', 0))
    manual_commit = _parse_float(inputs.get('pstn_manual_committed', 0))
    if inbound_min > 0:
        bundled = min(inbound_min, inbound_commit)
        overage = max(0.0, inbound_min - inbound_commit)
        in_bundled = pstn_in_bundled_rate or PSTN_CALLING_CHARGES['inbound_ai']['bundled']
        in_overage = pstn_in_overage_rate or PSTN_CALLING_CHARGES['inbound_ai']['overage']
        costs['pstn_inbound_ai'] = bundled * in_bundled + overage * in_overage
    if outbound_min > 0:
        bundled = min(outbound_min, outbound_commit)
        overage = max(0.0, outbound_min - outbound_commit)
        out_bundled = pstn_out_bundled_rate or PSTN_CALLING_CHARGES['outbound_ai']['bundled']
        out_overage = pstn_out_overage_rate or PSTN_CALLING_CHARGES['outbound_ai']['overage']
        costs['pstn_outbound_ai'] = bundled * out_bundled + overage * out_overage
    if manual_min > 0:
        bundled = min(manual_min, manual_commit)
        overage = max(0.0, manual_min - manual_commit)
        man_bundled = pstn_manual_bundled_rate or PSTN_CALLING_CHARGES['manual_c2c']['bundled']
        man_overage = pstn_manual_overage_rate or PSTN_CALLING_CHARGES['manual_c2c']['overage']
        costs['pstn_manual_c2c'] = bundled * man_bundled + overage * man_overage
    # WhatsApp Voice
    wa_out_min = _parse_float(inputs.get('whatsapp_voice_outbound_minutes', 0))
    wa_in_min = _parse_float(inputs.get('whatsapp_voice_inbound_minutes', 0))
    total_wa_min = wa_out_min + wa_in_min
    if wa_out_min > 0:
        outbound_rate = wa_out_rate_override or get_whatsapp_voice_rate(country, total_wa_min, 'outbound')
        costs['whatsapp_voice_outbound'] = wa_out_min * outbound_rate
    if wa_in_min > 0:
        inbound_rate = wa_in_rate_override or get_whatsapp_voice_rate(country, total_wa_min, 'inbound')
        costs['whatsapp_voice_inbound'] = wa_in_min * inbound_rate
    costs['total'] = (
        costs['pstn_inbound_ai']
        + costs['pstn_outbound_ai']
        + costs['pstn_manual_c2c']
        + costs['whatsapp_voice_outbound']
        + costs['whatsapp_voice_inbound']
    )
    return costs

def calculate_voice_pricing(inputs, country='India', has_text_ai=False):
    """
    High-level aggregator for voice pricing: development, platform, calling.
    Returns a dict with mandays, cost breakdown and total.
    """
    voice_mandays = calculate_voice_dev_mandays(inputs)
    # Use custom_ai rate for voice work when available, else bot_ui
    rates = COUNTRY_MANDAY_RATES.get(country, COUNTRY_MANDAY_RATES['APAC'])
    if isinstance(rates.get('custom_ai'), dict):
        # Country like LATAM has per dev_location dict; default to country key or any
        dev_location = (inputs.get('dev_location') or 'India').strip()
        custom_ai_rate = rates['custom_ai'].get(dev_location, list(rates['custom_ai'].values())[0])
    else:
        custom_ai_rate = rates.get('custom_ai', rates.get('bot_ui', 0))
    voice_dev_cost = voice_mandays * float(custom_ai_rate or 0)
    whatsapp_setup_fee = VOICE_DEV_EFFORT['whatsapp_voice_setup_fee_other'] if inputs.get('whatsapp_voice_platform', 'None') == 'Other' else 0
    voice_platform_fee = calculate_voice_platform_fee(inputs, has_text_ai)
    calling_costs = calculate_voice_calling_costs(inputs, country)
    total_voice_cost = voice_dev_cost + whatsapp_setup_fee + voice_platform_fee + calling_costs['total']
    return {
        'voice_mandays': voice_mandays,
        'voice_dev_cost': voice_dev_cost,
        'whatsapp_setup_fee': whatsapp_setup_fee,
        'voice_platform_fee': voice_platform_fee,
        'calling_costs': calling_costs,
        'total_voice_cost': total_voice_cost,
    }
