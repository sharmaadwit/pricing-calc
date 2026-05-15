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
# USAGE: calculator.calculate_total_mandays / calculate_total_manday_cost
# Per-journey/API counts and 4+4 bundle size (5) are hardcoded in calculator._calculate_set_mandays.
ACTIVITY_MANDAYS = {
    "aa_setup": 1,
    "onboarding": 0.5,
    "testing": 1,
    "ux": 1,
    "ai_agents": 5,
    "ai_workspace_support": 2,
}

TEXT_ONE_TIME_LANGUAGE_SCALE_MULTIPLIER = 0.5
TEXT_ONE_TIME_HOURS_PER_MANDAY = 8

# WhatsApp flow screen effort (CE Bot Delivery Effort Estimates — GTM sheet)
TEXT_ONE_TIME_STATIC_FLOW_BASE_DAYS = 1.0
TEXT_ONE_TIME_STATIC_FLOW_INCLUDED_SCREENS = 5
TEXT_ONE_TIME_DYNAMIC_FLOW_BASE_DAYS = 4.0
TEXT_ONE_TIME_DYNAMIC_FLOW_INCLUDED_SCREENS = 5
TEXT_ONE_TIME_FLOW_EXTRA_SCREEN_HOURS = 2

TEXT_ONE_TIME_EFFORT_PROFILES = [
    {
        "id": "simple_structured",
        "complexity": "Simple",
        "bot_type": "Structured Bot",
        "definition": "One static journey up to 20 steps.",
        "inclusions": ["Conditional handling within the base journey."],
        "base_days": 1.0,
        "rate_bucket": "bot_ui",
        "included": {"journeys": 1, "logical_steps": 20},
        "scale_ups": {
            "logical_steps": {"over": 20, "per": 10, "hours": 6},
            "languages_multiplier": TEXT_ONE_TIME_LANGUAGE_SCALE_MULTIPLIER,
        },
        "scale_up_rules": [
            "Every additional 10 logical steps adds 6 hours.",
            "Every additional language adds about 50% of base implementation effort.",
        ],
    },
    {
        "id": "simple_structured_api",
        "complexity": "Simple",
        "bot_type": "Structured + API",
        "definition": "Structured journey up to 20 steps and 5 API calls.",
        "inclusions": ["Journey logic and API integration within the stated limits."],
        "base_days": 1.5,
        "rate_bucket": "bot_ui",
        "included": {"journeys": 1, "logical_steps": 20, "apis": 5},
        "scale_ups": {
            "logical_steps": {"over": 20, "per": 10, "hours": 6},
            "apis": {"over": 5, "per": 2, "hours": 4},
            "languages_multiplier": TEXT_ONE_TIME_LANGUAGE_SCALE_MULTIPLIER,
        },
        "scale_up_rules": [
            "Every additional 10 logical steps adds 6 hours.",
            "Every additional 2 APIs adds 4 hours.",
            "Every additional language adds about 50% of base implementation effort.",
        ],
    },
    {
        "id": "simple_agentic_ai",
        "complexity": "Simple",
        "bot_type": "Agentic AI",
        "definition": "Static FAQ agent.",
        "inclusions": [
            "Training data: text-readable PDFs, CSV files, websites, and PDFs with images and tabular data.",
        ],
        "base_days": 1.0,
        "rate_bucket": "custom_ai",
        "included": {},
        "scale_ups": {},
        "scale_up_rules": ["Total hours may vary based on time taken to train the agent on the supplied data."],
    },
    {
        "id": "medium_structured_api",
        "complexity": "Medium",
        "bot_type": "Structured + API",
        "definition": "One journey up to 20 steps and 2 APIs with encryption/decryption handling.",
        "inclusions": ["Encryption/decryption handling and journey-specific logic."],
        "base_days": 2.0,
        "rate_bucket": "bot_ui",
        "included": {"journeys": 1, "logical_steps": 20, "apis": 2},
        "scale_ups": {
            "logical_steps": {"over": 20, "per": 10, "hours": 6},
            "apis": {"over": 2, "per": 2, "hours": 4},
            "languages_multiplier": TEXT_ONE_TIME_LANGUAGE_SCALE_MULTIPLIER,
        },
        "scale_up_rules": [
            "Every additional 10 logical steps adds 6 hours.",
            "Every additional 2 APIs adds 4 hours.",
            "Every additional language adds about 50% of base implementation effort.",
        ],
    },
    {
        "id": "medium_catalog",
        "complexity": "Medium",
        "bot_type": "Catalog",
        "definition": "Catalog journey without native payment (up to 20 steps and 3 APIs).",
        "inclusions": ["Catalog browsing and product selection without native payment."],
        "base_days": 3.0,
        "rate_bucket": "bot_ui",
        "included": {"journeys": 1, "logical_steps": 20, "apis": 3},
        "scale_ups": {
            "logical_steps": {"over": 20, "per": 10, "hours": 6},
            "apis": {"over": 3, "per": 2, "hours": 4},
        },
        "scale_up_rules": [],
    },
    {
        "id": "medium_native_payment",
        "complexity": "Medium",
        "bot_type": "Native Payment",
        "definition": "Purchase journey without catalog with native payment (up to 20 steps and 5 APIs).",
        "inclusions": ["Native payment flow without catalog integration."],
        "base_days": 4.0,
        "rate_bucket": "bot_ui",
        "included": {"journeys": 1, "logical_steps": 20, "apis": 5},
        "scale_ups": {
            "logical_steps": {"over": 20, "per": 10, "hours": 6},
            "apis": {"over": 5, "per": 2, "hours": 4},
        },
        "scale_up_rules": [],
    },
    {
        "id": "medium_catalog_native_payment",
        "complexity": "Medium",
        "bot_type": "Catalog + Native Payment",
        "definition": "Purchase journey with catalog and native payment (up to 20 steps and 5 APIs).",
        "inclusions": ["Catalog browsing and native payment within the stated limits."],
        "base_days": 5.0,
        "rate_bucket": "bot_ui",
        "included": {"journeys": 1, "logical_steps": 20, "apis": 5},
        "scale_ups": {
            "logical_steps": {"over": 20, "per": 10, "hours": 6},
            "apis": {"over": 5, "per": 2, "hours": 4},
        },
        "scale_up_rules": [],
    },
    {
        "id": "medium_agentic_ai_api",
        "complexity": "Medium",
        "bot_type": "Agentic AI + API",
        "definition": "Journey with a set of steps and up to 3 APIs (tool integration).",
        "inclusions": ["Agentic journey with tool/API integration within the base API limit."],
        "base_days": 3.0,
        "rate_bucket": "custom_ai",
        "included": {"apis": 3},
        "scale_ups": {"apis": {"over": 3, "per": 2, "hours": 4}},
        "comments": "Examples: lead generation, appointment booking.",
        "scale_up_rules": [],
    },
    {
        "id": "complex_agentic_ai_api",
        "complexity": "Complex",
        "bot_type": "Agentic AI + API",
        "definition": "AI agent with richer training data, tool integration, and formatted messaging.",
        "inclusions": [
            "Training data: websites, complex PDF documents, and web scraping.",
            "API tool integration for more than 3 APIs, including APIs with certificates.",
            "WhatsApp formatted messages and up to 5 APIs.",
        ],
        "base_days": 7.5,
        "rate_bucket": "custom_ai",
        "included": {"apis": 5},
        "scale_ups": {"apis": {"over": 5, "per": 2, "hours": 4}},
        "scale_up_rules": [],
    },
]

