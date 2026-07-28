from app import app, db, Analytics, COUNTRY_CURRENCY

# --- Backfill region for users ---
USER_REGION_COUNTRY = {
    'Ankit':    ('India', 'South'),
    'Kat':      ('India', 'South'),
    'Saurabh':  ('India', 'North'),
    'Puru':     ('India', 'West'),
    'Nikhil':   ('India', 'North'),
    'Saathwik': ('India', 'South'),
    'Mridul':   ('India', 'West'),
    'Mariana':  ('LATAM', 'Brazil'),
    'Matheus':  ('LATAM', 'Mexico'),
    'Gourav':   ('India', 'North'),
    # Africa region mappings (matching the regions defined in index.html)
    'Africa_User1': ('Africa', 'South Africa'),
    'Africa_User2': ('Africa', 'Nigeria'),
    'Africa_User3': ('Africa', 'Rest of Africa'),
}

with app.app_context():
    updated = 0
    for rec in Analytics.query.all():
        mapping = USER_REGION_COUNTRY.get(rec.user_name)
        if mapping:
            country, region = mapping
            rec.country = country
            rec.region = region
            updated += 1
    db.session.commit()
    print(f'Backfilled region and country for {updated} records.') 