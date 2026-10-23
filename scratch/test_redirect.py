import sqlite3
import requests

conn = sqlite3.connect('c:/Users/User/sopromoboa/backend/sopromoboa.db')
cur = conn.cursor()
cur.execute("SELECT id, title, source, affiliate_url FROM products WHERE source LIKE '%Amazon%' LIMIT 1")
row = cur.fetchone()
print('Sample Amazon Product:', row)
product_id = row[0]
conn.close()

# Test local redirect
res = requests.get(f'http://127.0.0.1:8001/r/{product_id}', allow_redirects=False)
print('Redirect Status:', res.status_code)
loc = res.headers.get('Location')
print('Target Location:', loc)
print('Has thiagovinigo-20 tag?', 'thiagovinigo-20' in loc)

# Test public tunnel redirect
try:
    tunnel_res = requests.get(f'https://everything-printer-temp-colon.trycloudflare.com/r/{product_id}', allow_redirects=False, timeout=8)
    print('Public Tunnel Redirect Status:', tunnel_res.status_code)
    loc_tunnel = tunnel_res.headers.get('Location')
    print('Public Tunnel Location:', loc_tunnel)
    print('Tunnel has thiagovinigo-20 tag?', 'thiagovinigo-20' in str(loc_tunnel))
except Exception as e:
    print('Tunnel test error:', e)
