# utils.py

def parse_volume(val):
    """
    Safely parse a volume value from string to float. Returns 0.0 if invalid or empty.
    """
    try:
        return float(val.replace(',', '')) if val and str(val).strip() else 0.0
    except Exception:
        return 0.0

def parse_price(val):
    """
    Safely parse a price value from string to float. Returns None if invalid or empty.
    """
    try:
        return float(val.replace(',', '')) if val and str(val).strip() else None
    except Exception:
        return None

def is_zero(val):
    """
    Returns True if the value is zero or empty, False otherwise.
    """
    try:
        return float(val) == 0.0
    except Exception:
        return True 