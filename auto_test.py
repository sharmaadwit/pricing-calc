import requests

COUNTRIES = ["India", "MENA", "LATAM", "Africa", "Europe", "Rest of the World"]
BASE_URL = "http://127.0.0.1:8081"

def run_test(country, committed=True):
    path_type = "Committed Amount" if committed else "Volume"
    print(f"\n--- Testing {country} ({path_type} path) ---")
    session = requests.Session()
    # Step 1: Volumes
    data = {
        "step": "volumes",
        "country": country,
        "ai_volume": 0 if committed else 1000,
        "advanced_volume": 0,
        "basic_marketing_volume": 0,
        "basic_utility_volume": 0,
        "user_name": "TestUser"
    }
    print("  Submitting volumes...")
    resp1 = session.post(f"{BASE_URL}/", data=data)
    print(f"    Response: {resp1.status_code}")
    # Step 2: Prices
    data = {
        "step": "prices",
        "platform_fee": 1000,
        "ai_price": 0.1,
        "advanced_price": 0.05,
        "basic_marketing_price": 0.01,
        "basic_utility_price": 0.005
    }
    print("  Submitting prices...")
    resp2 = session.post(f"{BASE_URL}/", data=data)
    print(f"    Response: {resp2.status_code}")
    # Step 3: Committed or Volume
    if committed:
        data = {"step": "bundle", "committed_amount": 5000}
        print("  Submitting committed amount...")
        r = session.post(f"{BASE_URL}/", data=data)
        print(f"    Response: {r.status_code}")
        fname = f"results_committed_{country.replace(' ', '_')}.html"
    else:
        print("  Submitting for volume path (no committed amount)...")
        r = session.post(f"{BASE_URL}/", data=data)
        print(f"    Response: {r.status_code}")
        fname = f"results_volume_{country.replace(' ', '_')}.html"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(r.text)
    print(f"  Saved: {fname}")

if __name__ == "__main__":
    print("Starting auto_test.py...")
    for country in COUNTRIES:
        run_test(country, committed=True)
        run_test(country, committed=False)
    print("\nAll tests complete.") 