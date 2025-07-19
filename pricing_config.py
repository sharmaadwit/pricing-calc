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
price_tiers = {
    'India': {
        'ai': [(0, 1000, 0.50), (1001, 5000, 0.45), (5001, 10000, 0.40), (10001, 50000, 0.35), (50001, 100000, 0.30), (100001, 500000, 0.25), (500001, 1000000, 0.20), (1000001, float('inf'), 0.15)],
        'advanced': [(0, 1000, 0.25), (1001, 5000, 0.22), (5001, 10000, 0.20), (10001, 50000, 0.18), (50001, 100000, 0.15), (100001, 500000, 0.12), (500001, 1000000, 0.10), (1000001, float('inf'), 0.08)],
        'basic_marketing': [(0, 1000, 0.10), (1001, 5000, 0.09), (5001, 10000, 0.08), (10001, 50000, 0.07), (50001, 100000, 0.06), (100001, 500000, 0.05), (500001, 1000000, 0.04), (1000001, float('inf'), 0.03)],
        'basic_utility': [(0, 1000, 0.025), (1001, 5000, 0.022), (5001, 10000, 0.020), (10001, 50000, 0.018), (50001, 100000, 0.015), (100001, 500000, 0.012), (500001, 1000000, 0.010), (1000001, float('inf'), 0.008)],
    },
    'MENA': {
        'ai': [(0, 1000, 0.0167), (1001, 1500, 0.0158), (1501, 2500, 0.0150), (2501, 3500, 0.0142), (3501, 5000, 0.0133), (5001, 7500, 0.0125), (7501, 10000, 0.0117), (10001, 15000, 0.0108)],
        'advanced': [(0, 1000, 0.0083), (1001, 1500, 0.0075), (1501, 2500, 0.0067), (2501, 3500, 0.0058), (3501, 5000, 0.0050), (5001, 7500, 0.0042), (7501, 10000, 0.0033), (10001, 15000, 0.0025)],
        'basic_marketing': [(0, 1000, 0.0033), (1001, 1500, 0.0030), (1501, 2500, 0.0025), (2501, 3500, 0.0020), (3501, 5000, 0.0017), (5001, 7500, 0.0013), (7501, 10000, 0.0008), (10001, 15000, 0.0005)],
        'basic_utility': [(0, 1000, 0.0008), (1001, 1500, 0.0008), (1501, 2500, 0.0007), (2501, 3500, 0.0006), (3501, 5000, 0.0005), (5001, 7500, 0.0004), (7501, 10000, 0.0003), (10001, 15000, 0.0003)],
    },
    'LATAM': {
        'ai': [(0, 1000, 0.0167), (1001, 1500, 0.0158), (1501, 2500, 0.0150), (2501, 3500, 0.0142), (3501, 5000, 0.0133), (5001, 7500, 0.0125), (7501, 10000, 0.0117), (10001, 15000, 0.0108)],
        'advanced': [(0, 1000, 0.0083), (1001, 1500, 0.0075), (1501, 2500, 0.0067), (2501, 3500, 0.0058), (3501, 5000, 0.0050), (5001, 7500, 0.0042), (7501, 10000, 0.0033), (10001, 15000, 0.0025)],
        'basic_marketing': [(0, 1000, 0.0033), (1001, 1500, 0.0030), (1501, 2500, 0.0025), (2501, 3500, 0.0020), (3501, 5000, 0.0017), (5001, 7500, 0.0013), (7501, 10000, 0.0008), (10001, 15000, 0.0005)],
        'basic_utility': [(0, 1000, 0.0008), (1001, 1500, 0.0008), (1501, 2500, 0.0007), (2501, 3500, 0.0006), (3501, 5000, 0.0005), (5001, 7500, 0.0004), (7501, 10000, 0.0003), (10001, 15000, 0.0003)],
    },
    'Africa': {
        'ai': [(0, 1000, 0.0083), (1001, 1500, 0.0079), (1501, 2500, 0.0075), (2501, 3500, 0.0071), (3501, 5000, 0.0067), (5001, 7500, 0.0062), (7501, 10000, 0.0058), (10001, 15000, 0.0054)],
        'advanced': [(0, 1000, 0.0042), (1001, 1500, 0.0037), (1501, 2500, 0.0033), (2501, 3500, 0.0029), (3501, 5000, 0.0025), (5001, 7500, 0.0021), (7501, 10000, 0.0017), (10001, 15000, 0.0012)],
        'basic_marketing': [(0, 1000, 0.0017), (1001, 1500, 0.0015), (1501, 2500, 0.0012), (2501, 3500, 0.0010), (3501, 5000, 0.0008), (5001, 7500, 0.0007), (7501, 10000, 0.0004), (10001, 15000, 0.0002)],
        'basic_utility': [(0, 1000, 0.0004), (1001, 1500, 0.0004), (1501, 2500, 0.0003), (2501, 3500, 0.0003), (3501, 5000, 0.0002), (5001, 7500, 0.0002), (7501, 10000, 0.0002), (10001, 15000, 0.0001)],
    },
    'Europe': {
        'ai': [(0, 1000, 0.0209), (1001, 1500, 0.0199), (1501, 2500, 0.0188), (2501, 3500, 0.0178), (3501, 5000, 0.0167), (5001, 7500, 0.0157), (7501, 10000, 0.0146), (10001, 15000, 0.0136)],
        'advanced': [(0, 1000, 0.0105), (1001, 1500, 0.0094), (1501, 2500, 0.0084), (2501, 3500, 0.0073), (3501, 5000, 0.0063), (5001, 7500, 0.0052), (7501, 10000, 0.0042), (10001, 15000, 0.0031)],
        'basic_marketing': [(0, 1000, 0.0042), (1001, 1500, 0.0038), (1501, 2500, 0.0031), (2501, 3500, 0.0025), (3501, 5000, 0.0021), (5001, 7500, 0.0017), (7501, 10000, 0.0010), (10001, 15000, 0.0006)],
        'basic_utility': [(0, 1000, 0.0010), (1001, 1500, 0.0009), (1501, 2500, 0.0008), (2501, 3500, 0.0007), (3501, 5000, 0.0006), (5001, 7500, 0.0005), (7501, 10000, 0.0004), (10001, 15000, 0.0003)],
    },
    'Rest of the World': {
        'ai': [(0, 1000, 0.0167), (1001, 1500, 0.0158), (1501, 2500, 0.0150), (2501, 3500, 0.0142), (3501, 5000, 0.0133), (5001, 7500, 0.0125), (7501, 10000, 0.0117), (10001, 15000, 0.0108)],
        'advanced': [(0, 1000, 0.0083), (1001, 1500, 0.0075), (1501, 2500, 0.0067), (2501, 3500, 0.0058), (3501, 5000, 0.0050), (5001, 7500, 0.0042), (7501, 10000, 0.0033), (10001, 15000, 0.0025)],
        'basic_marketing': [(0, 1000, 0.0033), (1001, 1500, 0.0030), (1501, 2500, 0.0025), (2501, 3500, 0.0020), (3501, 5000, 0.0017), (5001, 7500, 0.0013), (7501, 10000, 0.0008), (10001, 15000, 0.0005)],
        'basic_utility': [(0, 1000, 0.0008), (1001, 1500, 0.0008), (1501, 2500, 0.0007), (2501, 3500, 0.0006), (3501, 5000, 0.0005), (5001, 7500, 0.0004), (7501, 10000, 0.0003), (10001, 15000, 0.0003)],
    },
}

