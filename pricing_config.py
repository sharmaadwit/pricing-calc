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
    # NOTE: For AI, we now use LLM prices from AI_AGENT_PRICING and treat the
    # entire AI per-message price as Gupshup markup (no separate Meta AI cost).
    # Hence, all 'ai' meta costs are set to 0.0 below.
    'India': {'marketing': 0.7846, 'utility': 0.1150, 'ai': 0.0, 'advanced': 0},
    'MENA': {'marketing': 0.0384, 'utility': 0.0157, 'ai': 0.0, 'advanced': 0},
    'LATAM': {'marketing': 0.0625, 'utility': 0.0068, 'ai': 0.0, 'advanced': 0},
    'Africa': {'marketing': 0.0379, 'utility': 0.0076, 'ai': 0.0, 'advanced': 0},
    'Europe': {'marketing': 0.1597, 'utility': 0.05, 'ai': 0.0, 'advanced': 0},
    'APAC': {'marketing': 0.0592, 'utility': 0.0171, 'ai': 0.0, 'advanced': 0},
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

# --- User profile & defaults configuration ---
#
# Lightweight, code-based mapping so we can infer country/region defaults from
# email (or email domain). This keeps v1 simple and developer-maintained while
# making it easy to later move to a DB + admin UI.
#
# Keys can be:
#   - Full email ID: 'alice@example.com'
#   - Email domain: '@example.com'
# Values are dicts with at least:
#   - 'country': e.g. 'India'
#   - 'region': e.g. 'North'
USER_DEFAULTS = {
    # Explicitly mapped internal users
    'adwit.sharma@gupshup.io': {'country': 'India', 'region': 'North'},
    'ankit.kanwara@gupshup.io': {'country': 'India', 'region': 'South'},
    'gargi.upadhyay@gupshup.io': {'country': 'MENA', 'region': 'KSA'},
    'kathyayani.nayak@gupshup.io': {'country': 'India', 'region': 'South'},
    'mauricio.martins@gupshup.io': {'country': 'LATAM', 'region': 'Brazil'},
    'mridul.kumawat@gupshup.io': {'country': 'India', 'region': 'West'},
    'nikhil.sharma@knowlarity.com': {'country': 'India', 'region': 'North'},
    'nikhil.sharma@gupshup.io': {'country': 'India', 'region': 'North'},
    'purusottam.singh@gupshup.io': {'country': 'India', 'region': 'West'},
    'siddharth.singh@gupshup.io': {'country': 'MENA', 'region': 'UAE'},
    'yashas.reddy@gupshup.io': {'country': 'Africa', 'region': 'South Africa'},
}


def _normalize_email(email: str) -> str:
    """Normalize email for lookup – lowercase and strip spaces."""
    if not email:
        return ''
    return email.strip().lower()


def get_default_location_for_email(email: str):
    """
    Infer default (country, region) for a given email.

    Resolution order:
      1. Exact email match in USER_DEFAULTS
      2. Domain match (e.g. '@gupshup.io')
      3. Fallback: None (caller responsible for using existing defaults)

    Returns:
        tuple | None: (country, region) or None if no mapping found.
    """
    normalized = _normalize_email(email)
    if not normalized:
        return None

    # 1) Exact match
    exact = USER_DEFAULTS.get(normalized)
    if exact and exact.get('country'):
        return exact.get('country'), exact.get('region', '')

    # 2) Domain match
    if '@' in normalized:
        domain = '@' + normalized.split('@', 1)[1]
        dom_cfg = USER_DEFAULTS.get(domain)
        if dom_cfg and dom_cfg.get('country'):
            return dom_cfg.get('country'), dom_cfg.get('region', '')

    return None

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

# =============================================================================
# VOICE CHANNEL PRICING CONFIGURATION (India-first)
# =============================================================================

# Voice Bot Development Effort (Mandays)
VOICE_DEV_EFFORT = {
    'journey': 3,
    'api_integration': 1,
    'additional_language_multiplier': 0.30,
    'agent_handover_pstn_knowlarity': 1,
    'agent_handover_pstn_other': 5,
    'whatsapp_voice_knowlarity': 1,
    'whatsapp_voice_other': 5,
    'whatsapp_voice_setup_fee_other': 50000,
}

# Voice Platform Fees (INR)
VOICE_PLATFORM_FEES = {
    'voice_ai': 150000,
    'knowlarity_platform': 25000,
    'virtual_number': 500,
}

# PSTN Calling Charges (INR per minute)
PSTN_CALLING_CHARGES = {
    'inbound_ai': {
        'bundled': 4.5,
        'overage': 6.0,
    },
    'outbound_ai': {
        'bundled': 4.8,
        'overage': 6.0,
    },
    'manual_c2c': {
        'bundled': 0.55,
        'overage': 0.6,
    },
}

