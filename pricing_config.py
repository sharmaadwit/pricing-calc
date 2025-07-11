# pricing_config.py

# --- Price Tiers by Country and Message Type ---
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

# --- Cost Table by Country ---
meta_costs_table = {
    'India': {'marketing': 0.7846, 'utility': 0.1150, 'ai': 0.30},
    'MENA': {'marketing': 0.0384, 'utility': 0.0157, 'ai': 0.0035},
    'LATAM': {'marketing': 0.0625, 'utility': 0.0068, 'ai': 0.0035},
    'Africa': {'marketing': 0.0379, 'utility': 0.0076, 'ai': 0.0035},
    'Europe': {'marketing': 0.1597, 'utility': 0.05, 'ai': 0.0035},
    'Rest of the World': {'marketing': 0.0592, 'utility': 0.0171, 'ai': 0.0035},
}

# --- Messaging Bundle Markup Rates by Country (for committed amount/bundle flow) ---
bundle_markup_rates = {
    'India': [
        {'min': 0, 'max': 50000, 'basic_marketing': 0.20, 'basic_utility': 0.05, 'advanced': 0.50, 'ai': 1.00},
        {'min': 50001, 'max': 150000, 'basic_marketing': 0.18, 'basic_utility': 0.05, 'advanced': 0.45, 'ai': 0.95},
        {'min': 150001, 'max': 200000, 'basic_marketing': 0.15, 'basic_utility': 0.04, 'advanced': 0.40, 'ai': 0.90},
        {'min': 200001, 'max': 250000, 'basic_marketing': 0.12, 'basic_utility': 0.04, 'advanced': 0.35, 'ai': 0.85},
        {'min': 250001, 'max': 500000, 'basic_marketing': 0.10, 'basic_utility': 0.03, 'advanced': 0.30, 'ai': 0.80},
        {'min': 500001, 'max': 750000, 'basic_marketing': 0.08, 'basic_utility': 0.03, 'advanced': 0.25, 'ai': 0.75},
        {'min': 750001, 'max': 1000000, 'basic_marketing': 0.05, 'basic_utility': 0.02, 'advanced': 0.20, 'ai': 0.70},
        {'min': 1000001, 'max': 2000000, 'basic_marketing': 0.03, 'basic_utility': 0.02, 'advanced': 0.15, 'ai': 0.65},
    ],
    'MENA': [
        {'min': 0, 'max': 1000, 'basic_marketing': 0.0033, 'basic_utility': 0.0008, 'advanced': 0.0083, 'ai': 0.0167},
        {'min': 1001, 'max': 1500, 'basic_marketing': 0.0030, 'basic_utility': 0.0008, 'advanced': 0.0075, 'ai': 0.0158},
        {'min': 1501, 'max': 2500, 'basic_marketing': 0.0025, 'basic_utility': 0.0007, 'advanced': 0.0067, 'ai': 0.0150},
        {'min': 2501, 'max': 3500, 'basic_marketing': 0.0020, 'basic_utility': 0.0006, 'advanced': 0.0058, 'ai': 0.0142},
        {'min': 3501, 'max': 5000, 'basic_marketing': 0.0017, 'basic_utility': 0.0005, 'advanced': 0.0050, 'ai': 0.0133},
        {'min': 5001, 'max': 7500, 'basic_marketing': 0.0013, 'basic_utility': 0.0004, 'advanced': 0.0042, 'ai': 0.0125},
        {'min': 7501, 'max': 10000, 'basic_marketing': 0.0008, 'basic_utility': 0.0003, 'advanced': 0.0033, 'ai': 0.0117},
        {'min': 10001, 'max': 15000, 'basic_marketing': 0.0005, 'basic_utility': 0.0003, 'advanced': 0.0025, 'ai': 0.0108},
    ],
    'LATAM': [
        {'min': 0, 'max': 1000, 'basic_marketing': 0.0033, 'basic_utility': 0.0008, 'advanced': 0.0083, 'ai': 0.0167},
        {'min': 1001, 'max': 1500, 'basic_marketing': 0.0030, 'basic_utility': 0.0008, 'advanced': 0.0075, 'ai': 0.0158},
        {'min': 1501, 'max': 2500, 'basic_marketing': 0.0025, 'basic_utility': 0.0007, 'advanced': 0.0067, 'ai': 0.0150},
        {'min': 2501, 'max': 3500, 'basic_marketing': 0.0020, 'basic_utility': 0.0006, 'advanced': 0.0058, 'ai': 0.0142},
        {'min': 3501, 'max': 5000, 'basic_marketing': 0.0017, 'basic_utility': 0.0005, 'advanced': 0.0050, 'ai': 0.0133},
        {'min': 5001, 'max': 7500, 'basic_marketing': 0.0013, 'basic_utility': 0.0004, 'advanced': 0.0042, 'ai': 0.0125},
        {'min': 7501, 'max': 10000, 'basic_marketing': 0.0008, 'basic_utility': 0.0003, 'advanced': 0.0033, 'ai': 0.0117},
        {'min': 10001, 'max': 15000, 'basic_marketing': 0.0005, 'basic_utility': 0.0003, 'advanced': 0.0025, 'ai': 0.0108},
    ],
    'Africa': [
        {'min': 0, 'max': 1000, 'basic_marketing': 0.0017, 'basic_utility': 0.0004, 'advanced': 0.0042, 'ai': 0.0083},
        {'min': 1001, 'max': 1500, 'basic_marketing': 0.0015, 'basic_utility': 0.0004, 'advanced': 0.0037, 'ai': 0.0079},
        {'min': 1501, 'max': 2500, 'basic_marketing': 0.0012, 'basic_utility': 0.0003, 'advanced': 0.0033, 'ai': 0.0075},
        {'min': 2501, 'max': 3500, 'basic_marketing': 0.0010, 'basic_utility': 0.0003, 'advanced': 0.0029, 'ai': 0.0071},
        {'min': 3501, 'max': 5000, 'basic_marketing': 0.0008, 'basic_utility': 0.0002, 'advanced': 0.0025, 'ai': 0.0067},
        {'min': 5001, 'max': 7500, 'basic_marketing': 0.0007, 'basic_utility': 0.0002, 'advanced': 0.0021, 'ai': 0.0062},
        {'min': 7501, 'max': 10000, 'basic_marketing': 0.0004, 'basic_utility': 0.0002, 'advanced': 0.0017, 'ai': 0.0058},
        {'min': 10001, 'max': 15000, 'basic_marketing': 0.0002, 'basic_utility': 0.0001, 'advanced': 0.0012, 'ai': 0.0054},
    ],
    'Europe': [
        {'min': 0, 'max': 1000, 'basic_marketing': 0.0042, 'basic_utility': 0.0010, 'advanced': 0.0105, 'ai': 0.0209},
        {'min': 1001, 'max': 1500, 'basic_marketing': 0.0038, 'basic_utility': 0.0009, 'advanced': 0.0094, 'ai': 0.0199},
        {'min': 1501, 'max': 2500, 'basic_marketing': 0.0031, 'basic_utility': 0.0008, 'advanced': 0.0084, 'ai': 0.0188},
        {'min': 2501, 'max': 3500, 'basic_marketing': 0.0025, 'basic_utility': 0.0007, 'advanced': 0.0073, 'ai': 0.0178},
        {'min': 3501, 'max': 5000, 'basic_marketing': 0.0021, 'basic_utility': 0.0006, 'advanced': 0.0063, 'ai': 0.0167},
        {'min': 5001, 'max': 7500, 'basic_marketing': 0.0017, 'basic_utility': 0.0005, 'advanced': 0.0052, 'ai': 0.0157},
        {'min': 7501, 'max': 10000, 'basic_marketing': 0.0010, 'basic_utility': 0.0004, 'advanced': 0.0042, 'ai': 0.0146},
        {'min': 10001, 'max': 15000, 'basic_marketing': 0.0006, 'basic_utility': 0.0003, 'advanced': 0.0031, 'ai': 0.0136},
    ],
    'Rest of the World': [
        {'min': 0, 'max': 1000, 'basic_marketing': 0.0033, 'basic_utility': 0.0008, 'advanced': 0.0083, 'ai': 0.0167},
        {'min': 1001, 'max': 1500, 'basic_marketing': 0.0030, 'basic_utility': 0.0008, 'advanced': 0.0075, 'ai': 0.0158},
        {'min': 1501, 'max': 2500, 'basic_marketing': 0.0025, 'basic_utility': 0.0007, 'advanced': 0.0067, 'ai': 0.0150},
        {'min': 2501, 'max': 3500, 'basic_marketing': 0.0020, 'basic_utility': 0.0006, 'advanced': 0.0058, 'ai': 0.0142},
        {'min': 3501, 'max': 5000, 'basic_marketing': 0.0017, 'basic_utility': 0.0005, 'advanced': 0.0050, 'ai': 0.0133},
        {'min': 5001, 'max': 7500, 'basic_marketing': 0.0013, 'basic_utility': 0.0004, 'advanced': 0.0042, 'ai': 0.0125},
        {'min': 7501, 'max': 10000, 'basic_marketing': 0.0008, 'basic_utility': 0.0003, 'advanced': 0.0033, 'ai': 0.0117},
        {'min': 10001, 'max': 15000, 'basic_marketing': 0.0005, 'basic_utility': 0.0003, 'advanced': 0.0025, 'ai': 0.0108},
    ],
}