# =============================================================================
# SHARED CONFIGURATIONS (Used by both routes)
# =============================================================================

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
        (0, 50000,    {'marketing': 0.15, 'utility': 0.03, 'advanced': 0.50, 'ai': 1.00}),
        (50000, 150000, {'marketing': 0.12, 'utility': 0.024, 'advanced': 0.45, 'ai': 0.95}),
        (150000, 200000, {'marketing': 0.10, 'utility': 0.019, 'advanced': 0.40, 'ai': 0.90}),
        (200000, 250000, {'marketing': 0.08, 'utility': 0.015, 'advanced': 0.35, 'ai': 0.85}),
        (250000, 500000, {'marketing': 0.06, 'utility': 0.012, 'advanced': 0.30, 'ai': 0.80}),
        (500000, 750000, {'marketing': 0.05, 'utility': 0.010, 'advanced': 0.25, 'ai': 0.75}),
        (750000, 1000000, {'marketing': 0.04, 'utility': 0.008, 'advanced': 0.20, 'ai': 0.70}),
        (1000000, 2000000, {'marketing': 0.03, 'utility': 0.006, 'advanced': 0.15, 'ai': 0.65}),
    ],
    'MENA': [
        (0, 500,    {'marketing': 0.0075, 'utility': 0.0015, 'advanced': 0.0250, 'ai': 0.0500}),
        (500, 1000, {'marketing': 0.0060, 'utility': 0.0012, 'advanced': 0.0225, 'ai': 0.0475}),
        (1000, 1500, {'marketing': 0.0048, 'utility': 0.0010, 'advanced': 0.0200, 'ai': 0.0450}),
        (1500, 2500, {'marketing': 0.0038, 'utility': 0.0008, 'advanced': 0.0175, 'ai': 0.0425}),
        (2500, 5000, {'marketing': 0.0031, 'utility': 0.0006, 'advanced': 0.0150, 'ai': 0.0400}),
        (5000, 7500, {'marketing': 0.0025, 'utility': 0.0005, 'advanced': 0.0125, 'ai': 0.0375}),
        (7500, 10000, {'marketing': 0.0020, 'utility': 0.0004, 'advanced': 0.0100, 'ai': 0.0350}),
        (10000, 15000, {'marketing': 0.0016, 'utility': 0.0003, 'advanced': 0.0075, 'ai': 0.0325}),
    ],
    'LATAM': [
        (0, 500,    {'marketing': 0.0075, 'utility': 0.0015, 'advanced': 0.0250, 'ai': 0.0500}),
        (500, 1000, {'marketing': 0.0060, 'utility': 0.0012, 'advanced': 0.0225, 'ai': 0.0475}),
        (1000, 1500, {'marketing': 0.0048, 'utility': 0.0010, 'advanced': 0.0200, 'ai': 0.0450}),
        (1500, 2500, {'marketing': 0.0038, 'utility': 0.0008, 'advanced': 0.0175, 'ai': 0.0425}),
        (2500, 5000, {'marketing': 0.0031, 'utility': 0.0006, 'advanced': 0.0150, 'ai': 0.0400}),
        (5000, 7500, {'marketing': 0.0025, 'utility': 0.0005, 'advanced': 0.0125, 'ai': 0.0375}),
        (7500, 10000, {'marketing': 0.0020, 'utility': 0.0004, 'advanced': 0.0100, 'ai': 0.0350}),
        (10000, 15000, {'marketing': 0.0016, 'utility': 0.0003, 'advanced': 0.0075, 'ai': 0.0325}),
    ],
    'Africa': [
        (0, 500,    {'marketing': 0.0037, 'utility': 0.0007, 'advanced': 0.0125, 'ai': 0.0250}),
        (500, 1000, {'marketing': 0.0030, 'utility': 0.0006, 'advanced': 0.0112, 'ai': 0.0237}),
        (1000, 1500, {'marketing': 0.0024, 'utility': 0.0005, 'advanced': 0.0100, 'ai': 0.0225}),
        (1500, 2500, {'marketing': 0.0019, 'utility': 0.0004, 'advanced': 0.0087, 'ai': 0.0212}),
        (2500, 5000, {'marketing': 0.0015, 'utility': 0.0003, 'advanced': 0.0075, 'ai': 0.0200}),
        (5000, 7500, {'marketing': 0.0012, 'utility': 0.0002, 'advanced': 0.0050, 'ai': 0.0175}),
        (7500, 10000, {'marketing': 0.0010, 'utility': 0.0002, 'advanced': 0.0037, 'ai': 0.0162}),
        (10000, 15000, {'marketing': 0.0008, 'utility': 0.0002, 'advanced': 0.0037, 'ai': 0.0162}),
    ],
    'Europe': [
        (0, 500,    {'marketing': 0.0094, 'utility': 0.0019, 'advanced': 0.0314, 'ai': 0.0627}),
        (500, 1000, {'marketing': 0.0075, 'utility': 0.0015, 'advanced': 0.0282, 'ai': 0.0596}),
        (1000, 1500, {'marketing': 0.0060, 'utility': 0.0012, 'advanced': 0.0251, 'ai': 0.0564}),
        (1500, 2500, {'marketing': 0.0048, 'utility': 0.0010, 'advanced': 0.0219, 'ai': 0.0533}),
        (2500, 5000, {'marketing': 0.0039, 'utility': 0.0008, 'advanced': 0.0188, 'ai': 0.0502}),
        (5000, 7500, {'marketing': 0.0031, 'utility': 0.0006, 'advanced': 0.0157, 'ai': 0.0470}),
        (7500, 10000, {'marketing': 0.0025, 'utility': 0.0005, 'advanced': 0.0125, 'ai': 0.0439}),
        (10000, 15000, {'marketing': 0.0020, 'utility': 0.0004, 'advanced': 0.0094, 'ai': 0.0408}),
    ],
    'Rest of the World': [
        (0, 500,    {'marketing': 0.0050, 'utility': 0.0010, 'advanced': 0.0167, 'ai': 0.0333}),
        (500, 1000, {'marketing': 0.0040, 'utility': 0.0008, 'advanced': 0.0150, 'ai': 0.0317}),
        (1000, 1500, {'marketing': 0.0032, 'utility': 0.0006, 'advanced': 0.0133, 'ai': 0.0300}),
        (1500, 2500, {'marketing': 0.0026, 'utility': 0.0005, 'advanced': 0.0117, 'ai': 0.0283}),
        (2500, 5000, {'marketing': 0.0020, 'utility': 0.0004, 'advanced': 0.0100, 'ai': 0.0267}),
        (5000, 7500, {'marketing': 0.0016, 'utility': 0.0003, 'advanced': 0.0083, 'ai': 0.0250}),
        (7500, 10000, {'marketing': 0.0013, 'utility': 0.0003, 'advanced': 0.0067, 'ai': 0.0233}),
        (10000, 15000, {'marketing': 0.0010, 'utility': 0.0002, 'advanced': 0.0050, 'ai': 0.0217}),
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