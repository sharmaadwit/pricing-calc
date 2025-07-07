from app import app, db, Analytics, COUNTRY_CURRENCY

with app.app_context():
    records = Analytics.query.filter((Analytics.currency == None) | (Analytics.currency == '')).all()
    updated = 0
    for rec in records:
        rec.currency = COUNTRY_CURRENCY.get(rec.country, '$')
        updated += 1
    db.session.commit()
    print(f'Backfilled {updated} records.') 