from app import calculate_pricing_simulation, calculate_platform_fee
from pricing_config import COUNTRY_CURRENCY

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
}

print('| Country | Currency | Platform Fee | AI Price (Vol) | Adv Price (Vol) | Total (Vol) | AI Price (Bundle) | Adv Price (Bundle) | Committed Amount | Total (Bundle) |')
print('|---------|----------|--------------|----------------|-----------------|-------------|-------------------|--------------------|------------------|----------------|')
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
    print(f"| {country} | {c} | {pf:,.0f} | {v['ai_price']:.4f} | {v['adv_price']:.4f} | {v['total']:,.0f} | {b['ai_price']:.4f} | {b['adv_price']:.4f} | {b['committed_amount']:,.0f} | {b['total']:,.0f} |")

print('\n--- Detailed Breakdown by Country ---\n')
for country in countries:
    print(f'## {country}')
    sim = results[country]
    print('### Volume Route')
    for k, v in sim['volume_route'].items():
        print(f'  {k}: {v}')
    print('### Bundle Route')
    for k, v in sim['bundle_route'].items():
        print(f'  {k}: {v}')
    print('\n') 