TEXT_ONE_TIME_EFFORT_PROFILES_BY_ID = {
    profile["id"]: profile for profile in TEXT_ONE_TIME_EFFORT_PROFILES
}

TEXT_ONE_TIME_AGENTIC_PROFILE_IDS = {
    profile["id"]
    for profile in TEXT_ONE_TIME_EFFORT_PROFILES
    if profile.get("rate_bucket") == "custom_ai"
}


def normalize_one_time_dev_profile(profile_id: str) -> str:
    profile_id = (profile_id or "").strip()
    return profile_id if profile_id in TEXT_ONE_TIME_EFFORT_PROFILES_BY_ID else ""


def get_one_time_dev_profile(profile_id: str):
    return TEXT_ONE_TIME_EFFORT_PROFILES_BY_ID.get(normalize_one_time_dev_profile(profile_id))


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
    'siddharth.singh@gupshup.io': {'country': 'MENA', 'region': 'UAE'},
    'yashas.reddy@gupshup.io': {'country': 'Africa', 'region': 'South Africa'},
    'nidhi.shridhar@gupshup.io': {'country': 'India', 'region': 'North'},
    'maria.diaz@gupshup.io': {'country': 'LATAM', 'region': 'Mexico'},
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
    'additional_language_multiplier': 0.30,
    'agent_handover_pstn_knowlarity': 1,
    'agent_handover_pstn_other': 5,
    'whatsapp_voice_knowlarity': 1,
    'whatsapp_voice_other': 5,
}

