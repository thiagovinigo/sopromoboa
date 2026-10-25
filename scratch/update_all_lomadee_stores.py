import sqlite3, urllib.parse, re

db_path = '/var/lib/docker/volumes/sopromoboa_sopromoboa_data/_data/sopromoboa.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

LOMADEE_ID = "2324685"

stores_to_update = [
    ("Magazine Luiza", ["%magazine%", "%magalu%"]),
    ("KaBuM!", ["%kabum%"]),
    ("Casas Bahia", ["%casasbahia%", "%casas bahia%"]),
    ("Terabyteshop", ["%terabyte%"]),
]

total_updated = 0

for store_name, patterns in stores_to_update:
    store_updated = 0
    for pat in patterns:
        cur.execute("SELECT id, url FROM products WHERE source LIKE ?", (pat,))
        rows = cur.fetchall()
        for pid, raw_url in rows:
            clean_url = raw_url
            if 'magazinevoce.com.br' in clean_url:
                clean_url = re.sub(r'https?://(www\.)?magazinevoce\.com\.br/[^/]+/', 'https://www.magazineluiza.com.br/', clean_url)
            # Remove parâmetros antigos de parceiro
            clean_url = re.sub(r'[?&]parceiro=[^&]+', '', clean_url)
            clean_url = re.sub(r'[?&]tipo=link', '', clean_url)
            clean_url = clean_url.replace('?&', '?').rstrip('?')
            
            aff_url = f"https://redir.lomadee.com/v2/click?sourceId={LOMADEE_ID}&url={urllib.parse.quote_plus(clean_url)}"
            cur.execute("UPDATE products SET affiliate_url = ? WHERE id = ?", (aff_url, pid))
            store_updated += 1
            total_updated += 1
    print(f"[{store_name}] Total atualizados com Lomadee ({LOMADEE_ID}): {store_updated}")

conn.commit()
print(f"\nTOTAL GERAL ATUALIZADO COM LOMADEE: {total_updated} produtos!")
conn.close()
