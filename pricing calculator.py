# fee_calculator.py

# --- Utility Functions ---
def get_numeric_input(prompt):
    """
    Prompts the user for numeric input and handles potential errors.
    Continues to prompt until a valid number is entered.
    """
    while True:
        try:
            value = float(input(prompt))
            if value < 0:
                print("Value cannot be negative. Please enter a positive number or zero.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a valid number.")


def get_country():
    """
    Prompts the user to select a country from the supported list.
    Returns the country name as a string.
    """
    countries = {
        '1': 'India',
        '2': 'MENA',
        '3': 'LATAM',
        '4': 'Africa',
        '5': 'Europe',
        '6': 'Rest of the World',
    }
    print("Select the country:")
    for k, v in countries.items():
        print(f"{k}. {v}")
    while True:
        choice = input("Enter the number for your country: ").strip()
        if choice in countries:
            return countries[choice]
        else:
            print("Invalid choice. Please enter a valid number.")


def get_fee_input(prompt):
    """
    Prompts the user for a markup fee and ensures it's a valid number.
    """
    while True:
        user_input = input(f"{prompt} ").strip()
        try:
            value = float(user_input)
            if value < 0:
                print("Value cannot be negative. Please enter a positive number or zero.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a valid number.")

# --- Price Tiers by Country and Message Type ---
# These are used to suggest default markup fees based on country and volume.
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


def suggest_price(country, msg_type, volume, currency=None):
    """
    Suggests a markup fee for a given message type, country, and volume based on the price_tiers table.
    Returns None if no suggestion is available.
    """
    if country in price_tiers and msg_type in price_tiers[country]:
        for lower, upper, price in price_tiers[country][msg_type]:
            if lower < volume <= upper:
                return price
    return None