# Leverage (Voice AI partner) — development pass-through in INR; margin applied in calculator
LEVERAGE_VOICE_DEV_COSTS_INR = {
    'simple': 25000,
    'medium': 50000,
    'complex': 125000,
}
LEVERAGE_VOICE_ADDITIONAL_LANGUAGE_COST_INR = 25000
# Client price = partner_cost * (1 + LEVERAGE_VOICE_BUILD_MARGIN)
LEVERAGE_VOICE_BUILD_MARGIN = 0.50

AED_TO_USD = 0.2723

# PSTN Calling Charges (Knowlarity)
PSTN_CALLING_CHARGES_BY_REGION = {
    'India': {
        'inbound': 0.0,
        'outbound': 0.4,
        'manual_c2c': 0.4,
    },
    'MENA': {
        'inbound': round(0.10 * AED_TO_USD, 4),
        'outbound': round(0.30 * AED_TO_USD, 4),
        'manual_c2c': round(0.30 * AED_TO_USD, 4),
    },
}

# WhatsApp Voice Calling Charges - volume-based tiers
WHATSAPP_VOICE_CHARGES = {
    'India': [
        {
            'min_minutes': 0,
            'max_minutes': 50000,
            'outbound': 0.58275,
            'inbound': 0.097125,
            'voice_ai_addon_per_min': 7,
            'wa_platform_fee': 50000,
        },
        {
            'min_minutes': 50001,
            'max_minutes': 250000,
            'outbound': 0.41775,
            'inbound': 0.069625,
            'voice_ai_addon_per_min': 6.5,
            'wa_platform_fee': 75000,
        },
        {
            'min_minutes': 250001,
            'max_minutes': 1000000,
            'outbound': 0.26385,
            'inbound': 0.043975,
            'voice_ai_addon_per_min': 6,
            'wa_platform_fee': 100000,
        },
        {
            'min_minutes': 1000001,
            'max_minutes': 2500000,
            'outbound': 0.19785,
            'inbound': 0.032975,
            'voice_ai_addon_per_min': 5.5,
            'wa_platform_fee': 200000,
        },
        {
            'min_minutes': 2500001,
            'max_minutes': 5000000,
            'outbound': 0.132,
            'inbound': 0.022,
            'voice_ai_addon_per_min': 5,
            'wa_platform_fee': 300000,
        },
        {
            'min_minutes': 5000001,
            'max_minutes': float('inf'),
            'outbound': 0.0879,
            'inbound': 0.01465,
            'voice_ai_addon_per_min': None,
            'wa_platform_fee': None,
        },
    ],
    'United Arab Emirates': [
        {'min_minutes': 0, 'max_minutes': 50000, 'inbound': 0.003175, 'outbound': 0.01905, 'voice_ai_addon_per_min': 0.16666666666666666, 'wa_platform_fee': 2000.0},
        {'min_minutes': 50001, 'max_minutes': 250000, 'inbound': 0.002675, 'outbound': 0.01605, 'voice_ai_addon_per_min': 0.15555555555555556, 'wa_platform_fee': 3000.0},
        {'min_minutes': 250001, 'max_minutes': 1000000, 'inbound': 0.00225, 'outbound': 0.0135, 'voice_ai_addon_per_min': 0.14444444444444443, 'wa_platform_fee': 4000.0},
        {'min_minutes': 1000001, 'max_minutes': 2500000, 'inbound': 0.0017, 'outbound': 0.0102, 'voice_ai_addon_per_min': 0.14444444444444443, 'wa_platform_fee': 5000.0},
        {'min_minutes': 2500001, 'max_minutes': 5000000, 'inbound': 0.001375, 'outbound': 0.00825, 'voice_ai_addon_per_min': 0.13333333333333333, 'wa_platform_fee': 6000.0},
        {'min_minutes': 5000001, 'max_minutes': float('inf'), 'inbound': 0.00125, 'outbound': 0.0075, 'voice_ai_addon_per_min': None, 'wa_platform_fee': None},
    ],
    'Saudi Arabia': [
        {'min_minutes': 0, 'max_minutes': 50000, 'inbound': 0.003175, 'outbound': 0.01905, 'voice_ai_addon_per_min': 0.16666666666666666, 'wa_platform_fee': 2000.0},
        {'min_minutes': 50001, 'max_minutes': 250000, 'inbound': 0.002675, 'outbound': 0.01605, 'voice_ai_addon_per_min': 0.15555555555555556, 'wa_platform_fee': 3000.0},
        {'min_minutes': 250001, 'max_minutes': 1000000, 'inbound': 0.00225, 'outbound': 0.0135, 'voice_ai_addon_per_min': 0.14444444444444443, 'wa_platform_fee': 4000.0},
        {'min_minutes': 1000001, 'max_minutes': 2500000, 'inbound': 0.0017, 'outbound': 0.0102, 'voice_ai_addon_per_min': 0.14444444444444443, 'wa_platform_fee': 5000.0},
        {'min_minutes': 2500001, 'max_minutes': 5000000, 'inbound': 0.001375, 'outbound': 0.00825, 'voice_ai_addon_per_min': 0.13333333333333333, 'wa_platform_fee': 6000.0},
        {'min_minutes': 5000001, 'max_minutes': float('inf'), 'inbound': 0.00125, 'outbound': 0.0075, 'voice_ai_addon_per_min': None, 'wa_platform_fee': None},
    ],
    'Brazil': [
        {'min_minutes': 0, 'max_minutes': 50000, 'inbound': 0.0027, 'outbound': 0.0162, 'voice_ai_addon_per_min': 0.16666666666666666, 'wa_platform_fee': 2000.0},
        {'min_minutes': 50001, 'max_minutes': 250000, 'inbound': 0.0017, 'outbound': 0.0102, 'voice_ai_addon_per_min': 0.15555555555555556, 'wa_platform_fee': 3000.0},
        {'min_minutes': 250001, 'max_minutes': 1000000, 'inbound': 0.0011, 'outbound': 0.0066, 'voice_ai_addon_per_min': 0.14444444444444443, 'wa_platform_fee': 4000.0},
        {'min_minutes': 1000001, 'max_minutes': 2500000, 'inbound': 0.00085, 'outbound': 0.0051, 'voice_ai_addon_per_min': 0.14444444444444443, 'wa_platform_fee': 5000.0},
        {'min_minutes': 2500001, 'max_minutes': 5000000, 'inbound': 0.0005, 'outbound': 0.003, 'voice_ai_addon_per_min': 0.13333333333333333, 'wa_platform_fee': 6000.0},
        {'min_minutes': 5000001, 'max_minutes': float('inf'), 'inbound': 0.00045, 'outbound': 0.0027, 'voice_ai_addon_per_min': None, 'wa_platform_fee': None},
    ],
    'Mexico': [
        {'min_minutes': 0, 'max_minutes': 50000, 'inbound': 0.00235, 'outbound': 0.0141, 'voice_ai_addon_per_min': 0.16666666666666666, 'wa_platform_fee': 2000.0},
        {'min_minutes': 50001, 'max_minutes': 250000, 'inbound': 0.002, 'outbound': 0.012, 'voice_ai_addon_per_min': 0.15555555555555556, 'wa_platform_fee': 3000.0},
        {'min_minutes': 250001, 'max_minutes': 1000000, 'inbound': 0.00175, 'outbound': 0.0105, 'voice_ai_addon_per_min': 0.14444444444444443, 'wa_platform_fee': 4000.0},
        {'min_minutes': 1000001, 'max_minutes': 2500000, 'inbound': 0.00135, 'outbound': 0.0081, 'voice_ai_addon_per_min': 0.14444444444444443, 'wa_platform_fee': 5000.0},
        {'min_minutes': 2500001, 'max_minutes': 5000000, 'inbound': 0.00105, 'outbound': 0.0063, 'voice_ai_addon_per_min': 0.13333333333333333, 'wa_platform_fee': 6000.0},
        {'min_minutes': 5000001, 'max_minutes': float('inf'), 'inbound': 0.00095, 'outbound': 0.0057, 'voice_ai_addon_per_min': None, 'wa_platform_fee': None},
    ],
    'South Africa': [
        {'min_minutes': 0, 'max_minutes': 50000, 'inbound': 0.0027, 'outbound': 0.0162, 'voice_ai_addon_per_min': 0.16666666666666666, 'wa_platform_fee': 2000.0},
        {'min_minutes': 50001, 'max_minutes': 250000, 'inbound': 0.00195, 'outbound': 0.0117, 'voice_ai_addon_per_min': 0.15555555555555556, 'wa_platform_fee': 3000.0},
        {'min_minutes': 250001, 'max_minutes': 1000000, 'inbound': 0.001475, 'outbound': 0.00885, 'voice_ai_addon_per_min': 0.14444444444444443, 'wa_platform_fee': 4000.0},
        {'min_minutes': 1000001, 'max_minutes': 2500000, 'inbound': 0.0011, 'outbound': 0.0066, 'voice_ai_addon_per_min': 0.14444444444444443, 'wa_platform_fee': 5000.0},
        {'min_minutes': 2500001, 'max_minutes': 5000000, 'inbound': 0.001025, 'outbound': 0.00615, 'voice_ai_addon_per_min': 0.13333333333333333, 'wa_platform_fee': 6000.0},
        {'min_minutes': 5000001, 'max_minutes': float('inf'), 'inbound': 0.00095, 'outbound': 0.0057, 'voice_ai_addon_per_min': None, 'wa_platform_fee': None},
    ],
    'Nigeria': [
        {'min_minutes': 0, 'max_minutes': 50000, 'inbound': 0.002575, 'outbound': 0.01545, 'voice_ai_addon_per_min': 0.16666666666666666, 'wa_platform_fee': 2000.0},
        {'min_minutes': 50001, 'max_minutes': 250000, 'inbound': 0.0021, 'outbound': 0.0126, 'voice_ai_addon_per_min': 0.15555555555555556, 'wa_platform_fee': 3000.0},
        {'min_minutes': 250001, 'max_minutes': 1000000, 'inbound': 0.00185, 'outbound': 0.0111, 'voice_ai_addon_per_min': 0.14444444444444443, 'wa_platform_fee': 4000.0},
        {'min_minutes': 1000001, 'max_minutes': 2500000, 'inbound': 0.001725, 'outbound': 0.01035, 'voice_ai_addon_per_min': 0.14444444444444443, 'wa_platform_fee': 5000.0},
        {'min_minutes': 2500001, 'max_minutes': 5000000, 'inbound': 0.001375, 'outbound': 0.00825, 'voice_ai_addon_per_min': 0.13333333333333333, 'wa_platform_fee': 6000.0},
        {'min_minutes': 5000001, 'max_minutes': float('inf'), 'inbound': 0.001325, 'outbound': 0.00795, 'voice_ai_addon_per_min': None, 'wa_platform_fee': None},
    ],
    'Rest of Africa': [
        {'min_minutes': 0, 'max_minutes': 50000, 'inbound': 0.002575, 'outbound': 0.01545, 'voice_ai_addon_per_min': 0.16666666666666666, 'wa_platform_fee': 2000.0},
        {'min_minutes': 50001, 'max_minutes': 250000, 'inbound': 0.0021, 'outbound': 0.0126, 'voice_ai_addon_per_min': 0.15555555555555556, 'wa_platform_fee': 3000.0},
        {'min_minutes': 250001, 'max_minutes': 1000000, 'inbound': 0.00185, 'outbound': 0.0111, 'voice_ai_addon_per_min': 0.14444444444444443, 'wa_platform_fee': 4000.0},
        {'min_minutes': 1000001, 'max_minutes': 2500000, 'inbound': 0.00155, 'outbound': 0.0093, 'voice_ai_addon_per_min': 0.14444444444444443, 'wa_platform_fee': 5000.0},
        {'min_minutes': 2500001, 'max_minutes': 5000000, 'inbound': 0.001175, 'outbound': 0.00705, 'voice_ai_addon_per_min': 0.13333333333333333, 'wa_platform_fee': 6000.0},
        {'min_minutes': 5000001, 'max_minutes': float('inf'), 'inbound': 0.00105, 'outbound': 0.0063, 'voice_ai_addon_per_min': None, 'wa_platform_fee': None},
    ],
    'Rest of Middle East': [
        {'min_minutes': 0, 'max_minutes': 50000, 'inbound': 0.003175, 'outbound': 0.01905, 'voice_ai_addon_per_min': 0.16666666666666666, 'wa_platform_fee': 2000.0},
        {'min_minutes': 50001, 'max_minutes': 250000, 'inbound': 0.002675, 'outbound': 0.01605, 'voice_ai_addon_per_min': 0.15555555555555556, 'wa_platform_fee': 3000.0},
        {'min_minutes': 250001, 'max_minutes': 1000000, 'inbound': 0.00225, 'outbound': 0.0135, 'voice_ai_addon_per_min': 0.14444444444444443, 'wa_platform_fee': 4000.0},
        {'min_minutes': 1000001, 'max_minutes': 2500000, 'inbound': 0.0017, 'outbound': 0.0102, 'voice_ai_addon_per_min': 0.14444444444444443, 'wa_platform_fee': 5000.0},
        {'min_minutes': 2500001, 'max_minutes': 5000000, 'inbound': 0.001375, 'outbound': 0.00825, 'voice_ai_addon_per_min': 0.13333333333333333, 'wa_platform_fee': 6000.0},
        {'min_minutes': 5000001, 'max_minutes': float('inf'), 'inbound': 0.00125, 'outbound': 0.0075, 'voice_ai_addon_per_min': None, 'wa_platform_fee': None},
    ],
    'Rest of Latin America': [
        {'min_minutes': 0, 'max_minutes': 50000, 'inbound': 0.0029, 'outbound': 0.0174, 'voice_ai_addon_per_min': 0.16666666666666666, 'wa_platform_fee': 2000.0},
        {'min_minutes': 50001, 'max_minutes': 250000, 'inbound': 0.002375, 'outbound': 0.01425, 'voice_ai_addon_per_min': 0.15555555555555556, 'wa_platform_fee': 3000.0},
        {'min_minutes': 250001, 'max_minutes': 1000000, 'inbound': 0.00205, 'outbound': 0.0123, 'voice_ai_addon_per_min': 0.14444444444444443, 'wa_platform_fee': 4000.0},
        {'min_minutes': 1000001, 'max_minutes': 2500000, 'inbound': 0.00175, 'outbound': 0.0105, 'voice_ai_addon_per_min': 0.14444444444444443, 'wa_platform_fee': 5000.0},
        {'min_minutes': 2500001, 'max_minutes': 5000000, 'inbound': 0.0012, 'outbound': 0.0072, 'voice_ai_addon_per_min': 0.13333333333333333, 'wa_platform_fee': 6000.0},
        {'min_minutes': 5000001, 'max_minutes': float('inf'), 'inbound': 0.001175, 'outbound': 0.00705, 'voice_ai_addon_per_min': None, 'wa_platform_fee': None},
    ],
    'Rest of Western Europe': [
        {'min_minutes': 0, 'max_minutes': 50000, 'inbound': 0.002575, 'outbound': 0.01545, 'voice_ai_addon_per_min': 0.16666666666666666, 'wa_platform_fee': 2000.0},
        {'min_minutes': 50001, 'max_minutes': 250000, 'inbound': 0.0021, 'outbound': 0.0126, 'voice_ai_addon_per_min': 0.15555555555555556, 'wa_platform_fee': 3000.0},
        {'min_minutes': 250001, 'max_minutes': 1000000, 'inbound': 0.00185, 'outbound': 0.0111, 'voice_ai_addon_per_min': 0.14444444444444443, 'wa_platform_fee': 4000.0},
        {'min_minutes': 1000001, 'max_minutes': 2500000, 'inbound': 0.00155, 'outbound': 0.0093, 'voice_ai_addon_per_min': 0.14444444444444443, 'wa_platform_fee': 5000.0},
        {'min_minutes': 2500001, 'max_minutes': 5000000, 'inbound': 0.001375, 'outbound': 0.00825, 'voice_ai_addon_per_min': 0.13333333333333333, 'wa_platform_fee': 6000.0},
        {'min_minutes': 5000001, 'max_minutes': float('inf'), 'inbound': 0.001175, 'outbound': 0.00705, 'voice_ai_addon_per_min': None, 'wa_platform_fee': None},
    ],
    'Rest of Asia Pacific': [
        {'min_minutes': 0, 'max_minutes': 50000, 'inbound': 0.00285, 'outbound': 0.0171, 'voice_ai_addon_per_min': 0.16666666666666666, 'wa_platform_fee': 2000.0},
        {'min_minutes': 50001, 'max_minutes': 250000, 'inbound': 0.00235, 'outbound': 0.0141, 'voice_ai_addon_per_min': 0.15555555555555556, 'wa_platform_fee': 3000.0},
        {'min_minutes': 250001, 'max_minutes': 1000000, 'inbound': 0.002025, 'outbound': 0.01215, 'voice_ai_addon_per_min': 0.14444444444444443, 'wa_platform_fee': 4000.0},
        {'min_minutes': 1000001, 'max_minutes': 2500000, 'inbound': 0.001725, 'outbound': 0.01035, 'voice_ai_addon_per_min': 0.14444444444444443, 'wa_platform_fee': 5000.0},
        {'min_minutes': 2500001, 'max_minutes': 5000000, 'inbound': 0.0013, 'outbound': 0.0078, 'voice_ai_addon_per_min': 0.13333333333333333, 'wa_platform_fee': 6000.0},
        {'min_minutes': 5000001, 'max_minutes': float('inf'), 'inbound': 0.0011, 'outbound': 0.0066, 'voice_ai_addon_per_min': None, 'wa_platform_fee': None},
    ],
}