# WhatsApp Voice Calling Charges (INR per minute) - Volume-based tiers
WHATSAPP_VOICE_CHARGES = {
    'India': [
        {
            'min_minutes': 0,
            'max_minutes': 50000,
            'outbound': 0.49,
            'inbound': 0.06,
            'meta_rate': 0.3885,
            'gupshup_margin_pct': 25,
        },
        {
            'min_minutes': 50001,
            'max_minutes': 250000,
            'outbound': 0.35,
            'inbound': 0.05,
            'meta_rate': 0.2785,
            'gupshup_margin_pct': 25,
        },
        {
            'min_minutes': 250001,
            'max_minutes': 1000000,
            'outbound': 0.22,
            'inbound': 0.04,
            'meta_rate': 0.1759,
            'gupshup_margin_pct': 25,
        },
        {
            'min_minutes': 1000001,
            'max_minutes': 2500000,
            'outbound': 0.16,
            'inbound': 0.03,
            'meta_rate': 0.1319,
            'gupshup_margin_pct': 25,
        },
        {
            'min_minutes': 2500001,
            'max_minutes': 5000000,
            'outbound': 0.11,
            'inbound': 0.02,
            'meta_rate': 0.0880,
            'gupshup_margin_pct': 25,
        },
        {
            'min_minutes': 5000001,
            'max_minutes': float('inf'),
            'outbound': 0.07,
            'inbound': 0.02,
            'meta_rate': 0.0586,
            'gupshup_margin_pct': 25,
        },
    ],
}

def get_whatsapp_voice_rate(country, minutes, call_type='outbound'):
    if country != 'India':
        tier = WHATSAPP_VOICE_CHARGES['India'][-1]
        return tier[call_type]
    tiers = WHATSAPP_VOICE_CHARGES.get(country, WHATSAPP_VOICE_CHARGES['India'])
    for tier in tiers:
        if tier['min_minutes'] <= minutes <= tier['max_minutes']:
            return tier[call_type]
    return tiers[-1][call_type]

# =============================================================================
# AI AGENT PRICING (per LLM call)
# =============================================================================
#
# Each ACE model has vendor costs for Regular, Hard, and Complex use cases.
# These are the underlying LLM costs per call in INR (India) or USD
# (International). Pricing logic:
#   - If model cost < threshold (1 INR or 0.0105 USD), we ignore model pricing
#     and continue to use the existing per-message tier logic for AI.
#   - If model cost >= threshold, final AI price per message is:
#         final_price = cost * multiplier
#     where multiplier is currently 5x. In that case, we back out the AI
#     markup as:
#         ai_markup = max(0, final_price - meta_costs_table[country]['ai'])
#     so that:
#         meta_costs_table[country]['ai'] + ai_markup == final_price.
#
# NOTE: All thresholds and multipliers MUST be read from this config; do not
#       hard-code them in app.py or calculator.py.

AI_AGENT_PRICING = {
    'India': {  # Costs in INR per call
        'ACE Agent Lite (Qwen-Qwen3-8B)': {
            'regular': 0.0693208,
            'hard': 0.1299766,
            'complex': 0.1733021,
        },
        'ACE Agent Lite Experimental (gpt-5-nano)': {
            'regular': 0.0736534,
            'hard': 0.1381001,
            'complex': 0.1841335,
        },
        'ACE Agentic pro (gpt-4o-mini)': {
            'regular': 0.1689695,
            'hard': 0.3168179,
            'complex': 0.4224238,
        },
        'ACE Agentic Pro Experimental (gpt-4.1-mini)': {
            'regular': 0.4505854,
            'hard': 0.8448476,
            'complex': 1.1264635,
        },
        'ACE Agent Premium (gpt-4o)': {
            'regular': 2.8161588,
            'hard': 5.2802978,
            'complex': 7.0403970,
        },
        'ACE Agent Premium Experimental (gpt-5-mini)': {
            'regular': 1.8413346,
            'hard': 3.4525024,
            'complex': 4.6033365,
        },
        'ACE Agent Premium Experimental (gpt-4.1)': {
            'regular': 2.2529270,
            'hard': 4.2242382,
            'complex': 5.6323176,
        },
        'ACE Agent Nano Experimental (gpt-4.1-nano)': {
            'regular': 0.1126464,
            'hard': 0.2112119,
            'complex': 0.2816159,
        },
        'ACE Flash Agent Pro (gemini-2.5-flash-lite)': {
            'regular': 0.1126464,
            'hard': 0.2112119,
            'complex': 0.2816159,
        },
        'ACE Flash Agent Premium (gemini-2.5-flash)': {
            'regular': 0.4505854,
            'hard': 0.8448476,
            'complex': 1.1264635,
        },
    },
    'International': {  # Costs in USD per call
        'ACE Agent Lite (Qwen-Qwen3-8B)': {
            'regular': 0.0007680,
            'hard': 0.0014400,
            'complex': 0.0019200,
        },
        'ACE Agent Lite Experimental (gpt-5-nano)': {
            'regular': 0.0008160,
            'hard': 0.0015300,
            'complex': 0.0020400,
        },
        'ACE Agentic pro (gpt-4o-mini)': {
            'regular': 0.0018720,
            'hard': 0.0035100,
            'complex': 0.0046800,
        },
        'ACE Agentic Pro Experimental (gpt-4.1-mini)': {
            'regular': 0.0049920,
            'hard': 0.0093600,
            'complex': 0.0124800,
        },
        'ACE Agent Premium (gpt-4o)': {
            'regular': 0.0312000,
            'hard': 0.0585000,
            'complex': 0.0780000,
        },
        'ACE Agent Premium Experimental (gpt-5-mini)': {
            'regular': 0.0204000,
            'hard': 0.0382500,
            'complex': 0.0510000,
        },
        'ACE Agent Premium Experimental (gpt-4.1)': {
            'regular': 0.0249600,
            'hard': 0.0468000,
            'complex': 0.0624000,
        },
        'ACE Agent Nano Experimental (gpt-4.1-nano)': {
            'regular': 0.0012480,
            'hard': 0.0023400,
            'complex': 0.0031200,
        },
        'ACE Flash Agent Pro (gemini-2.5-flash-lite)': {
            'regular': 0.0012480,
            'hard': 0.0023400,
            'complex': 0.0031200,
        },
        'ACE Flash Agent Premium (gemini-2.5-flash)': {
            'regular': 0.0049920,
            'hard': 0.0093600,
            'complex': 0.0124800,
        },
    },
}

