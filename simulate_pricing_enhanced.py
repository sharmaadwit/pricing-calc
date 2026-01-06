#!/usr/bin/env python3
"""
Enhanced Pricing Simulation with Detailed Breakdown
Shows Meta costs, Gupshup markup, internal sections, and pricing options
"""

from app import calculate_pricing_simulation, calculate_platform_fee
from calculator import calculate_pricing, get_suggested_price, get_committed_amount_rate_for_volume
from pricing_config import (
    COUNTRY_CURRENCY,
    meta_costs_table,
    committed_amount_slabs,
    get_voice_notes_price,
    compute_ai_price_components,
    AI_AGENT_PRICING,
)
import json

def format_currency(amount, currency_symbol):
    """Format amount with currency symbol and proper formatting"""
    if currency_symbol == '₹':
        return f"₹{amount:,.2f}"
    else:
        return f"${amount:,.2f}"

def print_separator(title=""):
    """Print a visual separator"""
    if title:
        print(f"\n{'='*80}")
        print(f" {title}")
        print('='*80)
    else:
        print('-'*80)

def print_section_header(title):
    """Print a section header"""
    print(f"\n🔹 {title}")
    print('─' * 60)

def print_subsection_header(title):
    """Print a subsection header"""
    print(f"\n  📋 {title}")
    print('  ' + '·' * 50)

countries = ['India', 'MENA', 'LATAM', 'Africa', 'Europe', 'APAC']
inputs_template = {
    'ai_volume': 10000,
    'advanced_volume': 5000,
    'basic_marketing_volume': 2000,
    'basic_utility_volume': 1000,
    'bfsi_tier': 'Tier 2',
    'personalize_load': 'Standard',
    'human_agents': '50+',
    'ai_module': 'Yes',
    'smart_cpaas': 'Yes',
    'increased_tps': '250',
    'voice_notes_price': 'Yes',
    'voice_notes_model': 'google_stt_v2',
    'voice_notes_volume': 1000,  # Simulate 1000 minutes of voice notes usage
}

print_separator("🚀 ENHANCED PRICING SIMULATION - DETAILED BREAKDOWN")
print(f"📊 Test Configuration:")
print(f"   • AI Messages: {inputs_template['ai_volume']:,}")
print(f"   • Advanced Messages: {inputs_template['advanced_volume']:,}")
print(f"   • Basic Marketing Messages: {inputs_template['basic_marketing_volume']:,}")
print(f"   • Basic Utility Messages: {inputs_template['basic_utility_volume']:,}")
print(f"   • Voice Notes: {inputs_template['voice_notes_price']} ({inputs_template['voice_notes_model']}) - {inputs_template['voice_notes_volume']:,} minutes")
print(f"   • BFSI Tier: {inputs_template['bfsi_tier']}")
print(f"   • Personalize Load: {inputs_template['personalize_load']}")
print(f"   • Human Agents: {inputs_template['human_agents']}")
print(f"   • AI Module: {inputs_template['ai_module']}")
print(f"   • Smart CPaaS: {inputs_template['smart_cpaas']}")
print(f"   • Increased TPS: {inputs_template['increased_tps']}")

print_section_header("🤖 AI Model Pricing Check (India example)")
base_ai_markup_india = get_suggested_price('India', 'ai', inputs_template['ai_volume'])
ai_components_india = compute_ai_price_components(
    country='India',
    model='ACE Agent Premium (gpt-4o)',
    complexity='complex',
    tier_ai_markup=base_ai_markup_india,
)
print(f"  Baseline AI markup from tiers (India): {base_ai_markup_india:.4f}")
print(f"  Model-driven AI final price (India, ACE Agent Premium gpt-4o, complex): {ai_components_india['final_price']:.4f}")
print(f"  Implied AI markup used in calculator: {ai_components_india['markup']:.4f}")

print_section_header("🌍 AI Model Pricing Matrix (All Countries & Models)")
for country in countries:
    # Map to pricing key used in AI_AGENT_PRICING
    pricing_key = 'India' if country == 'India' else 'International'
    base_ai_markup = get_suggested_price(country, 'ai', inputs_template['ai_volume'])
    print_subsection_header(f"{country} (pricing_key={pricing_key}) — baseline AI markup: {base_ai_markup:.4f}")
    models = AI_AGENT_PRICING.get(pricing_key, {})
    for model_name, complexities in models.items():
        for complexity, _ in complexities.items():
            comps = compute_ai_price_components(
                country=country,
                model=model_name,
                complexity=complexity,
                tier_ai_markup=base_ai_markup,
            )
            tag = "MODEL_USED" if comps['used_model'] else "TIER_ONLY"
            print(
                f"    [{tag}] {model_name} / {complexity:<7} -> "
                f"final_price={comps['final_price']:.6f}, markup={comps['markup']:.6f}"
            )