def perform_calculations_and_display(data, suggested_fees=None):
    """
    Calculates all financial metrics and displays the formatted results using the updated formulae from the Excel logic.
    Also shows margin based on suggested price vs user-chosen price if suggested_fees is provided.
    """
    # Unpack data dictionary for easier access
    platform_fee = data['platform_fee']
    adv_fee = data['fees']['advanced']
    ai_fee = data['fees']['ai']
    basic_marketing_fee = data['fees']['basic_marketing']
    basic_utility_fee = data['fees']['basic_utility']
    adv_vol = data['volumes']['advanced']
    ai_vol = data['volumes']['ai']
    basic_marketing_vol = data['volumes']['basic_marketing']
    basic_utility_vol = data['volumes']['basic_utility']
    marketing_price = data['meta_costs']['marketing']
    utility_price = data['meta_costs']['utility']
    ai_unit_cost = data['meta_costs']['ai']
    currency_symbol = data['currency_symbol']

    # --- Revenue (CC MRR) ---
    ai_final_price = ai_fee + ai_unit_cost
    adv_final_price = adv_fee + ai_unit_cost
    basic_marketing_final_price = basic_marketing_fee + marketing_price
    basic_utility_final_price = basic_utility_fee + utility_price

    revenue = (
        platform_fee
        + (adv_final_price * adv_vol)
        + (ai_final_price * ai_vol)
        + (basic_marketing_final_price * basic_marketing_vol)
        + (basic_utility_final_price * basic_utility_vol)
    )

    # --- Suggested Revenue ---
    if suggested_fees is not None:
        ai_final_price_s = suggested_fees['ai'] + ai_unit_cost
        adv_final_price_s = suggested_fees['advanced'] + ai_unit_cost
        basic_marketing_final_price_s = suggested_fees['basic_marketing'] + marketing_price
        basic_utility_final_price_s = suggested_fees['basic_utility'] + utility_price
        suggested_revenue = (
            platform_fee
            + (adv_final_price_s * adv_vol)
            + (ai_final_price_s * ai_vol)
            + (basic_marketing_final_price_s * basic_marketing_vol)
            + (basic_utility_final_price_s * basic_utility_vol)
        )
    else:
        suggested_revenue = None

    # --- Channel Cost (Advanced + Basic) ---
    # Advanced Marketing/Utility volumes are set to 0 as per current business logic.
    adv_marketing_vol = 0.0
    adv_utility_vol = 0.0
    channel_cost = (
        (marketing_price * adv_marketing_vol)
        + (utility_price * adv_utility_vol)
        + (basic_marketing_vol * marketing_price)
        + (basic_utility_vol * utility_price)
    )

    # --- AI Costs ---
    ai_costs = ai_unit_cost * ai_vol

    # --- Total Costs ---
    # Platform infra cost is 0 in this model.
    total_costs = 0 + channel_cost + ai_costs

    # --- Margin (with META discount) ---
    margin_denom = revenue + channel_cost
    if margin_denom > 0:
        margin = (revenue + channel_cost - total_costs) / margin_denom
        margin_percentage = margin * 100
    else:
        margin = 0
        margin_percentage = 0

    # --- If suggested_fees provided, calculate suggested margin ---
    if suggested_fees is not None:
        suggested_margin_denom = suggested_revenue + channel_cost
        if suggested_margin_denom > 0:
            suggested_margin = (suggested_revenue + channel_cost - total_costs) / suggested_margin_denom
            suggested_margin_percentage = suggested_margin * 100
        else:
            suggested_margin = 0
            suggested_margin_percentage = 0
    else:
        suggested_margin = None
        suggested_margin_percentage = None

    # --- Display Results ---
    print("\n\n" + "=" * 50)
    print("      Generated Monthly Fee Structure")
    print("=" * 50)

    print(f"\n{'FEE COMPONENTS (REVENUE)':<35} {'AMOUNT':>14}")
    print("-" * 50)
    print(f"{'AI Message Final Price':<35} {currency_symbol}{ai_final_price:>13.2f}")
    print(f"{'Advanced Message Final Price':<35} {currency_symbol}{adv_final_price:>13.2f}")
    print(f"{'Basic Marketing Message Final Price':<35} {currency_symbol}{basic_marketing_final_price:>13.2f}")
    print(f"{'Basic Utility/Authentication Final Price':<35} {currency_symbol}{basic_utility_final_price:>13.2f}")
    print(f"{'AI Message Fees':<35} {currency_symbol}{ai_final_price * ai_vol:>13.2f}")
    print(f"{'Advanced Message Fees':<35} {currency_symbol}{adv_final_price * adv_vol:>13.2f}")
    print(f"{'Basic Marketing Message Fees':<35} {currency_symbol}{basic_marketing_final_price * basic_marketing_vol:>13.2f}")
    print(f"{'Basic Utility/Authentication Fees':<35} {currency_symbol}{basic_utility_final_price * basic_utility_vol:>13.2f}")
    print(f"{'Fixed Platform Fee':<35} {currency_symbol}{platform_fee:>13.2f}")
    print("-" * 50)
    print(f"{'CC MRR - Revenue':<35} {currency_symbol}{revenue:>13.2f}")
    if suggested_revenue is not None:
        print(f"{'Suggested Revenue':<35} {currency_symbol}{suggested_revenue:>13.2f}")
    print(f"{'CHANNEL COSTS':<35} {currency_symbol}{channel_cost:>13.2f}")
    print(f"{'AI COSTS':<35} {currency_symbol}{ai_costs:>13.2f}")
    print(f"{'TOTAL COSTS':<35} {currency_symbol}{total_costs:>13.2f}")
    print("=" * 50)

    print(f"\n{'MARGIN ANALYSIS':<35} {'AMOUNT':>14}")
    print("-" * 50)
    print(f"{'Margin (Amount) (User Chosen)':<35} {currency_symbol}{(revenue + channel_cost - total_costs):>13.2f}")
    print(f"{'Margin (Percentage) (User Chosen)':<35} {f'{margin_percentage:.2f}%':>14}")
    if suggested_margin is not None:
        print(f"{'Margin (Amount) (Suggested)':<35} {currency_symbol}{(suggested_revenue + channel_cost - total_costs):>13.2f}")
        print(f"{'Margin (Percentage) (Suggested)':<35} {f'{suggested_margin_percentage:.2f}%':>14}")
    print("-" * 50)