WA_VOICE_MARKET_BY_REGION = {
    'UAE': 'United Arab Emirates',
    'KSA': 'Saudi Arabia',
    'Brazil': 'Brazil',
    'Mexico': 'Mexico',
    'South Africa': 'South Africa',
    'Nigeria': 'Nigeria',
    'Rest of Africa': 'Rest of Africa',
}

WA_VOICE_MARKET_BY_COUNTRY = {
    'MENA': 'Rest of Middle East',
    'LATAM': 'Rest of Latin America',
    'Africa': 'Rest of Africa',
    'Europe': 'Rest of Western Europe',
    'APAC': 'Rest of Asia Pacific',
}

def resolve_wa_voice_market(country, region=None):
    if country == 'India':
        return 'India'
    region_key = (region or '').strip()
    if region_key and region_key in WA_VOICE_MARKET_BY_REGION:
        return WA_VOICE_MARKET_BY_REGION[region_key]
    return WA_VOICE_MARKET_BY_COUNTRY.get(country, 'Rest of Western Europe')

def get_pstn_rates(country, region=None):
    if country == 'India':
        return PSTN_CALLING_CHARGES_BY_REGION['India']
    if country == 'MENA':
        return PSTN_CALLING_CHARGES_BY_REGION['MENA']
    return None