# Summary table
print_separator("📈 SUMMARY TABLE")
print('| Country | Currency | Platform Fee | AI Price | Adv Price | Mkt Price | Utl Price | Voice Notes Rate | Total (Vol) | Total (Bundle) |')
print('|---------|----------|--------------|----------|-----------|-----------|-----------|------------------|-------------|----------------|')

results = {}
for country in countries:
    inputs = dict(inputs_template)
    pf, _ = calculate_platform_fee(
        country,
        inputs['bfsi_tier'],
        inputs['personalize_load'],
        inputs['human_agents'],
        inputs['ai_module'],
        inputs['smart_cpaas'],
        inputs['increased_tps']
    )
    inputs['country'] = country
    inputs['platform_fee'] = pf
    sim = calculate_pricing_simulation(inputs)
    c = COUNTRY_CURRENCY.get(country, '$')
    v = sim['volume_route']
    b = sim['bundle_route']
    results[country] = sim
    
    # Get final prices for display
    meta_costs = meta_costs_table.get(country, meta_costs_table['APAC'])
    total_volume = inputs['ai_volume'] + inputs['advanced_volume'] + inputs['basic_marketing_volume'] + inputs['basic_utility_volume']
    
    ai_markup = get_committed_amount_rate_for_volume(country, 'ai', total_volume)
    adv_markup = get_committed_amount_rate_for_volume(country, 'advanced', total_volume)
    mkt_markup = get_committed_amount_rate_for_volume(country, 'basic_marketing', total_volume)
    utl_markup = get_committed_amount_rate_for_volume(country, 'basic_utility', total_volume)
    
    ai_final = meta_costs['ai'] + ai_markup
    adv_final = meta_costs['advanced'] + adv_markup
    mkt_final = meta_costs['marketing'] + mkt_markup
    utl_final = meta_costs['utility'] + utl_markup
    
    # Get voice notes rate
    voice_notes_rate = get_voice_notes_price(country, inputs['voice_notes_model'])
    
    print(f"| {country} | {c} | {pf:,.0f} | {ai_final:.4f} | {adv_final:.4f} | {mkt_final:.4f} | {utl_final:.4f} | {voice_notes_rate:.4f} | {v['total']:,.0f} | {b['total']:,.0f} |")

