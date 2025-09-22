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
    'APAC': {'marketing': 0.0592, 'utility': 0.0171, 'ai': 0.0035, 'advanced': 0},
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
# NOTE: APAC pricing replaces "Rest of the World" category
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
        (0, 500,    {'basic_marketing': 0.0080, 'basic_utility': 0.0080, 'advanced': 0.0160, 'ai': 0.0267}),
        (500, 1000, {'basic_marketing': 0.0080, 'basic_utility': 0.0080, 'advanced': 0.0160, 'ai': 0.0267}),
        (1000, 1500, {'basic_marketing': 0.0080, 'basic_utility': 0.0080, 'advanced': 0.0160, 'ai': 0.0267}),
        (1500, 2500, {'basic_marketing': 0.0054, 'basic_utility': 0.0054, 'advanced': 0.0108, 'ai': 0.0203}),
        (2500, 5000, {'basic_marketing': 0.0054, 'basic_utility': 0.0054, 'advanced': 0.0108, 'ai': 0.0203}),
        (5000, 7500, {'basic_marketing': 0.0054, 'basic_utility': 0.0054, 'advanced': 0.0108, 'ai': 0.0203}),
        (7500, 10000, {'basic_marketing': 0.0041, 'basic_utility': 0.0041, 'advanced': 0.0082, 'ai': 0.0154}),
        (10000, 15000, {'basic_marketing': 0.0041, 'basic_utility': 0.0041, 'advanced': 0.0082, 'ai': 0.0154}),
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
    'APAC': [
        (0, 500,    {'basic_marketing': 0.0021, 'basic_utility': 0.0013, 'advanced': 0.0070, 'ai': 0.0105}),
        (500, 1000,  {'basic_marketing': 0.0021, 'basic_utility': 0.0013, 'advanced': 0.0070, 'ai': 0.0105}),
        (1000, 1500, {'basic_marketing': 0.0021, 'basic_utility': 0.0013, 'advanced': 0.0070, 'ai': 0.0105}),
        (1500, 2500, {'basic_marketing': 0.0021, 'basic_utility': 0.0013, 'advanced': 0.0070, 'ai': 0.0105}),
        (2500, 5000, {'basic_marketing': 0.0021, 'basic_utility': 0.0013, 'advanced': 0.0070, 'ai': 0.0105}),
        (5000, 7500, {'basic_marketing': 0.0021, 'basic_utility': 0.0013, 'advanced': 0.0070, 'ai': 0.0105}),
        (7500, 10000, {'basic_marketing': 0.0021, 'basic_utility': 0.0013, 'advanced': 0.0070, 'ai': 0.0105}),
        (10000, 15000, {'basic_marketing': 0.0021, 'basic_utility': 0.0013, 'advanced': 0.0070, 'ai': 0.0105}),
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
    'APAC': {
        'currency': 'USD',
        'bot_ui': 300,
        'custom_ai': 420,
    },
    'Europe': {
        'currency': 'USD',  # Not in table, fallback to APAC
        'bot_ui': 300,
        'custom_ai': 420,
    },
    'Rest of the World': {
        'currency': 'USD',  # For historical data compatibility
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
    "security_audit": 2,
    "performance_optimization": 1.5,
    "integration_setup": 2,
    "data_migration": 3,
    "custom_component": 0.5,
    "webhook": 0.25,
    "ai_workspace_support": 2,
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
    'APAC': '$',
}

# Voice Notes Pricing Configuration (INR per minute)
# USD conversion rate: 1 USD = 83 INR (approximate)
VOICE_NOTES_PRICING = {
    'India': {
        'deepgram_nova3': 0.58,      # INR per minute
        'google_stt_v2': 2.16,       # INR per minute
        'azure_stt': 2.25,           # INR per minute
        'google_tts_neural2': 1.49,  # INR per minute
        'google_tts_wavenet': 0.37,  # INR per minute
        'cartesia_pro': 4.67,        # INR per minute
    },
    'MENA': {
        'deepgram_nova3': 0.007,     # USD per minute (0.58 INR / 83)
        'google_stt_v2': 0.026,      # USD per minute (2.16 INR / 83)
        'azure_stt': 0.027,          # USD per minute (2.25 INR / 83)
        'google_tts_neural2': 0.018, # USD per minute (1.49 INR / 83)
        'google_tts_wavenet': 0.004, # USD per minute (0.37 INR / 83)
        'cartesia_pro': 0.056,       # USD per minute (4.67 INR / 83)
    },
    'LATAM': {
        'deepgram_nova3': 0.007,     # USD per minute
        'google_stt_v2': 0.026,      # USD per minute
        'azure_stt': 0.027,          # USD per minute
        'google_tts_neural2': 0.018, # USD per minute
        'google_tts_wavenet': 0.004, # USD per minute
        'cartesia_pro': 0.056,       # USD per minute
    },
    'Africa': {
        'deepgram_nova3': 0.007,     # USD per minute
        'google_stt_v2': 0.026,      # USD per minute
        'azure_stt': 0.027,          # USD per minute
        'google_tts_neural2': 0.018, # USD per minute
        'google_tts_wavenet': 0.004, # USD per minute
        'cartesia_pro': 0.056,       # USD per minute
    },
    'Europe': {
        'deepgram_nova3': 0.007,     # USD per minute
        'google_stt_v2': 0.026,      # USD per minute
        'azure_stt': 0.027,          # USD per minute
        'google_tts_neural2': 0.018, # USD per minute
        'google_tts_wavenet': 0.004, # USD per minute
        'cartesia_pro': 0.056,       # USD per minute
    },
    'APAC': {
        'deepgram_nova3': 0.007,     # USD per minute
        'google_stt_v2': 0.026,      # USD per minute
        'azure_stt': 0.027,          # USD per minute
        'google_tts_neural2': 0.018, # USD per minute
        'google_tts_wavenet': 0.004, # USD per minute
        'cartesia_pro': 0.056,       # USD per minute
    },
}

def get_voice_notes_price(country, model):
    """
    Get voice notes price based on country and selected model.
    
    Args:
        country: Country name (e.g., 'India', 'MENA', 'LATAM', etc.)
        model: Voice notes model (e.g., 'deepgram_nova3', 'google_stt_v2', etc.)
    
    Returns:
        float: Price per minute for the selected model in the given country
    """
    if not model or model == '':
        return 0.0
    
    country_pricing = VOICE_NOTES_PRICING.get(country, VOICE_NOTES_PRICING.get('APAC', {}))
    return country_pricing.get(model, 0.0)

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
    'Europe': {
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
    'APAC': {
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
} 