import psycopg2
import csv
import sys

# --- CONFIGURE THESE VARIABLES ---
DB_URL = "postgresql://postgres:prdeuXwtBzpLZaOGpxgRspfjfLNEQrys@gondola.proxy.rlwy.net:25504/railway"
TABLE = "analytics"
OUTPUT_CSV = "analytics.csv"

# --- OPTIONAL: Allow table name and output file as command line args ---
if len(sys.argv) > 1:
    TABLE = sys.argv[1]
if len(sys.argv) > 2:
    OUTPUT_CSV = sys.argv[2]

try:
    # Connect using the full URL
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {TABLE}")
    if cur.description is None:
        print(f"Error: Table '{TABLE}' does not exist or query failed.")
        cur.close()
        conn.close()
        sys.exit(1)
    columns = [desc[0] for desc in cur.description]
    with open(OUTPUT_CSV, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        for row in cur.fetchall():
            writer.writerow(row)
    cur.close()
    conn.close()
    print(f"Exported table '{TABLE}' to {OUTPUT_CSV}")
except Exception as e:
    print(f"Error: {e}") 