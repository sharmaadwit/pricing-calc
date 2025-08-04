# pricing_config.py

# =============================================================================
# PRICING CONFIGURATION FOR MESSAGING CALCULATOR
# =============================================================================
# This file contains all pricing configurations used by the messaging calculator.
# There are two main calculation routes:
# 1. VOLUMES ROUTE: User enters specific message volumes, uses price_tiers
# 2. COMMITTED AMOUNT/BUNDLE ROUTE: User enters committed amount, uses committed_amount_slabs
# =============================================================================

# =============================================================================
# VOLUMES ROUTE CONFIGURATIONS
# =============================================================================
# Used when user enters specific message volumes (ai_volume, advanced_volume, etc.)
# These tiers determine suggested prices and overage prices for the volumes route.
# Format: (min_volume, max_volume, price_per_message)
# =============================================================================

# --- Volume-based Price Tiers by Country and Message Type (VOLUMES ROUTE) ---
# USAGE: Used in volumes route for suggested prices and tier-based overage prices
# FUNCTIONS: get_suggested_price(), get_next_tier_price() in calculator.py
# --- Meta Costs by Country and Message Type (SHARED) ---
# USAGE: Used in both volumes route and committed amount route for final price calculation
# PURPOSE: Meta's charges for each message type, added to Gupshup markup to get final price
# FUNCTIONS: calculate_pricing() in calculator.py
meta_costs_table = {
    'India': {'marketing': 0.7846, 'utility': 0.1150, 'ai': 0.30, 'advanced': 0},
    'MENA': {'marketing': 0.0384, 'utility': 0.0157, 'ai': 0.0035, 'advanced': 0},
    'LATAM': {'marketing': 0.0625, 'utility': 0.0068, 'ai': 0.0035, 'advanced': 0},
    'Africa': {'marketing': 0.0379, 'utility': 0.0076, 'ai': 0.0035, 'advanced': 0},
    'Europe': {'marketing': 0.1597, 'utility': 0.05, 'ai': 0.0035, 'advanced': 0},
    'Rest of the World': {'marketing': 0.0592, 'utility': 0.0171, 'ai': 0.0035, 'advanced': 0},
}

# =============================================================================
# COMMITTED AMOUNT/BUNDLE ROUTE CONFIGURATIONS
# =============================================================================
# Used when user enters a committed amount instead of specific volumes
# These determine the per-message rates based on the committed amount slab
# =============================================================================