def get_whatsapp_voice_tier(country, minutes, region=None):
    market = resolve_wa_voice_market(country, region)
    tiers = WHATSAPP_VOICE_CHARGES.get(market, WHATSAPP_VOICE_CHARGES['India'])
    for tier in tiers:
        if tier['min_minutes'] <= minutes <= tier['max_minutes']:
            return tier
    return tiers[-1]

def get_whatsapp_voice_rate(country, minutes, call_type='outbound', region=None):
    tier = get_whatsapp_voice_tier(country, minutes, region=region)
    return tier[call_type]


def build_voice_rate_card_for_prices(inputs, country=None):
    """
    Structure for the prices step UI: PSTN bundled/overage per minute and WhatsApp per-minute
    rates, aligned with calculator.calculate_voice_calling_costs defaults
    (base Knowlarity/MENA rate + PSTN voice-AI add-on when applicable).
    """
    chan = (inputs or {}).get('channel_type', 'text_only')
    if chan not in ('voice_only', 'text_voice'):
        return None

    def _pv(x):
        try:
            return float(str(x).replace(',', '')) if x not in (None, '') else 0.0
        except Exception:
            return 0.0

    c = (country or (inputs or {}).get('country') or 'India').strip()
    region = (inputs or {}).get('region')
    wa_out = _pv((inputs or {}).get('whatsapp_voice_outbound_minutes', 0))
    wa_in = _pv((inputs or {}).get('whatsapp_voice_inbound_minutes', 0))
    total_wa_min = wa_out + wa_in
    wa_addon = 0.0
    if total_wa_min > 0 and (inputs or {}).get('voice_ai_enabled', 'No') == 'Yes':
        wt = get_whatsapp_voice_tier(c, total_wa_min, region=region)
        wa_addon = float(wt.get('voice_ai_addon_per_min') or 0)
    wa_out_rate = float(get_whatsapp_voice_rate(c, total_wa_min, 'outbound', region=region)) + wa_addon
    wa_in_rate = float(get_whatsapp_voice_rate(c, total_wa_min, 'inbound', region=region)) + wa_addon

    pstn_block = None
    pstn_rates = get_pstn_rates(c, region)
    if pstn_rates:
        in_m = _pv((inputs or {}).get('pstn_inbound_ai_minutes', 0))
        out_m = _pv((inputs or {}).get('pstn_outbound_ai_minutes', 0))
        man_m = _pv((inputs or {}).get('pstn_manual_minutes', 0))
        total_pstn_min = in_m + out_m + man_m
        pstn_ai_addon = 0.0
        if total_pstn_min > 0 and (inputs or {}).get('voice_ai_enabled', 'No') == 'Yes':
            pt = get_whatsapp_voice_tier(c, total_pstn_min, region=region)
            pstn_ai_addon = float(pt.get('voice_ai_addon_per_min') or 0)

        def _pair(base):
            r = float(base) + pstn_ai_addon
            return {'bundled': r, 'overage': r}

        pstn_block = {
            'inbound': _pair(pstn_rates['inbound']),
            'outbound': _pair(pstn_rates['outbound']),
            'manual': _pair(pstn_rates['manual_c2c']),
        }

    return {
        'pstn': pstn_block,
        'whatsapp': {
            'outbound': wa_out_rate,
            'inbound': wa_in_rate,
            'total_minutes': total_wa_min,
        },
    }