# --- Country-specific Manday Rates (Bot/UI and Custom/AI) ---
COUNTRY_MANDAY_RATES = {
    'India': {
        'currency': 'INR',
        'bot_ui': 20000,  # Updated
        'custom_ai': 30000,  # Updated
    },
    'LATAM': {
        'currency': 'USD',
        'bot_ui': {
            'LATAM': 825,
            'India': 440,
        },
        'custom_ai': {
            'LATAM': 1100,
            'India': 605,
        },
    },
    'MENA': {
        'currency': 'USD',  # USD for MENA
        'bot_ui': 300,      # Updated to 300 USD
        'custom_ai': 500,   # Updated to 500 USD
    },
    'Africa': {
        'currency': 'USD',
        'bot_ui': 440,
        'custom_ai': 605,
    },
    'Rest of the World': {
        'currency': 'USD',
        'bot_ui': 440,
        'custom_ai': 605,
    },
    'Europe': {
        'currency': 'USD',  # Not in table, fallback to Rest of the World?
        'bot_ui': 440,
        'custom_ai': 605,
    },
}

# --- Country to currency symbol mapping ---
COUNTRY_CURRENCY = {
    'India': '₹',
    'MENA': '$',  # USD for MENA
    'LATAM': '$',
    'Africa': '$',
    'Europe': '$',  # Use USD for Europe
    'Rest of the World': '$',
} 