# --- Committed Amount Slabs by Country (COMMITTED AMOUNT/BUNDLE ROUTE) ---
# USAGE: Used in committed amount/bundle route to determine per-message rates
# PURPOSE: Defines Gupshup markup rates for each message type based on committed amount
# FORMAT: (min_amount, max_amount, {'marketing': rate, 'utility': rate, 'advanced': rate, 'ai': rate})
# FUNCTIONS: get_committed_amount_rates() in calculator.py
# OVERAGE CALCULATION: Base rate × 1.2 (20% markup) - see app.py line 458
committed_amount_slabs = {
    'India': [
        (0, 50000,    {'basic_marketing': 0.15, 'basic_utility': 0.03, 'advanced': 0.50, 'ai': 1.00}),
        (50000, 150000, {'basic_marketing': 0.12, 'basic_utility': 0.024, 'advanced': 0.45, 'ai': 0.95}),
        (150000, 200000, {'basic_marketing': 0.10, 'basic_utility': 0.019, 'advanced': 0.40, 'ai': 0.90}),
        (200000, 250000, {'basic_marketing': 0.08, 'basic_utility': 0.015, 'advanced': 0.35, 'ai': 0.85}),
        (250000, 500000, {'basic_marketing': 0.06, 'basic_utility': 0.012, 'advanced': 0.30, 'ai': 0.80}),
        (500000, 750000, {'basic_marketing': 0.05, 'basic_utility': 0.010, 'advanced': 0.25, 'ai': 0.75}),
        (750000, 1000000, {'basic_marketing': 0.04, 'basic_utility': 0.008, 'advanced': 0.20, 'ai': 0.70}),
        (1000000, 2000000, {'basic_marketing': 0.03, 'basic_utility': 0.006, 'advanced': 0.15, 'ai': 0.65}),
    ],
    'MENA': [
        (0, 500,    {'basic_marketing': 0.0080, 'basic_utility': 0.0080, 'advanced': 0.0160, 'ai': 0.0267}),
        (500, 1000,  {'basic_marketing': 0.0080, 'basic_utility': 0.0080, 'advanced': 0.0160, 'ai': 0.0267}),
        (1000, 1500, {'basic_marketing': 0.0080, 'basic_utility': 0.0080, 'advanced': 0.0160, 'ai': 0.0267}),
        (1500, 2500, {'basic_marketing': 0.0054, 'basic_utility': 0.0054, 'advanced': 0.0108, 'ai': 0.0203}),
        (2500, 5000, {'basic_marketing': 0.0054, 'basic_utility': 0.0054, 'advanced': 0.0108, 'ai': 0.0203}),
        (5000, 7500, {'basic_marketing': 0.0054, 'basic_utility': 0.0054, 'advanced': 0.0108, 'ai': 0.0203}),
        (7500, 10000, {'basic_marketing': 0.0041, 'basic_utility': 0.0041, 'advanced': 0.0082, 'ai': 0.0154}),
        (10000, 15000, {'basic_marketing': 0.0041, 'basic_utility': 0.0041, 'advanced': 0.0082, 'ai': 0.0154}),
    ],
    'LATAM': [
        (0, 500,    {'basic_marketing': 0.0075, 'basic_utility': 0.0015, 'advanced': 0.0250, 'ai': 0.0500}),
        (500, 1000, {'basic_marketing': 0.0060, 'basic_utility': 0.0012, 'advanced': 0.0225, 'ai': 0.0475}),
        (1000, 1500, {'basic_marketing': 0.0048, 'basic_utility': 0.0010, 'advanced': 0.0200, 'ai': 0.0450}),
        (1500, 2500, {'basic_marketing': 0.0038, 'basic_utility': 0.0008, 'advanced': 0.0175, 'ai': 0.0425}),
        (2500, 5000, {'basic_marketing': 0.0031, 'basic_utility': 0.0006, 'advanced': 0.0150, 'ai': 0.0400}),
        (5000, 7500, {'basic_marketing': 0.0025, 'basic_utility': 0.0005, 'advanced': 0.0125, 'ai': 0.0375}),
        (7500, 10000, {'basic_marketing': 0.0020, 'basic_utility': 0.0004, 'advanced': 0.0100, 'ai': 0.0350}),
        (10000, 15000, {'basic_marketing': 0.0016, 'basic_utility': 0.0003, 'advanced': 0.0075, 'ai': 0.0325}),
    ],
    'Africa': [
        (0, 500,    {'basic_marketing': 0.0030, 'basic_utility': 0.0030, 'advanced': 0.0060, 'ai': 0.0150}),
        (500, 1000, {'basic_marketing': 0.0030, 'basic_utility': 0.0030, 'advanced': 0.0060, 'ai': 0.0150}),
        (1000, 1500, {'basic_marketing': 0.0030, 'basic_utility': 0.0030, 'advanced': 0.0060, 'ai': 0.0150}),
        (1500, 2500, {'basic_marketing': 0.0030, 'basic_utility': 0.0030, 'advanced': 0.0060, 'ai': 0.0150}),
        (2500, 5000, {'basic_marketing': 0.0030, 'basic_utility': 0.0030, 'advanced': 0.0060, 'ai': 0.0150}),
        (5000, 7500, {'basic_marketing': 0.0030, 'basic_utility': 0.0030, 'advanced': 0.0060, 'ai': 0.0150}),
        (7500, 10000, {'basic_marketing': 0.0030, 'basic_utility': 0.0030, 'advanced': 0.0060, 'ai': 0.0150}),
        (10000, 15000, {'basic_marketing': 0.0030, 'basic_utility': 0.0030, 'advanced': 0.0060, 'ai': 0.0150}),
    ],
    'Europe': [
        (0, 500,    {'basic_marketing': 0.0080, 'basic_utility': 0.0080, 'advanced': 0.0160, 'ai': 0.0267}),
        (500, 1000,  {'basic_marketing': 0.0080, 'basic_utility': 0.0080, 'advanced': 0.0160, 'ai': 0.0267}),
        (1000, 1500, {'basic_marketing': 0.0080, 'basic_utility': 0.0080, 'advanced': 0.0160, 'ai': 0.0267}),
        (1500, 2500, {'basic_marketing': 0.0054, 'basic_utility': 0.0054, 'advanced': 0.0108, 'ai': 0.0203}),
        (2500, 5000, {'basic_marketing': 0.0054, 'basic_utility': 0.0054, 'advanced': 0.0108, 'ai': 0.0203}),
        (5000, 7500, {'basic_marketing': 0.0054, 'basic_utility': 0.0054, 'advanced': 0.0108, 'ai': 0.0203}),
        (7500, 10000, {'basic_marketing': 0.0041, 'basic_utility': 0.0041, 'advanced': 0.0082, 'ai': 0.0154}),
        (10000, 15000, {'basic_marketing': 0.0041, 'basic_utility': 0.0041, 'advanced': 0.0082, 'ai': 0.0154}),
    ],
    'Rest of the World': [
        (0, 500,    {'basic_marketing': 0.0080, 'basic_utility': 0.0080, 'advanced': 0.0160, 'ai': 0.0267}),
        (500, 1000,  {'basic_marketing': 0.0080, 'basic_utility': 0.0080, 'advanced': 0.0160, 'ai': 0.0267}),
        (1000, 1500, {'basic_marketing': 0.0080, 'basic_utility': 0.0080, 'advanced': 0.0160, 'ai': 0.0267}),
        (1500, 2500, {'basic_marketing': 0.0054, 'basic_utility': 0.0054, 'advanced': 0.0108, 'ai': 0.0203}),
        (2500, 5000, {'basic_marketing': 0.0054, 'basic_utility': 0.0054, 'advanced': 0.0108, 'ai': 0.0203}),
        (5000, 7500, {'basic_marketing': 0.0054, 'basic_utility': 0.0054, 'advanced': 0.0108, 'ai': 0.0203}),
        (7500, 10000, {'basic_marketing': 0.0041, 'basic_utility': 0.0041, 'advanced': 0.0082, 'ai': 0.0154}),
        (10000, 15000, {'basic_marketing': 0.0041, 'basic_utility': 0.0041, 'advanced': 0.0082, 'ai': 0.0154}),
    ],
}

