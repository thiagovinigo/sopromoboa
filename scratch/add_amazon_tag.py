import sqlite3
import requests

conn = sqlite3.connect("c:/Users/User/sopromoboa/backend/sopromoboa.db")
cur = conn.cursor()

# Check columns of stores
cur.execute("PRAGMA table_info(stores);")
print("stores columns:", cur.fetchall())

# Check columns of affiliate_programs
cur.execute("PRAGMA table_info(affiliate_programs);")
print("affiliate_programs columns:", cur.fetchall())

# Verify affiliate_programs row
cur.execute("SELECT * FROM affiliate_programs WHERE network_slug='amazon';")
print("Amazon in affiliate_programs:", cur.fetchall())

# Update stores if affiliate_tag column exists
cur.execute("PRAGMA table_info(stores);")
store_cols = [c[1] for c in cur.fetchall()]
if "affiliate_tag" in store_cols:
    cur.execute("UPDATE stores SET affiliate_tag='thiagovinigo-20' WHERE slug='amazon'")
    print("Updated stores affiliate_tag to thiagovinigo-20")

# Update all existing Amazon products affiliate_url
cur.execute("SELECT count(*) FROM products WHERE source LIKE '%Amazon%'")
amz_count = cur.fetchone()[0]
print(f"Total Amazon products: {amz_count}")

# Replace any old tag 'sopromoboa-20' or 'quepromo-20' with 'thiagovinigo-20' in products.affiliate_url and url
cur.execute("UPDATE products SET affiliate_url = REPLACE(affiliate_url, 'sopromoboa-20', 'thiagovinigo-20') WHERE source LIKE '%Amazon%'")
cur.execute("UPDATE products SET affiliate_url = REPLACE(affiliate_url, 'quepromo-20', 'thiagovinigo-20') WHERE source LIKE '%Amazon%'")
cur.execute("UPDATE products SET url = REPLACE(url, 'sopromoboa-20', 'thiagovinigo-20') WHERE source LIKE '%Amazon%'")
print("Updated all product URLs in database!")

conn.commit()
conn.close()

# Test API
try:
    res = requests.post("http://127.0.0.1:8001/api/affiliates", json={
        "name": "Amazon Brasil",
        "network_slug": "amazon",
        "tracking_id": "thiagovinigo-20",
        "commission_rate": "Até 15%"
    }, timeout=3)
    print("API update:", res.status_code, res.json())
except Exception as e:
    print("API call error:", e)

# Test GET /api/affiliates
try:
    res = requests.get("http://127.0.0.1:8001/api/affiliates", timeout=3)
    print("Affiliate programs in API:", res.json())
except Exception as e:
    print("API get error:", e)