def calculate_platform_fee(country, bfsi_tier, personalize_load, human_agents, ai_module):
    if country == 'India':
        min_fee = 100000
    elif country in ['Africa', 'Rest of the World']:
        min_fee = 500
    else:
        min_fee = 1000
    fee = min_fee
    # BFSI tier
    if bfsi_tier == 'Tier 1':
        if country == 'India': fee += 250000
        elif country == 'Africa': fee += 500
        else: fee += 1500
    elif bfsi_tier == 'Tier 2':
        if country == 'India': fee += 500000
        elif country == 'Africa': fee += 1000
        else: fee += 3000
    elif bfsi_tier == 'Tier 3':
        if country == 'India': fee += 800000
        elif country == 'Africa': fee += 1500
        else: fee += 5000
    # Personalize load
    if personalize_load == 'Standard':
        if country == 'India': fee += 50000
        elif country == 'Africa': fee += 250
        else: fee += 500
    elif personalize_load == 'Advanced':
        if country == 'India': fee += 100000
        elif country == 'Africa': fee += 500
        else: fee += 1000
    # Human agents
    if human_agents == '20+':
        if country == 'India': fee += 50000
        elif country == 'Africa': fee += 250
        elif country in ['LATAM', 'Europe']: fee += 1000
        else: fee += 500
    elif human_agents == '50+':
        if country == 'India': fee += 75000
        elif country == 'Africa': fee += 400
        elif country in ['LATAM', 'Europe']: fee += 1200
        else: fee += 700
    elif human_agents == '100+':
        if country == 'India': fee += 100000
        elif country == 'Africa': fee += 500
        elif country in ['LATAM', 'Europe']: fee += 1500
        else: fee += 1000
    # AI Module Yes/No
    if ai_module == 'Yes':
        if country == 'India': fee += 50000
        elif country == 'Africa': fee += 250
        elif country in ['LATAM', 'Europe']: fee += 1000
        else: fee += 500
    return fee