# --- Messaging Bundle Markup Rates by Country (COMMITTED AMOUNT/BUNDLE ROUTE) ---
# USAGE: Alternative format for committed amount route (currently not used, kept for reference)
# PURPOSE: Same data as committed_amount_slabs but in different format
# NOTE: This configuration is currently commented out as committed_amount_slabs is used instead
# bundle_markup_rates = {
#     'India': [
#         {'min': 0, 'max': 50000, 'basic_marketing': 0.15, 'basic_utility': 0.03, 'advanced': 0.50, 'ai': 1.00},
#         # ... rest of the data
#     ],
#     # ... rest of countries
# }

# =============================================================================
# DEVELOPMENT COST CONFIGURATIONS (Used by both routes)
# =============================================================================

# --- Country-specific Manday Rates (Bot/UI and Custom/AI) ---
# USAGE: Used in both routes for development cost calculations
# PURPOSE: Defines hourly/daily rates for development work by country and activity type
# FUNCTIONS: calculate_total_manday_cost() in calculator.py
COUNTRY_MANDAY_RATES = {
    'India': {
        'currency': 'INR',
        'bot_ui': 20000,  # Updated
        'custom_ai': 30000,  # Updated
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
        'currency': 'USD',  # USD for MENA
        'bot_ui': 300,      # Updated to 300 USD
        'custom_ai': 500,   # Updated to 500 USD
    },
    'Africa': {
        'currency': 'USD',
        'bot_ui': 300,
        'custom_ai': 420,
    },
    'Rest of the World': {
        'currency': 'USD',
        'bot_ui': 300,
        'custom_ai': 420,
    },
    'Europe': {
        'currency': 'USD',  # Not in table, fallback to Rest of the World?
        'bot_ui': 300,
        'custom_ai': 420,
    },
}