# =============================================================================
# AI AGENT PRICING (per LLM call)
# =============================================================================
#
# Each ACE model has vendor costs for Regular, Hard, and Complex use cases.
# These are the underlying LLM costs per call in INR (India) or USD
# (International), derived from the rate card: cost per 1k tokens × token
# assumptions (regular 8k, hard 15k, complex 20k), including 20% infra.
# Pricing logic (see compute_ai_price_components):
#   - Raw cost below/equal threshold (1 INR or ~0.0105 USD): AI markup is a flat
#     threshold amount (charge “at 1” / USD equivalent).
#   - Raw cost above threshold: AI markup = raw_cost * multiplier (2x).
#   - Model path only applies when that markup beats volume-tier AI markup.
#   - final AI price per message = meta_costs_table[country]['ai'] + markup.
#
# NOTE: All thresholds and multipliers MUST be read from this config; do not
#       hard-code them in app.py or calculator.py.

AI_AGENT_PRICING = {
    'India': {  # Costs in INR per call (rate card; token × FX, incl. 20% infra)
        'ACE Agent Lite (Qwen-Qwen3-8B)': {
            'regular': 0.0723644,
            'hard': 0.1356833,
            'complex': 0.1809111,
        },
        'ACE Agent Lite Experimental (gpt-5-nano)': {
            'regular': 0.0768872,
            'hard': 0.1441635,
            'complex': 0.1922180,
        },
        'ACE Agentic pro (gpt-5-mini)': {
            'regular': 0.3844360,
            'hard': 0.7208175,
            'complex': 0.9610900,
        },
        'ACE Agentic Pro Experimental (gpt-4.1-mini)': {
            'regular': 0.4703687,
            'hard': 0.8819414,
            'complex': 1.1759219,
        },
        'ACE Agent Premium (gpt-5)': {
            'regular': 1.9221800,
            'hard': 3.6040875,
            'complex': 4.8054499,
        },
        'ACE Agent Premium Experimental (gpt-4.1)': {
            'regular': 2.3518437,
            'hard': 4.4097070,
            'complex': 5.8796093,
        },
        'ACE Flash Agent Pro (gemini-2.5-flash-lite)': {
            'regular': 0.1175922,
            'hard': 0.2204854,
            'complex': 0.2939805,
        },
        'ACE Flash Agent Premium (gemini-2.5-flash)': {
            'regular': 0.4703687,
            'hard': 0.8819414,
            'complex': 1.1759219,
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
        'ACE Agentic pro (gpt-5-mini)': {
            'regular': 0.0040800,
            'hard': 0.0076500,
            'complex': 0.0102000,
        },
        'ACE Agentic Pro Experimental (gpt-4.1-mini)': {
            'regular': 0.0049920,
            'hard': 0.0093600,
            'complex': 0.0124800,
        },
        'ACE Agent Premium (gpt-5)': {
            'regular': 0.0204000,
            'hard': 0.0382500,
            'complex': 0.0510000,
        },
        'ACE Agent Premium Experimental (gpt-4.1)': {
            'regular': 0.0249600,
            'hard': 0.0468000,
            'complex': 0.0624000,
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

# Older sessions stored these display names; map to current keys for lookups.
AI_AGENT_MODEL_LEGACY_ALIASES = {
    'ACE Agentic pro (gpt-4o-mini)': 'ACE Agentic pro (gpt-5-mini)',
    'ACE Agent Premium (gpt-4o)': 'ACE Agent Premium (gpt-5)',
    'ACE Agent Nano Experimental (gpt-4.1-nano)': 'ACE Flash Agent Pro (gemini-2.5-flash-lite)',
}

AI_AGENT_SETTINGS = {
    # Threshold: flat markup when raw_cost <= threshold; above threshold use multiplier.
    'India': {
        'threshold': 1.0,      # INR — flat AI markup when model raw cost <= 1
        'multiplier': 2.0,
    },
    'International': {
        'threshold': 0.0105,   # USD (~parity with 1 INR tier in prior config)
        'multiplier': 2.0,
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
    model = AI_AGENT_MODEL_LEGACY_ALIASES.get(model, model)
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

    # Model-based markup: above threshold → 2× raw cost; at/below → flat threshold
    # (1 INR or USD equivalent), not the raw fractional token cost.
    if raw_cost <= 0:
        model_markup = 0.0
    elif raw_cost <= threshold:
        model_markup = threshold
    else:
        model_markup = raw_cost * multiplier

    if raw_cost > 0 and model_markup > float(tier_ai_markup or 0.0):
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