# Detailed breakdown for each country
for country in countries:
    print_separator(f"🌍 {country} ({COUNTRY_CURRENCY.get(country, '$')})")
    
    inputs = dict(inputs_template)
    inputs['country'] = country
    pf, pf_breakdown = calculate_platform_fee(
        country,
        inputs['bfsi_tier'],
        inputs['personalize_load'],
        inputs['human_agents'],
        inputs['ai_module'],
        inputs['smart_cpaas'],
        inputs['increased_tps']
    )
    inputs['platform_fee'] = pf
    sim = calculate_pricing_simulation(inputs)
    
    # Get detailed pricing information
    meta_costs = meta_costs_table.get(country, meta_costs_table['APAC'])
    total_volume = inputs['ai_volume'] + inputs['advanced_volume'] + inputs['basic_marketing_volume'] + inputs['basic_utility_volume']
    
    # Get Gupshup markup rates
    ai_markup = get_committed_amount_rate_for_volume(country, 'ai', total_volume)
    adv_markup = get_committed_amount_rate_for_volume(country, 'advanced', total_volume)
    mkt_markup = get_committed_amount_rate_for_volume(country, 'basic_marketing', total_volume)
    utl_markup = get_committed_amount_rate_for_volume(country, 'basic_utility', total_volume)
    
    # Calculate final prices
    ai_final = meta_costs['ai'] + ai_markup
    adv_final = meta_costs['advanced'] + adv_markup
    mkt_final = meta_costs['marketing'] + mkt_markup
    utl_final = meta_costs['utility'] + utl_markup
    
    # Get suggested prices
    suggested_ai = get_suggested_price(country, 'ai', inputs['ai_volume'])
    suggested_adv = get_suggested_price(country, 'advanced', inputs['advanced_volume'])
    suggested_mkt = get_suggested_price(country, 'basic_marketing', inputs['basic_marketing_volume'])
    suggested_utl = get_suggested_price(country, 'basic_utility', inputs['basic_utility_volume'])
    
    print_section_header("💰 PRICING BREAKDOWN")
    
    print_subsection_header("Meta Costs + Gupshup Markup = Final Price")
    print(f"  🤖 AI Messages:")
    print(f"     Meta Cost: {meta_costs['ai']:.4f} + Gupshup Markup: {ai_markup:.4f} = Final Price: {ai_final:.4f}")
    print(f"     Volume: {inputs['ai_volume']:,} × {ai_final:.4f} = {format_currency(inputs['ai_volume'] * ai_final, COUNTRY_CURRENCY.get(country, '$'))}")
    
    print(f"  📱 Advanced Messages:")
    print(f"     Meta Cost: {meta_costs['advanced']:.4f} + Gupshup Markup: {adv_markup:.4f} = Final Price: {adv_final:.4f}")
    print(f"     Volume: {inputs['advanced_volume']:,} × {adv_final:.4f} = {format_currency(inputs['advanced_volume'] * adv_final, COUNTRY_CURRENCY.get(country, '$'))}")
    
    print(f"  📢 Basic Marketing Messages:")
    print(f"     Meta Cost: {meta_costs['marketing']:.4f} + Gupshup Markup: {mkt_markup:.4f} = Final Price: {mkt_final:.4f}")
    print(f"     Volume: {inputs['basic_marketing_volume']:,} × {mkt_final:.4f} = {format_currency(inputs['basic_marketing_volume'] * mkt_final, COUNTRY_CURRENCY.get(country, '$'))}")
    
    print(f"  🔧 Basic Utility Messages:")
    print(f"     Meta Cost: {meta_costs['utility']:.4f} + Gupshup Markup: {utl_markup:.4f} = Final Price: {utl_final:.4f}")
    print(f"     Volume: {inputs['basic_utility_volume']:,} × {utl_final:.4f} = {format_currency(inputs['basic_utility_volume'] * utl_final, COUNTRY_CURRENCY.get(country, '$'))}")
    
    # Voice Notes pricing
    voice_notes_rate = get_voice_notes_price(country, inputs['voice_notes_model'])
    voice_notes_volume = inputs.get('voice_notes_volume', 0)
    voice_notes_revenue = voice_notes_volume * voice_notes_rate if voice_notes_volume > 0 else 0
    print(f"  🎤 Voice Notes ({inputs['voice_notes_model']}):")
    print(f"     Rate per minute: {voice_notes_rate:.4f}")
    if voice_notes_volume > 0:
        print(f"     Volume: {voice_notes_volume:,} minutes × {voice_notes_rate:.4f} = {format_currency(voice_notes_revenue, COUNTRY_CURRENCY.get(country, '$'))}")
    else:
        print(f"     Note: Billed on actuals (no volume input required)")
    
    print_section_header("📊 PRICING OPTIONS & SUGGESTED RATES")
    
    print_subsection_header("Suggested Prices (Rate Card)")
    print(f"  AI Messages: {suggested_ai:.4f}")
    print(f"  Advanced Messages: {suggested_adv:.4f}")
    print(f"  Basic Marketing Messages: {suggested_mkt:.4f}")
    print(f"  Basic Utility Messages: {suggested_utl:.4f}")
    print(f"  Voice Notes: {voice_notes_rate:.4f} per minute")
    
    print_subsection_header("Committed Amount Slabs")
    slabs = committed_amount_slabs.get(country, committed_amount_slabs['APAC'])
    print(f"  Available Slabs for {country}:")
    for i, (lower, upper, rates) in enumerate(slabs[:5]):  # Show first 5 slabs
        print(f"    Slab {i+1}: {lower:,} - {upper:,} | AI: {rates['ai']:.4f} | Adv: {rates['advanced']:.4f} | Mkt: {rates['basic_marketing']:.4f} | Utl: {rates['basic_utility']:.4f}")
    if len(slabs) > 5:
        print(f"    ... and {len(slabs) - 5} more slabs")
    
    print_section_header("💼 PLATFORM FEE BREAKDOWN")
    print(f"  Total Platform Fee: {format_currency(pf, COUNTRY_CURRENCY.get(country, '$'))}")
    if pf_breakdown and isinstance(pf_breakdown, dict):
        print(f"  Breakdown:")
        for key, value in pf_breakdown.items():
            if isinstance(value, (int, float)) and value > 0:
                print(f"    {key}: {format_currency(value, COUNTRY_CURRENCY.get(country, '$'))}")
    else:
        print(f"  Platform Fee Details: {pf_breakdown}")
    
    print_section_header("📈 VOLUME ROUTE CALCULATION")
    v = sim['volume_route']
    print(f"  AI Cost: {format_currency(v['ai_cost'], COUNTRY_CURRENCY.get(country, '$'))}")
    print(f"  Advanced Cost: {format_currency(v['adv_cost'], COUNTRY_CURRENCY.get(country, '$'))}")
    print(f"  Marketing Cost: {format_currency(v['mkt_cost'], COUNTRY_CURRENCY.get(country, '$'))}")
    print(f"  Utility Cost: {format_currency(v['utl_cost'], COUNTRY_CURRENCY.get(country, '$'))}")
    print(f"  Platform Fee: {format_currency(v['platform_fee'], COUNTRY_CURRENCY.get(country, '$'))}")
    print(f"  ──────────────────────────────────────────────────────────────")
    print(f"  TOTAL: {format_currency(v['total'], COUNTRY_CURRENCY.get(country, '$'))}")
    
    print_section_header("📦 BUNDLE ROUTE CALCULATION")
    b = sim['bundle_route']
    print(f"  Required Committed Amount: {format_currency(b['required_committed_amount'], COUNTRY_CURRENCY.get(country, '$'))}")
    print(f"  Nearest Bundle: {format_currency(b['nearest_bundle'], COUNTRY_CURRENCY.get(country, '$'))}")
    print(f"  Platform Fee: {format_currency(b['platform_fee'], COUNTRY_CURRENCY.get(country, '$'))}")
    print(f"  ──────────────────────────────────────────────────────────────")
    print(f"  TOTAL: {format_currency(b['total'], COUNTRY_CURRENCY.get(country, '$'))}")
    
    # Show detailed pricing calculation using the main calculate_pricing function
    print_section_header("🔍 DETAILED PRICING ANALYSIS")
    try:
        # For simulation, calculate voice notes revenue with actual volume
        voice_notes_volume = inputs.get('voice_notes_volume', 0)
        voice_notes_revenue = voice_notes_volume * voice_notes_rate if voice_notes_volume > 0 else 0
        
        detailed_pricing = calculate_pricing(
            country=country,
            ai_volume=inputs['ai_volume'],
            advanced_volume=inputs['advanced_volume'],
            basic_marketing_volume=inputs['basic_marketing_volume'],
            basic_utility_volume=inputs['basic_utility_volume'],
            platform_fee=pf,
            ai_price=suggested_ai,
            advanced_price=suggested_adv,
            basic_marketing_price=suggested_mkt,
            basic_utility_price=suggested_utl,
            voice_notes_rate=voice_notes_rate
        )
        
        # Override voice notes revenue for simulation
        if voice_notes_revenue > 0:
            for item in detailed_pricing.get('line_items', []):
                if item['label'] == 'Voice Notes':
                    item['volume'] = voice_notes_volume
                    item['revenue'] = voice_notes_revenue
                    item['suggested_revenue'] = voice_notes_revenue
                    break
            
            # Update total revenue
            detailed_pricing['revenue'] = detailed_pricing.get('revenue', 0) + voice_notes_revenue
            detailed_pricing['suggested_revenue'] = detailed_pricing.get('suggested_revenue', 0) + voice_notes_revenue
        
        print_subsection_header("Line Items Breakdown")
        for item in detailed_pricing.get('line_items', []):
            print(f"  {item['label']}:")
            print(f"    Volume: {item['volume']:,}")
            print(f"    Suggested Price: {item['suggested_price']:.4f}")
            print(f"    Meta Cost: {item['meta_cost']:.4f}")
            print(f"    Final Price: {item['final_price']:.4f}")
            print(f"    Revenue: {format_currency(item['revenue'], COUNTRY_CURRENCY.get(country, '$'))}")
        
        print_subsection_header("Financial Summary")
        print(f"  Total Revenue: {format_currency(detailed_pricing.get('revenue', 0), COUNTRY_CURRENCY.get(country, '$'))}")
        print(f"  Total Costs: {format_currency(detailed_pricing.get('total_costs', 0), COUNTRY_CURRENCY.get(country, '$'))}")
        print(f"  Platform Fee: {format_currency(detailed_pricing.get('platform_fee', 0), COUNTRY_CURRENCY.get(country, '$'))}")
        print(f"  Margin: {detailed_pricing.get('margin_percentage', 0):.2f}%")
        
    except Exception as e:
        print(f"  Error in detailed pricing calculation: {e}")

print_separator("✅ SIMULATION COMPLETE")
print("📝 Summary: This simulation shows the complete pricing breakdown including:")
print("   • Meta costs (fixed costs from Meta)")
print("   • Gupshup markup (profit margin)")
print("   • Final prices (Meta cost + Gupshup markup)")
print("   • Platform fee breakdown")
print("   • Volume route vs Bundle route comparison")
print("   • Committed amount slabs and pricing options")
print("   • Detailed financial analysis with margins")