def main_calculator():
    """
    Main function to orchestrate the calculator's workflow using the updated formulae.
    Handles country selection, cost/fee setup, user input, and the what-if analysis loop.
    """
    print("-" * 50)
    print("Monthly Fee and Gross Margin Calculator")
    print("-" * 50)
    
    country = get_country()
    print(f"\nCountry selected: {country}\n")

    # --- Set currency and conversion rates ---
    # (You can update conversion rates as needed)
    if country == 'India':
        currency_symbol = '₹'
        currency = 'INR'
        usd_to_aed = 3.67  # Placeholder
        advanced_cost_usd = 0.0036  # ₹0.3 to USD (assuming 1 USD = ₹83)
        ai_cost_usd = 0.0036  # ₹0.3 to USD
    elif country == 'MENA':
        currency_symbol = 'د.إ'
        currency = 'AED'
        usd_to_aed = 3.67
        advanced_cost_usd = 0.0036
        ai_cost_usd = 0.0036
    else:
        currency_symbol = '$'
        currency = 'USD'
        usd_to_aed = 3.67
        advanced_cost_usd = 0.0036
        ai_cost_usd = 0.0036

    # --- Meta/RCS List Prices (costs) ---
    # These are the internal costs for each country and message type.
    if country == 'India':
        meta_costs = {
            'marketing': 0.78,
            'utility': 0.12,
            'ai': 0.30,
        }
    elif country == 'MENA':
        meta_costs = {
            'marketing': 0.0455 * usd_to_aed,  # USD to AED
            'utility': 0.0115 * usd_to_aed,
            'ai': ai_cost_usd * usd_to_aed,
        }
    elif country == 'LATAM':
        meta_costs = {
            'marketing': 0.0625,
            'utility': 0.0080,
            'ai': ai_cost_usd,
        }
    elif country == 'Africa':
        meta_costs = {
            'marketing': 0.0379,
            'utility': 0.0076,
            'ai': ai_cost_usd,
        }
    elif country == 'Europe':
        meta_costs = {
            'marketing': 0.0529,
            'utility': 0.0220,
            'ai': ai_cost_usd,
        }
    elif country == 'Rest of the World':
        meta_costs = {
            'marketing': 0.0604,
            'utility': 0.0077,
            'ai': ai_cost_usd,
        }
    else:
        meta_costs = {
            'marketing': 0.0,
            'utility': 0.0,
            'ai': 0.0,
        }

    print(f"Currency set to {currency} ({currency_symbol})\n")
    print("Please provide the following details for the client.\n")

    # --- Platform Fee Inputs ---
    print("--- Platform Fee Options ---")
    print("BFSI Tier options: NA, Tier 1, Tier 2, Tier 3")
    bfsi_tier = input("Select BFSI Tier: ").strip()
    if bfsi_tier not in ['NA', 'Tier 1', 'Tier 2', 'Tier 3']:
        bfsi_tier = 'NA'
    print("Personalize Load options: NA, Standard, Advanced")
    personalize_load = input("Select Personalize Load: ").strip()
    if personalize_load not in ['NA', 'Standard', 'Advanced']:
        personalize_load = 'NA'
    print("Number of Human Agents (AI Module) options: NA, 20+, 50+, 100+")
    human_agents = input("Select Human Agents: ").strip()
    if human_agents not in ['NA', '20+', '50+', '100+']:
        human_agents = 'NA'
    print("AI Module options: NA, Yes, No")
    ai_module = input("AI Module (Yes/No): ").strip()
    if ai_module not in ['NA', 'Yes', 'No']:
        ai_module = 'NA'
    platform_fee = calculate_platform_fee(country, bfsi_tier, personalize_load, human_agents, ai_module)
    print(f"Calculated Platform Fee: {platform_fee}")
    user_platform_fee = input(f"Enter platform fee to use (press Enter to accept {platform_fee}): ").strip()
    if user_platform_fee == '':
        platform_fee = platform_fee
    else:
        try:
            platform_fee = float(user_platform_fee)
        except:
            platform_fee = platform_fee

    # --- Gather Initial Client Requirements and Volumes ---
    print("--- Message Volumes (Monthly) ---")
    volumes = {
        'ai': float(get_numeric_input("Enter the total volume of AI messages: ")),
        'advanced': float(get_numeric_input("Enter the total volume of Advanced messages: ")),
        'basic_marketing': float(get_numeric_input("Enter the total volume of Basic Marketing messages: ")),
        'basic_utility': float(get_numeric_input("Enter the total volume of Basic Utility/Authentication messages: "))
    }

    # --- Gather Initial Markup Fees ---
    # For each message type, suggest a price based on country/volume, but allow user override.
    print(f"\n--- Markup Fees (to be added on top of {currency} cost) ---")
    fees = {'ai': 0.0, 'advanced': 0.0, 'basic_marketing': 0.0, 'basic_utility': 0.0}
    for msg_type, label in [
        ('ai', 'AI message'),
        ('advanced', 'Advanced message'),
        ('basic_marketing', 'Basic Marketing message'),
        ('basic_utility', 'Basic Utility/Authentication message'),
    ]:
        vol = volumes[msg_type]
        if vol > 0:
            suggested = suggest_price(country, msg_type, vol, currency)
            if suggested is not None:
                print(f"Suggested markup fee for {label} (volume {int(vol)}): {currency_symbol}{suggested}")
            else:
                print(f"No suggested price for {label} (volume {int(vol)}). Please enter manually.")
            user_input = input(f"Enter the markup fee for a {label} (in {currency_symbol}) [Press Enter to accept suggested]: ").strip()
            if user_input == '' and suggested is not None:
                fees[msg_type] = suggested
            else:
                while True:
                    try:
                        value = float(user_input) if user_input != '' else suggested
                        if value is None or value < 0:
                            print("Value cannot be negative. Please enter a positive number or zero.")
                            user_input = input(f"Enter the markup fee for a {label} (in {currency_symbol}): ").strip()
                            continue
                        fees[msg_type] = value
                        break
                    except ValueError:
                        print("Invalid input. Please enter a valid number.")
                        user_input = input(f"Enter the markup fee for a {label} (in {currency_symbol}): ").strip()

    # --- Store all data in a single dictionary ---
    master_data = {
        'meta_costs': meta_costs,
        'volumes': volumes,
        'fees': fees,
        'platform_fee': platform_fee,
        'currency_symbol': currency_symbol
    }

    # --- Build suggested_fees dict for margin comparison ---
    suggested_fees = {'ai': 0.0, 'advanced': 0.0, 'basic_marketing': 0.0, 'basic_utility': 0.0}
    for msg_type in ['ai', 'advanced', 'basic_marketing', 'basic_utility']:
        vol = volumes[msg_type]
        suggested = suggest_price(country, msg_type, vol, currency)
        suggested_fees[msg_type] = suggested if suggested is not None else 0.0
    # --- Initial Calculation and Display ---
    perform_calculations_and_display(master_data, suggested_fees)

    # --- "What-If" Analysis Loop ---
    while True:
        change = input(f"\nWould you like to change volumes, markup fees, or both? (v/p/b/n): ").strip().lower()
        
        if change == 'n':
            break

        if change in ['v', 'b']:
            print("\n--- Update Message Volumes (Monthly) ---")
            master_data['volumes']['ai'] = float(get_numeric_input("Enter the total volume of AI messages: "))
            master_data['volumes']['advanced'] = float(get_numeric_input("Enter the total volume of Advanced messages: "))
            master_data['volumes']['basic_marketing'] = float(get_numeric_input("Enter the total volume of Basic Marketing messages: "))
            master_data['volumes']['basic_utility'] = float(get_numeric_input("Enter the total volume of Basic Utility/Authentication messages: "))
        
        if change in ['p', 'b']:
            print(f"\n--- Update Markup Fees ---")
            master_data['fees'] = {'ai': 0.0, 'advanced': 0.0, 'basic_marketing': 0.0, 'basic_utility': 0.0}
            for msg_type, label in [
                ('ai', 'AI message'),
                ('advanced', 'Advanced message'),
                ('basic_marketing', 'Basic Marketing message'),
                ('basic_utility', 'Basic Utility/Authentication message'),
            ]:
                vol = master_data['volumes'][msg_type]
                if vol > 0:
                    suggested = suggest_price(country, msg_type, vol, currency)
                    if suggested is not None:
                        print(f"Suggested markup fee for {label} (volume {int(vol)}): {currency_symbol}{suggested}")
                    else:
                        print(f"No suggested price for {label} (volume {int(vol)}). Please enter manually.")
                    user_input = input(f"Enter the markup fee for a {label} (in {currency_symbol}) [Press Enter to accept suggested]: ").strip()
                    if user_input == '' and suggested is not None:
                        master_data['fees'][msg_type] = suggested
                    else:
                        while True:
                            try:
                                value = float(user_input) if user_input != '' else suggested
                                if value is None or value < 0:
                                    print("Value cannot be negative. Please enter a positive number or zero.")
                                    user_input = input(f"Enter the markup fee for a {label} (in {currency_symbol}): ").strip()
                                    continue
                                master_data['fees'][msg_type] = value
                                break
                            except ValueError:
                                print("Invalid input. Please enter a valid number.")
                                user_input = input(f"Enter the markup fee for a {label} (in {currency_symbol}): ").strip()
        
        if change not in ['v', 'p', 'b', 'n']:
            print("Invalid choice. Please enter 'v' (volumes), 'p' (prices), 'b' (both), or 'n' (no).")
            continue
        
        # Recalculate and display with the new data
        # Update suggested_fees for new volumes
        for msg_type in ['ai', 'advanced', 'basic_marketing', 'basic_utility']:
            vol = master_data['volumes'][msg_type]
            suggested = suggest_price(country, msg_type, vol, currency)
            suggested_fees[msg_type] = suggested if suggested is not None else 0.0
        perform_calculations_and_display(master_data, suggested_fees)


if __name__ == "__main__":
    main_calculator()