AI_AGENT_SETTINGS = {
    # Thresholds are in the same currency as the underlying costs.
    # Lowered thresholds to ensure model-based pricing kicks in when it 
    # exceeds the standard tier pricing (e.g. price > 1.0 INR or > 0.01 USD).
    'India': {
        'threshold': 0.2,      # INR (0.2 * 5x = 1.0 price floor)
        'multiplier': 5.0,
    },
    'International': {
        'threshold': 0.002,   # USD (0.002 * 5x = 0.01 price floor)
        'multiplier': 5.0,
    },
}


def get_ai_pricing_key(country: str) -> str:
    """
    Map a selected country to the AI pricing key.

    India uses INR pricing, all other countries use the International USD table.
    """
    return 'India' if country == 'India' else 'International'


def get_ai_model_cost(pricing_key: str, model: str, complexity: str) -> float:
    """
    Look up the raw vendor cost per call for a given model + complexity.

    Returns 0.0 if the model or complexity is not found.
    """
    if not model or model == 'None':
        return 0.0
    models = AI_AGENT_PRICING.get(pricing_key, {})
    model_data = models.get(model)
    if not model_data:
        return 0.0
    return float(model_data.get(complexity, 0.0) or 0.0)


def compute_ai_price_components(country: str, model: str, complexity: str, tier_ai_markup: float):
    """
    Compute the effective AI per-message final price and markup.

    Args:
        country: Selected country (e.g., 'India', 'MENA', etc.)
        model: Selected AI agent model name (or 'None' / empty for standard AI)
        complexity: 'regular', 'hard', or 'complex'
        tier_ai_markup: The existing tier-based AI markup (per message) that
                        would be used if models were ignored.

    Returns:
        dict with keys:
            - 'final_price': Final AI price per message (channel + Gupshup markup)
            - 'markup': AI markup per message to show on the rate card
            - 'used_model': True if model pricing overrode the tier logic
    """
    # Base channel AI meta cost (e.g., Meta's per-message AI fee)
    costs = meta_costs_table.get(country, meta_costs_table['APAC'])
    meta_ai_cost = float(costs.get('ai', 0.0) or 0.0)

    pricing_key = get_ai_pricing_key(country)
    settings = AI_AGENT_SETTINGS.get(pricing_key, AI_AGENT_SETTINGS['International'])
    threshold = float(settings.get('threshold', 0.0) or 0.0)
    multiplier = float(settings.get('multiplier', 1.0) or 1.0)

    raw_cost = get_ai_model_cost(pricing_key, model, complexity)
    model_markup = raw_cost * multiplier
    
    # Logic: Only use model-based pricing if cost is above threshold AND 
    # resulting price is higher than the standard tier-based price.
    if raw_cost >= threshold and model_markup > float(tier_ai_markup or 0.0):
        final_price = meta_ai_cost + model_markup
        return {
            'final_price': final_price,
            'markup': model_markup,
            'used_model': True,
        }

    # Fallback: use existing tier-based pricing
    final_price = meta_ai_cost + float(tier_ai_markup or 0.0)
    return {
        'final_price': final_price,
        'markup': float(tier_ai_markup or 0.0),
        'used_model': False,
    }