# --- Activity to Manday Mapping (applies to all countries) ---
# USAGE: Used in both routes for development cost calculations
# PURPOSE: Maps development activities to manday requirements
# FUNCTIONS: calculate_total_mandays() in calculator.py
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

# =============================================================================
# UI/UX CONFIGURATIONS (Used by both routes)
# =============================================================================

# --- Country to currency symbol mapping ---
# USAGE: Used in both routes for display purposes
# PURPOSE: Maps countries to their currency symbols for UI display
COUNTRY_CURRENCY = {
    'India': '₹',
    'MENA': '$',  # USD for MENA
    'LATAM': '$',
    'Africa': '$',
    'Europe': '$',  # Use USD for Europe
    'Rest of the World': '$',
}

PLATFORM_PRICING_GUIDANCE = {
    'India': {
        'minimum': 100000,
        'BFSI_Tier_1': 250000,
        'BFSI_Tier_2': 500000,
        'BFSI_Tier_3': 800000,
        'TPS_250': 50000,
        'TPS_1000': 100000,
        'Personalize_Standard': 50000,
        'Personalize_Pro': 100000,
        'Agent_Assist_20_50': 50000,
        'Agent_Assist_50_100': 75000,
        'Agent_Assist_100_plus': 100000,
        'AI_Module': 50000,
        'Smart_CPaaS': 25000,
    },
    'MENA': {
        'minimum': 1650,
        'BFSI_Tier_1': 4150,
        'BFSI_Tier_2': 8350,
        'BFSI_Tier_3': 13350,
        'TPS_250': 850,
        'TPS_1000': 1650,
        'Personalize_Standard': 850,
        'Personalize_Pro': 1650,
        'Agent_Assist_20_50': 850,
        'Agent_Assist_50_100': 1250,
        'Agent_Assist_100_plus': 1650,
        'AI_Module': 850,
        'Smart_CPaaS': 400,
    },
    'LATAM': {
        'minimum': 1650,
        'BFSI_Tier_1': 4150,
        'BFSI_Tier_2': 8350,
        'BFSI_Tier_3': 13350,
        'TPS_250': 850,
        'TPS_1000': 1650,
        'Personalize_Standard': 850,
        'Personalize_Pro': 1650,
        'Agent_Assist_20_50': 850,
        'Agent_Assist_50_100': 1250,
        'Agent_Assist_100_plus': 1650,
        'AI_Module': 850,
        'Smart_CPaaS': 400,
    },
    'Africa': {
        'minimum': 850,
        'BFSI_Tier_1': 2100,
        'BFSI_Tier_2': 4150,
        'BFSI_Tier_3': 6650,
        'TPS_250': 400,
        'TPS_1000': 850,
        'Personalize_Standard': 400,
        'Personalize_Pro': 850,
        'Agent_Assist_20_50': 400,
        'Agent_Assist_50_100': 600,
        'Agent_Assist_100_plus': 850,
        'AI_Module': 400,
        'Smart_CPaaS': 200,
    },
    'Europe': {
        'minimum': 2100,
        'BFSI_Tier_1': 5250,
        'BFSI_Tier_2': 10450,
        'BFSI_Tier_3': 16700,
        'TPS_250': 1050,
        'TPS_1000': 2100,
        'Personalize_Standard': 1050,
        'Personalize_Pro': 2100,
        'Agent_Assist_20_50': 1050,
        'Agent_Assist_50_100': 1550,
        'Agent_Assist_100_plus': 2100,
        'AI_Module': 1050,
        'Smart_CPaaS': 500,
    },
    'Rest of the World': {
        'minimum': 1650,
        'BFSI_Tier_1': 4150,
        'BFSI_Tier_2': 8350,
        'BFSI_Tier_3': 13350,
        'TPS_250': 850,
        'TPS_1000': 1650,
        'Personalize_Standard': 850,
        'Personalize_Pro': 1650,
        'Agent_Assist_20_50': 850,
        'Agent_Assist_50_100': 1250,
        'Agent_Assist_100_plus': 1650,
        'AI_Module': 850,
        'Smart_CPaaS': 400,
    },
} 