import sqlite3

conn = sqlite3.connect('sopromoboa.db')
c = conn.cursor()
c.execute("SELECT id, title, url, affiliate_url, source FROM products WHERE title LIKE '%Plugue Inteligente%'")
rows = c.fetchall()
print(f"Found {len(rows)} rows:")
for r in rows:
    print(r)
